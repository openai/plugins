---
description: Implement a server-side Zoom integration with Rivet modules for auth, APIs, webhooks, and deployment-safe composition.
---

# Build Zoom Rivet App

Use this command when the repo should build a server-side Zoom integration around the Rivet SDK instead of hand-rolled API and webhook plumbing.

## Preflight

1. Inspect the codebase for existing Rivet usage, server entry points, OAuth handling, webhook receivers, and deployment configuration.
2. Confirm Rivet is the intended abstraction and not just a generic backend integration that should stay with direct API and webhook code.
3. Identify the required modules: app configuration, OAuth, API clients, webhook handlers, and business workflow handlers.
4. Check whether the required environment variables and deployment model are already represented without printing secrets.

## Plan

Before making changes:

- state the Rivet workflow being implemented
- list the files that will be changed
- state the auth path, webhook path, and module composition strategy
- state how the first working Rivet path will be verified

## Commands

1. Add or correct the Rivet-based module structure at the correct server layer.
2. Implement the smallest authenticated API path and webhook receiver before composing broader multi-module behavior.
3. Keep environment handling and deployment assumptions explicit, especially for Lambda-style or serverless receivers.
4. Reuse existing repo patterns for config, logging, and secret management where possible.
5. Avoid wrapping Rivet in unnecessary abstractions that make the auth and webhook paths harder to reason about.

## Verification

1. Re-read the Rivet module setup, auth handling, and webhook integration code after changes.
2. Run local build or tests where available.
3. Verify the module wiring, auth path, and first useful API or webhook flow.
4. State any remaining blocker such as framework drift, deployment mismatch, or missing app credentials.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Rivet integration
- Status: success | partial | failed
- Details: files changed, module setup, auth path, verification run
```

## Next Steps

- Exercise one real authenticated API path and one webhook flow.
- Expand to multi-module workflows only after the base path works.
- If Rivet is adding more complexity than value, fall back to direct REST plus webhook implementation.
