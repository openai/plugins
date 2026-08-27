# Earnings Dashboard Feedback Map

Use this when converting user feedback on a pre- or post-earnings dashboard into reusable skill changes.

## Where Feedback Lives

- `dashboard-builder` owns reusable presentation capabilities: single-page vs tabbed layout, sticky table of contents, responsive tables, issuer identity tiles, module rendering, module validation, and source/missing-evidence visibility.
- `earnings-deep-dive` owns post-print analytical depth: executive summary, beat/miss versus consensus, EPS quality and normalization, guidance deep dive, quarterly key metrics, growth trajectory, transcript Q&A quality, read-throughs, catalysts, contradictions, and filing/transcript/interview evidence.
- `earnings-preview` owns pre-print analytical depth: expectation bar, consensus/guide/whisper posture, last-quarter KPI baseline, quarterly key metrics, growth trajectory, guide credibility, peer/sector read-throughs, scenarios, and call-prep questions.
- `sector-context-overlay` should be used by the producer skill to pick nuanced company-specific KPIs, read-through relationships, and sector accounting conventions. It should not render dashboards.
- `financial-source-of-truth` owns evidence conflicts, source hierarchy, stale data flags, and precise absence labels when sources disagree or a value cannot be verified.

## Feedback Structure

Structure future dashboard feedback as:

1. `Analysis requirement`: what the producer skill must research or normalize.
2. `Visual/module requirement`: what the dashboard-builder must render.
3. `Coverage rule`: whether the requirement applies to pre-earnings, post-earnings, all PM dashboards, or only a sector.
4. `Evidence standard`: official filing/release, transcript, consensus source, price/market data, alternative data, management interview, or analyst-derived estimate.
5. `Quality gate`: what should fail, warn, or be called out as missing evidence.

## Cross-Skill Rules

- Put the quarter once in the hero/title area; do not duplicate it in a highlight tile.
- Highlight tiles must be PM-selective, not mechanically populated. Use the metric that changed the debate: revenue surprise %, normalized EPS beat, guide raise/cut, growth acceleration, margin inflection, backlog, capex guide, customer metrics, churn, NIM, reserves, production, ARR, or sector-specific KPI.
- When a growth rate, surprise %, or acceleration is the investor signal, use it as the highlighted value and place the absolute dollar amount in supporting detail. Do not default to the largest reported absolute number.
- Financial trend charts should use net margin only when net income is a fair recurring-profitability proxy. If EPS quality is distorted by below-the-line gains/losses, tax, FX, mark-to-market, equity-investment gains, restructuring, impairments, litigation, asset sales, or other one-time items, the producer skill should select operating margin or another source-backed profitability metric and pass `margin_metric`, `margin_label`, and `margin_rationale` to `dashboard-builder`.
- Positive-only chart scales should start at zero and show multiple readable tick/grid lines. Negative axis labels should only appear when the underlying data is negative, not because the renderer padded an all-positive scale.
- Company-specific quarterly key metrics belong in both pre-earnings and post-earnings dashboards. Pre-earnings uses the baseline and bar; post-earnings uses actuals, growth, consensus/guide delta, and PM read.
- Post-earnings dashboards should include a dense executive summary, granular beat/miss, EPS quality bridge, guidance deep dive, transcript Q&A map, read-through table, catalyst timeline, and missing-evidence list.
- Transcript modules should capture analyst, firm, topic, management response, short direct quote where available, and response quality. If the response deflects, say so.
