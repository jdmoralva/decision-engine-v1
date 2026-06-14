from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from backend.app.api.schemas.contracts import (
    AttachmentManifestResponse,
    AttachmentMetadataResponse,
    ContractError,
    StructuredErrorResponse,
)
from backend.app.application.credit_requests.attachments_service import (
    AttachmentNotFoundError,
    AttachmentService,
    AttachmentValidationError,
)
from backend.app.security.dependencies import require_permission


router = APIRouter(prefix="/credit-requests/{request_id}/attachments", tags=["attachments"])


error_responses = {
    400: {"model": StructuredErrorResponse, "description": "Business validation error."},
    401: {"model": StructuredErrorResponse, "description": "Authentication required."},
    403: {"model": StructuredErrorResponse, "description": "Forbidden."},
    404: {"model": StructuredErrorResponse, "description": "Resource not found."},
    422: {"description": "Request validation error."},
}


def _structured_error(status_code_value: int, code: str, message: str) -> JSONResponse:
    payload = StructuredErrorResponse(error=ContractError(code=code, message=message))
    return JSONResponse(status_code=status_code_value, content=payload.model_dump())


@router.post("", response_model=AttachmentMetadataResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
async def upload_attachment(
    request_id: str,
    file: UploadFile = File(...),
    context: tuple = Depends(require_permission("gestionar_adjuntos")),
) -> AttachmentMetadataResponse | JSONResponse:
    user, _roles = context
    service = AttachmentService()
    try:
        payload = await file.read()
        return service.upload_attachment(
            request_id=request_id,
            filename=file.filename or "adjunto.zip",
            content_type=file.content_type or "application/zip",
            content=payload,
            actor_user_id=user.id,
            actor_username=user.username,
        )
    except AttachmentValidationError as exc:
        return _structured_error(status.HTTP_400_BAD_REQUEST, "ATTACHMENT_VALIDATION", str(exc))
    except AttachmentNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "ATTACHMENT_NOT_FOUND", str(exc))


@router.get("", response_model=list[AttachmentMetadataResponse], responses=error_responses)
def list_attachments(
    request_id: str,
    _context: tuple = Depends(require_permission("gestionar_adjuntos")),
) -> list[AttachmentMetadataResponse] | JSONResponse:
    service = AttachmentService()
    try:
        return service.list_attachments(request_id=request_id)
    except AttachmentNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "ATTACHMENT_NOT_FOUND", str(exc))


@router.get("/{attachment_id}/manifest", response_model=AttachmentManifestResponse, responses=error_responses)
def get_attachment_manifest(
    request_id: str,
    attachment_id: str,
    _context: tuple = Depends(require_permission("gestionar_adjuntos")),
) -> AttachmentManifestResponse | JSONResponse:
    service = AttachmentService()
    try:
        return service.get_manifest(request_id=request_id, attachment_id=attachment_id)
    except AttachmentNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "ATTACHMENT_NOT_FOUND", str(exc))


@router.get("/{attachment_id}/download", responses={**error_responses, 200: {"description": "ZIP download."}})
def download_attachment(
    request_id: str,
    attachment_id: str,
    context: tuple = Depends(require_permission("gestionar_adjuntos")),
):
    user, _roles = context
    service = AttachmentService()
    try:
        record, _payload = service.download_attachment(
            request_id=request_id,
            attachment_id=attachment_id,
            actor_user_id=user.id,
        )
        return FileResponse(
            path=record.storage_path,
            media_type="application/zip",
            filename=record.original_filename,
        )
    except AttachmentNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "ATTACHMENT_NOT_FOUND", str(exc))
