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
