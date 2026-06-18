// @vitest-environment jsdom

import React from "react";
import { act } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";
import { saveWorkspaceDraft } from "../src/features/decision-workspace/workspace-session";
import { createTestAppHost, jsonResponse, resetBrowserState } from "./test-utils";

describe("app shell", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("redirects protected product routes to login when there is no session", async () => {
    window.location.hash = "#/productos";

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(window.location.hash).toBe("#/login");
    expect(host.container.textContent).toContain("Inicio de sesion");

    host.cleanup();
  });

  it("clears authenticated and workspace session state on logout", async () => {
    saveStoredSession({
      accessToken: "token-admin",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
    });
    saveWorkspaceDraft({
      productCode: "PLD",
      serviceKey: "DecisionEngine",
      workflowId: "wf-1",
      workflowCode: "originacion",
      title: "Workflow originacion",
      activeSidebarGroup: "Reglas de Negocio",
      activeSidebarItem: "workflows",
      selectedNodeId: "node-1",
      viewport: { x: 10, y: 20, zoom: 1.1 },
      dirty: true,
    });
    window.location.hash = "#/productos";

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const path = String(input);
        if (path === "/api/v1/me") {
          return jsonResponse({
            id: "user-1",
            username: "admin",
            display_name: "Administrador",
            roles: ["admin"],
          });
        }
        throw new Error(`Unexpected fetch: ${path}`);
      }),
    );

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    const logoutButton = Array.from(host.container.querySelectorAll("button")).find(
      (button) => button.textContent?.includes("Cerrar sesion"),
    );
    expect(logoutButton).toBeDefined();

    await act(async () => {
      logoutButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(localStorage.getItem("decision-engine.session")).toBeNull();
    expect(
      sessionStorage.getItem("decision-engine.workspace.PLD.DecisionEngine.wf-1"),
    ).toBeNull();
    expect(window.location.hash).toBe("#/login");

    host.cleanup();
  });
});
