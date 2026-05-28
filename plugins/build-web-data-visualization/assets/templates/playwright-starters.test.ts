import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
import { dirname, join } from "node:path";
import { describe, test } from "node:test";
import { fileURLToPath } from "node:url";

const templateDir = dirname(fileURLToPath(import.meta.url));

function readTemplate(name: string): string {
  return readFileSync(join(templateDir, name), "utf8");
}

describe("Playwright visualization starter templates", () => {
  test("visual regression starter uses deterministic browser settings", () => {
    const source = readTemplate("playwright-visual-regression-starter.ts");

    assert.match(source, /viewport: \{ width: 1280, height: 720 \}/);
    assert.match(source, /mobile-portrait/);
    assert.match(source, /mobile-landscape/);
    assert.match(source, /page\.setViewportSize/);
    assert.match(source, /reducedMotion: "reduce"/);
    assert.match(source, /timezoneId: "UTC"/);
    assert.match(source, /await page\.route/);
    assert.match(source, /toHaveScreenshot/);
    assert.match(source, /animations: "disabled"/);
  });

  test("PDF starter exports with print background and explicit margins", () => {
    const source = readTemplate("playwright-pdf-starter.ts");

    assert.match(source, /chromium\.launch/);
    assert.match(source, /page\.pdf/);
    assert.match(source, /printBackground: true/);
    assert.match(source, /format: "Letter"/);
    assert.match(source, /top: "16mm"/);
  });
});
