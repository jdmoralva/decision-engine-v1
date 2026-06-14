import asyncio
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.engine_admin_test_support import EngineAdminApiTestCaseMixin


class EngineAdminContractTests(EngineAdminApiTestCaseMixin, unittest.TestCase):
    def test_openapi_exposes_engine_admin_resources(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                response = await client.get("/openapi.json")

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            paths = payload["paths"]

            for path in (
                "/api/v1/admin/engine/products",
                "/api/v1/admin/engine/products/{productCode}/activation",
                "/api/v1/admin/engine/products/{productCode}/retirement",
                "/api/v1/admin/engine/products/{productCode}",
                "/api/v1/admin/engine/products/{productCode}/workflows",
                "/api/v1/admin/engine/products/{productCode}/variables",
                "/api/v1/admin/engine/products/{productCode}/variable-catalogs",
                "/api/v1/admin/engine/products/{productCode}/parameter-sets",
                "/api/v1/admin/engine/products/{productCode}/pipeline-strategies",
                "/api/v1/admin/engine/workflows/{workflowId}",
                "/api/v1/admin/engine/workflows/{workflowId}/rules",
                "/api/v1/admin/engine/workflows/{workflowId}/versions",
                "/api/v1/admin/engine/workflow-versions/{versionId}/activation",
                "/api/v1/admin/engine/rules/{ruleId}",
                "/api/v1/admin/engine/profiles/{roleCode}/permissions",
            ):
                self.assertIn(path, paths)

            schemas = payload["components"]["schemas"]
            for schema_name in (
                "ProfilePermissionAssignmentRequest",
                "ProfilePermissionResponse",
                "ProductCreateRequest",
                "ProductResponse",
                "WorkflowCreateRequest",
                "WorkflowResponse",
                "ProductVariableCreateRequest",
                "VariableCatalogCreateRequest",
                "ParameterSetCreateRequest",
                "PipelineStrategyCreateRequest",
                "RuleCreateRequest",
                "WorkflowVersionCreateRequest",
            ):
                self.assertIn(schema_name, schemas)

        asyncio.run(run_test())

    def test_profile_permission_change_applies_on_next_protected_request(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                plataforma_headers = await self.auth_headers(client, "plataforma")
                negocio_headers = await self.auth_headers(client, "negocio")

                before_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "PERM0", "name": "Permisos 0"},
                )
                self.assertEqual(before_response.status_code, 201, before_response.text)

                update_response = await client.put(
                    "/api/v1/admin/engine/profiles/admin_negocio/permissions",
                    headers=plataforma_headers,
                    json={"permissionCodes": ["consultar_auditoria"]},
                )
                self.assertEqual(update_response.status_code, 200, update_response.text)
                self.assertEqual(update_response.json()["roleCode"], "admin_negocio")

                after_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "PERM1", "name": "Permisos 1"},
                )
                self.assertEqual(after_response.status_code, 403, after_response.text)

        asyncio.run(run_test())

    def test_admin_negocio_can_create_product_draft(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers = await self.auth_headers(client, "negocio")
                response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=headers,
                    json={
                        "productCode": "AUTO",
                        "name": "Auto Convenios",
                        "description": "Producto para creditos vehiculares.",
                    },
                )

            self.assertEqual(response.status_code, 201)
            payload = response.json()
            self.assertEqual(payload["productCode"], "AUTO")
            self.assertEqual(payload["status"], "draft")
            self.assertEqual(payload["name"], "Auto Convenios")

        asyncio.run(run_test())

    def test_admin_riesgos_cannot_create_product_draft(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers = await self.auth_headers(client, "riesgos")
                response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=headers,
                    json={
                        "productCode": "AUTO",
                        "name": "Auto Convenios",
                    },
                )

            self.assertEqual(response.status_code, 403)

        asyncio.run(run_test())
