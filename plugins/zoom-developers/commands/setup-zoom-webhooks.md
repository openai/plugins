---
description: Implement or correct a Zoom webhook receiver with endpoint validation, signature verification, and reliable delivery handling.
---

# Setup Zoom Webhooks

Use this command when the integration receives Zoom events over HTTP and needs a correct webhook receiver path.

## Preflight

1. Inspect the repository for existing webhook routes, signature verification helpers, queueing, and downstream event handlers.
2. Identify the event types and the Zoom app or account scope that owns the subscription.
3. Confirm the public endpoint shape, validation requirements, and webhook secret env var names without printing secrets.
4. If the repo actually needs low-latency persistent delivery instead of HTTP callbacks, say so before proceeding and compare against WebSockets.

## Plan

Before making changes:

- state the event types and endpoint path being implemented
- list the files that will be changed
- state the validation, signature, and retry-handling approach
- state how the webhook flow will be verified

## Commands

1. Add or correct the webhook receiver route at the appropriate backend layer.
2. Implement endpoint validation and signature verification before business logic.
3. Keep handlers idempotent and preserve delivery metadata needed for replay protection or debugging.
4. Separate ingestion from slow downstream work when reliability matters.
5. Reuse existing logging, queue, and secret-management patterns where possible.
6. Avoid claiming the webhook path works until validation and signature handling are both checked.

## Verification

1. Re-read the webhook route, validation logic, and signature helper after changes.
2. Run local build or tests where available.
3. Verify the endpoint validation path and the signed-event path independently.
4. State any remaining blocker such as public reachability, missing app configuration, or subscription settings.

## Summary

```text
## Result
- Action: implemented or updated a Zoom webhook receiver
- Status: success | partial | failed
- Details: route, event types, signature path, verification run
```

## Next Steps

- Send or replay one real event through the receiver.
- If delivery reaches the route but fails later, run `/debug-zoom-webhook`.
- If auth or app setup is missing, run `/setup-zoom-oauth`.
