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
          id: "user-admin",
          username: "admin",
          display_name: "Administrador",
          roles: ["admin"],
        });
      }

      if (path === "/api/v1/admin/engine/products/PLD/workflows") {
        return jsonResponse({
          items: [
            { id: "wf-active", productCode: "PLD", workflowCode: "originacion", name: "Workflow Originacion", status: "active" },
          ],
        });
      }

      if (path === "/api/v1/admin/engine/products/PLD/workflows?state=draft") {
        return jsonResponse({
          items: [
            { id: "wf-draft", productCode: "PLD", workflowCode: "pre-originacion", name: "Workflow Pre Originacion", status: "draft" },
          ],
        });
      }

      throw new Error(`Unexpected fetch: ${path}`);
    }),
  );
}

describe("decision workspace catalogs", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("shows governed workflows and session-local channels, testing and events panels", async () => {
    saveStoredSession({
      accessToken: "token-admin",
      me: { id: "user-admin", username: "admin", displayName: "Administrador", roles: ["admin"] },
    });
    window.location.hash = "#/productos/PLD/servicios/decision-engine/workflows/approved-workflows";
    stubWorkspaceFetches();

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(host.container.textContent).toContain("Aprobado");
    expect(host.container.textContent).toContain("Borrador");
    expect(host.container.textContent).toContain("Workflow Originacion");

    const channelsButton = host.container.querySelector('[aria-label="Abrir channels"]');
    await act(async () => {
      channelsButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(host.container.textContent).toContain("Canales");
    expect(host.container.textContent).toContain("Workflow aprobado");
    expect(host.container.textContent).toContain("Compatibilidad valida");

    const testingButton = host.container.querySelector('[aria-label="Abrir testing"]');
    await act(async () => {
      testingButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(host.container.textContent).toContain("Pruebas AB");

    const eventsButton = host.container.querySelector('[aria-label="Abrir events"]');
    await act(async () => {
      eventsButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(host.container.textContent).toContain("Ultimos eventos");

    host.cleanup();
  });
});
