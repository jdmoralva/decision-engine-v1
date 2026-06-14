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


describe("audit timeline", () => {
  let container: HTMLDivElement;
  let root: ReactDOM.Root;

  beforeEach(() => {
    globalThis.IS_REACT_ACT_ENVIRONMENT = true;
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

  it("renders audit events and trace for evaluador", async () => {
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
          created_by: { username: "evaluador" },
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
          created_by: { username: "evaluador" },
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
              changed_by: { username: "evaluador" },
              changed_at: "2026-06-14T12:00:00Z",
            },
          ],
          attachments: [],
        });
      }
      if (path === "/api/v1/credit-requests/req-1/attachments") {
        return jsonResponse([]);
      }
      if (path === "/api/v1/audit?request_id=req-1&evaluation_id=eval-1") {
        return jsonResponse({
          page: 1,
          page_size: 50,
          total: 2,
          items: [
            {
              event_id: "evt-1",
              aggregate_id: "req-1",
              aggregate_type: "credit_request",
              event_type: "credit_request_created",
              event_payload: { request_id: "req-1" },
              created_by: { username: "evaluador" },
              created_at: "2026-06-14T12:00:00Z",
            },
            {
              event_id: "evt-2",
              aggregate_id: "att-1",
              aggregate_type: "credit_request_attachment",
              event_type: "attachment_uploaded",
              event_payload: { request_id: "req-1", original_filename: "evidencia.zip" },
              created_by: { username: "evaluador" },
              created_at: "2026-06-14T12:05:00Z",
            },
          ],
        });
      }
      if (path === "/api/v1/loans/PLD/evaluaciones/eval-1/trace") {
        return jsonResponse({
          trace_id: "trace-1",
          evaluation_id: "eval-1",
          product_code: "PLD",
          applied_versions: {
            rule_set_version: "pld.collect_context:1",
            parameter_version: "1",
            pipeline_version: "1",
          },
          alerts: [],
          blocks: [],
          rules_applied: ["pld.calculate_metrics"],
          consumed_variables: ["campaign_code"],
          produced_variables: ["offered_amount"],
          produced_effects: ["decision_ready"],
          nodes_executed: [
            {
              node_key: "calculate_metrics",
              node_type: "metrics",
              outcome: "calculated",
              rules_applied: ["pld.calculate_metrics"],
              consumed_variables: ["campaign_code"],
              produced_variables: ["offered_amount"],
              produced_effects: ["decision_ready"],
            },
          ],
          evidence: [],
        });
      }
      throw new Error(`Unexpected fetch: ${path}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await act(async () => {
      root.render(<App />);
    });

    const submitButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Registrar solicitud"),
    ) as HTMLButtonElement;

    await act(async () => {
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("Timeline de auditoria");
    expect(container.textContent).toContain("credit_request_created");
    expect(container.textContent).toContain("attachment_uploaded");
    expect(container.textContent).toContain("calculate_metrics");
  });

  it("hides audit timeline for analista without audit permission", async () => {
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
          status_history: [],
          attachments: [],
        });
      }
      if (path === "/api/v1/credit-requests/req-1/attachments") {
        return jsonResponse([]);
      }
      throw new Error(`Unexpected fetch: ${path}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await act(async () => {
      root.render(<App />);
    });

    const submitButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Registrar solicitud"),
    ) as HTMLButtonElement;

    await act(async () => {
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).not.toContain("Timeline de auditoria");
  });
});
