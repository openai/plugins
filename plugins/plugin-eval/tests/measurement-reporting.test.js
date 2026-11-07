import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { analyzePath } from "../src/core/analyze.js";
import { analyzeObservedUsage } from "../src/core/observed-usage.js";
import { compareResults } from "../src/core/compare.js";
import { renderPayload } from "../src/renderers/index.js";

const execFileAsync = promisify(execFile);
const fixture = fileURLToPath(new URL("../fixtures/minimal-skill", import.meta.url));
const cli = fileURLToPath(new URL("../scripts/plugin-eval.js", import.meta.url));

async function workspace(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "plugin-eval-reporting-"));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  return root;
}

test("reports expose heuristic limits and the four assessment areas", async () => {
  const result = await analyzePath(fixture);
  for (const format of ["markdown", "html"]) {
    const report = renderPayload(result, format);
    assert.match(report, /not calibrated/i);
    for (const area of ["Operational correctness", "Maintainability", "Context efficiency", "Evidence coverage"]) {
      assert.ok(report.includes(area), `${format} must display ${area}`);
    }
  }
});

test("CLI includes explicitly supplied external instructions in budget estimates", async (t) => {
  const root = await workspace(t);
  const external = path.join(root, "external skill.md");
  await fs.writeFile(external, "External instruction.\n".repeat(30));
  const { stdout } = await execFileAsync(process.execPath,
    [cli, "explain-budget", fixture, "--additional-context", external, "--distribution", "private-local", "--format", "json"], { timeout: 30000 });
  const result = JSON.parse(stdout);
  assert.equal(result.budgets.external_context.components.length, 1);
  assert.equal(result.budgets.external_context.complete, false);
  assert.match(result.nextAction.command, /--distribution private-local/);
  assert.ok(result.budgets.invoke_cost_tokens.components.some((item) => path.resolve(item.path) === external));
});

test("CLI rejects missing additional context values", async () => {
  await assert.rejects(execFileAsync(process.execPath,
    [cli, "analyze", fixture, "--additional-context", "--format", "json"], { timeout: 30000 }), /Missing additional context/);
});

test("analysis and suggested follow-up commands preserve explicitly selected context", async (t) => {
  const root = await workspace(t);
  const external = path.join(root, "extra instructions.md");
  await fs.writeFile(external, "Read these additional instructions.");
  const result = await analyzePath(fixture, { additionalContextPaths: [external], distribution: "public" });
  assert.match(result.nextAction.command, /--additional-context/);
  assert.match(result.measurementPlan.nextAction.command, /--additional-context/);
  assert.match(result.workflowGuide.startHere.firstCommand, /--additional-context/);
  assert.match(result.nextAction.command, /--distribution public/);
  assert.match(result.measurementPlan.nextAction.command, /--distribution public/);
  assert.match(result.workflowGuide.startHere.firstCommand, /--distribution public/);
  const { stdout } = await execFileAsync(process.execPath,
    [cli, "start", fixture, "--additional-context", external, "--format", "json"], { timeout: 30000 });
  assert.match(JSON.parse(stdout).startHere.firstCommand, /--additional-context/);
});

test("full-session input telemetry cannot establish package estimate failure", async (t) => {
  const root = await workspace(t);
  const usage = path.join(root, "usage.json");
  await fs.writeFile(usage, JSON.stringify({ usage: { input_tokens: 10000, output_tokens: 30 }}));
  const result = await analyzeObservedUsage([usage], {
    trigger_cost_tokens: { value: 10 }, invoke_cost_tokens: { value: 100 },
  }, { kind: "skill", name: "fixture", path: root });
  assert.equal(result.observedUsage.estimateComparison.comparable, false);
  assert.ok(result.checks.every((check) => check.status !== "fail"));
  assert.ok(result.observedUsage.estimateComparison.note);
});

test("comparison report explains incompatible methods instead of printing a fake delta", async () => {
  const after = await analyzePath(fixture);
  const before = structuredClone(after);
  delete before.summary.assessment;
  const report = renderPayload(compareResults(before, after), "markdown");
  assert.match(report, /Grading methods differ/);
  assert.doesNotMatch(report, /[+]null/);
});

test("human reports disclose session and package scope even when token counts align", async (t) => {
  const root = await workspace(t);
  const baseline = await analyzePath(fixture);
  const tokens = baseline.budgets.trigger_cost_tokens.value + baseline.budgets.invoke_cost_tokens.value;
  const usage = path.join(root, "aligned.json");
  await fs.writeFile(usage, JSON.stringify({ usage: { input_tokens: tokens, output_tokens: 10 } }));
  const result = await analyzePath(fixture, { observedUsagePaths: [usage] });
  for (const format of ["markdown", "html"]) {
    assert.match(renderPayload(result, format), /Whole-session input includes/);
  }
});
