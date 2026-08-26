# Workbook And Export Boundary

`comps-valuation` owns the comps judgment layer in both modes. In `report` mode it may render compact tables in chat for quick reads, and substantial reusable comps work should become a polished standalone HTML comps report following the shared HTML artifact standard. Use `dashboard-builder` only when the user explicitly selects a standardized dashboard, reusable dashboard template, PM cockpit, or structured payload-driven render. Use `workbook` mode for CSV, XLSX, Google Sheets, refreshable, formula-driven, or external-circulation workbook artifacts.

Use `comps-valuation` in `workbook` mode when the user asks for:

- Excel or Google Sheets comps
- CSV/exported/downloadable tables
- refreshable peer universes
- formula-driven EV bridges
- source/provenance tabs
- valuation range sensitivity tables
- audit-ready workbook outputs
- file deliverables for IC, committee, client, board, lender, or senior circulation

If the user provides a spreadsheet or provider export, `comps-valuation` can use it as source context for the comps read-through, standalone HTML report, or explicitly selected dashboard payload. Use `excel-data-cleaner` first when the table is too messy to read reliably.
