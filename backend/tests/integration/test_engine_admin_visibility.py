import asyncio
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.engine_admin_test_support import EngineAdminApiTestCaseMixin


class EngineAdminVisibilityIntegrationTests(EngineAdminApiTestCaseMixin, unittest.TestCase):
    def test_deleted_and_retired_artifacts_are_hidden_but_products_remain_persisted(self):
        from backend.app.infrastructure.db.models import LoanProduct, ProductWorkflow
        from backend.app.infrastructure.db.session import get_session_factory

        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                draft_product = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "BORRAR", "name": "Producto para borrar"},
                )
                self.assertEqual(draft_product.status_code, 201, draft_product.text)

                delete_product = await client.delete(
                    "/api/v1/admin/engine/products/BORRAR",
                    headers=negocio_headers,
                )
                self.assertEqual(delete_product.status_code, 204, delete_product.text)

                active_product = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "RETIRAR", "name": "Producto para retiro"},
                )
                self.assertEqual(active_product.status_code, 201, active_product.text)

                activate_product = await client.post(
                    "/api/v1/admin/engine/products/RETIRAR/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(activate_product.status_code, 200, activate_product.text)

                workflow = await client.post(
                    "/api/v1/admin/engine/products/RETIRAR/workflows",
                    headers=negocio_headers,
                    json={"workflowCode": "draft_flow", "name": "Workflow draft"},
                )
                self.assertEqual(workflow.status_code, 201, workflow.text)
                workflow_id = workflow.json()["id"]

                retire_workflow = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/retirement",
                    headers=riesgos_headers,
                )
                self.assertEqual(retire_workflow.status_code, 200, retire_workflow.text)

                active_list = await client.get(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                )
                self.assertEqual(active_list.status_code, 200, active_list.text)
                self.assertEqual([item["productCode"] for item in active_list.json()["items"]], ["RETIRAR"])

                draft_list = await client.get(
                    "/api/v1/admin/engine/products?state=draft",
                    headers=negocio_headers,
                )
                self.assertEqual(draft_list.status_code, 200, draft_list.text)
                self.assertEqual(draft_list.json()["items"], [])

                workflow_list = await client.get(
                    "/api/v1/admin/engine/products/RETIRAR/workflows",
                    headers=negocio_headers,
                )
                self.assertEqual(workflow_list.status_code, 200, workflow_list.text)
                self.assertEqual(workflow_list.json()["items"], [])

            with get_session_factory()() as session:
                deleted_product = session.get(LoanProduct, "BORRAR")
                retired_workflow = session.get(ProductWorkflow, workflow_id)

            self.assertIsNotNone(deleted_product)
            self.assertIsNotNone(deleted_product.deleted_at)
            self.assertIsNotNone(deleted_product.deleted_by)
            self.assertEqual(deleted_product.status, "draft")
            self.assertIsNotNone(retired_workflow)
            self.assertEqual(retired_workflow.status, "retired")
            self.assertIsNotNone(retired_workflow.retired_at)

        asyncio.run(run_test())
