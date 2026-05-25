---
name: deepnote
description: Use when a task mentions Deepnote, the connected Deepnote app, Deepnote OAuth connection, Deepnote docs, projects, workspaces, notebooks, blocks, integrations, or notebook runs.
---

# Deepnote Router

Use the connected Deepnote app tools as the source of truth for hosted Deepnote state. Prefer them over browser automation, screenshots, ad hoc HTTP calls, or local filesystem guesses for Deepnote projects, notebooks, blocks, integrations, docs, or runs.

If the Deepnote app tools are unavailable, say so and ask the user to connect the Deepnote app with OAuth. Do not pretend to have inspected Deepnote state.

When the user asks what Deepnote can do, start with:

Deepnote can identify the current workspace, search resources, list projects and integrations, inspect notebooks, create and edit notebook structure, map integration usage and cached table structure, read Deepnote docs, run notebooks, and fetch run status and history.

## Capability Map

Use the current tool surface only; if a required tool is absent, say which capability is missing.

- Identity and discovery: `get_me`, `search`, `list_projects`.
- Notebook inspection: `get_notebook`.
- Notebook editing: `create_project`, `create_notebook`, `create_block`, `update_block`, `reorder_notebook_blocks`.
- Integrations: `list_integrations`, `get_integration`, `list_integration_project_usages`, `list_integration_notebook_usages`, `list_integration_block_usages`.
- Execution: `create_run`, `list_notebook_runs`, `get_run`.
- Docs: `list_docs`, `get_doc`.

## Route By Intent

| User asks for | Use |
| --- | --- |
| Workspace overview, heartbeat, active/scheduled notebooks, broad inventory | `get_me`, `list_projects`, `list_integrations`, and [references/workspace-summary.md](references/workspace-summary.md) |
| Notebook contents, inputs, SQL, blocks, outputs, review, or explanation | `deepnote-notebooks` |
| Project/notebook creation, adding cells, updating cells, moving/reordering cells, scaffolded notebook content | `deepnote-notebook-editing` |
| Notebook execution, run status, recent/failed runs, run history, snapshots, integration usage, cached tables/columns | `deepnote-data-execution` |
| Project, notebook, workspace, or share links | `deepnote-links` |
| Product docs or how-to questions | `list_docs`, then `get_doc` |

## Routing Defaults

1. Resolve ambiguous names and IDs with `search`, `list_projects`, or `list_integrations`.
2. Use `get_me` when workspace identity, connected user, caller role, or OAuth context matters.
3. Read with `get_notebook` before reasoning about notebook blocks, inputs, latest run metadata, or before editing notebook structure.
4. Use `get_integration` for cached table, schema, column, or table-existence questions about an integration.
5. Use `list_notebook_runs` for run history or failed-run searches; use `get_run` for one selected run's status, errors, or snapshot.
6. Use specialist skills for any workflow with detailed rules. Keep this skill as the router.

## Global Guardrails

- Never expose tokens, secret values, raw credentials, or sensitive integration metadata. Refer to secret names only.
- Treat project creation, notebook creation, block creation, block updates, block reordering, and notebook runs as persistent or stateful actions. Resolve targets carefully and report affected IDs.
- Do not run a notebook unless the user asks for execution, clearly needs fresh results, or confirms a creation workflow's final run prompt. Creation workflows may ask whether to run the newly created notebook, but must not run it preemptively. Run input overrides apply only to that run.
- Do not expose `snapshotDownloadUrl` values unless the user asks for a download/file handoff; use inline snapshots only when output or error details are needed.
- Use cached integration structure when available, but do not claim a fresh live database scan, row preview, single-block execution, environment mutation, permission change, publishing change, or scheduling change unless a current app tool exposes it.
- Keep responses brief and grounded in Deepnote object names, IDs, statuses, and links when available.
