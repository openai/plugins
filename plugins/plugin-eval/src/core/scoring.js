const SEVERITY_WEIGHT = {
  error: 14,
  warning: 6,
  info: 1,
};

const STATUS_MULTIPLIER = {
  fail: 1,
  warn: 0.75,
  info: 0.25,
  pass: 0,
};

const GRADE_THRESHOLDS = {
  A: 93,
  B: 85,
  C: 70,
  D: 55,
};

const CATEGORY_PRIORITY = {
  manifest: 0,
  "skill-structure": 1,
  budget: 2,
  measurement: 3,
  "best-practice": 4,
  complexity: 5,
  readability: 6,
  "code-quality": 7,
};

const STATUS_PRIORITY = {
  fail: 0,
  warn: 1,
  info: 2,
  pass: 3,
};

function unique(items) {
  return [...new Set(items.filter(Boolean))];
}

export function summarizeChecks(checks) {
  return checks.reduce(
    (summary, check) => {
      summary.total += 1;
      summary[check.status] = (summary[check.status] || 0) + 1;
      summary[check.severity] = (summary[check.severity] || 0) + 1;
      return summary;
    },
    {
      total: 0,
      pass: 0,
      warn: 0,
      fail: 0,
      info: 0,
      error: 0,
      warning: 0,
    },
  );
}

function computeCheckPenalty(check) {
  const weight = SEVERITY_WEIGHT[check.severity] ?? 0;
  const multiplier = STATUS_MULTIPLIER[check.status] ?? 0;
  return weight * multiplier;
}

function deriveCheckWhy(check) {
  if (check.why) {
    return check.why;
  }

  if (check.category === "manifest") {
    return "Manifest issues reduce trust because Codex may not discover or represent the plugin correctly.";
  }

  if (check.category === "skill-structure") {
    return "Skill structure issues reduce trigger quality and make the skill harder to trust or maintain.";
  }

  if (check.category === "budget") {
    return "Budget pressure matters because always-loaded or frequently-loaded text can make the workflow feel expensive fast.";
  }

  if (check.category === "measurement") {
    return "Weak measurement means you are still steering with estimates instead of evidence.";
  }

  if (check.category === "best-practice") {
    return "Best-practice gaps usually do not break the workflow immediately, but they make the skill harder to understand and improve.";
  }

  if (check.category === "complexity") {
    return "Complexity findings matter because they increase review cost and make generated or helper code harder to change safely.";
  }

  if (check.category === "readability") {
    return "Readability issues slow engineers down during review, debugging, and follow-up edits.";
  }

  if (check.category === "code-quality") {
    return "Code-quality findings matter because helper scripts and supporting code are part of the user experience too.";
  }

  return "This finding affects confidence, clarity, or trust in the overall workflow.";
}

function buildDeductions(checks) {
  return checks
    .map((check) => ({
      id: check.id,
      category: check.category,
      severity: check.severity,
      status: check.status,
      message: check.message,
      penalty: computeCheckPenalty(check),
      remediation: check.remediation,
      source: check.source,
      ...(check.targetPath ? { targetPath: check.targetPath } : {}),
    }))
    .filter((entry) => entry.penalty > 0)
    .sort((left, right) => {
      if (right.penalty !== left.penalty) {
        return right.penalty - left.penalty;
      }
      return left.id.localeCompare(right.id);
    });
}

function buildCategoryDeductions(deductions) {
  const totals = new Map();
  for (const deduction of deductions) {
    const current = totals.get(deduction.category) || {
      category: deduction.category,
      totalPenalty: 0,
      checks: 0,
    };
    current.totalPenalty += deduction.penalty;
    current.checks += 1;
    totals.set(deduction.category, current);
  }

  return [...totals.values()].sort((left, right) => {
    if (right.totalPenalty !== left.totalPenalty) {
      return right.totalPenalty - left.totalPenalty;
    }
    return left.category.localeCompare(right.category);
  });
}

function rankActionableChecks(checks) {
  return checks
    .filter((check) => check.status === "fail" || check.status === "warn")
    .map((check) => ({
      ...check,
      penalty: computeCheckPenalty(check),
      why: deriveCheckWhy(check),
    }))
    .sort((left, right) => {
      if (right.penalty !== left.penalty) {
        return right.penalty - left.penalty;
      }
      if ((STATUS_PRIORITY[left.status] ?? 99) !== (STATUS_PRIORITY[right.status] ?? 99)) {
        return (STATUS_PRIORITY[left.status] ?? 99) - (STATUS_PRIORITY[right.status] ?? 99);
      }
      if ((CATEGORY_PRIORITY[left.category] ?? 99) !== (CATEGORY_PRIORITY[right.category] ?? 99)) {
        return (CATEGORY_PRIORITY[left.category] ?? 99) - (CATEGORY_PRIORITY[right.category] ?? 99);
      }
      return left.id.localeCompare(right.id);
    });
}

function summarizeFinding(check) {
  return {
    id: check.id,
    category: check.category,
    severity: check.severity,
    status: check.status,
    message: check.message,
    why: check.why,
    remediation: check.remediation,
    penalty: check.penalty,
    source: check.source,
    ...(check.targetPath ? { targetPath: check.targetPath } : {}),
  };
}

function buildWhyBullets(result, summary, failedErrors, warningSignals) {
  const bullets = [];

  if (failedErrors > 0) {
    bullets.push(`${failedErrors} failing error check${failedErrors === 1 ? "" : "s"} are driving the highest-confidence problems.`);
  }

  if (warningSignals > 0) {
    bullets.push(`${warningSignals} warning signal${warningSignals === 1 ? "" : "s"} still need cleanup before this feels polished.`);
  }

  if (summary.categoryDeductions.length > 0) {
    const topCategory = summary.categoryDeductions[0];
    bullets.push(`${topCategory.category} is the largest source of score loss at -${topCategory.totalPenalty} points.`);
  }

  if (
    ["heavy", "excessive"].includes(result.budgets?.trigger_cost_tokens?.band) ||
    ["heavy", "excessive"].includes(result.budgets?.invoke_cost_tokens?.band)
  ) {
    bullets.push("Active budget pressure is high enough that token cost may dominate the user experience.");
  } else {
    bullets.push("Budget pressure is not the dominant issue right now.");
  }

  if (result.observedUsage?.sampleCount) {
    bullets.push(`Observed usage is available from ${result.observedUsage.sampleCount} sample${result.observedUsage.sampleCount === 1 ? "" : "s"}.`);
  } else {
    bullets.push("No observed usage is attached yet, so budget conclusions are still based on static estimates.");
  }

  if (bullets.length === 0) {
    bullets.push(`Current grade is ${summary.grade} with ${summary.riskLevel} reported risk.`);
  }

  return bullets.slice(0, 5);
}

function buildRiskReasons({ score, failedErrors, warningSignals, deductions, checkSummary }) {
  const reasons = [];
  if (failedErrors > 0) {
    const examples = deductions
      .filter((entry) => entry.status === "fail" && entry.severity === "error")
      .slice(0, 3)
      .map((entry) => entry.id);
    reasons.push(
      `Contains ${failedErrors} failing error check${failedErrors === 1 ? "" : "s"}${
        examples.length > 0 ? ` (${examples.join(", ")})` : ""
      }.`,
    );
  }
  if (score < GRADE_THRESHOLDS.C) {
    reasons.push(`Overall score is below ${GRADE_THRESHOLDS.C}, which the evaluator treats as high risk.`);
  } else if (warningSignals > 0) {
    reasons.push(
      `Contains ${warningSignals} warning signal${warningSignals === 1 ? "" : "s"} that still need attention.`,
    );
  }
  if (checkSummary.info > 0 && reasons.length === 0) {
    reasons.push("No failing or warning checks were found; remaining items are informational only.");
  }
  if (reasons.length === 0) {
    reasons.push("No failing error checks and no warning signals were found.");
  }
  return reasons;
}

export function computeSummary(result) {
  const deductions = buildDeductions(result.checks);
  const penalty = deductions.reduce((total, entry) => total + entry.penalty, 0);

  const score = Math.max(0, Math.round(100 - penalty));
  const grade =
    score >= GRADE_THRESHOLDS.A
      ? "A"
      : score >= GRADE_THRESHOLDS.B
        ? "B"
        : score >= GRADE_THRESHOLDS.C
          ? "C"
          : score >= GRADE_THRESHOLDS.D
            ? "D"
            : "F";

  const failedErrors = result.checks.filter(
    (check) => check.status === "fail" && check.severity === "error",
  ).length;
  const warningSignals = result.checks.filter((check) => check.status === "warn").length;
  const riskLevel = failedErrors > 0 || score < 70 ? "high" : warningSignals > 0 || score < 85 ? "medium" : "low";
  const checkCounts = summarizeChecks(result.checks);
  const riskReasons = buildRiskReasons({
    score,
    failedErrors,
    warningSignals,
    deductions,
    checkSummary: checkCounts,
  });

  const topRecommendations = unique(
    result.checks
      .filter((check) => check.status === "fail" || check.status === "warn")
      .flatMap((check) => check.remediation)
      .slice(0, 5),
  );

  return enrichSummary(result, {
    score,
    grade,
    riskLevel,
    riskReasons,
    scoreBreakdown: {
      startingScore: 100,
      totalDeductions: penalty,
      finalScore: score,
      gradeThresholds: GRADE_THRESHOLDS,
    },
    checkCounts,
    deductions,
    categoryDeductions: buildCategoryDeductions(deductions),
    topRecommendations,
  });
}

export function enrichSummary(result, summary) {
  const deductions = Array.isArray(summary?.deductions) ? summary.deductions : buildDeductions(result.checks);
  const categoryDeductions = Array.isArray(summary?.categoryDeductions)
    ? summary.categoryDeductions
    : buildCategoryDeductions(deductions);
  const failedErrors = result.checks.filter(
    (check) => check.status === "fail" && check.severity === "error",
  ).length;
  const warningSignals = result.checks.filter((check) => check.status === "warn").length;
  const actionableChecks = rankActionableChecks(result.checks).map(summarizeFinding);
  const nextSummary = {
    ...summary,
    deductions,
    categoryDeductions,
  };

  return {
    ...nextSummary,
    whyBullets:
      Array.isArray(nextSummary.whyBullets) && nextSummary.whyBullets.length > 0
        ? nextSummary.whyBullets
        : buildWhyBullets(result, { ...nextSummary, categoryDeductions }, failedErrors, warningSignals),
    fixFirst:
      Array.isArray(nextSummary.fixFirst) && nextSummary.fixFirst.length > 0
        ? nextSummary.fixFirst
        : actionableChecks.slice(0, 3),
    watchNext:
      Array.isArray(nextSummary.watchNext) && nextSummary.watchNext.length > 0
        ? nextSummary.watchNext
        : actionableChecks.slice(3, 6),
  };
}
