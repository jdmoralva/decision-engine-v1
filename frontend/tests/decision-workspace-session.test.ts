import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearWorkspaceDraft,
  loadWorkspaceDraft,
  saveWorkspaceDraft,
} from "../src/features/decision-workspace/workspace-session";

describe("decision workspace session", () => {
  beforeEach(() => {
    const store = new Map<string, string>();

    vi.stubGlobal("sessionStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => store.set(key, value),
      removeItem: (key: string) => store.delete(key),
      key: (index: number) => Array.from(store.keys())[index] ?? null,
      get length() {
        return store.size;
      },
    });
  });

  it("persists a rich workspace draft with nodes, connections and execution history", () => {
    saveWorkspaceDraft({
      productCode: "PLD",
      serviceKey: "DecisionEngine",
      workflowId: "wf-42",
      workflowCode: "originacion",
      title: "Workflow originacion",
      activeSidebarGroup: "Reglas de Negocio",
      activeSidebarItem: "workflows",
      selectedNodeId: "node-start",
      viewport: { x: 30, y: 20, zoom: 1.15 },
      dirty: true,
      nodes: [
        { id: "node-start", name: "Inicio", type: "inicio", x: 80, y: 120 },
        { id: "node-score", name: "Score", type: "score", x: 260, y: 120 },
      ],
      connections: [
        { id: "edge-1", sourceNodeId: "node-start", targetNodeId: "node-score", label: "continuar" },
      ],
      executionHistory: ["Nodo Inicio ejecutado"],
      validationMessages: ["Compatibilidad valida"],
    });

    expect(loadWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" })).toMatchObject({
      selectedNodeId: "node-start",
      dirty: true,
      nodes: expect.arrayContaining([
        expect.objectContaining({ id: "node-start", type: "inicio" }),
      ]),
      connections: expect.arrayContaining([
        expect.objectContaining({ id: "edge-1", label: "continuar" }),
      ]),
      executionHistory: ["Nodo Inicio ejecutado"],
      validationMessages: ["Compatibilidad valida"],
    });
  });

  it("clears malformed rich drafts", () => {
    sessionStorage.setItem("decision-engine.workspace.PLD.DecisionEngine.wf-42", JSON.stringify({ invalid: true }));

    expect(loadWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" })).toBeNull();

    clearWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" });
    expect(loadWorkspaceDraft({ productCode: "PLD", serviceKey: "DecisionEngine", workflowId: "wf-42" })).toBeNull();
  });
});
