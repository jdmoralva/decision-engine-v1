import { afterEach, describe, expect, it } from "vitest";

import { AuthApiClient } from "../src/features/auth/auth-service";
import { EngineAdminApiClient } from "../src/services/engine-admin-api";
import { RuntimeApiClient } from "../src/services/runtime-api";

describe("fetch binding", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("binds global fetch for auth, runtime, and engine-admin clients", async () => {
    globalThis.fetch = function mockFetch(input: RequestInfo | URL) {
      if (this !== globalThis) {
        throw new TypeError("Illegal invocation");
      }

      const path = String(input);
      if (path === "/api/v1/me") {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: "user-1",
              username: "analista",
              display_name: "Analista",
              roles: ["analista"],
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          ),
        );
      }

      return Promise.resolve(
        new Response(JSON.stringify({ id: "product-1", productCode: "PLD", name: "PLD", status: "draft" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    } as typeof fetch;

    const me = await new AuthApiClient().restore("token-123");
    const consultation = await new RuntimeApiClient("token-123").consult("PLD", {
      document_type: "DNI",
      document_number: "12345678",
    });
    const product = await new EngineAdminApiClient("token-123").createProduct({
      productCode: "PLD",
      name: "PLD",
    });

    expect(me.username).toBe("analista");
    expect(consultation.product_code ?? "PLD").toBe("PLD");
    expect(product.productCode).toBe("PLD");
  });
});
