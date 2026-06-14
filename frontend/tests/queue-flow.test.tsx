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


describe("queue flow", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  beforeEach(() => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;
    localStorage.setItem(
      "decision-engine.session",
      JSON.stringify({
        accessToken: "token-123",
        me: {
          id: "user-2",
          username: "evaluador",
          displayName: "Evaluador Uno",
          roles: ["evaluador"],
        },
      }),
    );
    window.location.hash = "#/solicitudes";
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

  it("loads the queue, transitions a request, and exports the current filter", async () => {
    let queueStatus = "en_revision";
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path === "/api/v1/me") {
        return jsonResponse({
          id: "user-2",
          username: "evaluador",
          display_name: "Evaluador Uno",
          roles: ["evaluador"],
          authorization_mode: "request_time",
        });
      }
      if (path === "/api/v1/credit-requests?status=registrada") {
        return jsonResponse({ applied_filters: { status: "registrada" }, items: [] });
      }
      if (path === "/api/v1/credit-requests?status=en_revision") {
        return jsonResponse({
          applied_filters: { status: "en_revision" },
          items: [
            {
              request_id: "req-2",
              product_code: "PLD",
              workflow_code: "standard",
              evaluation_id: "eval-2",
              document: { document_type: "DNI", document_number: "12345678" },
              customer_name: "Cliente Demo PLD",
              status: queueStatus,
              created_at: "2026-06-14T12:00:00Z",
              updated_at: "2026-06-14T12:15:00Z",
              available_actions: queueStatus === "en_revision" ? ["aprobada", "rechazada", "anulada"] : [],
            },
          ],
        });
      }
      if (path === "/api/v1/credit-requests/req-2/status-transitions" && init?.method === "POST") {
        queueStatus = "aprobada";
        return jsonResponse({
          request_id: "req-2",
          product_code: "PLD",
          evaluation_id: "eval-2",
          workflow_code: "standard",
          status: "aprobada",
          document: { document_type: "DNI", document_number: "12345678" },
          campaign_code: "PLD_48M",
          requested_amount: 9800,
          comment: "Aprobada",
          created_by: { username: "analista" },
        });
      }
      if (path === "/api/v1/credit-requests/export?status=en_revision") {
        return new Response("filtros_aplicados,status=en_revision\nrequest_id\nreq-2\n", {
          status: 200,
          headers: { "Content-Type": "text/csv; charset=utf-8" },
        });
      }
      throw new Error(`Unexpected fetch: ${path}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await act(async () => {
      root.render(<App />);
    });

    const statusSelect = container.querySelector('select[name="queueStatus"]') as HTMLSelectElement;
    const loadButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Cargar bandeja"),
    ) as HTMLButtonElement;

    await act(async () => {
      statusSelect.value = "en_revision";
      statusSelect.dispatchEvent(new Event("change", { bubbles: true }));
    });

    await act(async () => {
      loadButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("req-2");
    expect(container.textContent).toContain("Cliente Demo PLD");

    const approveButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("aprobada"),
    ) as HTMLButtonElement;

    await act(async () => {
      approveButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("Estado actualizado a aprobada");

    const exportButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Exportar CSV"),
    ) as HTMLButtonElement;

    await act(async () => {
      exportButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("filtros_aplicados");
  });
});
