---
description: Implement a Zoom Contact Center integration for web, mobile, or backend workflows with the right auth and event handling.
---

# Build Zoom Contact Center App

Use this command when the repo needs Zoom Contact Center web, mobile, or backend integration work.

## Preflight

1. Inspect the codebase for existing Contact Center code, SDK usage, OAuth handling, and event consumers.
2. Identify the target platform and workflow: web embed, native wrapper, engagement handling, campaign flow, or backend orchestration.
3. Confirm the owning runtime and UI surface.
4. Check for the required auth, SDK, or endpoint configuration without printing secrets.

## Plan

Before making changes:

- state the target platform and Contact Center workflow
- list the files that will be changed
- state the auth path, event path, and interaction model
- state how the initial integration will be verified

## Commands

1. Add or correct the Contact Center integration at the proper platform layer.
2. Reuse existing app structure and avoid generic abstractions that hide platform-specific requirements.
3. Keep the first pass scoped to one concrete engagement or routing workflow.
4. Add the minimum auth, event, and UI wiring required for a working path.
5. Keep secrets and account-specific identifiers out of output.

## Verification

1. Re-read the platform integration files and supporting auth or event code that changed.
2. Run local build or tests where available.
3. Verify the configured workflow path and handler shape.
4. State any remaining blocker such as missing SDK setup, app configuration, or account prerequisites.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Contact Center workflow
- Status: success | partial | failed
- Details: platform, files changed, auth path, verification run
```

## Next Steps

- Test the target engagement flow in the intended environment.
- Expand to more event or campaign cases only after the base path works.
- If auth or delivery is failing, use the narrower setup or debug commands next.
