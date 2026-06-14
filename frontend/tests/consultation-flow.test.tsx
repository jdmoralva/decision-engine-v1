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


describe("consultation flow", () => {
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
    window.location.hash = "#/consultas";
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

  it("restores session and shows consultation results", async () => {
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
      if (path === "/api/v1/loans/PLD/consultas") {
        return jsonResponse({
          product_code: "PLD",
          document: { document_type: "DNI", document_number: "12345678" },
          customer: {
            customer_id: "c-1",
            full_name: "ANA CLIENTE",
            customer_type: "CLIENTE",
            profile_code: "PERFIL 1",
            sunedu_flag: "CON SUNEDU",
            employment_status: "DEP",
            validated_income: 2500,
          },
          campaigns: [
            {
              campaign_code: "PLD_48M",
              offered_amount: 12000,
              rate: 18.5,
              term_months: 48,
              installment_amount: 360,
              metadata: {},
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
      (button) => button.textContent?.includes("Consultar"),
    ) as HTMLButtonElement;

    await act(async () => {
      submitButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("ANA CLIENTE");
    expect(container.textContent).toContain("PLD_48M");
  });
});
