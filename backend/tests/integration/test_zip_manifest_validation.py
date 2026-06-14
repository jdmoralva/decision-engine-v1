import asyncio
import io
import sys
import unittest
import zipfile
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


def _build_zip_payload() -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("b-folder/evidencia.txt", "evidencia")
        archive.writestr("a-folder/ingresos.csv", "mes,monto\n2026-06,2500\n")
    return stream.getvalue()


class ZipManifestValidationIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    async def _create_request(self, client: AsyncClient) -> tuple[dict[str, str], str]:
        headers = await self.auth_headers(client, "analista")
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
        evaluation_id = evaluation_response.json()["evaluation_id"]
        request_response = await client.post(
            "/api/v1/credit-requests",
            headers=headers,
            json={
                "product_code": "PLD",
                "evaluation_id": evaluation_id,
                "document": {"document_type": "DNI", "document_number": "12345678"},
                "campaign_code": "PLD_48M",
                "requested_amount": 9800,
                "comment": "Solicitud con ZIP",
                "created_by": {"username": "analista"},
            },
        )
        self.assertEqual(request_response.status_code, 201, request_response.text)
        return headers, request_response.json()["request_id"]

    def test_manifest_lists_zip_entries_in_sorted_visual_order(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers, request_id = await self._create_request(client)
                upload_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/attachments",
                    headers=headers,
                    files={"file": ("evidencia.zip", _build_zip_payload(), "application/zip")},
                )
                self.assertEqual(upload_response.status_code, 201, upload_response.text)
                attachment_payload = upload_response.json()
                self.assertEqual(attachment_payload["entry_count"], 2)

                manifest_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments/{attachment_payload['attachment_id']}/manifest",
                    headers=headers,
                )
                self.assertEqual(manifest_response.status_code, 200, manifest_response.text)
                manifest_payload = manifest_response.json()
                self.assertEqual(
                    [entry["path"] for entry in manifest_payload["entries"]],
                    ["a-folder/ingresos.csv", "b-folder/evidencia.txt"],
                )
                self.assertTrue(all(entry["size"] > 0 for entry in manifest_payload["entries"]))

        asyncio.run(run_test())
