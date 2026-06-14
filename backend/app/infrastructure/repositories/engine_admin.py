from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.db.models import (
    ParameterSet,
    Permission,
    PipelineNode,
    PipelineStrategy,
    ProductVariable,
    ProductWorkflow,
    Role,
    RolePermission,
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


@dataclass(frozen=True)
class RolePermissionAssignment:
    role_code: str
    permission_code: str


class EngineAdminRuntimeRepository(Protocol):
    def load_active_runtime_bundle(self, product_code: str, workflow_code: str) -> RuntimeBundle | None: ...

    def list_active_workflows(self) -> list[tuple[str, str]]: ...

    def list_role_permissions(self, role_codes: list[str] | None = None) -> list[RolePermissionAssignment]: ...

    def replace_role_permissions(self, role_code: str, permission_codes: list[str]) -> list[RolePermissionAssignment]: ...


class SqlAlchemyEngineAdminRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_active_workflows(self) -> list[tuple[str, str]]:
        with self._session_factory() as session:
            rows = session.execute(
                select(ProductWorkflow.product_code, ProductWorkflow.workflow_code).where(
                    ProductWorkflow.status == "active"
                ).order_by(ProductWorkflow.product_code, ProductWorkflow.workflow_code)
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

    def list_role_permissions(self, role_codes: list[str] | None = None) -> list[RolePermissionAssignment]:
        with self._session_factory() as session:
            query = (
                select(Role.code, Permission.code)
                .join(RolePermission, RolePermission.role_id == Role.id)
                .join(Permission, Permission.id == RolePermission.permission_id)
                .order_by(Role.code, Permission.code)
            )
            if role_codes:
                query = query.where(Role.code.in_(role_codes))

            rows = session.execute(query).all()

        return [
            RolePermissionAssignment(role_code=role_code, permission_code=permission_code)
            for role_code, permission_code in rows
        ]

    def replace_role_permissions(self, role_code: str, permission_codes: list[str]) -> list[RolePermissionAssignment]:
        with self._session_factory() as session:
            role = session.execute(select(Role).where(Role.code == role_code)).scalar_one_or_none()
            if role is None:
                return []

            permission_rows = list(
                session.execute(select(Permission).where(Permission.code.in_(permission_codes))).scalars()
            )
            permissions_by_code = {permission.code: permission for permission in permission_rows}

            current_links = list(
                session.execute(
                    select(RolePermission).where(RolePermission.role_id == role.id)
                ).scalars()
            )
            for link in current_links:
                session.delete(link)

            for permission_code in permission_codes:
                permission = permissions_by_code.get(permission_code)
                if permission is None:
                    continue
                session.add(
                    RolePermission(
                        id=str(uuid4()),
                        role_id=role.id,
                        permission_id=permission.id,
                        created_at=datetime.now(UTC),
                    )
                )

            session.commit()

        return self.list_role_permissions([role_code])
