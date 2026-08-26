# Workbook Artifact Standard

Use this standard for Public Equity Investing skills that generate an `.xlsx` model, tracker, export pack, or workbook-style deliverable.

## Core rule

Generated workbooks must include a first visible sheet named `Cover`, or a workflow-specific equivalent such as `Update_Cover` for a model-update control pack, unless the task is explicitly a non-destructive edit of a user-provided workbook.

The cover is an analyst and PM insight dashboard, not a raw data table, README, or table of contents. It should answer, within one screen:

- what the workbook is and what decision it supports;
- the recommendation, net read, or decision question;
- the headline output or read-through;
- the key metrics, cases, or events that drive the answer;
- the major sensitivities, catalyst/risk flags, or thesis breaks that could change the answer;
- the model/workbook status and decision-readiness label, including whether the output is screen-grade, senior-review-ready, decision-grade, blocked, or not-decision-ready;
- the source posture, stale or missing evidence, warnings, and hard failures;
- where the reviewer should go next inside the workbook.

Workbook navigation is secondary. A table-of-contents cover is not enough. A cover that only explains workbook contents is not sufficient.

## Required cover blocks

Include the following blocks whenever the underlying data exists. If a block cannot be supported, include it with a clear `not provided`, `not modeled`, or `needs source support` note rather than silently omitting it.

| Block | Required content |
|---|---|
| Header / status strip | Company or issuer, ticker/security, workbook type, as-of or valuation date, currency, units, freeze time, model status, artifact level, workbook mode. |
| Executive read-through | Two to four concise sentences or rows describing the main implication and how much confidence to place on it. |
| KPI tiles | The highest-signal metrics for the workbook type: value/share, scenario range, revenue/EBITDA/FCF, liquidity, peer multiples, event counts, or data-quality metrics. |
| Scenario / output table | Base/upside/downside, bull/base/bear, valuation range, top catalysts, cleaning summary, thesis state, or comparable-company statistics. |
| Visuals or chart-ready data | At least two chart-ready tables. Add native charts when the writer supports them; otherwise label the chart-ready tables clearly. |
| Source posture | Primary sources used, source dates, confidence labels, stale items, missing source support, and unsupported assumptions. |
| QA and caveats | Hard failures, warnings, denominator distortions, formula/value-export caveats, open checks, and recalc limitations. |
| Workbook map | Tab name, role, what the reviewer should use it for, and notable limitations. |

## Skill-specific mapping

- `comps-valuation`: target snapshot, peer universe, selected multiples, valuation range, peer medians/quartiles, outlier and denominator flags, EV bridge caveats, source gaps, QA status.
- `dcf-model-builder`: valuation range, value/share by case, WACC and terminal assumptions, terminal value share of EV, PV bridge, key value drivers, sensitivity highlights, source and QA posture.
- `three-statement-model-builder`: final revenue, EBITDA, FCF, cash, liquidity trough, peak net leverage, covenant or liquidity warnings, driver deltas, source and QA posture.
- `catalyst-calendar`: top catalysts, urgency/impact counts, next 30/60/90 day calendar pressure, owner/prep status, source confidence, stale or unconfirmed events.
- `earnings-preview`: consensus bar, whisper deltas, key KPI watch items, scenario framing, source freeze, unsupported live-market sections, call watch items.
- `thesis-tracker`: thesis status, conviction/rating, base/bull/bear value, pillar health, KPI evidence, upcoming catalysts, estimate revisions, open questions.
- `excel-data-cleaner`: input and output row counts, inferred grain/domain, cleaning actions, quality issue counts, missingness/duplicate/type-conversion flags, preserved raw tabs, downstream use limitations.

## Formula Workbook Inspection Gates

Formula workbooks must clear model-specific thresholds before the skill may label them `banker_formula_workbook`:

- DCF formula workbooks: at least 800 formulas, required sheets present, required formula-bearing sheets populated, `Cover` first, styles preserved, no external workbook links, and named ranges or a source-to-cell anchor map such as `model_citations.json`.
- Three-statement formula workbooks: at least 1,100 formulas, required sheets present, required formula-bearing sheets populated, `Cover` first, styles preserved, no external workbook links, and named ranges or a source-to-cell anchor map such as `model_citations.json`.

The inspection threshold should be high enough to catch accidental flattening of the bundled formula template, not just prove that a few formulas survived.

## Audit expectation

`model-audit-tieout` should flag generated or reviewed workbooks that lack a decision-useful first visible cover/dashboard. A workbook can pass mechanical formula checks but still be weak for review if source posture, model status, warnings, and key outputs are buried in later tabs.
