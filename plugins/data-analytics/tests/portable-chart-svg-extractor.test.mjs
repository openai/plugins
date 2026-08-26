import assert from "node:assert/strict";
import test from "node:test";

import {
  injectPortableChartExtractionProbe,
  parsePortableChartExtractionDump,
} from "../skills/build-report/scripts/extract_portable_chart_svgs.mjs";

test("chart extraction instrumentation runs before the portable artifact CSP", () => {
  const html = [
    "<!doctype html>",
    "<html><head>",
    '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'">',
    "</head><body></body></html>",
  ].join("\n");
  const instrumented = injectPortableChartExtractionProbe(html, {
    colorScheme: "light",
    resultToken: "unit-test-token",
  });

  const probeIndex = instrumented.indexOf("data-portable-chart-extraction-probe");
  assert.ok(probeIndex > instrumented.indexOf("<head>"));
  assert.ok(probeIndex < instrumented.indexOf("Content-Security-Policy"));
  assert.match(instrumented, /extractChartVariantInBrowser/);
  assert.match(instrumented, /settleRenderedChartsInBrowser/);
});

test("chart extraction result parser requires one nonce-bound result", () => {
  const token = "unit-test-token";
  const payload = {
    charts: [{ chartId: "chart", chartKey: "block", variant: null }],
    externalRequests: [],
    ok: true,
  };
  const encoded = Buffer.from(JSON.stringify(payload), "utf8").toString("base64");
  const marker = `<meta data-result="${encoded}" data-portable-chart-extraction="${token}">`;

  assert.deepEqual(parsePortableChartExtractionDump(`<html>${marker}</html>`, token), payload);
  assert.throws(
    () => parsePortableChartExtractionDump(`<html>${marker}${marker}</html>`, token),
    (error) => error?.code === "probe_invalid",
  );
  assert.throws(
    () => parsePortableChartExtractionDump(`<html>${marker}</html>`, "different-token"),
    (error) => error?.code === "probe_missing",
  );
});

test("chart extraction instrumentation rejects HTML without a head", () => {
  assert.throws(
    () => injectPortableChartExtractionProbe("<html><body></body></html>", {}),
    (error) => error?.code === "html_invalid",
  );
});
