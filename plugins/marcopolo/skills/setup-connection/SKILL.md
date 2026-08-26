---
name: setup-connection
description: Adds a new connection to the MarcoPolo workspace — hosted demo connections (no credentials) and credentialed connections to databases, warehouses, APIs, and storage (Postgres, Snowflake, BigQuery, Salesforce, S3, Google Drive, etc.). Use this skill whenever the user mentions adding, connecting, installing, hooking up, or wiring up a datasource — even when they describe it informally ("connect my Snowflake", "try the demo data", "let me hook up our Salesforce", "I want to look at the data in S3"). Also use when troubleshooting `connection test` failures, expired credentials, or an OAuth flow that didn't finish.
---

# Set up a connection

There are two paths: a **hosted demo connection** (no credentials, installs
in one call) and a **credentialed connection** (the user opens a browser
setup flow). Both end with the same verification steps inside the workspace.

The in-workspace canonical reference is `/workspace/workflows/setup-connection.md`.

## Path A — install a hosted demo connection

Use this when the user wants to try MarcoPolo without bringing their own
credentials, or asked for a specific demo dataset.

Call the MCP tool directly:

```
install_demo_connection(
  demo_connection="<id-or-natural-language>",
  intent_text="<optional free text>",
  display_name="<optional friendly name>",
)
```

Behavior:

- If `demo_connection` matches a known demo id, it installs immediately.
- If ambiguous, the response has `success: false`, `resolution_mode:
  "ambiguous"`, and `available_demo_connections: [{id, label, description, type}, ...]`.
  Show the user the choices and call again with a specific `id`.
- If unknown, the response includes `available_demo_connections` you can
  offer the user.

On success, run the post-install verification (below).

## Path B — add a credentialed connection

Use this when the user has their own database, warehouse, API, or storage
account.

1. Generate the setup URL via the MCP tool.

   ```
   connection_setup(type="<canonical-type>", intent_text="<optional free text>")
   ```

   `type` should be a canonical type value (`pg`, `mysql`, `snowflake`,
   `bigquery`, `s3`, `google_drive`, `salesforce`, `local_file`, etc.). If
   unsure, pass the user's words as `intent_text` and a best-guess `type` —
   the tool will resolve via intent if `type` is non-canonical. If still
   unknown, the response returns `valid_types` and `suggested_types`; pick
   from those and retry.

   On success, the response includes:
   - `url` — open this in a browser; the user signs in and configures
     credentials
   - `workflow_type` — typically `oauth` or `configure`
   - `instructions` and `next_actions` — surface these to the user
   - `configuration_schema` (for `configure` workflows) — the fields the
     setup UI will collect
   - `workspace_ssh_keypair` (for connections that support SSH tunnelling)
     — show the public key so the user can authorize it on their bastion

2. Surface the URL to the user and wait. Do not try to complete setup from
   the session — the user has to click through the browser flow.

3. Once the user says they're done, confirm the connection is visible.

   ```
   workspace_shell("connection list --json")
   ```

   If it doesn't appear yet, wait briefly and retry — provisioning can take
   a moment.

## Post-install verification (both paths)

1. Verify credentials.

   ```
   workspace_shell("connection test <name> --json")
   ```

   On failure, surface `error` and `message` to the user. For credential
   issues, send them back through `connection_setup` to update credentials.

2. Read the seeded connection docs.

   ```
   workspace_shell("cat connections/<name>/README.md connections/<name>/SYNTAX.md connections/<name>/RULES.md")
   ```

   The `README.md` lists the connection's authoritative `capabilities`. Note
   them before doing anything else with the connection.

3. Write initial metadata snapshots.

   ```
   workspace_shell("connection describe <name> --json")
   ```

   This populates `connections/<name>/metadata/`. The snapshot files become
   the default in-workspace reference for query authoring.

4. Confirm the directory shape.

   ```
   workspace_shell("ls connections/<name>/")
   ```

   Expect: `README.md`, `RULES.md`, `SYNTAX.md`, `queries/`, `metadata/`,
   `profile/`, `scratch/`.

## Troubleshooting

- **`connection_setup` returns `Unknown connection type`.** The response
  includes `valid_types` and `suggested_types`. Pick a canonical value and
  retry. If user intent is natural language, also pass `intent_text`.
- **`install_demo_connection` returns `ambiguous`.** Surface
  `available_demo_connections` to the user and retry with a specific id.
- **`connection test` fails after setup.** Likely cause: incomplete browser
  flow, wrong host/port, or missing network access. Surface the error
  message to the user; for credential changes, rerun `connection_setup` to
  reissue the setup URL.
- **Connection not visible in `connection list --json`.** Wait and retry —
  provisioning may still be running. If it persists, surface that to the
  user.

## Pointers

- writing the first query → `query-and-analyze`
- per-verb flag reference → `using-connection-cli`
- workspace layout → `using-marcopolo-workspace`
