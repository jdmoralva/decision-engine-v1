import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEnginePLDRegistrationTests(unittest.TestCase):
    def test_pld_definition_exposes_standard_workflow_and_core_variables(self):
        from backend.app.products.pld.runtime import build_pld_product_definition

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
        from backend.app.products.pld.runtime import compile_pld_runtime

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

    def test_default_registry_registers_runtimes_from_configuration(self):
        from backend.app.domain.decision_engine import build_default_decision_engine_registry
        from backend.app.config.settings import clear_settings_cache

        with patch.dict(
            "os.environ",
            {"DECISION_ENGINE_RUNTIME_BUILDERS": "backend.tests.support.fake_runtime_builders:compile_fake_runtime"},
            clear=False,
        ):
            clear_settings_cache()
            registry = build_default_decision_engine_registry()
            clear_settings_cache()

        runtime = registry.resolve("TEST", "standard")

        self.assertEqual(runtime.product_code, "TEST")
        self.assertEqual(runtime.workflow_code, "standard")
        self.assertEqual(runtime.strategy.applied_versions.pipeline_version, "test.pipeline.v1")

    def test_default_registry_starts_empty_without_configured_builders(self):
        from backend.app.config.settings import clear_settings_cache
        from backend.app.domain.decision_engine import build_default_decision_engine_registry
        from backend.app.domain.decision_engine.exceptions import UnknownProductError

        with patch.dict("os.environ", {"DECISION_ENGINE_RUNTIME_BUILDERS": ""}, clear=False):
            clear_settings_cache()
            registry = build_default_decision_engine_registry()
            clear_settings_cache()

        with self.assertRaises(UnknownProductError):
            registry.resolve("PLD", "standard")


if __name__ == "__main__":
    unittest.main()
