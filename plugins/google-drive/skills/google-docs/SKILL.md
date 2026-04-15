---
name: google-docs
description: Inspect and edit Google Docs documents with raw document reads and index-aware batch updates. Use when the user wants to read document text or structure, find paragraph indexes, rewrite sections in place, edit tables, or apply style-aware document changes with Google Docs tools.
---

# Google Docs

Use this guide for precise Google Docs reading, editing, and creation.

## Read Path

- If you only know the doc title or title keywords, use `search` first instead of asking for a URL.
- Prefer `get_document` for Docs-native reads. It returns the raw document and tab content, and replaces the synthesized `get_document_text` view that is being phased out.
- Prefer `find_document_text_range` over hand-picked indexes when you can anchor on exact text.
- Use `get_document_paragraph_range` when you have an index inside a paragraph and need its full boundaries.
- Use `get_document_tables` before editing or rebuilding table content.
- If the doc has tabs, use `get_document` to identify the right tab and carry `tab_id` through follow-up reads.
- Re-read after substantial edits so later writes use live indexes.

## Workflow

1. Read before writing.
- Identify the exact section, heading structure, paragraph boundaries, table locations, and current formatting.
- If the target is ambiguous, summarize the candidate section first and make the scope explicit in the response.
- For read-only answers, quote or closely paraphrase the specific retrieved line or paragraph from `get_document` that supports the answer so the response stays visibly grounded in the document.

2. Find live indexes.
- Use `find_document_text_range` when you can anchor on exact text.
- Use `get_document` when you need to inspect the current body, tab content, or nearby structure before resolving ranges.
- Use `get_document_paragraph_range` when you need a single paragraph's range around an index.
- Do not guess offsets after prior writes.
- After many edits, call `get_document` again before the next batch.

3. Build a `batch_update_document`.
- All document changes go through `batch_update_document`.
- IMPORTANT: `batch_update_document.requests` must be an array of structured request objects. Do not JSON-stringify Docs API requests.
- `batch_update_document.write_control` must also be an object, and not a JSON-stringified string.
- Requests execute in order, so sequence dependent edits deliberately.
- For concurrency-sensitive writes, prefer `write_control` with the latest `revisionId`. Set either `requiredRevisionId` or `targetRevisionId`, never both.

4. Preserve Docs-native formatting.
- Use heading levels and paragraph styles to organize the document.
- Build lists with inserted text plus Docs list or paragraph styling. Do not fake bullets or numbering with literal `-`, `*`, or `1.` characters alone.
- Do not add blank paragraphs for spacing. Use styles instead.
- Do not leave the document unformatted unless the user explicitly asks.

5. Verify the write.
- After finishing all edits, call `get_document` one more time.
- Confirm the text landed in the intended place and indexes still line up before ending.

## Allowed `batch_update_document` Request Types

- Text: `replaceAllText`, `insertText`, `deleteContentRange`, `replaceNamedRangeContent`
- Text and paragraph formatting: `updateTextStyle`, `updateParagraphStyle`, `createParagraphBullets`, `deleteParagraphBullets`
- Named ranges: `createNamedRange`, `deleteNamedRange`
- Images and embedded objects: `insertInlineImage`, `replaceImage`, `deletePositionedObject`
- Tables: `insertTable`, `insertTableRow`, `insertTableColumn`, `deleteTableRow`, `deleteTableColumn`, `updateTableColumnProperties`, `updateTableCellStyle`, `updateTableRowStyle`, `mergeTableCells`, `unmergeTableCells`, `pinTableHeaderRows`
- Document layout and structure: `updateDocumentStyle`, `updateSectionStyle`, `insertPageBreak`, `insertSectionBreak`
- Headers, footers, and notes: `createHeader`, `deleteHeader`, `createFooter`, `deleteFooter`, `createFootnote`
- Tabs: `addDocumentTab`, `deleteTab`, `updateDocumentTabProperties`
- People: `insertPerson`

## Write Rules

- Preserve existing headings, styles, links, dates, and table structure when editing unless the user asks to change them.
- Use multiple heading levels to organize a doc unless the user instructs otherwise.
- Treat large rewrites, deletions, tab changes, layout changes, and table restructuring as explicit actions.
- When similar headings or repeated text exist, identify the exact target section before editing.

## Read-Only Answers

- When the user only asked to read, summarize, or answer from the doc, prefer the lightest read path that still keeps the answer grounded in the raw document response.
- Support the answer with a short quoted phrase or a close paraphrase from the retrieved text instead of giving an ungrounded conclusion.

## Fallback

If document content or write tools are unavailable, say that Google Docs access or tooling is missing and ask the user to reconnect or clarify the target document.
