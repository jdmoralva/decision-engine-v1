import asyncio
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEnginePLDRuntimeTests(unittest.TestCase):
    def test_pld_runtime_calculates_segment_metrics_and_offer(self):
        from backend.app.domain.decision_engine import (
            DecisionEngineOrchestrator,
            EngineEvaluationRequest,
        )
        from backend.app.products.pld.runtime import compile_pld_runtime

        runtime = compile_pld_runtime(workflow_code="standard")
        request = EngineEvaluationRequest(
            product_code="PLD",
            workflow_code="standard",
            document={"document_type": "DNI", "document_number": "12345678"},
            requested_by={"username": "analista"},
            product_context={
                "campaign_code": "PLD-01",
                "customer_type": "CLIENTE",
                "profile_code": "PERFIL 2",
                "sunedu_flag": "CON SUNEDU",
                "employment_status": "DEP",
                "validated_income": 3000,
                "reported_debt": 300,
                "initial_offered_amount": 12000,
                "existing_consumption_balance": 2000,
                "campaign_rate": 35,
                "campaign_term_months": 48,
            },
        )

        normalized = runtime.normalizer(request)
        result = asyncio.run(
            DecisionEngineOrchestrator(nodes=runtime.nodes).evaluate(normalized, runtime.strategy)
        )

        self.assertTrue(result.eligible)
        self.assertEqual(result.product_result["segment_code"], "CS_DEP")
        self.assertEqual(result.product_result["reviewed_income"], 3000.0)
        self.assertAlmostEqual(result.product_result["rci"], 0.1, places=4)
        self.assertEqual(result.product_result["offered_amount"], 10000.0)
        self.assertEqual(result.product_result["installment_amount"], 362.0)
        self.assertEqual(result.product_result["rate"], 0.35)
        self.assertEqual(result.product_result["term_months"], 48)
        self.assertEqual(result.alerts, [])
        self.assertEqual(result.blocks, [])

    def test_pld_runtime_emits_evaluation_alerts_for_low_income_high_rci_and_low_offer(self):
        from backend.app.domain.decision_engine import (
            DecisionEngineOrchestrator,
            EngineEvaluationRequest,
        )
        from backend.app.products.pld.runtime import compile_pld_runtime

        runtime = compile_pld_runtime(workflow_code="standard")
        request = EngineEvaluationRequest(
            product_code="PLD",
            workflow_code="standard",
            document={"document_type": "DNI", "document_number": "87654321"},
            requested_by={"username": "analista"},
            product_context={
                "campaign_code": "PLD-02",
                "customer_type": "NO CLIENTE",
                "profile_code": "PERFIL 1",
                "sunedu_flag": "SIN SUNEDU",
                "employment_status": "DEP",
                "validated_income": 1800,
                "reported_debt": 1200,
                "initial_offered_amount": 0,
                "existing_consumption_balance": 0,
            },
        )

        normalized = runtime.normalizer(request)
        result = asyncio.run(
            DecisionEngineOrchestrator(nodes=runtime.nodes).evaluate(normalized, runtime.strategy)
        )

        self.assertTrue(result.eligible)
        self.assertEqual(result.product_result["segment_code"], "SS_DEP")
        self.assertEqual(result.product_result["reviewed_income"], 1800.0)
        self.assertAlmostEqual(result.product_result["rci"], 1200 / 1800, places=4)
        self.assertEqual(result.product_result["offered_amount"], 0.0)
        self.assertEqual(result.product_result["installment_amount"], 0.0)
        self.assertEqual(result.product_result["rate"], 0.3)
        self.assertEqual(result.product_result["term_months"], 36)
        self.assertEqual(
            result.alerts,
            [
                "income_below_threshold",
                "offer_below_threshold",
                "rci_above_threshold",
            ],
        )
        self.assertEqual(result.blocks, [])


if __name__ == "__main__":
    unittest.main()
