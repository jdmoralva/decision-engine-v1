import asyncio
import os
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


class PLDRuntimeFlowIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.bundle = self.activate_pld_runtime()

    def test_consultation_evaluation_and_trace_persist_effective_versions_and_snapshots(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers = await self.auth_headers(client, "analista")

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
                payload = evaluation_response.json()
                self.assertEqual(payload["product_result"]["term_months"], 48)
                self.assertIn("offered_amount", payload["product_result"])

                detail_response = await client.get(
                    f"/api/v1/loans/PLD/evaluaciones/{payload['evaluation_id']}",
                    headers=headers,
                )
                self.assertEqual(detail_response.status_code, 200, detail_response.text)
                self.assertEqual(detail_response.json()["product_result"], payload["product_result"])

                trace_response = await client.get(
                    f"/api/v1/loans/PLD/evaluaciones/{payload['evaluation_id']}/trace",
                    headers=headers,
                )
                self.assertEqual(trace_response.status_code, 200, trace_response.text)
                trace_payload = trace_response.json()
                self.assertEqual(trace_payload["applied_versions"], payload["applied_versions"])
                self.assertEqual(trace_payload["evidence"][0]["field_name"], "campaign_code")
                self.assertTrue(any(item["field_name"] == "reported_debt" for item in trace_payload["evidence"]))

                from backend.app.infrastructure.db.models import AIInteraction, DecisionTrace, EvaluationInputSnapshot, LoanEvaluation
                from backend.app.infrastructure.db.session import get_session_factory
                from sqlalchemy import select

                with get_session_factory()() as session:
                    evaluation = session.get(LoanEvaluation, payload["evaluation_id"])
                    self.assertEqual(evaluation.workflow_version_id, self.bundle["workflow_version_id"])
                    self.assertEqual(evaluation.variable_catalog_version_id, self.bundle["variable_catalog_version_id"])
                    self.assertEqual(evaluation.parameter_set_id, self.bundle["parameter_set_id"])
                    self.assertEqual(evaluation.workflow_code, "standard")
                    self.assertEqual(evaluation.executed_by, session.execute(select(__import__("backend.app.infrastructure.db.models", fromlist=["User"]).User.id).where(__import__("backend.app.infrastructure.db.models", fromlist=["User"]).User.username == "analista")).scalar_one())

                    snapshots = list(
                        session.execute(
                            select(EvaluationInputSnapshot).where(
                                EvaluationInputSnapshot.evaluation_id == payload["evaluation_id"]
                            )
                        ).scalars()
                    )
                    self.assertTrue(any(snapshot.field_name == "campaign_code" for snapshot in snapshots))
                    self.assertTrue(any(snapshot.field_name == "reported_debt" for snapshot in snapshots))

                    trace_row = session.execute(
                        select(DecisionTrace).where(DecisionTrace.evaluation_id == payload["evaluation_id"])
                    ).scalar_one()
                    self.assertEqual(trace_row.id, payload["decision_trace_id"])
                    self.assertIsNotNone(trace_row.human_summary)

                    ai_interaction = session.execute(
                        select(AIInteraction).where(AIInteraction.evaluation_id == payload["evaluation_id"])
                    ).scalar_one()
                    self.assertEqual(ai_interaction.model_name, "fallback")

        asyncio.run(run_test())

    def test_evaluation_rejects_user_input_for_campaign_only_variable(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
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
                            "validated_income": 2500,
                        },
                        "external_inputs": [
                            {
                                "source_type": "user_input",
                                "source_key": "form:pld",
                                "field_name": "validated_income",
                                "field_value": "2500",
                            }
                        ],
                    },
                )
                self.assertEqual(response.status_code, 400, response.text)
                self.assertEqual(response.json()["error"]["code"], "EVALUATION_VALIDATION")

        asyncio.run(run_test())
