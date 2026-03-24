---
name: google-sheets-formula-builder
description: Design, repair, and roll out Google Sheets formulas with better syntax recall and validation discipline. Use when the user wants to add a formula column, fix a broken formula, choose between a row formula and a spill formula, build a lookup or filter formula, or turn repeated logic into a reusable named function.
---

# Google Sheets Formula Builder

Use this skill when the formula itself is the task.

Read `./references/formula-patterns.md` before drafting the first formula. The point is not to relearn Sheets from scratch. It is to refresh exact syntax and a few high-value function constraints before writing.

## Workflow

1. Ground the formula in the live sheet first: exact input columns, target output cell or column, and a few representative rows.
2. Choose the formula shape deliberately:
   - row formula when the logic is local to one row and should copy down
   - spill formula when one formula should populate a whole output range
   - lookup formula when the task is key-to-value retrieval
   - filter/query formula when the task is to derive a subset or summary table
   - named function only when the same logic is conceptually reusable
3. Draft the formula in one helper cell or a scratch location first.
4. Test on a small representative slice, including likely edge cases.
5. Iterate until the sample output is correct, then roll the formula out to the intended target range.

## Output Conventions

- Name the exact target cell or output column.
- Return the final formula exactly as it should be entered.
- If rollout matters, say whether the formula should be filled down, spilled from one anchor cell, or turned into a named function.

## References

- For syntax reminders, formula-shape heuristics, and official Google Sheets docs links, read `./references/formula-patterns.md`.
