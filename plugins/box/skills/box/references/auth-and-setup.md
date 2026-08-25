# Auth and Setup

## Table of Contents

- MCP server auth
  - Diagnosing auth failures
  - Retrieving credentials from an existing app
  - Creating a Box OAuth 2.0 app
  - Setting up credentials
  - Completing auth
- Actor selection checklist
- CLI-first local testing
- Choosing the auth path
- Choosing SDK vs REST
- Inspecting an existing codebase
- Common secrets and config
- Official Box starting points

## MCP server auth

The plugin provides the Box skill and safety rules. The Box MCP server
authenticates via OAuth 2.0, and the connection is configured by the user
through their platform's MCP settings/config file. This keeps credentials in
the user's own config and avoids the complexity of environment-variable
resolution. For platform-specific config paths and examples, use the current
client's connector or MCP setup documentation.

Prefer the marketplace path first: if the user's client has a connector/plugin
marketplace, direct them to connect to Box through it. For the list of supported
clients, see https://docs.box.com/en/box-mcp/supported-ai-platforms and walk
them through those instructions. Only set up a custom MCP connection if the
client is not on that list.

The Box OAuth app must also have the platform's redirect URI registered.

If MCP tools are not appearing in the session:

1. Check your platform MCP config for a Box server entry. If it contains a `box` server with `CLIENT_ID` and `CLIENT_SECRET` values, the MCP server should be available. Verify by calling `who_am_i`. If it fails, the OAuth flow may not have been completed — call `mcp_auth` to trigger it.
2. If no Box server entry exists, guide the user through `references/auth-and-setup.md` to create or retrieve OAuth credentials and add the server:

```json
{
  "mcpServers": {
    "box": {
      "url": "https://mcp.box.com",
      "auth": {
        "CLIENT_ID": "<client_id>",
        "CLIENT_SECRET": "<client_secret>"
      }
    }
  }
}
```

If the file already contains other MCP servers, merge the `box` entry into the existing `mcpServers` object — do not overwrite the file. Never write credentials into the conversation or into files inside a repository.

3. Confirm the OAuth app has the correct redirect URI for the platform.
4. Confirm any platform setting required for third-party plugins or MCP integrations is enabled.
5. Restart the editor only as a last resort — MCP connections are established at startup.

### Diagnosing auth failures

If MCP tools are unavailable or `mcp_auth` fails, run these checks (never print credential values):

1. **Check your platform MCP config for a Box server entry.** If it contains a `box` server with `CLIENT_ID` and `CLIENT_SECRET` values, the MCP server should be available. Verify by calling `who_am_i`. If it fails, the OAuth flow may not have been completed — call `mcp_auth` to trigger it.
2. If the platform MCP config has no Box server entry, ask the user whether they already have a Box OAuth 2.0 app:
   - **Yes** — direct them to retrieve their credentials (see "Retrieving credentials from an existing app" below) and then configure them (see "Setting up credentials").
   - **No** — walk them through creating one (see "Creating a Box OAuth 2.0 app") and then configuring the credentials.
3. If credentials are configured but auth still fails, verify the OAuth app has the correct redirect URI for the platform (see below).
4. Confirm any platform setting required for third-party plugins or MCP integrations is enabled.
5. Restart the editor only as a last resort — MCP connections are established at startup.

### Retrieving credentials from an existing app

If the user already has a Box OAuth 2.0 app:

1. Go to the [Box Developer Console](https://app.box.com/developers/console).
2. Find the existing app and open it.
3. On the **Configuration** tab, copy the **Client ID** and **Client Secret**.
4. Verify that the platform's redirect URI is listed under **OAuth 2.0 Redirect URI**. Add it if missing, then click **Save Changes**.

Then proceed to "Setting up credentials" below.

### Creating a Box OAuth 2.0 app

Walk the user through these steps if they do not already have a Box OAuth app:

1. Go to the [Box Developer Console](https://app.box.com/developers/console).
2. Click **Create New App** and choose **Custom App**.
3. Select **User Authentication (OAuth 2.0)** as the authentication method.
4. Name the app (for example, "Box MCP") and click **Create App**.
5. On the app's **Configuration** tab, copy the **Client ID** and **Client Secret**.
6. Under **OAuth 2.0 Redirect URI**, add the callback URI documented by the current client.
7. Click **Save Changes**.

If the user's Box enterprise requires admin approval for new apps, they will need to submit the app for authorization in the [Admin Console](https://developer.box.com/guides/authorization/) before it can complete the OAuth flow.

### Setting up credentials

Add the Box server in your platform's MCP settings/config. Example:

```json
{
  "mcpServers": {
    "box": {
      "url": "https://mcp.box.com",
      "auth": {
        "CLIENT_ID": "<client_id_from_step_5>",
        "CLIENT_SECRET": "<client_secret_from_step_5>"
      }
    }
  }
}
```

Environment-variable setup is not required for MCP credentials. Whether restart is needed depends on platform; if tools do not appear, restart the editor/session and retry.

### Completing auth

After credentials are configured:

1. The agent calls `mcp_auth` to start the OAuth flow.
2. A browser window opens with the Box login page — the user authorizes the app.
3. Box redirects back to the platform via the registered callback URI.
4. The agent verifies the connection with `who_am_i`.

If the user cannot complete MCP auth immediately, fall back to Box CLI for the current session. See the CLI-first local testing section below.

## Actor selection checklist

Choose the acting identity before you choose endpoints or debug errors:

- Connected user: use when the product acts on behalf of an end user who linked their Box account.
- Enterprise service account: use when the backend runs unattended against enterprise-managed content.
- App user: use when the product provisions managed Box identities per tenant or workflow.
- Existing token from the platform: use when the surrounding app already resolved auth and passes the token into the Box layer.

Always capture which actor you are using in logs, test output, and the final answer. Many Box bugs are actually actor mismatches.

## CLI-first local testing

When the task is a local smoke test, quick inspection, or one-off verification from Codex, prefer Box CLI before raw REST if `box` is already installed and authenticated.

- Check CLI auth safely with `box users:get me --json`.
- If CLI auth is missing:
  - Fastest OAuth path: `box login -d`
  - Use your own Box app: `box login --platform-app`
  - Use an app config file: `box configure:environments:add PATH`
- Use `--as-user <id>` when you need to verify behavior as a managed user or another actor allowed by the current Box environment.
- Use `-t <token>` only when the task explicitly requires a direct bearer token instead of the current CLI environment.
- For CLI auth guardrails (safe checks, commands to avoid), see `references/box-cli.md`.
- For token-first REST verification, prefer environment-based auth (for example `BOX_ACCESS_TOKEN`) and pass the token via `Authorization: Bearer ...` headers. Avoid printing or echoing token values in logs or command output.

## Choosing the auth path

- Preferred order for agent operations: MCP first, CLI second, direct REST last.
- If MCP auth fails, guide the user through MCP setup and retry before shifting tools.
- If CLI is needed, guide the user through CLI login and verify with `box users:get me --json` before shifting tools.
- Use direct REST only after MCP and CLI remain unavailable (or CLI is explicitly declined) and after the user explicitly approves REST fallback.
- For REST fallback, prefer obtaining a fresh access token from configured Box app credentials/OAuth flow over relying on manually copied short-lived developer tokens.
- Reuse the repository's existing Box auth flow if one already exists.
- Use a user-auth flow when end users connect their own Box accounts and the app acts as that user.
- Use the enterprise or server-side pattern already approved for the Box app when the backend runs unattended or manages enterprise content.
- Treat impersonation, app-user usage, token exchange, or downscoping as advanced changes. Add them only when the product requirements clearly demand them.
- Verify the exact flow against the current auth guides before introducing a new auth path or changing scopes.

## Choosing SDK vs REST

- Use an official Box SDK when the target language already has one in the codebase or the team prefers SDK-managed models and pagination.
- Use direct REST calls when the project already centers on a generic HTTP client, only a few endpoints are needed, or SDK support does not match the feature set.
- In agent-driven operations, direct REST is a fallback path. Do not use it by default when MCP or CLI can be set up.
- Avoid mixing SDK abstractions and handwritten REST calls for the same feature unless there is a clear gap.
- Preserve the project's existing retry, logging, and error-normalization patterns.

## Inspecting an existing codebase

Search for:

- `box`
- `BOX_`
- `client_id`
- `client_secret`
- `enterprise`
- `shared_link`
- `webhook`
- `metadata`

Confirm:

- Where access tokens are issued, refreshed, or injected
- Whether requests are user-scoped, service-account-scoped, or app-user-scoped
- Whether the codebase already has pagination, retry, and rate-limit helpers
- Whether webhook verification already exists
- Whether file and folder IDs are persisted in a database, config, or user settings

## Common secrets and config

- Client ID and client secret
- Private key material or app config used by the approved Box auth flow
- Enterprise ID, user ID, or app-user identifiers when relevant
- Webhook signing secrets
- Default folder IDs
- Metadata template identifiers and field names
- Shared link defaults such as access level or expiration policy
- Box CLI environment names or `--as-user` conventions when the team uses CLI-based operations

## Official Box starting points

- Developer guides: https://developer.box.com/guides
- API reference root: https://developer.box.com/reference
- SDK overview: https://developer.box.com/guides/tooling/sdks/
- Authentication guides: https://developer.box.com/guides/authentication/
- CLI guides: https://developer.box.com/guides/cli
- CLI OAuth quick start: https://developer.box.com/guides/cli/quick-start

Check the current Box docs before introducing a new auth model, changing scopes, or changing Box AI behavior, because auth guidance and SDK coverage can evolve independently from the content endpoints.
