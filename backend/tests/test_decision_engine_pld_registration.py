import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEnginePLDRegistrationTests(unittest.TestCase):
    def test_pld_definition_exposes_standard_workflow_and_core_variables(self):
        from backend.app.domain.decision_engine import build_pld_product_definition

        product = build_pld_product_definition()

        self.assertEqual(product.product_code, "PLD")
        self.assertEqual(product.workflows[0].workflow_code, "standard")
        variable_keys = {item.variable_key for item in product.workflows[0].variables}
        self.assertTrue(
            {
                "campaign_code",
                "customer_type",
                "profile_code",
                "sunedu_flag",
                "employment_status",
                "validated_income",
                "reported_debt",
                "segment_code",
                "reviewed_income",
                "rci",
                "offered_amount",
                "installment_amount",
                "rate",
                "term_months",
            }.issubset(variable_keys)
        )

    def test_pld_runtime_compiles_on_generic_infrastructure(self):
        from backend.app.domain.decision_engine import compile_pld_runtime

        runtime = compile_pld_runtime(workflow_code="standard")

        self.assertEqual(runtime.product_code, "PLD")
        self.assertEqual(runtime.workflow_code, "standard")
        self.assertEqual(runtime.strategy.product_code, "PLD")
        self.assertEqual(runtime.strategy.start_node_key, "collect_context")
        self.assertEqual(runtime.normalizer.__name__, "normalize_evaluation_request")
        self.assertEqual([node.node_key for node in runtime.nodes], [
            "collect_context",
            "check_eligibility",
            "calculate_metrics",
            "build_decision",
        ])

    def test_default_registry_registers_pld_standard_runtime(self):
        from backend.app.domain.decision_engine import build_default_decision_engine_registry

        registry = build_default_decision_engine_registry()

        runtime = registry.resolve("PLD", "standard")

        self.assertEqual(runtime.product_code, "PLD")
        self.assertEqual(runtime.workflow_code, "standard")
        self.assertEqual(runtime.strategy.applied_versions.pipeline_version, "pld.standard.pipeline.v1")


if __name__ == "__main__":
    unittest.main()
