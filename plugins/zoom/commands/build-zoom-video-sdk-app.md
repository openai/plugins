---
description: Implement a custom Zoom Video SDK session workflow with the right auth, session lifecycle, and verification path.
---

# Build Zoom Video SDK App

Use this command when the repo needs a custom video experience rather than an actual Zoom meeting UI.

## Preflight

1. Inspect the codebase for existing video session code, frontend stack, backend support, and auth helpers.
2. Confirm the use case is a custom session workflow and not a standard Zoom meeting flow.
3. Identify the target platform and expected media features.
4. Check whether the required server-side auth or session token path already exists without printing secrets.

## Plan

Before making changes:

- state the target platform and custom session goal
- list the files that will be changed
- state the auth path, session lifecycle responsibilities, and media features in scope
- state how the implementation will be verified locally

## Commands

1. Add or correct Video SDK initialization, session join flow, auth handling, and lifecycle management.
2. Keep the implementation aligned with the platform’s existing architecture.
3. Limit the first pass to the minimum working session path unless the user explicitly asks for broader UI or media controls.
4. Add or update the supporting server code needed to mint the correct auth material.
5. Avoid mixing Meeting SDK assumptions into Video SDK code.

## Verification

1. Re-read the client and server files that changed.
2. Run the relevant local build or tests.
3. Verify the session auth shape and the basic connect flow.
4. State any remaining blocker such as missing credentials, unsupported environment, or unresolved media prerequisites.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Video SDK workflow
- Status: success | partial | failed
- Details: platform, files changed, auth path, verification run
```

## Next Steps

- Test the session with real participants or a controlled local environment.
- Add advanced media features only after the base session path works.
- If the requirement is actually to join real Zoom meetings, switch to `/build-zoom-meeting-app`.
