---
description: Implement a Zoom Virtual Agent integration for web or mobile wrapper environments with the right lifecycle and event handling.
---

# Build Zoom Virtual Agent

Use this command when the repo needs to embed or wrap Zoom Virtual Agent on web, Android, or iOS.

## Preflight

1. Inspect the codebase for existing web views, wrapper bridges, event handlers, and auth or context-passing code.
2. Identify the target platform and Virtual Agent launch path.
3. Confirm the lifecycle constraints for the host app and any required native bridge behavior.
4. Check for the required configuration values without printing secrets.

## Plan

Before making changes:

- state the target platform and Virtual Agent workflow
- list the files that will be changed
- state the launch path, event handling path, and host-app responsibilities
- state how the initial integration will be verified

## Commands

1. Add or correct the Virtual Agent embed or wrapper code at the appropriate platform layer.
2. Keep the implementation aligned with the host framework’s lifecycle and bridge patterns.
3. Add the minimum launch, event, and context update logic required for a working path.
4. Separate wrapper concerns from broader application state where possible.
5. Avoid leaking secrets or user tokens in logs or output.

## Verification

1. Re-read the embed or wrapper code and any supporting bridge files that changed.
2. Run local build or tests where available.
3. Verify the launch and message or event path shape.
4. State any remaining blocker such as missing platform config, unsupported host behavior, or app setup gaps.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Virtual Agent workflow
- Status: success | partial | failed
- Details: platform, files changed, launch path, verification run
```

## Next Steps

- Test the embedded agent in the intended runtime.
- Add deeper host-app integration only after the base launch path works.
- If wrapper lifecycle handling is unstable, narrow the integration before expanding scope.
