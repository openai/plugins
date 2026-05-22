# Smart Chips And Building Blocks

When to read: any task that needs smart chip or building-block parity beyond simple supported chip insertion, or needs to inspect or edit existing chip elements.

## Current Support Level

Support these smart chip element types through connector readback and `batchUpdate` writes:

- Date chips: read as `dateElement`, write with `insertDate`
- People chips: read as `person`, write with `insertPerson`
- Google resource chips: read as `richLink`, write with `insertRichLink`

Treat Google Docs building blocks as recognizable document structure, not as single API objects. There is no documented `batchUpdate` request that inserts arbitrary UI building blocks as native building-block objects.

Use these support tiers:

- Exact through `batchUpdate`: date chips, people chips, rich links, and meeting-notes-like regions composed from supported chips, text, paragraph style, and bullets after sampling a matching exemplar.
- Exact by template copy only: UI-inserted Email draft, Task tracker, Simple decision log, Calendar event draft, Code block, and custom building blocks. Copy a UI-inserted exemplar or template document, then edit supported child content.
- Approximation only: recreate visible tables, labels, and text with normal Docs requests when the user accepts that placeholder chips, dropdown chips, code-block containers, draft metadata, and other UI-only affordances will not be native.
- Unsupported dynamic or account-dependent UI: AI summary, View more catalog entries, and user/workspace-defined custom building blocks unless an existing exemplar is copied.

Do not claim exact Google Docs UI parity for a block unless connector readback proves the same observable structure and every unsupported native UI component came from an existing copied exemplar.

## Template Shape Sampling

Before writing into an existing template or building-block-like region:

1. Resolve the target `documentId` and `tabId`.
2. Read the nearest comparable section with `get_document`, not only plain text.
3. Capture paragraph-level metadata: `namedStyleType`, paragraph style fields, bullet/list state, and start/end indexes.
4. Capture table-level metadata when present: row/column count, table ranges, cell ranges, cell text, private-use placeholder glyph counts, inline object elements, and cell styles exposed by the connector.
5. Capture element-level metadata: `textRun`, `dateElement`, `person`, `richLink`, inline object, text style, and element ranges.
6. Reconstruct only the portions that have a verified write path. For exact UI-only blocks, copy an exemplar and edit inside it.
7. Re-read the inserted or edited region and compare element types, not just visible text.

## Critical Readback Rule

Do not use exact text range search as the primary way to find smart chips.
Chip display text appears in full `get_document` structure, but exact text match helpers may return `null` for that same visible display text.

For chip-aware work:

1. Use `get_document`.
2. Inspect paragraph `elements`.
3. Detect `dateElement`, `person`, and `richLink` directly.
4. Use each element's `startIndex` and `endIndex` for styling, deletion, or replacement.
5. Use element properties for semantic comparison:
   - `dateElement.dateElementProperties.displayText`, `timestamp`, `locale`, `dateFormat`, `timeFormat`
   - `person.personProperties.name`, `email`
   - `richLink.richLinkProperties.title`, `uri`, `mimeType`

Smart chips usually occupy a one-code-unit range. To change the chip payload itself, delete the element range and reinsert the chip. Use `updateTextStyle` only for style changes.

## Building Block Recognition

For calendar-backed Meeting notes insertion, use `reference-meeting-notes-direct.md` as the operational guide. This reference only records the broader capability boundary: the API may not prove that the user inserted the region through Insert > Building blocks > Meeting notes, but it can prove the same observable constituent structure.

For Email draft, Task tracker, Simple decision log, Calendar event draft, and Code block, exact output means starting from a UI-inserted exemplar or template copy. Writing out only the visible labels and table cells is an approximation unless the unsupported UI-only child components came from the copied exemplar.

## Verification

After writing chips or a building-block-like region:

1. Re-read with `get_document`.
2. Confirm the expected element types are present where supported: `dateElement`, `person`, `richLink`.
3. Confirm chip properties match the intended date, attendee emails, and resource URI.
4. Confirm paragraph styles, list state, table shapes, placeholder-glyph presence, and inline objects match the sampled peer block or accepted approximation.
5. Confirm there are no unintended extra empty bullets, duplicate sections, or leftover scaffolding.
6. Do not treat HTML export as proof that a chip survived as a chip; HTML export flattens chips into normal visible text and links.
7. Do not use Drive thumbnails as proof of final visual layout. Use PDF export plus page raster inspection when rendered page quality matters.
