#!/usr/bin/env node

import { randomUUID } from "node:crypto";
import {
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, resolve } from "node:path";
import { performance } from "node:perf_hooks";
import { pathToFileURL } from "node:url";

import { buildPortableArtifact } from "./build_portable_artifact.mjs";
import { extractPortableChartSvgs } from "./extract_portable_chart_svgs.mjs";
import {
  verifyPortableArtifact,
  verifyPortableArtifactStructure,
} from "./verify_portable_artifact.mjs";

const BROWSER_CAPABILITY_CODES = new Set([
  "browser_launch_failed",
  "browser_unavailable",
]);

function roundMs(value) {
  return Math.round(value * 10) / 10;
}

function usage() {
  return [
    "Usage: node deliver_portable_artifact.mjs --input <artifact.json> --output <report.html> [options]",
    "",
    "Options:",
    "  --ready-timeout-ms <milliseconds>  Reader startup budget (default: 5000).",
    "  --action-timeout-ms <milliseconds> Interaction budget (default: 2500).",
    "  --timeout-ms <milliseconds>        Whole verification budget (default: 10000).",
    "  --screenshot <failure.png>         Failure-only screenshot path.",
  ].join("\n");
}

const VALUE_OPTIONS = new Set([
  "input",
  "output",
  "ready-timeout-ms",
  "action-timeout-ms",
  "timeout-ms",
  "screenshot",
]);

export function parseArguments(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--help" || argument === "-h") return { help: true };
    if (!argument.startsWith("--")) throw new Error(`Unexpected argument: ${argument}\n${usage()}`);
    const key = argument.slice(2);
    if (!VALUE_OPTIONS.has(key)) throw new Error(`Unknown argument: ${argument}\n${usage()}`);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${argument}.\n${usage()}`);
    if (options[key] !== undefined) throw new Error(`${argument} may only be specified once.`);
    options[key] = value;
    index += 1;
  }
  if (!options.input || !options.output) throw new Error(`--input and --output are required.\n${usage()}`);
  return options;
}

function positiveNumber(value, label) {
  if (value === undefined) return undefined;
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) throw new Error(`${label} must be a positive number.`);
  return parsed;
}

function compactVerificationTimings(timings = {}) {
  const { totalMs: verificationMs, ...phases } = timings;
  return {
    ...phases,
    ...(verificationMs !== undefined ? { verificationMs } : {}),
  };
}

function compactMessage(value) {
  const firstLine = String(value ?? "Delivery failed.").split(/\r?\n/, 1)[0].trim();
  return firstLine.length > 400 ? `${firstLine.slice(0, 397)}...` : firstLine;
}

function browserCapabilityWarning(error) {
  const code = BROWSER_CAPABILITY_CODES.has(error?.code)
    ? error.code
    : error?.verificationResult?.code;
  if (!BROWSER_CAPABILITY_CODES.has(code)) return null;
  return {
    code,
    message: compactMessage(error?.message ?? error?.verificationResult?.error),
  };
}

function compactFailure(error, { stage, startedAt }) {
  const verification = error?.verificationResult;
  const validationIssues = Array.isArray(error?.issues) ? error.issues : null;
  return {
    ok: false,
    stage: validationIssues ? "validation" : stage,
    code: verification?.code ?? error?.code ?? "delivery_failed",
    error: compactMessage(verification?.error ?? error?.message ?? error),
    ...(validationIssues ? { issues: validationIssues } : {}),
    ...(verification?.screenshot ? { screenshot: verification.screenshot } : {}),
    timings: {
      ...compactVerificationTimings(verification?.timings),
      totalMs: roundMs(performance.now() - startedAt),
    },
  };
}

export async function deliverPortableArtifact({
  actionTimeoutMs,
  inputPath,
  outputPath,
  readyTimeoutMs,
  screenshotPath,
  timeoutMs,
} = {}, {
  build = buildPortableArtifact,
  extract = extractPortableChartSvgs,
  verify = verifyPortableArtifact,
  verifyStructure = verifyPortableArtifactStructure,
} = {}) {
  const startedAt = performance.now();
  let stage = "input";
  let absoluteOutputPath = outputPath ? resolve(outputPath) : null;
  let candidateOutputPath = null;

  try {
    if (!inputPath || !outputPath) throw new Error("inputPath and outputPath are required.");
    const absoluteInputPath = resolve(inputPath);
    absoluteOutputPath = resolve(outputPath);

    let input;
    try {
      input = JSON.parse(readFileSync(absoluteInputPath, "utf8"));
    } catch (error) {
      const unreadable = new Error(`Could not read artifact input ${absoluteInputPath}: ${error.message}`);
      unreadable.code = "artifact_unreadable";
      throw unreadable;
    }

    stage = "package";
    const packageStartedAt = performance.now();
    let html = build(input);
    mkdirSync(dirname(absoluteOutputPath), { recursive: true });
    candidateOutputPath = `${absoluteOutputPath}.tmp-${process.pid}-${randomUUID()}.html`;
    writeFileSync(candidateOutputPath, html, "utf8");
    let staticChartExtractionMs = 0;
    let browserWarning = null;
    if (html.includes('<figure class="portable-content-card portable-chart-summary"')) {
      stage = "static_charts";
      const extractionStartedAt = performance.now();
      try {
        const staticCharts = await extract({
          actionTimeoutMs,
          htmlPath: candidateOutputPath,
          readyTimeoutMs,
        });
        html = build(input, { staticCharts });
        writeFileSync(candidateOutputPath, html, "utf8");
      } catch (error) {
        browserWarning = browserCapabilityWarning(error);
        if (!browserWarning) throw error;
      } finally {
        staticChartExtractionMs = roundMs(performance.now() - extractionStartedAt);
      }
    }
    const packageMs = roundMs(performance.now() - packageStartedAt);

    stage = "verification";
    let verification;
    let verificationStage = "passed";
    if (browserWarning) {
      const structuralStartedAt = performance.now();
      verification = verifyStructure({
        artifactPath: absoluteInputPath,
        htmlPath: candidateOutputPath,
      });
      verification = {
        ...verification,
        sourceDialog: "not_verified",
        sourceInteraction: "not_verified",
        timings: {
          structuralVerificationMs: roundMs(performance.now() - structuralStartedAt),
        },
        viewports: [],
      };
      verificationStage = "structural_only";
    } else {
      try {
        verification = await verify({
          actionTimeoutMs,
          artifactPath: absoluteInputPath,
          htmlPath: candidateOutputPath,
          readyTimeoutMs,
          screenshotPath,
          timeoutMs,
        });
      } catch (error) {
        browserWarning = browserCapabilityWarning(error);
        if (!browserWarning) throw error;
        const structuralStartedAt = performance.now();
        verification = verifyStructure({
          artifactPath: absoluteInputPath,
          htmlPath: candidateOutputPath,
        });
        verification = {
          ...verification,
          sourceDialog: "not_verified",
          sourceInteraction: "not_verified",
          timings: {
            structuralVerificationMs: roundMs(performance.now() - structuralStartedAt),
          },
          viewports: [],
        };
        verificationStage = "structural_only";
      }
    }

    stage = "publish";
    renameSync(candidateOutputPath, absoluteOutputPath);
    candidateOutputPath = null;
    const totalMs = roundMs(performance.now() - startedAt);

    return {
      ok: true,
      html: absoluteOutputPath,
      stages: {
        validation: "passed",
        package: "passed",
        verification: verificationStage,
      },
      ...(browserWarning ? { browserWarning } : {}),
      counts: verification.counts,
      sourceDialog: verification.sourceDialog,
      ...(verification.sourceInteraction
        ? { sourceInteraction: verification.sourceInteraction }
        : {}),
      viewports: verification.viewports,
      timings: {
        validateAndPackageMs: packageMs,
        staticChartExtractionMs,
        ...compactVerificationTimings(verification.timings),
        totalMs,
      },
    };
  } catch (error) {
    if (candidateOutputPath) {
      try {
        rmSync(candidateOutputPath, { force: true });
      } catch {
        // Preserve the original delivery error if temporary-file cleanup fails.
      }
    }
    const result = compactFailure(error, {
      stage,
      startedAt,
    });
    try {
      error.deliveryResult = result;
    } catch {
      // The compact result below remains available through the wrapper error.
    }
    if (error?.deliveryResult === result) throw error;
    const wrapped = new Error(result.error, { cause: error });
    wrapped.deliveryResult = result;
    throw wrapped;
  }
}

export async function runCli(argv = process.argv.slice(2)) {
  try {
    const parsed = parseArguments(argv);
    if (parsed.help) {
      process.stdout.write(`${usage()}\n`);
      return;
    }
    const result = await deliverPortableArtifact({
      actionTimeoutMs: positiveNumber(parsed["action-timeout-ms"], "--action-timeout-ms"),
      inputPath: parsed.input,
      outputPath: parsed.output,
      readyTimeoutMs: positiveNumber(parsed["ready-timeout-ms"], "--ready-timeout-ms"),
      screenshotPath: parsed.screenshot,
      timeoutMs: positiveNumber(parsed["timeout-ms"], "--timeout-ms"),
    });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    const result = error?.deliveryResult ?? {
      ok: false,
      stage: "invocation",
      code: error?.code ?? "invalid_invocation",
      error: error?.message ?? String(error),
    };
    process.stderr.write(`${JSON.stringify(result)}\n`);
    process.exitCode = 1;
  }
}

const isMain = process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url;
if (isMain) await runCli();
