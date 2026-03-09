---
name: google-sheets
description: Analyze Google Sheets data, plan range-precise edits, and help with formulas or tabular transformations through connected Google Sheets data. Use when the user wants to inspect tabs or ranges, summarize spreadsheet contents, propose formulas, clean or restructure tables, or update cells with explicit range-level intent.
---

# Google Sheets

## Overview

Use this skill to turn spreadsheet data into precise range-aware analysis and edit plans. Anchor every recommendation in sheet names, ranges, headers, and formulas so the next action is explicit and low-risk.

## Preferred Deliverables

- Sheet briefs that summarize what a tab or range contains and where the issues are.
- Formula proposals with the exact cell or output column they belong in.
- Edit plans that specify ranges, current state, intended change, and reason.

## Workflow

1. Read the spreadsheet structure first. Identify the relevant sheet tabs, headers, key ranges, formulas, and any filtering or grouping logic before proposing changes.
2. Ground the task in exact ranges. Restate the sheet name, target columns, rows, or named ranges before suggesting edits.
3. When the request is exploratory, summarize the current data shape before drafting formulas or updates.
4. When the request is write-oriented, present the exact range-level change plan before applying broad edits or overwrites.
5. If the user asks to clean, normalize, or fix data, identify the affected tabs, ranges, and formulas before making changes.
6. Only make destructive, large-scale, or structure-changing edits when the user has clearly asked for them.

## Write Safety

- Preserve formulas, headers, frozen rows, and sheet structure unless the user requests a change.
- Treat sheet-wide overwrites, row or column deletes, and tab restructures as high-impact changes that require explicit confirmation.
- If a value could be either static text or a formula, state which one you intend to write.
- If multiple tabs or similarly named ranges exist, identify the exact target before editing.

## Output Conventions

- Always reference the sheet name and range when describing findings or planned edits.
- Prefer formulas, tables, and range-specific instructions over vague prose.
- For multi-range updates, use a compact table or list with range, proposed change, and reason.
- When summarizing data, explain what the table represents and highlight outliers, missing values, or inconsistent entries.
- When proposing formulas, include the exact formula, the intended output column or cell, and the dependency columns.

## Example Requests

- "Look at the revenue tab and tell me which rows are missing owner assignments."
- "Suggest the right formula for column G to classify each row by SLA status."
- "Summarize the data quality issues in this sheet before I clean it up."
- "Plan the exact range updates needed to normalize the date columns on the pipeline tab."

## Light Fallback

If the spreadsheet data is missing or incomplete, say that Google Sheets access may be unavailable or scoped to the wrong spreadsheet, then ask the user to reconnect or clarify the target sheet or range.
