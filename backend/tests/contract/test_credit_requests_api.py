import asyncio
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


class CreditRequestsContractTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    async def _create_evaluation(self, client: AsyncClient, username: str = "analista") -> tuple[dict[str, str], str]:
        headers = await self.auth_headers(client, username)
        response = await client.post(
            "/api/v1/loans/PLD/evaluaciones",
            headers=headers,
            json={
                "product_code": "PLD",
                "workflow_code": "standard",
                "document": {"document_type": "DNI", "document_number": "12345678"},
                "requested_by": {"username": username},
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
        self.assertEqual(response.status_code, 201, response.text)
        return headers, response.json()["evaluation_id"]

    def test_openapi_exposes_credit_request_detail_queue_and_export_contracts(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                response = await client.get("/openapi.json")

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            paths = payload["paths"]

            for path in (
                "/api/v1/credit-requests",
                "/api/v1/credit-requests/export",
                "/api/v1/credit-requests/{request_id}",
                "/api/v1/credit-requests/{request_id}/status-transitions",
            ):
                self.assertIn(path, paths)

            schemas = payload["components"]["schemas"]
            for schema_name in (
                "CreditRequestCreateRequest",
                "CreditRequestResponse",
                "CreditRequestDetailResponse",
                "CreditRequestQueueResponse",
                "CreditRequestStatusTransitionRequest",
            ):
                self.assertIn(schema_name, schemas)

        asyncio.run(run_test())

    def test_analista_can_register_detail_queue_and_move_request_to_en_revision(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers, evaluation_id = await self._create_evaluation(client)

                create_response = await client.post(
                    "/api/v1/credit-requests",
                    headers=headers,
                    json={
                        "product_code": "PLD",
                        "evaluation_id": evaluation_id,
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "campaign_code": "PLD_48M",
                        "requested_amount": 9800,
                        "comment": "Solicitud lista para revision",
                        "created_by": {"username": "analista"},
                    },
                )
                self.assertEqual(create_response.status_code, 201, create_response.text)
                request_payload = create_response.json()
                self.assertEqual(request_payload["status"], "registrada")

                detail_response = await client.get(
                    f"/api/v1/credit-requests/{request_payload['request_id']}",
                    headers=headers,
                )
                self.assertEqual(detail_response.status_code, 200, detail_response.text)
                detail_payload = detail_response.json()
                self.assertEqual(detail_payload["request_id"], request_payload["request_id"])
                self.assertEqual(detail_payload["status_history"][0]["status"], "registrada")
                self.assertEqual(detail_payload["attachments"], [])

                queue_response = await client.get(
                    "/api/v1/credit-requests?product_code=PLD&status=registrada",
                    headers=headers,
                )
                self.assertEqual(queue_response.status_code, 200, queue_response.text)
                queue_payload = queue_response.json()
                self.assertEqual(queue_payload["applied_filters"]["status"], "registrada")
                self.assertEqual(len(queue_payload["items"]), 1)
                self.assertIn("en_revision", queue_payload["items"][0]["available_actions"])

                transition_response = await client.post(
                    f"/api/v1/credit-requests/{request_payload['request_id']}/status-transitions",
                    headers=headers,
                    json={
                        "target_status": "en_revision",
                        "comment": "Pasa a evaluador",
                        "changed_by": {"username": "analista"},
                    },
                )
                self.assertEqual(transition_response.status_code, 200, transition_response.text)
                self.assertEqual(transition_response.json()["status"], "en_revision")

                export_response = await client.get(
                    "/api/v1/credit-requests/export?status=en_revision",
                    headers=headers,
                )
                self.assertEqual(export_response.status_code, 403, export_response.text)

        asyncio.run(run_test())

    def test_evaluador_can_export_and_approve_but_auditor_cannot_access_queue(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                analista_headers, evaluation_id = await self._create_evaluation(client)
                evaluador_headers = await self.auth_headers(client, "evaluador")
                auditor_headers = await self.auth_headers(client, "auditor")

                create_response = await client.post(
                    "/api/v1/credit-requests",
                    headers=analista_headers,
                    json={
                        "product_code": "PLD",
                        "evaluation_id": evaluation_id,
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "campaign_code": "PLD_48M",
                        "requested_amount": 9800,
                        "comment": "Solicitud para decision final",
                        "created_by": {"username": "analista"},
                    },
                )
                self.assertEqual(create_response.status_code, 201, create_response.text)
                request_id = create_response.json()["request_id"]

                review_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/status-transitions",
                    headers=analista_headers,
                    json={
                        "target_status": "en_revision",
                        "comment": "Revision inicial",
                        "changed_by": {"username": "analista"},
                    },
                )
                self.assertEqual(review_response.status_code, 200, review_response.text)

                approve_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/status-transitions",
                    headers=evaluador_headers,
                    json={
                        "target_status": "aprobada",
                        "comment": "Cumple condiciones",
                        "changed_by": {"username": "evaluador"},
                    },
                )
                self.assertEqual(approve_response.status_code, 200, approve_response.text)
                self.assertEqual(approve_response.json()["status"], "aprobada")

                export_response = await client.get(
                    "/api/v1/credit-requests/export?status=aprobada",
                    headers=evaluador_headers,
                )
                self.assertEqual(export_response.status_code, 200, export_response.text)
                self.assertIn("text/csv", export_response.headers["content-type"])
                self.assertIn("request_id", export_response.text)
                self.assertIn("status=aprobada", export_response.text)

                queue_response = await client.get("/api/v1/credit-requests", headers=auditor_headers)
                self.assertEqual(queue_response.status_code, 403, queue_response.text)

                detail_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}",
                    headers=auditor_headers,
                )
                self.assertEqual(detail_response.status_code, 200, detail_response.text)

        asyncio.run(run_test())
