// @vitest-environment jsdom

import React, { act } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";
import { createTestAppHost, jsonResponse, resetBrowserState } from "./test-utils";

describe("product catalog flow", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("shows seeded products with quick actions and contextual menu actions", async () => {
    saveStoredSession({
      accessToken: "token-admin",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
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

    expect(host.container.textContent).toContain("Productos");
    expect(host.container.textContent).toContain("PLD");
    expect(host.container.textContent).toContain("Hipotecario");
    expect(host.container.textContent).toContain("Crear producto");
    expect(host.container.textContent).toContain("Servicios");
    expect(host.container.textContent).toContain("Configuracion");
    expect(host.container.textContent).toContain("Validacion");
    expect(host.container.textContent).toContain("Despliegue");

    const menuButton = host.container.querySelector('[aria-label="Acciones de PLD"]');
    expect(menuButton).toBeInstanceOf(HTMLButtonElement);

    await act(async () => {
      menuButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(host.container.textContent).toContain("Renombrar");
    expect(host.container.textContent).toContain("Duplicar");
    expect(host.container.textContent).toContain("Exportar");
    expect(host.container.textContent).toContain("Eliminar");

    host.cleanup();
  });

  it("opens the selected product without the menu blocking navigation", async () => {
    saveStoredSession({
      accessToken: "token-admin",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
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

    const menuButton = host.container.querySelector('[aria-label="Acciones de PLD"]');
    await act(async () => {
      menuButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    const productButton = host.container.querySelector('[aria-label="Abrir producto PLD"]');
    expect(productButton).toBeInstanceOf(HTMLButtonElement);

    await act(async () => {
      productButton?.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(window.location.hash).toBe("#/productos/PLD/servicios");
    expect(host.container.textContent).toContain("Servicios");
    expect(host.container.textContent).toContain("Motor de decisiones");

    host.cleanup();
  });
});
