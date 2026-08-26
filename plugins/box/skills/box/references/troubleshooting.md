# Troubleshooting

## Table of Contents

- Debugging checklist
- 401 or 403
- 404
- 409
- 429
- Webhook verification failures
- Search quality problems
- MCP server not connected
- MCP tool missing
- CLI auth problems
- Codex sandbox network access

## Debugging checklist

Before changing code, capture these facts:

- Acting auth context
- Exact endpoint and HTTP method
- Box object type and ID
- Minimal request payload
- Response status and error body

Most Box failures reduce to one of these mismatches: wrong actor, wrong object ID, wrong endpoint, or an access-control change that was never confirmed.

When using Box CLI, run `box <command> --help` before the first invocation of any subcommand to confirm it exists in the installed version and to verify flag names, required arguments, and supported options.

## 401 or 403

- Wrong auth context
- Missing scope or app permission
- Acting user does not have access to the target object
- Token expired, downscoped, or issued for a different flow than expected

## 404

- Wrong file or folder ID
- Object exists but is not visible to the current actor
- Shared link or collaboration refers to a different object than expected

## 409

- File or folder name conflict on create or upload
- Collaboration already exists
- Metadata write conflicts with the expected template or instance state

## 429

- Rate limit or burst traffic
- Missing backoff and retry handling
- Excessive search or listing requests without pagination controls
- Bulk operations (batch moves, folder creation, metadata writes) sending requests too quickly — read the `Retry-After` header and wait that many seconds before retrying
- Parallel Box CLI invocations — the CLI must run serially; concurrent calls cause auth conflicts and can trigger rate limits faster than expected
- For bulk workflows, add a 200–500ms pause between serial operations and implement proper `Retry-After` backoff; see `references/bulk-operations.md`

## Webhook verification failures

- Wrong signing secret
- Request body mutated before signature verification
- Timestamp tolerance or replay checks missing
- The code logs the body before verification and accidentally changes normalization

## Search quality problems

- Missing ancestor-folder, type, owner, or metadata filters
- Querying as the wrong actor
- Expecting search to return content the current identity cannot see
- Downloading too early instead of returning IDs and metadata first

## MCP server not connected

Box MCP tools are not appearing in the session, or MCP calls fail with auth errors.

- `CLIENT_ID` or `CLIENT_SECRET` is missing or incorrect in the platform's MCP config. Verify the config has a `box` server entry with both values set. Never ask the user to paste credentials into the conversation.
- The Box OAuth 2.0 app is missing the platform's redirect URI
- The MCP config file has stale or malformed credentials — re-copy the Client ID and Client Secret from the Box Developer Console
- Third-party plugins are not enabled in the platform settings
- The editor was not restarted after making auth changes — MCP connections are established at startup
- The Box admin has not enabled the MCP server integration in the [Admin Console](https://developer.box.com/guides/authorization/)

**Quick diagnostic:** If other MCP servers work but Box does not, the issue is Box-specific auth. If no MCP servers work, the issue is platform configuration.

**Workaround:** Fall back to Box CLI while the user resolves MCP auth. See `references/box-cli.md` for CLI auth setup. If CLI is not available, request explicit user confirmation before using REST fallback and follow `references/rest-calls.md`.

## MCP tool missing

If the user asks to use a Box MCP tool that seems like it should work but it is not visible in the current client, check the updated/maintained tool list at https://docs.box.com/en/box-mcp/tools. If the tool appears there but is not discoverable or callable, it may be disabled in the Box Admin Console or by the MCP client. Refer the user to https://docs.box.com/en/box-mcp/admin-controls to enable tools in the Box Admin Console, then close and reopen the MCP client, reconnect their Box account, or start a new chat if the tool list appears cached.

## CLI auth problems

- `box` is installed but the current environment is not authorized
- The command is running as the wrong CLI actor because `--as-user` was omitted or mis-set
- A direct token passed with `-t` overrides the expected CLI environment
- Someone used environment-inspection commands that print sensitive values instead of safe auth checks like `box users:get me --json`

## Codex sandbox network access

Box CLI commands that worked in a regular terminal fail inside Codex with `getaddrinfo ENOTFOUND api.box.com` or a generic "Unexpected Error" with no HTTP body. Auth checks like `box users:get me --json` may still pass because they use cached local credentials, making it look like auth works but API calls do not.

**Cause:** Codex sandboxes block outbound network access by default. The CLI cannot reach `api.box.com`, `upload.box.com`, or any other Box endpoint.

**Fix for Codex CLI:** Add to `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
network_access = true
```

Then restart the Codex CLI session.

**Fix for Codex web (cloud):** In the environment settings, turn agent internet access **On** and add `box.com` and `boxcloud.com` to the domain allowlist.

**How to tell this is the problem:** If `box users:get me --json` succeeds but `box files:get <ID> --json` fails with a DNS or connection error, the sandbox is blocking outbound network access. The same commands will work in a regular terminal outside of Codex.
