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
        return jsonResponse({ items: [] });
      }

      if (path === "/api/v1/admin/engine/products/PLD/workflows?state=draft") {
        return jsonResponse({ items: [] });
      }

      throw new Error(`Unexpected fetch: ${path}`);
    }),
  );
}

describe("decision workspace admin sections", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("shows parametros and data sections, then handles local profile actions and logout", async () => {
    saveStoredSession({
      accessToken: "token-riesgos",
      me: { id: "user-riesgos", username: "riesgos", displayName: "Equipo Riesgos", roles: ["admin_riesgos"] },
    });
    window.location.hash = "#/productos/PLD/servicios/decision-engine/parametros/limites-internos";
    stubWorkspaceFetches();

    const host = createTestAppHost();
    await host.render(<App />);
    await act(async () => {});

    expect(host.container.textContent).toContain("Limites internos");
    expect(host.container.textContent).toContain("Editable por riesgos");

    const dataButton = host.container.querySelector('[aria-label="Abrir Importar dataset"]');
    await act(async () => {
      dataButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(host.container.textContent).toContain("Importar dataset");
    expect(host.container.textContent).toContain("Gobernanza pendiente");

    const profileButton = host.container.querySelector('[aria-label="Abrir perfil de usuario"]');
    await act(async () => {
      profileButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    const passwordButton = host.container.querySelector('[aria-label="Cambiar contrasena"]');
    await act(async () => {
      passwordButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(host.container.textContent).toContain("Cambio de contrasena disponible como demo local");

    const permissionsButton = host.container.querySelector('[aria-label="Consultar permisos aprobados"]');
    await act(async () => {
      permissionsButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });
    expect(host.container.textContent).toContain("Permisos aprobados visibles como referencia local");

    const logoutButton = host.container.querySelector('[aria-label="Cerrar sesion workspace"]');
    await act(async () => {
      logoutButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(window.location.hash).toBe("#/login");
    expect(localStorage.getItem("decision-engine.session")).toBeNull();

    host.cleanup();
  });
});
