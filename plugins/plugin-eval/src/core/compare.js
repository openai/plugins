import { createComparisonNextAction } from "./presentation.js";

export function compareResults(before, after) {
  const beforeFailures = new Set(
    before.checks.filter((check) => check.status === "fail").map((check) => check.id),
  );
  const afterFailures = new Set(
    after.checks.filter((check) => check.status === "fail").map((check) => check.id),
  );

  const resolvedFailures = [...beforeFailures].filter((id) => !afterFailures.has(id));
  const newFailures = [...afterFailures].filter((id) => !beforeFailures.has(id));

  const payload = {
    kind: "comparison",
    createdAt: new Date().toISOString(),
    target: after.target,
    scoreDelta: after.summary.score - before.summary.score,
    gradeBefore: before.summary.grade,
    gradeAfter: after.summary.grade,
    riskBefore: before.summary.riskLevel,
    riskAfter: after.summary.riskLevel,
    budgetDelta: {
      trigger_cost_tokens:
        (after.budgets.trigger_cost_tokens?.value || 0) - (before.budgets.trigger_cost_tokens?.value || 0),
      invoke_cost_tokens:
        (after.budgets.invoke_cost_tokens?.value || 0) - (before.budgets.invoke_cost_tokens?.value || 0),
      deferred_cost_tokens:
        (after.budgets.deferred_cost_tokens?.value || 0) - (before.budgets.deferred_cost_tokens?.value || 0),
    },
    resolvedFailures,
    newFailures,
    beforeSummary: before.summary,
    afterSummary: after.summary,
  };
  payload.nextAction = createComparisonNextAction(payload);
  return payload;
}
