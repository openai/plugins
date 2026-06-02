---
description: Implement a Zoom REST API integration with the right resources, auth path, and verification loop.
---

# Build Zoom REST API App

Use this command when the repo should call Zoom REST endpoints directly for meetings, users, recordings, docs-adjacent workflows, or account resources.

## Preflight

1. Inspect the codebase for existing Zoom API usage, env vars, HTTP client wrappers, and server routes.
2. Confirm the requested workflow is actually a REST API problem and not better served by Meeting SDK, Video SDK, or Webhooks.
3. Identify the runtime that will own the Zoom API calls and token lifecycle.
4. Check whether the required OAuth values and scope configuration already exist without printing secrets.

## Plan

Before making changes:

- state the exact Zoom resource or endpoint family to implement
- list the files that will be created or edited
- state the auth model, token owner, and required scopes
- state how the new API flow will be verified

## Commands

1. Inspect the existing project structure and add the Zoom API integration at the narrowest appropriate layer.
2. Reuse existing HTTP client, config, and error-handling patterns where possible.
3. Add or correct Zoom OAuth token usage, API calls, request validation, and response shaping.
4. Keep secrets out of logs and avoid leaking access tokens in output.
5. Add minimal docs or examples only where they materially help the next developer use the integration.

## Verification

1. Re-read the edited files and confirm the endpoint, auth path, and error handling are coherent.
2. Run the relevant local tests or build if available.
3. If safe credentials already exist, exercise the narrowest live or mocked API path to confirm request shape.
4. State any remaining blocker such as missing scopes, callback setup, or account permissions.

## Summary

```text
## Result
- Action: implemented or updated a Zoom REST API integration
- Status: success | partial | failed
- Details: endpoints, files changed, auth path, verification run
```

## Next Steps

- Run one end-to-end request with real credentials if not already done.
- Add webhook handoff only if the use case actually needs it.
- If auth is incomplete, run `/setup-zoom-oauth` next.
