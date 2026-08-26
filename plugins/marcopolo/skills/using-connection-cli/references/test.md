# `connection test`

```
workspace_shell("connection test <name> --json")
```

Verify stored credentials for a connection.

## When to run

- Right after a new connection is added (via `connection_setup` or
  `install_demo_connection`).
- After the user changes credentials.
- When a query that used to work starts failing with auth-shaped errors.

There's no need to run `test` before every query — credentials don't
expire on a per-call basis.

## Response shape

On success:

```json
{
  "success": true,
  "operation": "test",
  "message": "Connection test succeeded."
}
```

On failure, surface `error` and `message` to the user. Most failures
indicate incomplete browser setup, wrong host/port, or missing network
access — not something you can fix from the session. The right next step
is usually to rerun `connection_setup` to reissue the browser flow.
