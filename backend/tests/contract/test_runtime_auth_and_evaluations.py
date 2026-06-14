import asyncio
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


class RuntimeAuthAndEvaluationsContractTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    def test_openapi_exposes_auth_consultation_and_evaluation_contracts(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                response = await client.get("/openapi.json")

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            paths = payload["paths"]

            for path in (
                "/api/v1/auth/login",
                "/api/v1/me",
                "/api/v1/loans/{product_code}/consultas",
                "/api/v1/loans/{product_code}/evaluaciones",
                "/api/v1/loans/{product_code}/evaluaciones/{evaluation_id}",
                "/api/v1/loans/{product_code}/evaluaciones/{evaluation_id}/trace",
            ):
                self.assertIn(path, paths)

            schemas = payload["components"]["schemas"]
            for schema_name in (
                "LoginRequest",
                "TokenResponse",
                "MeResponse",
                "LoanConsultationRequest",
                "LoanConsultationResponse",
                "EvaluationRequest",
                "EvaluationResponse",
                "DecisionTraceResponse",
            ):
                self.assertIn(schema_name, schemas)

        asyncio.run(run_test())

    def test_analista_can_bootstrap_session_consult_evaluate_and_fetch_trace(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                token = await self.login(client, "analista")
                headers = {"Authorization": f"Bearer {token}"}

                me_response = await client.get("/api/v1/me", headers=headers)
                self.assertEqual(me_response.status_code, 200)
                self.assertEqual(me_response.json()["username"], "analista")

                consultation_response = await client.post(
                    "/api/v1/loans/PLD/consultas",
                    headers=headers,
                    json={"document": {"document_type": "DNI", "document_number": "12345678"}},
                )
                self.assertEqual(consultation_response.status_code, 200, consultation_response.text)

                evaluation_response = await client.post(
                    "/api/v1/loans/PLD/evaluaciones",
                    headers=headers,
                    json={
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
                    },
                )
                self.assertEqual(evaluation_response.status_code, 201, evaluation_response.text)
                evaluation_payload = evaluation_response.json()
                self.assertEqual(evaluation_payload["product_code"], "PLD")
                self.assertIn("evaluation_id", evaluation_payload)
                self.assertIn("decision_trace_id", evaluation_payload)

                detail_response = await client.get(
                    f"/api/v1/loans/PLD/evaluaciones/{evaluation_payload['evaluation_id']}",
                    headers=headers,
                )
                self.assertEqual(detail_response.status_code, 200, detail_response.text)
                self.assertEqual(detail_response.json()["evaluation_id"], evaluation_payload["evaluation_id"])

                trace_response = await client.get(
                    f"/api/v1/loans/PLD/evaluaciones/{evaluation_payload['evaluation_id']}/trace",
                    headers=headers,
                )
                self.assertEqual(trace_response.status_code, 200, trace_response.text)
                self.assertEqual(trace_response.json()["evaluation_id"], evaluation_payload["evaluation_id"])

        asyncio.run(run_test())

    def test_auditor_cannot_execute_evaluation_but_can_consult_trace(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                analista_headers = await self.auth_headers(client, "analista")
                auditor_headers = await self.auth_headers(client, "auditor")

                create_response = await client.post(
                    "/api/v1/loans/PLD/evaluaciones",
                    headers=analista_headers,
                    json={
                        "product_code": "PLD",
                        "workflow_code": "standard",
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "requested_by": {"username": "analista"},
                        "product_context": {
                            "campaign_code": "PLD_48M",
                            "validated_income": 2500,
                        },
                        "external_inputs": [
                            {
                                "source_type": "user_input",
                                "source_key": "form:pld",
                                "field_name": "reported_debt",
                                "field_value": "100",
                            }
                        ],
                    },
                )
                self.assertEqual(create_response.status_code, 201, create_response.text)
                evaluation_id = create_response.json()["evaluation_id"]

                forbidden_response = await client.post(
                    "/api/v1/loans/PLD/evaluaciones",
                    headers=auditor_headers,
                    json={
                        "product_code": "PLD",
                        "workflow_code": "standard",
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "requested_by": {"username": "auditor"},
                        "product_context": {"campaign_code": "PLD_48M", "validated_income": 2500},
                    },
                )
                self.assertEqual(forbidden_response.status_code, 403)

                trace_response = await client.get(
                    f"/api/v1/loans/PLD/evaluaciones/{evaluation_id}/trace",
                    headers=auditor_headers,
                )
                self.assertEqual(trace_response.status_code, 200, trace_response.text)

        asyncio.run(run_test())
