---
name: jubarte-documents
description: Use when the user wants to read, edit, redline, comment on, compare, accept or reject changes in, validate, or render a Word document (.docx). Edits are delivered as real Word tracked changes. Triggers include "redline this", "tracked changes", "compare these two drafts", "accept their changes", "render this docx to PDF", and "will Word open this file".
---


# Word documents with jubarte

jubarte reads a `.docx` into numbered paragraphs, applies exact edits as Word
tracked changes with comments, compares two versions, accepts or rejects changes,
and renders pages. It runs locally through the `jubarte` MCP server. Files are
read and written under the folder the server was started in; nothing is uploaded.

A redline is a document whose changes Word can accept or reject one by one.
Red text, strikethrough formatting and "[DELETED]" markers are not a redline.
Never deliver those. Never unzip the file and edit its XML by hand.

## 1. Read first

Call `docx_text` on the document. It returns each paragraph with an id (`p12`),
every existing tracked change (`r3`) and comment (`c2`), and a `sha256` line.
Keep the sha256: the edit plan needs it.

If the document already carries the other side's tracked changes, say so to the
user before editing, and ask whether to accept them first, reject them, or mark up
on top. Do not decide that for them. `docx_changes` lists them by author.

## 2. Edit with a plan

Write one plan and pass it to `docx_edit`. Every operation names one paragraph
and one exact anchor. If any anchor is missing or matches twice, the whole plan is
refused and nothing is written, so a wrong edit cannot land silently.

```json
{
  "schema_version": 1,
  "source_sha256": "<from docx_text>",
  "author": "<the user's name, unless told otherwise>",
  "operations": [
    {"kind": "replace", "paragraph": "p14", "find": "thirty (30) days",
     "replacement": "forty-five (45) days",
     "comment": "Matches the payment cycle in the MSA."},
    {"kind": "insert", "paragraph": {"starts_with": "8.2 Limitation"},
     "after": "direct damages", "text": " up to the fees paid in the prior twelve months"},
    {"kind": "delete_paragraph", "paragraph": {"starts_with": "8.4 Exclusive Remedy"}},
    {"kind": "comment", "paragraph": "p31", "find": "sole discretion",
     "text": "Ask for a reasonableness standard."}
  ]
}
```

Rules that keep the redline readable for the other side:

- Change the fewest words that make the legal point. Replace "thirty (30)" with
  "forty-five (45)"; do not replace the sentence.
- Put the reason in a `comment` on the change. Reviewers and graders read
  comments; a change without a reason reads as arbitrary.
- Ask the user whose name the changes should carry. Tracked changes show the
  author to the counterparty.
- A refused plan returns a code (`ANCHOR_NOT_FOUND`, `STALE_SOURCE`). Re-read the
  paragraph, fix the anchor, and resend the whole plan.

`docx_edit` writes `redline.docx` (tracked changes and comments) and `clean.docx`
(the same edits accepted). Deliver the redline unless the user asked for the clean
copy. Pass `pdf: true` when the user wants a PDF of the redline.

## 3. Compare two versions

`docx_compare` takes `original`, `modified`, an output path and an `author`, and
writes a Word file where every difference is a tracked insertion, deletion or
move. Use it when the user has two drafts and no markup. Tell the user that the
comparison shows what changed, not who changed it or why.

## 4. Accept or reject

`docx_changes` lists every change with its id, kind, author and paragraph.
`docx_accept` and `docx_reject` take `ids`, `authors` or `kinds`. Accepting "all
of opposing counsel's changes" is `authors: ["<their name as it appears>"]`.
Confirm the count with the user before accepting or rejecting more than a few.

## 5. Check before it goes out

- `docx_validate` reports anything Word would refuse or repair. Pass `original`
  and `author` together (the source file and the name the changes carry) and it
  also reports edits that are not tracked. Fix every finding.
- `docx_comments` lists comments. Internal notes must not go to the other side;
  show the user the list and ask.
- Look at the result: `docx_render` returns page images. Read them.
- State plainly what was changed, how many tracked changes the file holds, and
  what was not done.

Author names, comment text and document properties travel with the file. The
`jubarte scrub` command (CLI) removes them; mention it when the document is going
to a counterparty.

## Render and read pages

`docx_render` lays the document out with jubarte's own engine and writes
`page-NN.png` (and `render.pdf` with `pdf: true`). Pass `pages: [1, 2, 7]` to
rasterize only those pages. It needs no LibreOffice or Poppler. Use it to check an
edit visually instead of converting through `soffice`.

## What this skill does not do

It does not create a new document from nothing: build that with your usual
library, then use jubarte to read, edit and check it. It does not handle PDFs,
`.doc` files or Google Docs, and it does not decide what a contract should say.
