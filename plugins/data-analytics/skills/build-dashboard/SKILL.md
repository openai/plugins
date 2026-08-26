---
name: build-dashboard
description: "Build source-backed dashboards for monitoring performance, exploring drivers, or acting on product and business metrics. Use when the task needs a dashboard, scorecard, or monitoring view with clear metrics, filters, source definitions, and QA."
---

## Related Skills

Use $create-data-context only when the dashboard work explicitly asks to save data context or create, update, inspect, or repair a semantic layer.

Use $analyze-data-quality when dashboard metrics disagree or source freshness, grain, joins, or definitions could affect trust.

# Dashboard Building

Use this skill when the user needs a dashboard rather than a report, notebook-only analysis, spreadsheet, or transient chat summary. A good dashboard is summary-first, chart-led, scannable, and organized around what the audience needs to monitor, understand, or act on.

Clarify with the user when a missing input would materially change the dashboard brief, analysis, or recommendation. Otherwise make a reasonable assumption, state it, and proceed.

This skill owns the dashboard brief, delivery-mode selection, metric definitions, source expectations, layout logic, dashboard QA, and handoff. Delivery-specific mechanics belong in the selected dashboard specification.

## Skill Configuration

### Runtime Delivery Routing

If `mode = work_mode` is positively identified, do not visibly render the Data Analytics MCP artifact app or a generated web app, regardless of surface. Use a connected BI destination only when the user selected one. Otherwise automatically use `sites-app` when the full Sites create, checkpoint, and deployment lifecycle is callable: load the MCP artifact dashboard specification, build and validate the canonical manifest/snapshot, skip `render_artifact`, and invoke `$publish-artifact-to-sites`. Do not ask for another delivery choice or publish confirmation. Build portable HTML automatically when Sites is unavailable, publishing fails, or the user explicitly declines Sites. Use Streamlit only when the user explicitly asks for it. MCP servers and other callable tools remain valid data sources.

### Source Discovery And Verification

Use the relevant semantic layer as a starting map, not a boundary.

1. **Explore all possible sources.** Search every connected or provided source that could contain task-relevant data or change the interpretation. Within each structured-data source, run fresh catalog or metadata discovery for relevant schemas, datasets, tables, views, models, and metrics. Known sources, tables, dashboards, and semantic mappings are starting points, not stopping points.
2. **Compare duplicates and conflicts.** When sources overlap or disagree, compare ownership, freshness, definition, grain, coverage, and directness. Use the best authoritative source, or combine complementary sources when needed. Note material conflicts, explain why the selected source or sources control the answer, and verify selected data through live reads before concluding.

### Source Access Guardrail

Before querying sources, building artifacts, or drawing conclusions, determine whether the answer requires a specific source of truth.

If a required source is unavailable, stop that path. Tell the user what source is needed, ask them to make it available or provide a reviewed fallback, and do not treat weaker substitutes as equivalent.

If the missing source is only optional enrichment, continue with the strongest available evidence and label the gap when it materially affects the answer.

## Workflow

### 1. Define The Dashboard Brief

Understand who will use the dashboard, what they need to measure or monitor, which metrics matter, what surface it should live in, and what constraints could change the build.

Clarify only the inputs that materially affect the dashboard, such as the primary audience, measurement goal, metric scope, delivery surface, refresh expectations, required filters, access constraints, or sharing needs. Decide whether the dashboard is mainly for status monitoring, recurring operating review, or analytical exploration, because that changes the layout, filter design, and validation bar.

Use $gather-business-context when dashboard purpose, metric definitions, operating context, audience expectations, or existing dashboard conventions are not clear enough to design the dashboard well.

### 2. Select The Delivery Surface

Pick the first delivery surface that fits the user's need and available access. If the user specifies the destination or surface, use that instead of the default order.

For positively identified Work Mode on any surface, use this order:

1. Use a connected BI tool when the user explicitly selected it.
2. When the full Sites create, checkpoint, and deployment lifecycle is callable, automatically use `sites-app`; the dashboard request authorizes publishing without another confirmation.
3. Otherwise use HTML automatically for the dashboard handoff.

Do not call the visible `render_artifact` handoff in Work Mode, even if the tool is visible. `sites-app` reuses the artifact specification as a validated authoring and packaging contract.

On ChatGPT Desktop outside Work Mode, use the destination explicitly selected by the user; otherwise default to the MCP artifact app. Use HTML only when the user requests a portable file or after an MCP rendering failure. After a successful final MCP dashboard handoff, offer Sites as an optional coworker-sharing follow-up and invoke `$publish-artifact-to-sites` only after an explicit request or acceptance.

After the ChatGPT web Chat-mode stop gate has been explicitly overridden (`surface = chatgpt_web`, `mode = chat`), use a connected BI tool only when the user explicitly selected it; otherwise use portable HTML for a durable dashboard. Do not automatically publish to Sites or select the MCP artifact app in this branch.

For other environments, use a connected BI tool by default when one is identified from the request, current-run context, or explicit user preference. Otherwise use the MCP artifact app when it is available and appropriate, then HTML when the user needs a portable static dashboard or the richer surfaces are unavailable.

Use Streamlit only when the user explicitly asks for it or an existing Streamlit app must be changed.

Read the matching specification before building:

- `../../src/analytics-app-core.md` for shared MCP artifact mechanics, source safety, runtime behavior, and validation helpers.
- `specifications/bi-platform-dashboard.md` for BI platform dashboards.
- `specifications/mcp-artifact-dashboard.md` for MCP artifact dashboards and `sites-app` dashboards that reuse the same validated runtime.
- `specifications/html-dashboard.md` for portable self-contained HTML dashboards.
- `specifications/streamlit-dashboard.md` for Streamlit dashboards.

### 3. Gather And Validate The Data

Do the data work in this order:

- **Find the source path before rendering.** Source discovery is part of dashboard building, not optional enrichment. Identify the source path for the core dashboard metrics. Use `~~structured_data` when the dashboard needs data from a warehouse or another structured data source. Use context lanes such as `~~company_docs`, `~~team_communication`, or `~~dashboards_or_bi` when the dashboard needs business meaning, source-of-truth guidance, metric definitions, or requirements that are not captured in structured data alone.
- **Use durable dashboard data.** Validate the data before wiring it into the dashboard. Keep final extracts compact and aggregated unless a bounded detail table is part of the dashboard's purpose. Avoid final dashboards that depend on scratch or temporary tables.
- **Validate trust.** For straightforward dashboards, confirm the source, grain, freshness, and basic reconciliation needed to trust the displayed metrics. Use $analyze-data-quality when data trust is a material risk, such as a new source, recent backfill, complex join, or surprising result.
- **Resolve time and context anchors.** Before selecting metrics, establish any date anchor, comparison window, latest complete data date, source coverage, or authoritative artifact needed to shape the dashboard, such as a launch date, incident window, or campaign period. Use $gather-business-context when the prompt does not provide it. If still unclear, ask only when it would materially change the dashboard; otherwise state the assumption and shape queries around it.
- **Stop if source-backed data is unavailable.** Do not render dashboards from fallback, sample, scratch, or partially blocked data unless the user explicitly asked for a mockup. If the core dashboard data is not available, stop the build path and tell the user what source or access is needed. Do not claim a dashboard was created from real data when the source path is missing.

### 4. Define The Metric Model

**Select the metrics.**

When selecting dashboard metrics, classify the measurement object and choose a balanced metric model for that object. Do not use a fixed checklist. Identify which metric families are decision-relevant and which are intentionally out of scope.

Consider these metric families as prompts, not required sections:

- Reach: who or what is using the thing, eligible population, penetration, activation, adoption, coverage.
- Volume: events, usage, transactions, sessions, requests, units, throughput, frequency.
- Value: revenue, cost, margin, savings, conversion, retention value, productivity, business outcome.
- Quality: success, failure, reliability, latency, satisfaction, correctness, safety, support burden.
- Depth: repeat usage, intensity, feature mix, workflow completion, productionization, maturity, lifecycle stage.
- Mix: segment, customer type, geography, channel, model/product/version, plan, use case, cohort.
- Movement: trend, growth, seasonality, pre/post change, benchmark, target, forecast, leading indicators.
- Risk and constraints: data coverage, source freshness, known blind spots, capacity, compliance, operational limits.

**Build breadth without flattening the dashboard.**

Build enough metric breadth to cover every family that is relevant to the dashboard's measurement object and decision. Keep the default view hierarchical rather than exhaustive: lead with the primary outcome and the highest-signal drivers, then use sections, tabs, filters, detail tables, or supporting views for additional relevant metrics. A selected family can be represented by one or many KPIs, drivers, guardrails, or breakdowns, depending on what the user needs to monitor or diagnose.

Map the selected families into dashboard roles before building: hero metrics for the default view, diagnostic metrics for movement and breakdowns, guardrails for interpretation, and detail metrics for lookup or follow-up.

Let the decision determine the number of hero metric cards. Do not pad or truncate the set to four—or any preferred count. Give each card one distinct, decision-relevant headline metric. Use chips only for short comparison context tied directly to that headline, such as its prior-period value, target, or delta; move independent secondary measures into their own cards, charts, tables, narrative, or detail views. Keep coherent cards in the same strip; odd counts are valid because the artifact renderer balances rows responsively.

**Escalate when metric design is the hard part.**

Invoke $design-kpis when this baseline metric-family pass is not enough, such as when the dashboard needs a deeper metric framework, target-setting, formal KPI tradeoff analysis, or clearer definitions than this workflow can safely infer. Pass the dashboard brief, business context, source context, existing metric definitions, and constraints so the recommended metrics fit the audience and use case.

**Keep the data model consistent.**

Build from a reusable compact data model where possible instead of many slightly different tile queries. Keep date logic, filters, dimensions, and metric definitions consistent across cards, charts, and tables so numbers reconcile. Reuse shared metric definitions from the selected tool or semantic layer when available.

### 5. Design The Dashboard Layout

Make the default view useful before the viewer interacts. Arrange the dashboard from summary to detail: lead with the key status or primary KPI context, follow with movement over time, then show the breakdowns that explain the pattern, and put detail tables lower on the page when lookup or operational follow-up is needed.

Use global filters only when they materially update the dashboard-wide view. Prefer a few high-signal controls over a dense filter panel. Keep dashboards visual-heavy and neutral: short labels, direct metric names, sparse annotations, and minimal explanatory text on the main canvas. Use human-readable short date form in visible labels and freshness text; keep ISO timestamps for machine-readable source metadata.

Prefer human-readable short date forms in visible labels and tooltips unless the dashboard needs timestamps for operational precision.

### 6. Choose The Right Charts

Use $visualize-data when the dashboard needs chart selection, visual encoding, or chart polish. This skill should define what each chart needs to communicate; $visualize-data handles the detailed visual design.

Choose the simplest visual that answers the viewer's question. Use a chart when it makes the pattern easier to understand than text or a table.

Put metrics in the same chart only when comparing them directly makes sense. Otherwise, split them into separate charts, KPI cards, or tables.

Use the selected dashboard specification for exact schema, renderer, and interaction requirements.

### 7. Build And Validate In The Selected Surface

Build in the selected surface using its native patterns. Before handoff, check that the dashboard opens cleanly, filters work, charts render, numbers reconcile, access is handled clearly, and performance is acceptable.

Record the source or query path when it would be hard to rediscover later.

### 8. Hand Off The Dashboard

Include the dashboard link or local artifact path, source caveats, and any remaining operational steps. Keep routine check details in support artifacts. Do not list internal checks in the user-facing handoff unless a check failed, was unavailable, or produced a user-relevant caveat. For MCP artifact and `sites-app` dashboards, follow the validation and surface-specific handoff rules in `specifications/mcp-artifact-dashboard.md`. A Sites handoff must include the URL, snapshot timestamp, and a note that the data is a published snapshot rather than a live connection. After a successful final MCP app handoff in ChatGPT Desktop outside Work Mode, offer to publish the dashboard to Sites for coworker sharing; do not start that workflow until the user explicitly accepts.

## Dashboard Quality Bar

Before handoff, make sure the dashboard is usable as a measurement surface:

- The default view answers the primary audience question before the viewer interacts.
- Filters are few, meaningful, and work across the surfaces they claim to control.
- Cards, charts, and tables reconcile unless differences are clearly labeled.
- Charts answer clear questions with compatible metrics.
- Tables support lookup, comparison, or operational follow-up after the chart-led summary.
- The metric set is broad enough for the measurement object: it covers the relevant families with primary outcomes, important drivers, guardrails, and supporting breakdowns while keeping the default view usable.
- KPI cards are precisely defined: business-defined metrics include enough visible or nearby context for a reader to understand what is counted, over what window, and under what denominator or eligibility rule.
- Source freshness, access limits, and caveats are visible where they matter.
- The layout, labels, and performance work for the selected delivery mode.
- The selected dashboard specification's validation and render rules were followed.
