# Box Search

## MCP

### Tools

- Search: `search_folders_by_name`, `search_files_keyword`, `search_files_metadata`
- Metadata schema lookup: `list_metadata_templates`, `get_metadata_template_schema`
- Confirm before acting: `get_file_details`, `get_folder_details`

### Security guidelines

- Use least-privilege search scopes. When the user names a folder or project area, resolve it with `search_folders_by_name` and pass `ancestor_folder_id` to later searches instead of searching the whole Box account.
- Do not expose file contents from search results unless the user asks and content-display preferences are clear. Search results should usually be summarized by name, type, path, owner, modified date, and Box URL.
- Request only the fields needed for the task. Avoid pulling `permissions`, `sharedLink`, `metadata`, or collaboration-related fields unless they are needed for access review, sharing analysis, or disambiguation.

### Tool selection

- Use `search_folders_by_name` when the user names a folder, workspace, client, project, or department. If multiple folders match, ask the user to choose or disambiguate using path, owner, or modified date.
- Use `search_files_keyword` for natural-language, filename, extension, or broad content searches. Scope with `ancestor_folder_id`, `file_extensions`, date ranges, and a low initial `limit`.
- Use `search_files_metadata` when the user's criteria map to structured metadata fields such as contract value, status, department, matter type, expiration date, or risk rating.
- Use `list_metadata_templates` and `get_metadata_template_schema` before metadata search so the agent uses the correct `from`, field keys, and query fields.
- Use `get_file_details` or `get_folder_details` after search to confirm the item, path, classification, permissions, metadata, or sharing state before taking follow-up action.

### Search workflows

### Folder-scoped search

1. Resolve the folder with `search_folders_by_name`.
2. If there are multiple matches, disambiguate using `path_collection`, owner, or date fields.
3. Search inside the selected folder with `ancestor_folder_id`.
4. Fetch details for the final item before acting on it.

### Metadata search

1. Call `list_metadata_templates` for `enterprise` or `global`.
2. Call `get_metadata_template_schema` for the selected template.
3. Build `search_files_metadata` with the schema's field keys.
4. Use `query_params` for user-provided values instead of embedding arbitrary values directly in the query string.

### Broad keyword search

1. Start with a small `limit`.
2. Add `file_extensions`, `ancestor_folder_id`, or RFC3339 date ranges when results are too broad.
3. Ask a clarifying question before expanding to enterprise-wide search if the query may expose too many unrelated results.

### Error handling

- If search returns no results, broaden one dimension at a time: remove date filters, remove file extension filters, search by partial folder name, or try keyword search instead of metadata search.
- If search returns too many results, narrow with folder scope, file extension, date range, metadata filters, or requested fields.
- If metadata search fails, verify the template scope, template key, field keys, and `from` value using `list_metadata_templates` and `get_metadata_template_schema`.
- If permissions block access, explain that Box returned only accessible content and ask the user for a different folder, file, or collaborator with access.
- If results are ambiguous, do not assume the intended file. Present the top candidates with stable identifiers such as name, type, path, modified date, and owner.
