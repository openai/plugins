---
description: Inspect the repository and set up the correct Zoom OAuth path with the right app type, scopes, redirect handling, and token lifecycle.
---

# Setup Zoom OAuth

Use this command when the goal is to wire or correct a Zoom OAuth flow in application code, deployment config, or local development.

## Preflight

1. Inspect the repository for existing Zoom auth code, env templates, callback routes, and token storage patterns.
2. Identify the Zoom product surface involved: REST API, Meeting SDK, Video SDK, Team Chat, Phone, or Contact Center.
3. Confirm the expected app model and grant path from the current implementation or user intent.
4. Check for required values without printing secrets: client ID, redirect URI, scope list, callback handler, and token persistence location.
5. If the repo does not make the integration goal clear, ask one direct question before editing auth code.

## Plan

Before making changes:

- state which Zoom OAuth model will be implemented
- list the files that will be inspected or edited
- list the env vars and redirect URIs involved
- flag whether refresh-token handling or server-side token exchange must be added

## Commands

1. Search for existing Zoom auth usage with `rg` over `ZOOM_`, `oauth`, `redirect_uri`, `client_id`, and known Zoom endpoints.
2. Standardize the authorize and token exchange path for the chosen app model.
3. Add or correct env var names, callback routing, scope configuration, and token exchange code.
4. Treat refresh tokens as single-use values when implementing refresh logic.
5. Keep secrets out of the output and avoid logging access or refresh tokens.
6. If the user only asked for setup guidance, limit the change to the minimum required configuration and notes.

## Verification

1. Re-read the auth files and env templates that were changed.
2. Verify the redirect URI string matches exactly across code and configuration.
3. Verify the scope set is coherent for the Zoom surface in use.
4. If safe test credentials already exist, validate the auth URL shape and callback handling path without exposing secrets.
5. Call out any missing secret, callback endpoint, or deployment configuration that still blocks completion.

## Summary

```text
## Result
- Action: set up or corrected the Zoom OAuth path
- Status: success | partial | failed
- Details: app model, files changed, env vars used, scopes reviewed
```

## Next Steps

- Run the login flow once end to end and confirm the callback is reached.
- Test token refresh if the integration uses long-lived sessions.
