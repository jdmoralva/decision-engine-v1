import asyncio
import json
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


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


class RuntimeReproducibilityIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    def test_repeated_evaluations_keep_deterministic_results_and_ai_traceability(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers = await self.auth_headers(client, "analista")
                first = await client.post("/api/v1/loans/PLD/evaluaciones", headers=headers, json=_evaluation_payload())
                second = await client.post("/api/v1/loans/PLD/evaluaciones", headers=headers, json=_evaluation_payload())

                self.assertEqual(first.status_code, 201, first.text)
                self.assertEqual(second.status_code, 201, second.text)

                first_payload = first.json()
                second_payload = second.json()
                self.assertEqual(first_payload["eligible"], second_payload["eligible"])
                self.assertEqual(first_payload["product_result"], second_payload["product_result"])
                self.assertEqual(first_payload["alerts"], second_payload["alerts"])
                self.assertEqual(first_payload["blocks"], second_payload["blocks"])
                self.assertEqual(first_payload["applied_versions"], second_payload["applied_versions"])

                from backend.app.infrastructure.db.models import AIInteraction, EvaluationInputSnapshot
                from backend.app.infrastructure.db.session import get_session_factory
                from sqlalchemy import select

                with get_session_factory()() as session:
                    snapshots = list(
                        session.execute(
                            select(EvaluationInputSnapshot).where(
                                EvaluationInputSnapshot.evaluation_id == first_payload["evaluation_id"]
                            )
                        ).scalars()
                    )
                    snapshot_fields = sorted(snapshot.field_name for snapshot in snapshots)
                    self.assertEqual(snapshot_fields, sorted(set(snapshot_fields)))
                    self.assertIn("campaign_code", snapshot_fields)
                    self.assertIn("reported_debt", snapshot_fields)
                    self.assertIn("validated_income", snapshot_fields)

                    interactions = list(
                        session.execute(
                            select(AIInteraction).where(
                                AIInteraction.evaluation_id.in_([
                                    first_payload["evaluation_id"],
                                    second_payload["evaluation_id"],
                                ])
                            )
                        ).scalars()
                    )

                self.assertEqual(len(interactions), 2)
                for interaction in interactions:
                    self.assertEqual(interaction.model_name, "fallback")
                    stored_payload = json.loads(interaction.input_payload)
                    self.assertEqual(stored_payload["applied_versions"], first_payload["applied_versions"])

        asyncio.run(run_test())
