from dataclasses import dataclass, field
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import LoanProduct


class UnsupportedLoanProductError(Exception):
    pass


class LoanConsultationNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class LoanConsultationCustomerData:
    customer_id: str
    full_name: str
    customer_type: str | None = None
    profile_code: str | None = None
    sunedu_flag: str | None = None
    employment_status: str | None = None
    validated_income: float | None = None


@dataclass(frozen=True)
class LoanConsultationCampaignData:
    campaign_code: str
    offered_amount: float | None = None
    rate: float | None = None
    term_months: int | None = None
    installment_amount: float | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LoanConsultationResult:
    product_code: str
    document_type: str
    document_number: str
    customer: LoanConsultationCustomerData
    campaigns: list[LoanConsultationCampaignData]


class LoanConsultationProvider(Protocol):
    async def consult(self, document_type: str, document_number: str) -> LoanConsultationResult | None: ...


class LoanConsultationService:
    def __init__(self, db: Session, provider_registry: dict[str, LoanConsultationProvider]):
        self._db = db
        self._provider_registry = provider_registry

    async def consult(self, product_code: str, document_type: str, document_number: str) -> LoanConsultationResult:
        normalized_product_code = product_code.strip().upper()
        normalized_document_type = document_type.strip().upper()
        normalized_document_number = document_number.strip()

        product = self._db.execute(
            select(LoanProduct).where(
                LoanProduct.code == normalized_product_code,
                LoanProduct.is_active.is_(True),
            )
        ).scalar_one_or_none()
        if product is None:
            raise UnsupportedLoanProductError(f"Loan product '{normalized_product_code}' is not available.")

        provider = self._provider_registry.get(normalized_product_code)
        if provider is None:
            raise UnsupportedLoanProductError(
                f"Loan product '{normalized_product_code}' does not have a consultation provider configured."
            )

        result = await provider.consult(normalized_document_type, normalized_document_number)
        if result is None:
            raise LoanConsultationNotFoundError(
                f"Customer '{normalized_document_type}-{normalized_document_number}' was not found for product '{normalized_product_code}'."
            )

        return result
