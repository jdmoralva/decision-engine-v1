import { describe, expect, it } from "vitest";

import { platformProducts, platformServices } from "../src/features/platform/platform-seed-data";
import { getStatusLabel } from "../src/features/platform/status-labels";
import { getVisibleServicesForRoles } from "../src/features/platform/service-visibility";

describe("platform catalog", () => {
  it("provides seeded products and services for the platform shell", () => {
    expect(platformProducts.map((product) => product.productCode)).toEqual(["PLD", "Hipotecario"]);
    expect(platformServices.map((service) => service.serviceKey)).toEqual([
      "CreditApplications",
      "DecisionEngine",
      "DataModel",
    ]);
  });

  it("derives visible services from authenticated roles", () => {
    expect(getVisibleServicesForRoles(["analista"]).map((service) => service.serviceKey)).toEqual([
      "CreditApplications",
    ]);
    expect(getVisibleServicesForRoles(["admin_riesgos"]).map((service) => service.serviceKey)).toEqual([
      "CreditApplications",
      "DecisionEngine",
      "DataModel",
    ]);
  });

  it("maps governed backend states to spanish labels", () => {
    expect(getStatusLabel("draft")).toBe("Borrador");
    expect(getStatusLabel("active")).toBe("Aprobado");
    expect(getStatusLabel("retired")).toBe("Retirado");
  });
});
