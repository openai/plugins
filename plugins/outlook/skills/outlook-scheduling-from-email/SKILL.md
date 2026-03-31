---
name: outlook-scheduling-from-email
description: Turn Outlook email context into scheduling decisions. Use when the user wants to extract proposed times from an email thread, compare them against calendar availability, and prepare either an event or the right reply draft.
---

# Outlook Scheduling From Email

Use this skill when the workflow starts in email but ends in calendar reasoning.

## Workflow

1. Read the relevant thread first with `search_messages`, `list_messages`, `fetch_message`, or `fetch_messages_batch`.
2. Extract the concrete scheduling facts from the thread:
   - proposed dates and times
   - timezone cues
   - required attendees
   - whether the user is asking to reply, create an event, or both
3. Compare those proposals against calendar context with `list_events`, `search_events`, `get_schedule`, or `find_available_slots`.
4. If the user needs a response first, prepare a reply draft with `create_reply_draft` or `draft_email`.
5. If the user wants the meeting placed on the calendar and the details are explicit enough, prepare or create the event with `create_event`.
6. When the thread still leaves key scheduling facts unresolved, draft the smallest useful clarification reply instead of inventing the event details.

## Safety

- Restate exact interpreted dates, times, and timezones before any calendar write.
- Do not invent attendee availability, acceptance, or meeting ownership that the thread and calendar context do not establish.
- Keep the reply draft and the event proposal separate when the user has not clearly asked for both actions.

## Example Requests

- "Take this email thread, figure out the best meeting options, and draft the reply."
- "Use the thread plus my calendar to tell me whether Tuesday 2 PM Pacific works."
- "Turn this confirmed scheduling thread into an Outlook event."
