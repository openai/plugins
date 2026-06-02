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
    summary: `Raise the evaluation from grade ${result.summary.grade} (${result.summary.score}/100) with a focus on the highest-signal structural and budget issues first.`,
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
      `Keep the structure compact and move bulky details into references or scripts.`,
      ...(measurementGoals.length > 0
        ? [`Define success measures with these toolsets: ${measurementGoals.join(", ")}.`]
        : []),
      ...prioritized.map((check) => `Address ${check.id}: ${check.message}`),
    ].join(" "),
  };
}
