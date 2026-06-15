from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.schemas.engine_admin import (
    ParameterSetCreateRequest,
    PipelineStrategyCreateRequest,
    ProfilePermissionAssignmentRequest,
    ProductCreateRequest,
    ProductVariableCreateRequest,
    RuleCreateRequest,
    VariableCatalogCreateRequest,
    WorkflowCreateRequest,
    WorkflowVersionCreateRequest,
)
from backend.app.application.engine_admin.activation_rules import (
    EngineAdminValidationError,
    ensure_delete_allowed,
    ensure_not_last_active_workflow_version,
    ensure_product_retirement_coherence,
    ensure_segregation_of_duties,
    ensure_status,
    ensure_workflow_retirement_coherence,
)
from backend.app.application.engine_admin.workflow_versions import next_workflow_version_number
from backend.app.infrastructure.db.models import (
    LoanProduct,
    ParameterSet,
    Permission,
    PipelineNode,
    PipelineStrategy,
    ProductVariable,
    ProductWorkflow,
    Role,
    RolePermission,
    RuleSet,
    RuleVersion,
    VariableCatalogItem,
    VariableCatalogVersion,
    WorkflowRuleAssignment,
    WorkflowVersion,
)
from backend.app.infrastructure.repositories.audit_events import AuditEventWrite, AuditEventWriter


@dataclass(frozen=True)
class WorkflowVersionResult:
    workflow_version: WorkflowVersion
    rule_version_ids: list[str]


class EngineAdminService:
    def __init__(self, session_factory: sessionmaker[Session], audit_writer: AuditEventWriter) -> None:
        self._session_factory = session_factory
        self._audit_writer = audit_writer

    def create_product(self, payload: ProductCreateRequest, actor_id: str) -> LoanProduct:
        with self._session_factory() as session:
            existing = session.get(LoanProduct, payload.productCode)
            if existing is not None:
                raise EngineAdminValidationError(f"Product '{payload.productCode}' already exists.")

            product = LoanProduct(
                code=payload.productCode,
                name=payload.name,
                description=payload.description,
                status="draft",
                is_active=False,
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(product)
            session.commit()
            session.refresh(product)

        self._write_audit(product.code, "loan_product", "created", {"status": "draft"}, actor_id)
        return product

    def list_products(self, state: str = "active") -> list[LoanProduct]:
        with self._session_factory() as session:
            return list(
                session.execute(
                    select(LoanProduct).where(
                        LoanProduct.status == state,
                        LoanProduct.deleted_at.is_(None),
                    )
                ).scalars()
            )

    def get_product_detail(self, product_code: str) -> tuple[LoanProduct, list[ProductWorkflow]]:
        with self._session_factory() as session:
            product = session.execute(
                select(LoanProduct).where(
                    LoanProduct.code == product_code,
                    LoanProduct.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if product is None:
                raise EngineAdminValidationError(f"Product '{product_code}' does not exist.")

            active_workflows = list(
                session.execute(
                    select(ProductWorkflow).where(
                        ProductWorkflow.product_code == product_code,
                        ProductWorkflow.status == "active",
                        ProductWorkflow.deleted_at.is_(None),
                    )
                ).scalars()
            )
            return product, active_workflows

    def activate_product(self, product_code: str, actor_id: str) -> LoanProduct:
        with self._session_factory() as session:
            product = session.get(LoanProduct, product_code)
            if product is None:
                raise EngineAdminValidationError(f"Product '{product_code}' does not exist.")
            self._ensure_not_deleted("Product", product.deleted_at)

            product.status = "active"
            product.is_active = True
            product.activated_by = actor_id
            product.activated_at = datetime.now(UTC)
            session.commit()
            session.refresh(product)

        self._write_audit(product.code, "loan_product", "activated", {"status": "active"}, actor_id)
        return product

    def retire_product(self, product_code: str, actor_id: str) -> LoanProduct:
        with self._session_factory() as session:
            product = session.get(LoanProduct, product_code)
            if product is None:
                raise EngineAdminValidationError(f"Product '{product_code}' does not exist.")
            self._ensure_not_deleted("Product", product.deleted_at)

            if product.status == "active":
                active_workflow_count = session.execute(
                    select(ProductWorkflow).where(
                        ProductWorkflow.product_code == product_code,
                        ProductWorkflow.status == "active",
                        ProductWorkflow.deleted_at.is_(None),
                    )
                ).scalars().all()
                ensure_product_retirement_coherence(len(active_workflow_count))
            elif product.status != "draft":
                raise EngineAdminValidationError(
                    f"Product must be 'draft' or 'active' but is '{product.status}'."
                )
            product.status = "retired"
            product.is_active = False
            product.retired_by = actor_id
            product.retired_at = datetime.now(UTC)
            session.commit()
            session.refresh(product)

        self._write_audit(product.code, "loan_product", "retired", {"status": "retired"}, actor_id)
        return product

    def delete_product(self, product_code: str, actor_id: str, actor_roles: list[str]) -> None:
        deleted_status = ""
        with self._session_factory() as session:
            product = session.get(LoanProduct, product_code)
            if product is None:
                raise EngineAdminValidationError(f"Product '{product_code}' does not exist.")
            self._ensure_not_deleted("Product", product.deleted_at)

            ensure_delete_allowed("Product", product.status, actor_roles)
            deleted_status = product.status
            product.deleted_by = actor_id
            product.deleted_at = datetime.now(UTC)
            product.delete_reason = "administrative_delete"
            product.is_active = False
            session.commit()

        self._write_audit(product_code, "loan_product", "deleted", {"status": deleted_status}, actor_id)

    def create_workflow(self, product_code: str, payload: WorkflowCreateRequest, actor_id: str) -> ProductWorkflow:
        with self._session_factory() as session:
            self._require_product(session, product_code)
            existing = session.execute(
                select(ProductWorkflow).where(
                    ProductWorkflow.product_code == product_code,
                    ProductWorkflow.workflow_code == payload.workflowCode,
                )
            ).scalar_one_or_none()
            if existing is not None:
                raise EngineAdminValidationError(
                    f"Workflow '{payload.workflowCode}' already exists for product '{product_code}'."
                )

            workflow = ProductWorkflow(
                id=str(uuid4()),
                product_code=product_code,
                workflow_code=payload.workflowCode,
                name=payload.name,
                description=payload.description,
                status="draft",
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(workflow)
            session.commit()
            session.refresh(workflow)

        self._write_audit(workflow.id, "product_workflow", "created", {"status": "draft"}, actor_id)
        return workflow

    def list_workflows(self, product_code: str, state: str = "active") -> list[ProductWorkflow]:
        with self._session_factory() as session:
            self._require_product(session, product_code)
            return list(
                session.execute(
                    select(ProductWorkflow).where(
                        ProductWorkflow.product_code == product_code,
                        ProductWorkflow.status == state,
                        ProductWorkflow.deleted_at.is_(None),
                    )
                ).scalars()
            )

    def get_workflow_detail(
        self,
        workflow_id: str,
    ) -> tuple[ProductWorkflow, list[WorkflowVersion], list[str]]:
        with self._session_factory() as session:
            workflow = session.execute(
                select(ProductWorkflow).where(
                    ProductWorkflow.id == workflow_id,
                    ProductWorkflow.deleted_at.is_(None),
                )
            ).scalar_one_or_none()
            if workflow is None:
                raise EngineAdminValidationError(f"Workflow '{workflow_id}' does not exist.")

            workflow_versions = list(
                session.execute(
                    select(WorkflowVersion).where(WorkflowVersion.workflow_id == workflow_id)
                ).scalars()
            )
            workflow_version_ids = [version.id for version in workflow_versions]
            rule_version_ids: list[str] = []
            if workflow_version_ids:
                rule_version_ids = [
                    assignment.rule_version_id
                    for assignment in session.execute(
                        select(WorkflowRuleAssignment).where(
                            WorkflowRuleAssignment.workflow_version_id.in_(workflow_version_ids)
                        )
                    ).scalars()
                ]
            return workflow, workflow_versions, rule_version_ids

    def retire_workflow(self, workflow_id: str, actor_id: str) -> ProductWorkflow:
        with self._session_factory() as session:
            workflow = session.get(ProductWorkflow, workflow_id)
            if workflow is None:
                raise EngineAdminValidationError(f"Workflow '{workflow_id}' does not exist.")
            self._ensure_not_deleted("Workflow", workflow.deleted_at)

            if workflow.status == "active":
                active_version_count = session.execute(
                    select(WorkflowVersion).where(
                        WorkflowVersion.workflow_id == workflow_id,
                        WorkflowVersion.status == "active",
                    )
                ).scalars().all()
                ensure_workflow_retirement_coherence(len(active_version_count))
            elif workflow.status != "draft":
                raise EngineAdminValidationError(
                    f"Workflow must be 'draft' or 'active' but is '{workflow.status}'."
                )
            workflow.status = "retired"
            workflow.retired_by = actor_id
            workflow.retired_at = datetime.now(UTC)
            session.commit()
            session.refresh(workflow)

        self._write_audit(workflow.id, "product_workflow", "retired", {"status": "retired"}, actor_id)
        return workflow

    def delete_workflow(self, workflow_id: str, actor_id: str, actor_roles: list[str]) -> None:
        deleted_status = ""
        with self._session_factory() as session:
            workflow = session.get(ProductWorkflow, workflow_id)
            if workflow is None:
                raise EngineAdminValidationError(f"Workflow '{workflow_id}' does not exist.")
            self._ensure_not_deleted("Workflow", workflow.deleted_at)

            ensure_delete_allowed("Workflow", workflow.status, actor_roles)
            deleted_status = workflow.status
            workflow.deleted_by = actor_id
            workflow.deleted_at = datetime.now(UTC)
            workflow.delete_reason = "administrative_delete"
            session.commit()

        self._write_audit(workflow_id, "product_workflow", "deleted", {"status": deleted_status}, actor_id)

    def create_variable(self, product_code: str, payload: ProductVariableCreateRequest, actor_id: str) -> ProductVariable:
        with self._session_factory() as session:
            self._require_product(session, product_code)
            variable = ProductVariable(
                id=str(uuid4()),
                product_code=product_code,
                variable_key=payload.variableKey,
                name=payload.name,
                business_meaning=payload.businessMeaning,
                description=payload.description,
                data_type=payload.dataType,
                is_required=payload.required,
                allowed_sources=payload.allowedSource,
                status="draft",
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(variable)
            try:
                session.commit()
                session.refresh(variable)
            except IntegrityError as exc:
                session.rollback()
                raise EngineAdminValidationError(
                    f"Variable '{payload.variableKey}' already exists for product '{product_code}'."
                ) from exc

        self._write_audit(variable.id, "product_variable", "created", {"status": "draft"}, actor_id)
        return variable

    def activate_variable(self, variable_id: str, actor_id: str) -> ProductVariable:
        with self._session_factory() as session:
            variable = session.get(ProductVariable, variable_id)
            if variable is None:
                raise EngineAdminValidationError(f"Variable '{variable_id}' does not exist.")
            ensure_status("Variable", variable.status, "draft")
            variable.status = "active"
            variable.activated_by = actor_id
            variable.activated_at = datetime.now(UTC)
            session.commit()
            session.refresh(variable)

        self._write_audit(variable.id, "product_variable", "activated", {"status": "active"}, actor_id)
        return variable

    def create_variable_catalog(
        self,
        product_code: str,
        payload: VariableCatalogCreateRequest,
        actor_id: str,
    ) -> tuple[VariableCatalogVersion, list[VariableCatalogItem]]:
        with self._session_factory() as session:
            self._require_product(session, product_code)
            version_number = self._next_catalog_version_number(session, product_code)
            catalog = VariableCatalogVersion(
                id=str(uuid4()),
                product_code=product_code,
                version_number=version_number,
                status="draft",
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(catalog)
            session.flush()

            items: list[VariableCatalogItem] = []
            for item in payload.items:
                variable = session.get(ProductVariable, item.productVariableId)
                if variable is None or variable.product_code != product_code:
                    raise EngineAdminValidationError("Catalog contains variables from another product.")

                row = VariableCatalogItem(
                    id=str(uuid4()),
                    catalog_version_id=catalog.id,
                    product_variable_id=item.productVariableId,
                    is_required_in_runtime=item.requiredInRuntime,
                    default_value=None if item.defaultValue is None else json.dumps(item.defaultValue),
                    source_policy_payload=json.dumps(item.sourcePolicyPayload),
                )
                session.add(row)
                items.append(row)

            session.commit()
            session.refresh(catalog)
            items = list(
                session.execute(
                    select(VariableCatalogItem).where(VariableCatalogItem.catalog_version_id == catalog.id)
                ).scalars()
            )

        self._write_audit(catalog.id, "variable_catalog_version", "created", {"status": "draft"}, actor_id)
        return catalog, items

    def activate_variable_catalog(self, catalog_id: str, actor_id: str) -> tuple[VariableCatalogVersion, list[VariableCatalogItem]]:
        with self._session_factory() as session:
            catalog = session.get(VariableCatalogVersion, catalog_id)
            if catalog is None:
                raise EngineAdminValidationError(f"Variable catalog '{catalog_id}' does not exist.")
            ensure_status("Variable catalog", catalog.status, "draft")
            items = list(
                session.execute(
                    select(VariableCatalogItem).where(VariableCatalogItem.catalog_version_id == catalog_id)
                ).scalars()
            )
            for item in items:
                variable = session.get(ProductVariable, item.product_variable_id)
                if variable is None or variable.status != "active":
                    raise EngineAdminValidationError(
                        "Variable catalog can only be activated with active variables."
                    )

            catalog.status = "active"
            catalog.activated_by = actor_id
            catalog.activated_at = datetime.now(UTC)
            session.commit()
            session.refresh(catalog)
            items = list(
                session.execute(
                    select(VariableCatalogItem).where(VariableCatalogItem.catalog_version_id == catalog_id)
                ).scalars()
            )

        self._write_audit(catalog.id, "variable_catalog_version", "activated", {"status": "active"}, actor_id)
        return catalog, items

    def create_parameter_set(
        self,
        product_code: str,
        payload: ParameterSetCreateRequest,
        actor_id: str,
    ) -> ParameterSet:
        with self._session_factory() as session:
            self._require_product(session, product_code)
            version_number = self._next_parameter_version_number(session, product_code, payload.workflowCode)
            row = ParameterSet(
                id=str(uuid4()),
                product_code=product_code,
                workflow_code=payload.workflowCode,
                version_number=version_number,
                status="draft",
                payload=json.dumps(payload.payload),
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(row)
            session.commit()
            session.refresh(row)

        self._write_audit(row.id, "parameter_set", "created", {"status": "draft"}, actor_id)
        return row

    def activate_parameter_set(self, parameter_set_id: str, actor_id: str) -> ParameterSet:
        with self._session_factory() as session:
            row = session.get(ParameterSet, parameter_set_id)
            if row is None:
                raise EngineAdminValidationError(f"Parameter set '{parameter_set_id}' does not exist.")
            ensure_status("Parameter set", row.status, "draft")
            row.status = "active"
            row.activated_by = actor_id
            row.activated_at = datetime.now(UTC)
            session.commit()
            session.refresh(row)

        self._write_audit(row.id, "parameter_set", "activated", {"status": "active"}, actor_id)
        return row

    def create_pipeline_strategy(
        self,
        product_code: str,
        payload: PipelineStrategyCreateRequest,
        actor_id: str,
    ) -> tuple[PipelineStrategy, list[PipelineNode]]:
        with self._session_factory() as session:
            self._require_product(session, product_code)
            version_number = self._next_pipeline_version_number(session, product_code)
            strategy = PipelineStrategy(
                id=str(uuid4()),
                loan_product_code=product_code,
                version_number=version_number,
                graph_definition=json.dumps(payload.graphDefinition),
                status="draft",
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(strategy)
            session.flush()

            nodes: list[PipelineNode] = []
            for node in payload.nodes:
                row = PipelineNode(
                    id=str(uuid4()),
                    pipeline_strategy_id=strategy.id,
                    node_key=node.nodeKey,
                    node_type=node.nodeType,
                    position_x=node.positionX,
                    position_y=node.positionY,
                    config_payload=json.dumps(node.configPayload),
                    created_at=datetime.now(UTC),
                )
                session.add(row)
                nodes.append(row)

            session.commit()
            session.refresh(strategy)
            nodes = list(
                session.execute(
                    select(PipelineNode).where(PipelineNode.pipeline_strategy_id == strategy.id)
                ).scalars()
            )

        self._write_audit(strategy.id, "pipeline_strategy", "created", {"status": "draft"}, actor_id)
        return strategy, nodes

    def activate_pipeline_strategy(self, strategy_id: str, actor_id: str) -> tuple[PipelineStrategy, list[PipelineNode]]:
        with self._session_factory() as session:
            strategy = session.get(PipelineStrategy, strategy_id)
            if strategy is None:
                raise EngineAdminValidationError(f"Pipeline strategy '{strategy_id}' does not exist.")
            ensure_status("Pipeline strategy", strategy.status, "draft")
            nodes = list(
                session.execute(
                    select(PipelineNode).where(PipelineNode.pipeline_strategy_id == strategy_id)
                ).scalars()
            )
            if not nodes:
                raise EngineAdminValidationError("Pipeline strategy must define at least one node.")

            strategy.status = "active"
            strategy.approved_by = actor_id
            session.commit()
            session.refresh(strategy)
            nodes = list(
                session.execute(
                    select(PipelineNode).where(PipelineNode.pipeline_strategy_id == strategy_id)
                ).scalars()
            )

        self._write_audit(strategy.id, "pipeline_strategy", "activated", {"status": "active"}, actor_id)
        return strategy, nodes

    def create_rule(self, workflow_id: str, payload: RuleCreateRequest, actor_id: str) -> tuple[RuleSet, RuleVersion]:
        with self._session_factory() as session:
            workflow = session.get(ProductWorkflow, workflow_id)
            if workflow is None:
                raise EngineAdminValidationError(f"Workflow '{workflow_id}' does not exist.")

            rule_set = RuleSet(
                id=str(uuid4()),
                loan_product_code=workflow.product_code,
                name=payload.name,
                description=None,
                effective_from=datetime.now(UTC),
                status="draft",
                is_active=False,
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(rule_set)
            session.flush()

            rule_version = RuleVersion(
                id=str(uuid4()),
                rule_set_id=rule_set.id,
                version_number=1,
                rule_key=f"{workflow.workflow_code}_{rule_set.id}",
                rule_name=payload.name,
                rule_type=payload.ruleType,
                condition_expression=payload.conditionExpression,
                action_expression=payload.actionExpression,
                parameters=json.dumps(payload.parameters),
                status="draft",
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(rule_version)
            session.commit()
            session.refresh(rule_set)
            session.refresh(rule_version)

        self._write_audit(rule_set.id, "rule_set", "created", {"status": "draft"}, actor_id)
        return rule_set, rule_version

    def activate_rule_version(self, rule_version_id: str, actor_id: str) -> tuple[RuleSet, RuleVersion, str | None]:
        with self._session_factory() as session:
            rule_version = session.get(RuleVersion, rule_version_id)
            if rule_version is None:
                raise EngineAdminValidationError(f"Rule version '{rule_version_id}' does not exist.")
            ensure_status("Rule version", rule_version.status, "draft")
            rule_set = session.get(RuleSet, rule_version.rule_set_id)
            if rule_set is None:
                raise EngineAdminValidationError("Rule set does not exist.")

            rule_version.status = "active"
            rule_version.approved_by = actor_id
            rule_set.status = "active"
            rule_set.is_active = True
            rule_set.activated_by = actor_id
            rule_set.activated_at = datetime.now(UTC)
            workflow_id = self._resolve_workflow_id_for_rule_version(session, rule_set, rule_version)
            session.commit()
            session.refresh(rule_set)
            session.refresh(rule_version)

        self._write_audit(rule_version.id, "rule_version", "activated", {"status": "active"}, actor_id)
        return rule_set, rule_version, workflow_id

    def delete_rule(self, rule_id: str, actor_id: str, actor_roles: list[str]) -> None:
        deleted_status = ""
        with self._session_factory() as session:
            rule_set = session.get(RuleSet, rule_id)
            if rule_set is None:
                raise EngineAdminValidationError(f"Rule '{rule_id}' does not exist.")
            self._ensure_not_deleted("Rule", rule_set.deleted_at)

            ensure_delete_allowed("Rule", rule_set.status, actor_roles)
            deleted_status = rule_set.status
            rule_set.deleted_by = actor_id
            rule_set.deleted_at = datetime.now(UTC)
            rule_set.delete_reason = "administrative_delete"
            rule_set.is_active = False
            session.commit()

        self._write_audit(rule_id, "rule_set", "deleted", {"status": deleted_status}, actor_id)

    def create_workflow_version(
        self,
        workflow_id: str,
        payload: WorkflowVersionCreateRequest,
        actor_id: str,
    ) -> WorkflowVersionResult:
        with self._session_factory() as session:
            workflow = session.get(ProductWorkflow, workflow_id)
            if workflow is None:
                raise EngineAdminValidationError(f"Workflow '{workflow_id}' does not exist.")

            catalog = session.get(VariableCatalogVersion, payload.variableCatalogVersionId)
            parameter_set = session.get(ParameterSet, payload.parameterSetId)
            pipeline_strategy = session.get(PipelineStrategy, payload.pipelineStrategyId)
            if catalog is None or parameter_set is None or pipeline_strategy is None:
                raise EngineAdminValidationError("Workflow version references missing dependencies.")
            if catalog.product_code != workflow.product_code:
                raise EngineAdminValidationError("Variable catalog belongs to another product.")
            if parameter_set.product_code != workflow.product_code or parameter_set.workflow_code != workflow.workflow_code:
                raise EngineAdminValidationError("Parameter set does not match workflow identity.")
            if pipeline_strategy.loan_product_code != workflow.product_code:
                raise EngineAdminValidationError("Pipeline strategy belongs to another product.")
            if catalog.status != "active" or parameter_set.status != "active" or pipeline_strategy.status != "active":
                raise EngineAdminValidationError(
                    "Workflow version can only be created from active catalog, parameter set, and pipeline strategy."
                )

            existing_versions = list(
                session.execute(
                    select(WorkflowVersion).where(WorkflowVersion.workflow_id == workflow_id)
                ).scalars()
            )
            version = WorkflowVersion(
                id=str(uuid4()),
                workflow_id=workflow_id,
                version_number=next_workflow_version_number(existing_versions),
                status="draft",
                variable_catalog_version_id=catalog.id,
                parameter_set_id=parameter_set.id,
                pipeline_strategy_id=pipeline_strategy.id,
                change_notes=payload.changeNotes,
                created_by=actor_id,
                created_at=datetime.now(UTC),
            )
            session.add(version)
            session.flush()

            for order, rule_version_id in enumerate(payload.ruleVersionIds, start=1):
                rule_version = session.get(RuleVersion, rule_version_id)
                if rule_version is None or rule_version.status != "active":
                    raise EngineAdminValidationError(
                        "Workflow version can only reference active rule versions."
                    )
                session.add(
                    WorkflowRuleAssignment(
                        id=str(uuid4()),
                        workflow_version_id=version.id,
                        rule_version_id=rule_version_id,
                        execution_order=order,
                        is_active=True,
                    )
                )

            session.commit()
            session.refresh(version)

        self._write_audit(version.id, "workflow_version", "created", {"status": "draft"}, actor_id)
        return WorkflowVersionResult(version, payload.ruleVersionIds)

    def activate_workflow_version(self, version_id: str, actor_id: str) -> WorkflowVersionResult:
        with self._session_factory() as session:
            workflow_version = session.get(WorkflowVersion, version_id)
            if workflow_version is None:
                raise EngineAdminValidationError(f"Workflow version '{version_id}' does not exist.")
            ensure_status("Workflow version", workflow_version.status, "draft")
            ensure_segregation_of_duties("Workflow version", workflow_version.created_by, actor_id)

            active_versions = list(
                session.execute(
                    select(WorkflowVersion).where(
                        WorkflowVersion.workflow_id == workflow_version.workflow_id,
                        WorkflowVersion.status == "active",
                    )
                ).scalars()
            )
            for active in active_versions:
                active.status = "retired"
                active.retired_by = actor_id
                active.retired_at = datetime.now(UTC)

            workflow_version.status = "active"
            workflow_version.activated_by = actor_id
            workflow_version.activated_at = datetime.now(UTC)

            workflow = session.get(ProductWorkflow, workflow_version.workflow_id)
            if workflow is None:
                raise EngineAdminValidationError("Workflow does not exist.")
            workflow.status = "active"
            workflow.activated_by = actor_id
            workflow.activated_at = datetime.now(UTC)

            session.commit()
            session.refresh(workflow_version)
            rule_version_ids = [
                assignment.rule_version_id
                for assignment in session.execute(
                    select(WorkflowRuleAssignment).where(
                        WorkflowRuleAssignment.workflow_version_id == workflow_version.id
                    )
                ).scalars()
            ]

        self._write_audit(version_id, "workflow_version", "activated", {"status": "active"}, actor_id)
        return WorkflowVersionResult(workflow_version, rule_version_ids)

    def retire_workflow_version(self, version_id: str, actor_id: str) -> WorkflowVersionResult:
        with self._session_factory() as session:
            workflow_version = session.get(WorkflowVersion, version_id)
            if workflow_version is None:
                raise EngineAdminValidationError(f"Workflow version '{version_id}' does not exist.")
            ensure_status("Workflow version", workflow_version.status, "active")

            workflow = session.get(ProductWorkflow, workflow_version.workflow_id)
            if workflow is None:
                raise EngineAdminValidationError("Workflow does not exist.")
            product = session.get(LoanProduct, workflow.product_code)
            if product is None:
                raise EngineAdminValidationError("Product does not exist.")

            active_versions = list(
                session.execute(
                    select(WorkflowVersion).where(
                        WorkflowVersion.workflow_id == workflow.id,
                        WorkflowVersion.status == "active",
                    )
                ).scalars()
            )
            ensure_not_last_active_workflow_version(product, workflow_version, active_versions)

            workflow_version.status = "retired"
            workflow_version.retired_by = actor_id
            workflow_version.retired_at = datetime.now(UTC)
            session.commit()
            session.refresh(workflow_version)
            rule_version_ids = [
                assignment.rule_version_id
                for assignment in session.execute(
                    select(WorkflowRuleAssignment).where(
                        WorkflowRuleAssignment.workflow_version_id == workflow_version.id
                    )
                ).scalars()
            ]

        self._write_audit(version_id, "workflow_version", "retired", {"status": "retired"}, actor_id)
        return WorkflowVersionResult(workflow_version, rule_version_ids)

    def get_profile_permissions(self, role_code: str) -> list[dict[str, str | None]]:
        with self._session_factory() as session:
            role = session.execute(select(Role).where(Role.code == role_code)).scalar_one_or_none()
            if role is None:
                raise EngineAdminValidationError(f"Profile '{role_code}' does not exist.")

            rows = session.execute(
                select(Permission).join(RolePermission, RolePermission.permission_id == Permission.id).where(
                    RolePermission.role_id == role.id
                )
            ).scalars().all()

            if not rows:
                from backend.app.security.permissions import ROLE_PERMISSIONS

                return [
                    {"code": code, "name": code.replace("_", " ").title(), "description": None}
                    for code in sorted(ROLE_PERMISSIONS.get(role_code, set()))
                ]

            return [
                {"code": row.code, "name": row.name, "description": row.description}
                for row in sorted(rows, key=lambda item: item.code)
            ]

    def replace_profile_permissions(
        self,
        role_code: str,
        payload: ProfilePermissionAssignmentRequest,
        actor_id: str,
    ) -> list[dict[str, str | None]]:
        requested_codes = sorted(set(payload.permissionCodes))
        with self._session_factory() as session:
            role = session.execute(select(Role).where(Role.code == role_code)).scalar_one_or_none()
            if role is None:
                raise EngineAdminValidationError(f"Profile '{role_code}' does not exist.")

            existing_permissions = {
                permission.code: permission
                for permission in session.execute(select(Permission)).scalars().all()
            }
            for permission_code in requested_codes:
                permission = existing_permissions.get(permission_code)
                if permission is None:
                    permission = Permission(
                        id=str(uuid4()),
                        code=permission_code,
                        name=permission_code.replace("_", " ").title(),
                        description=None,
                        created_at=datetime.now(UTC),
                    )
                    session.add(permission)
                    session.flush()
                    existing_permissions[permission_code] = permission

            current_links = list(
                session.execute(
                    select(RolePermission).where(RolePermission.role_id == role.id)
                ).scalars()
            )
            for link in current_links:
                session.delete(link)
            session.flush()

            for permission_code in requested_codes:
                session.add(
                    RolePermission(
                        id=str(uuid4()),
                        role_id=role.id,
                        permission_id=existing_permissions[permission_code].id,
                        created_at=datetime.now(UTC),
                    )
                )

            session.commit()

        self._audit_writer.write_profile_permission_change(
            role_code=role_code,
            permission_codes=requested_codes,
            created_by=actor_id,
        )
        return self.get_profile_permissions(role_code)

    def _require_product(self, session: Session, product_code: str) -> LoanProduct:
        product = session.get(LoanProduct, product_code)
        if product is None:
            raise EngineAdminValidationError(f"Product '{product_code}' does not exist.")
        self._ensure_not_deleted("Product", product.deleted_at)
        return product

    def _ensure_not_deleted(self, entity_name: str, deleted_at) -> None:
        if deleted_at is not None:
            raise EngineAdminValidationError(f"{entity_name} was deleted and cannot transition anymore.")

    def _resolve_workflow_id_for_rule_version(
        self,
        session: Session,
        rule_set: RuleSet,
        rule_version: RuleVersion,
    ) -> str | None:
        workflow_code = rule_version.rule_key.rsplit("_", 1)[0]
        workflow = session.execute(
            select(ProductWorkflow).where(
                ProductWorkflow.product_code == rule_set.loan_product_code,
                ProductWorkflow.workflow_code == workflow_code,
                ProductWorkflow.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        return None if workflow is None else workflow.id

    def _next_catalog_version_number(self, session: Session, product_code: str) -> int:
        versions = list(
            session.execute(
                select(VariableCatalogVersion).where(VariableCatalogVersion.product_code == product_code)
            ).scalars()
        )
        return max((version.version_number for version in versions), default=0) + 1

    def _next_parameter_version_number(self, session: Session, product_code: str, workflow_code: str) -> int:
        versions = list(
            session.execute(
                select(ParameterSet).where(
                    ParameterSet.product_code == product_code,
                    ParameterSet.workflow_code == workflow_code,
                )
            ).scalars()
        )
        return max((version.version_number for version in versions), default=0) + 1

    def _next_pipeline_version_number(self, session: Session, product_code: str) -> int:
        versions = list(
            session.execute(
                select(PipelineStrategy).where(PipelineStrategy.loan_product_code == product_code)
            ).scalars()
        )
        return max((version.version_number for version in versions), default=0) + 1

    def _write_audit(
        self,
        aggregate_id: str,
        aggregate_type: str,
        event_type: str,
        payload: dict[str, str],
        actor_id: str,
    ) -> None:
        self._audit_writer.write(
            AuditEventWrite(
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                event_type=event_type,
                event_payload=json.dumps(payload),
                created_by=actor_id,
            )
        )
