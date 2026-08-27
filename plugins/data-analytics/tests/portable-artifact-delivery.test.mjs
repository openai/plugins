import assert from "node:assert/strict";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import {
  deliverPortableArtifact,
  parseArguments,
} from "../skills/build-report/scripts/deliver_portable_artifact.mjs";

test("combined delivery packages once, verifies once, and returns a compact receipt", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  const artifact = { manifest: { title: "One-pass report" } };
  writeFileSync(inputPath, JSON.stringify(artifact), "utf8");
  writeFileSync(outputPath, "previous report", "utf8");

  let packageCalls = 0;
  let extractionCalls = 0;
  let verificationCalls = 0;
  const packagedHtml = '<!doctype html><style>.portable-chart-summary{margin:0}</style><title>One-pass report</title>';
  const result = await deliverPortableArtifact({
    inputPath,
    outputPath,
    timeoutMs: 9_000,
  }, {
    build(input) {
      packageCalls += 1;
      assert.deepEqual(input, artifact);
      return packagedHtml;
    },
    async extract() {
      extractionCalls += 1;
      throw new Error("Chart-free delivery must not start static extraction.");
    },
    async verify(options) {
      verificationCalls += 1;
      assert.equal(options.artifactPath, inputPath);
      assert.notEqual(options.htmlPath, outputPath);
      assert.match(options.htmlPath, /report\.html\.tmp-/);
      assert.equal(options.htmlPath.endsWith(".html"), true);
      assert.equal(readFileSync(options.htmlPath, "utf8"), packagedHtml);
      assert.equal(readFileSync(outputPath, "utf8"), "previous report");
      assert.equal(options.timeoutMs, 9_000);
      return {
        ok: true,
        counts: { blocks: 3, charts: 1, html: 0, metrics: 1, tables: 1 },
        sourceDialog: "passed",
        timings: {
          browserLaunchMs: 100.1,
          documentLoadMs: 80.2,
          readerReadyMs: 90.3,
          totalMs: 321.4,
        },
        viewports: [1_440, 390],
      };
    },
  });

  assert.equal(packageCalls, 1);
  assert.equal(extractionCalls, 0);
  assert.equal(verificationCalls, 1);
  assert.equal(readFileSync(outputPath, "utf8"), packagedHtml);
  assert.equal(result.ok, true);
  assert.equal(result.html, outputPath);
  assert.deepEqual(result.stages, {
    validation: "passed",
    package: "passed",
    verification: "passed",
  });
  assert.deepEqual(result.counts, { blocks: 3, charts: 1, html: 0, metrics: 1, tables: 1 });
  assert.equal(result.sourceDialog, "passed");
  assert.deepEqual(result.viewports, [1_440, 390]);
  assert.equal(result.timings.browserLaunchMs, 100.1);
  assert.equal(result.timings.documentLoadMs, 80.2);
  assert.equal(result.timings.readerReadyMs, 90.3);
  assert.equal(result.timings.verificationMs, 321.4);
  assert.ok(result.timings.validateAndPackageMs >= 0);
  assert.ok(result.timings.totalMs >= result.timings.validateAndPackageMs);
});

test("combined delivery extracts chart SVGs, rebuilds the candidate, and still publishes atomically", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-svg-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  const artifact = { manifest: { title: "Vector report" } };
  writeFileSync(inputPath, JSON.stringify(artifact), "utf8");
  writeFileSync(outputPath, "previous report", "utf8");

  const staticCharts = {
    chart: {
      dark: {
        legend: { items: [], position: "bottom", title: null },
        svg: '<svg><rect fill="rgb(0, 0, 0)"></rect></svg>',
      },
      height: 320,
      light: {
        legend: { items: [], position: "bottom", title: null },
        svg: '<svg><rect fill="rgb(255, 255, 255)"></rect></svg>',
      },
      width: 640,
    },
  };
  let buildCalls = 0;
  let extractionCalls = 0;
  let verificationCalls = 0;
  const result = await deliverPortableArtifact({ inputPath, outputPath }, {
    build(input, options = {}) {
      buildCalls += 1;
      assert.deepEqual(input, artifact);
      if (buildCalls === 1) {
        assert.equal(options.staticCharts, undefined);
        return '<!doctype html><figure class="portable-content-card portable-chart-summary">seed</figure>';
      }
      assert.deepEqual(options.staticCharts, staticCharts);
      return '<!doctype html><figure class="portable-content-card portable-chart-summary">enriched</figure>';
    },
    async extract(options) {
      extractionCalls += 1;
      assert.match(options.htmlPath, /report\.html\.tmp-/);
      assert.equal(options.htmlPath.endsWith(".html"), true);
      assert.match(readFileSync(options.htmlPath, "utf8"), />seed</);
      assert.equal(readFileSync(outputPath, "utf8"), "previous report");
      return staticCharts;
    },
    async verify(options) {
      verificationCalls += 1;
      assert.match(readFileSync(options.htmlPath, "utf8"), />enriched</);
      assert.equal(readFileSync(outputPath, "utf8"), "previous report");
      return {
        counts: { blocks: 1, charts: 1, html: 0, metrics: 0, tables: 0 },
        sourceDialog: "not_applicable",
        timings: { totalMs: 1 },
        viewports: [1_440, 390],
      };
    },
  });

  assert.equal(buildCalls, 2);
  assert.equal(extractionCalls, 1);
  assert.equal(verificationCalls, 1);
  assert.match(readFileSync(outputPath, "utf8"), />enriched</);
  assert.ok(result.timings.staticChartExtractionMs >= 0);
});

test("combined delivery preserves an existing report when static chart extraction fails", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-svg-failure-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  writeFileSync(inputPath, JSON.stringify({ manifest: { title: "Failure" } }), "utf8");
  writeFileSync(outputPath, "previous verified report", "utf8");

  let candidatePath;
  let verificationCalls = 0;
  await assert.rejects(
    deliverPortableArtifact({ inputPath, outputPath }, {
      build: () => '<!doctype html><figure class="portable-content-card portable-chart-summary">seed</figure>',
      async extract(options) {
        candidatePath = options.htmlPath;
        throw new Error("Chart extraction failed.");
      },
      async verify() {
        verificationCalls += 1;
      },
    }),
    (error) => {
      assert.equal(error.deliveryResult.stage, "static_charts");
      assert.equal(error.deliveryResult.error, "Chart extraction failed.");
      return true;
    },
  );

  assert.equal(verificationCalls, 0);
  assert.equal(readFileSync(outputPath, "utf8"), "previous verified report");
  assert.equal(existsSync(candidatePath), false);
});

test("combined delivery publishes a structurally verified fallback when Chromium is unavailable", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-structural-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  const artifact = { manifest: { title: "Structural fallback" } };
  const packagedHtml = "<!doctype html><figure class=\"portable-content-card portable-chart-summary\">table fallback</figure>";
  writeFileSync(inputPath, JSON.stringify(artifact), "utf8");

  let runtimeVerificationCalls = 0;
  let structuralVerificationCalls = 0;
  const result = await deliverPortableArtifact({ inputPath, outputPath }, {
    build: () => packagedHtml,
    async extract() {
      const error = new Error("No installed headless shell was found.");
      error.code = "browser_unavailable";
      throw error;
    },
    async verify() {
      runtimeVerificationCalls += 1;
    },
    verifyStructure(options) {
      structuralVerificationCalls += 1;
      assert.equal(options.artifactPath, inputPath);
      assert.equal(readFileSync(options.htmlPath, "utf8"), packagedHtml);
      return {
        counts: { blocks: 1, charts: 1, html: 0, metrics: 0, tables: 0 },
        html: options.htmlPath,
        ok: true,
        title: artifact.manifest.title,
      };
    },
  });

  assert.equal(runtimeVerificationCalls, 0);
  assert.equal(structuralVerificationCalls, 1);
  assert.equal(readFileSync(outputPath, "utf8"), packagedHtml);
  assert.deepEqual(result.stages, {
    validation: "passed",
    package: "passed",
    verification: "structural_only",
  });
  assert.deepEqual(result.browserWarning, {
    code: "browser_unavailable",
    message: "No installed headless shell was found.",
  });
  assert.equal(result.sourceDialog, "not_verified");
  assert.equal(result.sourceInteraction, "not_verified");
  assert.deepEqual(result.viewports, []);
});

test("combined delivery never degrades reader timeouts to structural-only verification", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-no-timeout-fallback-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  writeFileSync(inputPath, JSON.stringify({ manifest: { title: "Timeout" } }), "utf8");

  let structuralVerificationCalls = 0;
  await assert.rejects(
    deliverPortableArtifact({ inputPath, outputPath }, {
      build: () => "<!doctype html><title>Timeout</title>",
      async verify() {
        const error = new Error("Reader startup timed out.");
        error.code = "reader_timeout";
        throw error;
      },
      verifyStructure() {
        structuralVerificationCalls += 1;
      },
    }),
    (error) => error.deliveryResult.code === "reader_timeout" &&
      error.deliveryResult.stage === "verification",
  );
  assert.equal(structuralVerificationCalls, 0);
  assert.equal(existsSync(outputPath), false);
});

test("combined delivery never degrades incompatible browser probe results", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-no-probe-fallback-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  writeFileSync(inputPath, JSON.stringify({ manifest: { title: "Probe" } }), "utf8");

  let structuralVerificationCalls = 0;
  await assert.rejects(
    deliverPortableArtifact({ inputPath, outputPath }, {
      build: () => "<!doctype html><title>Probe</title>",
      async verify() {
        const error = new Error("Chromium returned no verifier probe result.");
        error.code = "probe_missing";
        throw error;
      },
      verifyStructure() {
        structuralVerificationCalls += 1;
      },
    }),
    (error) => error.deliveryResult.code === "probe_missing" &&
      error.deliveryResult.stage === "verification",
  );
  assert.equal(structuralVerificationCalls, 0);
  assert.equal(existsSync(outputPath), false);
});

test("combined delivery returns aggregate validation issues without starting browser verification", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-validation-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  writeFileSync(inputPath, JSON.stringify({ manifest: {} }), "utf8");

  let verificationCalls = 0;
  await assert.rejects(
    deliverPortableArtifact({ inputPath, outputPath }, {
      build() {
        const error = new Error("Artifact validation failed with 2 issues.");
        error.issues = [
          { path: "$.manifest.title", message: "is required" },
          { path: "$.snapshot.datasets", message: "must not be empty" },
        ];
        throw error;
      },
      async verify() {
        verificationCalls += 1;
      },
    }),
    (error) => {
      assert.equal(error.deliveryResult.ok, false);
      assert.equal(error.deliveryResult.stage, "validation");
      assert.equal(error.deliveryResult.issues.length, 2);
      return true;
    },
  );

  assert.equal(verificationCalls, 0);
});

test("combined delivery preserves an existing report when verification fails", async () => {
  const directory = mkdtempSync(join(tmpdir(), "portable-delivery-failure-"));
  const inputPath = join(directory, "artifact.json");
  const outputPath = join(directory, "report.html");
  writeFileSync(inputPath, JSON.stringify({ manifest: { title: "Failure" } }), "utf8");
  writeFileSync(outputPath, "previous verified report", "utf8");

  let verificationCalls = 0;
  let candidatePath;
  await assert.rejects(
    deliverPortableArtifact({ inputPath, outputPath }, {
      build: () => "<!doctype html><title>Failure</title>",
      async verify(options) {
        verificationCalls += 1;
        candidatePath = options.htmlPath;
        assert.notEqual(candidatePath, outputPath);
        assert.equal(readFileSync(candidatePath, "utf8"), "<!doctype html><title>Failure</title>");
        assert.equal(readFileSync(outputPath, "utf8"), "previous verified report");
        const error = new Error("Reader did not become ready.\nBrowser logs:\nverbose launch diagnostics");
        error.verificationResult = {
          ok: false,
          code: "reader_timeout",
          error: error.message,
          html: outputPath,
          screenshot: join(directory, "failure.png"),
          timings: { totalMs: 10_000 },
        };
        throw error;
      },
    }),
    (error) => {
      assert.equal(error.deliveryResult.ok, false);
      assert.equal(error.deliveryResult.stage, "verification");
      assert.equal(error.deliveryResult.code, "reader_timeout");
      assert.equal(error.deliveryResult.error, "Reader did not become ready.");
      assert.equal(error.deliveryResult.html, undefined);
      assert.equal(error.deliveryResult.timings.verificationMs, 10_000);
      return true;
    },
  );

  assert.equal(verificationCalls, 1);
  assert.equal(readFileSync(outputPath, "utf8"), "previous verified report");
  assert.equal(existsSync(candidatePath), false);
});

test("combined delivery CLI accepts only the package and bounded verification inputs", () => {
  assert.deepEqual(parseArguments([
    "--input",
    "artifact.json",
    "--output",
    "report.html",
    "--timeout-ms",
    "10000",
  ]), {
    input: "artifact.json",
    output: "report.html",
    "timeout-ms": "10000",
  });
  assert.throws(
    () => parseArguments(["--input", "artifact.json", "--output", "report.html", "--verify-twice", "true"]),
    /Unknown argument: --verify-twice/,
  );
});
