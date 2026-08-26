---
name: scenario-sensitivity-generator
description: Use when turning a public-equity base case, model, thesis, event, or catalyst into scenario skew, sensitivity, breakpoint, and PM action-threshold analysis. Do not use for first-pass model builds, credit-security valuation, or generic planning.
---

# Scenario & Sensitivity Generator

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Market Data & Estimates`
- `Company Filings & IR`
- `Portfolio Models & Trackers`
- `Earnings Transcripts & Events`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing`
router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive reusable scenario analysis, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, the default resolves the presentation surface to a polished standalone HTML scenario report unless the user requests an alternate surface, a quick/no-file answer, workbook/model output, or a standardized dashboard. In interactive runs, ask only remaining material choices such as depth, audience/use, or focus; in non-interactive runs, default to the HTML scenario report and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose

Turn an existing Public Equity Investing base case into scenario and sensitivity outputs that show what changes the investment view. This skill owns grids, breakpoints, probability cases, thesis triggers, source posture, and interpretation after a model, earnings setup, equity-risk credit-signal handoff, event case, macro view, or thesis tracker already exists.

The default lens is a public-equity investor deciding whether to add, press, hold, trim, exit, hedge, wait for proof, re-underwrite, or change rating/target. The output should tell a buy-side PM, long/short analyst, sell-side equity researcher, or ETF/index diligence user what the stock already discounts, what scenario is underwriteable, what is merely optical, what breaks first, and what evidence would change the action.

For a concrete dated corporate event, this skill may directly produce a success/delay/break, implied-probability, or breakpoint overlay when the user specifically requests scenario sensitivity and the relevant deal terms, current-price anchor, timing, and downside convention are available or can be verified. This is a scenario overlay, not a replacement for full event underwriting.

## Do Not Use

- First-pass DCF, 3-statement, comps, credit, earnings, full event-underwriting, or memo builds.
- Raw source cleanup, source hierarchy, or evidence conflict resolution.
- Final memo, pitch, hedge, sizing, or deck QC ownership.
- Generic FP&A planning or target-setting exercises.

Use the relevant local owner first, then return here for the scenario layer.

## Routing

Use downstream of `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `earnings-preview`, `earnings-deep-dive`, Credit Markets read-throughs, `event-driven-analyzer`, `economic-impact-report`, or `thesis-tracker`.

Use `financial-source-of-truth`, `financials-normalizer`, or `excel-data-cleaner` first if inputs are not clean or sourced. Use `model-audit-tieout` before treating workbook scenarios as final. See `references/p0-integration.md` for ownership boundaries.

Use `event-driven-analyzer` when the work requires a full event fact pack, process or regulatory/legal underwriting, trade expression, execution inputs, or ongoing event monitoring. When the request is explicitly for scenario skew on a named event and verified terms and pricing can anchor the cases, this skill may own the focused overlay while making any missing event diligence visible.

## Workflow

1. **Confirm base case and decision.** Identify security/issuer/model/event/thesis, decision type, and base-case source. If the base case is not model-validated, label outputs screen-grade or illustrative. For event overlays, verify offer or terminal terms, current price and as-of timestamp, key dates, contractual protections where relevant, and the chosen break/downside convention before presenting expected value. Use primary transaction documents and the freshest accessible market-data source for load-bearing inputs before relying on press reporting or older price observations; a focused overlay reduces analytical scope, not source-quality requirements.
2. **Select scenario mode.** Choose price-target, valuation, EPS/estimate revision, KPI driver, equity-liquidity downside, Credit Markets read-through sensitivity, event probability tree, macro factor, or thesis trigger table.
3. **Materialize tables when useful.** Use the deterministic helper for repeatable shells or populated calculations; if inputs are missing, it emits input-required rows instead of inventing values. Treat JSON, CSV, Markdown, run logs, and manifests as support artifacts unless the user explicitly asks for them.
4. **Interpret investor impact.** State the driver that matters most, what breaks first, whether upside is underwriteable, where the thesis depends on multiple expansion, estimate revisions, event probability, financing, or macro conditions, and which PM action would change. For event probability cases, state the analyst probability assumptions, hurdle, break-value convention, market-implied probability, and entry or maximum-break-probability threshold.
5. **Hand off cleanly.** Send model mechanics back to model builders, final narrative to `memo-builder` or `long-short-pitch`, exposure/sizing and hedge construction to the appropriate `portfolio-risk-management` mode, monitoring thresholds to `thesis-tracker`, and circulated decks/reports to `deck-report-qc`.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: base-driver ownership, scenario design, sensitivity math, output tables, and QA. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Deterministic Materializer

Run from this skill folder:

```bash
python3 scripts/materialize_public_equity_sensitivities.py --tables all --format json
```

With an assumptions file:

```bash
python3 scripts/materialize_public_equity_sensitivities.py --input assumptions.json --tables price_target_scenario,valuation_sensitivity --format json
```

Canonical table names:

- `price_target_scenario`
- `valuation_sensitivity`
- `eps_revision_sensitivity`
- `kpi_driver_sensitivity`
- `equity_liquidity_downside`
- `event_probability_tree`
- `macro_factor_sensitivity`
- `thesis_trigger_table`

Probability-weighted rows require complete probabilities that sum to 100%. Deterministic rows include `source_id`, `source_posture`, and `as_of_date` so downstream artifacts can distinguish model outputs from illustrative math. Load `references/materializer-schema.md` for the full input/output contract.

When `--output` or `--run-log` is used, the helper also writes `run_log.json` and `manifest.json` with `status`, `model_status`, warnings, hard failures, source basis, output paths, and output manifest. These deterministic tables are support artifacts unless a downstream workbook or dashboard turns them into the human-facing deliverable. Invalid table names or unsupported CSV multi-table requests must return non-zero with a failed run log when a log path is available.

Readiness is conservative: missing input JSON, missing base case, missing current price, or invalid probabilities must cap `model_status` at `not-decision-ready`. Complete math with missing source/as-of posture is `screen-grade`, not senior-review-ready. Only source-backed current price, valid scenario values, valid probabilities, and visible source posture can produce `senior-review-ready`.

If scenario outputs are inserted into or packaged as an XLSX workbook by a downstream tool, require a first visible `Cover` or scenario dashboard summarizing base case, cases tested, driver deltas, output range, source posture, validation status, warnings/hard failures, and the workbook/tab map.

## Output Modes

- **Full scenario report:** default route for substantive reusable scenario analysis, an explicit HTML scenario report, or a sourced discrete-event success/delay/break overlay. Produce a polished standalone HTML scenario report following `../../shared/html-artifact-standard.md`; let the decision and primary scenario object determine the layout rather than forcing a fixed dashboard module inventory.
- **Standardized dashboard:** use only when the user explicitly asks for a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render. For that path, use `references/DASHBOARD_PACK.md`: `scenario-sensitivity-generator` owns the scenario math, stock-price anchoring, expected-return/skew interpretation, action thresholds, source posture, and missing-evidence calls; `dashboard-builder` owns the shell/rendering/QA. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input, and keep JSON/Markdown/CSV/run-log support files behind the HTML dashboard unless explicitly requested.
- **Explicit quick PM read:** use only when the user explicitly asks for quick, short, summary, brief, one-page, or TL;DR. Include decision posture, current-price/base-case anchor, scenario range, binding breakpoint, primary missing evidence, and what changes the action.
- **Workbook/model overlay:** preserve or extend the owning workbook/model when scenario outputs are an input to an existing model package rather than a new standalone report.

## Artifact Contract

Every final answer or handoff should include:

- decision context and base-case source;
- table names used;
- driver changes, timing, absolute outputs, and deltas;
- source labels and as-of dates for market-sensitive inputs;
- whether outputs are model-validated, source-derived, user-provided, or illustrative;
- threshold, trigger, or breakpoint interpretation;
- expected return versus hurdle, downside/upside ratio, break-even probability, and skew label where applicable;
- explicit PM action rules for add, press, hold, trim, exit, hedge, wait for proof, or re-underwrite;
- what would change the investment view;
- recommended next workflow or user data request.

## HTML Guidance

For a substantive standalone HTML scenario report, load `../../shared/html-artifact-standard.md` and apply these scenario-specific requirements:

- Give each first-read element a distinct job: lead with the investment conclusion and posture; then show the current-price/base-case anchor, primary scenario tree or sensitivity object, market-implied hurdle or breakpoint, and what must be verified next. Do not repeat the same verdict through a hero, posture card, metric-tile row, and second decision panel.
- For a sourced discrete-event overlay, organize the report around verified terms and as-of price, success/delay/break cases, expected value versus hurdle, implied completion probability, break-value convention, timing sensitivity, regulatory or evidence gates, and conditional action rules. If wider event diligence is missing, label the output as a focused scenario overlay or screen-grade report and route full underwriting to `event-driven-analyzer`.
- Require agreement-verified ticking-fee or contingent-consideration mechanics and an exact assumed close or break date before featuring precise timing-adjusted payoff or hurdle-probability calculations. If either is missing, show timing math only as a clearly provisional sensitivity or omit it in favor of the evidence needed to calculate it.
- When scenario probabilities are illustrative rather than independently underwritten, lead with market-implied probabilities and required-probability or entry-price breakpoints. Keep any sample probability-weighted value secondary, explicitly illustrative, and out of the headline investment case.
- Distinguish `Reported` or `Source-derived` facts from `Analyst assumption`, `Derived calculation`, and `PM judgment`. Scenario probabilities, hurdle rates, break-value capture, terminal-value adjustments, and unvalidated timing assumptions must never appear to be sourced from a filing or market-data citation.
- Use action language appropriate to position status and evidence: when no holding or executed trade is provided, prefer `Conditional Action Rules`, `wait for proof`, `research`, or `re-underwrite` over language that implies an active position.
- Cite load-bearing terms, prices, dates, and calculations near use while keeping the page readable. Do not fragment tickers, dates, prices, percentages, scenario labels, or table cells into repetitive citation links; prefer a compact nearby source note when adjacent values share the same basis.
- Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, and iterate on hierarchy, density, clipping, citation rendering, whitespace, and whether the scenario decision is immediately usable.

## Reference Map

- `references/p0-integration.md`: local ownership and handoffs.
- `references/public-equity-investing-sensitivity-taxonomy.md`: table selection and interpretation rules.
- `references/materializer-schema.md`: deterministic script contract.
- `references/planning-mode-router.md`: Public Equity Investing mode selection.
- `references/scenario-overlay-contract.md`: workbook/cross-skill overlay schema.
- `references/target-backsolve-rubric.md`: feasibility labels for target backsolves.
- `references/output-templates.md`: trigger tables, QA checks, and reusable outputs.

## Quality Bar

Keep scenarios tied to a concrete security, issuer, model, event, or thesis. Label unsourced assumptions and stale data. Distinguish price-target math from investable risk/reward. Do not rebuild the base model, hide weak assumptions behind clean tables, or present probability-weighted outputs without source posture and downside. For discrete event overlays, require primary-document terms and fresh market-data anchoring when accessible, clear success/delay/break definitions, break-value methodology, expected return versus hurdle, market-implied probability where calculable, and the evidence gate that changes the conditional action. Treat timing-adjusted precision and probability-weighted values as provisional or secondary when their mechanics or probabilities have not been independently supported.

## Equity Valuation PM Standard

Load `shared/equity-valuation-pm-standard.md` and `shared/pm-judgment-heuristics.md` for substantial model, valuation, scenario, model-update, or audit work.

The output must state what the current stock price implies, the variant estimate path, whether upside is driven by fundamentals, multiple expansion, mix, capital return, sentiment, or event probability, what breaks first in downside, what changes target, rating, sizing, hedge, trim, exit, or watchlist status, and what evidence is missing.

Keep equity valuation as the center of gravity. Debt is allowed only as an input to common-equity value through net debt, cost of debt, leverage, liquidity, refinancing risk, or downside equity impairment. Use Credit Markets for bond comps, loan comps, CDS, spread/yield relative value, covenant-package analysis, debt-security valuation, recovery waterfall, restructuring valuation, creditworthiness, private-credit / public-credit instrument underwriting, or distressed claim valuation.
