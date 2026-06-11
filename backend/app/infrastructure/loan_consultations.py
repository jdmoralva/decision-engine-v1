from backend.app.application.loan_consultations import (
    LoanConsultationCampaignData,
    LoanConsultationCustomerData,
    LoanConsultationProvider,
    LoanConsultationResult,
)


class InMemoryLoanConsultationProvider(LoanConsultationProvider):
    def __init__(self, product_code: str, records: dict[tuple[str, str], LoanConsultationResult]):
        self._product_code = product_code
        self._records = records

    async def consult(self, document_type: str, document_number: str) -> LoanConsultationResult | None:
        return self._records.get((document_type, document_number))


def build_loan_consultation_provider_registry() -> dict[str, LoanConsultationProvider]:
    pld_customer = LoanConsultationCustomerData(
        customer_id="customer-pld-12345678",
        full_name="Cliente Demo PLD",
        customer_type="CLIENTE",
        profile_code="PERFIL_2",
        sunedu_flag="CON_SUNEDU",
        employment_status="DEPENDIENTE",
        validated_income=4500.0,
    )
    pld_campaigns = [
        LoanConsultationCampaignData(
            campaign_code="PLD_48M",
            offered_amount=12500.0,
            rate=0.35,
            term_months=48,
            installment_amount=420.0,
            metadata={"source": "local-dev-adapter", "segment": "CS_DEP"},
        )
    ]

    return {
        "PLD": InMemoryLoanConsultationProvider(
            product_code="PLD",
            records={
                (
                    "DNI",
                    "12345678",
                ): LoanConsultationResult(
                    product_code="PLD",
                    document_type="DNI",
                    document_number="12345678",
                    customer=pld_customer,
                    campaigns=pld_campaigns,
                )
            },
        )
    }
