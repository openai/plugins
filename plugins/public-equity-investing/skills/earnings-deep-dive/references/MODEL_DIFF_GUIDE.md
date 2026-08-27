# Model Diff Methodology (Signal, not cell noise)

## Table of contents
1. [Goals](#goals)
2. [What to diff](#what-to-diff)
3. [How to rank changes](#how-to-rank-changes)
4. [Workbook diff strategy](#workbook-diff-strategy)
5. [Using the script](#using-the-script)

---

## Goals
The diff exists to answer:
- **What changed in the model?** (inputs and key outputs)
- **Why did it change?** (source-tagged rationale)
- **Which changes matter most for near-term valuation KPIs?**

## What to diff
1) **Driver inputs** (from `driver_registry.csv`)
2) **Key outputs** (from `output_registry.csv`)
3) Optional: scenario switches and key assumptions (WACC, terminal growth, etc.) if your model has them as drivers.

Do NOT diff:
- Formatting, column widths, styles
- Intermediate calculation blocks unless they are decision-critical

## How to rank changes
Rank by estimated impact priority. In absence of a full valuation engine:
1. Next-quarter revenue/EPS/FCF changes
2. FY revenue/EPS/FCF changes
3. Margin and opex run-rate assumptions
4. Working capital and capex assumptions

## Workbook diff strategy
- Prefer **named ranges** for stability.
- If using cells, diff only the explicit cell map in the registry (not the whole sheet).
- Treat blanks carefully:
  - blank vs 0 can be meaningful; retain both
  - if a cell contains a formula, diff the evaluated value and optionally the formula string (advanced)

## Using the script
Run:

```bash
python scripts/model_diff.py \
  --old <prior_model.xlsx> \
  --new <updated_model.xlsx> \
  --driver-registry <driver_registry.csv> \
  --output-registry <output_registry.csv> \
  --out output/audit/WhatChanged_Diff.csv
```

The script outputs:
- `Category` = Driver or Output
- Old/New/Delta
- Rank (simple heuristic)

Then add `SourceTag` and `Why` where missing.
