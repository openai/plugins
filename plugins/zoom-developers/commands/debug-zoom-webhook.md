---
description: Diagnose Zoom webhook issues across endpoint validation, signature verification, event delivery, retries, and handler logic.
---

# Debug Zoom Webhook

Use this command when Zoom webhook events are not arriving, signature validation is failing, endpoint validation is broken, or handlers are processing the wrong payload shape.

## Preflight

1. Inspect the repo for webhook routes, signature verification code, event subscriptions, and deployment endpoint configuration.
2. Capture the failing symptom: no events, validation failure, signature mismatch, retries, or handler-side processing error.
3. Confirm the public callback URL, webhook secret env var name, and raw body handling path without printing secrets.
4. Check whether the implementation uses the exact raw request body for signature verification.
5. If the repo has no webhook endpoint yet, say that before attempting webhook debugging.

## Plan

Before changing anything:

- identify whether the likely fault is registration, validation, signature verification, transport, or business logic
- list the files and logs that will be checked
- state whether a replay or local reproduction will be used

## Commands

1. Inspect endpoint registration and subscribed event names.
2. Verify the endpoint validation flow is implemented for the expected Zoom webhook handshake.
3. Verify signature checking uses the raw request body, correct timestamp handling, and the right secret source.
4. Inspect handler parsing and downstream logic separately from signature verification.
5. Reproduce the failing request path with a safe replay or fixture when possible.
6. Apply the minimum fix needed to the failing layer instead of rewriting the entire webhook stack.

## Verification

1. Re-read the webhook route and verification helper after changes.
2. Confirm the endpoint validation path now returns the expected response shape.
3. Confirm the signature verification code operates on the raw body and correct headers.
4. If logs or replay are available, verify the handler reaches application logic successfully.
5. If delivery still fails, state whether the remaining blocker is registration, public reachability, or Zoom-side configuration.

## Summary

```text
## Result
- Action: diagnosed or fixed a Zoom webhook issue
- Status: success | partial | failed
- Details: failing layer, files checked, fix applied, remaining blocker
```

## Next Steps

- Send one real or replayed event through the endpoint.
- Add regression coverage for signature verification and endpoint validation if missing.
- If the root cause is auth or app setup, run `/debug-zoom-auth` or `/setup-zoom-oauth` next.
