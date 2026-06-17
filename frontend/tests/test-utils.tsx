// @vitest-environment jsdom

import React, { act } from "react";
import ReactDOM from "react-dom/client";

export function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export function resetBrowserState(): void {
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  sessionStorage.clear();
  window.location.hash = "";
}

export function createTestAppHost() {
  const container = document.createElement("div");
  document.body.appendChild(container);
  const root = ReactDOM.createRoot(container);

  return {
    container,
    root,
    async render(ui: React.ReactNode) {
      await act(async () => {
        root.render(ui);
      });
    },
    cleanup() {
      act(() => {
        root.unmount();
      });
      container.remove();
    },
  };
}
