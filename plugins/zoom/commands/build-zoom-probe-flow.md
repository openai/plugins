---
description: Implement readiness checks with Zoom Probe SDK before users join meetings or sessions.
---

# Build Zoom Probe Flow

Use this command when the app needs pre-join diagnostics for browser, device, network, or environment readiness before Meeting SDK or Video SDK sessions.

## Preflight

1. Inspect the codebase for existing pre-join screens, media-permission checks, diagnostics code, and meeting or video join flows.
2. Confirm the requirement is readiness gating before join, not a general support diagnostics page unrelated to Zoom session entry.
3. Identify which checks matter for this workflow: browser support, camera, microphone, speaker, network, CPU, or diagnostic reports.
4. Check how failed checks should be handled: block join, warn the user, or capture telemetry.

## Plan

Before making changes:

- state the target join flow and the readiness checks in scope
- list the files that will be changed
- state the gating behavior and any telemetry or support output
- state how the probe flow will be verified

## Commands

1. Add or correct the Probe SDK integration at the pre-join layer of the app.
2. Run diagnostics before the Meeting SDK or Video SDK join path rather than during unrelated app initialization.
3. Keep probe results separate from tokens and avoid collecting unnecessary device details.
4. Add the minimum UI or state handling needed to communicate readiness and block or allow join appropriately.
5. Reuse existing telemetry or support-reporting patterns where possible.

## Verification

1. Re-read the diagnostics code, gating logic, and any reporting path after changes.
2. Run local build or tests where available.
3. Verify the probe checks run before join and influence the flow as intended.
4. State any remaining blocker such as HTTPS requirements, browser limitations, permission handling, or unsupported environments.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Probe readiness flow
- Status: success | partial | failed
- Details: files changed, checks added, gating behavior, verification run
```

## Next Steps

- Test the flow under both passing and failing device or network conditions.
- Tune the threshold between warn and block after observing real user behavior.
- If the app also needs the actual meeting or session join flow, wire the probe output into the corresponding build command next.
