// @vitest-environment jsdom

import React, { act } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";
import { createTestAppHost, jsonResponse, resetBrowserState } from "./test-utils";

function stubMeResponse() {
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

      throw new Error(`Unexpected fetch: ${path}`);
    }),
  );
}

describe("service workspace flow", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("renders shared sidebar navigation for placeholder services and updates the route", async () => {
    saveStoredSession({
      accessToken: "token-riesgos",
      me: {
        id: "user-riesgos",
        username: "riesgos",
        displayName: "Equipo Riesgos",
        roles: ["admin_riesgos"],
      },
    });
    window.location.hash = "#/productos/PLD/servicios/data-model";
    stubMeResponse();

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(host.container.textContent).toContain("Modelo de datos");
    expect(host.container.textContent).toContain("Resumen");
    expect(host.container.textContent).toContain("Entidades");
    expect(host.container.textContent).toContain("Relaciones");
    expect(host.container.textContent).toContain("Catalogos");
    expect(host.container.textContent).toContain("Calidad");
    expect(host.container.textContent).toContain("Publicacion");
    expect(host.container.textContent).not.toContain("Inspector");

    const relationshipsButton = host.container.querySelector('[aria-label="Abrir Relaciones"]');
    expect(relationshipsButton).toBeInstanceOf(HTMLButtonElement);

    await act(async () => {
      relationshipsButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(window.location.hash).toBe("#/productos/PLD/servicios/data-model/relaciones");
    expect(host.container.textContent).toContain("Relaciones");
    expect(host.container.textContent).toContain("Mock operativo");

    host.cleanup();
  });
});
