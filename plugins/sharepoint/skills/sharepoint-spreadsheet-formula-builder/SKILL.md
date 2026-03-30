---
name: sharepoint-spreadsheet-formula-builder
description: Design, repair, and roll out formulas in SharePoint-hosted workbooks with connector-aware retrieval, validation, and upload discipline. Use when the user wants to add a formula column, fix a broken formula, choose between a fill-down formula and a spill formula, build a lookup or filter formula, or reuse workbook logic safely.
---

# SharePoint Spreadsheet Formula Builder

Use this skill when the formula itself is the task and the workbook lives in SharePoint.

This workflow depends on the Microsoft SharePoint connector for file discovery and binary transfer, not formula-aware editing. The relevant connector actions on the exposed Codex surface are `get_site`, `search`, `list_recent_documents`, `list_folder_items`, `fetch`, `update_file`, and `upload_file`.

In Codex, use those direct Microsoft SharePoint app tools rather than generic MCP resource-listing flows. The backend wrapper routes connector actions through tool calls, not through user-facing SharePoint resource enumeration.

Read `./references/formula-patterns.md` before drafting the first formula. The point is to refresh exact Excel syntax, formula-shape choices, and SharePoint-specific rollout risks before editing the workbook.

## Workflow

1. Ground the formula in the live workbook first: exact SharePoint file, sheet, target cell or output column, input columns, and a few representative rows.
2. Use the SharePoint connector flow to locate the exact workbook:
   - `get_site` when you need to confirm the canonical site before path-based operations
   - `search` when you have keywords
   - `list_recent_documents` when the user means a recently accessed file or you have no search keywords
   - `list_folder_items` when the folder is already known
   - prefer the exact Graph-style `url` returned by `search` or `list_recent_documents` as the input to `fetch`
   - `fetch` once for extracted content to identify sheets and likely target ranges
   - `fetch(download_raw_file=true)` for the actual `.xlsx` bytes before editing formulas
3. Choose the formula shape deliberately:
   - table or row formula when the logic is local to one record and should fill down
   - spill formula when one anchor cell should populate the whole output range
   - lookup formula when the task is key-to-value retrieval
   - filter or summary formula when the output should derive a live subset or aggregate view
   - `LET` when repeated subexpressions make the formula hard to read or maintain
   - `LAMBDA` or a named formula only when the logic is conceptually reusable and the workbook environment supports it
   - if workbook compatibility is unknown, bias toward broadly compatible Excel formulas before modern dynamic-array features
4. Preserve the workbook's existing reference style. If the sheet already uses structured references in tables, continue using them instead of switching to ad hoc A1 references.
5. Draft the formula in a helper cell, scratch column, or local workbook copy first rather than replacing the production range immediately.
6. Test on a small representative slice, including blanks, missing lookups, spill collisions, and unusual values.
7. Roll the formula out to the intended target cells while preserving neighboring formulas, formatting, named ranges, and table behavior.
8. Write the revised workbook back through the connector using the exact drive-root-relative path from SharePoint metadata:
   - `update_file` when replacing an existing workbook at a known path
   - `upload_file` only when creating a new workbook or when the workflow genuinely requires upload semantics
9. Re-fetch the workbook or update metadata and verify the exact target formula cells or output column after upload.

## SharePoint-Specific Safety

- Do not treat a SharePoint workbook like a live Google Sheet. Formula design happens against a downloaded `.xlsx`, then goes back through the SharePoint file-update path.
- The connector does not expose cell-level formula editing, workbook recalculation controls, or formula-engine introspection. Do not imply that SharePoint tooling itself validated Excel semantics beyond successful file round-trip.
- The implementation prefers exact Graph item URLs returned by `search` and `list_recent_documents`. Browser or sharing URLs are supported by `fetch`, but they are fallback inputs rather than the preferred primary path.
- `search` only returns text-friendly document types and enforces the connector's file-size gate. If `search` is blank, the implementation falls back to recent documents instead of running an unrestricted keyword search.
- If local tooling does not recalculate formulas exactly, verify both the formula text and the dependency ranges, then say clearly that final computed values depend on Excel or SharePoint recalculation after upload.
- Treat modern Excel functions such as `XLOOKUP`, `FILTER`, `LET`, and `LAMBDA` as workbook-compatibility choices, not connector features. Use them when the target workbook is expected to open in Microsoft 365-era Excel or Excel for the web, and call out compatibility risk otherwise.
- When compatibility is unclear, prefer conservative formulas such as `IF`, `IFERROR`, `SUMIFS`, `COUNTIFS`, `INDEX/MATCH`, and exact-match `VLOOKUP(FALSE)` over newer dynamic-array constructs.
- If the workbook uses Excel Tables, prefer table formulas because they auto-fill more safely and survive row insertions better than loose copied formulas.
- Before using a spill formula, inspect the intended spill range so the formula does not overwrite existing content after Excel recalculates it.
- For path-based writes, the implementation normalizes leading and trailing slashes away from drive-root-relative paths. Preserve the actual path from SharePoint metadata instead of rebuilding it from memory.
- If a write fails with `itemNotFound`, re-check the root-relative path from SharePoint metadata instead of guessing from the browser URL.

## Output Conventions

- Name the exact SharePoint workbook, sheet, and target cell or output column.
- Return the final formula exactly as it should be entered.
- State whether rollout should happen as a filled-down row formula, a table column formula, a spill formula from one anchor cell, or a named formula.
- If calculation support is uncertain, distinguish formula-text verification from value verification.
- If function compatibility is uncertain, say that explicitly instead of presenting the formula as universally safe for all Excel consumers.
- If compatibility drove the design choice, say which compatibility level you optimized for, for example conservative legacy Excel compatibility versus Microsoft 365 features.

## References

- For formula-shape heuristics and Excel syntax reminders, read `./references/formula-patterns.md`.
