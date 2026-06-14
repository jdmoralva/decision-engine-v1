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


describe("attachments flow", () => {
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

  it("uploads a zip and renders its manifest", async () => {
    let listedAttachments = [
      {
        attachment_id: "att-1",
        request_id: "req-1",
        original_filename: "evidencia.zip",
        mime_type: "application/zip",
        uploaded_at: "2026-06-14T12:05:00Z",
        uploaded_by: { username: "analista" },
        entry_count: 2,
      },
    ];

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
      if (path === "/api/v1/credit-requests/req-1/attachments") {
        if (init?.method === "POST") {
          return jsonResponse(listedAttachments[0], 201);
        }
        return jsonResponse(listedAttachments);
      }
      if (path === "/api/v1/credit-requests/req-1/attachments/att-1/manifest") {
        return jsonResponse({
          attachment_id: "att-1",
          request_id: "req-1",
          original_filename: "evidencia.zip",
          entries: [
            { path: "dni.txt", size: 8, compressed_size: 8 },
            { path: "carpeta/evidencia.json", size: 12, compressed_size: 12 },
          ],
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

    const fileInput = container.querySelector('input[name="attachmentFile"]') as HTMLInputElement;
    const uploadButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Cargar ZIP"),
    ) as HTMLButtonElement;

    await act(async () => {
      const file = new File(["zip-binary"], "evidencia.zip", { type: "application/zip" });
      Object.defineProperty(fileInput, "files", {
        value: [file],
        configurable: true,
      });
      fileInput.dispatchEvent(new Event("change", { bubbles: true }));
    });

    await act(async () => {
      uploadButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    const manifestButton = Array.from(container.querySelectorAll("button")).find((button) =>
      button.textContent?.includes("Ver contenido"),
    ) as HTMLButtonElement;

    await act(async () => {
      manifestButton.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    });

    expect(container.textContent).toContain("evidencia.zip");
    expect(container.textContent).toContain("dni.txt");
    expect(container.textContent).toContain("carpeta/evidencia.json");
  });
});
