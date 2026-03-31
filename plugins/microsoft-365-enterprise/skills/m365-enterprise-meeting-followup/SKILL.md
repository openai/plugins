---
name: m365-enterprise-meeting-followup
description: Build a cross-surface follow-up for one meeting or workstream. Use when the user wants event context, related email, Teams conversation, linked docs, and follow-up tasks synthesized into one practical output.
---

# Microsoft 365 Enterprise Meeting Follow-Up

Use this skill when one meeting or workstream spans Outlook, Teams, SharePoint, and Planner.

## Workflow

1. Start from the focal meeting or workstream and confirm the primary anchor:
   - Outlook event
   - email thread
   - Teams thread or chat
2. Pull the relevant Outlook event context with `fetch_event` or `search_events`.
3. Pull the relevant email context with `search_messages`, `fetch_message`, or `fetch_messages_batch`.
4. Pull the relevant Teams context with `search_teams`, `fetch_teams`, `list_chat_messages`, or `list_channel_messages`.
5. Pull the relevant document context with `search_sharepoint` and `fetch_sharepoint`.
6. Synthesize the decisions, open questions, owners, blockers, and next steps across those surfaces.
7. If the user asked for task creation, convert confirmed follow-ups into Planner tasks with `create_planner_task`.

## Safety

- Keep Outlook, Teams, and SharePoint evidence separate until the synthesis step.
- Do not claim cross-surface agreement when the sources actually disagree; call out the mismatch.
- Create tasks only from confirmed follow-ups, not speculative action items.

## Example Requests

- "Use the event, the email thread, the Teams messages, and the linked doc to tell me what happened and what I owe."
- "Turn the follow-ups from this workstream into Planner tasks."
