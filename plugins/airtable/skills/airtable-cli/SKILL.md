---
name: airtable-cli
description: >-
    Lists bases, reads and writes records, manages tables and fields, filters and
    searches data in Airtable via the `airtable-mcp` CLI. Use when the task
    involves Airtable data or the user mentions airtable-mcp, bases, tables,
    records, or fields.
---

# airtable-mcp

## Self-discovery

Tools are fetched from the MCP server at runtime, so the CLI never has a hardcoded command list. Discover what's available:

```sh
airtable-mcp tools            # human-readable list
airtable-mcp tools --json     # machine-parseable list
airtable-mcp <tool> --help    # show flags and descriptions for a tool
```

Run `airtable-mcp tools` before assuming a tool exists. Tool names, arguments, and output shapes can change between server releases without a CLI update.

## Install

```sh
npm install -g @airtable/mcp-cli
```

## Auth

The CLI needs an Airtable personal access token (PAT). Two paths:

**Environment variable (preferred for scripts/agents):**

```sh
export AIRTABLE_TOKEN=pat_xxx
```

**Interactive configure (stores token in `~/.airtable/cli.json` with 0600 permissions):**

```sh
airtable-mcp configure
```

Create tokens at https://airtable.com/create/tokens. Ensure the token has the scopes required by the tools being called.

`AIRTABLE_TOKEN` takes precedence over saved profiles when no `--profile` flag is set. Never log or echo tokens.

## Quick reference

| Task                   | Command                                                 |
| ---------------------- | ------------------------------------------------------- |
| Set up credentials     | `airtable-mcp configure`                                |
| Add a named profile    | `airtable-mcp configure --profile work`                 |
| Check auth status      | `airtable-mcp whoami`                                   |
| Remove credentials     | `airtable-mcp logout`                                   |
| Remove all profiles    | `airtable-mcp logout --all`                             |
| List available tools   | `airtable-mcp tools`                                    |
| Run a tool             | `airtable-mcp <tool> --flagName value`                  |
| Get tool help          | `airtable-mcp <tool> --help`                            |
| Pass args via stdin    | `echo '{"key":"val"}' \| airtable-mcp <tool> --input -` |
| Bypass tool cache      | `airtable-mcp <tool> --refresh`                         |
| Suppress status msgs   | `airtable-mcp <tool> -q`                                |
| Raw text output        | `airtable-mcp <tool> --output raw`                      |
| Use a specific profile | `airtable-mcp <tool> --profile work`                    |

Tool names use hyphens on the CLI (`list-records`) but underscores in MCP (`list_records`). The CLI translates automatically.

## Workflow

1. **Auth** — set `AIRTABLE_TOKEN` or run `airtable-mcp configure`
2. **Discover** — run `airtable-mcp tools` to see available tools
3. **Inspect** — run `airtable-mcp <tool> --help` for flags and descriptions
4. **Check access** — in `tools --json` output, check the `access` field: `read-only`, `write`, or `destructive`. Confirm with the user before running `destructive` tools.
5. **Execute** — run `airtable-mcp <tool> --flagName value`

## Output & automation

-   Default output is formatted JSON to stdout. Status messages go to stderr.
-   `--json` on `tools` gives a JSON array of `{name, title, access}`.
-   `-q` / `--quiet` suppresses stderr status messages (cache warnings, etc).
-   `--output raw` returns the raw server response text instead of parsed JSON.
-   `--input -` reads tool arguments as a JSON object from stdin, bypassing flag parsing.
-   Exit codes: `0` success, `1` error (auth, tool failure, not found), `2` usage error (bad flags, bad input).

## Common tasks

**Find a base and list its tables:**

```sh
airtable-mcp search-bases --searchQuery "Project Tracker" -q
airtable-mcp list-tables-for-base --baseId appK9MtBqFw3o5jGN -q
```

**List records with specific fields:**

```sh
airtable-mcp list-records-for-table \
  --baseId appK9MtBqFw3o5jGN --tableId tblL4GpTfEz8byRsW \
  --fieldIds '["Name","Status"]' --pageSize 10 -q
```

**Filter records** — filters use structured JSON, not formula strings. Wrap conditions in an `operands` array; the top-level `operator` defaults to `and` if omitted:

```sh
airtable-mcp list-records-for-table \
  --baseId appK9MtBqFw3o5jGN --tableId tblL4GpTfEz8byRsW \
  --filters '{"operator":"and","operands":[{"operator":"=","operands":["Status","Done"]}]}' -q
```

For select fields, filter by choice ID (from `get-table-schema`), not the display name. The `airtable-filters` skill covers compound filters, date filters, and operator-by-field-type details.

**Search records** — use `search-records` for free-text/fuzzy queries on large tables. Use `list-records-for-table` with `--filters` when filtering by exact field values:

```sh
airtable-mcp search-records \
  --baseId appK9MtBqFw3o5jGN --table tblL4GpTfEz8byRsW \
  --query "acme" --fields '["Name","Notes"]' -q
```

Pass `--fields ALL_SEARCHABLE_FIELDS` to search across every indexed field. Date, rating, checkbox, and button fields are not searchable.

**Update records** — complex args are easier via `--input -`:

```sh
echo '{"baseId":"appK9MtBqFw3o5jGN","tableId":"tblL4GpTfEz8byRsW","records":[{"id":"recVnR3xPq8sD2yLk","fields":{"fld8WsrpLHHevsnW8":"Done"}}]}' \
  | airtable-mcp update-records-for-table --input - -q
```

Select field values are returned as objects (`{"id":"sel...","name":"Done"}`) but must be written as plain strings (`"Done"`). Record field keys in create/update currently require field IDs (`fldXXX`) — use `get-table-schema` to resolve names to IDs before writing. Note that `fieldIds`, `sort`, and `filters` accept both names and IDs.

## Gotchas

| Problem                                      | Cause                                                              | Fix                                                                      |
| -------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `Unknown tool: X`                            | Tool name doesn't exist on the server or cache is stale            | Run `airtable-mcp tools --refresh` to refresh, then retry                |
| `Authentication failed`                      | Token expired, revoked, or wrong                                   | Run `airtable-mcp configure` or check `AIRTABLE_TOKEN`                   |
| `Access denied`                              | Token missing required scopes                                      | Add scopes at https://airtable.com/create/tokens                         |
| `Connection timed out`                       | Server unreachable (10s timeout)                                   | Check network; CLI falls back to stale cache if available                |
| Boolean flags take no value                  | `--dryRun true` passes `"true"` as next arg                        | Use `--dryRun` alone (booleans are presence-based)                       |
| Array/object args fail                       | Value isn't valid JSON                                             | Pass as JSON string: `--fieldMappings '{"a":"b"}'`                       |
| Filter rejected at top level                 | Single condition passed without `operands` wrapper                 | Wrap in `{"operands":[...]}` (`operator` defaults to `and`)              |
| Sort key is `fieldId` not `field`            | `--sort '[{"field":"Name"}]'` silently ignored                     | Use `{"fieldId":"Name","direction":"asc"}` — accepts field IDs or names  |
| Select filter returns no matches             | Filtering by display name instead of choice ID                     | Run `get-table-schema` first to get `sel...` choice IDs                  |
| `INVALID_RECORDS` on batch write             | Batch limit is 10 records per request (default; varies by account) | Split into chunks of ≤10 and check `<tool> --help` for the current limit |
| Permission error on `list-records-for-table` | User has interface-only access to the base                         | Use `list-records-for-page` / `get-record-for-page` instead              |
| Endpoints restricted                         | CLI only allows HTTPS on `*.airtable.com`                          | Cannot point at arbitrary servers (security constraint)                  |
