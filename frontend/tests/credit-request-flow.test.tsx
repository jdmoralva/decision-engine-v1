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


describe("credit request flow", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  beforeEach(() => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;
    localStorage.setItem(
      "decision-engine.session",
      JSON.stringify({
        accessToken: "token-123",
        me: {
          id: "user-1",
          username: "analista",
          displayName: "Analista Uno",
          roles: ["analista"],
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

  it("registers a request and renders the resulting detail", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path === "/api/v1/me") {
        return jsonResponse({
          id: "user-1",
          username: "analista",
          display_name: "Analista Uno",
          roles: ["analista"],
          authorization_mode: "request_time",
        });
      }
      if (path === "/api/v1/credit-requests?status=registrada") {
        return jsonResponse({ applied_filters: { status: "registrada" }, items: [] });
      }
      if (path === "/api/v1/credit-requests" && init?.method === "POST") {
        return jsonResponse({
          request_id: "req-1",
          product_code: "PLD",
          evaluation_id: "eval-1",
          workflow_code: "standard",
          status: "registrada",
          document: { document_type: "DNI", document_number: "12345678" },
          campaign_code: "PLD_48M",
          requested_amount: 9800,
          comment: "Solicitud inicial",
          created_by: { username: "analista" },
        }, 201);
      }
      if (path === "/api/v1/credit-requests/req-1") {
        return jsonResponse({
          request_id: "req-1",
          product_code: "PLD",
          evaluation_id: "eval-1",
          workflow_code: "standard",
          status: "registrada",
          document: { document_type: "DNI", document_number: "12345678" },
          campaign_code: "PLD_48M",
          requested_amount: 9800,
          comment: "Solicitud inicial",
          created_by: { username: "analista" },
          customer_name: "Cliente Demo PLD",
          created_at: "2026-06-14T12:00:00Z",
          updated_at: "2026-06-14T12:00:00Z",
          offered_amount: 9800,
          installment_amount: 310,
          term_months: 48,
          rate: 0.185,
          status_history: [
            {
              status: "registrada",
              comment: "Solicitud inicial",
              changed_by: { username: "analista" },
              changed_at: "2026-06-14T12:00:00Z",
            },
          ],
          attachments: [],
        });
      }
      throw new Error(`Unexpected fetch: ${path}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await act(async () => {
      root.render(<App />);
    });

    const evaluationIdInput = container.querySelector('input[name="evaluationId"]') as HTMLInputElement;
    const amountInput = container.querySelector('input[name="requestedAmount"]') as HTMLInputElement;
    const commentInput = container.querySelector('textarea[name="comment"]') as HTMLTextAreaElement;
    const submitButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Registrar solicitud"),
    ) as HTMLButtonElement;

    await act(async () => {
      evaluationIdInput.value = "eval-1";
      evaluationIdInput.dispatchEvent(new Event("input", { bubbles: true }));
      amountInput.value = "9800";
      amountInput.dispatchEvent(new Event("input", { bubbles: true }));
      commentInput.value = "Solicitud inicial";
      commentInput.dispatchEvent(new Event("input", { bubbles: true }));
    });

    await act(async () => {
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("req-1");
    expect(container.textContent).toContain("Cliente Demo PLD");
    expect(container.textContent).toContain("Historial de estados");
  });
});
