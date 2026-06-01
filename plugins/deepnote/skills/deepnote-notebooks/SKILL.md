---
name: deepnote-notebooks
description: Use when reading, reviewing, inspecting, or reasoning about hosted Deepnote notebooks, blocks, inputs, SQL, Python, or notebook outputs through the Deepnote app tools.
---

# Deepnote Notebooks

## Notebook Inspection Workflow

1. Resolve the target notebook with `search` or project context before using `get_notebook`.
2. Read the notebook with `get_notebook` before answering questions about structure, inputs, blocks, or latest run state.
3. Preserve distinctions between block types, notebook inputs, code, SQL, markdown, and metadata in your reasoning.
4. When reporting inputs, include the input `name`, `type`, current `value`, and `label` when useful.
5. When SQL connection usage matters, use `list_integrations` and the integration usage tools to confirm project, notebook, or block references instead of inferring solely from names. When table, schema, or column context matters, use `get_integration` for cached structure.
6. When asked to review or explain a notebook, ground the answer in specific notebook/block names or IDs when useful.
7. If the user asks to create a project, create a notebook, add blocks/cells, update existing blocks/cells, or scaffold notebook content, use the `deepnote-notebook-editing` skill.
8. If the user asks for recent runs, failed runs, or run history, use `list_notebook_runs` before selecting a run for `get_run`.

## Notebook Inspection Output

Great notebook-inspection output should help the user decide what the notebook does, whether it is safe to run, and what to do next. Prefer this structure:

Keep notebook inspection brief and high signal by default. Lead with the answer, then include only the tables or cautions that materially help the user. Omit exhaustive block listings, raw code, and long outputs unless the user asks for more detail.

1. Start with a one-sentence brief: `Notebook "Name" in project "Project" has 12 blocks, 2 inputs, 1 visible connection, and last ran successfully on YYYY-MM-DD HH:MM UTC.`
1. Show a compact status table:

| Field | Value |
| --- | --- |
| Project | `Project name` |
| Notebook | `Notebook name` |
| Notebook ID | `notebook-id` |
| Scheduled | `Yes` or `No` |
| Last Run | `status/date/run id` or `No run visible` |
| Visible Connections | `Integration name (type)` or `None visible via app tools` |

1. If inputs exist, add an inputs table:

| Input | Type | Current Value | Label |
| --- | --- | --- | --- |
| `input_name` | `text` | `safe summary or value` | `Human label` |

1. Add a block map when useful, especially for reviews and debugging:

| Order | Type | Purpose | Connection / Output |
| --- | --- | --- | --- |
| `1` | `sql` | `SELECT demo.gapminder sample` | `Clickhouse (clickhouse)` |

1. Add `Cautions` only when actionable: cells that print environment variables, hard-coded credentials, mutating external calls, long-running servers, large dataset dumps, missing inputs, failed/pending last runs, SQL blocks whose integration is not visible, or integration usage that was not checked when it matters.
1. End with `Useful Next Actions` only when it helps, such as run notebook, inspect latest run, list recent runs, map integrations, summarize outputs, or review risky cells.

When the Deepnote app tools do not expose a detail, say `Not visible via app tools` rather than inferring from names. Keep raw code excerpts short; summarize large cells and mention block IDs when useful.

## Code And Output Handling

- Before suggesting code changes, inspect nearby blocks for imports, shared variables, SQL connections, inputs, and upstream assumptions.
- Prefer deterministic notebook code. Avoid hidden global state, implicit external files, or hard-coded credentials.
- Do not claim an edit was applied unless a write-capable tool is available and reports success. For project, notebook, block creation, and existing block updates, use `deepnote-notebook-editing`.
- If you run a notebook, pass requested input values through `create_run.inputs` using the input `name` fields returned by `get_notebook`, then capture run status with `get_run`. Omit `snapshotDelivery` for status checks so the default download URL delivery is used; request `snapshotDelivery: "inline"` when you need to summarize snapshot content or errors.
- Run input values do not change the notebook's saved default input values.
- For SQL blocks, preserve the existing connection or data source in recommendations unless the user asks to move it. Use `get_integration` for cached table/column context when needed.
- Before running a notebook, flag cells that print `os.environ`, environment variables, credentials, tokens, or broad secret dumps. Do not run those notebooks unless the user explicitly confirms after the risk is named.
- Treat cells that start servers, send network requests, write files, cancel/modify external records, or call production-like systems as stateful. Call out the side effect before execution.

## Review And Cleanup

Use Deepnote app reads to verify notebook structure before making claims. If execution was not run, say so plainly and mention the remaining risk. For larger reviews, summarize relevant sections rather than listing every block.
