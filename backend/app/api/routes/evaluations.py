from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.schemas.contracts import (
    DecisionTraceResponse,
    EvaluationRequest,
    EvaluationResponse,
    StructuredErrorResponse,
)
from backend.app.security.dependencies import require_permission
error_responses = {
    400: {"model": StructuredErrorResponse, "description": "Business validation error."},
    401: {"model": StructuredErrorResponse, "description": "Authentication required."},
    403: {"model": StructuredErrorResponse, "description": "Forbidden."},
    404: {"model": StructuredErrorResponse, "description": "Resource not found."},
    409: {"model": StructuredErrorResponse, "description": "Conflicting request state."},
    422: {"description": "Request validation error."},
    501: {"model": StructuredErrorResponse, "description": "Not implemented yet."},
}


router = APIRouter(prefix="/loans/{product_code}/evaluaciones", tags=["evaluations"])


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_evaluation(
    product_code: str,
    _payload: EvaluationRequest,
    _context: tuple = Depends(require_permission("evaluar_oferta")),
) -> EvaluationResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Evaluation execution for product '{product_code}' is not implemented yet.",
    )


@router.get("/{evaluation_id}", response_model=EvaluationResponse, responses=error_responses)
def get_evaluation(
    product_code: str,
    evaluation_id: str,
    _context: tuple = Depends(require_permission("consultar_evaluacion")),
) -> EvaluationResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            f"Evaluation '{evaluation_id}' retrieval for product '{product_code}' "
            "is not implemented yet."
        ),
    )


@router.get("/{evaluation_id}/trace", response_model=DecisionTraceResponse, responses=error_responses)
def get_decision_trace(
    product_code: str,
    evaluation_id: str,
    _context: tuple = Depends(require_permission("consultar_trace")),
) -> DecisionTraceResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            f"Decision trace for evaluation '{evaluation_id}' and product '{product_code}' "
            "is not implemented yet."
        ),
    )
