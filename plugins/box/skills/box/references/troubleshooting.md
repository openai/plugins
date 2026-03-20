# Troubleshooting

## Table of Contents

- Debugging checklist
- 401 or 403
- 404
- 409
- 429
- Webhook verification failures
- Search quality problems
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
