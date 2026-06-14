import asyncio
import io
import json
import sys
import unittest
import zipfile
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.runtime_test_support import RuntimeApiTestCaseMixin


def build_zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("documentos/dni.txt", "12345678")
        archive.writestr("resumen.txt", "ok")
    return buffer.getvalue()


class AttachmentsAndAuditFlowIntegrationTests(RuntimeApiTestCaseMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.activate_pld_runtime()

    async def _create_request(self, client: AsyncClient) -> tuple[str, str, dict[str, str]]:
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
                "comment": "Solicitud con evidencia",
                "created_by": {"username": "analista"},
            },
        )
        self.assertEqual(request_response.status_code, 201, request_response.text)
        return request_response.json()["request_id"], evaluation_id, headers

    def test_zip_lifecycle_manifest_download_and_audit_retrieval(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                request_id, evaluation_id, analista_headers = await self._create_request(client)
                auditor_headers = await self.auth_headers(client, "auditor")

                upload_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/attachments",
                    headers=analista_headers,
                    files={"file": ("evidencia.zip", build_zip_bytes(), "application/zip")},
                )
                self.assertEqual(upload_response.status_code, 201, upload_response.text)
                uploaded_payload = upload_response.json()
                attachment_id = uploaded_payload["attachment_id"]
                self.assertEqual(uploaded_payload["entry_count"], 2)

                list_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments",
                    headers=analista_headers,
                )
                self.assertEqual(list_response.status_code, 200, list_response.text)
                listed_payload = list_response.json()
                self.assertEqual(len(listed_payload), 1)
                self.assertEqual(listed_payload[0]["entry_count"], 2)

                manifest_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments/{attachment_id}/manifest",
                    headers=analista_headers,
                )
                self.assertEqual(manifest_response.status_code, 200, manifest_response.text)
                manifest_payload = manifest_response.json()
                self.assertEqual([entry["path"] for entry in manifest_payload["entries"]], ["documentos/dni.txt", "resumen.txt"])

                download_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments/{attachment_id}/download",
                    headers=analista_headers,
                )
                self.assertEqual(download_response.status_code, 200, download_response.text)
                self.assertEqual(download_response.content, build_zip_bytes())

                audit_response = await client.get(
                    f"/api/v1/audit?request_id={request_id}&evaluation_id={evaluation_id}",
                    headers=auditor_headers,
                )
                self.assertEqual(audit_response.status_code, 200, audit_response.text)
                audit_payload = audit_response.json()
                self.assertGreaterEqual(audit_payload["total"], 3)
                self.assertTrue(any(item["event_type"] == "attachment_uploaded" for item in audit_payload["items"]))
                self.assertTrue(any(item["event_type"] == "attachment_downloaded" for item in audit_payload["items"]))

                from backend.app.infrastructure.db.models import AdministrativeAuditEvent, CreditRequestAttachment
                from backend.app.infrastructure.db.session import get_session_factory
                from sqlalchemy import select

                with get_session_factory()() as session:
                    attachment_row = session.get(CreditRequestAttachment, attachment_id)
                    self.assertIsNotNone(attachment_row)
                    self.assertEqual(attachment_row.request_id, request_id)
                    self.assertTrue(Path(attachment_row.storage_path).exists())

                    attachment_audit_rows = list(
                        session.execute(
                            select(AdministrativeAuditEvent).where(AdministrativeAuditEvent.aggregate_id == attachment_id)
                        ).scalars()
                    )
                    self.assertEqual(
                        [row.event_type for row in attachment_audit_rows],
                        ["attachment_uploaded", "attachment_downloaded"],
                    )
                    self.assertEqual(
                        json.loads(attachment_audit_rows[0].event_payload)["request_id"],
                        request_id,
                    )

        asyncio.run(run_test())
