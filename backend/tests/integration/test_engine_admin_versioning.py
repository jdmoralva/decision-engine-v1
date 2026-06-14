import asyncio
import json
import sys
import unittest
from pathlib import Path

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.engine_admin_test_support import EngineAdminApiTestCaseMixin


class EngineAdminVersioningRegressionTests(EngineAdminApiTestCaseMixin, unittest.TestCase):
    async def _create_bundle(self, client: AsyncClient, product_code: str) -> dict[str, str]:
        negocio_headers = await self.auth_headers(client, "negocio")
        riesgos_headers = await self.auth_headers(client, "riesgos")

        response = await client.post(
            "/api/v1/admin/engine/products",
            headers=negocio_headers,
            json={"productCode": product_code, "name": f"Producto {product_code}"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        workflow_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/workflows",
            headers=negocio_headers,
            json={"workflowCode": "standard", "name": f"Workflow {product_code}"},
        )
        self.assertEqual(workflow_response.status_code, 201, workflow_response.text)
        workflow_id = workflow_response.json()["id"]

        variable_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/variables",
            headers=negocio_headers,
            json={
                "variableKey": f"income_{product_code.lower()}",
                "name": "Ingreso",
                "businessMeaning": "Ingreso validado",
                "dataType": "number",
                "required": True,
                "allowedSource": "campaign_db",
            },
        )
        self.assertEqual(variable_response.status_code, 201, variable_response.text)
        variable_id = variable_response.json()["id"]
        response = await client.post(
            f"/api/v1/admin/engine/variables/{variable_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        catalog_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/variable-catalogs",
            headers=negocio_headers,
            json={
                "items": [
                    {
                        "productVariableId": variable_id,
                        "requiredInRuntime": True,
                        "sourcePolicyPayload": {"allowedSource": "campaign_db"},
                    }
                ]
            },
        )
        self.assertEqual(catalog_response.status_code, 201, catalog_response.text)
        catalog_id = catalog_response.json()["id"]
        response = await client.post(
            f"/api/v1/admin/engine/variable-catalogs/{catalog_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        parameter_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/parameter-sets",
            headers=riesgos_headers,
            json={"workflowCode": "standard", "payload": {"max_term": 48}},
        )
        self.assertEqual(parameter_response.status_code, 201, parameter_response.text)
        parameter_set_id = parameter_response.json()["id"]
        response = await client.post(
            f"/api/v1/admin/engine/parameter-sets/{parameter_set_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        pipeline_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/pipeline-strategies",
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
        self.assertEqual(pipeline_response.status_code, 201, pipeline_response.text)
        pipeline_strategy_id = pipeline_response.json()["id"]
        response = await client.post(
            f"/api/v1/admin/engine/pipeline-strategies/{pipeline_strategy_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        rule_response = await client.post(
            f"/api/v1/admin/engine/workflows/{workflow_id}/rules",
            headers=riesgos_headers,
            json={
                "name": "Regla principal",
                "ruleType": "eligibility",
                "conditionExpression": "1 == 1",
                "actionExpression": "allow",
            },
        )
        self.assertEqual(rule_response.status_code, 201, rule_response.text)
        rule_version_id = rule_response.json()["activeVersion"]["id"]
        response = await client.post(
            f"/api/v1/admin/engine/rule-versions/{rule_version_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)

        return {
            "workflow_id": workflow_id,
            "catalog_id": catalog_id,
            "parameter_set_id": parameter_set_id,
            "pipeline_strategy_id": pipeline_strategy_id,
            "rule_version_id": rule_version_id,
        }

    def test_workflow_replacement_switches_runtime_and_keeps_activation_audit(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")
                bundle = await self._create_bundle(client, "PLD")

                first_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{bundle['workflow_id']}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": bundle["catalog_id"],
                        "parameterSetId": bundle["parameter_set_id"],
                        "pipelineStrategyId": bundle["pipeline_strategy_id"],
                        "ruleVersionIds": [bundle["rule_version_id"]],
                        "changeNotes": "Version inicial",
                    },
                )
                self.assertEqual(first_response.status_code, 201, first_response.text)
                first_version_id = first_response.json()["id"]

                response = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{first_version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(response.status_code, 200, response.text)

                second_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{bundle['workflow_id']}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": bundle["catalog_id"],
                        "parameterSetId": bundle["parameter_set_id"],
                        "pipelineStrategyId": bundle["pipeline_strategy_id"],
                        "ruleVersionIds": [bundle["rule_version_id"]],
                        "changeNotes": "Version reemplazo",
                    },
                )
                self.assertEqual(second_response.status_code, 201, second_response.text)
                second_version_id = second_response.json()["id"]

                response = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{second_version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(response.status_code, 200, response.text)

                from backend.app.application.engine_admin.runtime_loader import RuntimeLoader
                from backend.app.infrastructure.db.models import AdministrativeAuditEvent, WorkflowVersion
                from backend.app.infrastructure.db.session import get_session_factory
                from sqlalchemy import select

                loader = RuntimeLoader(get_session_factory())
                runtime = loader.load_runtime("PLD", "standard")

                with get_session_factory()() as session:
                    first_row = session.get(WorkflowVersion, first_version_id)
                    second_row = session.get(WorkflowVersion, second_version_id)
                    activation_events = list(
                        session.execute(
                            select(AdministrativeAuditEvent).where(
                                AdministrativeAuditEvent.aggregate_type == "workflow_version",
                                AdministrativeAuditEvent.event_type == "activated",
                            )
                        ).scalars()
                    )

                self.assertEqual(first_row.status, "retired")
                self.assertEqual(second_row.status, "active")
                self.assertEqual(runtime.strategy.applied_versions.parameter_version, "1")
                self.assertEqual(runtime.strategy.applied_versions.pipeline_version, "1")
                self.assertGreaterEqual(len(activation_events), 2)
                self.assertTrue(any(event.aggregate_id == first_version_id for event in activation_events))
                self.assertTrue(any(event.aggregate_id == second_version_id for event in activation_events))

        asyncio.run(run_test())

    def test_workflow_version_rejects_parameter_set_from_another_product(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                pl_d_bundle = await self._create_bundle(client, "PLD")
                auto_bundle = await self._create_bundle(client, "AUTO")

                blocked_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{pl_d_bundle['workflow_id']}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": pl_d_bundle["catalog_id"],
                        "parameterSetId": auto_bundle["parameter_set_id"],
                        "pipelineStrategyId": pl_d_bundle["pipeline_strategy_id"],
                        "ruleVersionIds": [pl_d_bundle["rule_version_id"]],
                        "changeNotes": "Debe fallar por mezclar productos",
                    },
                )

                self.assertEqual(blocked_response.status_code, 409, blocked_response.text)
                self.assertEqual(blocked_response.json()["error"]["code"], "ENGINE_ADMIN_VALIDATION")

        asyncio.run(run_test())
