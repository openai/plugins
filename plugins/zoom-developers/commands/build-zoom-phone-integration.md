---
description: Implement a Zoom Phone integration around APIs, Smart Embed, calling flows, and event handling.
---

# Build Zoom Phone Integration

Use this command when the repo needs Zoom Phone APIs, embedded phone experiences, CTI-style workflows, or call-related automation.

## Preflight

1. Inspect the codebase for existing phone integration code, OAuth handling, embed surfaces, and event consumers.
2. Identify whether the workflow is Smart Embed, direct API usage, call automation, CRM integration, or another phone-specific path.
3. Confirm the runtime and UI surface that will own the phone workflow.
4. Check for the required auth and event configuration without printing secrets.

## Plan

Before making changes:

- state the Phone workflow being implemented
- list the files that will be changed
- state the auth path, event path, and user interaction surface
- state how the initial phone flow will be verified

## Commands

1. Add or correct the Zoom Phone integration at the appropriate UI or backend layer.
2. Reuse existing routing, event, and API abstractions where possible.
3. Keep the first pass focused on one concrete calling or phone-data workflow.
4. Add the minimum configuration, auth handling, and event logic required for a working path.
5. Avoid blending general meeting assumptions into phone-specific workflows.

## Verification

1. Re-read the phone integration code and supporting auth or event code that changed.
2. Run local build or tests where available.
3. Verify the API, embed, or event path shape.
4. State any remaining blocker such as missing account setup, OAuth scope gaps, or runtime prerequisites.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Phone integration
- Status: success | partial | failed
- Details: files changed, auth path, event path, verification run
```

## Next Steps

- Exercise one real call-related workflow end to end.
- Add CRM or analytics follow-up only after the base integration works.
- If auth is incomplete, run `/setup-zoom-oauth`.
