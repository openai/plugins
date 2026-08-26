---
name: earnings-preview
description: Use when preparing full pre-earnings preview reports with executive summary, expectation bar, guidance credibility, KPI dashboard, scenarios, and call questions. Do not use after results or for short summaries unless the user explicitly asks for a summary/short version.
---

# Earnings Preview

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Earnings Transcripts & Events`
- `Company Filings & IR`
- `Market Data & Estimates`
- `Internal Research`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing` router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For an explicit pre-earnings preview, full preview report, or reusable/source-heavy pre-print package, the default resolves the presentation surface to a polished standalone HTML pre-earnings report unless the user requests an alternate surface, a quick/no-file answer, or workbook/model output. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus; in non-interactive runs, default to the HTML pre-earnings report and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

Produce a full, decision-grade pre-print report by default: executive summary first, then what the market expects, what can move the stock, what must be answered on the call, and what evidence is missing.

## Route

- `full preview report`: default route for any pre-earnings preview request. For an explicit pre-earnings preview, full preview report, or reusable/source-heavy pre-print package, produce a polished standalone HTML pre-earnings report following `../../shared/html-artifact-standard.md`; let the named investor question determine the hierarchy. Always surface the expectation bar, stock-reaction drivers, key evidence, call watch items, source posture, and missing evidence. Add KPI trajectories, guidance credibility, peer/sector read-throughs, macro context, market events, reaction/options context, bull/base/bear cases, and extended call questions only when relevant and source-supported.
- `explicit short summary`: use only when the user explicitly asks for `summary`, `short`, `quick read`, `one-pager`, `top things to watch`, or similar compression. Do not maintain this as a separate tear-sheet artifact; pare back the full preview report while preserving freeze time, source posture, key bar numbers, top debates, call questions, and missing evidence.
- `standardized dashboard`: use only when the user explicitly asks for a standardized dashboard, reusable dashboard template, PM cockpit, tabbed dashboard, or structured payload-driven render. Keep this skill as the analysis owner and hand the resulting `public_equity_investing_dashboard.v1` payload to `dashboard-builder`. Use `references/DASHBOARD_PACK.md` for module mapping.
- `deterministic export pack`: only when requested or plan-driven; validate local inputs, run packaged scripts, and write support artifacts such as `preview_note.md`, `exports.xlsx`, `exports/*.csv`, `qa_report.*`, and `run_manifest.json`. The workbook or rendered dashboard/report is the hero artifact; CSV/JSON/Markdown sidecars are support/audit files unless explicitly requested.

Load `references/REFERENCE_ROUTER.md` first, then only the smallest reference needed for the chosen route.

## Non-Negotiables

- State freeze time and source timestamps for consensus, whisper, options, price/reaction, and other time-sensitive inputs.
- Never fabricate numbers, dates, guidance, option data, peer read-throughs, or whisper color.
- Separate company/SEC/IR facts, consensus, whisper, analyst inference, user assumptions, and web fallback.
- Keep GAAP/non-GAAP labels, units, scale, period mapping, and KPI definitions explicit.
- Identify EPS-quality landmines before the print: tax rate, share count, equity-investment marks, FX, asset sales, impairments, restructuring, litigation, non-operating income/expense, and any mismatch between GAAP EPS, adjusted EPS, and consensus basis.
- Include the last reported baseline and the consensus/guide bar where sourced. Include quarterly key metrics and growth trajectory when they sharpen the investor question or the stock-reaction setup rather than as mandatory display inventory.
- For dashboard handoffs, include the earnings visualization pack only when source-backed data exists: quarterly revenue, gross profit, net income, and the best source-backed profitability margin history; estimated EPS versus actual EPS for the past five quarters; and equity-price history annotated with material market events. Omit any chart whose required series is missing, stale, or not comparable, and surface that gap in `missing_evidence`.
- Treat the margin line in financial trend charts as part of the pre-print risk setup. Default to net margin only when net income is a fair recurring-profitability proxy. Prefer operating margin or another issuer-specific source-backed margin when net income has been distorted by tax, equity-investment marks, FX, asset sales, impairments, restructuring, litigation, or other non-operating items. State the selected `margin_metric`, `margin_label`, and `margin_rationale` in dashboard payloads when using a line other than net margin.
- Rank dashboard highlights by investor salience rather than mechanical size. If a growth rate, acceleration, surprise %, guide delta, backlog, or normalized metric is what matters for the stock, use that as the highlighted value and put the absolute value in the supporting detail.
- Include major news coverage and market events when they can affect the earnings setup, guide credibility, estimate bar, multiple, positioning, or call questions. Scan the last quarter, the last twelve months, and forward-looking anticipated events; cite every event and label uncertain windows.
- Use primary company/SEC/IR and connected sources before general web; label fallback sources.
- Do not imply MNPI or confidential whisper data; weak whisper support becomes qualitative setup language.
- Without sourced implied move, relevant positioning/context, and adequate consensus or whisper evidence for the stated question, provide an earnings setup and reaction framework rather than a trade-ready position instruction. Use `Wait for proof`, `Monitor`, or similarly evidence-calibrated language where appropriate.
- Treat an options-implied move as an earnings reaction bar only when the contract tenor reasonably isolates the earnings event. If the available expiry includes substantial pre-event trading time or another material catalyst window, label the metric as `expiry-tenor volatility context`, explain the limitation, and do not feature it as a first-read earnings-move tile unless the limitation is immediately prominent.
- Do not create optional exports or support files unless requested or plan-driven. The workflow-resolved standalone HTML pre-earnings report is the planned hero artifact for an explicit full preview request.
- Do not shorten the default preview just because some inputs are missing; keep full analysis of the investment question and label unavailable optional modules or inputs explicitly.

## Workflow

1. Classify route. Default to `full preview report` unless the user explicitly asks for a summary/short format.
2. Anchor the preview quarter; map `t`, `t-1`, `t-4`, and `t-8`.
3. Freeze sources/timestamps and normalize units, GAAP/non-GAAP basis, KPI definitions, and source posture.
4. Identify 3-6 stock-moving KPIs and build the expectation bar: consensus, guide, whisper if sourced, prior setup, key-metric baseline, growth trajectory, EPS-quality watch items, and base framing.
5. Add guidance credibility, peer read-throughs, reaction/options, macro/sector context, and major news/market events when relevant and sourced. Separate company-specific events from peer, macro, regulatory, legal, FX/rates, commodity, industry, and upcoming catalyst events.
6. Build supportable bull/base/bear framing and write only decision-relevant call questions with listen-fors and falsifiers. Convert material news/event items into call questions when they create a contradiction or open diligence item.
7. Run QA for executive-summary coverage, freeze time, period consistency, source labels, units/scale, chart/display unit agreement, readable citation placement, cited event claims, missing evidence, and unresolved placeholders.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: source and consensus freeze, KPI/guide bar, peer/macro/reaction context, scenarios, call questions, and QA. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Deterministic Contract

Scripts are local materializers; they do not fetch data or replace analyst judgment.

- Required inputs: `company_master.csv`, `fiscal_period_index.csv`, `reported_financials.csv`, `kpi_timeseries.csv`, `consensus_estimates.csv`.
- Required for full scripted pack: `guidance_history.csv` and canonical event file `event_calendar.csv` can be empty but must exist with headers.
- Optional inputs: `whisper_estimates.csv`, `price_returns.csv`, `options_snapshot.csv`, `qual_notes.csv`, `scenario_assumptions.csv`.
- Schema source: `references/SCHEMAS.md` plus `assets/plan_schema.json`.
- Generated Markdown support notes must not contain unresolved bracket tokens, `TODO`, or unfinished placeholders.
- `exports.xlsx` starts with `Cover`, a dashboard sheet summarizing company/ticker, preview period, freeze time, workbook mode, warnings, consensus bar, bull/base/bear revenue and EPS, KPI dashboard row counts, call watch item, input file count, and workbook map.

## Handoffs

Use `financial-source-of-truth` for evidence conflicts, `financials-normalizer` for messy tables, `scenario-sensitivity-generator` for deeper cases, `dashboard-builder` for responsive pre-earnings dashboard rendering, `earnings-deep-dive` after the print, `equity-model-update` for model refreshes, `long-short-pitch` for trade expression, and `memo-builder` for formal memos.

## HTML Guidance

For a substantive HTML full preview report, load `../../shared/html-artifact-standard.md` and apply these preview-specific requirements:

- Lead with the expectation bar and the stock-reaction debate. If the user names a specific issue, such as AI memory demand, put that issue and its reaction drivers ahead of broad KPI archives or general diligence sections.
- Use four to six first-read tiles only when each has a distinct decision job, such as event timing, guide/consensus bar, operating proof point, market setup, an event-isolating implied move when available, or most important evidence gap.
- Make visible what is known, what the market likely requires, what could surprise, and what evidence is missing before taking incremental event risk.
- Include detailed KPI dashboards, peer/macro context, historical reactions, options/implied-move analysis, scenario maps, and extended call-question lists only when relevant and source-backed. Do not force a fixed dashboard module inventory into a flexible report.
- Match chart axes and labels to the units stated in the adjacent headings or tables. Omit a misleading chart rather than mixing units or scales.
- Keep citations traceable but readable; do not fragment dates, times, ticker symbols, product names, or product specifications into separately linked characters or tokens.
- Visually inspect the HTML according to the shared artifact standard before delivery and iterate on hierarchy, legibility, clipping, crowding, citation noise, and whether the requested investment question is immediately visible.

## Public Equity PM Judgment Layer

For substantial previews, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Default PM question: is the bar beatable, does it matter for the stock, and what would change sizing into or after the print?

Required PM judgment:
- State the expectation bar, consensus dispersion, guidance setup, implied move or reaction risk when available, and the estimate-revision path.
- Separate company fundamentals from stock setup: what is priced in, what the market may be ignoring, and what would make a bad print buyable or a good print fadeable.
- Include call-question falsifiers, listen-for items, and position actions: `add`, `press`, `hold`, `trim`, `exit`, `hedge`, `watchlist`, or `wait for proof`.
- For ETF/index diligence, include constituent weight, passive ownership/flow relevance, liquidity, benchmark exposure, and rebalance/event risk when relevant.
