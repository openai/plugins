import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  realpathSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { resolveChromiumExecutable } from "../skills/build-report/scripts/portable_browser_helpers.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(here, "..");
const repositoryRoot = resolve(pluginRoot, "../..");
const pluginPathFromRepository = relative(repositoryRoot, pluginRoot);

function trackedPluginFiles() {
  const result = spawnSync(
    "git",
    ["-C", repositoryRoot, "ls-files", "-z", "--", pluginPathFromRepository],
    { encoding: "buffer" },
  );
  assert.equal(
    result.status,
    0,
    `Could not enumerate tracked plugin files:\n${result.stderr.toString("utf8")}`,
  );
  return result.stdout
    .toString("utf8")
    .split("\0")
    .filter(Boolean);
}

function materializeReleaseCopy(destination) {
  const files = trackedPluginFiles();
  assert.ok(files.length > 0, "The release-shaped copy must contain tracked plugin files.");
  for (const repositoryPath of files) {
    const relativePluginPath = relative(pluginPathFromRepository, repositoryPath);
    const source = resolve(repositoryRoot, repositoryPath);
    const target = resolve(destination, relativePluginPath);
    mkdirSync(dirname(target), { recursive: true });
    copyFileSync(source, target);
  }
  return files.length;
}

function releaseFixture() {
  return {
    surface: "report",
    manifest: {
      version: 1,
      surface: "report",
      title: "Release-shaped portable report",
      generatedAt: "2026-07-09T12:00:00Z",
      charts: [{
        id: "revenue_trend",
        title: "Revenue trend",
        type: "line",
        dataset: "trend",
        sourceId: "release_query",
        encodings: {
          x: { field: "month", type: "ordinal", label: "Month" },
          y: { field: "revenue", type: "quantitative", label: "Revenue", format: "currency" },
        },
        valueFormat: "currency",
      }],
      sources: [{
        id: "release_query",
        label: "Release verification query",
        path: "queries/release-verification.sql",
      }],
      blocks: [{ id: "trend", type: "chart", chartId: "revenue_trend" }],
    },
    snapshot: {
      version: 1,
      generatedAt: "2026-07-09T12:00:00Z",
      status: "ready",
      datasets: {
        trend: [
          { month: "May", revenue: 1_200_000 },
          { month: "June", revenue: 1_450_000 },
          { month: "July", revenue: 1_720_000 },
        ],
      },
    },
  };
}

function parseReceipt(stdout) {
  const lines = stdout.trim().split(/\r?\n/u).filter(Boolean);
  assert.ok(lines.length, "Portable delivery did not emit a receipt.");
  return JSON.parse(lines.at(-1));
}

function assertNoAncestorNodeModules(path) {
  let current = resolve(path);
  while (true) {
    assert.equal(
      existsSync(join(current, "node_modules")),
      false,
      `Release smoke could resolve undeclared packages from ${join(current, "node_modules")}.`,
    );
    const parent = dirname(current);
    if (parent === current) return;
    current = parent;
  }
}

const workspace = realpathSync(mkdtempSync(join(tmpdir(), "portable-release-package-")));
const releaseRoot = join(workspace, "data-analytics");
const inputPath = join(workspace, "artifact.json");
const outputPath = join(workspace, "report.html");

try {
  const chromiumExecutable = resolveChromiumExecutable();
  assert.equal(
    existsSync(chromiumExecutable),
    true,
    `The release smoke requires an existing Chromium executable: ${chromiumExecutable}`,
  );
  const trackedFileCount = materializeReleaseCopy(releaseRoot);
  assert.equal(
    existsSync(join(releaseRoot, "skills/build-report/scripts/deliver_portable_artifact.mjs")),
    true,
    "The release-shaped copy must contain the delivery entrypoint.",
  );
  assert.equal(
    existsSync(join(releaseRoot, "assets/portable-artifact-reader.html")),
    true,
    "The release-shaped copy must contain the built portable reader.",
  );
  assert.equal(
    existsSync(join(releaseRoot, "node_modules")),
    false,
    "The release-shaped plugin copy must not contain node_modules.",
  );
  assertNoAncestorNodeModules(releaseRoot);

  writeFileSync(inputPath, JSON.stringify(releaseFixture()), "utf8");
  const deliveryScript = join(
    releaseRoot,
    "skills/build-report/scripts/deliver_portable_artifact.mjs",
  );
  const result = spawnSync(
    process.execPath,
    [
      deliveryScript,
      "--input",
      inputPath,
      "--output",
      outputPath,
      "--ready-timeout-ms",
      "5000",
      "--action-timeout-ms",
      "5000",
      "--timeout-ms",
      "30000",
    ],
    {
      cwd: releaseRoot,
      encoding: "utf8",
      env: {
        ...process.env,
        CHROMIUM_EXECUTABLE_PATH: chromiumExecutable,
        NODE_OPTIONS: "",
        NODE_PATH: "",
        PLAYWRIGHT_EXECUTABLE_PATH: "",
      },
      maxBuffer: 10 * 1024 * 1024,
      timeout: 90_000,
    },
  );

  assert.equal(
    result.status,
    0,
    [
      `Portable delivery failed from a release-shaped plugin copy (status ${result.status}).`,
      result.error?.message,
      result.stdout,
      result.stderr,
    ].filter(Boolean).join("\n"),
  );
  assert.equal(result.signal, null, `Portable delivery was terminated by ${result.signal}.`);

  const receipt = parseReceipt(result.stdout);
  assert.equal(receipt.ok, true);
  assert.deepEqual(receipt.stages, {
    validation: "passed",
    package: "passed",
    verification: "passed",
  });
  assert.equal(receipt.counts.charts, 1);
  assert.deepEqual(receipt.viewports, [1_440, 390]);

  const html = readFileSync(outputPath, "utf8");
  assert.match(html, /data-analytics-portable-artifact-payload-source/u);
  assert.match(html, /data-analytics-portable-reader-runtime-source/u);
  const staticChartVariants = (variant) => html.match(new RegExp(
    `<div class="portable-static-chart-variant portable-static-chart-${variant}"[^>]*>` +
      `\\s*<svg[^>]*class="portable-static-chart-svg"`,
    "gu",
  )) ?? [];
  assert.equal(
    staticChartVariants("light").length,
    1,
    "Static chart extraction must embed one light SVG in the light variant wrapper.",
  );
  assert.equal(
    staticChartVariants("dark").length,
    1,
    "Static chart extraction must embed one dark SVG in the dark variant wrapper.",
  );

  const structuralOutputPath = join(workspace, "report-structural-only.html");
  const emptyHome = join(workspace, "empty-home");
  const emptyBrowserCache = join(workspace, "empty-browser-cache");
  mkdirSync(emptyHome, { recursive: true });
  mkdirSync(emptyBrowserCache, { recursive: true });
  const structuralResult = spawnSync(
    process.execPath,
    [
      deliveryScript,
      "--input",
      inputPath,
      "--output",
      structuralOutputPath,
      "--timeout-ms",
      "30000",
    ],
    {
      cwd: releaseRoot,
      encoding: "utf8",
      env: {
        ...process.env,
        CHROMIUM_EXECUTABLE_PATH: "",
        HOME: emptyHome,
        LOCALAPPDATA: emptyHome,
        NODE_OPTIONS: "",
        NODE_PATH: "",
        PLAYWRIGHT_BROWSERS_PATH: emptyBrowserCache,
        PLAYWRIGHT_EXECUTABLE_PATH: "",
        USERPROFILE: emptyHome,
      },
      maxBuffer: 10 * 1024 * 1024,
      timeout: 90_000,
    },
  );
  assert.equal(
    structuralResult.status,
    0,
    [
      "Portable delivery should retain its semantic artifact when Chromium is unavailable.",
      structuralResult.error?.message,
      structuralResult.stdout,
      structuralResult.stderr,
    ].filter(Boolean).join("\n"),
  );
  const structuralReceipt = parseReceipt(structuralResult.stdout);
  assert.equal(structuralReceipt.ok, true);
  assert.deepEqual(structuralReceipt.stages, {
    validation: "passed",
    package: "passed",
    verification: "structural_only",
  });
  assert.equal(structuralReceipt.browserWarning.code, "browser_unavailable");
  assert.equal(structuralReceipt.sourceDialog, "not_verified");
  assert.deepEqual(structuralReceipt.viewports, []);

  const structuralHtml = readFileSync(structuralOutputPath, "utf8");
  assert.match(structuralHtml, /data-portable-fallback="true"/u);
  assert.match(structuralHtml, /<table\b/u);
  assert.match(structuralHtml, /Release verification query/u);
  assert.match(structuralHtml, /data-analytics-portable-artifact-payload-source/u);
  assert.match(structuralHtml, /data-analytics-portable-reader-runtime-source/u);
  assert.doesNotMatch(
    structuralHtml,
    /<div class="portable-static-chart-variant/u,
    "Structural-only delivery must retain the semantic chart table without static SVG variant markup.",
  );

  process.stdout.write(
    `Portable release package passed (${trackedFileCount} tracked files, ${Buffer.byteLength(html)} HTML bytes).\n`,
  );
} finally {
  rmSync(workspace, { force: true, recursive: true });
}
