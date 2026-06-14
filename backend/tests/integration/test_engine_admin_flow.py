import asyncio
import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tests.engine_admin_test_support import EngineAdminApiTestCaseMixin


class EngineAdminFlowIntegrationTests(EngineAdminApiTestCaseMixin, unittest.TestCase):
    async def _create_bundle(self, client: AsyncClient, product_code: str = "PLD") -> dict[str, str]:
        negocio_headers = await self.auth_headers(client, "negocio")
        riesgos_headers = await self.auth_headers(client, "riesgos")

        product_response = await client.post(
            "/api/v1/admin/engine/products",
            headers=negocio_headers,
            json={"productCode": product_code, "name": f"Producto {product_code}"},
        )
        self.assertEqual(product_response.status_code, 201, product_response.text)

        activate_product_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(activate_product_response.status_code, 200, activate_product_response.text)

        workflow_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/workflows",
            headers=negocio_headers,
            json={"workflowCode": "standard", "name": "Standard"},
        )
        self.assertEqual(workflow_response.status_code, 201, workflow_response.text)
        workflow_id = workflow_response.json()["id"]

        variable_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/variables",
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

        variable_activation_response = await client.post(
            f"/api/v1/admin/engine/variables/{variable_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(variable_activation_response.status_code, 200, variable_activation_response.text)

        catalog_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/variable-catalogs",
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

        catalog_activation_response = await client.post(
            f"/api/v1/admin/engine/variable-catalogs/{catalog_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(catalog_activation_response.status_code, 200, catalog_activation_response.text)

        parameter_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/parameter-sets",
            headers=riesgos_headers,
            json={
                "workflowCode": "standard",
                "payload": {"min_score": 500},
            },
        )
        self.assertEqual(parameter_response.status_code, 201, parameter_response.text)
        parameter_set_id = parameter_response.json()["id"]

        parameter_activation_response = await client.post(
            f"/api/v1/admin/engine/parameter-sets/{parameter_set_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(parameter_activation_response.status_code, 200, parameter_activation_response.text)

        pipeline_response = await client.post(
            f"/api/v1/admin/engine/products/{product_code}/pipeline-strategies",
            headers=riesgos_headers,
            json={
                "graphDefinition": {"entryNode": "eligibility"},
                "nodes": [
                    {
                        "nodeKey": "eligibility",
                        "nodeType": "rule_group",
                        "positionX": 10,
                        "positionY": 20,
                        "configPayload": {"mode": "all"},
                    }
                ],
            },
        )
        self.assertEqual(pipeline_response.status_code, 201, pipeline_response.text)
        pipeline_strategy_id = pipeline_response.json()["id"]

        pipeline_activation_response = await client.post(
            f"/api/v1/admin/engine/pipeline-strategies/{pipeline_strategy_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(pipeline_activation_response.status_code, 200, pipeline_activation_response.text)

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
        rule_version_id = rule_response.json()["activeVersion"]["id"]

        rule_activation_response = await client.post(
            f"/api/v1/admin/engine/rule-versions/{rule_version_id}/activation",
            headers=riesgos_headers,
        )
        self.assertEqual(rule_activation_response.status_code, 200, rule_activation_response.text)

        return {
            "workflow_id": workflow_id,
            "catalog_id": catalog_id,
            "parameter_set_id": parameter_set_id,
            "pipeline_strategy_id": pipeline_strategy_id,
            "rule_version_id": rule_version_id,
        }

    def test_activation_requires_active_dependencies(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")
                bundle = await self._create_bundle(client)

                draft_parameter_response = await client.post(
                    "/api/v1/admin/engine/products/PLD/parameter-sets",
                    headers=riesgos_headers,
                    json={"workflowCode": "standard", "payload": {"min_score": 750}},
                )
                self.assertEqual(draft_parameter_response.status_code, 201, draft_parameter_response.text)

                blocked_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{bundle['workflow_id']}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": bundle["catalog_id"],
                        "parameterSetId": draft_parameter_response.json()["id"],
                        "pipelineStrategyId": bundle["pipeline_strategy_id"],
                        "ruleVersionIds": [bundle["rule_version_id"]],
                        "changeNotes": "Draft parameter should block activation",
                    },
                )
                self.assertEqual(blocked_response.status_code, 409)
                self.assertEqual(blocked_response.json()["error"]["code"], "ENGINE_ADMIN_VALIDATION")

        asyncio.run(run_test())

    def test_workflow_version_replacement_retires_previous_active_version(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")
                bundle = await self._create_bundle(client)

                first_version_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{bundle['workflow_id']}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": bundle["catalog_id"],
                        "parameterSetId": bundle["parameter_set_id"],
                        "pipelineStrategyId": bundle["pipeline_strategy_id"],
                        "ruleVersionIds": [bundle["rule_version_id"]],
                        "changeNotes": "Initial version",
                    },
                )
                self.assertEqual(first_version_response.status_code, 201, first_version_response.text)
                first_version_id = first_version_response.json()["id"]

                first_activation_response = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{first_version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(first_activation_response.status_code, 200, first_activation_response.text)
                self.assertEqual(first_activation_response.json()["status"], "active")

                second_version_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{bundle['workflow_id']}/versions",
                    headers=negocio_headers,
                    json={
                        "variableCatalogVersionId": bundle["catalog_id"],
                        "parameterSetId": bundle["parameter_set_id"],
                        "pipelineStrategyId": bundle["pipeline_strategy_id"],
                        "ruleVersionIds": [bundle["rule_version_id"]],
                        "changeNotes": "Replacement version",
                    },
                )
                self.assertEqual(second_version_response.status_code, 201, second_version_response.text)
                second_version_id = second_version_response.json()["id"]
                self.assertEqual(second_version_response.json()["versionNumber"], 2)

                second_activation_response = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{second_version_id}/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(second_activation_response.status_code, 200, second_activation_response.text)
                self.assertEqual(second_activation_response.json()["status"], "active")

                from backend.app.infrastructure.db.models import WorkflowVersion
                from backend.app.infrastructure.db.session import get_session_factory

                with get_session_factory()() as session:
                    first_version = session.get(WorkflowVersion, first_version_id)
                    second_version = session.get(WorkflowVersion, second_version_id)

                self.assertEqual(first_version.status, "retired")
                self.assertEqual(second_version.status, "active")

                blocked_retirement_response = await client.post(
                    f"/api/v1/admin/engine/workflow-versions/{second_version_id}/retirement",
                    headers=riesgos_headers,
                )
                self.assertEqual(blocked_retirement_response.status_code, 409)
                self.assertEqual(blocked_retirement_response.json()["error"]["code"], "ENGINE_ADMIN_VALIDATION")

        asyncio.run(run_test())

    def test_negocio_can_delete_draft_product_but_not_active_product(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                draft_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "BORRADOR", "name": "Borrador"},
                )
                self.assertEqual(draft_response.status_code, 201, draft_response.text)

                delete_draft_response = await client.delete(
                    "/api/v1/admin/engine/products/BORRADOR",
                    headers=negocio_headers,
                )
                self.assertEqual(delete_draft_response.status_code, 204, delete_draft_response.text)

                active_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "ACTIVO", "name": "Activo"},
                )
                self.assertEqual(active_response.status_code, 201, active_response.text)
                activate_response = await client.post(
                    "/api/v1/admin/engine/products/ACTIVO/activation",
                    headers=riesgos_headers,
                )
                self.assertEqual(activate_response.status_code, 200, activate_response.text)

                blocked_response = await client.delete(
                    "/api/v1/admin/engine/products/ACTIVO",
                    headers=negocio_headers,
                )
                self.assertEqual(blocked_response.status_code, 409, blocked_response.text)

        asyncio.run(run_test())

    def test_riesgos_can_delete_draft_workflow_and_rule(self):
        async def run_test():
            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                negocio_headers = await self.auth_headers(client, "negocio")
                riesgos_headers = await self.auth_headers(client, "riesgos")

                product_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "DELTA", "name": "Delta"},
                )
                self.assertEqual(product_response.status_code, 201, product_response.text)

                workflow_response = await client.post(
                    "/api/v1/admin/engine/products/DELTA/workflows",
                    headers=negocio_headers,
                    json={"workflowCode": "standard", "name": "Standard"},
                )
                self.assertEqual(workflow_response.status_code, 201, workflow_response.text)
                workflow_id = workflow_response.json()["id"]

                rule_response = await client.post(
                    f"/api/v1/admin/engine/workflows/{workflow_id}/rules",
                    headers=riesgos_headers,
                    json={
                        "name": "Regla a borrar",
                        "ruleType": "eligibility",
                        "conditionExpression": "validated_income > 0",
                        "actionExpression": "allow",
                    },
                )
                self.assertEqual(rule_response.status_code, 201, rule_response.text)
                rule_id = rule_response.json()["id"]

                delete_rule_response = await client.delete(
                    f"/api/v1/admin/engine/rules/{rule_id}",
                    headers=riesgos_headers,
                )
                self.assertEqual(delete_rule_response.status_code, 204, delete_rule_response.text)

                delete_workflow_response = await client.delete(
                    f"/api/v1/admin/engine/workflows/{workflow_id}",
                    headers=riesgos_headers,
                )
                self.assertEqual(delete_workflow_response.status_code, 204, delete_workflow_response.text)

        asyncio.run(run_test())

    def test_profile_permission_update_is_audited_and_applies_on_next_request(self):
        from backend.app.infrastructure.db.models import AdministrativeAuditEvent, Permission, Role, RolePermission
        from backend.app.infrastructure.db.session import get_session_factory

        async def run_test():
            with get_session_factory()() as session:
                role = session.query(Role).filter_by(code="admin_negocio").one()
                permission = Permission(
                    id=str(uuid4()),
                    code="consultar_auditoria",
                    name="Consultar auditoria",
                    description="Permite solo lectura de auditoria.",
                    created_at=datetime.now(UTC),
                )
                session.add(permission)
                session.flush()
                session.add(
                    RolePermission(
                        id=str(uuid4()),
                        role_id=role.id,
                        permission_id=permission.id,
                        created_at=datetime.now(UTC),
                    )
                )
                session.commit()

            async with AsyncClient(transport=self.build_transport(), base_url="http://testserver") as client:
                plataforma_headers = await self.auth_headers(client, "plataforma")
                negocio_headers = await self.auth_headers(client, "negocio")

                response = await client.put(
                    "/api/v1/admin/engine/profiles/admin_negocio/permissions",
                    headers=plataforma_headers,
                    json={"permissionCodes": ["consultar_auditoria"]},
                )
                self.assertEqual(response.status_code, 200, response.text)

                denied_response = await client.post(
                    "/api/v1/admin/engine/products",
                    headers=negocio_headers,
                    json={"productCode": "POSTCAMBIO", "name": "Post cambio"},
                )
                self.assertEqual(denied_response.status_code, 403, denied_response.text)

            with get_session_factory()() as session:
                audit_events = session.query(AdministrativeAuditEvent).all()

            self.assertTrue(
                any(
                    event.aggregate_type == "role_permission_assignment"
                    and event.event_type == "permissions_replaced"
                    for event in audit_events
                )
            )

        asyncio.run(run_test())
