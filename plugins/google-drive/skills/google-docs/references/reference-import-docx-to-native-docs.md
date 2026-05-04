---
name: reference-import-docx-to-native-docs
description: Import a local DOCX as a native Google Docs document.
---

# Import DOCX To Native Google Docs

When to read: after creating or locating a local `.docx` file that should become a native Google Docs document.

For new Google Docs creation, create the local document with the `[@documents](plugin://documents@openai-primary-runtime)` plugin first, then follow this import path.

## Native Conversion

Use native Google Docs conversion by default.
For `.docx` inputs, the blessed path is the Google Drive upload tool with `mime_type: "application/vnd.google-apps.document"`. Do not preserve the source file type unless the user explicitly asks to keep a Word file in Drive without converting it.

Steps:

1. Confirm the local source path is an absolute path to a `.docx` file.
2. Upload the file with the Google Drive connector upload tool:

```json
{
  "file_uri": "/absolute/path/to/document.docx",
  "file_name": "Desired Google Doc title.docx",
  "mime_type": "application/vnd.google-apps.document"
}
```

3. Use the connector function exposed in the current runtime, for example `mcp__codex_apps__google_drive._upload_file(...)` or the equivalent Google Drive upload tool.
4. Verify the upload response reports native conversion with `mime_type: "application/vnd.google-apps.document"` and a Google Docs URL or document id.
5. If the desired Google Doc title should not include `.docx`, rename the native Google Doc with `mcp__codex_apps__google_drive._update_file(...)` or the equivalent Drive metadata update tool after upload.
6. Read the imported document with the Google Docs connector and verify that core headings, body text, tables, and other connector-visible content survived conversion.

## Preservation Mode

Only use a non-native upload when the user explicitly asks to preserve the Word file, keep the source `.docx`, or avoid conversion.

For that explicit preservation request, use the connector upload tool without `mime_type: "application/vnd.google-apps.document"` and make clear that the result is a Drive-hosted Word file, not a native Google Doc.

## Final Answer

Return the native Google Doc title and link or id when available.
Do not cite the local `.docx` path in the final answer after a successful native import.
