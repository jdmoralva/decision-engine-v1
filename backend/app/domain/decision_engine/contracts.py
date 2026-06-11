from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EngineDocumentRef(BaseModel):
    document_type: str = Field(min_length=1)
    document_number: str = Field(min_length=1)


class EngineActorRef(BaseModel):
    user_id: str | None = None
    username: str = Field(min_length=1)


class EngineExternalInput(BaseModel):
    source_type: str = Field(min_length=1)
    source_key: str = Field(min_length=1)
    field_name: str = Field(min_length=1)
    field_value: str
    used_by_engine: bool = True


class AppliedVersions(BaseModel):
    rule_set_version: str | None = None
    parameter_version: str | None = None
    pipeline_version: str | None = None


class EngineEvaluationRequest(BaseModel):
    product_code: str = Field(min_length=1)
    workflow_code: str = Field(min_length=1)
    document: EngineDocumentRef
    requested_by: EngineActorRef
    product_context: dict[str, object]
    external_inputs: list[EngineExternalInput] = Field(default_factory=list)
    requested_rule_set_version: str | None = None
    requested_pipeline_version: str | None = None


class EngineDecisionEvidence(BaseModel):
    source_type: str
    source_key: str
    field_name: str
    field_value: str


class EngineDecisionTraceNode(BaseModel):
    node_key: str
    node_type: str
    outcome: str
    branch_selected: str | None = None
    alerts_added: list[str] = Field(default_factory=list)
    blocks_added: list[str] = Field(default_factory=list)
    rules_applied: list[str] = Field(default_factory=list)
    consumed_variables: list[str] = Field(default_factory=list)
    produced_variables: list[str] = Field(default_factory=list)
    produced_effects: list[str] = Field(default_factory=list)
    evidence_keys: list[str] = Field(default_factory=list)


class EngineDecisionTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    product_code: str
    workflow_code: str
    applied_versions: AppliedVersions = Field(default_factory=AppliedVersions)
    alerts: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    rules_applied: list[str] = Field(default_factory=list)
    consumed_variables: list[str] = Field(default_factory=list)
    produced_variables: list[str] = Field(default_factory=list)
    produced_effects: list[str] = Field(default_factory=list)
    nodes_executed: list[EngineDecisionTraceNode] = Field(default_factory=list)
    evidence: list[EngineDecisionEvidence] = Field(default_factory=list)
    final_outcome: str | None = None


class EngineEvaluationResult(BaseModel):
    product_code: str
    eligible: bool
    alerts: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    applied_versions: AppliedVersions = Field(default_factory=AppliedVersions)
    product_result: dict[str, Any] = Field(default_factory=dict)
    decision_trace: EngineDecisionTrace
