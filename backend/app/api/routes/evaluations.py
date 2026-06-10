from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.schemas.contracts import (
    DecisionTraceResponse,
    EvaluationRequest,
    EvaluationResponse,
    StructuredErrorResponse,
)
from backend.app.security.dependencies import require_permission


router = APIRouter(prefix="/evaluations", tags=["evaluations"])


error_responses = {
    400: {"model": StructuredErrorResponse, "description": "Business validation error."},
    401: {"model": StructuredErrorResponse, "description": "Authentication required."},
    403: {"model": StructuredErrorResponse, "description": "Forbidden."},
    404: {"model": StructuredErrorResponse, "description": "Resource not found."},
    409: {"model": StructuredErrorResponse, "description": "Conflicting request state."},
    422: {"description": "Request validation error."},
    501: {"model": StructuredErrorResponse, "description": "Not implemented yet."},
}


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
def create_evaluation(
    _payload: EvaluationRequest,
    _context: tuple = Depends(require_permission("evaluar_oferta")),
) -> EvaluationResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evaluation execution is not implemented yet.",
    )


@router.get("/{evaluation_id}", response_model=EvaluationResponse, responses=error_responses)
def get_evaluation(
    evaluation_id: str,
    _context: tuple = Depends(require_permission("consultar_evaluacion")),
) -> EvaluationResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Evaluation '{evaluation_id}' retrieval is not implemented yet.",
    )


@router.get("/{evaluation_id}/decision-trace", response_model=DecisionTraceResponse, responses=error_responses)
def get_decision_trace(
    evaluation_id: str,
    _context: tuple = Depends(require_permission("consultar_trace")),
) -> DecisionTraceResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Decision trace for evaluation '{evaluation_id}' is not implemented yet.",
    )
