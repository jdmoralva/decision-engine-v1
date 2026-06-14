from fastapi import APIRouter, Depends

from backend.app.api.schemas.contracts import AuditEventPageResponse
from backend.app.application.credit_requests.attachments_service import AttachmentService
from backend.app.security.dependencies import require_permission


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditEventPageResponse)
def list_audit_events(
    request_id: str | None = None,
    evaluation_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    _context: tuple = Depends(require_permission("consultar_auditoria")),
) -> AuditEventPageResponse:
    service = AttachmentService()
    return service.list_audit_events(
        request_id=None if not request_id else request_id.strip(),
        evaluation_id=None if not evaluation_id else evaluation_id.strip(),
        page=max(page, 1),
        page_size=max(page_size, 1),
    )
