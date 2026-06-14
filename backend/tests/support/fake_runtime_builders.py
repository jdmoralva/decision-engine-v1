from backend.app.domain.decision_engine.contracts import AppliedVersions
from backend.app.domain.decision_engine.nodes import DecisionNode
from backend.app.domain.decision_engine.normalization import normalize_evaluation_request
from backend.app.domain.decision_engine.pipeline import PipelineNodeDefinition, PipelineStrategy
from backend.app.domain.decision_engine.runtime_definitions import (
    ProductDefinition,
    ProductRuntime,
    WorkflowDefinition,
    compile_product_runtime,
)


class FakeDecisionNode(DecisionNode):
    node_key = "start"
    node_type = "noop"

    async def run(self, _context):
        from backend.app.domain.decision_engine.nodes import NodeExecutionResult

        return NodeExecutionResult(outcome="done", eligible=True)


def compile_fake_runtime(workflow_code: str = "standard") -> ProductRuntime:
    return compile_product_runtime(
        product_definition=ProductDefinition(
            product_code="TEST",
            name="Test product",
            workflows=[
                WorkflowDefinition(
                    workflow_code=workflow_code,
                    product_code="TEST",
                    name="Test workflow",
                    pipeline_version="test.pipeline.v1",
                    rule_pack_version="test.rules.v1",
                )
            ],
        ),
        workflow_code=workflow_code,
        strategy=PipelineStrategy(
            strategy_key="test.standard",
            product_code="TEST",
            start_node_key="start",
            applied_versions=AppliedVersions(
                rule_set_version="test.rules.v1",
                parameter_version="test.parameters.v1",
                pipeline_version="test.pipeline.v1",
            ),
            nodes=[
                PipelineNodeDefinition(
                    node_key="start",
                    node_type="noop",
                    next_node_map={},
                )
            ],
        ),
        normalizer=normalize_evaluation_request,
        nodes=[FakeDecisionNode()],
    )
