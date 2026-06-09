from fastapi import APIRouter, HTTPException, status

from backend.app.api.schemas.contracts import (
    CreditRequestCreateRequest,
    CreditRequestResponse,
    CreditRequestStatusTransitionRequest,
    StructuredErrorResponse,
)


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
def create_credit_request(_payload: CreditRequestCreateRequest) -> CreditRequestResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Credit request creation is not implemented yet.",
    )


@router.get("/{request_id}", response_model=CreditRequestResponse, responses=error_responses)
def get_credit_request(request_id: str) -> CreditRequestResponse:
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
) -> CreditRequestResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Status transition for credit request '{request_id}' is not implemented yet.",
    )
