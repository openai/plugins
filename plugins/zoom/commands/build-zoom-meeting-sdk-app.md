---
description: Implement a Zoom Meeting SDK integration with the right platform-specific join or start flow, auth path, and verification loop.
---

# Build Zoom Meeting SDK App

Use this command when the repo needs to join, start, or embed real Zoom meetings through the Meeting SDK rather than a broader meeting workflow.

## Preflight

1. Inspect the codebase for existing Meeting SDK usage, target platform code, backend signature helpers, and meeting join UI.
2. Confirm the requirement is a real Zoom meeting and not a custom video session or an in-client Zoom app.
3. Identify the target platform: web, Android, iOS, macOS, Windows, Electron, React Native, Unreal, or Linux bot.
4. Check whether the required auth and meeting inputs exist without printing secrets: meeting number, password path, role, SDK auth material, and host start requirements.

## Plan

Before making changes:

- state the target Meeting SDK platform and user flow
- list the files that will be changed
- state the auth path, join or start flow, and any required backend pieces
- state how the implementation will be verified locally

## Commands

1. Add or correct Meeting SDK initialization at the appropriate client layer for the target platform.
2. Implement the smallest working join or start flow before adding advanced meeting controls or raw data features.
3. Add or correct the backend auth path needed for the chosen platform.
4. Keep platform-specific behavior explicit instead of forcing a generic abstraction over materially different SDKs.
5. Avoid leaking meeting credentials, signatures, or tokens in logs or command output.

## Verification

1. Re-read the client Meeting SDK code and supporting backend auth code after changes.
2. Run the relevant local build or tests where available.
3. Verify the join or start call shape, auth path, and expected meeting inputs.
4. State any remaining blocker such as missing credentials, waiting room constraints, unsupported environment, or platform setup gaps.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Meeting SDK integration
- Status: success | partial | failed
- Details: platform, files changed, auth path, verification run
```

## Next Steps

- Test the flow with a real meeting on the target platform.
- Add meeting controls or bot-like behavior only after the base join path works.
- If the requirement changes to a custom session product, switch to `/build-zoom-video-sdk-app`.
