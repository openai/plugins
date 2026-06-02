---
description: Isolate and fix Zoom authentication failures across OAuth, SDK signatures, and token refresh paths.
---

# Debug Zoom Auth

Use this command when a Zoom login flow, token exchange, or signature flow is failing and you need a concrete failure diagnosis.

## Preflight

1. Capture the exact failing symptom: error text, failing endpoint, affected surface, and whether the failure happens at authorize, callback, token exchange, refresh, or SDK join time.
2. Inspect the repository for the auth implementation, env var usage, callback handling, and token lifecycle code.
3. Identify the auth model in use: user-level OAuth, server-to-server or service auth where applicable, or SDK signature and token flows.
4. Confirm the presence of required config values without printing secrets.
5. If the issue report lacks the concrete error, ask for it before making speculative auth changes.

## Plan

Before changing anything:

- name the most likely failing layer
- list the evidence that will be checked
- list the files and commands involved
- state whether the workflow is read-only diagnosis or fix plus verification

## Commands

1. Inspect env and source usage for mismatched client IDs, redirect URIs, scope lists, token endpoints, or signature inputs.
2. For OAuth failures, verify exact redirect URI matching, token exchange parameters, and refresh-token rotation behavior.
3. For SDK auth failures, verify the expected server-side signature or token generation path for the specific SDK.
4. If the failure is caused by client capability mismatch, say that directly instead of pretending it is a token bug.
6. Apply only the minimum correction required to fix the identified layer.

## Verification

1. Re-run the failing path or reconstruct the exact auth request shape.
2. Confirm the corrected file, env var name, redirect URI, or server URL now matches the intended configuration.
3. If the failure persists, tighten the diagnosis to the next concrete layer rather than broadening scope.
4. State whether the issue is fixed, partially fixed, or blocked by missing credentials or external platform behavior.

## Summary

```text
## Result
- Action: diagnosed or fixed a Zoom auth failure
- Status: success | partial | failed
- Details: failing layer, evidence checked, fix applied, remaining blocker
```

## Next Steps

- Re-run the failing flow with the corrected auth path.
- If the issue is webhook-related after auth succeeds, run `/debug-zoom-webhook`.
