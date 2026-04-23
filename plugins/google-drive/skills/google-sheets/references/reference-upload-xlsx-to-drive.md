# Upload XLSX To Native Google Sheet

When to read: after creating a local `.xlsx` scratch workbook that should become the delivered Google Sheet.

## Workflow

1. Confirm the local workbook path is an `.xlsx` file.
2. Derive the destination title from the workbook stem or the user's requested title. Strip any `.xlsx` suffix unless the user explicitly asked for an Office file.
3. Import or upload the workbook with the Google Drive connector path that creates a native Google Sheet:
   ```json
   {
     "file_uri": "/absolute/path/to/workbook.xlsx",
     "file_name": "Workbook name",
     "mime_type": "application/vnd.google-apps.spreadsheet",
     "parent_folder_id": "optional-target-folder-id"
   }
   ```
4. Use the connector function exposed in the current runtime, for example `mcp__codex_apps__google_drive._upload_file(...)` or the equivalent Google Drive import/upload tool.
5. Read Drive metadata for the uploaded file when available and confirm the title and MIME type are the native Google Sheets artifact.
6. If the connector keeps the source `.xlsx` instead of creating a native Sheet, do not treat that as complete. Retry with a native Sheets upload/import path, or create a native `application/vnd.google-apps.spreadsheet` file and populate it through Google Sheets connector calls.
7. Return the Google Sheet title and link or id when available.

## Rules

- Treat the local `.xlsx` as a scratch artifact, not the deliverable.
- Use MIME type `application/vnd.google-apps.spreadsheet` for the destination.
- Do not preserve the workbook as `.xlsx` unless the user explicitly asks for an Office file.
- Include `parent_folder_id` only when the user gives a target folder or the workflow context provides one.
- In the final response, cite only the native Google Sheet link or id, not the local scratch workbook path.
