---
name: outlook-calendar-shared-calendars
description: Safely write to delegated or shared Outlook calendars. Use when the user explicitly wants to create, update, respond to, cancel, delete, or add a small attachment to an event on a shared or delegated Outlook Calendar.
---

# Outlook Calendar Shared Calendars

Use this skill for writes on delegated or shared Outlook calendars. These write actions are separate from the signed-in user's own calendar actions on purpose.

## Required Target

- Start with `list_calendars` and identify the exact shared or delegated `calendar_id`.
- Use the shared-calendar action names only when the target is a delegated or shared calendar.
- For the signed-in user's own calendar, use the base Outlook Calendar skill and the non-shared event actions.

## Action Routing

- Create event on signed-in user's calendar: `create_event`.
- Create event on shared calendar: `create_shared_calendar_event`.
- Update signed-in user's event: `update_event`.
- Update shared calendar event: `update_shared_calendar_event`.
- Respond to signed-in user's invite: `respond_to_event`.
- Respond to shared calendar invite: `respond_to_shared_calendar_event`.
- Cancel or delete signed-in user's event: `cancel_or_delete_event`.
- Cancel or delete shared calendar event: `cancel_or_delete_shared_calendar_event`.
- Add small attachment to signed-in user's event: `add_event_attachment`.
- Add small attachment to shared calendar event: `add_shared_calendar_event_attachment`.

## Workflow

1. Resolve the target calendar with `list_calendars`; preserve the exact shared `calendar_id`.
2. Fetch or list the relevant event context before a write, and say when the shared calendar exposes only partial detail.
3. Restate the exact target calendar and event before create, update, RSVP, cancel, delete, or attachment writes.
4. Use the shared-calendar action that matches the requested write. Do not pass shared-calendar intent through the normal signed-in-user action.
5. For recurring events, preserve the base Outlook Calendar recurrence safety flow and require the intended update scope.

## Safety

- Treat shared-calendar writes as high impact because they modify another calendar surface.
- Do not assume that free/busy access implies delegated write access.
- If a shared-calendar write action is not available in-session, say that the shared/delegated calendar write capability is unavailable; do not silently retry with the signed-in-user write action.
- Preserve Teams links, rooms, attendees, body format, reminders, recurrence, and show-as state unless the user explicitly asked to change them.

## Example Requests

- "Create this event on the team shared calendar, not my personal calendar."
- "Move the event on the recruiting shared calendar to Thursday at 10 AM Pacific."
- "Cancel that event from the ops shared calendar and send this cancellation note."
