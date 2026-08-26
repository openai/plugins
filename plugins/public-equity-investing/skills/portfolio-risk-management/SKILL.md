---
name: portfolio-risk-management
description: Use when sizing Public Equity Investing positions, finding equity hedges, or building an integrated position-and-hedge risk plan from a listed-equity thesis. Do not use for thesis construction, standalone event underwriting, trade execution, personal investment advice, or credit-instrument risk.
---

# Portfolio Risk Management

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

### Source Resolution

Load `../../shared/workflow-source-resolution.md`. Resolve only the categories needed for this workflow: `internal_research`, `portfolio_models_trackers`, and `market_data_estimates`. Use the shared runtime contract to map each attempted category to an available app, connector, file, export, or user-provided input.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Portfolio Models & Trackers`
- `Market Data & Estimates`
- `Internal Research`

## Internal Support

When this workflow needs rendering, evidence/data preparation, style, or sector context, route support through the visible `public-equity-investing` router and its bundled internal playbooks. Route workbook or model QA through the visible `model-audit-tieout` workflow.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive integrated position-and-hedge plan or explicit HTML risk-plan request, the default resolves the presentation surface to a polished standalone HTML risk decision report unless the user requests another surface, a quick/no-file answer, workbook output, or a standardized dashboard. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose

Turn a listed-equity investment view into an implementable risk posture: the right size, any appropriate hedge, the exposure intentionally retained, and the rules for resizing or removing protection. This skill owns equity longs, equity shorts, pair trades, ETFs/index constituents, listed options, equity factor hedges, futures/index overlays, and macro proxies when the decision remains a public-equity decision.

Do not treat sizing and hedging as independent answers when one changes the other. Size from the tightest credible constraint; hedge only risks that can be reduced without destroying the intended alpha. A size-down/no-hedge outcome is valid when hedge basis risk, cost, liquidity, or complexity is worse than the unwanted exposure.

For a substantive reusable risk package, produce a polished standalone HTML risk decision report following `../../shared/html-artifact-standard.md`; retain the structured decision-sheet strengths of sizing tables, hedge comparisons, scenarios, and monitoring triggers without forcing a standardized dashboard shell. Use `dashboard-builder` only when the user explicitly asks for a standardized dashboard, recurring monitoring dashboard, reusable validated template, or structured payload-driven render.

## Mode Selection

Infer the mode from the requested decision and available context:

| Mode | Use when | Core output |
| --- | --- | --- |
| `position_sizing` | The user asks how much to own or short, add/trim/exit thresholds, loss budgets, liquidity capacity, or portfolio exposure impact. | Recommended size, binding constraint, scenario P&L, liquidity exit, monitoring rules. |
| `hedge_design` | The user asks how to hedge, neutralize, protect, de-beta, rank hedge candidates, or compare hedge instruments. | Hedge objective, candidate set, basis-risk ledger, sizing method, readiness checks, exit rules. |
| `integrated_risk_plan` | The user asks for both position size and hedge, or the hedge choice could materially change recommended size. | Unhedged versus hedged/size-down comparison, recommended package, retained exposure, action rules. |

Do not ask the user to choose a mode when the prompt or supplied artifact makes the decision clear. Ask one targeted clarification only when selecting the wrong mode would materially change the deliverable, such as an ambiguous request to "manage risk" without a stated position, unwanted exposure, or requested action.

## Public Equity PM/Risk Lens

Load `../../shared/pm-judgment-heuristics.md` and `../../shared/credit-markets-handoff.md` before producing a substantial risk recommendation.

Audience modes:

- `long_only_pm`: emphasize benchmark active weight, tracking error, liquidity/capacity, drawdown tolerance, add/trim discipline, and portfolio role.
- `long_short_hf`: emphasize gross/net/beta/factor impact, borrow, short squeeze risk, catalyst path, hedge fit, and cover/resize rules.
- `market_neutral_pairs_pm`: emphasize leg sizing, beta/factor/driver neutrality, residual spread risk, borrow, and liquidity.
- `event_driven_equity_pm`: emphasize adverse gap, timing delay, probability-weighted outcomes, options/borrow liquidity, and event slippage.
- `etf_index_benchmark_pm`: emphasize constituent weight, active weight, ETF/index flow exposure, rebalance risk, liquidity, and tracking-error impact.

Every substantive output must state intended alpha, unwanted risk, retained exposure, binding constraint, liquidity/exit posture, hedge or size-down tradeoff, monitoring triggers, implementation readiness, and missing evidence that could change the decision. Include basis risk and a hedge-failure scenario whenever protection is proposed.

## Boundary With Credit Markets

This skill may use CDS levels, credit spreads, ratings, maturity walls, refinancing pressure, covenant headlines, or liquidity stress only as common-equity downside signals.

Use CDS/spreads only as common-equity risk context. CDS levels and credit spreads may appear only as equity-risk signals or common-equity downside context; never treat them as a locally owned hedge implementation.

Use Credit Markets for CDS, bonds, loans, spread DV01/CS01, credit spread hedges, capital-structure hedges, distressed hedges, recovery waterfalls, covenant analysis or covenant hedges, debt-security sizing, and credit-security relative value. Do not present a credit instrument as a local hedge recommendation.

## Do Not Use

- Thesis, variant perception, or pitch construction: use `long-short-pitch` or `memo-builder`.
- Dated event probability and payoff underwriting: use `event-driven-analyzer`.
- Macro/economic transmission mapping: use `economic-impact-report`.
- Catalyst calendar or monitoring-only work: use `catalyst-calendar` or `thesis-tracker`.
- Personal investment advice, trade execution, or legal/compliance conclusions.

## Context Modes

| Context | Default behavior |
| --- | --- |
| No context | Request the security/exposure, desired action, horizon, constraints, and available data; provide a usable intake frame without inventing a recommendation. |
| Partial context | Produce a conditional risk screen or screen-grade integrated plan with explicit assumptions and missing-data checks; do not recommend initiation when required implementation inputs are missing. |
| Full source | Normalize inputs, tie out sources, run scenarios, and produce decision-ready risk guidance. |
| Review or refresh | Preserve prior work, identify stale inputs and hidden exposures, and show what changes the size or hedge. |

## Workflow

1. **Define the decision.** Capture security, direction, current/proposed size, thesis exposure to retain, unwanted risk, price/as-of time, horizon/catalyst, portfolio context, mandate limits, liquidity, and requested action.
2. **Resolve the loss-budget interpretation.** Distinguish a `scenario loss budget`, which constrains loss under a stated adverse move, from an `absolute loss cap`, which must remain satisfied even if the stock moves beyond that scenario. When the user gives a loss limit for a short but does not say which interpretation applies, ask one targeted clarification in an interactive run. In a non-interactive run, show both branches and do not silently turn an assumed squeeze magnitude into an initiation recommendation. For a short with an absolute cap, require priced defined-loss protection or recommend no position.
3. **Map exposures.** Separate intended idiosyncratic, event, and chosen factor/macro exposures from unwanted beta, sector, factor, FX, commodity, liquidity, borrow, financing, crowding, gap, and portfolio-concentration risk.
4. **Build risk cases.** Estimate upside/base/downside/stress outcomes, probability-weighted return when supportable, scenario P&L, liquidity/exit implications, and any hedge-failure case. Label assumed stress magnitudes as illustrative until confirmed by the user or a governing risk policy.
5. **Apply the selected mode.**
   - For `position_sizing`, triangulate loss-budget, volatility, liquidity, exposure-limit, benchmark/factor, borrow/squeeze, catalyst, and portfolio-fit constraints; recommend the most restrictive credible size.
   - For `hedge_design`, classify exposures as keep, hedge, reduce, or monitor; evaluate direct equity, ETF/index, factor, pair, listed-option, futures/index, causal macro-proxy, portfolio-overlay, and no-hedge/size-down alternatives.
   - For `integrated_risk_plan`, compare unhedged size, hedged size, and size-down/no-hedge outcomes; recommend the package with the clearest retained alpha and acceptable cost/basis risk.
6. **Assess feasibility.** State market-data freshness, ADV/exit days, borrow/recall/squeeze constraints, option chain/Greeks where relevant, cost/carry, basis risk, mandate/compliance checks, and implementation-readiness gaps. For a short recommendation, current executable quote, ADV/exit capacity, locate/borrow terms, and current squeeze/crowding inputs are required before using `initiate` or other implementation-ready language; live option terms are additionally required before recommending an options hedge.
7. **Recommend and monitor.** If implementation inputs are missing, label the result `Conditional risk screen` or `Not implementation-ready` and state the conditional size/package rather than instructing initiation. Otherwise state recommended size and/or hedge, action, binding constraint, retained exposure, rejected alternative where material, add/trim/exit/cover/resize/roll/remove triggers, confidence, and missing evidence.
8. **Render and inspect when HTML is delivered.** In a standalone HTML report, front-load a compact constraint-interpretation table, conditional or executable action, hedge tradeoff, and missing inputs before entry. Keep citations readable: do not fragment tickers, dates, percentages, basis-point amounts, instrument terms such as `GLP-1`, or scenario labels with inline links. For a local HTML file, inspect the opening viewport and decision-critical downstream sections with local headless-browser screenshots rather than the in-app Browser plugin.

## Reference Map

Load only references needed by the selected mode:

- All substantive modes: `references/source-and-context-protocol.md`, `references/exposure-and-factor-risk.md`, and `references/liquidity-drawdown-scenarios.md`.
- `position_sizing`: `references/sizing-framework.md`, `references/strategy-nuance.md`, `references/position-sizing-output-templates.md`, and `references/quality-control.md`.
- `hedge_design`: `references/hedge-workflow.md`, `references/instrument-playbooks.md`, `references/hedge-output-templates.md`, and `references/hedge-scorecard-schema.md`.
- `integrated_risk_plan`: the sizing and hedge references necessary for the recommended package; avoid loading unused instrument playbooks.
- Standalone HTML deliverables: `../../shared/html-artifact-standard.md` and the selected mode's output template.
- Explicit standardized dashboard deliverables: `references/DASHBOARD_PACK.md`.

## Deterministic Scripts

Use bundled helpers when structured inputs are supplied or the user asks for templates/files:

```bash
python scripts/create_position_sizing_templates.py --out path/to/templates
python scripts/position_sizing_calculator.py --input path/to/input.json --out path/to/outputs
python scripts/score_hedge_candidates.py hedge_candidates.csv --output-dir path/to/outputs
```

The sizing helpers write transparent calculation/audit support files including `position_summary.csv`, `sizing_cases.csv`, `scenario_pnl.csv`, `exposure_impact.csv`, `liquidity_exit.csv`, `monitoring_rules.csv`, `support_note.md`, `run_log.json`, and `manifest.json`. The hedge helper writes `hedge_scorecard_support_note.md`, `hedge_scorecard.csv`, `hedge_scorecard.json`, and `basis_risk_ledger.csv`.

These helpers do not fetch live data, run portfolio risk systems, satisfy compliance checks, or replace PM judgment. CSV, Markdown, JSON, run-log, and manifest files are support artifacts unless the user explicitly asks for those formats. For substantial reusable packages, lead with a polished standalone HTML risk decision report unless the user explicitly requests a standardized dashboard.

## Dashboard Handoff

If the user explicitly asks for a standardized or recurring dashboard, use `references/DASHBOARD_PACK.md`. `portfolio-risk-management` owns size, hedge, retained-exposure, binding-constraint, basis-risk, scenario, liquidity, and monitoring judgment; `dashboard-builder` owns rendering and validation. Build a `public_equity_investing_dashboard.v1` payload as an internal renderer input and keep support files behind the HTML dashboard unless explicitly requested.

## Handoffs

- `long-short-pitch`: establish the thesis and trade expression before risk construction.
- `thesis-tracker`: maintain decision triggers after a position or hedge is adopted.
- `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `economic-impact-report`, or `event-driven-analyzer`: refresh the underlying equity case before risk work when needed.
- `scenario-sensitivity-generator`: build larger grids or breakevens.
- `financial-source-of-truth`, `financials-normalizer`, `model-audit-tieout`, and `excel-data-cleaner`: de-risk source data or workbook inputs.
- `memo-builder`, `deck-report-qc`, and `style-guide-adapter`: package or circulate a final artifact.

## Output Contract

Default output should include:

1. Decision summary: mode, recommendation or conditional screen status, action readiness, confidence, and binding constraint.
2. Exposure objective: intended alpha, unwanted risk, and retained exposure.
3. Constraint interpretation: scenario loss budget versus absolute loss cap, the assumptions needed for each branch, and the compliant action.
4. Risk/return cases: downside, stress, catalyst/path case, and hedge-failure case when relevant.
5. Sizing recommendation or hedge package, including size-down/no-hedge comparison where material.
6. Portfolio impact, liquidity/exit, cost/carry, basis risk, and readiness gaps.
7. Monitoring rules: add, trim, exit, cover, resize, roll, remove, and re-underwrite triggers as applicable.
8. Sources, assumptions, stale inputs, and open data requests.

Before finalizing a sizing or integrated recommendation, apply `references/quality-control.md`. Before recommending a hedge, confirm it preserves desired thesis exposure, names basis risk and cost/carry, and includes a no-hedge/size-down alternative.
