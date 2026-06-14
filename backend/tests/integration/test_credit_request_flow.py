import asyncio
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


class CreditRequestFlowIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    async def _create_evaluation(self, client: AsyncClient) -> str:
        headers = await self.auth_headers(client, "analista")
        response = await client.post(
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
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["evaluation_id"]

    def test_request_registration_detail_transitions_and_export_echo_filters(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                analista_headers = await self.auth_headers(client, "analista")
                evaluador_headers = await self.auth_headers(client, "evaluador")
                evaluation_id = await self._create_evaluation(client)

                create_response = await client.post(
                    "/api/v1/credit-requests",
                    headers=analista_headers,
                    json={
                        "product_code": "PLD",
                        "evaluation_id": evaluation_id,
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "campaign_code": "PLD_48M",
                        "requested_amount": 9800,
                        "comment": "Solicitud inicial",
                        "created_by": {"username": "analista"},
                    },
                )
                self.assertEqual(create_response.status_code, 201, create_response.text)
                request_id = create_response.json()["request_id"]

                detail_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}",
                    headers=analista_headers,
                )
                self.assertEqual(detail_response.status_code, 200, detail_response.text)
                detail_payload = detail_response.json()
                self.assertEqual(detail_payload["evaluation_id"], evaluation_id)
                self.assertEqual(detail_payload["status_history"][0]["status"], "registrada")

                invalid_approve_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/status-transitions",
                    headers=analista_headers,
                    json={
                        "target_status": "aprobada",
                        "comment": "No deberia aprobar",
                        "changed_by": {"username": "analista"},
                    },
                )
                self.assertEqual(invalid_approve_response.status_code, 403, invalid_approve_response.text)

                review_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/status-transitions",
                    headers=analista_headers,
                    json={
                        "target_status": "en_revision",
                        "comment": "Revision operativa",
                        "changed_by": {"username": "analista"},
                    },
                )
                self.assertEqual(review_response.status_code, 200, review_response.text)
                self.assertEqual(review_response.json()["status"], "en_revision")

                approve_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/status-transitions",
                    headers=evaluador_headers,
                    json={
                        "target_status": "aprobada",
                        "comment": "Aprobada",
                        "changed_by": {"username": "evaluador"},
                    },
                )
                self.assertEqual(approve_response.status_code, 200, approve_response.text)
                self.assertEqual(approve_response.json()["status"], "aprobada")

                forbidden_transition_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/status-transitions",
                    headers=evaluador_headers,
                    json={
                        "target_status": "rechazada",
                        "comment": "Ya no deberia cambiar",
                        "changed_by": {"username": "evaluador"},
                    },
                )
                self.assertEqual(forbidden_transition_response.status_code, 409, forbidden_transition_response.text)

                second_evaluation_id = await self._create_evaluation(client)
                cancelled_response = await client.post(
                    "/api/v1/credit-requests",
                    headers=analista_headers,
                    json={
                        "product_code": "PLD",
                        "evaluation_id": second_evaluation_id,
                        "document": {"document_type": "DNI", "document_number": "12345678"},
                        "campaign_code": "PLD_48M",
                        "requested_amount": 9700,
                        "comment": "Solicitud anulable",
                        "created_by": {"username": "analista"},
                    },
                )
                self.assertEqual(cancelled_response.status_code, 201, cancelled_response.text)
                cancelled_request_id = cancelled_response.json()["request_id"]

                cancel_transition_response = await client.post(
                    f"/api/v1/credit-requests/{cancelled_request_id}/status-transitions",
                    headers=evaluador_headers,
                    json={
                        "target_status": "anulada",
                        "comment": "Caso anulado",
                        "changed_by": {"username": "evaluador"},
                    },
                )
                self.assertEqual(cancel_transition_response.status_code, 200, cancel_transition_response.text)
                self.assertEqual(cancel_transition_response.json()["status"], "anulada")

                queue_response = await client.get(
                    "/api/v1/credit-requests?status=aprobada&product_code=PLD",
                    headers=evaluador_headers,
                )
                self.assertEqual(queue_response.status_code, 200, queue_response.text)
                queue_payload = queue_response.json()
                self.assertEqual(queue_payload["applied_filters"], {"product_code": "PLD", "status": "aprobada"})
                self.assertEqual(len(queue_payload["items"]), 1)
                self.assertEqual(queue_payload["items"][0]["request_id"], request_id)

                export_response = await client.get(
                    "/api/v1/credit-requests/export?status=aprobada&product_code=PLD",
                    headers=evaluador_headers,
                )
                self.assertEqual(export_response.status_code, 200, export_response.text)
                self.assertIn("status=aprobada", export_response.text)
                self.assertIn("product_code=PLD", export_response.text)
                self.assertIn(request_id, export_response.text)

                from backend.app.infrastructure.db.models import AdministrativeAuditEvent, CreditRequest, CreditRequestStatusHistory
                from backend.app.infrastructure.db.session import get_session_factory
                from sqlalchemy import select

                with get_session_factory()() as session:
                    request_row = session.get(CreditRequest, request_id)
                    self.assertEqual(request_row.evaluation_id, evaluation_id)
                    self.assertEqual(request_row.status, "aprobada")
                    self.assertEqual(request_row.workflow_code, "standard")

                    history_rows = list(
                        session.execute(
                            select(CreditRequestStatusHistory).where(
                                CreditRequestStatusHistory.request_id == request_id
                            )
                        ).scalars()
                    )
                    self.assertEqual([row.status for row in history_rows], ["registrada", "en_revision", "aprobada"])

                    audit_events = list(
                        session.execute(
                            select(AdministrativeAuditEvent).where(
                                AdministrativeAuditEvent.aggregate_id.in_([request_id, cancelled_request_id])
                            )
                        ).scalars()
                    )
                    self.assertTrue(any(event.event_type == "credit_request_created" for event in audit_events))
                    self.assertTrue(any(event.event_type == "credit_request_status_changed" for event in audit_events))
                    self.assertTrue(any(event.event_type == "credit_request_queue_exported" for event in audit_events))

        asyncio.run(run_test())
