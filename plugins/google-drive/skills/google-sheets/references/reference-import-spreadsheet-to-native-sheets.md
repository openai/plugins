# Import Spreadsheet To Native Google Sheets

When to read: after creating or locating a local spreadsheet file that should become a Google Sheets spreadsheet.

For new Google Sheets creation, prefer creating the local workbook with the `[@spreadsheets](plugin://spreadsheets@openai-primary-runtime)` plugin or `$Excel` skill before following this import path.

## Default Rule

Use native Google Sheets conversion by default.

For `.xlsx`, `.xls`, `.ods`, `.csv`, and `.tsv` inputs, the blessed path is the connector's spreadsheet import tool with `upload_mode: "native_google_sheets"`. Do not preserve the source file type unless the user explicitly asks to keep an Excel/OpenDocument/text spreadsheet file in Drive without converting it.

## Workflow

1. Confirm the local source path is an absolute path to a supported spreadsheet file: `.xlsx`, `.xls`, `.ods`, `.csv`, or `.tsv`.
2. Import the file with the Google Drive connector spreadsheet import tool:
   ```json
   {
     "source_file": "/absolute/path/to/workbook.xlsx",
     "title": "Workbook name",
     "upload_mode": "native_google_sheets"
   }
   ```
3. Use the connector function exposed in the current runtime, for example `mcp__codex_apps__google_drive._import_spreadsheet(...)` or the equivalent Google Drive spreadsheet import tool.
4. Verify the import response reports native conversion, typically with `converted: true`, `mimeType: "application/vnd.google-apps.spreadsheet"`, and a `spreadsheetId` or spreadsheet URL.
5. Read spreadsheet metadata when available and confirm the created spreadsheet title, URL, and sheet tabs.
6. Return only the Google Sheets title and spreadsheet link in the final answer unless the user asks for implementation details.

## Escape Hatch

Only use a non-native upload mode when the user explicitly asks to preserve the source file type, keep the file as Excel/OpenDocument/text, or avoid conversion.

For that explicit preservation request, use the connector's spreadsheet import tool with:
```json
{
  "source_file": "/absolute/path/to/workbook.xlsx",
  "title": "Workbook name",
  "upload_mode": "keep_source_file_type"
}
```

Use generic Drive `_upload_file(...)` only for generic file upload requests that are not asking for a Google Sheets spreadsheet outcome.

## Rules

- `native_google_sheets` is the default for spreadsheet imports.
- `keep_source_file_type` is opt-in and requires explicit user intent.
- Do not use generic `_upload_file(...)` for "import into Google Sheets"; it preserves the uploaded file instead of creating a native Sheet.
- Do not cite the local source path in the final answer for a successful native import.
