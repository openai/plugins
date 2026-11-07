import assert from "node:assert/strict";
import test from "node:test";
import { computeSummary } from "../src/core/scoring.js";
import { compareResults } from "../src/core/compare.js";

function result(checks = []) {
  const value = { target: { kind: "plugin", path: "/fixture", name: "fixture" }, checks, budgets: {} };
  value.summary = computeSummary(value);
  return value;
}

function check(id, category, severity, status) {
  return { id, category, severity, status, message: id, remediation: [], evidence: [] };
}

test("informational and missing-evidence findings never lower the static index", () => {
  const value = result([
    check("coverage-artifacts-missing", "coverage", "info", "info"),
    check("py-tests-missing", "best-practice", "warning", "warn"),
  ]);
  assert.equal(value.summary.score, 100);
  assert.equal(value.summary.scoreBreakdown.totalDeductions, 0);
  assert.equal(value.summary.dimensions.evidenceCoverage.checkCounts.warn, 1);
});

test("an informational finding is counted once in status totals", () => {
  const value = result([check("coverage-absent", "coverage", "info", "info")]);
  assert.equal(value.summary.checkCounts.total, 1);
  assert.equal(value.summary.checkCounts.info, 1);
  assert.equal(value.summary.checkCounts.severityCounts.info, 1);
});

test("large static inventories cannot establish high operational risk", () => {
  const value = result([check("deferred_cost_tokens-budget-high", "budget", "error", "fail")]);
  assert.equal(value.summary.score, 100);
  assert.equal(value.summary.riskLevel, "unknown");
  assert.equal(value.summary.dimensions.contextEfficiency.status, "attention");
});

test("maintenance warnings do not turn a low heuristic index into operational risk", () => {
  const value = result(Array.from({length: 12}, (_, i) => check(`long-${i}`, "readability", "warning", "warn")));
  assert.ok(value.summary.score < 70);
  assert.equal(value.summary.riskLevel, "unknown");
  assert.equal(value.summary.dimensions.maintainability.status, "attention");
});

test("functional failures still lower the index and raise scoped operational risk", () => {
  const value = result([check("manifest-invalid", "manifest", "error", "fail")]);
  assert.equal(value.summary.score, 86);
  assert.equal(value.summary.riskLevel, "high");
  assert.equal(value.summary.dimensions.operationalCorrectness.status, "attention");
});

test("UI length preferences are not operational failures", () => {
  const value = result([check("default-prompt-too-long", "manifest", "warning", "warn")]);
  assert.equal(value.summary.riskLevel, "unknown");
  assert.equal(value.summary.dimensions.maintainability.status, "attention");
});

test("comparison continuation retains the evaluated context scenario", () => {
  const after = result();
  after.additionalContextPaths = ["/fixture/context.md"];
  after.distribution = "private-local";
  assert.match(compareResults(result(), after).nextAction.command, /--additional-context/);
  assert.match(compareResults(result(), after).nextAction.command, /--distribution private-local/);
});

test("comparison does not treat distribution-scope changes as quality improvements", () => {
  const before = result();
  before.distribution = "public";
  const after = result();
  after.distribution = "private-local";
  assert.equal(compareResults(before, after).scoreDelta, null);
});

test("static grades explicitly disclose that their weights are not calibrated", () => {
  const value = result();
  assert.equal(value.summary.assessment.calibrated, false);
  assert.equal(value.summary.assessment.method, "static-check-heuristic-v2");
  assert.ok(value.summary.assessment.limitations.length > 0);
  assert.equal(value.summary.dimensions.operationalCorrectness.status, "not-assessed");
});

test("comparison refuses score deltas across different grading methods", () => {
  const before = result();
  delete before.summary.assessment;
  before.summary.score = 63;
  const after = result();
  const comparison = compareResults(before, after);
  assert.equal(comparison.scoreComparable, false);
  assert.equal(comparison.scoreDelta, null);
  assert.ok(comparison.comparisonNote);
});

test("comparison preserves deltas for results produced by the same method", () => {
  const before = result([check("manifest-invalid", "manifest", "error", "fail")]);
  const after = result();
  const comparison = compareResults(before, after);
  assert.equal(comparison.scoreComparable, true);
  assert.equal(comparison.scoreDelta, 14);
});

test("comparison does not subtract inventories with different measurement definitions", () => {
  const before = result();
  before.budgets = { deferred_cost_tokens: { value: 9000 } };
  const after = result();
  after.budgets = { measurement: { version: 2 }, deferred_cost_tokens: { value: 100 } };
  const comparison = compareResults(before, after);
  assert.equal(comparison.budgetComparable, false);
  assert.equal(comparison.budgetDelta.deferred_cost_tokens, null);
});
