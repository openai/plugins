---
name: catalyst-calendar
description: Use when building public-equity-investing catalyst calendars. Do not use for full event underwriting; use event-driven-analyzer.
---

# Catalyst Calendar

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

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved choices. For a substantive single-company 60/90-day catalyst calendar, the workflow default resolves the presentation surface to a polished HTML catalyst calendar unless the user asks for another format, a quick/no-file answer, or a workbook/tracker. In that case, do not block on a format question; ask only for unresolved depth, audience/use, or focus choices. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose
Build or refresh source-backed Public Equity Investing catalyst calendars. The output should show timing, confidence, thesis relevance, prep work, owner/status, and likely PM decision, not just dates.

## Use / Do Not Use
Use for single-name, portfolio, sector, earnings, regulatory, clinical, technical, capital-markets, and special-situation catalyst tracking. Use the script for tracker workbooks, CSV/JSON intake, refresh logs, blank templates, or optional ICS export.

Do not use for merger-arb/spin/tender probability math; route to `event-driven-analyzer`. Do not use for pure pre-print notes, post-event analysis, model refreshes, thesis updates, risk sizing, or hedge design; route to `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `thesis-tracker`, or `portfolio-risk-management`.

## Reference Router
- `../../shared/html-artifact-standard.md`: shared principles for polished, legible, evidence-aware HTML artifacts.
- `source-and-data-protocol.md`: source hierarchy, stale-date checks, confidence labels, refresh rules.
- `catalyst-taxonomy-and-fields.md`: event fields, categories, scoring labels.
- `event-scoring-framework.md`: impact, confidence, controversy, urgency.
- `pm-action-playbook.md` / `portfolio-pm-playbook.md`: prep actions, thesis checkpoints, clustering, position context.
- `sector-and-asset-overlays.md`: sector-specific catalyst logic.
- `output-templates.md` / `pm-review-checklist.md`: delivery formats and QA.

## Workflow
1. Classify mode: no-context template, partial-context build, refresh, single-company map, portfolio dashboard, single-event brief, or sector sweep.
2. Set scope: default to next 30/60/90 days plus thesis-critical longer-dated items. Ask only for destructive or blocking choices.
3. Build rows with exact date or window, source, confidence, status, thesis link, model/KPI line, prep action, owner, and decision implication.
4. Rank by impact, confidence, controversy, actionability, portfolio relevance, and same-day clustering.
5. Convert high-priority events into work items, model updates, questions, risk/sizing reviews, hedge prompts, or post-event follow-up.
6. Refresh non-destructively: preserve prior rows, append evidence, mark stale/superseded items, and produce a change log.
7. For a named issuer plus a substantive 60/90-day calendar, default to a polished standalone HTML catalyst calendar when local artifact creation is available unless the user requests another format, a quick/no-file answer, or a workbook/tracker. In interactive runs, ask only for unresolved depth, audience/use, or focus choices; mention that another format is available as an opt-out without making it a blocking question. In non-interactive runs, apply the HTML catalyst calendar plus full working analysis defaults and disclose those assumptions in the delivery message or accompanying chat summary, not as visible artifact metadata.
8. For other multi-category calendars, PM monitoring calendars, or requests that ask for earnings plus macro/regulatory/company-specific catalysts, treat polished standalone HTML as the recommended presentation path and use `../../shared/deliverable-intake-policy.md` for materially unresolved format or depth choices.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: event/date verification, source freshness, catalyst impact, probability/timing, and follow-up monitoring. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Guardrails
- Never imply a date is confirmed without reliable evidence.
- Use windows for guided, estimated, inferred, or street timing; do not turn soft windows into one-day ICS events.
- Separate facts, assumptions, rumors, restricted/internal notes, and PM judgments.
- Do not invent earnings dates, trial readouts, approvals, lockups, merger deadlines, conferences, or policy dates.
- Surface conflicts and prefer company/regulator/exchange sources over aggregators.

## Default Output
Recommend the full catalyst package: PM summary, top-catalysts table, full catalyst register or clearly scoped subset, prep plan, source/freshness notes, refresh change log when relevant, decision implications, and recommended adjacent work.

For substantive single-company 60/90-day catalyst calendars, default to a concise chat summary plus a polished standalone HTML catalyst calendar when local artifact creation is available. This workflow default resolves presentation format unless the user requests another format, a quick/no-file answer, or a workbook/tracker. In interactive runs, ask for unresolved analysis depth and any consequential audience/use or focus choice, but do not require the user to confirm HTML before proceeding. In non-interactive runs, default to the HTML catalyst calendar and `Full working analysis`, and state the assumed format and depth in the delivery message or accompanying chat summary rather than in the visible HTML artifact.

If the user explicitly asks for a standardized dashboard, reusable dashboard template, or structured payload-driven render, route that optional rendering path through `dashboard-builder` and follow its payload and validation contract. `catalyst-calendar` continues to own event selection, timing, confidence, impact, and PM monitoring judgment. Keep JSON/Markdown/CSV/ICS support files behind the HTML artifact unless explicitly requested.

Use a single-event brief or compressed watchlist only when the user explicitly asks for a summary, quick read, one-pager, brief, TL;DR, or one specific event.

## HTML Guidance

For substantive HTML output, load `../../shared/html-artifact-standard.md` and apply these calendar-specific priorities:

- Use a title that identifies the requested artifact, such as `<Company> (<Ticker>): 90-Day Catalyst Calendar`; do not substitute a generic label such as `Decision Map` for a calendar request.
- Structure the first read as an investor brief: concise thesis checkpoint, add/hold/trim triggers, then the catalyst schedule. Put the detailed register, preparation queue, and source ledger below that scan layer.
- Make the catalyst schedule the primary visual object; the reader should reach upcoming dates and timing windows quickly.
- Before a detailed register table, include a compact month-by-month or time-horizon visual summary of the highest-decision-pressure confirmed dates and inferred windows. Keep it concise: the detailed register should own full explanations, implications, and sourcing.
- Show confirmed dates distinctly from inferred windows and unscheduled monitoring items.
- Surface the highest-decision-pressure events prominently, while retaining lower-priority confirmed issuer events in the calendar when they fall inside scope.
- Include preparation actions and add/hold/trim implications when the user supplies portfolio context.
- Keep sourcing unobtrusive but auditable, with visible timing confidence and material evidence gaps.
- A full catalyst register is appropriate for substantive calendars, but do not repeat the same event across overview, register, thesis tests, and prep sections unless each view answers a distinct investment question.
- Do not surface internal support-contract fields in the HTML artifact; convert relevant evidence gaps and readiness limitations into polished PM-facing prose.
- Do not show format-selection, intake, or generation-process notes such as `Format assumption` in the HTML artifact; keep any required default disclosure in the delivery message.

## Script Contract

```bash
python scripts/create_catalyst_calendar_workbook.py --input events.csv --output catalyst_calendar.xlsx --ics catalyst_calendar.ics
python scripts/create_catalyst_calendar_workbook.py --prior prior_events.csv --input refreshed_events.csv --output refreshed_calendar.xlsx
```

The script is a materializer, not a live data provider. It preserves source/confidence fields, keeps undated/windowed items in review tables, writes refresh changes, and exports ICS entries only for confirmed exact dates.

Workbook outputs start with a `Cover` tab that serves as the PM dashboard: as-of date, event counts, 30/60/90 day pressure, red/amber urgency, high-impact events, low-confidence events, overdue/missing-owner prep, top catalysts, source posture, and workbook map.

## Public Equity PM Judgment Layer

For substantial catalyst work, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

PM catalyst discipline: a catalyst only matters if it can alter estimate path, narrative, multiple, position size, downside, liquidity, or event probability.

Required PM judgment:
- Rank by `decision_pressure`, not date proximity alone.
- Add index/ETF and technical catalysts when relevant: index additions/deletions, Russell/S&P/MSCI rebalance, ETF reconstitutions, lockups, secondary offerings, buyback windows, blackout windows, passive ownership shifts, and float changes.
- Separate confirmed dates from inferred windows. Do not export inferred windows as exact calendar events.
- Group low-impact dates as hygiene unless they are tied to a decision.
