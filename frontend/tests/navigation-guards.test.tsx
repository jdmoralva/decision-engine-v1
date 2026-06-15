// @vitest-environment jsdom

import React, { act } from "react";
import ReactDOM from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { saveStoredSession } from "../src/session-storage";


function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}


describe("navigation guards", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  beforeEach(() => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;
    localStorage.clear();
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
    window.location.hash = "";
  });

  it("redirects non-admin users away from the admin hash route", async () => {
    saveStoredSession({
      accessToken: "token-analista",
      me: {
        id: "user-1",
        username: "analista",
        displayName: "Analista Uno",
        roles: ["analista"],
      },
    });
    window.location.hash = "#/admin";

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const path = String(input);
        if (path === "/api/v1/me") {
          return jsonResponse({
            id: "user-1",
            username: "analista",
            display_name: "Analista Uno",
            roles: ["analista"],
          });
        }
        throw new Error(`Unexpected fetch: ${path}`);
      }),
    );

    await act(async () => {
      root.render(<App />);
    });

    expect(window.location.hash).toBe("#/consultas");
    expect(container.textContent).not.toContain("Phase 3");
    expect(container.textContent).not.toContain("Motor");
  });

  it("allows admin users to stay on the admin hash route", async () => {
    saveStoredSession({
      accessToken: "token-admin",
      me: {
        id: "user-2",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
    });
    window.location.hash = "#/admin";

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const path = String(input);
        if (path === "/api/v1/me") {
          return jsonResponse({
            id: "user-2",
            username: "admin",
            display_name: "Administrador",
            roles: ["admin"],
          });
        }
        throw new Error(`Unexpected fetch: ${path}`);
      }),
    );

    await act(async () => {
      root.render(<App />);
    });

    expect(window.location.hash).toBe("#/admin");
    expect(container.textContent).toContain("Phase 3");
    expect(container.textContent).toContain("Motor");
  });

  it("redirects plataforma users away from the admin hash route", async () => {
    saveStoredSession({
      accessToken: "token-plataforma",
      me: {
        id: "user-3",
        username: "plataforma",
        displayName: "Plataforma",
        roles: ["plataforma"],
      },
    });
    window.location.hash = "#/admin";

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const path = String(input);
        if (path === "/api/v1/me") {
          return jsonResponse({
            id: "user-3",
            username: "plataforma",
            display_name: "Plataforma",
            roles: ["plataforma"],
          });
        }
        throw new Error(`Unexpected fetch: ${path}`);
      }),
    );

    await act(async () => {
      root.render(<App />);
    });

    expect(window.location.hash).toBe("#/consultas");
    expect(container.textContent).not.toContain("Phase 3");
  });
});
