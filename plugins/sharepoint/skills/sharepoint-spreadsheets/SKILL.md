---
name: sharepoint-spreadsheets
description: Edit SharePoint-hosted spreadsheet files while preserving workbook structure, formulas, and formatting. Use when the user wants to update a real spreadsheet in SharePoint rather than summarize extracted sheet text.
---

# SharePoint Spreadsheets

## Overview

Use this skill for `.xlsx` edits that start from SharePoint. Inspect the workbook structure before editing, preserve formulas and formatting, and upload the revised workbook back to the same SharePoint item only after verifying the exact change.

If the formula itself is the task, pair this with [../sharepoint-spreadsheet-formula-builder/SKILL.md](../sharepoint-spreadsheet-formula-builder/SKILL.md) so formula design, syntax checks, and rollout choices stay deliberate instead of being improvised during the workbook edit.

## Core Workflow

1. Use the site-scoped SharePoint discovery path to locate the exact workbook:
   - `get_site(...)` when the user already knows the site
   - `list_site_drives(...)` when the site is known but the library is not
   - `search(query=None, hostname=..., site_path=..., folder_path=...)` to browse a known site or folder
   - `search(query="...")` when the user actually has keywords
2. Prefer the exact `url` returned by keyword search or browse results when you later call `fetch`.
3. Fetch extracted content once to identify relevant sheets and the likely target area.
4. Fetch the raw `.xlsx` with `fetch(download_raw_file=true)`.
5. Inspect workbook structure before editing:
   - sheet names
   - used ranges or dimensions
   - formulas
   - headers
   - the most natural insertion point
6. Apply the edit with workbook-aware local tooling such as `openpyxl`, preserving workbook structure, formulas, and formatting.
7. Verify the exact inserted cells, rows, or section header after save rather than relying on a generic workbook-size change.
8. Write the revised workbook back with `update_file` using the exact drive-root-relative path from SharePoint metadata.
9. Confirm the SharePoint update metadata and, when possible, reopen the workbook locally to verify the targeted cells.

Use the direct Microsoft SharePoint app tools for this flow. Do not rely on generic MCP resource listing for SharePoint workbook discovery in Codex.

## Safety

- Do not flatten a workbook into CSV-like text when the user expects the original spreadsheet to remain editable.
- Preserve formulas, charts, sheet structure, and formatting unless the user explicitly asked to change them.
- Treat connector writes as full workbook replacement. `update_file` does not patch individual cells or formulas inside the existing workbook on the server.
- `fetch` enforces the connector's supported-file and max-size constraints. If raw workbook retrieval fails at the connector layer, stop and report the limitation instead of pretending the workbook was safely inspected.
- Do not teach or rely on user-recency as the primary browse path. Resolve the right site, library, and folder first when the workbook location is still ambiguous.
- If the workbook contains formulas, charts, or formatting-sensitive layouts, treat operations that can shift references or overwrite styled ranges as high risk and inspect carefully before saving.
- For structured additions such as Q&A sections, notes blocks, or assumption tables, prefer inserting them into the most natural non-formula sheet instead of the main projection grid unless the user explicitly asked otherwise.

## Verification

- Verify the exact target cells, rows, or inserted block.
- If you can verify content but not workbook fidelity more broadly, say that clearly instead of implying a full workbook QA pass.
