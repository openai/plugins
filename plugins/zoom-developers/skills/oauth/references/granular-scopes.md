# Granular OAuth Scopes

Source: https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

This file is intentionally compact. Do not mirror the full Zoom granular scope catalog into the plugin; it changes over time and is too large for a local Codex reference bundle. Use the official source above as the authoritative endpoint-to-scope lookup.

## Format

Granular scopes are narrower than classic scopes and usually follow this shape:

```text
{service}:{action}:{data_claim}:{access_level}
```

Common parts:

| Part | Examples | Meaning |
|---|---|---|
| `service` | `meeting`, `cloud_recording`, `docs`, `whiteboard`, `contact_center` | Zoom product/API area |
| `action` | `read`, `write`, `update`, `delete` | Operation type |
| `data_claim` | `assets`, `search`, `content`, `whiteboard`, `collaborator` | Specific resource or capability |
| `access_level` | `user`, `admin`, `master` | Own-user, account admin, or master-account access |

Prefer granular scopes when the app only needs specific capabilities. They reduce consent surface and avoid overbroad classic scopes.

## Lookup Workflow

1. Identify the exact API endpoint or SDK capability.
2. Open the official granular scope catalog.
3. Search by endpoint name, operation ID, or resource term.
4. Add only the listed scopes for the operation.
5. Re-authorize the user after adding scopes; existing user tokens will not automatically gain newly added scopes.

## Common Mistakes

- Do not guess granular scope names from the URL path; verify against the official scope catalog.
- Do not mix user-level and admin-level assumptions. A user token cannot perform admin operations unless the app and authorizing user have the required admin scope and permissions.
- Do not rely on old tokens after adding scopes. Re-run OAuth authorization and token exchange.
