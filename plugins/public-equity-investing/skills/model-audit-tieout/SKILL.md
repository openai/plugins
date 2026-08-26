---
name: model-audit-tieout
description: Use when auditing existing Public Equity Investing models or spreadsheets. Do not use to build a new model from scratch.
---

# Model Audit Tie-Out

## Skill Configuration

### Common Skill Instructions

MANDATORY: Before searching connectors, retrieving evidence, or drafting output, read and apply the shared runtime contract in `../public-equity-investing/SKILL.md## Cross-Skill Runtime Contract`. Then check the router skill map and `../../shared/plugin-routing-playbook.md` for adjacent skills that should be sequenced with this workflow. Do not run user-context setup or inspection during ordinary workflow work; route only explicit saved-context, source-setup, onboarding, or automation-setup requests to `../user-context/SKILL.md`.

## Relevant Dependency Categories

These are the source categories most likely to matter for this workflow. Use the router contract to resolve only the categories the task actually needs, prefer user-named sources first, and state any material source limitation.

- `Portfolio Models & Trackers`
- `Company Filings & IR`
- `Market Data & Estimates`

## Internal Support

When the audit requires evidence control, generic data cleaning, dashboard rendering, style application, or sector context, route that support through the visible `public-equity-investing` router and its bundled internal playbooks. This visible skill remains the owner of the model-review deliverable.

## Deliverable Intake

Before source gathering or analysis for a new substantive hero deliverable, load `../../shared/deliverable-intake-policy.md` and use its adaptive `request_user_input` preflight for materially unresolved format, depth, audience/use, or focus choices. For a substantive standalone review of an existing model or explicit HTML model-audit request, the default resolves the presentation surface to a polished standalone HTML model-audit report unless the user requests an alternate surface, a quick/no-file answer, remediation output, or a standardized dashboard. In interactive runs, ask only remaining material choices such as depth, audience/use, materiality, or focus; in non-interactive runs, default to the HTML model-audit report and `Full working analysis` while disclosing those assumptions outside the artifact. Reuse resolved preferences in downstream steps; when acting only as input to an owning workflow, do not re-prompt.

## Purpose

Review an existing public-equity model, workbook, forecast, valuation file, estimate update, comps workbook, sensitivity deck, or model-derived output and produce a decision-useful audit pack. This skill is a QA layer for formula integrity, source support, assumption hygiene, scenario quality, controls, and decision readiness.

Do not rebuild the model unless the user explicitly asks for remediation. Default to an audit memo, issue log, source tie-out ledger, and prioritized fix list.

The headline output is an audit verdict on permitted use: `Ready`, `Ready with caveats`, `Not ready`, or `Not assessable`. This skill does not turn an unsupported model into an investment recommendation. When required valuation, scenario, or market-price outputs are absent, state that the model or model package cannot support portfolio action until remediated and re-audited.

## Core Principles

- Review before changing; never overwrite formulas, assumptions, outputs, or tabs unless asked.
- Separate model mechanics from investment judgment.
- Tie material outputs to workbook tabs/cells, source documents, or explicit assumptions.
- Prioritize by decision impact, not issue count.
- Escalate unsupported decision drivers even when formulas are mechanically clean.
- Distinguish a broken model from an undocumented or unsupported underwriting assumption, a stale forecast, a missing source bridge, and a missing decision-output layer.
- A three-statement operating model need not itself contain target price or valuation; for portfolio-decision use, require a linked valuation/scenario decision output in the model package before concluding that forecasts support action.
- Label auditor-created stresses as `Illustrative audit sensitivity` unless the user explicitly approves them as revised base-case assumptions.

## Workflow

1. **Confirm audit mandate.** Identify model type, intended model-package scope, decision context, materiality threshold, and requested output. Determine whether the workbook is expected to contain decision outputs or to feed a separate linked valuation/scenario layer.
2. **Run workbook inspection when available.** For `.xlsx` workbooks, use the helper as a starting point:

```bash
python scripts/audit_workbook.py path/to/model.xlsx --out-dir audit_output
```

Dependency note: the helper requires `openpyxl`; install the local dependency file in a fresh environment:

```bash
python -m pip install -r scripts/requirements.txt
```

3. **Map key outputs.** Trace valuation, target-price, estimate, earnings, event, risk, or common-equity downside outputs back to assumptions, formulas, source tabs, and source documents.
4. **Apply formula and workbook controls.** Check inconsistent formulas, hardcodes, broken links, hidden sheets, volatile functions, bypassed assumption tabs, circularity, plugs, unsupported checks, and formulas that do not tie to schedules.
5. **Review first-tab decision readiness.** Flag missing or thin first-visible `Cover` tabs when net read, key outputs, scenario metrics, model status, source posture, warnings/hard failures, chart-ready data, and workbook navigation are buried.
6. **Tie assumptions to evidence.** Use `references/tieout-and-source-checks.md` and `financial-source-of-truth` standards to label primary facts, claims, estimates, assumptions, inferences, and unsupported items.
7. **Review scenarios and downside.** Test whether scenarios focus on true value/risk drivers and whether downside captures liquidity/refinancing risk as common-equity impairment, multiple compression, estimate cuts, cash-burn dilution, or event failure as relevant. Treat auditor-created replacement assumptions or stress math as diagnostic illustrations, not repaired model forecasts.
8. **Build issue log.** Include severity, finding type, category, location, finding, decision impact, recommended fix, and owner. Use reader-facing finding types: `Formula/control defect`, `Source contradiction`, `Unsupported assumption`, `Missing forecast refresh`, `Missing decision output`, or `Not comparable without bridge`.
9. **Deliver audit pack.** Choose rapid screen or full audit pack based on user need.

## Sub-agent decomposition

For complex medium/large requests, use sub-agents where available; otherwise emulate the split as named workstreams. Suggested lanes: workbook controls, formula review, source tie-out, scenario/downside review, and issue prioritization. Keep this skill as the lead: reconcile conflicts, source labels, assumptions, open items, final QA, and the user-facing answer.


## Output Contract

**Rapid screen**

- model health score;
- top issues by severity;
- decision readiness;
- immediate fixes.

**Full audit pack**

Default substantial workbook audits to a reader-facing `model_audit_report.html`, produced as a polished standalone HTML model-audit report following `../../shared/html-artifact-standard.md`, plus an optional `model_audit_issues.xlsx` companion workbook. Keep `model_audit_findings.json`, `formula_exception_log.csv`, `source_tieout_ledger.csv`, raw workbook maps, and support notes behind the HTML/workbook unless the user asks for audit files. In the default delivery message, link only the primary HTML report and any requested user-facing workbook; mention supporting audit files without linking them unless the user asks.

- executive summary;
- readiness posture;
- issue log;
- formula/workbook controls;
- source tie-out findings;
- assumption and scenario critique;
- sensitivity review;
- remediation sequence;
- open evidence requests;
- appendix with formula exceptions and tie-out ledger.

Use `dashboard-builder` and `references/dashboard-map.md` only when the user explicitly requests a standardized dashboard, reusable validated template, model-health cockpit, remediation tracker, or structured payload-driven render. A substantial ordinary audit should remain a flexible standalone HTML report rather than a fixed dashboard-module package.

## HTML Guidance

For a substantive standalone HTML model-audit report, load `../../shared/html-artifact-standard.md` and use this audit-specific hierarchy:

1. Audit verdict and permitted use: whether the model may support the stated decision, the top blocker, the scope reviewed, and any limitations on recalculation or source verification.
2. Critical blockers and what appears mechanically sound, separated clearly so a linked workbook is not confused with an underwritten forecast.
3. Decision-output assessment: whether a linked valuation/scenario layer, current-price anchor, estimate bridge, or downside view exists and is supportable for the requested use.
4. Priority issue log with workbook location, finding type, decision impact, and remediation.
5. Source tie-out findings, diagnostic sensitivities, controls, remediation sequence, evidence requests, and method/limitations.

Additional rules:

- Keep the headline as an audit verdict. When decision outputs are absent or unreliable, say `Do not use for portfolio action until remediated and re-audited`; do not imply an `add`, `trim`, `exit`, `hedge`, or `wait for proof` recommendation from an audit-only mandate.
- Classify decision-relevant findings as `Formula/control defect`, `Source contradiction`, `Unsupported assumption`, `Missing forecast refresh`, `Missing decision output`, or `Not comparable without bridge`; do not make every unsupported forecast assumption sound like a formula error.
- Display auditor-created cash, leverage, EPS, valuation, or scenario stresses as `Illustrative audit sensitivity`; do not represent a diagnostic stress as a corrected forecast or revised base case.
- When reviewing an operating or three-statement model, distinguish absence of valuation inside that workbook from absence of a linked valuation/scenario decision output in the overall package. The latter blocks portfolio-decision use when required by the mandate; the former is not automatically a model defect.
- Do not feature a current-price or market-data anchor in the verdict, headline KPI row, or decision-output assessment unless the cited source has been verified for the correct security and as-of date; if it cannot be verified, state that the external price anchor is unavailable.
- Cite critical findings with workbook sheet/cell or range plus controlling source location where available. Keep source/as-of posture and limitations such as cached outputs versus native recalculation visible.
- Visually inspect local HTML via local headless-browser screenshots, not the in-app Browser plugin, and iterate on hierarchy, legibility, table density, citation rendering, and whether the audit verdict and top fixes are immediately visible.

## Handoffs

- `financial-source-of-truth`: evidence hierarchy, stale/conflicting data, citations, labels.
- `excel-data-cleaner`: malformed tables or unclear row/column grain before audit.
- Model/research builders: rebuild, refresh, expand, or stress-test after audit.
- `memo-builder`: convert audit findings into a decision memo.
- `deck-report-qc`: reconcile audited model outputs to decks, board packs, IC memos, or client presentations.

## Resources

- `scripts/audit_workbook.py`: static workbook inspection helper.
- `scripts/requirements.txt`: workbook helper dependency declaration.
- `references/audit-playbook.md`: audit modes by model type.
- `references/formula-and-workbook-controls.md`: formula and architecture checks.
- `references/tieout-and-source-checks.md`: source tie-out process and evidence labels.
- `references/issue-taxonomy.md`: severity and issue categories.
- `references/output-templates.md`: audit memo, issue log, tie-out ledger, and IC-ready templates.
- `references/dashboard-map.md`: dashboard mapping for model health, formula exceptions, source tie-outs, and readiness.
- `references/p0-integrations.md`: coordination with launch skills.

## Final QA

Confirm severity is tied to decision impact, model issues are separated from evidence issues, audit sensitivities are identified as illustrative rather than repaired forecasts, missing decision-layer scope is not confused with a formula defect, source/as-of dates are visible, unsupported assumptions are not buried, remediation steps are concrete, and no user workbook content was destructively changed.

## Equity Valuation PM Standard

Load `shared/equity-valuation-pm-standard.md` and `shared/pm-judgment-heuristics.md` for substantial model, valuation, scenario, model-update, or audit work.

The output must state what the current stock price implies, the variant estimate path, whether upside is driven by fundamentals, multiple expansion, mix, capital return, sentiment, or event probability, what breaks first in downside, what changes target, rating, sizing, hedge, trim, exit, or watchlist status, and what evidence is missing.

Keep equity valuation as the center of gravity. Debt is allowed only as an input to common-equity value through net debt, cost of debt, leverage, liquidity, refinancing risk, or downside equity impairment. Use Credit Markets for bond comps, loan comps, CDS, spread/yield relative value, covenant-package analysis, debt-security valuation, recovery waterfall, restructuring valuation, creditworthiness, private-credit / public-credit instrument underwriting, or distressed claim valuation.
