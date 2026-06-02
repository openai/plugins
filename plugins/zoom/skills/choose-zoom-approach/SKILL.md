---
name: choose-zoom-approach
description: Use when choosing architecture.
---

# Choose Zoom Approach

Pick the smallest correct Zoom surface for the job, then layer in only the supporting pieces that are actually required.

## Decision Framework

| Problem Type | Primary Zoom Surface |
|---|---|
| Deterministic backend automation, account management, reporting, scheduled jobs | [rest-api](../rest-api/SKILL.md) |
| Event delivery to your backend | [webhooks](../webhooks/SKILL.md) or [websockets](../websockets/SKILL.md) |
| Embed Zoom meetings into your app | [meeting-sdk](../meeting-sdk/SKILL.md) |
| Build a fully custom video experience | [video-sdk](../video-sdk/SKILL.md) |
| Build inside the Zoom client | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| Real-time media extraction or meeting bots | [rtms](../rtms/SKILL.md) plus [meeting-sdk](../meeting-sdk/SKILL.md) when needed |
| Phone workflows | [phone](../phone/SKILL.md) |
| Contact Center or Virtual Agent flows | [contact-center](../contact-center/SKILL.md) or [virtual-agent](../virtual-agent/SKILL.md) |

## Guardrails

- Do not recommend Video SDK when the user actually needs Zoom meeting semantics.
- Do not recommend Meeting SDK when the user needs a fully custom session product.
- Keep deterministic backend automation in REST APIs and event-driven code.

## What To Produce

- One recommended path
- Minimum supporting components
- Hard constraints and tradeoffs
- Immediate next implementation step
