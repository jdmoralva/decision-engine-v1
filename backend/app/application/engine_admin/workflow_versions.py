from backend.app.infrastructure.db.models import WorkflowVersion


def next_workflow_version_number(existing_versions: list[WorkflowVersion]) -> int:
    if not existing_versions:
        return 1
    return max(version.version_number for version in existing_versions) + 1
