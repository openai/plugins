---
name: outlook-meeting-followup
description: Build Outlook meeting follow-ups from event context plus related email. Use when the user wants to understand what changed around a meeting, draft the right follow-up, or connect the invite with the related mailbox thread.
---

# Outlook Meeting Follow-Up

Use this skill when the workflow spans an Outlook event and the related mailbox context.

## Workflow

1. Start from the focal event with `fetch_event` or `search_events`.
2. Pull the nearby email context with `search_messages`, `fetch_message`, or `fetch_messages_batch` when the meeting clearly has a related thread.
3. Compare what the invite says versus what the email thread says:
   - attendee expectations
   - timing changes
   - location or Teams-link changes
   - outstanding questions
   - follow-up commitments
4. If the user wants a follow-up email, draft it with `create_reply_draft` or `draft_email`.
5. If the user wants the event body updated, keep it short and preserve the existing body format.
6. Keep this workflow inside Outlook. Do not pull in Teams or SharePoint unless the user explicitly redirects the task to those surfaces.

## Output Conventions

- Separate event facts from mailbox facts.
- Lead with what changed and what still needs action.
- Keep attendee-facing follow-ups concise and operational.

## Example Requests

- "Tell me what changed between the event and the related email thread."
- "Draft the follow-up email after this meeting using the event and the thread."
- "Use the invite plus the mail context to tell me what I still owe."
