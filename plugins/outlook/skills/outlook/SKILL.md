---
name: outlook
description: Route unified Microsoft Outlook workflows across mail, calendar, and contacts. Use when the user needs one Outlook workflow that spans inbox context, scheduling context, or saved contacts without switching connectors.
---

# Outlook

## Overview

Use this skill to route work on the unified Microsoft Outlook connector. This connector combines mail, calendar, and contacts, so use it when the request crosses those surfaces or needs shared Outlook identity and recipient context.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Inspect, create, update, or organize Outlook contacts | [../outlook-contacts/SKILL.md](../outlook-contacts/SKILL.md) |
| Turn email context into scheduling options, an event, or a reply draft | [../outlook-scheduling-from-email/SKILL.md](../outlook-scheduling-from-email/SKILL.md) |
| Build a meeting follow-up from event context plus related mail | [../outlook-meeting-followup/SKILL.md](../outlook-meeting-followup/SKILL.md) |

## Specialist Handoffs

- For deep mailbox work such as inbox triage, reply drafting, forwards, and cleanup, use [../../../outlook-email/skills/outlook-email/SKILL.md](../../../outlook-email/skills/outlook-email/SKILL.md).
- For deep calendar work such as availability ranking, free-up-time planning, or recurring-series maintenance, use [../../../outlook-calendar/skills/outlook-calendar/SKILL.md](../../../outlook-calendar/skills/outlook-calendar/SKILL.md).
- Keep this plugin focused on combined-surface workflows plus contacts. Do not duplicate the full Outlook Email or Outlook Calendar specialist packs here.

## Core Truths

- Unified Outlook combines mail, calendar, and contacts in one connector.
- Outlook email writes remain plain-text only even on the unified connector.
- Contact workflows here are for recipient resolution, cleanup, and organization, not CRM or sales-pipeline work.
- If the task is clearly specialist and single-surface, prefer the matching specialist Outlook plugin rather than forcing everything through the unified connector.

## Routing

- Use this base skill when the workflow spans:
  - email thread + availability or event creation
  - event context + related email
  - contact lookup or cleanup before replying, forwarding, or scheduling
- If the request is mailbox-only, hand off to Outlook Email.
- If the request is calendar-only, hand off to Outlook Calendar.

## Example Requests

- "Use Outlook to turn this email thread into a proposed meeting time and draft the reply."
- "Look up the right saved contact before I send this follow-up."
- "Tell me what changed between the invite and the related email thread."
