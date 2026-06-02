import { createArtifact } from "./schema.js";
import { createMeasurementPlanNextAction } from "./presentation.js";

function hasMetric(result, id) {
  return result.metrics.some((metric) => metric.id === id);
}

function createToolset({
  id,
  label,
  priority,
  goal,
  why,
  signals,
  evidenceSources,
  starterPack,
}) {
  return {
    id,
    label,
    priority,
    goal,
    why,
    signals,
    evidenceSources,
    starterPack,
  };
}

export function buildMeasurementPlan(result) {
  const hasObservedUsage = Boolean(result.observedUsage?.sampleCount);
  const hasBudgetPressure =
    ["heavy", "excessive"].includes(result.budgets.trigger_cost_tokens?.band) ||
    ["heavy", "excessive"].includes(result.budgets.invoke_cost_tokens?.band);
  const hasCode =
    hasMetric(result, "ts_file_count") ||
    hasMetric(result, "py_file_count") ||
    result.target.kind === "directory";

  const toolsets = [
    createToolset({
      id: "token-usage-observer",
      label: "Token Usage Observer",
      priority: !hasObservedUsage || hasBudgetPressure ? "high" : "medium",
      goal: "Measure how many tokens the skill or plugin actually burns in representative runs.",
      why:
        "Static estimates are useful guardrails, but observed usage is what tells you whether a real workflow is affordable and whether caching or reasoning changes the picture.",
      signals: [
        "observed_usage_sample_count",
        "observed_input_tokens_avg",
        "observed_total_tokens_avg",
        "estimate_vs_observed_input_ratio",
      ],
      evidenceSources: [
        "Responses API usage logs",
        "Codex-like session exports",
        "JSONL traces captured from local benchmarking harnesses",
      ],
      starterPack: {
        manifestName: "token-usage-pack",
        focus: "Validate sample size, cold-start versus warm-cache behavior, and estimate drift over time.",
      },
    }),
    createToolset({
      id: "task-outcome-scorecard",
      label: "Task Outcome Scorecard",
      priority: "high",
      goal: "Measure whether the skill helps users finish the intended job with fewer retries and less cleanup.",
      why:
        "A low-token skill is still a miss if it fails the task, and a verbose skill may be worth it if it consistently improves first-pass success.",
      signals: [
        "task_success_rate",
        "first_pass_success_rate",
        "retry_rate",
        "human_override_rate",
      ],
      evidenceSources: [
        "Task run logs",
        "Structured user acceptance checklist",
        "Before/after comparison runs on the same prompts",
      ],
      starterPack: {
        manifestName: "task-outcomes-pack",
        focus: "Score success, retries, and manual intervention across a fixed prompt set.",
      },
    }),
    createToolset({
      id: "tool-call-audit",
      label: "Tool Call Audit",
      priority: result.target.kind === "plugin" ? "high" : "medium",
      goal: "Check whether the agent uses the right tools, arguments, and sequencing when the skill is active.",
      why:
        "For Codex plugins and many higher-agency skills, tool correctness is often the real determinant of user value.",
      signals: [
        "tool_call_success_rate",
        "invalid_tool_argument_rate",
        "recoverable_tool_failure_rate",
      ],
      evidenceSources: [
        "Tool invocation traces",
        "Recorded sessions",
        "Golden-path scenario replays",
      ],
      starterPack: {
        manifestName: "tool-audit-pack",
        focus: "Flag wrong tool selection, malformed args, and missing follow-up calls.",
      },
    }),
    createToolset({
      id: "latency-efficiency",
      label: "Latency And Efficiency",
      priority: hasBudgetPressure ? "high" : "medium",
      goal: "Track whether the skill speeds users up enough to justify its cost.",
      why:
        "DX improvements usually win when they reduce waiting or rework, not only when they reduce absolute token counts.",
      signals: [
        "p50_time_to_first_acceptable_answer_seconds",
        "p95_time_to_task_completion_seconds",
        "tokens_per_successful_run",
      ],
      evidenceSources: [
        "Benchmark harness timings",
        "Manual stopwatch runs on canonical tasks",
        "Responses API timestamps combined with usage logs",
      ],
      starterPack: {
        manifestName: "latency-efficiency-pack",
        focus: "Measure time-to-value and cost-per-success on a stable prompt suite.",
      },
    }),
    createToolset({
      id: "human-rubric-review",
      label: "Human Rubric Review",
      priority: "medium",
      goal: "Capture clarity, trust, and usefulness signals that automated checks will miss.",
      why:
        "The best skills often reduce confusion and editing effort in ways that do not show up in static lint-like checks.",
      signals: [
        "clarity_score_avg",
        "confidence_score_avg",
        "follow_up_question_rate",
      ],
      evidenceSources: [
        "Reviewer scorecards",
        "Team rubric sheets",
        "Annotated transcripts",
      ],
      starterPack: {
        manifestName: "human-rubric-pack",
        focus: "Collect 1 to 5 scores for clarity, trust, and edit burden across a small evaluator panel.",
      },
    }),
  ];

  if (hasCode) {
    toolsets.push(
      createToolset({
        id: "regression-suite",
        label: "Regression Suite",
        priority: "medium",
        goal: "Protect the repository behavior that the skill is supposed to improve.",
        why:
          "If a skill is meant to help coding workflows, outcomes should be paired with deterministic repo checks so quality gains do not come from cutting corners.",
        signals: [
          "test_pass_rate",
          "lint_pass_rate",
          "regression_escape_count",
        ],
        evidenceSources: [
          "Unit and integration test runs",
          "Coverage deltas",
          "Snapshot or golden-file checks",
        ],
        starterPack: {
          manifestName: "regression-pack",
          focus: "Blend repository test outcomes with evaluation-task success metrics.",
        },
      }),
    );
  }

  const recommendedToolsets = toolsets
    .filter((toolset) => toolset.priority === "high")
    .map((toolset) => toolset.id);

  const payload = {
    kind: "measurement-plan",
    createdAt: new Date().toISOString(),
    target: result.target,
    title: `Measurement plan for ${result.target.name}`,
    summary:
      "Combine cost, outcome, and trust signals so you can tell whether the skill or plugin is genuinely helping instead of only looking well-structured on paper.",
    recommendedToolsets,
    toolsets,
    artifact: createArtifact({
      id: "measurement-plan",
      type: "measurement-plan",
      label: "Measurement plan",
      description: "Recommended toolsets for measuring the real-world effect of this skill or plugin.",
      data: {
        recommendedToolsets,
        toolsets,
      },
    }),
  };
  payload.nextAction = createMeasurementPlanNextAction(payload);
  return payload;
}
