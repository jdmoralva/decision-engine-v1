from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.api.schemas.contracts import (
    ContractError,
    DocumentRef,
    LoanConsultationCampaign,
    LoanConsultationCustomer,
    LoanConsultationRequest,
    LoanConsultationResponse,
    StructuredErrorResponse,
)
from backend.app.application.loan_consultations import (
    LoanConsultationNotFoundError,
    LoanConsultationService,
    UnsupportedLoanProductError,
)
from backend.app.infrastructure.db.session import get_db
from backend.app.infrastructure.loan_consultations import build_loan_consultation_provider_registry
from backend.app.security.dependencies import require_permission


router = APIRouter(prefix="/loans", tags=["loans"])


error_responses = {
    400: {"model": StructuredErrorResponse, "description": "Business validation error."},
    401: {"model": StructuredErrorResponse, "description": "Authentication required."},
    403: {"model": StructuredErrorResponse, "description": "Forbidden."},
    404: {"model": StructuredErrorResponse, "description": "Resource not found."},
    422: {"description": "Request validation error."},
}


def _structured_error(status_code: int, code: str, message: str) -> JSONResponse:
    payload = StructuredErrorResponse(error=ContractError(code=code, message=message))
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@router.post("/{product_code}/consultas", response_model=LoanConsultationResponse, responses=error_responses)
async def create_loan_consultation(
    product_code: str,
    payload: LoanConsultationRequest,
    _context: tuple = Depends(require_permission("consultar_cliente")),
    db: Session = Depends(get_db),
) -> LoanConsultationResponse | JSONResponse:
    service = LoanConsultationService(db=db, provider_registry=build_loan_consultation_provider_registry())

    try:
        result = await service.consult(
            product_code=product_code,
            document_type=payload.document.document_type,
            document_number=payload.document.document_number,
        )
    except UnsupportedLoanProductError as exc:
        return _structured_error(status_code=404, code="LOAN_PRODUCT_NOT_AVAILABLE", message=str(exc))
    except LoanConsultationNotFoundError as exc:
        return _structured_error(status_code=404, code="CUSTOMER_NOT_FOUND", message=str(exc))

    return LoanConsultationResponse(
        product_code=result.product_code,
        document=DocumentRef(document_type=result.document_type, document_number=result.document_number),
        customer=LoanConsultationCustomer(
            customer_id=result.customer.customer_id,
            full_name=result.customer.full_name,
            customer_type=result.customer.customer_type,
            profile_code=result.customer.profile_code,
            sunedu_flag=result.customer.sunedu_flag,
            employment_status=result.customer.employment_status,
            validated_income=result.customer.validated_income,
        ),
        campaigns=[
            LoanConsultationCampaign(
                campaign_code=campaign.campaign_code,
                offered_amount=campaign.offered_amount,
                rate=campaign.rate,
                term_months=campaign.term_months,
                installment_amount=campaign.installment_amount,
                metadata=campaign.metadata,
            )
            for campaign in result.campaigns
        ],
    )
