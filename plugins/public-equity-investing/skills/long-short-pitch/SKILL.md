---
name: long-short-pitch
description: Use when building PM-facing Public Equity Investing trade pitches, including sparse-context or partial-section requests. Do not use for formal memos; use memo-builder.
---

# Long / Short Pitch

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `company_filings_ir`, `earnings_transcripts_presentations`, `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Market Data & Estimates`
- `Company Filings & IR`
- `Earnings Transcripts & Events`
- `Portfolio Models & Trackers`
- `Internal Research`

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive reusable trade pitch or explicit HTML pitch, the default resolves the presentation surface to a polished standalone HTML trade-pitch report unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus; in non-interactive runs, default to the HTML trade-pitch report and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Goal

Turn a public-equity-investing idea into an investable trade pitch. This is the buy-side pitch muscle: what is mispriced, how to express it, why now, how much can be made or lost, what proves us wrong, and what action discipline governs add, trim, cover, hedge, or exit decisions.

Default deliverable: full PM-facing trade pitch. Chat is fine for conversational or narrow pitch work, but a substantial reusable pitch or explicit HTML pitch should become a polished standalone HTML trade-pitch report following `../../shared/html-artifact-standard.md`. Let the trade decision, expression, and implementation gates determine the hierarchy. The output should sound like a seasoned portfolio manager forming a research posture, not an analyst filling a template. Do not compress to a quick pitch unless the user explicitly asks for `quick`, `short`, `summary`, `one-pager`, `TL;DR`, red-team-only review, or one specific section.

## Use When

Use this skill when the user asks to:

- pitch a public-equity long, short, pair, relative-value equity, or event-driven equity idea
- build variant perception, trade expression, catalyst path, sizing considerations, add/trim/exit/cover rules, or investability
- pressure-test weak catalysts, poor risk/reward, missing disconfirmers, crowding, borrow, carry, or bad exit discipline
- upgrade a hedge-fund-style idea note rather than a formal memo
- answer only part of a pitch, such as variant perception, why now, expression, sizing logic, disconfirmers, or cover rules

Do not use for:

- formal IC memos, investment memos, committee notes, client notes, research notes, or polished PM updates; use `memo-builder`
- pure merger-arb spread math or regulatory timeline; use `event-driven-analyzer` first
- pure capital-structure, covenant, recovery, maturity-wall, bond, loan, CDS, or debt-security work; use Credit Markets
- model refresh, earnings preview/deep dive, source update, or scenario table generation with no pitch synthesis
- personal investment advice or trade execution

## Boundary With `memo-builder`

`long-short-pitch` owns trade construction and pitch discipline. `memo-builder` owns formal written artifacts and final memo synthesis.

Use this skill first when the unresolved question is: what is the trade, variant perception, expression, catalyst, and action discipline?

Hand off to `memo-builder` when the pitch needs to become an IC memo, investment memo, committee note, client note, PM update, or formal equity research note. Credit-first memos route to Credit Markets.

## Operating Defaults

- Do not create files for narrow pitch work unless the user explicitly asks. For substantial reusable or explicitly requested HTML pitches, produce one polished standalone HTML trade-pitch report; do not force it through a fixed dashboard module inventory.
- Use `dashboard-builder` only when the user explicitly asks for a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render. For that optional path, use `references/DASHBOARD_PACK.md`: `long-short-pitch` owns trade construction, variant perception, expression, risk/reward, and monitoring rules; `dashboard-builder` owns the standardized shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV support files behind the HTML dashboard unless explicitly requested.
- Keep the pitch PM-usable; expand mechanics, not background.
- Never invent real-world facts. Unknowns must be labeled `TBD`, `not provided`, or explicit assumptions.
- Every material number must tie to a cited source, connector output, user-provided input, model output, or explicit assumption.
- If source access is incomplete, state the source posture and build a screen-grade pitch with missing data.
- Do not produce a blank template. If context is sparse, give a provisional stance, the best expression logic available, what would change the stance, and the exact missing data needed to upgrade conviction.
- If the user asks for only one section, answer that section directly with enough source posture, assumptions, and next data requests to make it usable. Otherwise default to the full pitch spine even when source context is thin.
- Ask a clarifying question only when there is no identifiable issuer, instrument, sector archetype, or trade direction and answering would be misleading.
- This skill can discuss proposed trade framing, but must not present account-specific advice or execute trades.

Load `references/intake-and-source-policy.md` for source tiers, request types, pitch modes, and minimum inputs.

## When To Invoke Support

Load `shared/support-layer-routing-contract.md` when support services are needed. Use `financial-source-of-truth` before final variant claims, market data, source conflicts, or management assertions. Use `financials-normalizer` or `excel-data-cleaner` before relying on messy financials, consensus/provider exports, ownership/short-interest tables, or event data. Use `deck-report-qc` before circulating a pitch deck/report and `style-guide-adapter` only after the pitch substance is locked. Support artifacts stay secondary; this skill owns trade construction, variant wedge, expression, catalyst path, and action discipline.

## Sparse Context And Partial Requests

When key facts are missing, lead with:

`Screen-grade only; placeholder assumptions used.`

Then give a PM stance before any metric table:

- `Actionability`: actionable candidate, watchlist, pass for now, or red-team only
- `Reason`: the one or two conditions that make the idea investable or not investable
- `What would change the stance`: evidence that would upgrade, downgrade, or kill the idea
- `Missing data`: exact items needed, not a generic diligence list

Sparse context does not mean short. Use the full pitch spine unless the user explicitly asks for a narrow section or compressed format.

For partial requests, do not force the full pitch spine. Deliver the requested slice, then add `Implications For The Trade` and `Missing Data To Upgrade Conviction`.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: variant perception, valuation/scenario work, catalyst path, risk/sizing/hedge, action rules, and red-team review. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Deterministic Scenario Support

This skill is primarily instruction-led, but it ships a scenario materializer for expected-value tables.

Use `scripts/materialize_trade_scenarios.py` when the user provides scenario rows or asks for scenario/EV math. The script accepts `references/scenario-ev-schema.md` and writes:

- `trade_scenarios_support_note.md`
- `trade_scenarios.json`

Default paths are under `/tmp/public_equity_investing_long_short_pitch/` unless explicit output paths are supplied. These are support artifacts. The helper is math-only, and the Markdown support note / JSON outputs are not the final user-facing pitch unless the user explicitly requests those formats. The final pitch still needs variant perception, expression, catalyst path, risk/reward, sizing considerations, disconfirmers, and add/trim/exit/cover rules.

## Output Spine

Use this full structure unless the user explicitly asks for a quick/short pitch, red-team-only review, or one section:

1. `Trade Recommendation`
2. `Variant Perception`
3. `Security / Expression`
4. `Why Now / Catalyst Path`
5. `Scenario Price Targets / Returns`
6. `Risk / Reward and Sizing Considerations`
7. `Disconfirmers and Kill Criteria`
8. `Add / Trim / Exit / Cover Rules`
9. `Monitoring Dashboard`
10. `Open Items / Data Requests`

Load `references/output-contract.md` for full section requirements and `references/strategy-playbooks.md` for long, short, pair, and event-driven equity pitch rules.

For sparse-context outputs, use the full spine with `screen-grade` labels and visible missing data. Use the narrower contracts in `references/output-contract.md` only when the user explicitly requests a partial section or compressed format.

## HTML Guidance

For a substantive standalone HTML trade-pitch report, load `../../shared/html-artifact-standard.md` and apply these pitch-specific requirements:

- Make actionability the primary visual object. Lead with the proposed posture (`initiate`, `watchlist`, `pass`, `cover`, or `wait for proof`), side and preferred expression if supportable, horizon, variant wedge, and the decisive implementation caveat.
- Immediately after the opening verdict, show a compact `Implementation Gate` block covering the trade-critical checks: catalyst, valuation or price anchor, liquidity, borrow/carry and squeeze/buyback risk for shorts, option cost/skew when relevant, and hedge ratio/residual exposure for pairs. Mark each as `Cleared`, `Not cleared`, `Missing`, or `Illustrative only`.
- Give the verdict, variant wedge, implementation gate, scenario skew, catalyst path, and action rules distinct jobs. Do not repeat the same recommendation in multiple large panels.
- Keep `What Is Priced In` explicit: distinguish demonstrated operating improvement from the expectation or valuation assumption a proposed trade would challenge.
- For shorts, put borrow, carry, crowding, squeeze/buyback exposure, preferred defined-risk expression if assessable, catalyst timing, and cover rule near the top rather than burying them in monitoring.
- For partnership, capacity, purchase, cloud-spend, or customer-commitment metrics shown in the first-read layer, name the economic direction explicitly. For example, label an issuer spending commitment `AWS Infrastructure Commitment` or `Snowflake AWS Spend Commitment` and state that it is not incremental revenue guidance unless the source establishes revenue.
- Title unsupported target/probability work `Illustrative Scenario Skew` when valuation support, borrow/carry, option pricing, or other implementation evidence is incomplete. Label targets and probabilities as analyst assumptions rather than company guidance, consensus, or externally validated price targets. Do not describe expected return as actionable until holding costs and constraints have been addressed.
- In standalone HTML, title the monitoring section `Monitoring Triggers` or `Evidence To Watch`; reserve `Monitoring Dashboard` for the explicitly selected standardized-dashboard path. When the proposed posture is `watchlist`, `pass`, or `wait for proof` with no current position, title action discipline `Conditional Action Rules` rather than implying an active position.
- Render evidence posture in plain investor language such as `Reported`, `Company guidance`, `Derived`, `Analyst assumption`, or `Not yet sourced`; do not expose internal evidence or schema labels in the visible report.
- Keep citations traceable but readable: do not fragment tickers, fiscal years, dates, percentages, numeric ranges, metric names, or product labels into separately linked tokens. Do not make an analyst assumption register appear to be an external evidentiary source.
- Do not render empty scenario fields, empty lists, decorative monitoring inventory, or repeated panels that do not sharpen expression or action discipline.
- Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, and iterate on hierarchy, density, clipping, citation rendering, and whether the proposed trade decision is immediately usable.

## Handoffs

- Source discipline: `financial-source-of-truth`, `financials-normalizer`
- Earnings/post-print: `earnings-preview`, `earnings-deep-dive`
- Valuation/model inputs: `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `scenario-sensitivity-generator`
- Trade risk: `portfolio-risk-management`, `thesis-tracker`
- Event foundations: `event-driven-analyzer`
- Equity-risk credit-signal inputs: use Credit Markets when credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, or debt-security analysis drive the case
- Formal memo synthesis: `memo-builder`

Use `sector-context-overlay` only when the issuer clearly matches a supported sector; use `references/sector-overlays.md` only for pitch-specific framing.

## QA Self-Check

Before finalizing:

- recommendation, side, expression, horizon, and caveat are clear
- sparse-context outputs lead with a stance rather than a placeholder template
- variant perception is not just "good company / bad company"
- catalyst path is actionable
- upside/downside math is internally consistent and probabilities sum to 100% when presented
- short pitches include borrow/carry/squeeze/cover discipline when data is available
- pair trades include hedge ratio, residual exposure, and break conditions
- credit-first pitches route to Credit Markets unless the final expression is common equity and credit is only an input
- missing live market data is labeled before any metric table
- partial-section requests answer only the requested section, plus trade implications and missing data; ambiguous broad pitch requests default to the full pitch
- action rules are evidence-based and not account-specific instructions
- ordinary standalone HTML pitches use actionability-first hierarchy and do not expose internal evidence labels or empty dashboard modules
- illustrative scenarios are clearly labeled when valuation anchors or implementation inputs are incomplete
- standalone HTML watchlist or no-position pitches use conditional action and monitoring-trigger language rather than dashboard or active-position headings

## Public Equity PM Judgment Layer

For substantial pitches, load `shared/pm-judgment-heuristics.md` before finalizing. Audience modes: `long_only_pm`, `long_short_hf`, `sell_side_research`, `etf_index_diligence`, `public_equity_diligence`.

Use this PM-native spine: `Proposed Trade / Actionability`, `Variant Wedge`, `What Is Priced In`, `Expression and Risk Budget`, `Scenario Skew`, `Catalyst Path`, `Disconfirmers`, `Add / Trim / Exit / Cover`, `Monitoring`.

Required PM judgment:
- Shorts require borrow, carry, squeeze path, buyback/low-float risk, catalyst timing, and cover rules when data is available or clearly missing.
- Pairs require hedge ratio, residual exposures, liquidity mismatch, catalyst symmetry, and break conditions.
- ETF/index can be a hedge, basket expression, benchmark-relative pair, or index rebalance/event setup.
- Preserve non-advice posture: discuss proposed expression and risk controls, not account-specific trade execution.
