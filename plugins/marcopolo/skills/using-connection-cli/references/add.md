# `connection add`

```
workspace_shell("connection add --type <CONNECTION_TYPE> [--intent <text>] --json")
```

Generate a browser setup URL for a credentialed connection.

## When to use the CLI vs. the MCP tool

For interactive setup from a session, prefer the `connection_setup` MCP
tool — it returns the same shape as `connection add` plus a scoped API
token for the browser flow. The CLI form is the right choice inside
scripts and scheduled jobs that need to surface a setup URL without going
through the MCP layer.

## Flags

- `--type` (required) — canonical connection type. Examples: `pg`,
  `mysql`, `snowflake`, `bigquery`, `s3`, `google_drive`, `salesforce`,
  `local_file`. If you pass a non-canonical value, the CLI may resolve it
  via aliases or via `--intent`.
- `--intent` (optional) — free-text description of what the user wants to
  connect. Used as a fallback when `--type` is non-canonical or
  ambiguous.
- `--json` — return structured envelope; always pass this.

## Response shape

On success:

```json
{
  "success": true,
  "operation": "add",
  "type": "<canonical-type>",
  "workflow_type": "oauth" | "configure",
  "url": "<browser-setup-url>",
  "message": "...",
  "instructions": ["..."]
}
```

Surface `url` and `instructions` to the user. They have to complete the
flow in a browser — the CLI cannot finish setup on its own.

On unknown type:

```json
{
  "success": false,
  "error": "Unknown connection type ...",
  "valid_types": [...],
  "suggested_types": [...],
  "next_actions": ["..."]
}
```

Pick a canonical value from `valid_types` or `suggested_types` and retry.

## After setup

Run `connection list --json` to confirm the connection appeared, then
`connection test <name> --json` to verify credentials, then
`connection describe <name> --json` to seed `connections/<name>/metadata/`.
See the `setup-connection` skill for the full flow.
