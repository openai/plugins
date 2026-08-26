# `connection list`

```
workspace_shell("connection list --json")
```

Discover connections visible in the current workspace.

## Why use it first

The response is the only authoritative source for what each connection can
do in this workspace. Connection types and capabilities can change as the
platform evolves and as the user's permissions change, so don't rely on
prior knowledge of "Snowflake supports X" — read what `list` actually
returns.

## Response shape

```json
{
  "success": true,
  "operation": "list",
  "count": <int>,
  "connections": [
    {
      "name": "<connection-name>",
      "type": "<canonical-type>",
      "capabilities": ["query", "describe", ...],
      "workspace_path": "connections/<name>"
    }
  ]
}
```

`capabilities` is the list of `connection` verbs allowed for this
connection. Treat it as the gate for `browse`, `download`, and `upload` —
do not call those verbs unless they appear here.

## Common patterns

- Run `list` first whenever you don't already know what's available.
- Re-run `list` after `connection_setup` or `install_demo_connection` to
  confirm a new connection appeared.
- After a job suddenly starts failing, re-run `list` to check whether the
  connection's capabilities changed.
