import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEngineRegistryTests(unittest.TestCase):
    def test_registry_resolves_multiple_products_without_pld_specific_core(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineOrchestrator,
            DecisionEngineRegistry,
            DecisionNode,
            EngineEvaluationRequest,
            NodeExecutionResult,
            PipelineNodeDefinition,
            PipelineStrategy,
        )

        class SharedNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                context.product_result["product"] = context.request.product_code
                return NodeExecutionResult(outcome="done", eligible=True)

        registry = DecisionEngineRegistry()
        strategy_a = PipelineStrategy(
            strategy_key="strategy-a",
            product_code="ALPHA",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="alpha-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )
        strategy_b = PipelineStrategy(
            strategy_key="strategy-b",
            product_code="BETA",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="beta-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )

        registry.register_product(
            product_code="ALPHA",
            strategy=strategy_a,
            normalizer=lambda request: request,
            nodes=[SharedNode()],
        )
        registry.register_product(
            product_code="BETA",
            strategy=strategy_b,
            normalizer=lambda request: request,
            nodes=[SharedNode()],
        )

        alpha_runtime = registry.resolve("ALPHA")
        beta_runtime = registry.resolve("BETA")
        alpha_result = asyncio.run(
            DecisionEngineOrchestrator(nodes=alpha_runtime.nodes).evaluate(
                EngineEvaluationRequest(
                    product_code="ALPHA",
                    document={"document_type": "DNI", "document_number": "12345678"},
                    requested_by={"username": "analista"},
                    product_context={},
                ),
                alpha_runtime.strategy,
            )
        )
        beta_result = asyncio.run(
            DecisionEngineOrchestrator(nodes=beta_runtime.nodes).evaluate(
                EngineEvaluationRequest(
                    product_code="BETA",
                    document={"document_type": "DNI", "document_number": "12345678"},
                    requested_by={"username": "analista"},
                    product_context={},
                ),
                beta_runtime.strategy,
            )
        )

        self.assertEqual(alpha_runtime.strategy.applied_versions.pipeline_version, "alpha-v1")
        self.assertEqual(beta_runtime.strategy.applied_versions.pipeline_version, "beta-v1")
        self.assertEqual(alpha_result.product_result["product"], "ALPHA")
        self.assertEqual(beta_result.product_result["product"], "BETA")

    def test_registry_rejects_unknown_product(self):
        from backend.app.domain.decision_engine import (
            DecisionEngineRegistry,
            EngineRegistryError,
        )

        registry = DecisionEngineRegistry()

        with self.assertRaises(EngineRegistryError):
            registry.resolve("UNKNOWN")
