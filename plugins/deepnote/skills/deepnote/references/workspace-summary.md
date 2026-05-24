# Workspace Summary Workflow

Use this workflow when the user asks for a workspace summary, heartbeat, overview, active notebooks, scheduled notebooks, or a broad project/notebook inventory.

1. Use `get_me` for workspace name, workspace ID, connected user, and caller access level when useful.
2. Use `list_projects` to collect projects and notebooks. For complete inventories, page through results with `pageSize: 100` until `pagination.hasMore` is false.
3. Use `list_integrations` to collect workspace integration names, types, and IDs.
4. Use `get_notebook` for notebooks that need connection details or latest run detail.
5. Use `list_notebook_runs` when the summary asks for recent runs, failed runs, or run history beyond the latest run metadata.
6. Identify scheduled notebooks from the `isScheduled` field returned by `list_projects` or `get_notebook`.
7. Identify active notebooks from available recency signals such as `lastRunAt`, recent `list_notebook_runs` results, a current or recent `lastRunId`, or an explicitly requested run status from `get_run`. If the app does not expose live kernel/session state, say active means recent run activity rather than an open editor session.
8. Identify integration usage with `list_integration_project_usages`, `list_integration_notebook_usages`, or `list_integration_block_usages` when direct usage mapping is needed. If usage is not checked, write `Usage not checked`; if a checked usage tool returns no usages, write `None found`.
9. Use `get_integration` when the workspace summary or integration report asks for cached table, schema, or column structure.
10. Build safe project and notebook links with `deepnote-links`, including UTM parameters on project and notebook URLs; use `utm_term=workspace_summary` when the link is created by this workflow rather than a single tool result.

Great workspace-status output should feel like a small operations dashboard:

1. Start with a one-sentence health line, for example: `Deepnote workspace is reachable; the current app response includes 6 projects, 15 notebooks, 1 scheduled notebook, and 4 integrations.`
2. Add a compact `Key Signals` list with counts visible in the current app response for projects, notebooks, scheduled notebooks, recently run notebooks, failed or pending runs when checked, and integrations.
3. Use a Markdown notebook summary table as the main artifact when individual notebook rows are reasonable, grouping rows by project. Use a compact project summary table only when the workspace is large enough that listing every notebook would be noisy.
4. Keep integrations inside the main table as an `Integrations` column for workspace summaries, notebook inventories, and project summaries.
5. Hyperlink project names and notebook names when links can be safely constructed. In any table with a `Notebook` column, the notebook name should be the Markdown link label.
6. Finish with `Notable Findings` only when there is something actionable, such as a scheduled notebook with no last run, a pending/failed run, a notebook that prints environment variables, or an integration with no checked usage.

Use this notebook summary table shape for workspace summaries, notebook inventories, and "which notebooks do I have?" style requests unless the workspace is too large or the user asks for a different format:

| Project | Notebook | Scheduled | Last Run Seen | Integrations |
| --- | --- | --- | --- | --- |
| `Project name as Markdown link` | `Notebook name as Markdown link` | `Yes` or `No` | `YYYY-MM-DD HH:MM UTC`, `None seen`, or `Not visible via app tools` | `Integration name/Type` or `None found` |

Use this compact project summary table only for large workspaces or high-level summaries. When listing notebook names inside the `Notebooks` column, hyperlink each notebook name:

| Project | Notebooks | Scheduled | Last Run Seen | Integrations |
| --- | --- | --- | --- | --- |
| `Project name as Markdown link` | `N` or linked notebook names | `Yes` if any notebook in the project is scheduled, otherwise `No` | `YYYY-MM-DD HH:MM UTC`, `None seen`, or `Not visible via app tools` | `Integration name/Type, Integration name/Type` or `None found` |

For `Last Run Seen`, use that notebook's visible `lastRunAt` in notebook rows. In compact project rows, use the most recent visible `lastRunAt` across notebooks in the project, or a checked `get_run` completion time when more current. Format dates in UTC as `YYYY-MM-DD HH:MM UTC`. Do not write "None seen" when a run ID or run timestamp is visible.

For `Integrations`, use integration names and IDs from `list_integrations`, then map usage with `list_integration_project_usages`, `list_integration_notebook_usages`, or `list_integration_block_usages` when direct usage matters. Use `get_integration` for cached table/column structure when requested. You may also mention visible references from `get_notebook` blocks or inline `get_run` snapshot content. Do not infer usage from integration names alone; say `None found` only when checked usage or visible references return no connection.

For a specific project breakdown or a specific notebook summary, filter the notebook summary table to the relevant project or notebook and keep the notebook name hyperlinked.

Use a standalone integration table only when the user explicitly asks for an integration inventory or integration usage report. In normal workspace and notebook summaries, do not split integrations into a separate table; keep them in the `Integrations` column.

| Integration | Type | Visible Notebook Usage |
| --- | --- | --- |
| `Integration name` | `type` | `Project / Notebook` from usage tools, `None found`, or `Usage not checked` |

Keep the table concise for large workspaces: include active notebooks, scheduled notebooks, and notebooks with visible linked connections first; then summarize any remaining notebooks by count.

Avoid calling notebooks "currently open" or "currently running" unless a current app tool exposes live session state. Prefer `recently run`, `scheduled`, `pending run`, or `last run`.
