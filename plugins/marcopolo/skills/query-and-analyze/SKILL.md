---
name: query-and-analyze
description: Queries connections, joins results across sources through DuckDB, and analyzes workspace data. Use this skill whenever the user wants to look at, count, summarize, filter, group, join, aggregate, compare, or analyze data, or when exploring a connection's schema or doing follow-up analysis on a previous query.
---

# Query and analyze data

Use this skill for all agent-side analytics: query authoring, schema exploration,
DuckDB materialization, joins across sources, and file analysis.

**Tool selection:**
- `workspace_shell("connection query ...")` is the correct tool for all agent
  analytics. The full result is always materialized into DuckDB; by default the
  command returns only the relation handle (`relation_name` + `row_count` +
  `column_count`), not the rows. Pass `--include-results` when you need the rows
  inline in `data`.
- `data_query` is for generated code that re-queries live data at view or load
  time: Remote Artifacts, external web apps, scheduled scripts. Do not use it
  for agent analytics or one-off snapshot visualizations — embed those inline.

**Session compatibility:** Some sessions (e.g. ChatGPT) expose only
`workspace_shell` and do not have `connections_list` or `data_query`. Check
which tools are available before deciding on a path. `workspace_shell` works
in every session and is the primary analytics tool in all cases.

## Required workflow — follow every step

### Step 1 — Orient in the workspace

```text
workspace_shell("cat /workspace/RULES.md")
```

This is the workspace's long-term memory. Read it before touching any connection.

### Step 2 — Discover connections

Use `connections_list` if the current session exposes it. Otherwise:

```text
workspace_shell("connection list --json")
```

Pick the connection(s) needed. Confirm `query` appears in each connection's
`capabilities`.

### Step 3 — Load connection context

For each connection:

```text
workspace_shell("cat connections/<name>/README.md connections/<name>/SYNTAX.md connections/<name>/RULES.md")
```

`RULES.md` is long-term memory for that connection — field quirks, naming
conventions, reliable query patterns, and known limitations accumulated from
prior sessions. Read it before authoring any query.

### Step 4 — Inspect schema and existing queries

```text
workspace_shell("ls connections/<name>/queries/ connections/<name>/metadata/")
```

If `describe` is in capabilities and metadata is missing or stale:

```text
workspace_shell("connection describe <name> --json")
```

Prefer adapting an existing query over writing from scratch.

### Step 5 — Author a query file

Write to a file under `connections/<name>/queries/`. Use a business-readable
filename. The file extension and query format are determined by the connection
type — use `SYNTAX.md` (loaded in Step 3) as the authoritative reference for
both. Do not default to `.sql` unless SYNTAX.md confirms the connection uses SQL.

```text
workspace_shell("""cat > connections/<name>/queries/<filename>.<ext> <<'EOF'
<query content per SYNTAX.md>
EOF""")
```

**Common patterns by connection type:**

| Connection type | Extension | Query format |
|---|---|---|
| SQL databases (Snowflake, BigQuery, DuckDB) | `.sql` | Standard SQL `SELECT` |
| Salesforce (SOQL) | `.json` | `{"soql": "SELECT ... FROM Object WHERE ..."}` |
| Object storage (S3, SFTP) | `.json` | Path or glob pattern per SYNTAX.md |
| Document storage (Google Drive, OneDrive) | `.json` | File path or search spec per SYNTAX.md |
| Other SaaS APIs | `.json` | Endpoint + parameters object per SYNTAX.md |

If SYNTAX.md does not specify an extension, default to `.json` for API-based
connections and `.sql` for SQL-native connections.

### Step 6 — Execute the query

```text
workspace_shell("connection query <name> --file connections/<name>/queries/<filename>.<ext> --json")
```

The full result is always materialized into DuckDB. By default the command
returns only the relation handle (`relation_name` + `row_count` +
`column_count`), not the rows — so a large result never floods context. Query
the relation in DuckDB (Step 7), or pass `--include-results` to get the rows
inline in `data`, bounding large results with a SQL `LIMIT`. See the
`using-connection-cli` skill for full flag reference and timeout guidance.

`data` in the response envelope is a JSON-encoded **string** — call
`json.loads(resp["data"])` to get `list[dict]`. `rows` in the envelope is an
int count, not a record list. For group-bys, totals, or joins, skip parsing
`data` and run a DuckDB query over `relation_name` (Step 7) instead.

### Step 7 — Analyze and join through DuckDB

Each upstream query materializes as a `relation_name` in DuckDB. Use it for
aggregations, joins across connections, and transformations:

```text
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

Save reusable joins in `connections/DUCKDB/queries/`.

### Step 8 — Export large results for the user

When the user needs to retrieve a large result set, export from DuckDB to CSV
in `/workspace/data/downloads/` for pickup from the MarcoPolo web UI:

```sql
COPY (SELECT * FROM <relation_name>) TO '/workspace/data/downloads/<filename>.csv' (HEADER, DELIMITER ',');
```

Run via:

```text
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/export.sql --json")
```

### Step 9 — Offer to save learnings

After answering the user's question, offer to save any new facts discovered —
schema quirks, reliable query patterns, field naming conventions, known
limitations — to the appropriate RULES.md:

- Connection-specific: `connections/<name>/RULES.md`
- Workspace-wide: `/workspace/RULES.md`

Ask the user to confirm before writing. Saving these enriches the context layer
for future sessions.

## Join across connections through DuckDB

DuckDB is the in-workspace analytical connection.

1. Run each upstream `connection query` first and note each `relation_name`.
2. Write a DuckDB SQL file that joins or transforms those relations.
3. Execute through DuckDB.

   ```text
   workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
   ```

## Work with files in the remote workspace

- User-provided files belong in `data/uploads/`.
- Files fetched via `connection download` land in `data/downloads/`.
- Use `data/databases/` for database files when needed.

DuckDB can read CSV, Parquet, and JSON files directly:

```text
workspace_shell("""cat > connections/DUCKDB/queries/<file>.sql <<'SQL'
SELECT * FROM read_csv_auto('data/uploads/<file>.csv') LIMIT 100
SQL""")
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

## Common pitfalls

- The `connection` CLI only exists inside the remote workspace — always use
  `workspace_shell` for workspace commands.
- Trust `connection list --json` or `connections_list` for capabilities.
- Query through named files, not inline SQL.
- **Rows are opt-in.** By default a query returns only the relation handle, not
  the rows; the full dataset is materialized in DuckDB regardless. Pass
  `--include-results` for the rows inline (with a SQL `LIMIT` for large results),
  or query the relation in DuckDB.
- Query file paths in `--file` resolve from `/workspace`, not from your current
  directory — always include the `connections/<name>/` prefix. A bare
  `queries/<file>` resolves to `/workspace/queries/<file>` and fails with
  "No such file or directory" even if you just created the file via
  `cd <connection-dir> && cat > queries/<file>`.

## Pointers

- adding a connection or installing a demo → `setup-connection`
- per-verb flag reference → `using-connection-cli`
- workspace layout → `using-marcopolo-workspace`
