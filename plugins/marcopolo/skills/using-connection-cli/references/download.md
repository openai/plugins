# `connection download` (capability-gated)

```
workspace_shell("connection download <name> --remote-path <provider-path> [--local-path <workspace-path>] --json")
```

Fetch a provider file into the workspace.

## Capability rule

Only call `download` if the connection's `capabilities` array (from
`connection list --json`) includes `download`. Skip it otherwise.

## Flags

- `--remote-path <provider-path>` (required) — provider-side file path
  to download.
- `--local-path <workspace-path>` (optional) — workspace destination
  path. Defaults under `data/downloads/` if omitted, which is the
  conventional landing place for fetched files.
- `--json` — always pass.

## Response shape

```json
{
  "success": true,
  "operation": "download",
  "source_file": "<provider-path>",
  "destination": "<workspace-path>"
}
```

## Where to put downloads

Default to `data/downloads/` so fetched files are co-located with other
external data and don't pollute connection-specific working directories.
If the user wants downloads grouped with a specific analysis, point
`--local-path` into a project-shaped directory (e.g.,
`projects/<name>/inputs/<file>`).

## After downloading

To analyze the file with SQL, query it through DUCKDB — DuckDB can read
CSV, Parquet, JSON, and others directly from a path:

```
workspace_shell("""cat > connections/DUCKDB/queries/<file>.sql <<'SQL'
SELECT * FROM read_csv_auto('data/downloads/<file>.csv') LIMIT 100
SQL""")
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```
