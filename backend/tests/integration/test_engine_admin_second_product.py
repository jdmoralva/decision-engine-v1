import asyncio
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.engine_admin_test_support import EngineAdminApiTestCaseMixin


class EngineAdminSecondProductIntegrationTests(EngineAdminApiTestCaseMixin, unittest.TestCase):
    def test_second_product_can_be_onboarded_without_shared_layer_changes(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "AUTO", "name": "Auto Convenios"},
                )
                await client.post(
                    "/api/v1/admin/engine/products/AUTO/activation",
                    headers=riesgos_headers,
                )
                workflow_response = await client.post(
                    "/api/v1/admin/engine/products/AUTO/workflows",
                    headers=negocio_headers,
                    json={"workflowCode": "standard", "name": "Originacion Auto"},
                )
                workflow_id = workflow_response.json()["id"]

                variable_response = await client.post(
                    "/api/v1/admin/engine/products/AUTO/variables",
                    headers=negocio_headers,
                    json={
                        "variableKey": "segment_code",
                        "name": "Segmento",
                        "businessMeaning": "Segmento comercial",
                        "dataType": "string",
                        "required": True,
                        "allowedSource": "user_input",
                    },
                )
                variable_id = variable_response.json()["id"]
                await client.post(
                    f"/api/v1/admin/engine/variables/{variable_id}/activation",
                    headers=riesgos_headers,
                )

                catalog_response = await client.post(
                    "/api/v1/admin/engine/products/AUTO/variable-catalogs",
                    headers=negocio_headers,
                    json={
                        "items": [
                            {
                                "productVariableId": variable_id,
                                "requiredInRuntime": True,
                                "sourcePolicyPayload": {"allowedSource": "user_input"},
                            }
                        ]
                    },
                )
                catalog_id = catalog_response.json()["id"]
                await client.post(
                    f"/api/v1/admin/engine/variable-catalogs/{catalog_id}/activation",
                    headers=riesgos_headers,
                )

                parameter_response = await client.post(
                    "/api/v1/admin/engine/products/AUTO/parameter-sets",
                    headers=riesgos_headers,
                    json={"workflowCode": "standard", "payload": {"max_term": 48}},
                )
                parameter_set_id = parameter_response.json()["id"]
                await client.post(
                    f"/api/v1/admin/engine/parameter-sets/{parameter_set_id}/activation",
                    headers=riesgos_headers,
                )

                pipeline_response = await client.post(
                    "/api/v1/admin/engine/products/AUTO/pipeline-strategies",
                    headers=riesgos_headers,
                    json={
                        "graphDefinition": {"entryNode": "start"},
                        "nodes": [
                            {
                                "nodeKey": "start",
                                "nodeType": "rule_group",
                                "configPayload": {"mode": "all"},
                            }
                        ],
                    },
                )
                pipeline_strategy_id = pipeline_response.json()["id"]
                await client.post(
                    f"/api/v1/admin/engine/pipeline-strategies/{pipeline_strategy_id}/activation",
                    headers=riesgos_headers,
                )

                rule_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/rules",
                    headers=riesgos_headers,
                    json={
                        "name": "Segment filter",
                        "ruleType": "eligibility",
                        "conditionExpression": "segment_code != ''",
                        "actionExpression": "allow",
                    },
                )
                rule_version_id = rule_response.json()["activeVersion"]["id"]
                await client.post(
                    f"/api/v1/admin/engine/rule-versions/{rule_version_id}/activation",
                    headers=riesgos_headers,
                )

                version_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": catalog_id,
                        "parameterSetId": parameter_set_id,
                        "pipelineStrategyId": pipeline_strategy_id,
                        "ruleVersionIds": [rule_version_id],
                        "changeNotes": "AUTO workflow",
                    },
                )
                version_id = version_response.json()["id"]
                activate_response = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(activate_response.status_code, 200, activate_response.text)

                from backend.app.application.engine_admin.runtime_loader import RuntimeLoader
                from backend.app.infrastructure.db.session import get_session_factory

                loader = RuntimeLoader(get_session_factory())
                runtime = loader.load_runtime("AUTO", "standard")

                self.assertEqual(runtime.product_code, "AUTO")
                self.assertEqual(runtime.workflow_code, "standard")

        asyncio.run(run_test())
