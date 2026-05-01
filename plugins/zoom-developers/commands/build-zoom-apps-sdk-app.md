---
description: Implement a Zoom Apps SDK app that runs inside the Zoom client with the right running context, auth path, and backend integration.
---

# Build Zoom Apps SDK App

Use this command when the repo should build an app that runs inside the Zoom client rather than embedding Zoom in an external app.

## Preflight

1. Inspect the codebase for existing Zoom Apps SDK usage, frontend framework, backend APIs, and auth handling.
2. Confirm the requirement is truly an in-client Zoom app and not a Meeting SDK or Video SDK workflow.
3. Identify the required running context: meeting, webinar, main client, phone, collaborate mode, immersive mode, camera mode, or another supported context.
4. Check for required Marketplace app settings, allowed domains, redirect URIs, and in-client OAuth requirements without printing secrets.

## Plan

Before making changes:

- state the target running context and user flow
- list the files that will be changed
- state the auth model, backend responsibilities, and any capability gating
- state how the app will be verified locally or in Zoom client testing

## Commands

1. Add or correct Zoom Apps SDK initialization in the correct frontend surface.
2. Configure capability checks and gate features by running context instead of assuming global support.
3. Add the minimum backend or API wiring needed for the app’s first useful flow.
4. Wire in-client OAuth or supporting backend auth only where the chosen workflow requires it.
5. Keep domain allowlists, callback paths, and app configuration aligned with the implementation.
6. Avoid mixing external embed assumptions into an in-client Zoom app architecture.

## Verification

1. Re-read the client initialization, capability checks, and backend integration code after changes.
2. Run local build or tests where available.
3. Verify the app load path, running-context assumptions, and first useful user action.
4. State any remaining blocker such as allowlist gaps, missing Zoom client context, or app configuration mismatch.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Apps SDK app
- Status: success | partial | failed
- Details: running context, files changed, auth path, verification run
```

## Next Steps

- Test the app inside the intended Zoom client context.
- Add advanced client capabilities only after the base app loads reliably.
- If the requirement is to run outside Zoom client, switch to the appropriate meeting, video, or REST flow.
