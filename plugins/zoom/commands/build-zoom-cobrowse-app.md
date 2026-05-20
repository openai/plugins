---
description: Implement a Zoom Cobrowse integration with session lifecycle, privacy controls, and support workflow wiring.
---

# Build Zoom Cobrowse App

Use this command when the repo needs a browser co-browsing experience for support or guided assistance workflows.

## Preflight

1. Inspect the codebase for existing support tooling, session initialization code, frontend embeds, and auth or token generation helpers.
2. Confirm the workflow is truly browser co-browsing rather than Contact Center, Virtual Agent, or a general screen-sharing feature.
3. Identify the role model: customer page, agent console, session initiation path, and handoff mechanism.
4. Check whether required tokens, allowed origins, and privacy requirements are already represented without printing secrets.

## Plan

Before making changes:

- state the support workflow and role model
- list the files that will be changed
- state the auth path, session lifecycle responsibilities, and privacy controls in scope
- state how the base Cobrowse flow will be verified

## Commands

1. Add or correct the Cobrowse SDK initialization and base session lifecycle in the proper frontend and backend layers.
2. Implement the smallest working start or join flow before adding advanced annotations or remote-assist behavior.
3. Add privacy masking and blocked-element handling early when required by the workflow.
4. Reuse existing session management, logging, and support tooling patterns where possible.
5. Avoid pushing unrelated Contact Center or Virtual Agent abstractions into a Cobrowse-specific flow.

## Verification

1. Re-read the session initialization, auth path, and privacy or event-handling code after changes.
2. Run local build or tests where available.
3. Verify the start or join flow, session lifecycle, and privacy assumptions.
4. State any remaining blocker such as token generation, allowed-origin config, CORS or CSP, or browser constraints.

## Summary

```text
## Result
- Action: implemented or updated a Zoom Cobrowse integration
- Status: success | partial | failed
- Details: files changed, auth path, session lifecycle, verification run
```

## Next Steps

- Test one real support session end to end.
- Add remote assist or richer collaboration only after the base session path works.
- If the product choice is still uncertain, compare against Contact Center or Virtual Agent before expanding scope.
