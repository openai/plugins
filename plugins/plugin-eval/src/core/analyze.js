import path from "node:path";

import { loadBudgetBaseline } from "./baseline.js";
import { applyBudgetBands, computeBudgetProfile } from "./budget.js";
import { buildImprovementBrief } from "./improvement-brief.js";
import { buildMeasurementPlan } from "./measurement-plan.js";
import { runMetricPacks } from "./metric-packs.js";
import { analyzeObservedUsage } from "./observed-usage.js";
import { applyEvaluationPresentation, createBudgetNextAction, createMeasurementPlanNextAction } from "./presentation.js";
import { createArtifact, createCheck, createEvaluationResult, createMetric } from "./schema.js";
import { computeSummary } from "./scoring.js";
import { resolveTarget } from "./target.js";
import { buildWorkflowGuide } from "./workflow-guide.js";
import { analyzeCodeMetrics } from "../evaluators/code.js";
import { analyzeCoverageArtifacts } from "../evaluators/coverage.js";
import { evaluatePlugin } from "../evaluators/plugin.js";
import { evaluateSkill } from "../evaluators/skill.js";

function appendFragment(result, fragment) {
  result.checks.push(...(fragment.checks || []));
  result.metrics.push(...(fragment.metrics || []));
  result.artifacts.push(...(fragment.artifacts || []));
}

function addBudgetFindings(result, budgets, baselineEvidence) {
  result.budgets = budgets;
  const bucketNames = ["trigger_cost_tokens", "invoke_cost_tokens", "deferred_cost_tokens"];

  for (const bucketName of bucketNames) {
    const bucket = budgets[bucketName];
    result.metrics.push(
      createMetric({
        id: bucketName,
        category: "budget",
        value: bucket.value,
        unit: "tokens",
        band: bucket.band,
      }),
    );

    if (bucket.band === "heavy" || bucket.band === "excessive") {
      result.checks.push(
        createCheck({
          id: `${bucketName}-budget-high`,
          category: "budget",
          severity: bucket.band === "excessive" ? "error" : "warning",
          status: bucket.band === "excessive" ? "fail" : "warn",
          message: `${bucketName} is ${bucket.band} relative to the current Codex baseline.`,
          evidence: [
            `Value: ${bucket.value} tokens`,
            `Baseline samples: skills=${baselineEvidence.skillSamples}, plugins=${baselineEvidence.pluginSamples}`,
          ],
          remediation: ["Reduce repeated instruction text and move detail into deferred supporting files."],
        }),
      );
    }
  }

  result.artifacts.push(
    createArtifact({
      id: "budget-breakdown",
      type: "budget",
      label: "Budget breakdown",
      description: "Trigger, invoke, and deferred token budget analysis.",
      data: {
        budgets,
        baselineEvidence,
      },
    }),
  );
}

function normalizeExtensionPayload(extension) {
  return {
    ...extension,
    checks: extension.checks.map((check) => ({ ...check, source: `extension:${extension.name}` })),
    metrics: extension.metrics.map((metric) => ({ ...metric, source: `extension:${extension.name}` })),
    artifacts: extension.artifacts.map((artifact) => ({ ...artifact, source: `extension:${extension.name}` })),
  };
}

export async function analyzePath(targetPath, options = {}) {
  const target = await resolveTarget(targetPath);
  const result = createEvaluationResult(target);

  if (target.kind === "skill") {
    appendFragment(result, await evaluateSkill(target.path));
  } else if (target.kind === "plugin") {
    appendFragment(result, await evaluatePlugin(target.path));
  } else {
    result.checks.push(
      createCheck({
        id: "generic-target-analysis",
        category: "best-practice",
        severity: "info",
        status: "info",
        message: "The target is not a skill or plugin root, so only generic code, coverage, and budget analysis will run.",
        evidence: [path.resolve(target.path)],
        remediation: ["Point the analyzer at a skill directory or plugin root for richer structural checks."],
      }),
    );
  }

  const baseline = await loadBudgetBaseline();
  const rawBudget = await computeBudgetProfile(target);
  addBudgetFindings(result, applyBudgetBands(rawBudget, baseline), baseline.evidence);

  const observedUsageFragment = await analyzeObservedUsage(options.observedUsagePaths || [], rawBudget, target);
  if (observedUsageFragment) {
    result.observedUsage = observedUsageFragment.observedUsage;
    appendFragment(result, observedUsageFragment);
  }

  appendFragment(result, await analyzeCodeMetrics(target.path, target));
  appendFragment(result, await analyzeCoverageArtifacts(target.path));

  const extensions = await runMetricPacks(target, options.metricPackManifests || []);
  result.extensions = extensions.map(normalizeExtensionPayload);

  result.summary = computeSummary(result);
  result.measurementPlan = buildMeasurementPlan(result);
  result.artifacts.push(result.measurementPlan.artifact);
  result.improvementBrief = buildImprovementBrief(result);
  result.workflowGuide = await buildWorkflowGuide(target.path, {
    goal: result.observedUsage?.sampleCount ? "measure" : "evaluate",
  });
  result.measurementPlan.nextAction = createMeasurementPlanNextAction(result.measurementPlan);
  applyEvaluationPresentation(result);
  return result;
}

export async function explainBudget(targetPath) {
  const target = await resolveTarget(targetPath);
  const baseline = await loadBudgetBaseline();
  const rawBudget = await computeBudgetProfile(target);
  const payload = {
    kind: "budget-explanation",
    createdAt: new Date().toISOString(),
    target,
    budgets: applyBudgetBands(rawBudget, baseline),
    baselineEvidence: baseline.evidence,
    workflowGuide: await buildWorkflowGuide(target.path, {
      goal: "budget",
    }),
  };
  payload.nextAction = createBudgetNextAction(payload);
  return payload;
}

export async function recommendMeasures(targetPath, options = {}) {
  const result = await analyzePath(targetPath, options);
  const payload = {
    ...result.measurementPlan,
    workflowGuide: await buildWorkflowGuide(result.target.path, {
      goal: "measure",
    }),
  };
  payload.nextAction = payload.nextAction || createMeasurementPlanNextAction(payload);
  return payload;
}
