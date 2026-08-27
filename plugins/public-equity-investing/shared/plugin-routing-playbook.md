# Public Equity Investing Plugin Routing Playbook

This playbook is the plugin-level router for broad Public Equity Investing prompts. Use it after `shared/invocation-policy.md` admits the request and before selecting a visible skill when the user describes a listed-equity investor workflow, ticker/security, public issuer, portfolio position, catalyst, earnings setup, valuation question, model update, or PM artifact instead of naming one narrow skill.

The machine-readable companion is `shared/plugin-routing-map.json`; the schema is `schemas/plugin_routing_map.schema.json`.

## Invocation Gate

Before routing an untagged request, apply `shared/invocation-policy.md`. Enter this plugin when the user explicitly names or tags Public Equity Investing or the request has listed-company, public-security, ticker, sector, portfolio position, event, earnings setup, thesis, catalyst, valuation, model update, or investor-lens context. Listed issuer, ticker, public security, earnings preview/deep dive, post-print, transcript, guidance update, call commentary, long/short pitch, public-equity valuation, model update, catalyst calendar, event-driven setup, position sizing, thesis-preserving hedge, thesis tracker, and PM memo language are high-signal when tied to a public-equity investment decision.

Do not activate this plugin for private-company diligence, credit-first analysis, personal financial advice, generic company summaries, generic share-price questions, or generic reports/decks/documents/models with no public-equity investment context. Corporate finance work, investment banking transaction execution, private markets diligence, and credit-security research remain outside scope unless the actual user task is a listed-equity investor workflow.

The `public-equity-investing` router reads `internal-support/policy.md` before using bundled evidence control, source-of-truth, generic data cleaning, rendering, style, provider guide, or sector-context support. Routing tables may refer to internal capability labels for support workstreams; resolve them to the router's bundled internal playbooks rather than presenting them as selectable skills. `financials-normalizer`, `model-audit-tieout`, `deck-report-qc`, `company-tearsheet`, and `meeting-prep` remain visible workflows when they are the standalone user job.

## Routing Principles

1. Route by listed-equity investor workflow first, skill lane second.
2. Keep one lead skill accountable for the first real investment judgment or hero artifact.
3. Use support skills only for owned workstreams: source normalization, model work, valuation, earnings, catalysts, risk, memo synthesis, QC, style, rendering, or source-of-truth validation.
4. Preserve the artifact hierarchy: hero human deliverable first, companion workbook/report artifacts second, support JSON/CSV/Markdown/log/manifest files last.
5. Lead final responses with the artifact the PM, analyst, IC, or client should open first.
6. Keep generic profile, cleanup, QC, and meeting-prep skills from absorbing substantive earnings, valuation, pitch, event, risk, or memo judgments.
7. Before a lead skill begins source gathering or analysis for a new substantive hero artifact, read `shared/deliverable-intake-policy.md` and collect only material preferences still missing from the request. Support skills reuse those choices rather than prompting again.

## Workflow Router

| Workflow | Lead Skill | Core Support Skills | Default Hero Artifact | Key Gates |
| --- | --- | --- | --- | --- |
| Company tearsheet | `company-tearsheet` | `financial-source-of-truth`, `sector-context-overlay`, `dashboard-builder` | Cited HTML profile or concise chat profile | Issuer/ticker/exchange/as-of verification; no rating or action unless escalated |
| Initiating coverage | `initiating-coverage` | `company-tearsheet`, `comps-valuation`, `dcf-model-builder`, `three-statement-model-builder`, `scenario-sensitivity-generator`, `catalyst-calendar`, `deck-report-qc` | Full HTML initiation report | Current price, share count, estimates, valuation support, thesis falsifiers |
| Earnings preview | `earnings-preview` | `company-tearsheet`, `financial-source-of-truth`, `sector-context-overlay`, `scenario-sensitivity-generator`, `portfolio-risk-management` | HTML pre-earnings report | Event date, consensus, company guide, price, KPI history, expectation bar |
| Earnings deep dive | `earnings-deep-dive` | `earnings-preview`, `equity-model-update`, `financial-source-of-truth`, `sector-context-overlay`, `scenario-sensitivity-generator`, `portfolio-risk-management` | HTML post-earnings report | Release, transcript, guidance, call commentary, price reaction, model/thesis impact |
| Equity model update | `equity-model-update` | `financials-normalizer`, `excel-data-cleaner`, `financial-source-of-truth`, `model-audit-tieout`, `scenario-sensitivity-generator` | Updated XLSX model | Copied workbook, source-to-cell map, formula preservation, post-update audit |
| Public comps valuation | `comps-valuation` | `company-tearsheet`, `financial-source-of-truth`, `sector-context-overlay`, `scenario-sensitivity-generator` | Comps workbook or HTML comps report | Peer selection, current market data, period/metric definition, outlier logic |
| Public-company DCF | `dcf-model-builder` | `financials-normalizer`, `financial-source-of-truth`, `scenario-sensitivity-generator`, `model-audit-tieout`, `comps-valuation` | Formula-first DCF workbook | WACC, terminal value, EV/equity bridge, current price, source labels |
| Three-statement model | `three-statement-model-builder` | `financials-normalizer`, `financial-source-of-truth`, `scenario-sensitivity-generator`, `model-audit-tieout` | Three-statement XLSX model | Period/unit reconciliation, model checks, first-tab insight dashboard |
| Long/short pitch | `long-short-pitch` | `company-tearsheet`, `earnings-preview`, `earnings-deep-dive`, `comps-valuation`, `portfolio-risk-management`, `catalyst-calendar` | PM-facing HTML trade pitch | Variant perception, trade expression, catalysts, risk/reward, exit/cover rules |
| Idea generation | `idea-generation` | `company-tearsheet`, `catalyst-calendar`, `sector-context-overlay`, `financial-source-of-truth` | HTML idea-triage report | Universe definition, screen logic, exclusions, next diligence step |
| Thesis tracker | `thesis-tracker` | `catalyst-calendar`, `earnings-deep-dive`, `portfolio-risk-management`, `financial-source-of-truth` | Tracker workbook or HTML thesis-status report | Stable thesis/source/catalyst ids, status reason, next review trigger |
| Catalyst calendar | `catalyst-calendar` | `company-tearsheet`, `earnings-preview`, `event-driven-analyzer`, `thesis-tracker`, `financial-source-of-truth` | HTML catalyst calendar | Confirmed vs inferred dates, event type, investor read-through, source posture |
| Event-driven analysis | `event-driven-analyzer` | `catalyst-calendar`, `scenario-sensitivity-generator`, `portfolio-risk-management`, `financial-source-of-truth`, `sector-context-overlay` | HTML event report | Terms, current price, probability/payoff/timing/downside, legal caveats |
| Portfolio risk and hedge | `portfolio-risk-management` | `long-short-pitch`, `thesis-tracker`, `scenario-sensitivity-generator`, `catalyst-calendar` | HTML risk decision report or sizing/hedge workbook | Position direction, constraints, hedge objective, add/trim/exit/unwind triggers |
| Scenario sensitivity | `scenario-sensitivity-generator` | `dcf-model-builder`, `comps-valuation`, `event-driven-analyzer`, `portfolio-risk-management`, `financial-source-of-truth` | HTML scenario report or sensitivity workbook | Case definitions, base price, assumptions, decision/action effect |
| Economic impact report | `economic-impact-report` | `idea-generation`, `company-tearsheet`, `sector-context-overlay`, `portfolio-risk-management`, `financial-source-of-truth` | HTML economic impact report | Macro/policy/commodity fact, issuer exposure, equity implication |
| Investment memo | `memo-builder` | `long-short-pitch`, `earnings-deep-dive`, `comps-valuation`, `dcf-model-builder`, `thesis-tracker`, `style-guide-adapter`, `deck-report-qc` | HTML investment memo or PM update | Import analysis from owning skills; preserve citations, assumptions, and caveats |
| Meeting prep | `meeting-prep` | `company-tearsheet`, `thesis-tracker`, `earnings-preview`, `earnings-deep-dive`, `financial-source-of-truth` | Meeting brief and question list | Public-equity decision context; thesis-linked questions and evidence requests |
| Financials normalizer | `financials-normalizer` | `excel-data-cleaner`, `financial-source-of-truth`, `equity-model-update`, `model-audit-tieout` | Model-ready financials workbook or explicit CSV pack | Source periods, units, metric definitions, source ids, QA flags |
| Model audit and tie-out | `model-audit-tieout` | `financial-source-of-truth`, `excel-data-cleaner`, `scenario-sensitivity-generator`, `equity-model-update`, `dcf-model-builder` | HTML model-audit report or audit workbook | Audit-only vs remediation, formula/source checks, workbook preservation |
| Deck and report QC | `deck-report-qc` | `financial-source-of-truth`, `style-guide-adapter`, `model-audit-tieout` | HTML QC report | Controlling artifact, source/model tie-outs, circulation posture |

## High-Signal Routing Cues

Use `earnings-preview` for pre-print setup language: earnings preview, pre-earnings, pre-print, expectation bar, quarter preview, and call questions before earnings.

Use `earnings-deep-dive` after results are available: post-print, post-earnings, transcript, guidance update, call commentary, beat/miss, stock reaction, and model/thesis impact.

Use `long-short-pitch` for trade-construction language: long/short pitch, pair trade, short pitch, long pitch, variant perception, trade expression, catalyst path, sizing considerations, and add/trim/exit/cover rules.

Use `catalyst-calendar` for dated monitoring windows and use `event-driven-analyzer` for probability/payoff event underwriting. A request for "upcoming catalysts" is a calendar; a request for "success/delay/break expected return" is event-driven analysis.

Use `portfolio-risk-management` for position sizing, hedge design, hedge this long, hedge this short, thesis-preserving hedge, risk budget, factor hedge, and integrated risk plans for listed-equity positions.

Use `equity-model-update` when the user supplies or references an existing public-equity model and asks to flow actuals, flow guidance, refresh assumptions, or produce a source-to-cell change log. Use `dcf-model-builder`, `three-statement-model-builder`, or `comps-valuation` when the user asks to build those model/valuation artifacts from scratch.

## Negative Routing Cues

Do not enter Public Equity Investing for:

- "Why did this stock move today?" unless the user asks for a listed-equity investment read-through, thesis impact, position action, or PM artifact.
- "Summarize earnings" unless the user asks for a post-print investment read, model impact, thesis status, or action implication.
- Generic company reports, decks, documents, profiles, valuation models, spreadsheet cleanup, or meeting briefs without a listed-equity investor mandate.
- Sell-side process, CIM, VDR, Datasite, buyer universe, bid log, deal committee, board transaction package, ECM/DCM/LevFin, or restructuring-pitch work; route those to Investment Banking.
- Bonds, loans, CDS, investment grade, high yield, leveraged loans, distressed debt, restructuring, recovery, covenants, spreads, yields, or debt-security recommendations; route those to Credit Markets.
- Internal FP&A, budgets, cash forecasts, close/reconciliation, procurement, or CFO reporting; route those to Corporate Finance.

## Clarifying Question Discipline

Ask only when the answer changes the route or artifact architecture. Good questions identify:

- investor use: PM screen, IC memo, sell-side research, client note, watchlist, risk review, or model update;
- first artifact: HTML report, workbook, tracker, memo, QC report, meeting brief, or chat-only answer;
- security context: ticker/issuer/security, position direction, benchmark, portfolio context, time window, and as-of date;
- source packet: filings, releases, transcripts, guidance, model version, provided workbook, data export, or market-data timestamp.

For new substantive hero deliverables, use the adaptive `request_user_input` preflight in `shared/deliverable-intake-policy.md` when these choices remain unresolved. If that tool is unavailable, ask all known material clarifying questions together in normal chat with recommended/default options first, then wait rather than asking one by one. If enough context exists, route and proceed. Mark assumptions in the hero artifact and final handoff.

## Escalation Rules

Route outside Public Equity Investing when the core task is not listed-equity investment work:

- Investment Banking: buyer-process execution, CIM drafting, VDR/Datasite/data-room diligence, banker pitch books, board transaction packages, deal committee materials, ECM/DCM/LevFin issuer advice, and restructuring pitches.
- Credit Markets: bonds, loans, CDS, IG/HY, bank loans, leveraged loans, distressed debt, restructuring, recovery, covenants, spreads, yields, and debt-security selection.
- Private Markets: sponsor IC, private-company diligence, sourcing, portfolio monitoring, and value creation with no public-equity security or listed-issuer decision.
- Corporate Finance: internal FP&A, budget, cash forecast, procurement, close/reconciliation, and CFO operating reporting.
- Legal: legal, regulatory, securities-law, compliance, fiduciary, or MNPI conclusions.
- Presentations, Documents, or Spreadsheets: native file production or direct editing when the user explicitly asks for those file types and no Public Equity Investing workflow owns the analysis.
