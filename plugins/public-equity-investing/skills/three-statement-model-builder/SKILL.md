---
name: three-statement-model-builder
description: Use when building public-equity three-statement operating model workbooks. Default to the banker formula workbook path for new model builds; use deterministic exports only for controlled support calculations or explicit lightweight runs. Do not use for standalone workbook audits.
---

# Three Statement Model Builder

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Company Filings & IR`
- `Portfolio Models & Trackers`
- `Market Data & Estimates`

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

Own formula-first public-company operating model builds: integrated IS/BS/CF, working capital, PP&E and D&A, retained earnings, debt, revolver-style draws, cash sweep, equity-relevant liquidity/headroom metrics, scenarios, sensitivities, machine checks, and senior-review reporting.

## Hard Contract

- Default model-build artifact level is `banker_formula_workbook`; use the formula workbook path for normal public-equity 3-statement build, refresh, forecast, and operating-model-package requests.
- Formula mode is executed through `scripts/build_banker_formula_workbook.py` and must be labeled `banker_formula_workbook` only when its run log, workbook inspection, and `model_citations.json` prove the formula builder ran successfully.
- Deterministic scripts remain available for controlled computed values, smoke tests, or explicit lightweight support exports. They produce `output/model.xlsx`, `output/plan.json`, `output/run_log.json`, `output/manifest.json`, and optionally `output/support_note.md`. Legacy `output/report.md` is written only with `--write-report-md`.
- Formula scripts produce `banker_formula_workbook.xlsx`, `banker_formula_workbook_run_log.json`, `model_citations.json`, and `manifest.json` in the selected output directory. The workbook is the hero deliverable; citation JSON, run logs, and manifests are support artifacts.
- `output/model.xlsx` must start with a `Cover` tab that functions as a dashboard: model status, scenario outputs, revenue/EBITDA/FCF/cash, liquidity trough, leverage/headroom, source posture, warnings/hard failures, workbook map.
- `run_log.json` and `manifest.json` are required reliability artifacts; hard failures force `not-decision-ready`.
- Never delete, overwrite, or mutate source data unless explicitly requested. Preserve raw tabs/files and write new outputs under `output/` or a clearly named copy.
- Material inputs must be evidence-labeled: `source_reported`, `company_provided`, `connector_sourced`, `public_filing`, `web_verified`, `management_guidance`, `analyst_estimate`, `benchmark`, `assumption`, or `placeholder`.
- If placeholders, stale data, unsupported assumptions, or failed tie-outs remain active, mark the model no higher than `screen-grade`; hard failures mean `not-decision-ready`.

## Routing

Use this skill when the deliverable is a 3-statement build, refresh, rerun, operating model package, or integrated forecast rebuild. Route away when the primary ask is workbook audit/debug (`model-audit-tieout`), source hierarchy (`financial-source-of-truth`), raw financial normalization (`financials-normalizer`), spreadsheet cleanup (`excel-data-cleaner`), valuation (`dcf-model-builder`, `comps-valuation`), public estimate update (`equity-model-update`), Credit Markets research, or memo/deck polish.

For complex builds, split the work into source/evidence, historical normalization, operating drivers, balance sheet and cash, QA, and executive output workstreams. If sub-agents are unavailable, emulate those workstreams and reconcile them into one plan before running scripts.

## When To Invoke Support

Load `shared/support-layer-routing-contract.md` when support services are needed. Use `financial-source-of-truth` for filings, releases, guidance, consensus, market data, and assumption labels; use `financials-normalizer` before building the plan from messy financials, KPI schedules, segment tables, share count, net debt, capital allocation, or provider exports; use `excel-data-cleaner` before relying on malformed workbook tables; use `model-audit-tieout` for workbook logic, external links, recalc/cache posture, and final tie-out. Support artifacts stay secondary to the formula workbook or owning dashboard/report.

## Input Handling

- Preferred input is a `plan.json` matching the schema.
- No context: run `assets/plan_template.json` as illustrative, label placeholders, and cap status at `screen-grade`.
- Partial context: preserve user facts, retain template defaults only when necessary, and label unsupported inputs.
- Full financial package: normalize IS/BS/CF, reconcile the balance sheet, preserve source data, fill the plan, validate, run, then report checks and caveats.

## Required Workflow

1. Build or receive a valid `plan.json`.
2. Validate with `python3 scripts/validate_plan.py path/to/plan.json`.
3. Fix validation errors before running; do not silently default conclusion-changing assumptions.
4. Default path: run `python3 scripts/build_banker_formula_workbook.py path/to/plan.json --output-dir output` and inspect `banker_formula_workbook_run_log.json`.
5. Use `python3 scripts/run_pipeline.py path/to/plan.json` only for controlled computed values, smoke tests, explicit lightweight support exports, or when formula mode fails and the fallback is clearly labeled `deterministic_export`.
6. Verify the relevant workbook, run log, manifest, and, in formula mode, `model_citations.json`.
7. Read the run log; hard failures require `not-decision-ready`.
8. Present the workbook as the hero artifact, with the `Cover` tab carrying the decision read-through, and link the normalized plan, run log, manifest, citation ledger, and optional support note as audit files.

Smoke test:

```bash
python3 scripts/validate_plan.py assets/plan_template.json
python3 scripts/build_banker_formula_workbook.py assets/plan_template.json --output-dir /tmp/public-equity-investing-3s-formula
python3 scripts/run_pipeline.py assets/plan_template.json
```

## Formula Mode Guardrail

Load `references/banker-formula-workbook-contract.md` before using formula mode. If the formula builder fails, the template is missing, required tabs/formulas/styles are not present, external links appear, or `model_citations.json` is absent, do not describe any fallback artifact as a banker formula workbook.

## Status Labels

Use exactly: `decision-grade`, `senior-review-ready`, `screen-grade`, `not-decision-ready`, `blocked`. Use `blocked` only when no reasonable run can be produced before execution.

## Senior Standard

Explain what drives the forecast, what must be true, where cash is consumed, what breaks first in downside, whether EBITDA converts to cash, and which assumptions deserve diligence. Balance-sheet integrity, retained earnings, cash flow linkage, debt roll-forward, PP&E roll-forward, and working-capital roll-forward are non-negotiable.

## Deferred Reference Router

Load `references/reference-router.md` only when deeper schema, math, QA, integration, industry, or forecast judgment guidance is needed. The router preserves the detailed reference map without loading every reference during invocation.

## Equity Valuation PM Standard

Load `shared/equity-valuation-pm-standard.md` and `shared/pm-judgment-heuristics.md` for substantial model, valuation, scenario, model-update, or audit work.

The output must state what the current stock price implies, the variant estimate path, whether upside is driven by fundamentals, multiple expansion, mix, capital return, sentiment, or event probability, what breaks first in downside, what changes target, rating, sizing, hedge, trim, exit, or watchlist status, and what evidence is missing.

Keep equity valuation as the center of gravity. Debt is allowed only as an input to common-equity value through net debt, cost of debt, leverage, liquidity, refinancing risk, or downside equity impairment. Use Credit Markets for bond comps, loan comps, CDS, spread/yield relative value, covenant-package analysis, debt-security valuation, recovery waterfall, restructuring valuation, creditworthiness, private-credit / public-credit instrument underwriting, or distressed claim valuation.
