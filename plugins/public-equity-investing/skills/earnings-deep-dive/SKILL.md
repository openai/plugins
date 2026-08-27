---
name: earnings-deep-dive
description: Use when analyzing public-company earnings after results, guidance, transcript, or call commentary. Do not use for pre-print previews.
---

# Earnings Deep Dive

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
- `Portfolio Models & Trackers`
- `Internal Research`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing` router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For an explicit `deep dive`, `full report`, or reusable/source-heavy post-print package, resolve presentation to a polished standalone HTML post-earnings report unless the user requests another format, a quick/no-file answer, or workbook/model-update output. In interactive runs, ask only remaining material questions such as depth, audience/use, or focus; narrower post-result questions continue to use normal intake. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

Produce a decision-grade, audit-ready post-print package after results are available.

Default to the full post-print package. Chat can be the surface for narrow or explicitly no-file asks, but an explicit deep dive, full report, or source-heavy reusable post-print package should be a polished standalone HTML post-earnings report following `../../shared/html-artifact-standard.md`. Use `dashboard-builder` only for the optional standardized-dashboard route below. Use deterministic file mode only when the user supplies `plan.json`, normalized CSVs, model-update inputs, or explicitly asks for files.

## Route

- `full deep dive`: default analytical route for post-earnings deep dives, earnings-print analysis, and investor-facing post-print questions. An explicit deep dive, full report, or reusable/source-heavy package defaults to polished standalone HTML.
- `one-page tear sheet`: use only when the user explicitly asks for a summary, one-pager, quick read, brief, or TL;DR.
- `audit-ready model update`: use only when the user supplies or references a model/workbook, driver registry, output registry, normalized CSVs, model-update inputs, or explicit data to update a model.
- `quote and debate map`: standalone only when the user asks only for transcript quotes/debate; otherwise include it inside the full deep dive.
- `standardized dashboard`: only when the user explicitly asks for a standardized dashboard, reusable dashboard template, PM cockpit, tabbed dashboard, or structured payload-driven render, keep this skill as the analysis owner and hand the resulting `public_equity_investing_dashboard.v1` payload to `dashboard-builder`. Use `references/DASHBOARD_PACK.md` for module mapping.
- `deterministic file mode`: validate inputs, run shipped scripts, fail QA on unresolved user-facing placeholders, and disclose packet versus workbook-apply path.

Load `references/REFERENCE_ROUTER.md` first, then only the route-specific reference needed for the selected artifact.

## Non-Negotiables

- Never invent numbers, quotes, guidance, definitions, accounting facts, estimate timestamps, source tags, or catalyst dates.
- Use official filings/releases before decks and transcripts; transcripts support narrative and call-only guidance, not primary GAAP numbers.
- Every reported number and every quote needs a source tag; analyst-derived numbers need formula/assumption and confidence.
- Full deep dives must include transcript evidence and a debate-map treatment when transcript evidence is available. If no transcript is available, show a concise visible limitation labelled `transcript not provided` or `transcript source not found` and list the exact missing artifact; do not render an empty Q&A table.
- For transcript Q&A, capture questioner name, firm if available, answering executive, topic, section, source tag, why it matters, bull/bear implication, and falsifier/next check.
- Keep GAAP/non-GAAP, reported/constant-currency, company-guided/analyst-derived, units/scale, and unavailable-data labels explicit.
- Always run an EPS quality screen: ask whether headline EPS could misstate recurring operating performance. Include a full EPS quality / ex-gain bridge when GAAP EPS surprise is distorted by below-the-line, tax, mark-to-market, equity-investment, FX, restructuring, litigation, asset-sale, impairment, share-count, or other non-recurring items; otherwise state that no material EPS-quality trigger was identified from available sources.
- Full deep dives must include quarterly key metrics and growth trajectory using the issuer's actual business drivers, not only generic revenue/EPS/margin. Use sector-context-overlay when the company-specific KPI set is not obvious.
- For HTML reports or standardized dashboard handoffs, include earnings visualizations when source-backed data exists: quarterly revenue, gross profit, net income, and the best source-backed profitability margin history; estimated EPS versus actual EPS for the past five quarters on a consistent basis; and equity-price history annotated with material market events. Omit any chart whose required series is missing, stale, or not comparable, and surface that gap clearly.
- Treat margin selection as an analytical decision, not a template default. Default to net margin only when net income is a fair recurring-profitability proxy. Prefer operating margin when net income is distorted by below-the-line, tax, mark-to-market, equity-investment, FX, restructuring, litigation, asset-sale, impairment, or other non-recurring items. Prefer adjusted operating margin, EBITDA margin, contribution margin, or FCF margin when that is the issuer's source-backed investor KPI. For dashboard payloads, set `financial_trend_chart.data.margin_metric`, `margin_label`, and `margin_rationale` whenever the line is not plain net margin.
- Rank highlight/snapshot metrics by investor salience. A growth rate, acceleration, surprise %, guide delta, backlog growth, margin inflection, or clean/normalized metric should be the tile value when it better explains the stock-moving point than the absolute reported amount; put the absolute amount in the detail.
- Full deep dives must include read-throughs when the print, filing, transcript, or management interviews mention customers, suppliers, peers, competitors, platforms, channels, commodities, regions, or adjacent industries.
- Full deep dives must include major news coverage and market events when recent or upcoming events change the interpretation of the print, guidance, estimate revisions, multiple, risk, positioning, or read-throughs. Scan the last quarter, last twelve months, and forward-looking anticipated events; cite every event and label uncertain windows.
- Capture catalysts learned from the release, filing, transcript, Q&A, and management interviews. Separate dated catalysts from inferred monitoring windows.
- Use precise absence labels: `not guided`, `not disclosed`, `not provided`, `source not provided`, or `MISSING: <dependency>` only where appropriate.
- Generated Markdown support notes must not contain unresolved bracket tokens, `TODO`, or authoring placeholders.

## Chat Contract

Default sections for full deep dive: setup/source posture, dense executive summary, PM bottom line, granular beat/miss or guide-versus-bar, EPS quality screen, quarterly key metrics, growth trajectory, guidance delta/deep dive, what changed, revision/stock setup, load-bearing drivers, transcript quote/Q&A and debate map, read-throughs, major news and market events, model/thesis impact, catalysts/watch list/falsifiers, source limitations, and open questions. For investor-facing prompts add thesis change, likely estimate revision, stock/valuation skew, and next catalyst.

Use the evidence pack that supports the selected artifact without shrinking the user-facing analysis:

- Full deep dive: release/filing, deck/prepared remarks, transcript, estimates, and prior-quarter/prior-guide sources where available.
- Explicit summary or one-page tear sheet: release or 8-K, deck if available, estimate source, and transcript only for high-signal quotes.
- Audit-ready model update: release/filing/deck, estimate set, prior guide, and model/workbook or normalized driver inputs supplied or referenced by the user.
- Standalone quote/debate: transcript plus release/deck to cross-check numeric claims.

## HTML Guidance

For a substantive HTML deep dive, load `../../shared/html-artifact-standard.md` and let the company-specific investment debate determine the layout.

- Title the artifact as a post-earnings deep dive identifying the company, ticker, and reported period.
- Start with a direct verdict answering the investor's question, 4-6 high-signal metric tiles, one compact decision box, and a quality-of-print bridge separating headline results from recurring operating evidence.
- Use only distinct decision-relevant tiles. Prefer 4-5 tiles when additional metrics repeat the same analytical point; combine related buyback, leverage, interest-expense, or cash-flow signals into one capital-allocation-quality tile when that improves readability.
- Put supporting analysis below that first read: beat/miss and guidance, EPS quality, company-specific growth drivers, capital allocation, valuation/stock setup, catalysts, falsifiers, source limitations, and evidence ledger as relevant.
- Give each first-read element a distinct job: the verdict answers the investment question and explains why; the decision box states thesis change, estimate direction, valuation/stock skew, action discipline, and next proof point; metric tiles show evidence rather than restating the verdict; the quality-of-print bridge reconciles headline results to recurring equity value. Do not repeat the same conclusion across these elements.
- Describe evidence posture in reader-facing terms by naming sources obtained and important confirmations still missing, for example `Company release reviewed; filing and transcript confirmation pending`. Avoid internal-sounding quality labels such as `research-grade` in the visible artifact.
- Include transcript Q&A, read-throughs, market-events tables, scenario sections, and charts only when substantive and evidence-supported. A missing transcript should be a concise limitation callout, not an empty table.
- Do not render blank scenario cards, placeholder modules, or visible source cells marked unsourced when the claim has a cited source.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: release and filing numbers, transcript/Q&A, estimates and guidance, model/thesis impact, and source QA. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Deterministic Contract

Use only when requested or file/model inputs are supplied:

- `scripts/validate_plan.py`
- `scripts/validate_normalized_inputs.py`
- `scripts/run_plan.py`
- `scripts/apply_model_updates.py`
- `scripts/model_diff.py`
- `scripts/verify_tearsheet.py`

If workbook apply fails or is unsafe, deliver a driver update packet and explain the limitation. The bundled plan defaults to packet/dry-run mode and writes outside the skill tree.

## Standardized Dashboard Handoff

Use `dashboard-builder` only when the user explicitly selects the standardized dashboard, reusable dashboard-template, or structured payload-driven rendering path. This skill still owns the analysis and maps it into `references/DASHBOARD_PACK.md`; prefer `layout: "single_page"` with sticky contents for full PM diligence dashboards unless the user explicitly asks for tabs. Ordinary standalone HTML deep dives use the flexible HTML guidance above rather than a fixed module inventory.

## Public Equity PM Judgment Layer

For substantial post-print work, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Default PM question: did the quarter change the thesis, estimates, valuation support, or sizing?

Required PM judgment:
- Lead with thesis change, estimate revision direction, valuation support, and position action.
- Bridge headline versus clean result, guide delta, quality of beat/miss, transcript evidence, management credibility, and next falsifier.
- Separate reported facts, management claims, consensus, market data, model output, assumptions, and PM judgment.
- For sell-side mode, add rating/target implications and risk-to-rating. For hedge fund mode, add add/trim/cover triggers.
