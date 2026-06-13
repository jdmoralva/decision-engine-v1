import { describe, expect, it, vi } from "vitest";

import {
  emptyEngineAdminWorkspaceState,
  EngineAdminApiClient,
  runEngineAdminLifecycle,
} from "../src/services/engine-admin-api";


describe("engine admin lifecycle", () => {
  it("orchestrates lifecycle, parameter publication, pipeline activation, and workflow versioning", async () => {
    const calls: string[] = [];
    const fetcher = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      calls.push(`${init?.method ?? "GET"} ${path}`);

      const payloadByPath: Record<string, unknown> = {
        "/api/v1/admin/engine/products": {
          id: "PLD",
          productCode: "PLD",
          name: "Prestamo Libre Disponibilidad",
          status: "draft",
        },
        "/api/v1/admin/engine/products/PLD/activation": {
          id: "PLD",
          productCode: "PLD",
          name: "Prestamo Libre Disponibilidad",
          status: "active",
        },
        "/api/v1/admin/engine/products/PLD/workflows": {
          id: "workflow-1",
          productCode: "PLD",
          workflowCode: "standard",
          name: "Workflow estandar",
          status: "draft",
        },
        "/api/v1/admin/engine/products/PLD/variables": {
          id: "variable-1",
          productCode: "PLD",
          variableKey: "validated_income",
          name: "Ingreso validado",
          businessMeaning: "Ingreso usado en la evaluacion",
          dataType: "number",
          required: true,
          allowedSource: "campaign_db",
          status: "draft",
        },
        "/api/v1/admin/engine/variables/variable-1/activation": {
          id: "variable-1",
          productCode: "PLD",
          variableKey: "validated_income",
          name: "Ingreso validado",
          businessMeaning: "Ingreso usado en la evaluacion",
          dataType: "number",
          required: true,
          allowedSource: "campaign_db",
          status: "active",
        },
        "/api/v1/admin/engine/products/PLD/variable-catalogs": {
          id: "catalog-1",
          productCode: "PLD",
          versionNumber: 1,
          status: "draft",
        },
        "/api/v1/admin/engine/variable-catalogs/catalog-1/activation": {
          id: "catalog-1",
          productCode: "PLD",
          versionNumber: 1,
          status: "active",
        },
        "/api/v1/admin/engine/products/PLD/parameter-sets": {
          id: "params-1",
          productCode: "PLD",
          workflowCode: "standard",
          versionNumber: 1,
          status: "draft",
          payload: { min_score: 500 },
        },
        "/api/v1/admin/engine/parameter-sets/params-1/activation": {
          id: "params-1",
          productCode: "PLD",
          workflowCode: "standard",
          versionNumber: 1,
          status: "active",
          payload: { min_score: 500 },
        },
        "/api/v1/admin/engine/products/PLD/pipeline-strategies": {
          id: "pipeline-1",
          productCode: "PLD",
          versionNumber: 1,
          status: "draft",
        },
        "/api/v1/admin/engine/pipeline-strategies/pipeline-1/activation": {
          id: "pipeline-1",
          productCode: "PLD",
          versionNumber: 1,
          status: "active",
        },
        "/api/v1/admin/engine/workflows/workflow-1/rules": {
          id: "rule-1",
          productCode: "PLD",
          workflowId: "workflow-1",
          name: "Regla base",
          status: "draft",
          activeVersion: { id: "rule-version-1", versionNumber: 1, status: "draft" },
        },
        "/api/v1/admin/engine/rule-versions/rule-version-1/activation": {
          id: "rule-1",
          productCode: "PLD",
          workflowId: "workflow-1",
          name: "Regla base",
          status: "active",
          activeVersion: { id: "rule-version-1", versionNumber: 1, status: "active" },
        },
        "/api/v1/admin/engine/workflows/workflow-1/versions": {
          id: "workflow-version-1",
          workflowId: "workflow-1",
          versionNumber: 1,
          status: "draft",
          variableCatalogVersionId: "catalog-1",
          parameterSetId: "params-1",
          pipelineStrategyId: "pipeline-1",
          ruleVersionIds: ["rule-version-1"],
        },
        "/api/v1/admin/engine/workflow-versions/workflow-version-1/activation": {
          id: "workflow-version-1",
          workflowId: "workflow-1",
          versionNumber: 1,
          status: "active",
          variableCatalogVersionId: "catalog-1",
          parameterSetId: "params-1",
          pipelineStrategyId: "pipeline-1",
          ruleVersionIds: ["rule-version-1"],
        },
      };

      return new Response(JSON.stringify(payloadByPath[path]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });

    const client = new EngineAdminApiClient("token-123", fetcher as typeof fetch);
    const result = await runEngineAdminLifecycle(client, emptyEngineAdminWorkspaceState);

    expect(result.workflowVersion.status).toBe("draft");
    expect(calls).toEqual([
      "POST /api/v1/admin/engine/products",
      "POST /api/v1/admin/engine/products/PLD/activation",
      "POST /api/v1/admin/engine/products/PLD/workflows",
      "POST /api/v1/admin/engine/products/PLD/variables",
      "POST /api/v1/admin/engine/variables/variable-1/activation",
      "POST /api/v1/admin/engine/products/PLD/variable-catalogs",
      "POST /api/v1/admin/engine/variable-catalogs/catalog-1/activation",
      "POST /api/v1/admin/engine/products/PLD/parameter-sets",
      "POST /api/v1/admin/engine/parameter-sets/params-1/activation",
      "POST /api/v1/admin/engine/products/PLD/pipeline-strategies",
      "POST /api/v1/admin/engine/pipeline-strategies/pipeline-1/activation",
      "POST /api/v1/admin/engine/workflows/workflow-1/rules",
      "POST /api/v1/admin/engine/rule-versions/rule-version-1/activation",
      "POST /api/v1/admin/engine/workflows/workflow-1/versions",
      "POST /api/v1/admin/engine/workflow-versions/workflow-version-1/activation",
    ]);
  });
});
