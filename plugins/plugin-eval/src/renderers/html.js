function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\"", "&quot;");
}

function renderList(items) {
  if (items.length === 0) {
    return "<p>None.</p>";
  }
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderOptionalList(items, emptyLabel = "None.") {
  return renderList(Array.isArray(items) && items.length > 0 ? items : [emptyLabel]);
}

function renderChecks(checks) {
  if (checks.length === 0) {
    return "<p>No checks recorded.</p>";
  }

  return `<ul>${checks
    .map(
      (check) =>
        `<li><strong>${escapeHtml(check.id)}</strong> [${escapeHtml(check.status)}] ${escapeHtml(check.message)}</li>`,
    )
    .join("")}</ul>`;
}

function renderMetrics(metrics) {
  if (metrics.length === 0) {
    return "<p>No metrics recorded.</p>";
  }

  return `<ul>${metrics
    .map(
      (metric) =>
        `<li><strong>${escapeHtml(metric.id)}</strong>: ${escapeHtml(metric.value)} ${escapeHtml(metric.unit)} (${escapeHtml(metric.band)})</li>`,
    )
    .join("")}</ul>`;
}

function renderDeductions(summary) {
  if (!summary.deductions || summary.deductions.length === 0) {
    return "<p>No deductions were applied.</p>";
  }

  return `<ul>${summary.deductions
    .map(
      (entry) =>
        `<li><strong>-${escapeHtml(entry.penalty)} points</strong> <code>${escapeHtml(entry.id)}</code> [${escapeHtml(entry.status)}/${escapeHtml(entry.severity)}] ${escapeHtml(entry.message)}</li>`,
    )
    .join("")}</ul>`;
}

function renderCategoryDeductions(summary) {
  if (!summary.categoryDeductions || summary.categoryDeductions.length === 0) {
    return "<p>No category deductions recorded.</p>";
  }

  return `<ul>${summary.categoryDeductions
    .map(
      (entry) =>
        `<li><strong>${escapeHtml(entry.category)}</strong>: -${escapeHtml(entry.totalPenalty)} points across ${escapeHtml(entry.checks)} check${entry.checks === 1 ? "" : "s"}</li>`,
    )
    .join("")}</ul>`;
}

function renderObservedUsage(observedUsage) {
  if (!observedUsage) {
    return "<p>No observed usage supplied.</p>";
  }

  const items = [
    `Samples: ${observedUsage.sampleCount}`,
    `Observed input avg: ${observedUsage.inputTokens.average}`,
    `Observed output avg: ${observedUsage.outputTokens.average}`,
    `Observed total avg: ${observedUsage.totalTokens.average}`,
  ];

  if (observedUsage.cachedTokens.total > 0) {
    items.push(`Observed cached avg: ${observedUsage.cachedTokens.average}`);
  }

  if (observedUsage.estimateComparison) {
    items.push(`Estimated active tokens: ${observedUsage.estimateComparison.estimatedActiveTokens}`);
    items.push(`Estimate delta: ${observedUsage.estimateComparison.deltaTokens}`);
    items.push(`Estimate ratio: ${observedUsage.estimateComparison.deltaRatio} (${observedUsage.estimateComparison.band})`);
  }

  return renderList(items);
}

function renderMeasurementPlan(plan) {
  if (!plan) {
    return "<p>No measurement plan available.</p>";
  }

  return `<p>${escapeHtml(plan.summary)}</p><ul>${plan.toolsets
    .map(
      (toolset) =>
        `<li><strong>${escapeHtml(toolset.label)}</strong> [${escapeHtml(toolset.priority)}] ${escapeHtml(toolset.goal)}</li>`,
    )
    .join("")}</ul>`;
}

function renderWorkflowGuide(guide) {
  if (!guide) {
    return "<p>No chat workflow guidance available.</p>";
  }

  const startHere = guide.startHere || {
    chatPrompt: guide.recommendedWorkflow.chatPrompt,
    routingExplanation: guide.recommendedWorkflow.summary,
    startCommand: guide.recommendedWorkflow.startCommand,
    firstCommand: guide.recommendedWorkflow.firstCommand,
  };

  return [
    `<p>${escapeHtml(guide.beginnerSummary)}</p>`,
    `<p><strong>Start with this chat request:</strong> ${escapeHtml(`"${startHere.chatPrompt}"`)}</p>`,
    `<p><strong>Why this path:</strong> ${escapeHtml(startHere.routingExplanation)}</p>`,
    `<p><strong>Quick local entrypoint:</strong> <code>${escapeHtml(startHere.startCommand)}</code></p>`,
    `<p><strong>Plugin Eval will run first:</strong> <code>${escapeHtml(startHere.firstCommand)}</code></p>`,
    "<h3>Other chat requests you can use</h3>",
    renderList(
      guide.entrypoints.map(
        (entry) => `${entry.label}: say "${entry.chatPrompt}" then run ${entry.firstCommand}`,
      ),
    ),
  ].join("");
}

function renderNextAction(nextAction) {
  if (!nextAction) {
    return "<p>No recommended next step.</p>";
  }

  return renderList([
    nextAction.label,
    `Why: ${nextAction.why}`,
    ...(nextAction.chatPrompt ? [`Chat request: "${nextAction.chatPrompt}"`] : []),
    ...(nextAction.command ? [`Local command: ${nextAction.command}`] : []),
  ]);
}

export function renderHtml(result) {
  if (result.kind === "workflow-guide") {
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Plugin Eval Start Here</title>
  </head>
  <body>
    <main>
      <h1>Plugin Eval Start Here: ${escapeHtml(result.target.name)}</h1>
      ${renderWorkflowGuide(result)}
      <h2>Recommended Next Step</h2>
      ${renderNextAction(result.nextAction)}
      <h2>Current Local State</h2>
      ${renderList([
        `Benchmark config present: ${result.workflowStatus.hasBenchmarkConfig ? "yes" : "no"}`,
        `Usage log present: ${result.workflowStatus.hasUsageLog ? "yes" : "no"}`,
      ])}
      <h2>Full Local Sequence</h2>
      ${renderList(result.startHere?.commands || [])}
    </main>
  </body>
</html>`;
  }

  if (result.kind === "measurement-plan") {
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Measurement Plan</title>
  </head>
  <body>
    <main>
      <h1>Measurement Plan: ${escapeHtml(result.target.name)}</h1>
      ${renderMeasurementPlan(result)}
      <h2>Recommended Next Step</h2>
      ${renderNextAction(result.nextAction)}
      <h2>Use From Codex Chat</h2>
      ${renderWorkflowGuide(result.workflowGuide)}
    </main>
  </body>
</html>`;
  }

  if (result.kind === "benchmark-template-init") {
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Benchmark Template Ready</title>
  </head>
  <body>
    <main>
      <h1>Benchmark Template Ready: ${escapeHtml(result.target.name)}</h1>
      <p>Config: ${escapeHtml(result.configPath)}</p>
      <h2>Recommended Next Step</h2>
      ${renderNextAction(result.nextAction)}
      <h2>Setup Questions To Ask First</h2>
      ${renderOptionalList(result.setupQuestions, "No setup questions provided.")}
      ${renderList(result.nextSteps || [])}
      <h2>Use From Codex Chat</h2>
      ${renderWorkflowGuide(result.workflowGuide)}
    </main>
  </body>
</html>`;
  }

  if (result.kind === "benchmark-run") {
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Benchmark Run</title>
  </head>
  <body>
    <main>
      <h1>Benchmark Run: ${escapeHtml(result.target.name)}</h1>
      <p>Mode: ${escapeHtml(result.mode)}</p>
      <p>Codex version: ${escapeHtml(result.codexVersion || "unknown")}</p>
      <p>Model: ${escapeHtml(result.config?.model || "")}</p>
      <p>Workspace source: ${escapeHtml(result.config?.workspaceSourcePath || "")}</p>
      <p>Run directory: ${escapeHtml(result.runDirectory || "")}</p>
      <h2>Recommended Next Step</h2>
      ${renderNextAction(result.nextAction)}
      <h2>Next Steps</h2>
      ${renderList(result.nextSteps || [])}
      <h2>Use From Codex Chat</h2>
      ${renderWorkflowGuide(result.workflowGuide)}
    </main>
  </body>
</html>`;
  }

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Plugin Eval Report</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f4faf8;
        --ink: #16302b;
        --accent: #0f766e;
        --panel: #ffffff;
        --border: #c8ece6;
      }
      body {
        font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
        background: radial-gradient(circle at top left, #d9fbe8 0, var(--bg) 40%);
        color: var(--ink);
        margin: 0;
        padding: 2rem;
      }
      main {
        max-width: 900px;
        margin: 0 auto;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(15, 118, 110, 0.08);
      }
      h1, h2 {
        margin-top: 0;
      }
      .summary {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
      }
      .card {
        padding: 1rem;
        border-radius: 16px;
        background: #f0fdfa;
        border: 1px solid var(--border);
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Plugin Eval Report: ${escapeHtml(result.target.name)}</h1>
      <section class="summary">
        <div class="card"><strong>Score</strong><div>${escapeHtml(result.summary.score)}/100</div></div>
        <div class="card"><strong>Grade</strong><div>${escapeHtml(result.summary.grade)}</div></div>
        <div class="card"><strong>Risk</strong><div>${escapeHtml(result.summary.riskLevel)}</div></div>
        <div class="card"><strong>Deductions</strong><div>-${escapeHtml(result.summary.scoreBreakdown?.totalDeductions || 0)}</div></div>
        <div class="card"><strong>Total Tokens</strong><div>${escapeHtml(result.budgets.total_tokens?.value || 0)}</div></div>
      </section>
      <h2>Why It Matters</h2>
      ${renderList(result.summary.whyBullets || [
        `Started at ${result.summary.scoreBreakdown?.startingScore || 100} and deducted ${result.summary.scoreBreakdown?.totalDeductions || 0} points.`,
        `Final score: ${result.summary.scoreBreakdown?.finalScore || result.summary.score}/100.`,
      ])}
      <h2>Fix First</h2>
      ${renderList((result.summary.fixFirst || []).map((item) => `${item.message} Why: ${item.why}`))}
      <h2>Recommended Next Step</h2>
      ${renderNextAction(result.nextAction)}
      <h2>Risk Assessment</h2>
      ${renderList(result.summary.riskReasons || [])}
      <h2>Deductions</h2>
      ${renderDeductions(result.summary)}
      <h2>Deductions By Category</h2>
      ${renderCategoryDeductions(result.summary)}
      <h2>Recommendations</h2>
      ${renderList(result.summary.topRecommendations)}
      <h2>Observed Usage</h2>
      ${renderObservedUsage(result.observedUsage)}
      <h2>Measurement Plan</h2>
      ${renderMeasurementPlan(result.measurementPlan)}
      <h2>Use From Codex Chat</h2>
      ${renderWorkflowGuide(result.workflowGuide)}
      <h2>Checks</h2>
      ${renderChecks(result.checks)}
      <h2>Metrics</h2>
      ${renderMetrics(result.metrics)}
    </main>
  </body>
</html>`;
}
