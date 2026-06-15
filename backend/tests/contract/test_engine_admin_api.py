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
                "/api/v1/admin/engine/products/{productCode}",
                "/api/v1/admin/engine/products/{productCode}/retirement",
                "/api/v1/admin/engine/products/{productCode}/workflows",
                "/api/v1/admin/engine/products/{productCode}/workflows",
                "/api/v1/admin/engine/products/{productCode}/variables",
                "/api/v1/admin/engine/products/{productCode}/variable-catalogs",
                "/api/v1/admin/engine/products/{productCode}/parameter-sets",
                "/api/v1/admin/engine/products/{productCode}/pipeline-strategies",
                "/api/v1/admin/engine/workflows/{workflowId}",
                "/api/v1/admin/engine/workflows/{workflowId}/retirement",
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

    def test_admin_product_list_and_detail_follow_active_and_draft_visibility_rules(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                active_product = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "ACTIVO", "name": "Producto Activo"},
                )
                self.assertEqual(active_product.status_code, 201, active_product.text)

                activate_product = await client.post(
                    "/api/v1/admin/engine/products/ACTIVO/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(activate_product.status_code, 200, activate_product.text)

                active_workflow = await client.post(
                    "/api/v1/admin/engine/products/ACTIVO/workflows",
                    headers=negocio_headers,
                    json={"workflowCode": "standard", "name": "Workflow Activo"},
                )
                self.assertEqual(active_workflow.status_code, 201, active_workflow.text)
                active_workflow_id = active_workflow.json()["id"]

                draft_product = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "BORRADOR", "name": "Producto Borrador"},
                )
                self.assertEqual(draft_product.status_code, 201, draft_product.text)

                active_list_response = await client.get(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                )
                self.assertEqual(active_list_response.status_code, 200, active_list_response.text)
                active_list = active_list_response.json()["items"]
                self.assertEqual([item["productCode"] for item in active_list], ["ACTIVO"])

                draft_list_response = await client.get(
                    "/api/v1/admin/engine/products?state=draft",
                    headers=negocio_headers,
                )
                self.assertEqual(draft_list_response.status_code, 200, draft_list_response.text)
                draft_list = draft_list_response.json()["items"]
                self.assertEqual([item["productCode"] for item in draft_list], ["BORRADOR"])

                detail_response = await client.get(
                    "/api/v1/admin/engine/products/BORRADOR",
                    headers=negocio_headers,
                )
                self.assertEqual(detail_response.status_code, 200, detail_response.text)
                detail = detail_response.json()
                self.assertEqual(detail["productCode"], "BORRADOR")
                self.assertEqual(detail["approval"]["status"], "pending")
                self.assertIsNone(detail["approval"]["approvedBy"])
                self.assertEqual(detail["activeWorkflows"], [])

                workflow_list_response = await client.get(
                    "/api/v1/admin/engine/products/ACTIVO/workflows?state=draft",
                    headers=negocio_headers,
                )
                self.assertEqual(workflow_list_response.status_code, 200, workflow_list_response.text)
                workflow_list = workflow_list_response.json()["items"]
                self.assertEqual([item["workflowCode"] for item in workflow_list], ["standard"])

                workflow_detail_response = await client.get(
                    f"/api/v1/admin/engine/workflows/{active_workflow_id}",
                    headers=negocio_headers,
                )
                self.assertEqual(workflow_detail_response.status_code, 200, workflow_detail_response.text)
                workflow_detail = workflow_detail_response.json()
                self.assertEqual(workflow_detail["workflowCode"], "standard")
                self.assertEqual(workflow_detail["approval"]["status"], "pending")

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

    def test_non_admin_module_role_is_forbidden_from_engine_admin_module(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                headers = await self.auth_headers(client, "auditor")
                response = await client.get(
                    "/api/v1/admin/engine/products",
                    headers=headers,
                )

            self.assertEqual(response.status_code, 403)

        asyncio.run(run_test())

    def test_profile_permission_get_and_engine_artifact_activation_contracts(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                plataforma_headers = await self.auth_headers(client, "plataforma")
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                permissions_response = await client.get(
                    "/api/v1/admin/engine/profiles/admin_negocio/permissions",
                    headers=plataforma_headers,
                )
                self.assertEqual(permissions_response.status_code, 200, permissions_response.text)
                self.assertEqual(permissions_response.json()["roleCode"], "admin_negocio")

                product_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "CONTRACT", "name": "Contrato"},
                )
                self.assertEqual(product_response.status_code, 201, product_response.text)

                workflow_response = await client.post(
                    "/api/v1/admin/engine/products/CONTRACT/workflows",
                    headers=negocio_headers,
                    json={"workflowCode": "standard", "name": "Standard"},
                )
                self.assertEqual(workflow_response.status_code, 201, workflow_response.text)
                workflow_id = workflow_response.json()["id"]

                variable_response = await client.post(
                    "/api/v1/admin/engine/products/CONTRACT/variables",
                    headers=negocio_headers,
                    json={
                        "variableKey": "validated_income",
                        "name": "Ingreso validado",
                        "businessMeaning": "Ingreso mensual validado",
                        "dataType": "number",
                        "required": True,
                        "allowedSource": "campaign_db",
                    },
                )
                self.assertEqual(variable_response.status_code, 201, variable_response.text)
                variable_id = variable_response.json()["id"]

                variable_activation = await client.post(
                    f"/api/v1/admin/engine/variables/{variable_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(variable_activation.status_code, 200, variable_activation.text)
                self.assertEqual(variable_activation.json()["status"], "active")

                catalog_response = await client.post(
                    "/api/v1/admin/engine/products/CONTRACT/variable-catalogs",
                    headers=negocio_headers,
                    json={
                        "items": [
                            {
                                "productVariableId": variable_id,
                                "requiredInRuntime": True,
                                "defaultValue": None,
                                "sourcePolicyPayload": {"allowedSource": "campaign_db"},
                            }
                        ]
                    },
                )
                self.assertEqual(catalog_response.status_code, 201, catalog_response.text)
                catalog_id = catalog_response.json()["id"]

                catalog_activation = await client.post(
                    f"/api/v1/admin/engine/variable-catalogs/{catalog_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(catalog_activation.status_code, 200, catalog_activation.text)
                self.assertEqual(catalog_activation.json()["status"], "active")

                parameter_response = await client.post(
                    "/api/v1/admin/engine/products/CONTRACT/parameter-sets",
                    headers=riesgos_headers,
                    json={"workflowCode": "standard", "payload": {"min_score": 500}},
                )
                self.assertEqual(parameter_response.status_code, 201, parameter_response.text)
                parameter_id = parameter_response.json()["id"]

                parameter_activation = await client.post(
                    f"/api/v1/admin/engine/parameter-sets/{parameter_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(parameter_activation.status_code, 200, parameter_activation.text)
                self.assertEqual(parameter_activation.json()["status"], "active")

                pipeline_response = await client.post(
                    "/api/v1/admin/engine/products/CONTRACT/pipeline-strategies",
                    headers=riesgos_headers,
                    json={
                        "graphDefinition": {"entryNode": "eligibility"},
                        "nodes": [
                            {
                                "nodeKey": "eligibility",
                                "nodeType": "rule_group",
                                "configPayload": {"mode": "all"},
                            }
                        ],
                    },
                )
                self.assertEqual(pipeline_response.status_code, 201, pipeline_response.text)
                pipeline_id = pipeline_response.json()["id"]

                pipeline_activation = await client.post(
                    f"/api/v1/admin/engine/pipeline-strategies/{pipeline_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(pipeline_activation.status_code, 200, pipeline_activation.text)
                self.assertEqual(pipeline_activation.json()["status"], "active")

                rule_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/rules",
                    headers=riesgos_headers,
                    json={
                        "name": "Max debt",
                        "ruleType": "eligibility",
                        "conditionExpression": "reported_debt < 1000",
                        "actionExpression": "allow",
                        "parameters": {"threshold": 1000},
                    },
                )
                self.assertEqual(rule_response.status_code, 201, rule_response.text)
                rule_id = rule_response.json()["id"]
                rule_version_id = rule_response.json()["activeVersion"]["id"]

                rule_activation = await client.post(
                    f"/api/v1/admin/engine/rule-versions/{rule_version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(rule_activation.status_code, 200, rule_activation.text)
                self.assertEqual(rule_activation.json()["status"], "active")
                self.assertEqual(rule_activation.json()["workflowId"], workflow_id)

                workflow_version_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": catalog_id,
                        "parameterSetId": parameter_id,
                        "pipelineStrategyId": pipeline_id,
                        "ruleVersionIds": [rule_version_id],
                        "changeNotes": "Version inicial",
                    },
                )
                self.assertEqual(workflow_version_response.status_code, 201, workflow_version_response.text)
                workflow_version_id = workflow_version_response.json()["id"]

                workflow_version_activation = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{workflow_version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(workflow_version_activation.status_code, 200, workflow_version_activation.text)
                self.assertEqual(workflow_version_activation.json()["status"], "active")

                workflow_retirement = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/retirement",
                    headers=riesgos_headers,
                )
                self.assertEqual(workflow_retirement.status_code, 409, workflow_retirement.text)

                delete_rule = await client.delete(
                    f"/api/v1/admin/engine/rules/{rule_id}",
                    headers=riesgos_headers,
                )
                self.assertEqual(delete_rule.status_code, 409, delete_rule.text)

        asyncio.run(run_test())

    def test_retired_and_deleted_artifacts_stay_hidden_from_operational_listings(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "DRAFTDEL", "name": "Draft delete"},
                )
                delete_response = await client.delete(
                    "/api/v1/admin/engine/products/DRAFTDEL",
                    headers=negocio_headers,
                )
                self.assertEqual(delete_response.status_code, 204, delete_response.text)

                await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "TORETIRE", "name": "To retire"},
                )
                workflow_response = await client.post(
                    "/api/v1/admin/engine/products/TORETIRE/workflows",
                    headers=negocio_headers,
                    json={"workflowCode": "draftflow", "name": "Draft flow"},
                )
                workflow_id = workflow_response.json()["id"]
                retire_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/retirement",
                    headers=riesgos_headers,
                )
                self.assertEqual(retire_response.status_code, 200, retire_response.text)

                active_products = await client.get(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                )
                draft_products = await client.get(
                    "/api/v1/admin/engine/products?state=draft",
                    headers=negocio_headers,
                )
                draft_workflows = await client.get(
                    "/api/v1/admin/engine/products/TORETIRE/workflows?state=draft",
                    headers=negocio_headers,
                )

                self.assertEqual(active_products.status_code, 200, active_products.text)
                self.assertEqual(draft_products.status_code, 200, draft_products.text)
                self.assertEqual(draft_workflows.status_code, 200, draft_workflows.text)
                self.assertEqual([item["productCode"] for item in draft_products.json()["items"]], ["TORETIRE"])
                self.assertEqual(draft_workflows.json()["items"], [])
                self.assertNotIn("DRAFTDEL", [item["productCode"] for item in active_products.json()["items"]])
                self.assertNotIn("DRAFTDEL", [item["productCode"] for item in draft_products.json()["items"]])

        asyncio.run(run_test())
