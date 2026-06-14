from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from backend.app.api.schemas.contracts import (
    ContractError,
    CreditRequestCreateRequest,
    CreditRequestDetailResponse,
    CreditRequestQueueResponse,
    CreditRequestResponse,
    CreditRequestStatusTransitionRequest,
    StructuredErrorResponse,
)
from backend.app.application.auth import get_permissions_for_roles
from backend.app.application.credit_requests.service import (
    CreditRequestNotFoundError,
    CreditRequestService,
    CreditRequestTransitionError,
    CreditRequestValidationError,
)
from backend.app.application.credit_requests.status_rules import normalize_credit_request_status
from backend.app.infrastructure.repositories.credit_requests import CreditRequestQueueFilters
from backend.app.infrastructure.db.session import get_db
from backend.app.security.dependencies import get_current_user_context, require_permission


router = APIRouter(prefix="/credit-requests", tags=["credit-requests"])


error_responses = {
    400: {"model": StructuredErrorResponse, "description": "Business validation error."},
    401: {"model": StructuredErrorResponse, "description": "Authentication required."},
    403: {"model": StructuredErrorResponse, "description": "Forbidden."},
    404: {"model": StructuredErrorResponse, "description": "Resource not found."},
    409: {"model": StructuredErrorResponse, "description": "Conflicting request state."},
    422: {"description": "Request validation error."},
    501: {"model": StructuredErrorResponse, "description": "Not implemented yet."},
}


def _structured_error(status_code_value: int, code: str, message: str) -> JSONResponse:
    payload = StructuredErrorResponse(error=ContractError(code=code, message=message))
    return JSONResponse(status_code=status_code_value, content=payload.model_dump())


def _require_queue_access(roles: list[str]) -> None:
    if not any(role in {"analista", "evaluador", "admin"} for role in roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def _build_filters(
    *,
    product_code: str | None,
    status: str | None,
    document_number: str | None,
    evaluation_id: str | None,
    from_date: date | None,
    to_date: date | None,
) -> CreditRequestQueueFilters:
    return CreditRequestQueueFilters(
        product_code=None if not product_code else product_code.strip().upper(),
        status=None if not status else normalize_credit_request_status(status),
        document_number=None if not document_number else document_number.strip(),
        evaluation_id=None if not evaluation_id else evaluation_id.strip(),
        from_date=from_date,
        to_date=to_date,
    )


@router.post("", response_model=CreditRequestResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_credit_request(
    payload: CreditRequestCreateRequest,
    context: tuple = Depends(require_permission("registrar_solicitud")),
) -> CreditRequestResponse | JSONResponse:
    user, _roles = context
    service = CreditRequestService()
    try:
        return service.create_credit_request(
            payload=payload,
            actor_user_id=user.id,
            actor_username=user.username,
        )
    except CreditRequestValidationError as exc:
        return _structured_error(status.HTTP_400_BAD_REQUEST, "CREDIT_REQUEST_VALIDATION", str(exc))


@router.get("/export", responses={**error_responses, 200: {"description": "CSV queue export."}})
def export_credit_requests(
    product_code: str | None = None,
    status: str | None = None,
    document_number: str | None = None,
    evaluation_id: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    context: tuple = Depends(require_permission("exportar_bandeja")),
) -> Response:
    user, roles = context
    service = CreditRequestService()
    export_payload = service.export_credit_requests(
        filters=_build_filters(
            product_code=product_code,
            status=status,
            document_number=document_number,
            evaluation_id=evaluation_id,
            from_date=from_date,
            to_date=to_date,
        ),
        actor_roles=roles,
        actor_user_id=user.id,
    )
    return Response(content=export_payload.content, media_type="text/csv; charset=utf-8")


@router.get("", response_model=CreditRequestQueueResponse, responses=error_responses)
def list_credit_requests(
    product_code: str | None = None,
    status: str | None = None,
    document_number: str | None = None,
    evaluation_id: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    context: tuple = Depends(require_permission("consultar_solicitud")),
) -> CreditRequestQueueResponse:
    _user, roles = context
    _require_queue_access(roles)
    service = CreditRequestService()
    filters = _build_filters(
        product_code=product_code,
        status=status,
        document_number=document_number,
        evaluation_id=evaluation_id,
        from_date=from_date,
        to_date=to_date,
    )
    return service.list_credit_requests(filters=filters, actor_roles=roles)


@router.get("/{request_id}", response_model=CreditRequestDetailResponse, responses=error_responses)
def get_credit_request(
    request_id: str,
    _context: tuple = Depends(require_permission("consultar_detalle_solicitud")),
) -> CreditRequestDetailResponse | JSONResponse:
    service = CreditRequestService()
    try:
        return service.get_credit_request(request_id=request_id)
    except CreditRequestNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "CREDIT_REQUEST_NOT_FOUND", str(exc))


@router.post(
    "/{request_id}/status-transitions",
    response_model=CreditRequestResponse,
    responses=error_responses,
)
def create_credit_request_status_transition(
    request_id: str,
    payload: CreditRequestStatusTransitionRequest,
    context: tuple = Depends(get_current_user_context),
    db: Session = Depends(get_db),
) -> CreditRequestResponse | JSONResponse:
    user, roles = context
    service = CreditRequestService()
    normalized_target = normalize_credit_request_status(payload.target_status)
    permissions = get_permissions_for_roles(db, roles)
    if normalized_target == "en_revision" and any(role in {"analista", "evaluador", "admin"} for role in roles):
        permissions = set(permissions) | {"cambiar_estado_solicitud"}

    permission = service.resolve_dynamic_permission(payload.target_status)
    if permission not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return service.transition_credit_request(
            request_id=request_id,
            payload=payload,
            actor_user_id=user.id,
            actor_username=user.username,
            actor_roles=roles,
        )
    except CreditRequestNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "CREDIT_REQUEST_NOT_FOUND", str(exc))
    except CreditRequestTransitionError as exc:
        return _structured_error(status.HTTP_409_CONFLICT, "CREDIT_REQUEST_TRANSITION_INVALID", str(exc))
