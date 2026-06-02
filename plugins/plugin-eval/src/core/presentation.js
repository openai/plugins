import { formatCommandPath, relativePath } from "../lib/files.js";
import { enrichSummary } from "./scoring.js";

function shellQuote(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`;
}

function targetLabel(target) {
  if (target.kind === "plugin") {
    return "plugin";
  }
  if (target.kind === "skill") {
    return "skill";
  }
  return "target";
}

function targetTypeLabel(target) {
  if (target.kind === "plugin") {
    return "plugin";
  }
  if (target.kind === "skill") {
    return "skill";
  }
  return "item";
}

function buildStartCommand(target, chatPrompt) {
  return `plugin-eval start ${formatCommandPath(target.path)} --request ${shellQuote(chatPrompt)} --format markdown`;
}

function hasStructuralFailures(result) {
  return result.checks.some(
    (check) =>
      check.status === "fail" &&
      (check.category === "manifest" || check.category === "skill-structure"),
  );
}

function hasBudgetPressure(result) {
  return ["heavy", "excessive"].includes(result.budgets?.trigger_cost_tokens?.band) ||
    ["heavy", "excessive"].includes(result.budgets?.invoke_cost_tokens?.band);
}

function hasWarningsOrFailures(result) {
  return result.checks.some((check) => check.status === "fail" || check.status === "warn");
}

export function createEvaluationNextAction(result) {
  const labelName = targetLabel(result.target);

  if (hasStructuralFailures(result)) {
    return {
      label: "Fix structural issues first",
      why: "Failing manifest or skill structure issues reduce trust and can invalidate later measurements.",
      command: buildStartCommand(result.target, "What should I fix first?"),
      chatPrompt: "What should I fix first?",
    };
  }

  if (!result.observedUsage?.sampleCount && hasBudgetPressure(result)) {
    return {
      label: "Measure real token usage next",
      why: "The static budget looks heavy, so live usage is the fastest way to confirm whether the cost is acceptable.",
      command: buildStartCommand(result.target, `Measure the real token usage of this ${labelName}.`),
      chatPrompt: `Measure the real token usage of this ${labelName}.`,
    };
  }

  if (result.observedUsage?.sampleCount) {
    return {
      label: "Review the measurement plan",
      why: "You already have observed usage, so the highest-value next step is deciding what to instrument or improve.",
      command: buildStartCommand(result.target, "What should I run next?"),
      chatPrompt: "What should I run next?",
    };
  }

  if (hasWarningsOrFailures(result)) {
    return {
      label: "Fix the top findings and rerun the report",
      why: "A short pass on the highest-value findings will improve trust, readability, and the signal quality of future benchmarks.",
      command: buildStartCommand(result.target, "What should I fix first?"),
      chatPrompt: "What should I fix first?",
    };
  }

  return {
    label: "Choose the next workflow from chat",
    why: "The report is clean enough that the best next step depends on whether you want budgets, benchmarks, or comparisons.",
    command: buildStartCommand(result.target, "What should I run next?"),
    chatPrompt: "What should I run next?",
  };
}

export function applyEvaluationPresentation(result) {
  result.summary = enrichSummary(result, result.summary);
  if (!result.nextAction) {
    result.nextAction = createEvaluationNextAction(result);
  }
  return result;
}

export function createWorkflowGuideNextAction(guide) {
  const startHere = guide.startHere || guide.recommendedWorkflow;
  return {
    label: startHere?.label || guide.recommendedWorkflow?.label || "Start here",
    why: startHere?.routingExplanation || guide.recommendedWorkflow?.summary || guide.beginnerSummary,
    command: startHere?.firstCommand || guide.recommendedWorkflow?.firstCommand,
    chatPrompt: startHere?.chatPrompt || guide.recommendedWorkflow?.chatPrompt,
  };
}

export function createMeasurementPlanNextAction(plan) {
  const toolset = plan.toolsets.find((entry) => plan.recommendedToolsets.includes(entry.id)) || plan.toolsets[0];
  const targetKind = targetTypeLabel(plan.target);

  return {
    label: toolset ? `Start with ${toolset.label}` : "Decide what to measure next",
    why: toolset
      ? toolset.goal
      : "A small measurement pass will turn the current report into a more trustworthy workflow decision.",
    command: buildStartCommand(plan.target, `What should I run next?`),
    chatPrompt: `What should I run next?`,
    ...(toolset ? { toolsetId: toolset.id } : {}),
    ...(toolset
      ? {}
      : {
          why: `Use Plugin Eval to decide the next measurement move for this ${targetKind}.`,
        }),
  };
}

export function createBudgetNextAction(payload) {
  const labelName = targetLabel(payload.target);
  const hasHeavyBudget = ["heavy", "excessive"].includes(payload.budgets?.trigger_cost_tokens?.band) ||
    ["heavy", "excessive"].includes(payload.budgets?.invoke_cost_tokens?.band);

  if (hasHeavyBudget) {
    return {
      label: "Validate the budget with real usage",
      why: "The estimate looks heavy enough that measured usage is worth collecting before you rewrite the skill or plugin.",
      command: buildStartCommand(payload.target, `Measure the real token usage of this ${labelName}.`),
      chatPrompt: `Measure the real token usage of this ${labelName}.`,
    };
  }

  return {
    label: "Review the full evaluation",
    why: "The budget does not look alarming on its own, so the next useful step is the full structural and quality report.",
    command: buildStartCommand(payload.target, `Evaluate this ${labelName}.`),
    chatPrompt: `Evaluate this ${labelName}.`,
  };
}

export function createBenchmarkTemplateNextAction(payload) {
  const commandTargetPath = formatCommandPath(payload.target.path);
  const commandConfigPath = formatCommandPath(payload.configPath);
  return {
    label: "Run the Codex benchmark",
    why: "Benchmarking now means a real codex exec run, so the next step is to execute the edited scenarios in an isolated workspace.",
    command: `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath} --format markdown`,
    chatPrompt: `Help me benchmark this ${targetLabel(payload.target)}.`,
  };
}

export function createBenchmarkRunNextAction(payload) {
  const commandTargetPath = formatCommandPath(payload.target.path);
  return {
    label: payload.usageLogPath ? "Fold the usage log back into analysis" : "Review the benchmark report",
    why: payload.usageLogPath
      ? "The Codex run produced observed usage, so the next step is to re-run analysis with those measurements."
      : "This benchmark completed without usage telemetry, so the report and preserved artifacts are the primary signal.",
    command: payload.usageLogPath
      ? `plugin-eval analyze ${commandTargetPath} --observed-usage ${formatCommandPath(payload.usageLogPath)} --format markdown`
      : `plugin-eval report ${formatCommandPath(payload.resultPath)} --format markdown`,
    chatPrompt: payload.usageLogPath ? `What should I run next?` : `Help me benchmark this ${targetLabel(payload.target)}.`,
  };
}

export function createComparisonNextAction(diff) {
  const chatPrompt = diff.newFailures.length > 0 ? "What should I fix first?" : "What should I run next?";
  return {
    label: diff.newFailures.length > 0 ? "Address the new failures first" : "Continue from the improved baseline",
    why: diff.newFailures.length > 0
      ? "New failures block trust in the comparison, even if the score improved elsewhere."
      : "The comparison is trending in the right direction, so the next move is to keep the workflow tight and repeatable.",
    command: buildStartCommand(diff.target, chatPrompt),
    chatPrompt,
  };
}
