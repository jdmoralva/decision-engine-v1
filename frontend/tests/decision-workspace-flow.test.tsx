// @vitest-environment jsdom

import React, { act } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";
import { createTestAppHost, jsonResponse, resetBrowserState } from "./test-utils";

function stubWorkspaceFetches() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const path = String(input);

      if (path === "/api/v1/me") {
        return jsonResponse({
          id: "user-riesgos",
          username: "riesgos",
          display_name: "Equipo Riesgos",
          roles: ["admin_riesgos"],
        });
      }

      if (path === "/api/v1/admin/engine/products/PLD/workflows") {
        return jsonResponse({
          items: [
            {
              id: "wf-active",
              productCode: "PLD",
              workflowCode: "originacion",
              name: "Workflow Originacion",
              description: "Gobernado",
              status: "active",
            },
          ],
        });
      }

      if (path === "/api/v1/admin/engine/products/PLD/workflows?state=draft") {
        return jsonResponse({
          items: [
            {
              id: "wf-draft",
              productCode: "PLD",
              workflowCode: "pre-originacion",
              name: "Workflow Pre Originacion",
              description: "Borrador",
              status: "draft",
            },
          ],
        });
      }

      throw new Error(`Unexpected fetch: ${path}`);
    }),
  );
}

describe("decision workspace flow", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("renders sidebar, canvas and inspector, then updates selection state", async () => {
    saveStoredSession({
      accessToken: "token-riesgos",
      me: {
        id: "user-riesgos",
        username: "riesgos",
        displayName: "Equipo Riesgos",
        roles: ["admin_riesgos"],
      },
    });
    window.location.hash = "#/productos/PLD/servicios/decision-engine";
    stubWorkspaceFetches();

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(host.container.textContent).toContain("Reglas de Negocio");
    expect(host.container.textContent).toContain("Parametros");
    expect(host.container.textContent).toContain("Data");
    expect(host.container.textContent).toContain("Workflow Originacion");
    expect(host.container.textContent).toContain("Inspector");
    expect(host.container.textContent).toContain("Inicio");

    const nodeButton = host.container.querySelector('[aria-label="Nodo Inicio"]');
    expect(nodeButton).toBeInstanceOf(HTMLButtonElement);

    await act(async () => {
      nodeButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(host.container.textContent).toContain("Nodo seleccionado");
    expect(host.container.textContent).toContain("Tipo inicio");

    const moveButton = host.container.querySelector('[aria-label="Mover nodo seleccionado"]');
    expect(moveButton).toBeInstanceOf(HTMLButtonElement);

    await act(async () => {
      moveButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(sessionStorage.length).toBeGreaterThan(0);

    host.cleanup();
  });
});
