export function buildImprovementBrief(result) {
  const failingChecks = result.checks.filter((check) => check.status === "fail");
  const warningChecks = result.checks.filter((check) => check.status === "warn");
  const prioritized = [...failingChecks, ...warningChecks].slice(0, 8);
  const measurementGoals =
    result.measurementPlan?.recommendedToolsets?.length > 0
      ? result.measurementPlan.recommendedToolsets
      : [];

  return {
    title: `Improve ${result.target.name}`,
    target: result.target,
    summary: `Review actionable static findings and collect outcome evidence. The heuristic index ${result.summary.score}/100 (${result.summary.grade}) is not a calibrated quality grade; budget estimates and evidence gaps are reported separately.`,
    goals: result.summary.topRecommendations,
    measurementGoals,
    requiredFixes: failingChecks.slice(0, 5).map((check) => ({
      id: check.id,
      message: check.message,
      remediation: check.remediation,
    })),
    recommendedFixes: warningChecks.slice(0, 5).map((check) => ({
      id: check.id,
      message: check.message,
      remediation: check.remediation,
    })),
    suggestedPrompt: [
      `Use the skill-creator guidance to improve ${result.target.name}.`,
      `Preserve working behavior and use measured outcomes to justify changes; do not optimize solely for the static index.`,
      ...(measurementGoals.length > 0
        ? [`Define success measures with these toolsets: ${measurementGoals.join(", ")}.`]
        : []),
      ...prioritized.map((check) => `Address ${check.id}: ${check.message}`),
    ].join(" "),
  };
}
