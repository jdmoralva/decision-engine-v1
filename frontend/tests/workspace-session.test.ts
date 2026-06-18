import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearWorkspaceDraft,
  loadWorkspaceDraft,
  saveWorkspaceDraft,
} from "../src/features/decision-workspace/workspace-session";

describe("workspace session", () => {
  beforeEach(() => {
    const store = new Map<string, string>();

    vi.stubGlobal("sessionStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => store.set(key, value),
      removeItem: (key: string) => store.delete(key),
    });
  });

  it("persists and restores a workspace draft by product and workflow", () => {
    saveWorkspaceDraft({
      productCode: "PLD",
      serviceKey: "DecisionEngine",
      workflowId: "wf-42",
      workflowCode: "originacion",
      title: "Workflow originacion",
      activeSidebarGroup: "Reglas de Negocio",
      activeSidebarItem: "workflows",
      selectedNodeId: "node-7",
      viewport: { x: 100, y: 240, zoom: 1.25 },
      dirty: true,
    });

    expect(
      loadWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" }),
    ).toEqual({
      productCode: "PLD",
      serviceKey: "DecisionEngine",
      workflowId: "wf-42",
      workflowCode: "originacion",
      title: "Workflow originacion",
      activeSidebarGroup: "Reglas de Negocio",
      activeSidebarItem: "workflows",
      selectedNodeId: "node-7",
      viewport: { x: 100, y: 240, zoom: 1.25 },
      dirty: true,
    });
  });

  it("clears saved drafts and drops malformed payloads", () => {
    saveWorkspaceDraft({
      productCode: "PLD",
      serviceKey: "DecisionEngine",
      workflowId: "wf-42",
      workflowCode: "originacion",
      title: "Workflow originacion",
      activeSidebarGroup: "Reglas de Negocio",
      activeSidebarItem: "workflows",
      selectedNodeId: null,
      viewport: { x: 0, y: 0, zoom: 1 },
      dirty: false,
    });

    clearWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" });
    expect(
      loadWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" }),
    ).toBeNull();

    sessionStorage.setItem("decision-engine.workspace.PLD.DecisionEngine.wf-42", "not-json");
    expect(
      loadWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" }),
    ).toBeNull();
  });
});
