// @vitest-environment jsdom

import React, { act } from "react";
import ReactDOM from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";


function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}


describe("auth flow", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  beforeEach(() => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;
    localStorage.clear();
    window.location.hash = "";
    container = document.createElement("div");
    document.body.appendChild(container);
    root = ReactDOM.createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
    vi.restoreAllMocks();
    localStorage.clear();
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

    await act(async () => {
      root.render(<App />);
    });

    const usernameInput = container.querySelector('input[autocomplete="username"]') as HTMLInputElement;
    const passwordInput = container.querySelector('input[autocomplete="current-password"]') as HTMLInputElement;
    const submitButton = container.querySelector('button[type="submit"]') as HTMLButtonElement;

    await act(async () => {
      usernameInput.value = "analista";
      usernameInput.dispatchEvent(new Event("input", { bubbles: true }));
      passwordInput.value = "analista123";
      passwordInput.dispatchEvent(new Event("input", { bubbles: true }));
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("Acceso correcto.");
    expect(container.textContent).toContain("analista");
    expect(localStorage.getItem("decision-engine.session")).toContain("token-123");
  });
});
