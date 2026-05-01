---
description: Run a read-first audit of a Zoom integration and report the most important architecture, auth, eventing, and SDK risks.
---

# Zoom Integration Doctor

Use this command for a broad diagnostic pass when a repo already contains Zoom integration code and you want a prioritized assessment before making changes.

## Preflight

1. Inventory the repository for Zoom-related files, env vars, SDK packages, and webhook routes.
2. Identify which Zoom surfaces are in play: REST API, Meeting SDK, Video SDK, Webhooks, WebSockets, Phone, or Contact Center.
3. Confirm whether the user wants a read-only audit or is also authorizing fixes in the same pass.
4. Check for dirty working tree and call it out if changes could complicate attribution.

## Plan

Before doing the audit:

- list the surfaces that will be reviewed
- state whether the audit is read-only or includes fixes
- state the ranking criteria: correctness, auth safety, architectural fit, and maintainability

## Commands

1. Inventory the active Zoom surfaces and determine whether the product choice matches the use case.
2. Review auth handling for app model, scopes, secret storage, redirect handling, and token lifecycle.
3. Review eventing for webhook signature handling, retries, or WebSocket suitability.
4. Review SDK usage for version drift, wrong surface choice, or incorrect server-side dependencies.
5. Review integration boundaries for unnecessary coupling, unclear ownership, and avoidable auth complexity.
6. Report findings ordered by severity. Do not bury the top risks under implementation detail.
7. Only make code changes if the user explicitly wants fixes applied in the same run.

## Verification

1. Confirm every reported finding points to concrete file or config evidence.
2. If fixes were applied, re-read the edited files and summarize the before or after state.
3. Distinguish confirmed issues from assumptions or missing evidence.

## Summary

```text
## Result
- Action: completed a Zoom integration audit
- Status: success | partial | failed
- Details: surfaces reviewed, top risks, fixes applied if any
```

## Next Steps

- Apply the highest-severity fixes first.
- Use the narrower setup or debug commands for the affected layer.
- Re-run the doctor after major auth or eventing changes to confirm the risk list shrank.
