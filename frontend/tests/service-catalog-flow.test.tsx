// @vitest-environment jsdom

import React, { act } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";
import { createTestAppHost, jsonResponse, resetBrowserState } from "./test-utils";

function stubMeResponse(username: string, displayName: string, roles: string[]) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const path = String(input);
      if (path === "/api/v1/me") {
        return jsonResponse({
          id: `user-${username}`,
          username,
          display_name: displayName,
          roles,
        });
      }

      throw new Error(`Unexpected fetch: ${path}`);
    }),
  );
}

describe("service catalog flow", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("shows only role-allowed services for analista users", async () => {
    saveStoredSession({
      accessToken: "token-analista",
      me: {
        id: "user-analista",
        username: "analista",
        displayName: "Analista Uno",
        roles: ["analista"],
      },
    });
    window.location.hash = "#/productos/PLD/servicios";
    stubMeResponse("analista", "Analista Uno", ["analista"]);

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(host.container.textContent).toContain("Servicios");
    expect(host.container.textContent).toContain("PLD");
    expect(host.container.textContent).toContain("Bandeja de solicitudes");
    expect(host.container.textContent).not.toContain("Motor de decisiones");
    expect(host.container.textContent).not.toContain("Modelo de datos");

    host.cleanup();
  });

  it("shows the admin service grid and opens a service workspace", async () => {
    saveStoredSession({
      accessToken: "token-riesgos",
      me: {
        id: "user-riesgos",
        username: "riesgos",
        displayName: "Equipo Riesgos",
        roles: ["admin_riesgos"],
      },
    });
    window.location.hash = "#/productos/PLD/servicios";
    stubMeResponse("riesgos", "Equipo Riesgos", ["admin_riesgos"]);

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(host.container.textContent).toContain("Bandeja de solicitudes");
    expect(host.container.textContent).toContain("Motor de decisiones");
    expect(host.container.textContent).toContain("Modelo de datos");

    const serviceButton = host.container.querySelector('[aria-label="Abrir servicio Motor de decisiones"]');
    expect(serviceButton).toBeInstanceOf(HTMLButtonElement);

    await act(async () => {
      serviceButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(window.location.hash).toBe("#/productos/PLD/servicios/decision-engine");
    expect(host.container.textContent).toContain("Workspace");
    expect(host.container.textContent).toContain("Motor de decisiones");

    host.cleanup();
  });
});
