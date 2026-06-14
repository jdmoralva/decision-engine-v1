from collections.abc import Iterable

from backend.app.infrastructure.db.models import LoanProduct, WorkflowVersion


class EngineAdminValidationError(ValueError):
    pass


def ensure_status(entity_name: str, current_status: str, expected_status: str) -> None:
    if current_status != expected_status:
        raise EngineAdminValidationError(
            f"{entity_name} must be '{expected_status}' but is '{current_status}'."
        )


def ensure_not_last_active_workflow_version(
    product: LoanProduct,
    workflow_version: WorkflowVersion,
    active_versions: list[WorkflowVersion],
) -> None:
    if product.status == "active" and len(active_versions) <= 1 and workflow_version in active_versions:
        raise EngineAdminValidationError(
            "Cannot retire the last active workflow version of an active product."
        )


def ensure_segregation_of_duties(artifact_name: str, creator_id: str, actor_id: str) -> None:
    if creator_id == actor_id:
        raise EngineAdminValidationError(
            f"{artifact_name} activation requires a different user than the creator."
        )


def ensure_product_retirement_coherence(active_workflow_count: int) -> None:
    if active_workflow_count > 0:
        raise EngineAdminValidationError(
            "Product cannot be retired while it still has active workflows."
        )


def ensure_workflow_retirement_coherence(active_version_count: int) -> None:
    if active_version_count > 0:
        raise EngineAdminValidationError(
            "Workflow cannot be retired while it still has active workflow versions."
        )


def ensure_delete_allowed(
    entity_name: str,
    status: str,
    actor_roles: Iterable[str],
) -> None:
    roles = set(actor_roles)
    if "admin" in roles or "admin_riesgos" in roles:
        if status == "active":
            raise EngineAdminValidationError(
                f"{entity_name} in active state must be retired before deletion."
            )
        return

    if "admin_negocio" in roles and status == "draft":
        return

    raise EngineAdminValidationError(
        f"Current role cannot delete {entity_name.lower()} in state '{status}'."
    )
