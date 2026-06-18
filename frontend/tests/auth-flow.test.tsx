// @vitest-environment jsdom

import React, { act } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";
import { createTestAppHost, jsonResponse, resetBrowserState } from "./test-utils";

describe("auth flow", () => {
  beforeEach(() => {
    resetBrowserState();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    resetBrowserState();
  });

  it("logs in and persists the restored session", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path === "/api/v1/auth/login") {
        expect(init?.method).toBe("POST");
        return jsonResponse({ access_token: "token-123", token_type: "bearer" });
      }
      if (path === "/api/v1/me") {
        return jsonResponse({
          id: "user-1",
          username: "analista",
          display_name: "Analista Uno",
          roles: ["analista"],
          authorization_mode: "request_time",
        });
      }
      throw new Error(`Unexpected fetch: ${path}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const host = createTestAppHost();

    await act(async () => {
      await host.render(<App />);
    });

    const usernameInput = host.container.querySelector('input[autocomplete="username"]') as HTMLInputElement;
    const passwordInput = host.container.querySelector('input[autocomplete="current-password"]') as HTMLInputElement;
    const submitButton = host.container.querySelector('button[type="submit"]') as HTMLButtonElement;

    await act(async () => {
      usernameInput.value = "analista";
      usernameInput.dispatchEvent(new Event("input", { bubbles: true }));
      passwordInput.value = "analista123";
      passwordInput.dispatchEvent(new Event("input", { bubbles: true }));
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(window.location.hash).toBe("#/productos");
    expect(host.container.textContent).toContain("Productos");
    expect(host.container.textContent).toContain("PLD");
    expect(host.container.textContent).toContain("analista");
    expect(localStorage.getItem("decision-engine.session")).toContain("token-123");

    host.cleanup();
  });

  it("restores a valid stored session into the product catalog", async () => {
    saveStoredSession({
      accessToken: "token-admin",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
    });

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

    expect(window.location.hash).toBe("#/productos");
    expect(host.container.textContent).toContain("Productos");
    expect(host.container.textContent).toContain("Hipotecario");
    expect(host.container.textContent).toContain("Administrador");

    host.cleanup();
  });
});
