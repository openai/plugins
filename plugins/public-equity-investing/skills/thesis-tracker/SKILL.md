---
name: thesis-tracker
description: Use when building or updating Public Equity Investing thesis trackers. Do not use for generic news summaries, trade pitches, or first-pass memos.
---

# Thesis Tracker

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Portfolio Models & Trackers`
- `Internal Research`
- `Earnings Transcripts & Events`
- `Market Data & Estimates`
- `Company Filings & IR`

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

For an update to an attached or existing thesis tracker, treat a polished XLSX thesis tracker workbook as the resolved presentation surface unless the user requests another format, a quick/no-file answer, or an HTML review package. Ask only remaining material choices that change the analysis.

## Purpose

Maintain a falsifiable public-equity-investing thesis over time. Preserve original underwriting, append new evidence, and translate each update into company-thesis status, security-thesis readiness, KPI/estimate/catalyst movement, model/valuation impact, risk/reward, and PM action.

## Non-negotiables

- Preserve user data append-only by default; never delete, collapse, or rewrite prior thesis data unless explicitly asked.
- Prefer user prompt, files, existing trackers/models/memos, and connected context before public sources. Use web/current sources only when needed and cite facts.
- Label source type, as-of date, reliability, stale data, assumptions, judgments, and possible MNPI/restricted or redistribution-sensitive material.
- Separate company-thesis status, security-thesis readiness, and position action; better fundamentals can coexist with worse forward risk/reward, and incomplete market data can block a stock conclusion.
- Track confirming and disconfirming evidence. Do not treat price action as proof; decompose it into fundamentals, estimates, multiple/spread, factor/sector, positioning, liquidity, rates/macro, and options effects.
- Convert narrative into prioritized falsifiable pillars, KPIs, thresholds, catalysts, kill criteria, and action triggers. Retain numeric weights or scores only when inherited from an existing tracker or explicitly requested; do not create scoring charts that imply false precision.
- For a material security-thesis update, attempt to retrieve current public price and basic market context when accessible, record the as-of timestamp and source, and label any unavailable consensus, internal model, ownership, or portfolio inputs as decision-blocking gaps.
- Identify whether each action threshold is an `Inherited threshold`, `Draft threshold for PM confirmation`, or `Approved monitoring rule`; never present analyst-created falsifiers as approved mandate rules.
- Every material update must state impact on assumptions/model lines, valuation/downside, conviction, sizing/hedge, decision timing, and next proof point.
- Avoid vague "monitor" language unless paired with exact metric, threshold, source, date, and action.

## When To Load References

- Missing/partial/conflicting context or source sensitivity: `references/intake-and-source-priority.md`.
- Full build/update sequence: `references/workflow-core.md`.
- Tables, fields, statuses, scoring, or spreadsheet shape: `references/thesis-schema.md`.
- CSV/XLSX scaffold helper: `references/tracker-materializer.md`.
- Investor mandate or sector-specific nuance: `references/investor-sector-overlays.md`.
- Final memo/dashboard/table formats: `references/output-templates.md`.
- Final PM judgment, compliance, drift, and red-team checks: `references/quality-guardrails.md`.

## Operating Modes

| Mode | Default behavior |
|---|---|
| Blank template | No ticker/thesis/files: create institutional shell plus minimal intake; invent no facts. |
| Ticker-only | Build preliminary shell from objective facts; label thesis fields as inferred/requires house-view confirmation. |
| Existing thesis | Extract original thesis, variant view, pillars, KPIs, catalysts, kill criteria, risks, and open questions. |
| Tracker update | Append evidence, preserve prior data, update statuses, and add changelog. |
| Post-earnings | Map release/transcript/guidance/estimate changes to pillars and decision impact. |
| Portfolio review | Triage by deterioration, improvement with worse risk/reward, catalysts, and required decisions. |
| Sell-side | Tie facts to rating, target price, estimates, valuation, client debate, and risks. |
| Long/short | Emphasize variant perception, setup, crowding/borrow/squeeze, catalyst path, sizing, and hedges. |
| Equity-risk credit signal / Credit Markets handoff | Track only credit facts that change common-equity downside, sizing, hedge, or re-underwrite status; route credit-security, covenant-package, restructuring, and recovery analysis to Credit Markets. |

## Workflow Contract

1. Define context: issuer/security, direction, mandate, horizon, exposure, benchmark/peers, rating/target/cost basis if supplied, and output need.
2. Inventory sources: name/type/as-of/reliability/coverage/limitations; retrieve current price and basic public market context when accessible; show missing or stale consensus, model, portfolio, and tracker data.
3. Preserve original underwriting: thesis, variant perception, market setup, valuation anchor, scenarios, catalysts, KPIs, risks, kill criteria, position implication, open diligence.
4. Decompose into prioritized falsifiable pillars with baseline, expected path, confirm/warning/break thresholds, timing, model linkage, action linkage, and next proof point. Use numeric weights only when source-backed or requested, and label their origin.
5. Append evidence ledger rows with fact, source/date, pillar, confirm/disconfirm signal, magnitude, quality, model/valuation/confidence/action impact, follow-up, and owner.
6. Update KPIs, catalysts, estimate revisions, and market-implied setup versus house view, guidance, consensus, buyside expectations if supplied, thresholds, peers, and prior periods.
7. Translate into model/valuation/risk-reward: near-term vs structural changes, affected model lines, fair value/target/downside/spread or recovery read-through where relevant to common equity, and hurdle clearance. If current price or valuation inputs remain unavailable, label the security thesis not decision-grade rather than inferring risk/reward.
8. Assess company-thesis status separately from security-thesis readiness: strengthening, intact, watch, impaired, broken, changed, untested, or retired for fundamentals; ready, conditional, re-underwrite, or not decision-grade for the security call. Explain movement with evidence, not price action alone. Reconcile aggregate status to core pillars: do not label the company thesis `Watch` when an inherited core pillar is `Impaired` without an explicit evidence-supported override rationale; when multiple core pillars are `Impaired`, default aggregate company-thesis status to `Impaired`.
9. Recommend action: add/press, hold, trim, exit/cover, upgrade/downgrade, hedge/pair, wait, re-underwrite, update model, diligence, or escalate. For every proposed hold/trim/exit threshold, show threshold origin and approval status.
10. Red-team: strongest opposing view, evidence for it, what would make it right, what changes the recommendation, open questions, next review date, changelog.
11. For XLSX delivery, keep the cover and key monitoring sheets readable at ordinary zoom: prefer compact decision-facing columns, move detail into the evidence ledger, freeze key identifier columns, render every sheet before delivery, and repair excessively wide or clipped tables. Keep full action-rule matrices and full diligence/gap registers on their dedicated tabs; the `Cover` tab should summarize action posture, top blockers, and next gate rather than duplicate them. Do not include a scored pillar chart unless the scoring method is inherited or explicitly requested.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: prior thesis extraction, evidence/KPI updates, valuation impact, action log, and red-team review. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Default Output

Unless the user explicitly asks for a short summary or one section, produce a full decision-grade thesis update:

1. Thesis status and recommendation.
2. Company-thesis status versus security-thesis readiness, including missing inputs that limit the stock call.
3. What changed versus prior house view, consensus, and market setup.
4. Pillar tracker with priority or inherited weight, status, latest evidence, signal, next test.
5. KPI / estimate / catalyst update.
6. Model, valuation, downside, and risk/reward impact.
7. Action thresholds with origin/approval status and decision log/changelog.
8. Red-team, kill criteria, open questions, sources/as-of dates.

For tracker builds or updates, lead with a polished XLSX thesis tracker workbook when XLSX is available; use an HTML report only when the user requests it or the task is a presentation-oriented review package rather than a live tracker update. Run `python scripts/materialize_thesis_tracker.py [tracker_input.json] --output-dir output` when its structured CSV/XLSX scaffold is useful, then apply workbook formatting and render-and-inspect QA for the final workbook. The helper writes a new CSV support bundle and optional XLSX when `openpyxl` is installed; it does not edit existing trackers in place. XLSX outputs should start with a compact `Cover` tab separating company-thesis status, security-thesis readiness, position action, market-data as-of, next catalyst, evidence gaps, and action thresholds. CSV/JSON support files should not be the lead user-facing artifact unless explicitly requested.

For optional dashboard handoffs requested by the user or needed for a reusable presentation view, use `references/DASHBOARD_PACK.md`. `thesis-tracker` owns thesis status, evidence ledger, KPI/catalyst monitoring, decision log, and update cadence; `dashboard-builder` owns the shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV/run-log support files behind the HTML dashboard unless explicitly requested.

## Adjacent Routing

Use or recommend adjacent public-equity-investing skills rather than duplicating work when the primary need is source hierarchy, financial normalization, model tie-out/update, scenario sensitivity, earnings preview/deep dive, new pitch, hedge/sizing, event/credit/macro analysis, or memo/deck QC.

## When To Invoke Support

Load `shared/support-layer-routing-contract.md` when support services are needed. Use `financial-source-of-truth` before changing pillar status based on new evidence. Use `financials-normalizer` or `excel-data-cleaner` before tracker updates rely on messy KPI, consensus, ownership, market-data, or model-output tables. Use `equity-model-update` and `model-audit-tieout` for estimate/model changes. Use `deck-report-qc` and `style-guide-adapter` only for circulation packets. Support files stay secondary to the tracker workbook, HTML dashboard/report, or decision-grade update.

## Language Standard

Write like a top PM or research MD: concise, evidence-weighted, and action-oriented. Call out when the business thesis improved but the security thesis worsened because expectations rerated, and when headline results look good but evidence quality or cash conversion is poor.

## Public Equity PM Judgment Layer

For substantial thesis updates, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Portfolio Monitoring Mode is first-class. Every update should classify the stock as `add`, `press`, `hold`, `trim`, `exit`, `hedge`, `wait for proof`, or `re-underwrite`.

Required PM judgment:
- Separate company-thesis status from security-thesis readiness, stock action, and portfolio role.
- Make the operating model explicit: PM owner, analyst owner, evidence owner, KPI owner, model owner, decision authority, review cadence, post-catalyst update SLA, escalation triggers, next review gate, active weight, portfolio role, status, action threshold, and append-only decision log.
- Include benchmark weight, active weight, sector/factor exposure, ETF ownership, passive-flow sensitivity, index inclusion/deletion/rebalance risk, liquidity, crowding, and priced-in status when relevant.
- Strengthen market setup into consensus, buyside whisper, what is priced, what is ignored, and where the PM edge sits.
- Maintain a diligence ladder: filings/transcripts, KPI history, competitor checks, customer/channel checks if supplied, management credibility, accounting quality, ownership/flow setup, sell-side consensus, and variant debate.
