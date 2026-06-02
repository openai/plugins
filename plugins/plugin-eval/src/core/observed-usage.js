import path from "node:path";

import { pathExists, readText, relativePath } from "../lib/files.js";
import { createArtifact, createCheck, createMetric } from "./schema.js";

function round(value) {
  return Math.round(value * 100) / 100;
}

function toNumber(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function buildStat(values) {
  if (values.length === 0) {
    return {
      total: 0,
      average: 0,
      min: 0,
      max: 0,
    };
  }

  const total = values.reduce((sum, value) => sum + value, 0);
  return {
    total,
    average: round(total / values.length),
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

function classifyEstimateAlignment(deltaRatio) {
  if (deltaRatio <= 0.2) {
    return "close";
  }
  if (deltaRatio <= 0.5) {
    return "drift";
  }
  return "wide-drift";
}

function extractUsagePayload(candidate) {
  if (!candidate || typeof candidate !== "object") {
    return null;
  }

  if (candidate.type === "response.done" && candidate.response?.usage) {
    return {
      usage: candidate.response.usage,
      responseId: candidate.response.id || candidate.id || null,
      label: candidate.metadata?.scenario || candidate.response?.metadata?.scenario || null,
    };
  }

  if (candidate.response?.usage) {
    return {
      usage: candidate.response.usage,
      responseId: candidate.response.id || candidate.id || null,
      label: candidate.metadata?.scenario || candidate.response?.metadata?.scenario || null,
    };
  }

  if (candidate.usage) {
    return {
      usage: candidate.usage,
      responseId: candidate.response_id || candidate.id || null,
      label: candidate.metadata?.scenario || candidate.scenario || null,
    };
  }

  if (
    typeof candidate.input_tokens === "number" ||
    typeof candidate.output_tokens === "number" ||
    typeof candidate.total_tokens === "number"
  ) {
    return {
      usage: candidate,
      responseId: candidate.response_id || candidate.id || null,
      label: candidate.metadata?.scenario || candidate.scenario || null,
    };
  }

  return null;
}

function normalizeSnapshot(candidate, sourcePath, index) {
  const extracted = extractUsagePayload(candidate);
  if (!extracted) {
    return null;
  }

  const usage = extracted.usage || {};
  const inputTokens = toNumber(usage.input_tokens);
  const outputTokens = toNumber(usage.output_tokens);
  const totalTokens = toNumber(usage.total_tokens) ?? ((inputTokens || 0) + (outputTokens || 0));
  const cachedTokens =
    toNumber(usage.input_token_details?.cached_tokens) ??
    toNumber(usage.cached_tokens) ??
    0;
  const reasoningTokens =
    toNumber(usage.output_tokens_details?.reasoning_tokens) ??
    toNumber(usage.reasoning_tokens) ??
    0;

  if (inputTokens === null && outputTokens === null && totalTokens === null) {
    return null;
  }

  return {
    id: extracted.responseId || `${path.basename(sourcePath)}#${index + 1}`,
    label: extracted.label || null,
    sourcePath,
    inputTokens: inputTokens ?? 0,
    outputTokens: outputTokens ?? 0,
    totalTokens,
    cachedTokens,
    reasoningTokens,
  };
}

function collectSnapshots(value, sourcePath, results) {
  if (Array.isArray(value)) {
    value.forEach((item) => collectSnapshots(item, sourcePath, results));
    return;
  }

  if (!value || typeof value !== "object") {
    return;
  }

  const snapshot = normalizeSnapshot(value, sourcePath, results.length);
  if (snapshot) {
    results.push(snapshot);
    return;
  }

  Object.values(value).forEach((nested) => {
    if (nested && typeof nested === "object") {
      collectSnapshots(nested, sourcePath, results);
    }
  });
}

function parseUsageContent(content) {
  const trimmed = content.trim();
  if (!trimmed) {
    return [];
  }

  if (trimmed.startsWith("[")) {
    return [JSON.parse(trimmed)];
  }

  if (trimmed.startsWith("{")) {
    try {
      return [JSON.parse(trimmed)];
    } catch {
      // Fall through to JSONL parsing when the file contains multiple JSON objects.
    }
  }

  return trimmed
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

async function loadSnapshotsFromFile(filePath) {
  const resolvedPath = path.resolve(filePath);
  if (!(await pathExists(resolvedPath))) {
    throw new Error(`Observed usage file not found: ${resolvedPath}`);
  }

  const parsedItems = parseUsageContent(await readText(resolvedPath));
  const snapshots = [];
  parsedItems.forEach((item) => collectSnapshots(item, resolvedPath, snapshots));
  return snapshots;
}

function createObservedUsageChecks(summary) {
  const checks = [];

  if (summary.sampleCount < 3) {
    checks.push(
      createCheck({
        id: "observed-usage-small-sample",
        category: "measurement",
        severity: "warning",
        status: "warn",
        message: "Observed usage coverage is too small to trust as a stable benchmark yet.",
        evidence: [`Samples collected: ${summary.sampleCount}`],
        remediation: ["Capture at least 5 to 10 representative sessions before treating observed usage as a baseline."],
      }),
    );
  }

  const comparison = summary.estimateComparison;
  if (comparison) {
    if (comparison.band === "drift" || comparison.band === "wide-drift") {
      checks.push(
        createCheck({
          id: "observed-usage-estimate-drift",
          category: "budget",
          severity: comparison.band === "wide-drift" ? "error" : "warning",
          status: comparison.band === "wide-drift" ? "fail" : "warn",
          message: "Static budget estimates differ meaningfully from observed input token usage.",
          evidence: [
            `Estimated active tokens: ${comparison.estimatedActiveTokens}`,
            `Observed average input tokens: ${comparison.observedAverageInputTokens}`,
            `Delta ratio: ${round(comparison.deltaRatio * 100)}%`,
          ],
          remediation: [
            "Trim repeated instructions or supporting text if the observed value is higher than expected.",
            "If the static estimate is intentionally conservative, record that assumption in the skill or plugin references.",
          ],
        }),
      );
    }

    if (summary.cachedTokens.average > 0) {
      checks.push(
        createCheck({
          id: "observed-usage-cache-present",
          category: "measurement",
          severity: "info",
          status: "info",
          message: "Observed runs include cached tokens, so repeated sessions are cheaper than the cold-start estimate.",
          evidence: [`Average cached tokens: ${summary.cachedTokens.average}`],
          remediation: ["Track cold-start and warm-cache sessions separately if you need tighter budgeting."],
        }),
      );
    }
  }

  return checks;
}

export async function analyzeObservedUsage(usagePaths = [], rawBudget, target) {
  if (!Array.isArray(usagePaths) || usagePaths.length === 0) {
    return null;
  }

  const snapshots = [];
  for (const usagePath of usagePaths) {
    const loaded = await loadSnapshotsFromFile(usagePath);
    snapshots.push(...loaded);
  }

  if (snapshots.length === 0) {
    throw new Error("Observed usage files were provided, but no usage payloads could be parsed.");
  }

  const inputTokens = buildStat(snapshots.map((snapshot) => snapshot.inputTokens));
  const outputTokens = buildStat(snapshots.map((snapshot) => snapshot.outputTokens));
  const totalTokens = buildStat(snapshots.map((snapshot) => snapshot.totalTokens));
  const cachedTokens = buildStat(snapshots.map((snapshot) => snapshot.cachedTokens));
  const reasoningTokens = buildStat(snapshots.map((snapshot) => snapshot.reasoningTokens));
  const estimatedActiveTokens = rawBudget.trigger_cost_tokens.value + rawBudget.invoke_cost_tokens.value;
  const observedAverageInputTokens = inputTokens.average;
  const deltaTokens = round(observedAverageInputTokens - estimatedActiveTokens);
  const deltaRatio =
    estimatedActiveTokens > 0 ? round(Math.abs(deltaTokens) / estimatedActiveTokens) : 0;

  const observedUsage = {
    method: "observed-usage-files",
    target: {
      name: target.name,
      kind: target.kind,
      path: target.path,
      relativePath: relativePath(process.cwd(), target.path),
    },
    sampleCount: snapshots.length,
    files: [...new Set(snapshots.map((snapshot) => relativePath(process.cwd(), snapshot.sourcePath)))],
    inputTokens,
    outputTokens,
    totalTokens,
    cachedTokens,
    reasoningTokens,
    estimateComparison: estimatedActiveTokens
      ? {
          estimatedActiveTokens,
          observedAverageInputTokens,
          deltaTokens,
          deltaRatio,
          band: classifyEstimateAlignment(deltaRatio),
        }
      : null,
    samples: snapshots.map((snapshot) => ({
      ...snapshot,
      sourcePath: relativePath(process.cwd(), snapshot.sourcePath),
    })),
  };

  const metrics = [
    createMetric({
      id: "observed_usage_sample_count",
      category: "measurement",
      value: observedUsage.sampleCount,
      unit: "samples",
      band: observedUsage.sampleCount >= 5 ? "good" : observedUsage.sampleCount >= 3 ? "moderate" : "heavy",
    }),
    createMetric({
      id: "observed_input_tokens_avg",
      category: "measurement",
      value: observedUsage.inputTokens.average,
      unit: "tokens",
      band: "info",
    }),
    createMetric({
      id: "observed_output_tokens_avg",
      category: "measurement",
      value: observedUsage.outputTokens.average,
      unit: "tokens",
      band: "info",
    }),
    createMetric({
      id: "observed_total_tokens_avg",
      category: "measurement",
      value: observedUsage.totalTokens.average,
      unit: "tokens",
      band: "info",
    }),
  ];

  if (observedUsage.cachedTokens.total > 0) {
    metrics.push(
      createMetric({
        id: "observed_cached_tokens_avg",
        category: "measurement",
        value: observedUsage.cachedTokens.average,
        unit: "tokens",
        band: "info",
      }),
    );
  }

  if (observedUsage.reasoningTokens.total > 0) {
    metrics.push(
      createMetric({
        id: "observed_reasoning_tokens_avg",
        category: "measurement",
        value: observedUsage.reasoningTokens.average,
        unit: "tokens",
        band: "info",
      }),
    );
  }

  if (observedUsage.estimateComparison) {
    metrics.push(
      createMetric({
        id: "estimate_vs_observed_input_delta",
        category: "measurement",
        value: observedUsage.estimateComparison.deltaTokens,
        unit: "tokens",
        band:
          observedUsage.estimateComparison.band === "close"
            ? "good"
            : observedUsage.estimateComparison.band === "drift"
              ? "moderate"
              : "heavy",
      }),
      createMetric({
        id: "estimate_vs_observed_input_ratio",
        category: "measurement",
        value: observedUsage.estimateComparison.deltaRatio,
        unit: "ratio",
        band:
          observedUsage.estimateComparison.band === "close"
            ? "good"
            : observedUsage.estimateComparison.band === "drift"
              ? "moderate"
              : "heavy",
      }),
    );
  }

  return {
    observedUsage,
    checks: createObservedUsageChecks(observedUsage),
    metrics,
    artifacts: [
      createArtifact({
        id: "observed-usage-summary",
        type: "measurement",
        label: "Observed usage summary",
        description: "Observed token telemetry aggregated from local usage log files.",
        data: observedUsage,
      }),
    ],
  };
}
