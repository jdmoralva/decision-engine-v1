import asyncio
import math
import sys
import time
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


def _consultation_payload() -> dict:
    return {"document": {"document_type": "DNI", "document_number": "12345678"}}


def _evaluation_payload() -> dict:
    return {
        "product_code": "PLD",
        "workflow_code": "standard",
        "document": {"document_type": "DNI", "document_number": "12345678"},
        "requested_by": {"username": "analista"},
        "product_context": {
            "campaign_code": "PLD_48M",
            "customer_type": "CLIENTE",
            "profile_code": "PERFIL 1",
            "sunedu_flag": "CON SUNEDU",
            "employment_status": "DEP",
            "validated_income": 2500,
            "initial_offered_amount": 12000,
            "existing_consumption_balance": 300,
            "campaign_rate": 18.5,
            "campaign_term_months": 48,
        },
        "external_inputs": [
            {
                "source_type": "user_input",
                "source_key": "form:pld",
                "field_name": "reported_debt",
                "field_value": "400",
            }
        ],
    }


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return ordered[index]


class PerformanceValidationIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    def test_runtime_endpoints_meet_local_p95_targets(self):
        async def run_test():
            consultation_latencies: list[float] = []
            evaluation_latencies: list[float] = []

            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers = await self.auth_headers(client, "analista")

                for _ in range(5):
                    response = await client.post(
                        "/api/v1/loans/PLD/consultas",
                        headers=headers,
                        json=_consultation_payload(),
                    )
                    self.assertEqual(response.status_code, 200, response.text)
                    response = await client.post(
                        "/api/v1/loans/PLD/evaluaciones",
                        headers=headers,
                        json=_evaluation_payload(),
                    )
                    self.assertEqual(response.status_code, 201, response.text)

                for _ in range(30):
                    start = time.perf_counter()
                    response = await client.post(
                        "/api/v1/loans/PLD/consultas",
                        headers=headers,
                        json=_consultation_payload(),
                    )
                    consultation_latencies.append(time.perf_counter() - start)
                    self.assertEqual(response.status_code, 200, response.text)

                for _ in range(30):
                    start = time.perf_counter()
                    response = await client.post(
                        "/api/v1/loans/PLD/evaluaciones",
                        headers=headers,
                        json=_evaluation_payload(),
                    )
                    evaluation_latencies.append(time.perf_counter() - start)
                    self.assertEqual(response.status_code, 201, response.text)

            consultation_p95 = _p95(consultation_latencies)
            evaluation_p95 = _p95(evaluation_latencies)
            print(f"consultation_p95_seconds={consultation_p95:.4f}")
            print(f"evaluation_p95_seconds={evaluation_p95:.4f}")
            self.assertLessEqual(consultation_p95, 2.0)
            self.assertLessEqual(evaluation_p95, 4.0)

        asyncio.run(run_test())
