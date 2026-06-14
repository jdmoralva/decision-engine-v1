from typing import Any

from pydantic import BaseModel, Field


class DocumentRef(BaseModel):
    document_type: str = Field(min_length=1)
    document_number: str = Field(min_length=1)


class ActorRef(BaseModel):
    user_id: str | None = None
    username: str = Field(
        min_length=1,
        description="Actor identity. Authorization is reevaluated on each protected request.",
    )


class ExternalInputSnapshotItem(BaseModel):
    source_type: str = Field(min_length=1)
    source_key: str = Field(min_length=1)
    field_name: str = Field(min_length=1)
    field_value: str
    used_by_engine: bool = True


class ContractError(BaseModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    details: list[dict[str, Any]] = Field(default_factory=list)


class StructuredErrorResponse(BaseModel):
    error: ContractError


class AppliedVersions(BaseModel):
    rule_set_version: str | None = None
    parameter_version: str | None = None
    pipeline_version: str | None = None


class LoanConsultationRequest(BaseModel):
    document: DocumentRef


class LoanConsultationCustomer(BaseModel):
    customer_id: str = Field(min_length=1)
    full_name: str = Field(min_length=1)
    customer_type: str | None = None
    profile_code: str | None = None
    sunedu_flag: str | None = None
    employment_status: str | None = None
    validated_income: float | None = None


class LoanConsultationCampaign(BaseModel):
    campaign_code: str = Field(min_length=1)
    offered_amount: float | None = None
    rate: float | None = None
    term_months: int | None = None
    installment_amount: float | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class LoanConsultationResponse(BaseModel):
    product_code: str = Field(min_length=1)
    document: DocumentRef
    customer: LoanConsultationCustomer
    campaigns: list[LoanConsultationCampaign] = Field(default_factory=list)


class EvaluationRequestBase(BaseModel):
    product_code: str = Field(min_length=1)
    workflow_code: str = Field(min_length=1)
    document: DocumentRef
    requested_by: ActorRef
    external_inputs: list[ExternalInputSnapshotItem] = Field(default_factory=list)
    requested_rule_set_version: str | None = None
    requested_pipeline_version: str | None = None


class EvaluationRequest(EvaluationRequestBase):
    product_context: dict[str, Any]


class EvaluationResponseBase(BaseModel):
    evaluation_id: str
    product_code: str
    eligible: bool
    alerts: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    applied_versions: AppliedVersions
    decision_trace_id: str


class EvaluationResponse(EvaluationResponseBase):
    product_result: dict[str, Any] | None = None


class DecisionTraceNode(BaseModel):
    node_key: str
    node_type: str
    outcome: str
    rules_applied: list[str] = Field(default_factory=list)
    consumed_variables: list[str] = Field(default_factory=list)
    produced_variables: list[str] = Field(default_factory=list)
    produced_effects: list[str] = Field(default_factory=list)


class DecisionTraceResponse(BaseModel):
    trace_id: str
    evaluation_id: str
    product_code: str
    applied_versions: AppliedVersions
    alerts: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    rules_applied: list[str] = Field(default_factory=list)
    consumed_variables: list[str] = Field(default_factory=list)
    produced_variables: list[str] = Field(default_factory=list)
    produced_effects: list[str] = Field(default_factory=list)
    nodes_executed: list[DecisionTraceNode] = Field(default_factory=list)
    evidence: list[ExternalInputSnapshotItem] = Field(default_factory=list)


class CreditRequestCreateRequest(BaseModel):
    product_code: str = Field(min_length=1)
    evaluation_id: str | None = None
    document: DocumentRef
    campaign_code: str | None = None
    requested_amount: float = Field(ge=0)
    comment: str = Field(min_length=1)
    created_by: ActorRef


class CreditRequestResponse(BaseModel):
    request_id: str
    product_code: str
    evaluation_id: str | None = None
    workflow_code: str | None = None
    status: str
    document: DocumentRef
    campaign_code: str | None = None
    requested_amount: float
    comment: str
    created_by: ActorRef


class CreditRequestStatusHistoryEntry(BaseModel):
    status: str
    comment: str | None = None
    changed_by: ActorRef
    changed_at: str


class CreditRequestAttachmentSummary(BaseModel):
    attachment_id: str
    original_filename: str
    mime_type: str
    uploaded_at: str


class CreditRequestDetailResponse(CreditRequestResponse):
    customer_name: str | None = None
    created_at: str
    updated_at: str
    offered_amount: float | None = None
    installment_amount: float | None = None
    term_months: int | None = None
    rate: float | None = None
    status_history: list[CreditRequestStatusHistoryEntry] = Field(default_factory=list)
    attachments: list[CreditRequestAttachmentSummary] = Field(default_factory=list)


class CreditRequestQueueItem(BaseModel):
    request_id: str
    product_code: str
    workflow_code: str | None = None
    evaluation_id: str | None = None
    document: DocumentRef
    customer_name: str | None = None
    status: str
    created_at: str
    updated_at: str
    available_actions: list[str] = Field(default_factory=list)


class CreditRequestQueueResponse(BaseModel):
    applied_filters: dict[str, str] = Field(default_factory=dict)
    items: list[CreditRequestQueueItem] = Field(default_factory=list)


class CreditRequestStatusTransitionRequest(BaseModel):
    target_status: str = Field(min_length=1)
    comment: str | None = None
    changed_by: ActorRef
