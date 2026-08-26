# Table Formatting Deep Dive

When to read: any task that creates, updates, or formats a real Google Docs table.

## Critical Invariant

A net-new table must match the local document's connector-visible table pattern closely enough that it should read as native template content. An existing template table and its applicable adjacent instructions govern its semantic schema and presentation; the defaults in this reference apply only where the user and template are silent. In this blind environment, verify table structure, text, style requests, and connector-exposed width or cell metadata. Do not claim rendered page fit, visible alignment, or visual density unless connector readback, HTML export, or PDF-export visual QA proves it.

Unless the user or template clearly calls for a different treatment, the default table presentation should use a light blue header row with fully bold header text and alternating white/light-gray body rows.

For net-new tables, table body and header text should normally be at least 9.5 pt and must not be below 9 pt without an explicit user or legal requirement. For an existing template, match the canonical peer table even when it is smaller; report a readability concern rather than silently redesigning it.

## Native Table Workflow

1. Insert the surrounding section label text and `insertTable` in one `mcp__codex_apps__google_drive._batch_update_document` call when possible.
2. Immediately verify the table with the Google Docs `get_tables` connector action instead of inferring cell indexes from paragraph reads.
3. Use the returned table `startIndex` as the anchor for all table styling requests.
4. Use the returned per-cell `startIndex` values for content insertion.
5. In the first table write after `get_tables`, include the normal-style reset for the whole new table and adjacent blank separator before or alongside cell population: set table-cell paragraphs to `NORMAL_TEXT`, clear inherited bold/italic/underline where appropriate, and set the peer table's body font family/size if connector metadata exposes it. For table cloning with known text, combine descending `insertText` requests with text/paragraph style resets over the calculated post-insert cell text ranges in the same batch when the ranges are straightforward. Do not wait for final readback to discover heading-sized or inherited text in the table.
6. Populate cells with absolute-index `insertText` writes in descending index order so earlier writes do not shift later targets.
7. After the first meaningful cell write, re-run `get_tables` and confirm the text landed in the intended row and column before continuing.
8. After full cell population, re-run `get_tables` and confirm every row and column landed in the intended cell.
9. Only after content is verified should you apply semantic table styling such as header bolding, header/body fills, borders, or column widths.
10. Never create a new table from inside an existing table cell unless the template already contains that nested table and the task explicitly calls for editing it.
11. Before styling a new standalone table, inspect the nearest comparable existing table through connector metadata and mirror its connector-visible presentation pattern unless the task explicitly calls for a different one.

## Expanding Or Repopulating Template Tables

When a supplied template already contains the table for the requested information, treat that table and its applicable adjacent instructions as the structural and formatting authority:

1. Populate the existing table in place when its schema can express the result, and extend that schema when an applicable user or template instruction requires it. Do not delete and recreate it merely because rebuilding is easier.
2. When the task requires extra rows or columns, first sample canonical header, ordinary body, alternating-row, label, and total cells. Record their borders, fills, padding, vertical alignment, widths, paragraph style, font family, size, weight, color, and emphasis.
3. Extend the existing native table when the available request path supports it. If reconstruction is unavoidable, apply the sampled table and cell signatures to the replacement before considering it complete.
4. Newly added rows and columns inherit their semantic peer's style: header from header, body from the correct stripe or body class, labels from labels, and totals from totals. Do not substitute a generic blue-header table style in a document with a custom template style.
5. Preserve the original table's document-level position, surrounding labels, spacing, and width behavior. Schema expansion is not permission to restyle neighboring headings or body text.
6. After population, compare the resulting header and body-cell signatures against the sampled template peers. Correct cell text with default borders, fills, font, size, or padding is a failed template adaptation.

When a source table has more columns than the template, first follow any applicable instructions in or around the template table. If those instructions are silent, preserve the row and column roles needed to keep the intended comparisons, distinctions, ordering, and relationships independently readable. Group fields only when doing so does not change that semantic structure. Page fit, compactness, or a general column-count preference does not authorize contradicting the template schema or its instructions. Any extension keeps the template's table style.

## Boxed Tables And Lists In Cells

Treat an existing table used as a visual box or content container as a table to fill, not as a location for another nested table.

1. Read the outer table and resolve the exact target cell by table identity, row, and column.
2. Preserve the outer table's dimensions, borders, fills, widths, and neighboring cells.
3. Insert list item text without typed markers, re-read final paragraph ranges, and apply native list semantics using `reference-response-and-list-format.md`.
4. Verify both the table cell and connector-visible list metadata.
5. Never create a nested table unless the source template already uses that structure and the user explicitly requests it.

## Explicit Global Table Formatting

Use this workflow only when the request explicitly says `all`, `every`, `throughout`, or otherwise requires consistent formatting across analogous tables:

1. Inventory the complete target table set once, including structural exceptions.
2. Translate the request into a canonical signature containing only the fields the user asked to normalize.
3. Pilot one representative table and verify that out-of-scope properties remain unchanged.
4. Apply the signature to every target using live table identities and bounded batches.
5. Re-read every target and reconcile the expected, verified, and explicit-exception counts.

Do not normalize unrelated typography, widths, borders, or body styles merely because one table field must be consistent.

## Table Request-Shape Reminders

1. `updateTableColumnProperties` should target `tableStartLocation.index` from `get_tables`.
2. `updateTableCellStyle` should use `tableRange.tableCellLocation.tableStartLocation`, plus `rowIndex` and `columnIndex`; do not guess row offsets from document indexes.
3. Header and stripe fills are safe as row-wide `updateTableCellStyle` requests once the table anchor is verified.
4. Before creating, inserting into, or formatting a table, force the intended table text to `NORMAL_TEXT`; do not let heading or inherited styles flow into cells.
5. The first table-formatting batch after `get_tables` must include a normal text reset across all new cell ranges and the blank paragraph/table boundary around the table. This is separate from semantic header styling and prevents inherited heading font size from leaking into table content.
6. Populate and verify the table before header text-style writes. Header text styling is brittle if applied before the final cell indexes are known.
7. Prefer styling header text cell by cell using the final `get_tables` cell ranges; do not rely on one broad header-row text range if later edits may shift indexes.
8. Header rows should be fully and consistently styled across every header cell, not partially styled.
9. Unless the user or template says otherwise, use a light blue header row and alternating white/light-gray body rows as the default scanability treatment. This default never overrides a sampled template table style.
10. For a net-new table or user-authorized redesign without a governing schema, choose a conservative schema before insertion. If a portrait-page table would need many medium-width columns, reduce column count by merging related fields only when their distinct roles and relationships remain clear.
11. Explicitly clear inherited text styling in table cells before the final styling pass. Body cells should be `bold: false`; only header cells should be re-bolded afterward.
12. For supporting lines above or below tables, use exact text-range lookup for hyperlinks rather than manual index math.
13. For existing two-column label/value tables, verify that new content is going into the value column, not the label column, before bulk-filling the section.
14. If the intended insertion point is inside a structured table cell, assume a new standalone table usually does not belong there. Place the standalone table at a deliberate document-level location outside the outer table, with its own intro label.
15. Do not apply a generic table look when the document already has a local connector-visible table pattern. Match the nearest analogous table's exposed fills, borders, typography, and width hints before inventing a new style.

## Table Shape Defaults For Net-New Or Explicitly Redesigned Tables

1. Start by asking whether the column count is justified.
2. Narrow short utility columns and keep them proportionate to their actual content when column width controls are available.
3. Keep longer narrative columns wide enough in the schema to avoid obvious overpacking.
4. Design the schema before inserting the table. If multiple fields are all medium-to-long, combine at least one pair up front.
5. Prefer compact composite headers when they reduce width without harming scanability.
6. Do not reproduce every source dimension as its own column merely because the source separated them when no user or template instruction, semantic role, or intended comparison requires that separation.
7. For compact summary tables, default toward 4 or 5 columns total.
8. Prefer merging short categorical fields into a richer combined column when that produces a cleaner doc block than a grid of skinny columns.
9. Choose column count from the intended document footprint and likely text lengths, not from the source data model.
10. Do not use tables as the default substitute for charts, diagrams, or design. Use them when comparison, ownership, timing, or structured choices become easier to scan.
11. If a document already contains several tables, require a clear reason before adding another one. Consider a short prose block, metric card, or grouped bullets instead.
12. Vary table shape intentionally across a long document. Repeated grids with the same header treatment and column rhythm create monotony even when each table is individually valid.
13. Treat four or more columns as a layout risk for net-new narrative tables, not as permission to collapse a user- or template-required schema. Use them when the entries are short and the table remains readable in the generated HTML or connector metadata; otherwise report or resolve the layout concern without changing authoritative structure.

## Styling Order

1. Create the table and verify it with `get_tables`.
2. Immediately normalize the table boundary and all cell paragraphs/text using the peer table's normal body style. Include this in the first table-formatting batch after `get_tables`, before or alongside cell population.
3. Populate cells in descending absolute-index order.
4. Re-run `get_tables` and verify final placement.
5. Apply header text styling cell by cell.
6. Apply header-row fill and alternating body-row fills.
7. Adjust column widths after content exists, not before.
8. Re-read with `get_tables` and verify connector-visible structure, cell text, fills, text styles, links, and width properties where available.
9. Export the document as `text/html` when available and verify table markup/CSS: `<table>` placement, row and cell order, header/background colors, font family and size, padding, border styles, page-body max width, and column width declarations.
10. If connector readback, HTML export, and PDF-export visual QA do not expose rendered fit, do not claim the table visually fits the page; report only the verified properties.

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
12. Intended lists inside table cells have native list metadata and contain no typed marker substitutes.
13. Net-new table text satisfies the readability floor; template tables match their canonical peer typography.
14. For explicit global formatting, every target is verified and every exception is explicit.
15. For a repopulated or expanded template table, canonical header and body cells match the sampled template signatures for borders, fills, padding, widths, paragraph role, font family, size, weight, color, and emphasis.

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
