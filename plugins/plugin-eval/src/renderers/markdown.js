import {
  applyEvaluationPresentation,
  createBenchmarkRunNextAction,
  createBenchmarkTemplateNextAction,
  createBudgetNextAction,
  createComparisonNextAction,
  createEvaluationNextAction,
  createMeasurementPlanNextAction,
  createWorkflowGuideNextAction,
} from "../core/presentation.js";
import { enrichSummary } from "../core/scoring.js";

function detailsBlock(summary, body) {
  const content = Array.isArray(body) ? body.join("\n") : body;
  if (!content || content.trim().length === 0) {
    return "";
  }

  return [`<details>`, `<summary>${summary}</summary>`, "", content, `</details>`].join("\n");
}

function section(title, lines) {
  return [`## ${title}`, ...lines].join("\n");
}

function renderNextAction(nextAction) {
  if (!nextAction) {
    return ["- No recommended next step."];
  }

  return [
    `- ${nextAction.label}`,
    `- Why: ${nextAction.why}`,
    ...(nextAction.chatPrompt ? [`- Chat request: "${nextAction.chatPrompt}"`] : []),
    ...(nextAction.command ? [`- Local command: \`${nextAction.command}\``] : []),
  ];
}

function renderBudgets(budgets) {
  return [
    `- trigger_cost_tokens: ${budgets.trigger_cost_tokens.value} (${budgets.trigger_cost_tokens.band})`,
    `- invoke_cost_tokens: ${budgets.invoke_cost_tokens.value} (${budgets.invoke_cost_tokens.band})`,
    `- deferred_cost_tokens: ${budgets.deferred_cost_tokens.value} (${budgets.deferred_cost_tokens.band})`,
    `- total_tokens: ${budgets.total_tokens.value} (${budgets.total_tokens.band})`,
  ].join("\n");
}

function renderObservedUsage(observedUsage) {
  if (!observedUsage) {
    return "- No observed usage supplied.";
  }

  const comparison = observedUsage.estimateComparison;
  return [
    `- samples: ${observedUsage.sampleCount}`,
    `- observed_input_tokens_avg: ${observedUsage.inputTokens.average}`,
    `- observed_output_tokens_avg: ${observedUsage.outputTokens.average}`,
    `- observed_total_tokens_avg: ${observedUsage.totalTokens.average}`,
    ...(observedUsage.cachedTokens.total > 0
      ? [`- observed_cached_tokens_avg: ${observedUsage.cachedTokens.average}`]
      : []),
    ...(comparison
      ? [
          `- estimated_active_tokens: ${comparison.estimatedActiveTokens}`,
          `- estimate_vs_observed_input_delta: ${comparison.deltaTokens}`,
          `- estimate_vs_observed_input_ratio: ${comparison.deltaRatio} (${comparison.band})`,
        ]
      : []),
  ].join("\n");
}

function renderFindingList(findings, emptyLabel) {
  if (!findings || findings.length === 0) {
    return [`- ${emptyLabel}`];
  }

  return findings.map((finding) => {
    const parts = [`- [${finding.status}/${finding.severity}] ${finding.message}`];
    if (finding.why) {
      parts.push(`Why: ${finding.why}`);
    }
    if (finding.remediation?.length > 0) {
      parts.push(`Fix: ${finding.remediation.join(" ")}`);
    }
    return parts.join(" ");
  });
}

function renderChecks(checks) {
  if (checks.length === 0) {
    return "No checks recorded.";
  }

  return checks
    .map((check) => {
      const parts = [`- [${check.status.toUpperCase()}] ${check.id}: ${check.message}`];
      if (check.why) {
        parts.push(`Why: ${check.why}`);
      }
      if (check.evidence?.length > 0) {
        parts.push(`Evidence: ${check.evidence.join(" ")}`);
      }
      if (check.remediation?.length > 0) {
        parts.push(`Remediation: ${check.remediation.join(" ")}`);
      }
      return parts.join(" ");
    })
    .join("\n");
}

function renderMetrics(metrics) {
  if (metrics.length === 0) {
    return "No metrics recorded.";
  }

  return metrics
    .map((metric) => `- ${metric.id}: ${metric.value} ${metric.unit} (${metric.band})`)
    .join("\n");
}

function renderDeductions(summary) {
  if (!summary.deductions || summary.deductions.length === 0) {
    return "No deductions were applied.";
  }

  return summary.deductions
    .map(
      (entry) =>
        `- -${entry.penalty} points: ${entry.id} [${entry.status}/${entry.severity}] ${entry.message}`,
    )
    .join("\n");
}

function renderCategoryDeductions(summary) {
  if (!summary.categoryDeductions || summary.categoryDeductions.length === 0) {
    return "No category deductions recorded.";
  }

  return summary.categoryDeductions
    .map(
      (entry) =>
        `- ${entry.category}: -${entry.totalPenalty} points across ${entry.checks} check${entry.checks === 1 ? "" : "s"}`,
    )
    .join("\n");
}

function renderWorkflowGuide(guide) {
  if (!guide) {
    return "No chat workflow guidance available.";
  }

  const startHere = guide.startHere || guide.recommendedWorkflow;
  return [
    guide.beginnerSummary,
    "",
    `Start with this chat request: "${startHere.chatPrompt}"`,
    `Why this path: ${startHere.routingExplanation || startHere.summary}`,
    `Quick local entrypoint: ${startHere.startCommand}`,
    `Plugin Eval will run first: ${startHere.firstCommand}`,
    "",
    "Other chat requests you can use:",
    ...guide.entrypoints.map((entry) =>
      `- ${entry.label}: say "${entry.chatPrompt}" -> ${entry.firstCommand}`,
    ),
  ].join("\n");
}

function renderMeasurementPlan(plan) {
  if (!plan) {
    return "No measurement plan available.";
  }

  return [
    plan.summary,
    "",
    ...plan.toolsets.map(
      (toolset) =>
        `- ${toolset.label} [${toolset.priority}] ${toolset.goal} Signals: ${toolset.signals.join(", ")}. Evidence: ${toolset.evidenceSources.join(", ")}.`,
    ),
  ].join("\n");
}

function ensureEvaluationPayload(payload) {
  const nextPayload = {
    ...payload,
    summary: enrichSummary(payload, payload.summary || {}),
  };

  if (!nextPayload.nextAction) {
    nextPayload.nextAction = createEvaluationNextAction(nextPayload);
  }

  return applyEvaluationPresentation(nextPayload);
}

function ensureMeasurementPlanPayload(payload) {
  return {
    ...payload,
    nextAction: payload.nextAction || createMeasurementPlanNextAction(payload),
  };
}

function ensureBudgetPayload(payload) {
  return {
    ...payload,
    nextAction: payload.nextAction || createBudgetNextAction(payload),
  };
}

function ensureWorkflowPayload(payload) {
  return {
    ...payload,
    nextAction: payload.nextAction || createWorkflowGuideNextAction(payload),
  };
}

function ensureBenchmarkTemplatePayload(payload) {
  return {
    ...payload,
    nextAction: payload.nextAction || createBenchmarkTemplateNextAction(payload),
  };
}

function ensureBenchmarkRunPayload(payload) {
  return {
    ...payload,
    nextAction: payload.nextAction || createBenchmarkRunNextAction(payload),
  };
}

function ensureComparisonPayload(payload) {
  return {
    ...payload,
    nextAction: payload.nextAction || createComparisonNextAction(payload),
  };
}

function renderEvaluation(payload) {
  const result = ensureEvaluationPayload(payload);

  return [
    `# Plugin Eval Report: ${result.target.name}`,
    "",
    section("At a Glance", [
      `- Score: ${result.summary.score}/100`,
      `- Grade: ${result.summary.grade}`,
      `- Risk: ${result.summary.riskLevel}`,
      `- Checks: ${result.summary.checkCounts.fail} fail, ${result.summary.checkCounts.warn} warn, ${result.summary.checkCounts.info} info`,
      `- Active budget: ${result.budgets.trigger_cost_tokens.value + result.budgets.invoke_cost_tokens.value} tokens (${result.budgets.invoke_cost_tokens.band})`,
      `- Observed usage: ${result.observedUsage?.sampleCount ? `${result.observedUsage.sampleCount} sample${result.observedUsage.sampleCount === 1 ? "" : "s"}` : "not supplied"}`,
    ]),
    "",
    section("Why It Matters", result.summary.whyBullets.map((item) => `- ${item}`)),
    "",
    section("Fix First", renderFindingList(result.summary.fixFirst, "No urgent fixes were identified.")),
    "",
    section("Recommended Next Step", renderNextAction(result.nextAction)),
    "",
    section("Details", [
      detailsBlock("Watch next", renderFindingList(result.summary.watchNext, "No secondary findings queued.")),
      detailsBlock(
        "Improvement brief",
        [
          `- ${result.improvementBrief?.summary || "No improvement brief available."}`,
          ...(result.improvementBrief?.goals?.length > 0
            ? result.improvementBrief.goals.map((item) => `- Goal: ${item}`)
            : []),
          ...(result.improvementBrief?.measurementGoals?.length > 0
            ? result.improvementBrief.measurementGoals.map((item) => `- Measure: ${item}`)
            : []),
          ...(result.improvementBrief?.suggestedPrompt
            ? [`- Suggested prompt: ${result.improvementBrief.suggestedPrompt}`]
            : []),
        ].join("\n"),
      ),
      detailsBlock(
        "Budgets and observed usage",
        [renderBudgets(result.budgets), "", renderObservedUsage(result.observedUsage)].join("\n"),
      ),
      detailsBlock("Measurement plan", renderMeasurementPlan(result.measurementPlan)),
      detailsBlock("Use From Codex Chat", renderWorkflowGuide(result.workflowGuide)),
      detailsBlock("Checks", renderChecks(result.checks)),
      detailsBlock("Metrics", renderMetrics(result.metrics)),
      detailsBlock("Score details", [
        `- Starting score: ${result.summary.scoreBreakdown.startingScore}`,
        `- Total deductions: -${result.summary.scoreBreakdown.totalDeductions}`,
        `- Final score: ${result.summary.scoreBreakdown.finalScore}`,
        ...(result.summary.riskReasons?.length > 0
          ? result.summary.riskReasons.map((item) => `- Risk: ${item}`)
          : []),
        "",
        renderDeductions(result.summary),
        "",
        renderCategoryDeductions(result.summary),
      ].join("\n")),
    ].filter(Boolean)),
  ].join("\n");
}

function renderWorkflowGuidePayload(payload) {
  const guide = ensureWorkflowPayload(payload);

  return [
    `# Plugin Eval Start Here: ${guide.target.name}`,
    "",
    section("At a Glance", [
      `- Recommended path: ${guide.startHere.label}`,
      `- Benchmark config present: ${guide.workflowStatus.hasBenchmarkConfig ? "yes" : "no"}`,
      `- Usage log present: ${guide.workflowStatus.hasUsageLog ? "yes" : "no"}`,
      `- Quick local entrypoint: \`${guide.startHere.startCommand}\``,
      `- First local command: \`${guide.startHere.firstCommand}\``,
    ]),
    "",
    section("Why It Matters", [
      `- ${guide.beginnerSummary}`,
      `- ${guide.startHere.routingExplanation}`,
    ]),
    "",
    section("Fix First", ["- Start with the recommended path before branching into secondary workflows."]),
    "",
    section("Recommended Next Step", renderNextAction(guide.nextAction)),
    "",
    section("Details", [
      detailsBlock(
        "Full local sequence",
        guide.startHere.commands.map((command) => `- ${command}`).join("\n"),
      ),
      detailsBlock(
        "Other chat requests",
        guide.entrypoints
          .map((entry) => `- ${entry.label}: "${entry.chatPrompt}" -> ${entry.firstCommand}`)
          .join("\n"),
      ),
    ]),
  ].join("\n");
}

function renderBudgetExplanation(payload) {
  const budgetPayload = ensureBudgetPayload(payload);
  const budgets = budgetPayload.budgets;
  const whyBullets = [
    `- Budget method: ${budgets.method}.`,
    `- Trigger and invoke tokens matter most because they are closest to always-loaded or frequently-loaded context.`,
    ...(budgetPayload.baselineEvidence
      ? [`- Baseline corpus: skills=${budgetPayload.baselineEvidence.skillSamples}, plugins=${budgetPayload.baselineEvidence.pluginSamples}.`]
      : []),
  ];
  const fixFirst = ["- Nothing to fix from this view alone; use the next step to validate or contextualize the estimate."];

  if (["heavy", "excessive"].includes(budgets.trigger_cost_tokens.band) || ["heavy", "excessive"].includes(budgets.invoke_cost_tokens.band)) {
    fixFirst.unshift("- The active budget is heavy enough that measured usage is worth collecting before tuning copy or structure.");
  }

  return [
    `# Budget Explanation: ${budgetPayload.target.name}`,
    "",
    section("At a Glance", [
      ...renderBudgets(budgets).split("\n"),
    ]),
    "",
    section("Why It Matters", whyBullets),
    "",
    section("Fix First", fixFirst),
    "",
    section("Recommended Next Step", renderNextAction(budgetPayload.nextAction)),
    "",
    section("Details", [
      detailsBlock(
        "Trigger components",
        budgets.trigger_cost_tokens.components.map((component) => `- ${component.label}: ${component.tokens} tokens`).join("\n"),
      ),
      detailsBlock(
        "Invoke components",
        budgets.invoke_cost_tokens.components.map((component) => `- ${component.label}: ${component.tokens} tokens`).join("\n"),
      ),
      detailsBlock(
        "Deferred components",
        budgets.deferred_cost_tokens.components.length > 0
          ? budgets.deferred_cost_tokens.components.map((component) => `- ${component.label}: ${component.tokens} tokens`).join("\n")
          : "- None",
      ),
      detailsBlock("Use From Codex Chat", renderWorkflowGuide(budgetPayload.workflowGuide)),
    ]),
  ].join("\n");
}

function renderMeasurementPlanPayload(payload) {
  const plan = ensureMeasurementPlanPayload(payload);
  const recommendedToolsets = plan.toolsets.filter((toolset) => plan.recommendedToolsets.includes(toolset.id));

  return [
    `# Measurement Plan: ${plan.target.name}`,
    "",
    section("At a Glance", [
      `- Recommended toolsets: ${plan.recommendedToolsets.length > 0 ? plan.recommendedToolsets.join(", ") : "none"}`,
      `- Toolset count: ${plan.toolsets.length}`,
      `- Summary: ${plan.summary}`,
    ]),
    "",
    section("Why It Matters", [
      `- ${plan.summary}`,
      ...recommendedToolsets.map((toolset) => `- ${toolset.label}: ${toolset.goal}`),
    ]),
    "",
    section(
      "Fix First",
      recommendedToolsets.length > 0
        ? recommendedToolsets.map((toolset) => `- ${toolset.label}: ${toolset.why}`)
        : ["- No high-priority toolsets were selected."],
    ),
    "",
    section("Recommended Next Step", renderNextAction(plan.nextAction)),
    "",
    section("Details", [
      detailsBlock(
        "Recommended toolsets",
        plan.recommendedToolsets.length > 0
          ? plan.recommendedToolsets.map((item) => `- ${item}`).join("\n")
          : "- None",
      ),
      detailsBlock(
        "All toolsets",
        plan.toolsets
          .map(
            (toolset) =>
              `- ${toolset.label} [${toolset.priority}] ${toolset.goal} Signals: ${toolset.signals.join(", ")}. Evidence: ${toolset.evidenceSources.join(", ")}. Starter pack: ${toolset.starterPack.manifestName}.`,
          )
          .join("\n"),
      ),
      detailsBlock("Use From Codex Chat", renderWorkflowGuide(plan.workflowGuide)),
    ]),
  ].join("\n");
}

function renderBenchmarkTemplateInit(payload) {
  const benchmarkPayload = ensureBenchmarkTemplatePayload(payload);

  return [
    `# Benchmark Template Ready: ${benchmarkPayload.target.name}`,
    "",
    section("At a Glance", [
      `- Config: \`${benchmarkPayload.configPath}\``,
      `- Scenarios: ${benchmarkPayload.scenarioCount}`,
    ]),
    "",
    section("Why It Matters", benchmarkPayload.notes.map((item) => `- ${item}`)),
    "",
    section("Fix First", ["- Edit the benchmark config so the scenarios match your real workflow before you trust the run."]),
    "",
    section("Recommended Next Step", renderNextAction(benchmarkPayload.nextAction)),
    "",
    section("Details", [
      detailsBlock(
        "Setup questions to ask first",
        benchmarkPayload.setupQuestions?.length > 0
          ? benchmarkPayload.setupQuestions.map((item) => `- ${item}`).join("\n")
          : "- No setup questions provided.",
      ),
      detailsBlock("Next steps", benchmarkPayload.nextSteps.map((item) => `- ${item}`).join("\n")),
      detailsBlock("Use From Codex Chat", renderWorkflowGuide(benchmarkPayload.workflowGuide)),
    ]),
  ].join("\n");
}

function renderBenchmarkScenario(scenario, mode) {
  const lines = [
    `- Purpose: ${scenario.purpose || "Not provided"}`,
    ...(scenario.successChecklist?.length > 0
      ? scenario.successChecklist.map((item) => `- Success checklist: ${item}`)
      : []),
  ];

  lines.push(`- Status: ${scenario.status}`);
  lines.push(`- Duration: ${scenario.durationMs} ms`);
  lines.push(`- Tool calls: ${scenario.telemetry?.toolCallCount || 0}`);
  lines.push(`- Shell commands: ${scenario.telemetry?.shellCommandCount || 0}`);
  lines.push(`- Failed shell commands: ${scenario.telemetry?.failedShellCommandCount || 0}`);
  lines.push(`- Usage availability: ${scenario.usageAvailability || "unavailable"}`);

  if (scenario.usage) {
    lines.push(`- Input tokens: ${scenario.usage.input_tokens || 0}`);
    lines.push(`- Output tokens: ${scenario.usage.output_tokens || 0}`);
    lines.push(`- Total tokens: ${scenario.usage.total_tokens || 0}`);
  }

  if (scenario.workspaceSummary) {
    lines.push(`- Added files: ${scenario.workspaceSummary.addedFileCount}`);
    lines.push(`- Modified files: ${scenario.workspaceSummary.modifiedFileCount}`);
    lines.push(`- Deleted files: ${scenario.workspaceSummary.deletedFileCount}`);
    lines.push(`- Generated tests: ${scenario.workspaceSummary.generatedTestFileCount}`);
  }

  if (scenario.finalMessagePreview) {
    lines.push("", "```text", scenario.finalMessagePreview, "```");
  }

  if (scenario.workspaceChanges?.length > 0) {
    lines.push("", ...scenario.workspaceChanges.map((entry) => `- ${entry.status}: ${entry.path}`));
  }

  if (scenario.verifierResults?.length > 0) {
    lines.push("", ...scenario.verifierResults.map((result) => `- Verifier [${result.status}]: ${result.command}`));
  }

  if (scenario.generatedCode?.metrics?.length > 0) {
    lines.push("", ...scenario.generatedCode.metrics.map((metric) => `- ${metric.id}: ${metric.value} ${metric.unit} (${metric.band})`));
  }

  if (scenario.generatedCode?.checks?.length > 0) {
    lines.push("", ...scenario.generatedCode.checks.map((check) => `- [${check.status}] ${check.message}`));
  }

  return detailsBlock(scenario.title, lines.join("\n"));
}

function renderBenchmarkRun(payload) {
  const benchmarkPayload = ensureBenchmarkRunPayload(payload);

  return [
    `# Benchmark Run: ${benchmarkPayload.target.name}`,
    "",
    section("At a Glance", [
      `- Mode: ${benchmarkPayload.mode}`,
      `- Codex version: ${benchmarkPayload.codexVersion}`,
      `- Scenarios: ${benchmarkPayload.config.scenarioCount}`,
      `- Model: ${benchmarkPayload.config.model}`,
      `- Workspace source: \`${benchmarkPayload.config.workspaceSourcePath}\``,
      `- Setup mode: ${benchmarkPayload.config.workspaceSetupMode}`,
      `- Preserve policy: ${benchmarkPayload.config.workspacePreserve}`,
      ...(benchmarkPayload.usageLogPath ? [`- Usage log: \`${benchmarkPayload.usageLogPath}\``] : []),
      `- Run directory: \`${benchmarkPayload.runDirectory}\``,
      `- Usage availability: ${benchmarkPayload.summary.usageAvailability}`,
      `- Average input tokens: ${benchmarkPayload.summary.averageInputTokens}`,
      `- Average output tokens: ${benchmarkPayload.summary.averageOutputTokens}`,
      `- Average total tokens: ${benchmarkPayload.summary.averageTotalTokens}`,
      `- Tool calls: ${benchmarkPayload.summary.toolCallCount}`,
      `- Shell commands: ${benchmarkPayload.summary.shellCommandCount}`,
      `- Failed shell commands: ${benchmarkPayload.summary.failedShellCommands}`,
      `- Generated files: ${benchmarkPayload.summary.generatedFileCount}`,
      `- Generated tests: ${benchmarkPayload.summary.generatedTestFileCount}`,
    ]),
    "",
    section("Why It Matters", [
      "- Benchmarking now runs real `codex exec` sessions in isolated workspaces instead of simulating the skill or plugin through a single API request.",
      `- Completed scenarios: ${benchmarkPayload.summary.completedScenarios}/${benchmarkPayload.summary.scenarioCount}`,
      `- Usage samples collected: ${benchmarkPayload.summary.sampleCount}`,
    ]),
    "",
    section(
      "Fix First",
      benchmarkPayload.summary.failedScenarios > 0
        ? ["- At least one scenario failed. Inspect the scenario logs and any preserved workspace before trusting the benchmark."]
        : benchmarkPayload.summary.usageAvailability === "unavailable"
          ? ["- No usage telemetry was emitted, so treat workspace outcomes and verifier results as the primary benchmark signal."]
          : ["- Re-run analysis with the usage log before you start optimizing the skill or plugin."],
    ),
    "",
    section("Recommended Next Step", renderNextAction(benchmarkPayload.nextAction)),
    "",
    section("Details", [
      detailsBlock(
        "Scenarios",
        benchmarkPayload.scenarios
          .map((scenario) => renderBenchmarkScenario(scenario, benchmarkPayload.mode))
          .join("\n\n"),
      ),
      detailsBlock("Workflow follow-up", benchmarkPayload.nextSteps.map((item) => `- ${item}`).join("\n")),
      detailsBlock("Use From Codex Chat", renderWorkflowGuide(benchmarkPayload.workflowGuide)),
    ]),
  ].join("\n");
}

function renderComparison(payload) {
  const diff = ensureComparisonPayload(payload);
  const whyBullets = [
    `- Score delta: ${diff.scoreDelta >= 0 ? "+" : ""}${diff.scoreDelta}.`,
    `- Grade moved from ${diff.gradeBefore} to ${diff.gradeAfter}.`,
    `- Risk moved from ${diff.riskBefore} to ${diff.riskAfter}.`,
  ];

  if (diff.newFailures.length > 0) {
    whyBullets.push(`- ${diff.newFailures.length} new failure${diff.newFailures.length === 1 ? "" : "s"} were introduced.`);
  }
  if (diff.resolvedFailures.length > 0) {
    whyBullets.push(`- ${diff.resolvedFailures.length} failure${diff.resolvedFailures.length === 1 ? "" : "s"} were resolved.`);
  }

  return [
    `# Plugin Eval Comparison: ${diff.target.name}`,
    "",
    section("At a Glance", [
      `- Score delta: ${diff.scoreDelta >= 0 ? "+" : ""}${diff.scoreDelta}`,
      `- Grade: ${diff.gradeBefore} -> ${diff.gradeAfter}`,
      `- Risk: ${diff.riskBefore} -> ${diff.riskAfter}`,
      `- Budget delta (trigger/invoke/deferred): ${diff.budgetDelta.trigger_cost_tokens >= 0 ? "+" : ""}${diff.budgetDelta.trigger_cost_tokens} / ${diff.budgetDelta.invoke_cost_tokens >= 0 ? "+" : ""}${diff.budgetDelta.invoke_cost_tokens} / ${diff.budgetDelta.deferred_cost_tokens >= 0 ? "+" : ""}${diff.budgetDelta.deferred_cost_tokens}`,
    ]),
    "",
    section("Why It Matters", whyBullets),
    "",
    section(
      "Fix First",
      diff.newFailures.length > 0
        ? diff.newFailures.map((item) => `- New failure: ${item}`)
        : ["- No new failures were introduced."],
    ),
    "",
    section("Recommended Next Step", renderNextAction(diff.nextAction)),
    "",
    section("Details", [
      detailsBlock(
        "Resolved failures",
        diff.resolvedFailures.length > 0
          ? diff.resolvedFailures.map((item) => `- ${item}`).join("\n")
          : "- No resolved failures.",
      ),
      detailsBlock(
        "New failures",
        diff.newFailures.length > 0
          ? diff.newFailures.map((item) => `- ${item}`).join("\n")
          : "- No new failures.",
      ),
    ]),
  ].join("\n");
}

export function renderMarkdown(payload) {
  if (payload.kind === "comparison") {
    return renderComparison(payload);
  }
  if (payload.kind === "workflow-guide") {
    return renderWorkflowGuidePayload(payload);
  }
  if (payload.kind === "budget-explanation") {
    return renderBudgetExplanation(payload);
  }
  if (payload.kind === "measurement-plan") {
    return renderMeasurementPlanPayload(payload);
  }
  if (payload.kind === "benchmark-template-init") {
    return renderBenchmarkTemplateInit(payload);
  }
  if (payload.kind === "benchmark-run") {
    return renderBenchmarkRun(payload);
  }
  return renderEvaluation(payload);
}
