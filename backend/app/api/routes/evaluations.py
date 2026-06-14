from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.app.api.schemas.contracts import (
    ContractError,
    DecisionTraceResponse,
    EvaluationRequest,
    EvaluationResponse,
    StructuredErrorResponse,
)
from backend.app.application.evaluations.service import (
    EvaluationNotFoundError,
    EvaluationRuntimeUnavailableError,
    EvaluationService,
    EvaluationValidationError,
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


def _structured_error(status_code: int, code: str, message: str) -> JSONResponse:
    payload = StructuredErrorResponse(error=ContractError(code=code, message=message))
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED, responses=error_responses)
async def create_evaluation(
    product_code: str,
    payload: EvaluationRequest,
    context: tuple = Depends(require_permission("evaluar_oferta")),
) -> EvaluationResponse | JSONResponse:
    user, _roles = context
    service = EvaluationService()
    try:
        return await service.create_evaluation(
            product_code=product_code,
            payload=payload,
            actor_user_id=user.id,
            actor_username=user.username,
        )
    except EvaluationValidationError as exc:
        return _structured_error(status.HTTP_400_BAD_REQUEST, "EVALUATION_VALIDATION", str(exc))
    except EvaluationRuntimeUnavailableError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "RUNTIME_NOT_AVAILABLE", str(exc))


@router.get("/{evaluation_id}", response_model=EvaluationResponse, responses=error_responses)
def get_evaluation(
    product_code: str,
    evaluation_id: str,
    _context: tuple = Depends(require_permission("consultar_evaluacion")),
) -> EvaluationResponse | JSONResponse:
    service = EvaluationService()
    try:
        return service.get_evaluation(product_code=product_code, evaluation_id=evaluation_id)
    except EvaluationNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "EVALUATION_NOT_FOUND", str(exc))


@router.get("/{evaluation_id}/trace", response_model=DecisionTraceResponse, responses=error_responses)
def get_decision_trace(
    product_code: str,
    evaluation_id: str,
    _context: tuple = Depends(require_permission("consultar_trace")),
) -> DecisionTraceResponse | JSONResponse:
    service = EvaluationService()
    try:
        return service.get_trace(product_code=product_code, evaluation_id=evaluation_id)
    except EvaluationNotFoundError as exc:
        return _structured_error(status.HTTP_404_NOT_FOUND, "EVALUATION_NOT_FOUND", str(exc))
