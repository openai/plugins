---
name: zoom-oauth
description: Use when implementing OAuth.
---

# Zoom OAuth

Use this skill for concrete Zoom authentication implementation and troubleshooting. Prefer `setup-zoom-oauth` for the first-pass setup plan, then return here for exact flows, scope behavior, refresh handling, and error diagnosis.

## Workflow

1. Identify the app type and actor: user-level OAuth, account-level OAuth, server-to-server OAuth where officially supported, SDK JWT, or Build-platform credentials.
2. Confirm the target API, SDK, or app surface, because scopes and token audiences differ by surface.
3. Choose the grant flow: authorization code with PKCE for public clients, authorization code for confidential web apps, device authorization where appropriate, or account credentials for supported account-level automation.
4. Store refresh tokens as single-use values: persist the replacement refresh token returned by each refresh response before reusing the old one.
5. Validate requests against redirect URI, account ID, scopes, app publication state, and token expiration before changing application code.
6. For local development, keep access tokens out of logs and treat refresh tokens as single-use when rotating credentials.

## References

- Full preserved guide: [references/full-guide.md](references/full-guide.md)
- OAuth flows: [concepts/oauth-flows.md](concepts/oauth-flows.md)
- Token lifecycle: [concepts/token-lifecycle.md](concepts/token-lifecycle.md)
- Scope architecture: [concepts/scopes-architecture.md](concepts/scopes-architecture.md)
- Granular scopes: [references/granular-scopes.md](references/granular-scopes.md)
- OAuth errors: [references/oauth-errors.md](references/oauth-errors.md)
- Redirect URI issues: [troubleshooting/redirect-uri-issues.md](troubleshooting/redirect-uri-issues.md)
