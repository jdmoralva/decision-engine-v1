from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.schemas.contracts import (
    CreditRequestCreateRequest,
    CreditRequestResponse,
    CreditRequestStatusTransitionRequest,
    StructuredErrorResponse,
)
from backend.app.security.dependencies import get_current_user_context, require_permission
from backend.app.security.permissions import roles_grant_permission


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


@router.post("", response_model=CreditRequestResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_credit_request(
    _payload: CreditRequestCreateRequest,
    _context: tuple = Depends(require_permission("registrar_solicitud")),
) -> CreditRequestResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Credit request creation is not implemented yet.",
    )


@router.get("/{request_id}", response_model=CreditRequestResponse, responses=error_responses)
def get_credit_request(
    request_id: str,
    _context: tuple = Depends(require_permission("consultar_solicitud")),
) -> CreditRequestResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Credit request '{request_id}' retrieval is not implemented yet.",
    )


@router.post(
    "/{request_id}/status-transitions",
    response_model=CreditRequestResponse,
    responses=error_responses,
)
def create_credit_request_status_transition(
    request_id: str,
    _payload: CreditRequestStatusTransitionRequest,
    context: tuple = Depends(get_current_user_context),
) -> CreditRequestResponse:
    _user, roles = context
    permission = (
        "anular_solicitud"
        if _payload.target_status.strip().lower() == "cancelled"
        else "cambiar_estado_solicitud"
    )
    if not roles_grant_permission(roles, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Status transition for credit request '{request_id}' is not implemented yet.",
    )
