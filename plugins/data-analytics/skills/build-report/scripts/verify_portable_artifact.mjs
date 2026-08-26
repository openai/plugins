#!/usr/bin/env node

import { randomUUID } from "node:crypto";
import {
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, extname, join, resolve } from "node:path";
import { performance } from "node:perf_hooks";
import { pathToFileURL } from "node:url";
import { isDeepStrictEqual } from "node:util";
import { gunzipSync } from "node:zlib";

import {
  PortableBrowserError,
  resolveChromiumExecutable,
} from "./portable_browser_helpers.mjs";
import {
  buildPortableVerifierHarness,
  chromiumDumpArguments,
  injectPortableVerifierProbe,
  parsePortableVerifierDump,
  spawnChromiumDump,
} from "./portable_browser_cli.mjs";
import { preparePortablePayload } from "./build_portable_artifact.mjs";

const PAYLOAD_SOURCE_ID = "data-analytics-portable-artifact-payload-source";
const RUNTIME_SOURCE_ID = "data-analytics-portable-reader-runtime-source";
const READER_CONTAINER_ID = "data-analytics-portable-reader";
const READER_ROOT = "#data-analytics-portable-reader-root";
const DEFAULT_READY_TIMEOUT_MS = 5_000;
const DEFAULT_ACTION_TIMEOUT_MS = 2_500;
const DEFAULT_TIMEOUT_MS = 10_000;
const DESKTOP_VIEWPORT = Object.freeze({ name: "desktop", width: 1_440, height: 1_000 });
const MOBILE_VIEWPORT = Object.freeze({ name: "mobile", width: 390, height: 844 });

function roundMs(value) {
  return Math.round(value * 10) / 10;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function check(condition, code, message, details = {}) {
  if (!condition) throw new PortableBrowserError(code, message, details);
}

export class VerificationDeadline {
  constructor(timeoutMs = DEFAULT_TIMEOUT_MS, now = () => performance.now()) {
    check(
      Number.isFinite(timeoutMs) && timeoutMs > 0,
      "invalid_timeout",
      "Verification timeout must be a positive number.",
    );
    this.now = now;
    this.startedAt = now();
    this.timeoutMs = timeoutMs;
  }

  elapsedMs() {
    return this.now() - this.startedAt;
  }

  remainingMs(phase = "verification") {
    const remaining = this.timeoutMs - this.elapsedMs();
    if (remaining <= 0) {
      throw new PortableBrowserError(
        "verification_timeout",
        `Portable artifact verification exceeded ${this.timeoutMs}ms during ${phase}.`,
        { phase, timeoutMs: this.timeoutMs },
      );
    }
    return Math.max(1, Math.floor(remaining));
  }

  remainingMsOrZero() {
    return Math.max(0, Math.floor(this.timeoutMs - this.elapsedMs()));
  }

  async run(phase, operation) {
    const remaining = this.remainingMs(phase);
    let timer;
    try {
      return await Promise.race([
        Promise.resolve().then(() => operation(remaining)),
        new Promise((_, reject) => {
          timer = setTimeout(() => reject(new PortableBrowserError(
            "verification_timeout",
            `Portable artifact verification exceeded ${this.timeoutMs}ms during ${phase}.`,
            { phase, timeoutMs: this.timeoutMs },
          )), remaining);
        }),
      ]);
    } finally {
      clearTimeout(timer);
    }
  }
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (error) {
    throw new PortableBrowserError(
      "artifact_unreadable",
      `Could not read ${label} ${path}: ${error.message}`,
      { path },
    );
  }
}

export function extractEmbeddedArtifact(html) {
  const pattern = new RegExp(
    `<template\\s+id=["']${PAYLOAD_SOURCE_ID}["'][^>]*>([\\s\\S]*?)<\\/template>`,
    "i",
  );
  const match = pattern.exec(html);
  check(
    match,
    "payload_missing",
    `Portable HTML is missing the embedded ${PAYLOAD_SOURCE_ID} template.`,
  );
  try {
    const compressed = Buffer.from(match[1].replace(/\s/g, ""), "base64");
    return JSON.parse(gunzipSync(compressed).toString("utf8"));
  } catch (error) {
    throw new PortableBrowserError(
      "payload_invalid",
      `Portable HTML contains an unreadable embedded artifact: ${error.message}`,
    );
  }
}

export function expectedPortableCounts(artifact) {
  const manifest = artifact?.manifest ?? {};
  const cards = new Set(asArray(manifest.cards).map((item) => item?.id).filter(Boolean));
  const charts = new Set(asArray(manifest.charts).map((item) => item?.id).filter(Boolean));
  const tables = new Set(asArray(manifest.tables).map((item) => item?.id).filter(Boolean));
  const counts = { blocks: 0, charts: 0, html: 0, metrics: 0, tables: 0 };

  for (const block of asArray(manifest.blocks)) {
    if (block?.type === "metric-strip") {
      const metricCount = asArray(block.cardIds).filter((id) => cards.has(id)).length;
      counts.metrics += metricCount;
      counts.blocks += metricCount;
      continue;
    }
    counts.blocks += 1;
    if (block?.type === "chart" && charts.has(block.chartId)) counts.charts += 1;
    if (block?.type === "table" && tables.has(block.tableId)) counts.tables += 1;
    if (block?.type === "html") counts.html += 1;
  }
  return counts;
}

function structuralSignature(artifact) {
  const manifest = artifact?.manifest ?? {};
  return {
    counts: expectedPortableCounts(artifact),
    generatedAt: manifest.generatedAt ?? null,
    surface: manifest.surface ?? artifact?.surface ?? null,
    title: manifest.title ?? null,
  };
}

export function assertArtifactMatchesEmbedded(artifact, embeddedArtifact) {
  const expectedArtifact = preparePortablePayload(artifact);
  check(
    isDeepStrictEqual(expectedArtifact, embeddedArtifact),
    "artifact_mismatch",
    "The supplied artifact does not exactly match the canonical artifact embedded in the HTML.",
    {
      embedded: structuralSignature(embeddedArtifact),
      supplied: structuralSignature(expectedArtifact),
    },
  );
}

function loadPortableArtifactStructure({ artifactPath, htmlPath } = {}) {
  check(htmlPath, "html_required", "htmlPath is required.");
  const absoluteHtmlPath = resolve(htmlPath);
  let html;
  try {
    html = readFileSync(absoluteHtmlPath, "utf8");
  } catch (error) {
    throw new PortableBrowserError(
      "html_unreadable",
      `Could not read portable HTML ${absoluteHtmlPath}: ${error.message}`,
      { htmlPath: absoluteHtmlPath },
    );
  }
  const embeddedArtifact = extractEmbeddedArtifact(html);
  const artifact = artifactPath ? readJson(resolve(artifactPath), "artifact") : embeddedArtifact;
  if (artifactPath) assertArtifactMatchesEmbedded(artifact, embeddedArtifact);

  const expectedCounts = expectedPortableCounts(artifact);
  const title = artifact?.manifest?.title;
  check(title, "title_missing", "The embedded artifact has no manifest title.");
  const requiredMarkers = [
    {
      code: "runtime_missing",
      label: RUNTIME_SOURCE_ID,
      pattern: new RegExp(`<template\\s+id=["']${RUNTIME_SOURCE_ID}["']`, "i"),
    },
    {
      code: "fallback_missing",
      label: "semantic fallback",
      pattern: /\bdata-portable-fallback=["']true["']/i,
    },
    {
      code: "reader_container_missing",
      label: READER_CONTAINER_ID,
      pattern: new RegExp(`\\bid=["']${READER_CONTAINER_ID}["']`, "i"),
    },
  ];
  for (const marker of requiredMarkers) {
    check(
      marker.pattern.test(html),
      marker.code,
      `Portable HTML is missing its required ${marker.label} marker.`,
    );
  }
  return { absoluteHtmlPath, artifact, expectedCounts, html, title };
}

export function verifyPortableArtifactStructure(options = {}) {
  const { absoluteHtmlPath, expectedCounts, title } = loadPortableArtifactStructure(options);
  return {
    counts: expectedCounts,
    html: absoluteHtmlPath,
    ok: true,
    title,
  };
}

function expectedSourceInteraction(artifact) {
  const manifest = artifact?.manifest ?? {};
  const sourceBackedItems = [
    ...asArray(manifest.cards),
    ...asArray(manifest.charts),
    ...asArray(manifest.tables),
  ];
  const hasSources = asArray(artifact?.sources).length > 0 ||
    asArray(manifest.sources).length > 0 ||
    sourceBackedItems.some((item) => Boolean(item?.source));
  const referenced = sourceBackedItems.some((item) => Boolean(item?.sourceId || item?.source));
  return hasSources && referenced;
}

/**
 * Recharts observes its container asynchronously after a viewport resize. In
 * reduced-motion browser contexts it can retain the previous desktop width
 * for several frames even though the final mobile layout is contained. Wait a
 * short, bounded interval for that real responsive state before applying the
 * unchanged hard overflow assertion.
 *
 * @param {{waitForFunction: Function}} page
 * @param {number} timeoutMs
 * @returns {Promise<boolean>}
 */
export async function waitForResponsiveLayout(page, timeoutMs = 500) {
  try {
    await page.waitForFunction(
      () => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1,
      undefined,
      { polling: "raf", timeout: timeoutMs },
    );
    return true;
  } catch {
    return false;
  }
}

function failureResult(error, { htmlPath, screenshot, timings }) {
  const { startedAt, ...publicTimings } = timings;
  return {
    ok: false,
    code: error?.code ?? "verification_failed",
    error: error?.message ?? String(error),
    html: htmlPath,
    screenshot,
    timings: { ...publicTimings, totalMs: roundMs(performance.now() - startedAt) },
  };
}

/**
 * Runtime correctness check for HTML emitted by buildPortableArtifact. The
 * sandboxed probe reduces local-file and result-forgery exposure, but this is
 * not a sanitizer or security boundary for arbitrary attacker-authored HTML.
 */
export async function verifyPortableArtifact({
  actionTimeoutMs = DEFAULT_ACTION_TIMEOUT_MS,
  artifactPath,
  browserExecutable,
  htmlPath,
  readyTimeoutMs = DEFAULT_READY_TIMEOUT_MS,
  screenshotPath,
  timeoutMs = DEFAULT_TIMEOUT_MS,
} = {}) {
  const deadline = new VerificationDeadline(timeoutMs);
  const timings = { startedAt: deadline.startedAt };
  const {
    absoluteHtmlPath,
    artifact,
    expectedCounts,
    html,
    title,
  } = loadPortableArtifactStructure({ artifactPath, htmlPath });
  const failureScreenshot = resolve(
    screenshotPath ??
      `${absoluteHtmlPath.slice(0, -extname(absoluteHtmlPath).length)}.verification-failure.png`,
  );
  const shouldCheckSource = expectedSourceInteraction(artifact);
  const harnessViewport = Object.freeze({
    height: Math.max(DESKTOP_VIEWPORT.height, MOBILE_VIEWPORT.height),
    width: DESKTOP_VIEWPORT.width + MOBILE_VIEWPORT.width + 16,
  });
  let executablePath;
  let harnessUrl;
  let temporaryDirectory;
  let virtualTimeBudgetMs;
  let actualCounts;

  try {
    deadline.remainingMs("browser resolution");
    executablePath = browserExecutable ?? resolveChromiumExecutable();
    temporaryDirectory = mkdtempSync(join(tmpdir(), "data-analytics-portable-verifier-"));
    const channel = randomUUID();
    const frames = [];
    for (const viewport of [DESKTOP_VIEWPORT, MOBILE_VIEWPORT]) {
      const instrumentedHtml = injectPortableVerifierProbe(html, {
        actionTimeoutMs,
        channel,
        checkSource: shouldCheckSource && viewport.name === DESKTOP_VIEWPORT.name,
        expectedCounts,
        readerRoot: READER_ROOT,
        readyTimeoutMs,
        title,
        viewport,
      });
      frames.push({ html: instrumentedHtml, viewport });
    }
    const probeTimeoutMs = readyTimeoutMs + (shouldCheckSource ? actionTimeoutMs : 0) + 1_000;
    virtualTimeBudgetMs = probeTimeoutMs + 250;
    const harnessPath = join(temporaryDirectory, "harness.html");
    writeFileSync(harnessPath, buildPortableVerifierHarness({
      channel,
      frames,
      timeoutMs: probeTimeoutMs,
    }), "utf8");
    harnessUrl = pathToFileURL(harnessPath).href;

    const browserStartedAt = performance.now();
    const browserResult = await spawnChromiumDump({
      arguments: chromiumDumpArguments({
        ...harnessViewport,
        profilePath: join(temporaryDirectory, "profile"),
        url: harnessUrl,
        virtualTimeBudgetMs,
      }),
      executablePath,
      timeoutMs: deadline.remainingMs("browser verification"),
    });
    timings.browserRunMs = roundMs(performance.now() - browserStartedAt);

    let aggregate;
    try {
      aggregate = parsePortableVerifierDump(browserResult.stdout);
    } catch (error) {
      if (error?.code === "probe_missing") {
        throw new PortableBrowserError(
          "probe_missing",
          "Chromium produced no verifier result. Use the discovered chrome-headless-shell executable; " +
            "full Chrome does not reliably support this dependency-free dump-DOM verifier.",
          {
            diagnostics: browserResult.stderr.slice(-4_000).trim(),
            executablePath,
          },
        );
      }
      throw error;
    }
    check(
      aggregate?.ok,
      aggregate?.code ?? "probe_failed",
      aggregate?.error ?? "Portable verifier probe did not complete.",
      {
        diagnostics: browserResult.stderr.slice(-4_000).trim(),
        missing: aggregate?.missing,
        results: aggregate?.results,
      },
    );
    const viewportResults = asArray(aggregate.results);
    check(
      viewportResults.length === 2,
      "probe_invalid",
      "Portable verifier did not return both viewport results.",
      { results: viewportResults },
    );
    const failed = viewportResults.find((result) => !result?.ok);
    if (failed) {
      throw new PortableBrowserError(
        failed.code ?? "verification_failed",
        `${failed.error ?? "Portable verification failed."} (${failed.viewport?.name ?? "unknown"} viewport)`,
        { ...failed.details, viewport: failed.viewport },
      );
    }

    const desktopResult = viewportResults.find(
      (result) => result.viewport?.name === DESKTOP_VIEWPORT.name,
    );
    const mobileResult = viewportResults.find(
      (result) => result.viewport?.name === MOBILE_VIEWPORT.name,
    );
    check(desktopResult && mobileResult, "probe_invalid", "Viewport probe names are invalid.");
    actualCounts = desktopResult.counts;
    const timingValues = (key) => viewportResults
      .map((result) => Number(result.timings?.[key]))
      .filter(Number.isFinite);
    const maxTiming = (key) => {
      const values = timingValues(key);
      return values.length ? Math.max(...values) : undefined;
    };
    timings.readerReadyMs = maxTiming("readerReadyMs");
    timings.contentChecksMs = maxTiming("contentChecksMs");
    timings.sourceDialogMs = desktopResult.timings?.sourceDialogMs;
    timings.responsiveChecksMs = mobileResult.timings?.contentChecksMs;
    deadline.remainingMs("result assembly");

    const { startedAt, ...publicTimings } = timings;
    return {
      ok: true,
      counts: actualCounts,
      html: absoluteHtmlPath,
      sourceDialog: shouldCheckSource ? "passed" : "not_applicable",
      sourceInteraction: shouldCheckSource
        ? desktopResult.sourceInteraction
        : "not_applicable",
      timings: {
        ...publicTimings,
        totalMs: roundMs(performance.now() - startedAt),
      },
      viewports: [DESKTOP_VIEWPORT.width, MOBILE_VIEWPORT.width],
    };
  } catch (error) {
    let screenshot = null;
    if (
      !["browser_timeout", "verification_timeout"].includes(error?.code) &&
      executablePath &&
      harnessUrl &&
      deadline.remainingMsOrZero() > 250
    ) {
      try {
        mkdirSync(dirname(failureScreenshot), { recursive: true });
        const remaining = deadline.remainingMs("failure screenshot");
        await spawnChromiumDump({
          arguments: chromiumDumpArguments({
            height: DESKTOP_VIEWPORT.height,
            profilePath: join(temporaryDirectory, "screenshot-profile"),
            screenshotPath: failureScreenshot,
            url: pathToFileURL(absoluteHtmlPath).href,
            virtualTimeBudgetMs: Math.min(virtualTimeBudgetMs ?? 1_000, remaining),
            width: DESKTOP_VIEWPORT.width,
          }),
          executablePath,
          timeoutMs: remaining,
        });
        screenshot = failureScreenshot;
      } catch {
        // The original verification failure remains authoritative.
      }
    }
    const result = failureResult(error, {
      htmlPath: absoluteHtmlPath,
      screenshot,
      timings,
    });
    error.verificationResult = result;
    throw error;
  } finally {
    if (temporaryDirectory) {
      try {
        rmSync(temporaryDirectory, {
          force: true,
          maxRetries: process.platform === "win32" ? 3 : 0,
          recursive: true,
          retryDelay: 100,
        });
      } catch {
        // Browser and verification failures remain authoritative if an OS
        // briefly retains a lock on the disposable Chromium profile.
      }
    }
  }
}

function usage() {
  return [
    "Usage: node verify_portable_artifact.mjs --html <report.html> [options]",
    "",
    "Options:",
    "  --artifact <artifact.json>       Compare the source artifact's structure with the embedded artifact.",
    "  --ready-timeout-ms <milliseconds>  Reader startup budget (default: 5000).",
    "  --action-timeout-ms <milliseconds> Interaction budget (default: 2500).",
    "  --timeout-ms <milliseconds>        Whole verification budget (default: 10000).",
    "  --screenshot <failure.png>       Failure-only screenshot path.",
  ].join("\n");
}

export function parseArguments(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--help" || argument === "-h") return { help: true };
    if (!argument.startsWith("--")) throw new Error(`Unexpected argument: ${argument}\n${usage()}`);
    const key = argument.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${argument}.\n${usage()}`);
    if (options[key] !== undefined) throw new Error(`${argument} may only be specified once.`);
    options[key] = value;
    index += 1;
  }
  if (!options.html) throw new Error(`--html is required.\n${usage()}`);
  return options;
}

function positiveNumber(value, label) {
  if (value === undefined) return undefined;
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) throw new Error(`${label} must be a positive number.`);
  return parsed;
}

export async function runCli(argv = process.argv.slice(2)) {
  let parsed;
  try {
    parsed = parseArguments(argv);
    if (parsed.help) {
      process.stdout.write(`${usage()}\n`);
      return;
    }
    const result = await verifyPortableArtifact({
      actionTimeoutMs: positiveNumber(parsed["action-timeout-ms"], "--action-timeout-ms"),
      artifactPath: parsed.artifact,
      htmlPath: parsed.html,
      readyTimeoutMs: positiveNumber(parsed["ready-timeout-ms"], "--ready-timeout-ms"),
      screenshotPath: parsed.screenshot,
      timeoutMs: positiveNumber(parsed["timeout-ms"], "--timeout-ms"),
    });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const result = error?.verificationResult ?? {
      ok: false,
      code: error?.code ?? "invalid_invocation",
      error: error?.message ?? String(error),
    };
    process.stderr.write(`${JSON.stringify(result)}\n`);
    process.exitCode = 1;
  }
}

const isMain = process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url;
if (isMain) await runCli();
