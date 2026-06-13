from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.db.models import (
    ParameterSet,
    PipelineNode,
    PipelineStrategy,
    ProductVariable,
    ProductWorkflow,
    RuleVersion,
    VariableCatalogItem,
    VariableCatalogVersion,
    WorkflowRuleAssignment,
    WorkflowVersion,
)


@dataclass(frozen=True)
class RuntimeBundle:
    product_code: str
    workflow_code: str
    workflow_version: WorkflowVersion
    catalog_version: VariableCatalogVersion
    catalog_items: list[VariableCatalogItem]
    variables: list[ProductVariable]
    parameter_set: ParameterSet
    pipeline_strategy: PipelineStrategy
    pipeline_nodes: list[PipelineNode]
    rule_versions: list[RuleVersion]


class EngineAdminRuntimeRepository(Protocol):
    def load_active_runtime_bundle(self, product_code: str, workflow_code: str) -> RuntimeBundle | None: ...

    def list_active_workflows(self) -> list[tuple[str, str]]: ...


class SqlAlchemyEngineAdminRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_active_workflows(self) -> list[tuple[str, str]]:
        with self._session_factory() as session:
            rows = session.execute(
                select(ProductWorkflow.product_code, ProductWorkflow.workflow_code).where(
                    ProductWorkflow.status == "active"
                )
            ).all()
        return [(product_code, workflow_code) for product_code, workflow_code in rows]

    def load_active_runtime_bundle(self, product_code: str, workflow_code: str) -> RuntimeBundle | None:
        with self._session_factory() as session:
            workflow = session.execute(
                select(ProductWorkflow).where(
                    ProductWorkflow.product_code == product_code,
                    ProductWorkflow.workflow_code == workflow_code,
                    ProductWorkflow.status == "active",
                )
            ).scalar_one_or_none()
            if workflow is None:
                return None

            workflow_version = session.execute(
                select(WorkflowVersion).where(
                    WorkflowVersion.workflow_id == workflow.id,
                    WorkflowVersion.status == "active",
                )
            ).scalar_one_or_none()
            if workflow_version is None:
                return None

            catalog_version = session.get(
                VariableCatalogVersion, workflow_version.variable_catalog_version_id
            )
            parameter_set = session.get(ParameterSet, workflow_version.parameter_set_id)
            pipeline_strategy = session.get(PipelineStrategy, workflow_version.pipeline_strategy_id)
            if catalog_version is None or parameter_set is None or pipeline_strategy is None:
                return None

            catalog_items = list(
                session.execute(
                    select(VariableCatalogItem).where(
                        VariableCatalogItem.catalog_version_id == catalog_version.id
                    )
                ).scalars()
            )
            variables_by_id = {
                variable.id: variable
                for variable in session.execute(
                    select(ProductVariable).where(ProductVariable.product_code == product_code)
                ).scalars()
            }
            variables = [variables_by_id[item.product_variable_id] for item in catalog_items if item.product_variable_id in variables_by_id]
            pipeline_nodes = list(
                session.execute(
                    select(PipelineNode).where(PipelineNode.pipeline_strategy_id == pipeline_strategy.id)
                ).scalars()
            )
            rule_assignments = list(
                session.execute(
                    select(WorkflowRuleAssignment).where(
                        WorkflowRuleAssignment.workflow_version_id == workflow_version.id,
                        WorkflowRuleAssignment.is_active.is_(True),
                    )
                ).scalars()
            )
            rule_versions = [
                rule_version
                for rule_version in (
                    session.get(RuleVersion, assignment.rule_version_id) for assignment in rule_assignments
                )
                if rule_version is not None
            ]
            return RuntimeBundle(
                product_code=product_code,
                workflow_code=workflow_code,
                workflow_version=workflow_version,
                catalog_version=catalog_version,
                catalog_items=catalog_items,
                variables=variables,
                parameter_set=parameter_set,
                pipeline_strategy=pipeline_strategy,
                pipeline_nodes=pipeline_nodes,
                rule_versions=rule_versions,
            )
