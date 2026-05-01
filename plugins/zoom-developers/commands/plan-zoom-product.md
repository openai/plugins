---
description: Choose the right Zoom product surface for a use case and explain the tradeoffs clearly.
---

# Plan Zoom Product

Use this command when the repo or product idea needs the right Zoom surface selected before implementation begins.

## Preflight

1. Inspect the repository for any existing Zoom integration code, SDK packages, API routes, or webhooks.
2. Capture the user goal in concrete terms: automation, embedded meetings, custom video, in-client app behavior, event delivery, live media, or AI tooling.
3. Identify hard constraints that affect product choice: target platform, required UX, hosting model, latency, account model, and whether the app runs inside or outside Zoom.
4. If the repo already uses one Zoom surface, note it before recommending a different one.

## Plan

Before recommending anything:

- list the candidate Zoom surfaces that fit the problem
- state the primary decision criteria
- state whether the output is read-only guidance or includes follow-on implementation
- state which path will be recommended unless the repo evidence contradicts it

## Commands

1. Inventory existing Zoom-related code with `rg` over known Zoom SDK names, API clients, and webhook handlers.
2. Classify the problem into the smallest correct Zoom surface: REST API, Webhooks, WebSockets, Meeting SDK, Video SDK, Zoom Apps SDK, RTMS, Phone, Contact Center, Virtual Agent, or a hybrid.
3. Recommend one primary surface and only the minimum supporting pieces required.
4. Explain why adjacent alternatives are worse for this exact case.
5. Keep the answer tied to the current repo and delivery goal rather than giving a generic product catalog.

## Verification

1. Confirm the recommendation matches the user’s actual product goal and the repo’s current shape.
2. Call out any missing evidence or assumptions that could change the decision.
3. Verify the recommendation includes the owning auth model and any mandatory supporting components.

## Summary

```text
## Result
- Action: selected the right Zoom product surface
- Status: success | partial | failed
- Details: recommended surface, supporting pieces, tradeoffs, assumptions
```

## Next Steps

- If the surface is chosen, run the matching build or setup command next.
- If the product still spans multiple Zoom surfaces, run `/plan-zoom-integration`.
- If the decision depends on missing constraints, gather those before implementing.
