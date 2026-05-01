---
description: Triage a broken Zoom integration when the failing layer is not yet obvious.
---

# Debug Zoom

Use this command when something in a Zoom integration is broken but the failure has not yet been narrowed to auth, webhooks, SDK behavior, or RTMS.

## Preflight

1. Capture the exact symptom: error text, failing endpoint, platform, runtime, and whether the failure is deterministic or intermittent.
2. Inspect the repository for the relevant Zoom integration code, env usage, event handlers, or SDK setup.
3. Note what still works versus what fails so the broken layer can be isolated.
4. If the report lacks the concrete error or failing path, ask for that evidence before making speculative changes.

## Plan

Before changing anything:

- state the most likely failing layer
- list the evidence that will be checked first
- list the repo files or runtime paths involved
- state whether the goal is diagnosis only or diagnosis plus a minimal fix

## Commands

1. Inventory the active Zoom surfaces in the failing workflow.
2. Narrow the problem to one layer: auth, REST request construction, webhook verification, WebSocket lifecycle, SDK initialization, or RTMS stream handling.
3. Inspect the smallest relevant code path and supporting configuration first.
4. Apply the minimum correction needed if the failure is clear.
5. If the layer cannot be fixed yet, produce ranked hypotheses instead of broad speculation.
6. Route to narrower follow-up commands when appropriate, such as `/debug-zoom-auth` or `/debug-zoom-webhook`.

## Verification

1. Re-run or reconstruct the failing path after any fix.
2. Confirm the diagnosis is tied to concrete repo evidence or exact runtime behavior.
3. State whether the issue is fixed, partially fixed, or blocked by missing credentials, account setup, or external platform behavior.

## Summary

```text
## Result
- Action: triaged a broken Zoom integration
- Status: success | partial | failed
- Details: failing layer, evidence checked, fix applied or ranked hypotheses
```

## Next Steps

- Use the narrower debug or setup command for the confirmed failing layer.
- If the architecture itself is wrong, run `/plan-zoom-product` or `/plan-zoom-integration`.
- If the repo is healthy but the client integration path is wrong, switch to the matching build command.
