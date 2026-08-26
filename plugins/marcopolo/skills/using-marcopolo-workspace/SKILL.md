---
name: using-marcopolo-workspace
description: Orientation for the MarcoPolo remote workspace, what it is, how `/workspace` is laid out, when to use the product MCP data tools versus `workspace_shell`, and how the `connection` CLI fits in. Use this skill whenever MarcoPolo, the marcopolo MCP server, `workspace_shell`, `/workspace`, connections, or `connection` CLI commands come up. Read this first when entering a MarcoPolo session, before reaching for a more specific skill.
---

# Using the MarcoPolo workspace

MarcoPolo is a persistent remote Linux workspace at `/workspace` for working
with company data, building dashboards, scheduling jobs, and keeping a durable
collection of queries, scripts, and artifacts.

## Two execution surfaces

Two execution surfaces coexist in a MarcoPolo session:

- `workspace_shell` for all agent-side work: query authoring, analytics, DuckDB
  joins, workspace files, scripts, git, and cron inside `/workspace`.
- Product MCP data tools (`connections_list`, `data_query`) for generated code
  that re-queries live data at view or load time — Remote Artifacts, external
  web apps, scheduled scripts.

For all agent analytics, use `workspace_shell`. Reserve `data_query` for
programmatic interfaces, not for the agent's own data exploration.

## Session capability detection

Check which tools are available in the current session before choosing a path:

- Sessions with `connections_list` and `data_query` (Claude, Cursor, etc.):
  - Agent analytics → always use `workspace_shell`
  - Programmatic interfaces (web apps, scripts, dashboards) → use `data_query`
- Sessions with only `workspace_shell` (ChatGPT, older sessions):
  - Agent analytics → use `workspace_shell`
  - Generated artifact code → use `workspace_shell("connection query <name> --file <file> --json")` (bound with a SQL `LIMIT`), noting in the code that it can be upgraded to `data_query` if the session gains that tool

`workspace_shell` is the primary analytics tool in every session. `data_query`
is an addition for programmatic interfaces, not a replacement for agent work.

When using `workspace_shell` for queries, treat results as CLI envelopes:

- rows from `data` (present only when `--include-results` was passed)
- `row_count` from `row_count`, otherwise `len(rows)`
- `run_id` if present
- `relation_name` if present

By default a query returns only the relation handle (`relation_name` +
`row_count` + `column_count`); pass `--include-results` for the rows in `data`.
For large results, query the relation in DuckDB rather than pulling every row
into `data`.

## Two shell environments

Two shell environments coexist in this session:

- Your built-in shell and filesystem tools act on the client's own environment.
- `workspace_shell` runs commands inside the MarcoPolo remote workspace at
  `/workspace`.

Your built-in tools cannot reach the MarcoPolo workspace. They cannot read or
create files there, run the `connection` CLI or `crontab` that only exist there,
or see git state inside it. Only `workspace_shell` can.

So for all MarcoPolo workspace work, such as reading files, writing queries,
running scripts, or inspecting git, use `workspace_shell`. Reach for your
built-in tools only for things outside MarcoPolo.

User-uploaded files land in `data/uploads/` inside the MarcoPolo workspace.
`workspace_shell` reads them, not the built-in tools.

## Common `workspace_shell` operations

Treat `/workspace` like a checked-out repo. Common shapes:

- read files: `workspace_shell("cat /workspace/RULES.md")`
- list and search: `workspace_shell("ls connections/")`,
  `workspace_shell("rg <pattern> connections/")`
- write and edit files: `workspace_shell` with heredocs, `sed`, or other shell
  tools
- run scripts: `workspace_shell("python scripts/<file>.py")`
- inspect git state: `workspace_shell("git status")`,
  `workspace_shell("git diff")`

Read `RULES.md` and the relevant `workflows/` guide before authoring; use git
as part of normal work.

## MCP tool families

Product data tools:

- `connections_list` for connection discovery when available
- `data_query` for bounded governed query execution when available

Workspace and ext-app tools:

- `workspace_shell(command, timeout=30)` for remote workspace commands
- `connection_setup(type, intent_text=None)` for credentialed connection setup
- `install_demo_connection(demo_connection, display_name=None, intent_text=None)`
  for hosted demo connections

Some sessions may also expose legacy or host-specific tools. Do not rely on
them as the primary dashboard or query path unless a more specific skill tells
you to.

## The `connection` CLI is the workspace verb surface

For full reference see the `using-connection-cli` skill. The shape:

```text
connection <verb> [args] --json
```

Common verbs: `list`, `add`, `test`, `describe`, `query`, `browse`, `download`,
`upload`. Always pass `--json` so output is structured.

`connection list --json` returns each connection's `capabilities` array. That
list is authoritative. Never call `browse`, `download`, or `upload` on a
connection unless that verb appears in its capabilities.

## Workspace layout

```text
/workspace/
  README.md                       workspace overview
  RULES.md                        workspace-wide rules and conventions
  workflows/                      curated guides for recurring tasks
    README.md
    setup-connection.md
    query-and-analyze-data.md
  connections/                    one subdirectory per visible connection
    <name>/
      README.md
      RULES.md
      SYNTAX.md
      queries/
      metadata/
      profile/
      scratch/
    DUCKDB/
  scripts/
  artifacts/
  data/
    uploads/
    downloads/
    databases/
  .dv/
```

Always read first before authoring:

- `workspace_shell("cat /workspace/RULES.md")`
- `workspace_shell("cat /workspace/workflows/README.md")`
- `workspace_shell("cat connections/<name>/README.md connections/<name>/RULES.md connections/<name>/SYNTAX.md")`
- Before authoring or running any query, also read the `query-and-analyze` and
  `using-connection-cli` skills — they are prerequisites, not optional
  further reading.

`RULES.md` files are long-term memory — the workspace-level one holds general
conventions, and each `connections/<name>/RULES.md` holds connection-specific
facts: field quirks, reliable query patterns, naming conventions accumulated
from prior sessions. Read them before authoring queries and update them when
you discover new facts.

## DUCKDB is a connection

DUCKDB is the in-workspace analytical connection, backed by
`.dv/duckdb/workspace.duckdb`. Query it through the `connection` CLI:

```text
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

Use it for joins across connections, intermediate tables, and in-workspace
derived datasets.

## Where to put things

- query files -> `connections/<name>/queries/`
- metadata snapshots -> `connections/<name>/metadata/`
- reusable programs -> `scripts/`
- user-facing outputs -> `artifacts/`
- scheduled jobs -> the user crontab (`crontab -l`), not a workspace file
- user-provided data -> `data/uploads/`
- fetched data -> `data/downloads/`
- database files -> `data/databases/`

Do not write to `.dv/`; it is runtime-managed.

## Pointers

- adding a connection, installing a demo, fixing credentials -> `setup-connection`
- querying data, exploring schemas, joining sources -> `query-and-analyze`
- before running any `connection` verb (even routine ones) -> `using-connection-cli`
