# Request Shapes And Write Safety

When to read: any task that writes through connector APIs.

## `google_docs_batch_update` Request Shape

Always pass `requests` as structured objects, not stringified JSON.
Pass `write_control` as an object when using it, not as stringified JSON.
For concurrency-sensitive writes, prefer the latest connector-visible revision id in `write_control`; set either `requiredRevisionId` or `targetRevisionId`, not both.
Requests execute in order, so sequence dependent edits deliberately.

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
- `get_document_text`
- range/find calls
- `batch_update`

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
- People: `insertPerson`

## Range Safety

Before destructive writes:

1. Resolve target ranges from a fresh read.
2. Confirm first and last paragraphs are the intended body region.
3. Write one chunk.
4. Verify before the next chunk.
5. Treat post-insertion style work as a new range-resolution step, not as a continuation of the insertion step. Re-read after content insertion before applying links, bolding, or heading fixes.
6. Treat figure insertion as another new range-resolution step. Re-read the intended insertion block before placing any connector-supported image after a text edit.
7. For write-capability questions, prefer a minimal pilot write and readback over a verbal inference about connector limits.

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
