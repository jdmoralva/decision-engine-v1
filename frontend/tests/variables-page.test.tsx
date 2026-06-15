// @vitest-environment jsdom

import { afterEach, describe, expect, it, vi } from "vitest";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";

import { VariablesPage } from "../src/features/engine-admin/VariablesPage";

vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);

type MockClient = {
  createVariable: ReturnType<typeof vi.fn>;
  activateVariable: ReturnType<typeof vi.fn>;
  createVariableCatalog: ReturnType<typeof vi.fn>;
  activateVariableCatalog: ReturnType<typeof vi.fn>;
};

const workspace = {
  productCode: "PLD",
  productName: "Prestamo de Libre Disponibilidad",
  workflowCode: "standard",
  workflowId: null,
  variableId: null,
  catalogId: null,
  parameterSetId: null,
  pipelineStrategyId: null,
  ruleId: null,
  ruleVersionId: null,
  workflowVersionId: null,
  selectedRoleCode: "admin_negocio",
  selectedPermissionCodes: [],
};

let root: Root | null = null;

afterEach(() => {
  if (root !== null) {
    act(() => {
      root?.unmount();
    });
    root = null;
  }
  document.body.innerHTML = "";
});

function renderVariablesPage(client: MockClient, onWorkspaceChange = vi.fn(), onNotice = vi.fn()) {
  const container = document.createElement("div");
  document.body.append(container);
  root = createRoot(container);

  act(() => {
    root?.render(
      <VariablesPage
        client={client as never}
        workspace={workspace}
        onWorkspaceChange={onWorkspaceChange}
        onNotice={onNotice}
      />,
    );
  });

  return { container, onWorkspaceChange, onNotice };
}

function setInputValue(input: HTMLInputElement | HTMLSelectElement, value: string) {
  act(() => {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function setCheckboxValue(input: HTMLInputElement, value: boolean) {
  act(() => {
    input.checked = value;
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

describe("VariablesPage", () => {
  it("submits the variable draft entered by the operator", async () => {
    const client: MockClient = {
      createVariable: vi.fn().mockResolvedValue({ id: "var-1", variableKey: "segment_code" }),
      activateVariable: vi.fn(),
      createVariableCatalog: vi.fn(),
      activateVariableCatalog: vi.fn(),
    };
    const onWorkspaceChange = vi.fn();
    const onNotice = vi.fn();
    const { container } = renderVariablesPage(client, onWorkspaceChange, onNotice);

    const variableKey = container.querySelector('input[name="variableKey"]') as HTMLInputElement | null;
    const name = container.querySelector('input[name="name"]') as HTMLInputElement | null;
    const businessMeaning = container.querySelector('textarea[name="businessMeaning"]') as HTMLTextAreaElement | null;
    const dataType = container.querySelector('select[name="dataType"]') as HTMLSelectElement | null;
    const required = container.querySelector('input[name="required"]') as HTMLInputElement | null;
    const allowedSource = container.querySelector('select[name="allowedSource"]') as HTMLSelectElement | null;
    const submit = container.querySelector('button[type="submit"]') as HTMLButtonElement | null;

    expect(variableKey).not.toBeNull();
    expect(name).not.toBeNull();
    expect(businessMeaning).not.toBeNull();
    expect(dataType).not.toBeNull();
    expect(required).not.toBeNull();
    expect(allowedSource).not.toBeNull();
    expect(submit).not.toBeNull();

    setInputValue(variableKey!, "segment_code");
    setInputValue(name!, "Segmento");
    setInputValue(businessMeaning!, "Segmento comercial");
    setInputValue(dataType!, "string");
    setCheckboxValue(required!, true);
    setInputValue(allowedSource!, "user_input");

    await act(async () => {
      submit!.click();
    });

    expect(client.createVariable).toHaveBeenCalledWith("PLD", {
      variableKey: "segment_code",
      name: "Segmento",
      businessMeaning: "Segmento comercial",
      dataType: "string",
      required: true,
      allowedSource: "user_input",
    });
    expect(onWorkspaceChange).toHaveBeenCalledWith({ variableId: "var-1" });
    expect(onNotice).toHaveBeenCalledWith("Variable segment_code creada.");
  });
});
