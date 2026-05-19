---
name: plan-zoom-product
description: Use when choosing products.
---

# /plan-zoom-product

> For local plugin installation and app mapping details, see [README.md](../../README.md).

Choose between Zoom REST API, Webhooks, WebSockets, Meeting SDK, Video SDK, Zoom Apps SDK, Phone, or Contact Center for a specific use case.

## Usage

```text
/plan-zoom-product $ARGUMENTS
```

## Workflow

1. Identify the user's actual goal.
2. Classify whether the problem is automation, embedded meetings, custom video, in-client app behavior, event delivery, AI tooling, or support/phone/contact-center work.
3. If the request is ambiguous, ask one short clarifier before locking the recommendation.
4. Recommend the primary Zoom surface and list the minimum supporting pieces.
5. Explain why the rejected alternatives are worse for this case.
6. End with a concrete next-step plan.

## Output

- Recommended Zoom surface
- Supporting components required
- Key tradeoffs and constraints
- Suggested implementation sequence
- Relevant skill links for the next step

## Related Skills

- [start](../start/SKILL.md)
- [choose-zoom-approach](../choose-zoom-approach/SKILL.md)
