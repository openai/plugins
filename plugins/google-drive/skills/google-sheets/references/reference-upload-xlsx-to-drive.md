# Upload XLSX To Drive

When to read: after creating a local `.xlsx` that should be uploaded to Google Drive.

## Workflow

1. Confirm the local workbook path is an `.xlsx` file.
2. Upload the workbook with the Google Drive connector upload tool, preserving it as an `.xlsx` file:
   ```json
   {
     "file_uri": "/absolute/path/to/workbook.xlsx",
     "file_name": "Workbook name.xlsx",
     "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     "parent_folder_id": "optional-target-folder-id"
   }
   ```
3. Use the connector function exposed in the current runtime, for example `mcp__codex_apps__google_drive._upload_file(...)` or the equivalent Google Drive upload tool.
4. Read Drive metadata for the uploaded file when available and confirm the uploaded file name and MIME type.
5. Return the uploaded file title and link or id when available.

## Rules

- Preserve the workbook as an `.xlsx`; this workflow is not native Google Sheets conversion.
- Use MIME type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
- Do not use `application/vnd.google-apps.spreadsheet` for this upload path.
- Include `parent_folder_id` only when the user gives a target folder or the workflow context provides one.
