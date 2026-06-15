// @vitest-environment jsdom

import React, { act } from "react";
import ReactDOM from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  emptyEngineAdminWorkspaceState,
  EngineAdminApiClient,
  runEngineAdminLifecycle,
} from "../src/services/engine-admin-api";
import { ProductsPage } from "../src/features/engine-admin/ProductsPage";
import { ProfilePermissionsPage } from "../src/features/engine-admin/ProfilePermissionsPage";
import { WorkflowsPage } from "../src/features/engine-admin/WorkflowsPage";


function flushPromises() {
  return act(async () => {
    await Promise.resolve();
  });
}


describe("engine admin lifecycle", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  beforeEach(() => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;
    container = document.createElement("div");
    document.body.appendChild(container);
    root = ReactDOM.createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
    vi.restoreAllMocks();
  });

  it("starts with a neutral empty workspace", () => {
    expect(emptyEngineAdminWorkspaceState).toMatchObject({
      productCode: "",
      productName: "",
      workflowCode: "",
      workflowId: null,
      selectedRoleCode: "admin_negocio",
    });
  });

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
    const result = await runEngineAdminLifecycle(client, {
      ...emptyEngineAdminWorkspaceState,
      productCode: "PLD",
      productName: "Prestamo Libre Disponibilidad",
      workflowCode: "standard",
    });

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

  it("supports profile-permission administration and governed delete operations", async () => {
    const calls: string[] = [];
    const fetcher = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      calls.push(`${init?.method ?? "GET"} ${path}`);

      const payloadByPath: Record<string, unknown> = {
        "/api/v1/admin/engine/profiles/admin_negocio/permissions": {
          roleCode: "admin_negocio",
          permissions: [{ code: "consultar_auditoria", name: "Consultar Auditoria" }],
        },
      };

      return new Response(JSON.stringify(payloadByPath[path] ?? null), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });

    const client = new EngineAdminApiClient("token-123", fetcher as typeof fetch);

    const currentPermissions = await client.getProfilePermissions("admin_negocio");
    const updatedPermissions = await client.replaceProfilePermissions("admin_negocio", [
      "consultar_auditoria",
    ]);
    await client.deleteProduct("PLD");
    await client.deleteWorkflow("workflow-1");
    await client.deleteRule("rule-1");

    expect(currentPermissions.roleCode).toBe("admin_negocio");
    expect(updatedPermissions.permissions[0]?.code).toBe("consultar_auditoria");
    expect(calls).toEqual([
      "GET /api/v1/admin/engine/profiles/admin_negocio/permissions",
      "PUT /api/v1/admin/engine/profiles/admin_negocio/permissions",
      "DELETE /api/v1/admin/engine/products/PLD",
      "DELETE /api/v1/admin/engine/workflows/workflow-1",
      "DELETE /api/v1/admin/engine/rules/rule-1",
    ]);
  });

  it("supports active and draft listings plus detail retrieval", async () => {
    const calls: string[] = [];
    const fetcher = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      calls.push(`${init?.method ?? "GET"} ${path}`);

      const payloadByPath: Record<string, unknown> = {
        "/api/v1/admin/engine/products": {
          items: [{ id: "PLD", productCode: "PLD", name: "Producto Activo", status: "active" }],
        },
        "/api/v1/admin/engine/products?state=draft": {
          items: [{ id: "AUTO", productCode: "AUTO", name: "Producto Draft", status: "draft" }],
        },
        "/api/v1/admin/engine/products/AUTO": {
          id: "AUTO",
          productCode: "AUTO",
          name: "Producto Draft",
          status: "draft",
          approval: { status: "pending", approvedBy: null, approvedAt: null },
          activeWorkflows: [],
        },
        "/api/v1/admin/engine/products/AUTO/workflows?state=draft": {
          items: [{ id: "wf-1", productCode: "AUTO", workflowCode: "draft", name: "Workflow Draft", status: "draft" }],
        },
        "/api/v1/admin/engine/workflows/wf-1": {
          id: "wf-1",
          productCode: "AUTO",
          workflowCode: "draft",
          name: "Workflow Draft",
          status: "draft",
          approval: { status: "pending", approvedBy: null, approvedAt: null },
          variables: [],
          parameterSets: [],
          rules: [],
        },
      };

      return new Response(JSON.stringify(payloadByPath[path]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });

    const client = new EngineAdminApiClient("token-123", fetcher as typeof fetch);

    const activeProducts = await client.listProducts();
    const draftProducts = await client.listProducts("draft");
    const productDetail = await client.getProductDetail("AUTO");
    const draftWorkflows = await client.listWorkflows("AUTO", "draft");
    const workflowDetail = await client.getWorkflowDetail("wf-1");

    expect(activeProducts.items[0]?.productCode).toBe("PLD");
    expect(draftProducts.items[0]?.status).toBe("draft");
    expect(productDetail.approval.status).toBe("pending");
    expect(draftWorkflows.items[0]?.workflowCode).toBe("draft");
    expect(workflowDetail.approval.approvedBy).toBeNull();
    expect(calls).toEqual([
      "GET /api/v1/admin/engine/products",
      "GET /api/v1/admin/engine/products?state=draft",
      "GET /api/v1/admin/engine/products/AUTO",
      "GET /api/v1/admin/engine/products/AUTO/workflows?state=draft",
      "GET /api/v1/admin/engine/workflows/wf-1",
    ]);
  });

  it("renders products page with active default, draft switch, detail metadata, and distinct retire/delete actions", async () => {
    const listProducts = vi
      .fn()
      .mockResolvedValueOnce({ items: [{ id: "PLD", productCode: "PLD", name: "Producto Activo", status: "active" }] })
      .mockResolvedValueOnce({ items: [{ id: "AUTO", productCode: "AUTO", name: "Producto Draft", status: "draft" }] });
    const getProductDetail = vi.fn().mockResolvedValue({
      id: "AUTO",
      productCode: "AUTO",
      name: "Producto Draft",
      status: "draft",
      createdBy: "negocio",
      createdAt: "2026-06-14T10:00:00Z",
      lastModifiedAt: "2026-06-14T10:00:00Z",
      approval: { status: "pending", approvedBy: null, approvedAt: null },
      retirement: { performedBy: null, performedAt: null, reason: null },
      deletion: { performedBy: null, performedAt: null, reason: null },
      activeWorkflows: [],
    });
    const client = {
      listProducts,
      getProductDetail,
      createProduct: vi.fn(),
      activateProduct: vi.fn(),
      retireProduct: vi.fn(),
      deleteProduct: vi.fn(),
      createWorkflow: vi.fn(),
    } as unknown as EngineAdminApiClient;

    let workspace = { ...emptyEngineAdminWorkspaceState };
    const onWorkspaceChange = vi.fn((patch: Partial<typeof workspace>) => {
      workspace = { ...workspace, ...patch };
    });
    const onNotice = vi.fn();

    await act(async () => {
      root.render(
        <ProductsPage
          client={client}
          workspace={workspace}
          onWorkspaceChange={onWorkspaceChange}
          onNotice={onNotice}
        />,
      );
    });
    await flushPromises();

    expect(listProducts).toHaveBeenCalledWith("active");
    expect(container.textContent).toContain("Vista actual: active");
    expect(container.textContent).toContain("PLD");
    expect(container.textContent).toContain("Retirar producto");
    expect(container.textContent).toContain("Eliminar producto draft");

    const draftButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Ver draft"),
    ) as HTMLButtonElement;
    await act(async () => {
      draftButton.click();
    });
    await flushPromises();

    expect(listProducts).toHaveBeenLastCalledWith("draft");
    expect(container.textContent).toContain("AUTO");

    const detailButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Ver detalle"),
    ) as HTMLButtonElement;
    await act(async () => {
      detailButton.click();
    });
    await flushPromises();

    expect(getProductDetail).toHaveBeenCalledWith("AUTO");
    expect(container.textContent).toContain("Aprobacion: pendiente");
    expect(container.textContent).toContain("Retiro: sin registro");
    expect(container.textContent).toContain("Eliminacion: sin registro");
  });

  it("renders workflow detail and distinct retire/delete semantics", async () => {
    const client = {
      listWorkflows: vi.fn().mockResolvedValue({
        items: [{ id: "wf-1", productCode: "PLD", workflowCode: "standard", name: "Workflow", status: "draft" }],
      }),
      getWorkflowDetail: vi.fn().mockResolvedValue({
        id: "wf-1",
        productCode: "PLD",
        workflowCode: "standard",
        name: "Workflow",
        status: "draft",
        createdBy: "negocio",
        createdAt: "2026-06-14T10:00:00Z",
        lastModifiedAt: "2026-06-14T10:00:00Z",
        approval: { status: "pending", approvedBy: null, approvedAt: null },
        retirement: { performedBy: null, performedAt: null, reason: null },
        deletion: { performedBy: null, performedAt: null, reason: null },
        variableCatalogVersionIds: [],
        parameterSetIds: [],
        pipelineStrategyIds: [],
        ruleVersionIds: ["rv-1"],
      }),
      createWorkflowVersion: vi.fn(),
      activateWorkflowVersion: vi.fn(),
      deleteWorkflow: vi.fn(),
      retireWorkflow: vi.fn(),
    } as unknown as EngineAdminApiClient;

    await act(async () => {
      root.render(
        <WorkflowsPage
          client={client}
          workspace={{ ...emptyEngineAdminWorkspaceState, productCode: "PLD" }}
          onWorkspaceChange={vi.fn()}
          onNotice={vi.fn()}
        />,
      );
    });
    await flushPromises();

    expect(container.textContent).toContain("Ver activos");
    expect(container.textContent).toContain("Eliminar workflow draft");
    expect(container.textContent).toContain("Retirar workflow");

    const detailButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Ver detalle"),
    ) as HTMLButtonElement;
    await act(async () => {
      detailButton.click();
    });
    await flushPromises();

    expect(container.textContent).toContain("Aprobacion: pendiente");
    expect(container.textContent).toContain("Retiro: sin registro");
    expect(container.textContent).toContain("Eliminacion: sin registro");
    expect(container.textContent).toContain("Reglas versionadas: 1");
  });

  it("syncs profile permission editor with loaded permissions and role changes", async () => {
    const client = {
      getProfilePermissions: vi
        .fn()
        .mockResolvedValueOnce({
          roleCode: "admin_negocio",
          permissions: [{ code: "consultar_auditoria", name: "Consultar Auditoria" }],
        })
        .mockResolvedValueOnce({
          roleCode: "admin_riesgos",
          permissions: [{ code: "administrar_reglas", name: "Administrar reglas" }],
        }),
      replaceProfilePermissions: vi.fn().mockResolvedValue({ roleCode: "admin_negocio", permissions: [] }),
    } as unknown as EngineAdminApiClient;

    let workspace = { ...emptyEngineAdminWorkspaceState };
    const onWorkspaceChange = vi.fn((patch: Partial<typeof workspace>) => {
      workspace = { ...workspace, ...patch };
    });

    await act(async () => {
      root.render(
        <ProfilePermissionsPage
          client={client}
          workspace={workspace}
          onWorkspaceChange={onWorkspaceChange}
          onNotice={vi.fn()}
        />,
      );
    });

    const loadButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Cargar permisos actuales"),
    ) as HTMLButtonElement;
    await act(async () => {
      loadButton.click();
    });
    await flushPromises();

    await act(async () => {
      root.render(
        <ProfilePermissionsPage
          client={client}
          workspace={workspace}
          onWorkspaceChange={onWorkspaceChange}
          onNotice={vi.fn()}
        />,
      );
    });
    await flushPromises();

    const textarea = container.querySelector("textarea") as HTMLTextAreaElement;
    expect(textarea.value).toContain("consultar_auditoria");
    expect(container.textContent).toContain("consultar_auditoria");

    const select = container.querySelector("select") as HTMLSelectElement;
    await act(async () => {
      select.value = "admin_riesgos";
      select.dispatchEvent(new Event("change", { bubbles: true }));
    });

    await act(async () => {
      root.render(
        <ProfilePermissionsPage
          client={client}
          workspace={{ ...workspace, selectedRoleCode: "admin_riesgos", selectedPermissionCodes: ["administrar_reglas"] }}
          onWorkspaceChange={onWorkspaceChange}
          onNotice={vi.fn()}
        />,
      );
    });
    await flushPromises();

    expect((container.querySelector("textarea") as HTMLTextAreaElement).value).toContain("administrar_reglas");
  });
});
