import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";


describe("frontend index.html", () => {
  it("references a favicon asset", () => {
    const html = readFileSync(resolve(__dirname, "../index.html"), "utf8");

    expect(html).toMatch(/<link\s+rel="icon"[^>]+href="\/favicon\.svg"/i);
  });
});
