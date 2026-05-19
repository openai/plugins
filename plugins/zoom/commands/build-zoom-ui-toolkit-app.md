---
description: Implement a Zoom Video SDK UI Toolkit integration for a prebuilt web session UI with the right auth, mount strategy, and session lifecycle.
---

# Build Zoom UI Toolkit App

Use this command when the repo needs a prebuilt web UI for a Zoom Video SDK session instead of a fully custom video interface.

## Preflight

1. Inspect the codebase for existing Video SDK usage, web frontend structure, server-side token generation, and session UI shells.
2. Confirm the requirement is a prebuilt Video SDK UI and not a real Zoom meeting flow.
3. Identify the host framework and where the UI Toolkit should mount.
4. Check whether the required Video SDK session auth path exists without printing secrets.

## Plan

Before making changes:

- state the target web framework and session UX goal
- list the files that will be changed
- state the auth path, mount strategy, and session lifecycle responsibilities
- state how the UI Toolkit flow will be verified

## Commands

1. Add or correct the UI Toolkit integration in the appropriate web UI layer.
2. Wire the minimum server-side signature or auth path required for a working session join.
3. Keep custom UI work limited unless the user explicitly needs it beyond the toolkit surface.
4. Configure permissions, session join and leave behavior, and any required media settings.
5. Avoid mixing Meeting SDK assumptions into a Video SDK UI Toolkit integration.

## Verification

1. Re-read the UI mount code, Video SDK auth path, and session join flow after changes.
2. Run the relevant local build or tests where available.
3. Verify the toolkit mount path, auth flow, and base session lifecycle.
4. State any remaining blocker such as browser restrictions, token generation gaps, or unsupported environment requirements.

## Summary

```text
## Result
- Action: implemented or updated a Zoom UI Toolkit integration
- Status: success | partial | failed
- Details: files changed, auth path, mount strategy, verification run
```

## Next Steps

- Test the session in the target browser environment.
- If deeper layout control is required, switch to `/build-zoom-video-sdk-app`.
- If auth is incomplete, fix the token path before expanding UI work.
