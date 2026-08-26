# `connection describe`

```
workspace_shell("connection describe <name> [--database <db>] [--table <t>] --json")
```

Write metadata snapshots into `connections/<name>/metadata/` and return
the structure at the requested level.

## Why metadata snapshots matter

The snapshot files are the default in-workspace reference for query authoring.
They give you (and any future session) a stable view of the connection's
shape without having to re-hit the live system every time. When you write
queries against snapshots, you avoid wasting connection resources on
exploratory metadata calls and you get repeatable behavior — the snapshot
is what existed at the time of `describe`, regardless of what changed
later upstream.

## Drill-down levels

- no `--database` → list databases
- `--database <db>` → list tables in that database
- `--database <db> --table <t>` → list columns in that table

Each call writes a snapshot file at the appropriate level.

## Response shape

```json
{
  "success": true,
  "operation": "describe",
  "artifact_path": "connections/<name>/metadata/<file>",
  "databases": [...] | "tables": [...] | "columns": [...]
}
```

After running, read the file at `artifact_path` — that's the durable
reference, not the inline response.

## When to refresh

Run `describe` again only when:

- the connection is new and has no snapshot yet
- the user says the structure changed (new tables, renamed columns)
- a query fails because the structure no longer matches the snapshot
- the snapshot looks stale (old timestamp, missing recently-added objects)

Re-running on every query wastes connection resources and pollutes git
history.
