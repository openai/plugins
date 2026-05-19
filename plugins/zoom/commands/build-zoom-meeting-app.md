---
description: Implement an embedded or managed Zoom meeting flow in the current codebase with the right SDK and auth path.
---

# Build Zoom Meeting App

Use this command when the repo needs to embed or launch real Zoom meetings with the Meeting SDK or adjacent server-side join flow.

## Preflight

1. Inspect the codebase for existing Zoom meeting code, frontend framework, backend support, and auth handling.
2. Confirm the requested experience is a real Zoom meeting and not a custom video experience that belongs on Video SDK.
3. Identify the target platform: web, mobile, desktop, or multi-platform.
4. Check whether the codebase already has the required server-side token or signature path without printing secrets.

## Plan

Before making changes:

- state the target platform and Meeting SDK surface
- list the files that will be changed
- state the join or start flow, auth path, and required backend pieces
- state how the meeting flow will be verified locally

## Commands

1. Inspect current app structure and place the meeting integration in the correct UI and server layers.
2. Add or correct Meeting SDK initialization, join or start flow, and backend auth support.
3. Keep the implementation aligned with the target platform’s established patterns instead of forcing a generic abstraction.
4. Add only the minimum UI, env wiring, and server code needed for a working meeting flow.
5. Keep secrets, tokens, and meeting credentials out of output and logs.

## Verification

1. Re-read the meeting client code and any server auth helpers that changed.
2. Run the relevant local build or tests.
3. Verify the UI path reaches the expected join or start call shape.
4. State any remaining blocker such as missing credentials, callback setup, domain config, or SDK prerequisites.

## Summary

```text
## Result
- Action: implemented or updated a Zoom meeting app flow
- Status: success | partial | failed
- Details: platform, files changed, auth path, verification run
```

## Next Steps

- Test the join or start flow with a real meeting.
- Add webhook or bot-side follow-up only if the product needs it.
- If the requirement is actually custom media control, switch to `/build-zoom-video-sdk-app`.
