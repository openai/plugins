# Table Formatting Deep Dive

When to read: any task that creates, updates, or formats a real Google Docs table.

## Critical Invariant

A new table must match the local document's connector-visible table pattern closely enough that it should read as native template content. In this blind environment, verify table structure, text, style requests, and connector-exposed width or cell metadata. Do not claim rendered page fit, visible alignment, or visual density unless the connector exposes enough data to prove it.

Unless the user or template clearly calls for a different treatment, the default table presentation should use a light blue header row with fully bold header text and alternating white/light-gray body rows.

## Native Table Workflow

1. Insert the surrounding section label text and `insertTable` in one `google_docs_batch_update` call when possible.
2. Immediately verify the table with the Google Docs `get_tables` connector action instead of inferring cell indexes from paragraph reads.
3. Use the returned table `startIndex` as the anchor for all table styling requests.
4. Use the returned per-cell `startIndex` values for content insertion.
5. Populate cells with absolute-index `insertText` writes in descending index order so earlier writes do not shift later targets.
6. After the first meaningful cell write, re-run `get_tables` and confirm the text landed in the intended row and column before continuing.
7. After full cell population, re-run `get_tables` and confirm every row and column landed in the intended cell.
8. Only after content is verified should you style the table with `updateTableCellStyle`, `updateTableColumnProperties`, or text-style requests.
9. Never create a new table from inside an existing table cell unless the template already contains that nested table and the task explicitly calls for editing it.
10. Before styling a new standalone table, inspect the nearest comparable existing table through connector metadata and mirror its connector-visible presentation pattern unless the task explicitly calls for a different one.

## Table Request-Shape Reminders

1. `updateTableColumnProperties` should target `tableStartLocation.index` from `get_tables`.
2. `updateTableCellStyle` should use `tableRange.tableCellLocation.tableStartLocation`, plus `rowIndex` and `columnIndex`; do not guess row offsets from document indexes.
3. Header and stripe fills are safe as row-wide `updateTableCellStyle` requests once the table anchor is verified.
4. Before creating, inserting into, or formatting a table, force the intended table text to `NORMAL_TEXT`; do not let heading or inherited styles flow into cells.
5. Populate and verify the table before any text-style writes. Header text styling is brittle if applied before the final cell indexes are known.
6. Prefer styling header text cell by cell using the final `get_tables` cell ranges; do not rely on one broad header-row text range if later edits may shift indexes.
7. Header rows should be fully and consistently styled across every header cell, not partially styled.
8. Unless the user or template says otherwise, use a light blue header row and alternating white/light-gray body rows as the default scanability treatment.
9. Choose a conservative schema before insertion. If a portrait-page table would need many medium-width columns, reduce column count by merging related fields.
10. Explicitly clear inherited text styling in table cells before the final styling pass. Body cells should be `bold: false`; only header cells should be re-bolded afterward.
11. For supporting lines above or below tables, use exact text-range lookup for hyperlinks rather than manual index math.
12. For existing two-column label/value tables, verify that new content is going into the value column, not the label column, before bulk-filling the section.
13. If the intended insertion point is inside a structured table cell, assume a new standalone table usually does not belong there. Place the standalone table at a deliberate document-level location outside the outer table, with its own intro label.
14. Do not apply a generic table look when the document already has a local connector-visible table pattern. Match the nearest analogous table's exposed fills, borders, typography, and width hints before inventing a new style.

## Table Shape

1. Start by asking whether the column count is justified.
2. Narrow short utility columns and keep them proportionate to their actual content when column width controls are available.
3. Keep longer narrative columns wide enough in the schema to avoid obvious overpacking.
4. Design the schema before inserting the table. If multiple fields are all medium-to-long, combine at least one pair up front.
5. Prefer compact composite headers when they reduce width without harming scanability.
6. Do not preserve every source dimension as its own column just because the source had them separated.
7. For compact summary tables, default toward 4 or 5 columns total.
8. Prefer merging short categorical fields into a richer combined column when that produces a cleaner doc block than a grid of skinny columns.
9. Choose column count from the intended document footprint and likely text lengths, not from the source data model.
10. Do not use tables as the default substitute for charts, diagrams, or design. Use them when comparison, ownership, timing, or structured choices become easier to scan.
11. If a document already contains several tables, require a clear reason before adding another one. Consider a short prose block, metric card, or grouped bullets instead.
12. Vary table shape intentionally across a long document. Repeated grids with the same header treatment and column rhythm create monotony even when each table is individually valid.
13. Treat four or more columns as high risk for narrative documents. Use them only when the entries are short and the table remains readable in the generated HTML or connector metadata.

## Styling Order

1. Create the table and verify it with `get_tables`.
2. Populate cells in descending absolute-index order.
3. Re-run `get_tables` and verify final placement.
4. Reset text styling across all final cell ranges so body cells are normal-weight and free of inherited emphasis.
5. Apply header text styling cell by cell.
6. Apply header-row fill and alternating body-row fills.
7. Adjust column widths after content exists, not before.
8. Re-read with `get_tables` and verify connector-visible structure, cell text, fills, text styles, links, and width properties where available.
9. Export the document as `text/html` when available and verify table markup/CSS: `<table>` placement, row and cell order, header/background colors, font family and size, padding, border styles, page-body max width, and column width declarations.
10. If the connector and HTML export do not expose rendered fit, do not claim the table visually fits the page; report only the connector/HTML-verified properties.

## Connector-Observable Acceptance Criteria

1. Correct row and column count.
2. Correct cell text in every intended cell.
3. Header row is fully bold and uses the intended header-row fill consistently across all header cells.
4. Body rows use consistent alternating fills unless the user or template clearly wants a different treatment.
5. Body typography stays consistent across all cells.
6. Body cells are not accidentally bold or otherwise inheriting emphasis from adjacent headings or labels.
7. The table is at the intended document level, not accidentally nested inside another table cell.
8. Header cells do not contain partial hyperlinks, partial bolding, or other split formatting inside a single intended label.
9. Connector-exposed column width properties are set intentionally when width tuning is part of the task.
10. HTML export shows the expected table structure and CSS when export is available.
11. Any unverified rendered properties, such as clipping, page breaks, or visual alignment, are reported as unverified rather than accepted.

## HTML Export Table Checks

Use HTML export as a second pass after `get_tables`, especially when table layout matters.

Check for:

1. generated `<table>` markup containing the expected row and cell text
2. header fill and alternating row fills as CSS colors
3. header text and body text font family and size
4. table width and column width values in points when present
5. expected paragraphs before and after the table, including `</table><p` ordering for post-table takeaways
6. no duplicated table content or leftover placeholder text in the exported body
7. repeated table colors, widths, or header patterns that make the document read as one long grid

If a check requires regex over escaped HTML, prefer `includes(...)`, parsing the JSON wrapper, or a small HTML-aware parser over brittle regular expressions.
