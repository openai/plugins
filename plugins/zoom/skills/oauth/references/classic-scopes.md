# Classic OAuth Scopes

Source: https://developers.zoom.us/docs/integrations/oauth-scopes/

This file is intentionally compact. Do not mirror the full Zoom classic scope catalog into the plugin; it changes over time and is too large for a local Codex reference bundle. Use the official source above as the authoritative endpoint-to-scope lookup.

## Format

Classic scopes are broader than granular scopes and usually follow this shape:

```text
{resource}:{action}:{level}
```

Common parts:

| Part | Examples | Meaning |
|---|---|---|
| `resource` | `meeting`, `recording`, `user`, `webinar`, `chat`, `phone`, `docs` | Zoom product/API area |
| `action` | `read`, `write` | Read or manage capability |
| `level` | omitted, `admin`, `master` | Own-user, account admin, or master-account access |

Examples:

```text
meeting:read
meeting:write
meeting:read:admin
meeting:write:admin
recording:read
recording:read:admin
user:read
user:write:admin
imchat:bot
phone:read
phone:write:admin
```

## When To Use Classic Scopes

Use classic scopes when:

- The endpoint documentation only lists classic scopes.
- You are maintaining an older Marketplace app that already uses classic scopes.
- The app legitimately needs broad access across a resource family.

Prefer granular scopes when:

- The endpoint supports granular scopes.
- The app only needs a narrow operation.
- The consent screen should expose the smallest possible access surface.

## Access Levels

| Level | Access pattern | Notes |
|---|---|---|
| omitted | Current user’s own resources | Usually available to normal user authorization if the app is installed |
| `admin` | Account-level resources | Requires suitable app type, scope approval, and admin authorization |
| `master` | Master/sub-account operations | Only use when the API and account model explicitly require it |

## Lookup Workflow

1. Identify the exact REST endpoint.
2. Open the official classic scope catalog or endpoint reference.
3. Search by endpoint name, operation ID, or resource term.
4. Confirm whether granular alternatives are available.
5. Add only the required scopes and re-authorize users after changes.

## Common Mistakes

- Do not request `:admin` scopes for user-owned workflows unless account-wide access is required.
- Do not use classic scopes as a shortcut when granular scopes are available and narrower.
- Do not assume Server-to-Server OAuth supports every endpoint; verify the endpoint and app type.
- Do not keep stale access tokens after changing scopes; complete OAuth again.
