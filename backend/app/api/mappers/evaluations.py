from backend.app.api.schemas.contracts import (
    ActorRef,
    AppliedVersions,
    DecisionTraceNode,
    DecisionTraceResponse,
    DocumentRef,
    ExternalInputSnapshotItem,
    PLDEvaluationRequest,
    PLDEvaluationResponse,
    PLDEvaluationResult,
)
from backend.app.domain.decision_engine import (
    AppliedVersions as EngineAppliedVersions,
)
from backend.app.domain.decision_engine import (
    EngineDecisionTrace,
    EngineEvaluationRequest,
    EngineEvaluationResult,
    EngineExternalInput,
)


def map_api_request_to_engine_request(api_request: PLDEvaluationRequest) -> EngineEvaluationRequest:
    return EngineEvaluationRequest(
        product_code=api_request.product_code,
        workflow_code=api_request.workflow_code,
        document=api_request.document.model_dump(),
        requested_by=api_request.requested_by.model_dump(),
        product_context=api_request.product_context.model_dump(exclude_none=True),
        external_inputs=[
            EngineExternalInput(**item.model_dump()) for item in api_request.external_inputs
        ],
        requested_rule_set_version=api_request.requested_rule_set_version,
        requested_pipeline_version=api_request.requested_pipeline_version,
    )


def map_engine_result_to_api_response(
    *,
    evaluation_id: str,
    engine_result: EngineEvaluationResult,
) -> PLDEvaluationResponse:
    return PLDEvaluationResponse(
        evaluation_id=evaluation_id,
        product_code=engine_result.product_code,
        eligible=engine_result.eligible,
        alerts=list(engine_result.alerts),
        blocks=list(engine_result.blocks),
        applied_versions=_map_applied_versions(engine_result.applied_versions),
        decision_trace_id=engine_result.decision_trace.trace_id,
        product_result=_map_product_result(
            product_code=engine_result.product_code,
            product_result=engine_result.product_result,
        ),
    )


def map_engine_trace_to_api_response(
    *,
    evaluation_id: str,
    engine_trace: EngineDecisionTrace,
) -> DecisionTraceResponse:
    return DecisionTraceResponse(
        trace_id=engine_trace.trace_id,
        evaluation_id=evaluation_id,
        product_code=engine_trace.product_code,
        applied_versions=_map_applied_versions(engine_trace.applied_versions),
        alerts=list(engine_trace.alerts),
        blocks=list(engine_trace.blocks),
        rules_applied=list(engine_trace.rules_applied),
        consumed_variables=list(engine_trace.consumed_variables),
        produced_variables=list(engine_trace.produced_variables),
        produced_effects=list(engine_trace.produced_effects),
        nodes_executed=[
            DecisionTraceNode(
                node_key=node.node_key,
                node_type=node.node_type,
                outcome=node.outcome,
                rules_applied=list(node.rules_applied),
                consumed_variables=list(node.consumed_variables),
                produced_variables=list(node.produced_variables),
                produced_effects=list(node.produced_effects),
            )
            for node in engine_trace.nodes_executed
        ],
        evidence=[
            ExternalInputSnapshotItem(
                source_type=item.source_type,
                source_key=item.source_key,
                field_name=item.field_name,
                field_value=item.field_value,
                used_by_engine=True,
            )
            for item in engine_trace.evidence
        ],
    )


def map_engine_request_to_api_request(engine_request: EngineEvaluationRequest) -> PLDEvaluationRequest:
    return PLDEvaluationRequest(
        product_code=engine_request.product_code,
        workflow_code=engine_request.workflow_code,
        document=DocumentRef(**engine_request.document.model_dump()),
        requested_by=ActorRef(**engine_request.requested_by.model_dump()),
        product_context=engine_request.product_context,
        external_inputs=[
            ExternalInputSnapshotItem(**item.model_dump())
            for item in engine_request.external_inputs
        ],
        requested_rule_set_version=engine_request.requested_rule_set_version,
        requested_pipeline_version=engine_request.requested_pipeline_version,
    )


def _map_applied_versions(applied_versions: EngineAppliedVersions) -> AppliedVersions:
    return AppliedVersions(**applied_versions.model_dump())


def _map_product_result(
    *,
    product_code: str,
    product_result: dict[str, object],
) -> PLDEvaluationResult | None:
    if product_code.strip().upper() != "PLD":
        return None

    allowed_fields = PLDEvaluationResult.model_fields.keys()
    projected_result = {
        key: value for key, value in product_result.items() if key in allowed_fields
    }
    return PLDEvaluationResult(**projected_result)
