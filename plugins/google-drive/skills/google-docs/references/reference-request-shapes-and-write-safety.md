# Request Shapes And Write Safety

When to read: non-meeting structural connector writes, table/form-like template edits, or any connector write that is not fully covered by a task-specific fast-path reference.

## Contents

- `mcp__codex_apps__google_drive._batch_update_document` Request Shape
- Tab-Aware Calls
- Request Key Reference
- API Capability Boundaries
- Range Safety
- Local Style Baseline
- Existing Table Writes

## `mcp__codex_apps__google_drive._batch_update_document` Request Shape

Always pass `requests` as structured objects, not stringified JSON.
Pass `write_control` as an object when using it, not as stringified JSON.
For concurrency-sensitive writes, prefer the latest connector-visible revision id in `write_control`; set either `requiredRevisionId` or `targetRevisionId`, not both.
Requests execute in order, so sequence dependent edits deliberately.
Preflight every hand-authored batch before calling the connector:

- Each `requests` array item must be an object with exactly one Google Docs request key.
- No request item may be an empty object, a JSON string, or a union of multiple request types.
- Field names must belong to the selected Docs request shape. Do not reuse Sheets, Slides, or Drive field names inside Docs requests.
- For destructive or index-sensitive edits, resolve the target range from current connector readback immediately before composing the request. Do not reuse stale start or end indexes after insertions, deletions, table edits, image insertion, or tab changes.

Bad:

```json
{"requests":["{\"deleteContentRange\":{\"range\":{\"startIndex\":10,\"endIndex\":20}}}"]}
```

Good:

```json
{
  "requests": [
    {
      "deleteContentRange": {
        "range": {
          "startIndex": 10,
          "endIndex": 20
        }
      }
    }
  ]
}
```

## Tab-Aware Calls

If document tabs exist, include the resolved `tabId` on all relevant reads and writes:

- `get_document`
- targeted follow-up range/find calls after the cache is stale or insufficient
- `mcp__codex_apps__google_drive._batch_update_document`

Missing `tabId` is a common reason edits land in the wrong location.

## Request Key Reference

When the connector supports the corresponding Google Docs request shape, use the native request key instead of plain-text approximations:

- Text: `replaceAllText`, `insertText`, `deleteContentRange`, `replaceNamedRangeContent`
- Text and paragraph formatting: `updateTextStyle`, `updateParagraphStyle`, `createParagraphBullets`, `deleteParagraphBullets`
- Named ranges: `createNamedRange`, `deleteNamedRange`
- Images and embedded objects: `insertInlineImage`, `replaceImage`, `deletePositionedObject`
- Tables: `insertTable`, `insertTableRow`, `insertTableColumn`, `deleteTableRow`, `deleteTableColumn`, `updateTableColumnProperties`, `updateTableCellStyle`, `updateTableRowStyle`, `mergeTableCells`, `unmergeTableCells`, `pinTableHeaderRows`
- Document layout and structure: `updateDocumentStyle`, `updateSectionStyle`, `insertPageBreak`, `insertSectionBreak`
- Headers, footers, and notes: `createHeader`, `deleteHeader`, `createFooter`, `deleteFooter`, `createFootnote`
- Tabs: `addDocumentTab`, `deleteTab`, `updateDocumentTabProperties`
- Supported smart chips: `insertDate`, `insertPerson`, `insertRichLink`

For calendar-backed Meeting notes, read `reference-meeting-notes-direct.md`. For simple supported-chip writes, `reference-direct-request-composition.md` is sufficient. For other smart chips and building-block-like content, read `reference-smart-chips-and-building-blocks.md` before writing. Exact text range helpers may not find chip display text even when `get_document` exposes that display text in `dateElement`, `person`, or `richLink` properties.
Google Docs accepts at most 10 `insertPerson` requests in one `batchUpdate` call. For person-heavy chip writes, split the request array into sequential connector batches and re-read between batches when using revision guards.

## API Capability Boundaries

Use `documents.get` as the source of truth for structure. It exposes connector-visible tabs, body content, paragraph elements, tables, inline objects, lists, text styles, paragraph styles, supported smart chips, headers, footers, footnotes, and revision ids.

Use `mcp__codex_apps__google_drive._create_file` to create blank or basic native Google Docs when `reference-native-create-direct.md` selects the connector-native route.

Use `documents.batchUpdate` as the write primitive for native Google Docs content writes. It validates the request batch before applying it, applies valid batches atomically, and supports `writeControl` for concurrency-sensitive writes.

Use Drive APIs around Docs operations when they fit the task:

- `files.copy` for whole-document template duplication when exact global template parity matters
- `files.export` to `text/html`, `.docx`, or `application/pdf` for verification and handoff when the task is layout-sensitive, table-heavy, figure-heavy, style-ambiguous, or explicitly requests an export.
- Drive comments and replies for comment workflows, because comments are not part of Docs `batchUpdate`

For calendar-backed Meeting notes, follow `reference-meeting-notes-direct.md`; it owns Calendar event lookup and event-payload handling.

Do not claim support for true suggestion-mode edits through `batchUpdate`; it creates direct document edits. Do not claim support for arbitrary Google Docs UI building blocks as a single API object unless a connector read and write path for that object has been verified in the current workflow.
For UI-only building blocks, exact parity requires copying a UI-inserted exemplar or template and editing supported child content in place. Recreating the visible text and table cells through `batchUpdate` is an approximation unless readback confirms every required native child component came from the copied exemplar.

## Range Safety

Before destructive writes:

1. Resolve target ranges from current connector readback, or from a fresh read if the prior read is stale.
2. Confirm first and last paragraphs are the intended body region.
3. Confirm every request item has exactly one Docs request key and still targets the live range.
4. Write one chunk.
5. Verify before the next chunk.
6. Treat post-insertion style work as a new range-resolution step, not as a continuation of the insertion step. Re-read after content insertion before applying links, bolding, or heading fixes.
7. Treat figure insertion as another new range-resolution step. Re-read the intended insertion block before placing any connector-supported image after a text edit.
8. For write-capability questions, prefer a minimal pilot write and readback over a verbal inference about connector limits.

## Local Style Baseline

1. Before inserting a new section, table intro, or multi-paragraph body block, inspect nearby template content and capture the local style baseline: heading level, font family, and normal body sizing.
2. Treat surrounding document typography as part of the target shape. If the doc body is Arial, reset inserted content to Arial rather than accepting connector defaults.
3. If a new line is meant to be a peer section header, match the nearest peer heading style from the template instead of inventing a custom bold line.
4. After the first substantive insertion in a section, re-read a small sample and verify both structure and typography before continuing.
5. Treat nearby existing content as a style anchor, not just a content anchor. Capture the closest comparable heading and the closest comparable table before creating a new one.
6. If connector metadata is incomplete for font family, heading weight, or table presentation, sample the nearest connector-visible peer structure. Do not invent a browser/UI fallback in this blind environment.
7. Do not style or link text based on offsets you predicted before the final content settled. Re-resolve live ranges from the written document state.
8. For new headings or section labels, prefer sampling the exact peer heading paragraph from the live document and matching its concrete style properties rather than relying on generic heading defaults.
9. When promoting a new peer section heading, use the peer heading's paragraph style as the primary mechanism. Treat explicit font-family, font-size, or bold overrides on that heading as a secondary repair step, not the default path.
10. After promoting a new heading, re-read that single line and its connector-visible style fields before continuing. If the paragraph-style match already matches connector-visible peer data, do not layer extra heading text styling on top.
11. `namedStyleType` alone is not proof that a heading matches the template. If nearby peer headings carry additional local text styling, compare against a concrete peer heading and reproduce that local treatment when needed.
12. When the heading match is high stakes, prefer a connector read that exposes concrete text-style details for the peer heading instead of relying only on paragraph-text summaries.
13. If the task includes figures, capture the intended text structure before figure placement. Headings, list formatting, and paragraph boundaries should be stable before connector-supported image insertion begins.

## Existing Table Writes

1. When filling an existing table, resolve the target table with `get_tables` first; do not infer cell placement from paragraph order alone.
2. Treat row and column identity as part of the write target. Confirm which column is the prompt column and which is the response column before inserting any answer text.
3. After the first inserted answer, re-read the table and verify the new content landed in the intended cell before filling the remaining rows.
4. If the document contains repeated two-column label/value tables, verify the target `tableNumber` and target row before each section write instead of assuming the next table is correct.
5. When the user asks to fill an existing template table, default to writing into that table, not appending a parallel “completed draft” section elsewhere in the doc.
6. Do not conclude that template cells are unwritable without a table-aware readback strategy. Use `get_tables`, target the intended answer cell, perform a minimal pilot write if needed, and verify the result before escalating.
7. If a fallback structure is truly required, it must preserve one canonical output shape. Do not leave both an empty template and a second full duplicate answer section unless the user explicitly asked for that.
8. Do not convert a table-based template into plain paragraphs just because connector cell editing is difficult. That changes the output shape and fails the template-fill task.
9. If cell targeting becomes unstable, re-read the table, re-resolve the target cell, and resume with smaller verified connector writes. Treat shifting indexes as a reason to slow down, not a reason to abandon the template structure.
10. If you need a fresh copy to recover from a corrupted template-fill attempt, the recovery copy must still be filled in the original template shape before handoff.
11. Treat empty table cells as writable targets unless connector evidence proves otherwise. Resolve them by table identity and cell position, not by whether the cell contains existing text.
12. If one connector write into a target cell fails, do not generalize that failure to the whole table. Re-read the table, confirm the intended cell again, and retry with a smaller pilot write before changing methods.
13. If a connector path looks fragile, prefer the smallest connector write that preserves exact target identity and supports immediate readback verification.
14. A markdown draft, shadow section, or externalized answer set is not an acceptable substitute for filling the intended existing table unless the user explicitly approves that substitution.
15. Do not let the absence of an obvious convenience wrapper stand in for connector capability detection. If the session exposes connector tools, use them directly or verify their availability explicitly. This blind plugin has no browser-only editing fallback.
