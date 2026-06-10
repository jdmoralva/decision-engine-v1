import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEnginePipelineTests(unittest.TestCase):
    def test_orchestrator_executes_async_pipeline_and_records_branching(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineOrchestrator,
            DecisionNode,
            EngineEvaluationRequest,
            NodeExecutionResult,
            PipelineNodeDefinition,
            PipelineStrategy,
        )

        class EligibilityNode(DecisionNode):
            node_key = "eligibility"
            node_type = "eligibility"

            async def run(self, context):
                context.product_result["score"] = 720
                return NodeExecutionResult(outcome="eligible", alerts_added=["manual_review"])

        class OfferNode(DecisionNode):
            node_key = "offer"
            node_type = "offer"

            async def run(self, context):
                context.product_result["offer_amount"] = 1500
                return NodeExecutionResult(outcome="completed", eligible=True)

        strategy = PipelineStrategy(
            strategy_key="default",
            product_code="PLD",
            start_node_key="eligibility",
            applied_versions=AppliedVersions(
                rule_set_version="rules-v1",
                parameter_version="params-v1",
                pipeline_version="pipe-v1",
            ),
            nodes=[
                PipelineNodeDefinition(
                    node_key="eligibility",
                    node_type="eligibility",
                    next_node_map={"eligible": "offer"},
                ),
                PipelineNodeDefinition(
                    node_key="offer",
                    node_type="offer",
                    next_node_map={},
                ),
            ],
        )
        orchestrator = DecisionEngineOrchestrator(nodes=[EligibilityNode(), OfferNode()])
        request = EngineEvaluationRequest(
            product_code="PLD",
            document={"document_type": "DNI", "document_number": "12345678"},
            requested_by={"username": "analista"},
            product_context={"campaign_code": "PLD-01"},
        )

        result = asyncio.run(orchestrator.evaluate(request, strategy))

        self.assertTrue(result.eligible)
        self.assertEqual(result.product_result["score"], 720)
        self.assertEqual(result.product_result["offer_amount"], 1500)
        self.assertEqual(result.applied_versions.pipeline_version, "pipe-v1")
        self.assertEqual(
            [node.node_key for node in result.decision_trace.nodes_executed],
            ["eligibility", "offer"],
        )
        self.assertEqual(result.decision_trace.nodes_executed[0].branch_selected, "offer")
        self.assertEqual(result.alerts, ["manual_review"])

    def test_orchestrator_rejects_invalid_topology(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineOrchestrator,
            DecisionNode,
            DecisionTopologyError,
            PipelineNodeDefinition,
            PipelineStrategy,
        )

        class EligibilityNode(DecisionNode):
            node_key = "eligibility"
            node_type = "eligibility"

            async def run(self, context):
                return None

        strategy = PipelineStrategy(
            strategy_key="broken",
            product_code="GENERIC",
            start_node_key="missing",
            applied_versions=AppliedVersions(),
            nodes=[
                PipelineNodeDefinition(
                    node_key="eligibility",
                    node_type="eligibility",
                    next_node_map={},
                )
            ],
        )

        with self.assertRaises(DecisionTopologyError):
            DecisionEngineOrchestrator(nodes=[EligibilityNode()]).validate_strategy(strategy)

    def test_orchestrator_rejects_cyclic_topology(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineOrchestrator,
            DecisionNode,
            DecisionTopologyError,
            PipelineNodeDefinition,
            PipelineStrategy,
        )

        class StartNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                raise AssertionError("run should not be reached for invalid topology")

        class ReviewNode(DecisionNode):
            node_key = "review"
            node_type = "shared"

            async def run(self, context):
                raise AssertionError("run should not be reached for invalid topology")

        strategy = PipelineStrategy(
            strategy_key="cyclic",
            product_code="GENERIC",
            start_node_key="start",
            applied_versions=AppliedVersions(),
            nodes=[
                PipelineNodeDefinition(
                    node_key="start",
                    node_type="shared",
                    next_node_map={"next": "review"},
                ),
                PipelineNodeDefinition(
                    node_key="review",
                    node_type="shared",
                    next_node_map={"retry": "start"},
                ),
            ],
        )

        with self.assertRaises(DecisionTopologyError):
            DecisionEngineOrchestrator(nodes=[StartNode(), ReviewNode()]).validate_strategy(
                strategy
            )
