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


describe("evaluation flow", () => {
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
    window.location.hash = "#/evaluaciones";
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

  it("executes an evaluation and renders the resulting trace", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
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
      if (path === "/api/v1/loans/PLD/evaluaciones") {
        return jsonResponse({
          evaluation_id: "eval-1",
          product_code: "PLD",
          eligible: true,
          alerts: ["manual_review"],
          blocks: [],
          applied_versions: {
            rule_set_version: "pld.collect_context:1",
            parameter_version: "1",
            pipeline_version: "1",
          },
          decision_trace_id: "trace-1",
          product_result: {
            offered_amount: 9800,
            installment_amount: 310,
            term_months: 48,
            rate: 0.185,
          },
        }, 201);
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
          alerts: ["manual_review"],
          blocks: [],
          rules_applied: ["pld.calculate_metrics"],
          consumed_variables: ["campaign_code", "reported_debt"],
          produced_variables: ["offered_amount"],
          produced_effects: ["decision_ready"],
          nodes_executed: [
            {
              node_key: "calculate_metrics",
              node_type: "metrics",
              outcome: "calculated",
              rules_applied: ["pld.calculate_metrics"],
              consumed_variables: ["campaign_code", "reported_debt"],
              produced_variables: ["offered_amount"],
              produced_effects: ["decision_ready"],
            },
          ],
          evidence: [
            {
              source_type: "campaign_db",
              source_key: "product_context:campaign_code",
              field_name: "campaign_code",
              field_value: "PLD_48M",
              used_by_engine: true,
            },
          ],
        });
      }
      throw new Error(`Unexpected fetch: ${path}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    await act(async () => {
      root.render(<App />);
    });

    const submitButton = Array.from(container.querySelectorAll("button")).find(
      (button) => button.textContent?.includes("Evaluar"),
    ) as HTMLButtonElement;

    await act(async () => {
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("Resultado de evaluacion");
    expect(container.textContent).toContain("9800");
    expect(container.textContent).toContain("calculate_metrics");
  });
});
