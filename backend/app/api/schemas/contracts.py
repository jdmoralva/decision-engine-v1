from typing import Any

from pydantic import BaseModel, Field


class DocumentRef(BaseModel):
    document_type: str = Field(min_length=1)
    document_number: str = Field(min_length=1)


class ActorRef(BaseModel):
    user_id: str | None = None
    username: str = Field(min_length=1)


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


class PLDEvaluationContext(BaseModel):
    campaign_code: str | None = None
    customer_type: str | None = None
    profile_code: str | None = None
    sunedu_flag: str | None = None
    employment_status: str | None = None
    validated_income: float | None = None
    reported_debt: float | None = None


class AppliedVersions(BaseModel):
    rule_set_version: str | None = None
    parameter_version: str | None = None
    pipeline_version: str | None = None


class EvaluationRequest(BaseModel):
    product_code: str = Field(min_length=1)
    document: DocumentRef
    requested_by: ActorRef
    product_context: PLDEvaluationContext
    external_inputs: list[ExternalInputSnapshotItem] = Field(default_factory=list)


class PLDEvaluationResult(BaseModel):
    segment_code: str | None = None
    reviewed_income: float | None = None
    rci: float | None = None
    offered_amount: float | None = None
    installment_amount: float | None = None
    rate: float | None = None
    term_months: int | None = None


class EvaluationResponse(BaseModel):
    evaluation_id: str
    product_code: str
    eligible: bool
    alerts: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    applied_versions: AppliedVersions
    decision_trace_id: str
    product_result: PLDEvaluationResult | None = None


class DecisionTraceNode(BaseModel):
    node_key: str
    node_type: str
    outcome: str


class DecisionTraceResponse(BaseModel):
    trace_id: str
    evaluation_id: str
    product_code: str
    applied_versions: AppliedVersions
    alerts: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
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
    status: str
    document: DocumentRef
    campaign_code: str | None = None
    requested_amount: float
    comment: str
    created_by: ActorRef


class CreditRequestStatusTransitionRequest(BaseModel):
    target_status: str = Field(min_length=1)
    comment: str | None = None
    changed_by: ActorRef
