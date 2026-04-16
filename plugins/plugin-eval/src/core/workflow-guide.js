import path from "node:path";

import { formatCommandPath, pathExists, relativePath } from "../lib/files.js";
import { createWorkflowGuideNextAction } from "./presentation.js";
import { resolveTarget } from "./target.js";

function shellQuote(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`;
}

function benchmarkConfigPath(target) {
  return path.join(target.path, ".plugin-eval", "benchmark.json");
}

function usageLogPath(target) {
  return path.join(target.path, ".plugin-eval", "benchmark-usage.jsonl");
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

function chatPromptForGoal(goal, target) {
  const label = targetLabel(target);
  if (goal === "analysis") {
    return `Give me a full analysis of this ${label}, including benchmark setup.`;
  }
  if (goal === "evaluate") {
    return `Evaluate this ${label}.`;
  }
  if (goal === "budget") {
    return `Explain the token budget for this ${label}.`;
  }
  if (goal === "measure") {
    return `Measure the real token usage of this ${label}.`;
  }
  if (goal === "benchmark") {
    return `Help me benchmark this ${label}.`;
  }
  return "What should I run next?";
}

function requestSignal(phrases, reason) {
  return {
    phrases,
    reason,
  };
}

function inferGoalFromRequest(requestText) {
  const normalized = String(requestText || "")
    .trim()
    .toLowerCase();

  if (!normalized) {
    return null;
  }

  const signals = [
    [
      "analysis",
      requestSignal(
        [
          "full analysis",
          "full eval",
          "full evaluation",
          "analyze this",
          "analysis of",
          "give me an analysis",
          "deep analysis",
          "deep dive",
        ],
        "it asks for a fuller analysis flow instead of only a single report or benchmark step",
      ),
    ],
    [
      "measure",
      requestSignal(
        [
          "measure the real token usage",
          "real token usage",
          "observed usage",
          "actual token usage",
          "measure token usage",
        ],
        "it asks for measured or observed token usage",
      ),
    ],
    [
      "benchmark",
      requestSignal(
        [
          "benchmark",
          "dry-run",
          "dry run",
          "starter scenario",
          "scenario",
        ],
        "it asks for a benchmark flow or scenario harness",
      ),
    ],
    [
      "budget",
      requestSignal(
        [
          "explain the token budget",
          "token budget",
          "context cost",
          "cost feels heavy",
          "why is this expensive",
        ],
        "it asks why the target feels expensive before measuring live usage",
      ),
    ],
    [
      "evaluate",
      requestSignal(
        [
          "evaluate",
          "audit",
          "review",
          "score",
          "report on",
          "why did this score",
          "what should i fix first",
          "fix first",
        ],
        "it asks for the overall evaluation report or prioritized findings from it",
      ),
    ],
    [
      "next",
      requestSignal(
        [
          "what should i run next",
          "what next",
          "where should i start",
          "where do i start",
          "start here",
          "i'm not sure",
        ],
        "it asks for the best next step instead of a specific workflow",
      ),
    ],
  ];

  for (const [goal, signal] of signals) {
    if (signal.phrases.some((phrase) => normalized.includes(phrase))) {
      return {
        goal,
        reason: signal.reason,
      };
    }
  }

  return null;
}

function workflowLabel(goal, target) {
  if (goal === "analysis") {
    return target.kind === "plugin" ? "Full Plugin Analysis" : "Full Skill Analysis";
  }
  if (goal === "evaluate") {
    return target.kind === "plugin" ? "Evaluate Plugin" : "Evaluate Skill";
  }
  if (goal === "budget") {
    return "Explain Token Budget";
  }
  if (goal === "measure") {
    return "Measure Real Token Usage";
  }
  if (goal === "benchmark") {
    return "Benchmark With Starter Scenarios";
  }
  return "Start Here";
}

function commandsForGoal(goal, target, status) {
  const commandTargetPath = formatCommandPath(target.path);
  const commandConfigPath = formatCommandPath(benchmarkConfigPath(target));
  const commandUsagePath = formatCommandPath(usageLogPath(target));

  if (goal === "analysis") {
    if (!status.hasBenchmarkConfig) {
      return [
        `plugin-eval analyze ${commandTargetPath} --format markdown`,
        `plugin-eval init-benchmark ${commandTargetPath}`,
        `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath}`,
      ];
    }

    if (!status.hasUsageLog) {
      return [
        `plugin-eval analyze ${commandTargetPath} --format markdown`,
        `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath}`,
      ];
    }

    return [
      `plugin-eval analyze ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
      `plugin-eval measurement-plan ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
    ];
  }

  if (goal === "evaluate") {
    return [`plugin-eval analyze ${commandTargetPath} --format markdown`];
  }

  if (goal === "budget") {
    return [`plugin-eval explain-budget ${commandTargetPath} --format markdown`];
  }

  if (goal === "measure") {
    if (!status.hasBenchmarkConfig) {
      return [
        `plugin-eval init-benchmark ${commandTargetPath}`,
        `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath}`,
        `plugin-eval analyze ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
      ];
    }

    if (!status.hasUsageLog) {
      return [
        `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath}`,
        `plugin-eval analyze ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
      ];
    }

    return [
      `plugin-eval analyze ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
      `plugin-eval measurement-plan ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
    ];
  }

  if (goal === "benchmark") {
    if (!status.hasBenchmarkConfig) {
      return [
        `plugin-eval init-benchmark ${commandTargetPath}`,
      ];
    }

    return [
      `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath}`,
    ];
  }

  if (status.hasUsageLog) {
    return [
      `plugin-eval analyze ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
      `plugin-eval measurement-plan ${commandTargetPath} --observed-usage ${commandUsagePath} --format markdown`,
    ];
  }

  if (status.hasBenchmarkConfig) {
    return [
      `plugin-eval benchmark ${commandTargetPath} --config ${commandConfigPath}`,
    ];
  }

  return [`plugin-eval analyze ${commandTargetPath} --format markdown`];
}

function summaryForGoal(goal, target, status) {
  const label = targetLabel(target);

  if (goal === "analysis") {
    if (status.hasUsageLog) {
      return `Use this when you want the full report plus measured usage follow-through for this ${label}.`;
    }
    if (status.hasBenchmarkConfig) {
      return `Use this when you want the full report and already have benchmark scaffolding ready for this ${label}.`;
    }
    return `Use this when you want the full report and starter benchmark setup for this ${label} in one guided path.`;
  }

  if (goal === "evaluate") {
    return `Start here when you want the overall report for a ${label}, including structure, budgets, and code checks.`;
  }

  if (goal === "budget") {
    return `Use this when the main question is why the ${label} feels expensive before you collect any live measurements.`;
  }

  if (goal === "measure") {
    return status.hasUsageLog
      ? `You already have a local usage log, so the next step is to fold those real measurements back into the report.`
      : `Use this when you want real token usage instead of only the static estimate.`;
  }

  if (goal === "benchmark") {
    return `Use this when you want starter scenarios and a repeatable real-Codex benchmark run for this ${label}.`;
  }

  if (status.hasUsageLog) {
    return "You already collected benchmark output, so the best next step is to analyze the real usage and decide what to improve.";
  }

  if (status.hasBenchmarkConfig) {
    return "You already have a benchmark config, so the next step is to run it.";
  }

  return `If you are new to plugin-eval, start with the overall evaluation report for this ${label}.`;
}

function inferRecommendedGoal(status, explicitGoal) {
  if (explicitGoal && explicitGoal !== "next") {
    return explicitGoal;
  }

  if (status.hasUsageLog) {
    return "measure";
  }

  if (status.hasBenchmarkConfig) {
    return "benchmark";
  }

  return "evaluate";
}

function createEntry(goal, target, status) {
  const commandTargetPath = formatCommandPath(target.path);
  const chatPrompt = chatPromptForGoal(goal, target);
  const commands = commandsForGoal(goal, target, status);
  return {
    id: goal,
    label: workflowLabel(goal, target),
    chatPrompt,
    summary: summaryForGoal(goal, target, status),
    firstCommand: commands[0],
    commands,
    startCommand: `plugin-eval start ${commandTargetPath} --request ${shellQuote(chatPrompt)} --format markdown`,
  };
}

export async function buildWorkflowGuide(targetPath, options = {}) {
  const target = await resolveTarget(targetPath);
  const status = {
    hasBenchmarkConfig: await pathExists(benchmarkConfigPath(target)),
    hasUsageLog: await pathExists(usageLogPath(target)),
  };
  const requestMatch = inferGoalFromRequest(options.request || "");

  const entries = [
    createEntry("analysis", target, status),
    createEntry("evaluate", target, status),
    createEntry("budget", target, status),
    createEntry("measure", target, status),
    createEntry("benchmark", target, status),
    createEntry("next", target, status),
  ];

  const requestedGoal = options.goal || requestMatch?.goal || null;
  const recommendedGoal = inferRecommendedGoal(status, requestedGoal);
  const recommendedWorkflow = entries.find((entry) => entry.id === recommendedGoal) || entries[0];
  const routedRequest = options.request || recommendedWorkflow.chatPrompt;
  const commandTargetPath = formatCommandPath(target.path);
  const routingExplanation = requestMatch
    ? `Plugin Eval routed "${options.request}" to ${recommendedWorkflow.label} because ${requestMatch.reason}.`
    : `Plugin Eval recommended ${recommendedWorkflow.label} from the current local state for this ${targetLabel(target)}.`;

  const payload = {
    kind: "workflow-guide",
    createdAt: new Date().toISOString(),
    target: {
      ...target,
      relativePath: relativePath(process.cwd(), target.path),
    },
    requestedGoal,
    requestedChatPrompt: options.request || null,
    requestRouting: requestMatch,
    recommendedWorkflowId: recommendedWorkflow.id,
    recommendedWorkflow,
    workflowStatus: status,
    beginnerSummary:
      "Start with a natural chat request, then let plugin-eval show the exact local command sequence behind it.",
    startHere: {
      chatPrompt: routedRequest,
      label: recommendedWorkflow.label,
      summary: recommendedWorkflow.summary,
      routingExplanation,
      startCommand: `plugin-eval start ${commandTargetPath} --request ${shellQuote(routedRequest)} --format markdown`,
      firstCommand: recommendedWorkflow.firstCommand,
      commands: recommendedWorkflow.commands,
    },
    entrypoints: entries,
    nextSteps: recommendedWorkflow.commands,
  };
  payload.nextAction = createWorkflowGuideNextAction(payload);
  return payload;
}
