---
name: sharepoint-spreadsheets
description: Edit SharePoint-hosted spreadsheet files while preserving workbook structure, formulas, and formatting. Use when the user wants to update a real spreadsheet in SharePoint rather than summarize extracted sheet text.
---

# SharePoint Spreadsheets

## Overview

Use this skill for `.xlsx` edits that start from SharePoint. Inspect the workbook structure before editing, preserve formulas and formatting, and upload the revised workbook back to the same SharePoint item only after verifying the exact change.

## Core Workflow

1. Search or list folder items to locate the exact workbook.
2. Fetch extracted content once to identify relevant sheets and the likely target area.
3. Fetch the raw `.xlsx`.
4. Inspect workbook structure before editing:
   - sheet names
   - used ranges or dimensions
   - formulas
   - headers
   - the most natural insertion point
5. Apply the edit with the `spreadsheet` skill or `openpyxl`, preserving workbook structure, formulas, and formatting.
6. Verify the exact inserted cells, rows, or section header after save rather than relying on a generic workbook-size change.
7. Upload the revised workbook back to the same SharePoint item.
8. Confirm the SharePoint update metadata and, when possible, reopen the workbook locally to verify the targeted cells.

## Safety

- Do not flatten a workbook into CSV-like text when the user expects the original spreadsheet to remain editable.
- Preserve formulas, charts, sheet structure, and formatting unless the user explicitly asked to change them.
- If the workbook contains formulas, charts, or formatting-sensitive layouts, treat operations that can shift references or overwrite styled ranges as high risk and inspect carefully before saving.
- For structured additions such as Q&A sections, notes blocks, or assumption tables, prefer inserting them into the most natural non-formula sheet instead of the main projection grid unless the user explicitly asked otherwise.

## Verification

- Verify the exact target cells, rows, or inserted block.
- If you can verify content but not workbook fidelity more broadly, say that clearly instead of implying a full workbook QA pass.
