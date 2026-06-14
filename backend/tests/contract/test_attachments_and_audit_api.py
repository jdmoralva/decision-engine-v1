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


def build_zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("dni.txt", "12345678")
        archive.writestr("carpeta/evidencia.json", '{"ok":true}')
    return buffer.getvalue()


class AttachmentsAndAuditContractTests(RuntimeApiTestCaseMixin, unittest.TestCase):
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

    async def _create_request(self, client: AsyncClient) -> tuple[str, str, dict[str, str]]:
        headers, evaluation_id = await self._create_evaluation(client)
        response = await client.post(
            "/api/v1/credit-requests",
            headers=headers,
            json={
                "product_code": "PLD",
                "evaluation_id": evaluation_id,
                "document": {"document_type": "DNI", "document_number": "12345678"},
                "campaign_code": "PLD_48M",
                "requested_amount": 9800,
                "comment": "Solicitud con adjuntos",
                "created_by": {"username": "analista"},
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["request_id"], evaluation_id, headers

    def test_openapi_exposes_attachment_and_audit_contracts(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                response = await client.get("/openapi.json")

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            paths = payload["paths"]
            for path in (
                "/api/v1/credit-requests/{request_id}/attachments",
                "/api/v1/credit-requests/{request_id}/attachments/{attachment_id}/manifest",
                "/api/v1/credit-requests/{request_id}/attachments/{attachment_id}/download",
                "/api/v1/audit",
            ):
                self.assertIn(path, paths)

            schemas = payload["components"]["schemas"]
            for schema_name in (
                "AttachmentMetadataResponse",
                "AttachmentManifestResponse",
                "AttachmentManifestEntry",
                "AuditEventPageResponse",
                "AuditEventResponse",
            ):
                self.assertIn(schema_name, schemas)

        asyncio.run(run_test())

    def test_attachment_and_audit_endpoints_enforce_role_access(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                request_id, evaluation_id, analista_headers = await self._create_request(client)
                evaluador_headers = await self.auth_headers(client, "evaluador")
                admin_headers = await self.auth_headers(client, "admin")
                auditor_headers = await self.auth_headers(client, "auditor")

                upload_response = await client.post(
                    f"/api/v1/credit-requests/{request_id}/attachments",
                    headers=analista_headers,
                    files={"file": ("evidencia.zip", build_zip_bytes(), "application/zip")},
                )
                self.assertEqual(upload_response.status_code, 201, upload_response.text)
                attachment_id = upload_response.json()["attachment_id"]

                list_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments",
                    headers=evaluador_headers,
                )
                self.assertEqual(list_response.status_code, 200, list_response.text)
                self.assertEqual(len(list_response.json()), 1)

                manifest_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments/{attachment_id}/manifest",
                    headers=admin_headers,
                )
                self.assertEqual(manifest_response.status_code, 200, manifest_response.text)
                manifest_payload = manifest_response.json()
                self.assertEqual(manifest_payload["original_filename"], "evidencia.zip")
                self.assertEqual(len(manifest_payload["entries"]), 2)

                download_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments/{attachment_id}/download",
                    headers=analista_headers,
                )
                self.assertEqual(download_response.status_code, 200, download_response.text)
                self.assertEqual(download_response.headers["content-type"], "application/zip")

                forbidden_response = await client.get(
                    f"/api/v1/credit-requests/{request_id}/attachments",
                    headers=auditor_headers,
                )
                self.assertEqual(forbidden_response.status_code, 403, forbidden_response.text)

                audit_response = await client.get(
                    f"/api/v1/audit?request_id={request_id}&evaluation_id={evaluation_id}",
                    headers=auditor_headers,
                )
                self.assertEqual(audit_response.status_code, 200, audit_response.text)
                audit_payload = audit_response.json()
                self.assertGreaterEqual(audit_payload["total"], 2)
                self.assertTrue(any(item["event_type"] == "credit_request_created" for item in audit_payload["items"]))
                self.assertTrue(any(item["event_type"] == "attachment_uploaded" for item in audit_payload["items"]))

        asyncio.run(run_test())
