---
name: google-calendar
description: Manage scheduling and conflicts in connected Google Calendar. Use when the user asks to inspect calendars, compare availability, review conflicts, or draft exact create, update, reschedule, or cancel changes with timezone-aware ranges and attendees.
---

# Google Calendar

## Overview

Use this skill to turn raw calendar data into clear scheduling decisions and safe event updates. Favor exact dates, times, and attendee details over ambiguous natural-language plans.

## Preferred Deliverables

- Availability summaries with exact candidate slots, timezone, and conflicts.
- Event change proposals that show the current event and the intended update.
- Final event details that are ready to create or confirm.

## Workflow

1. Read current calendar state first. Gather the relevant calendars, time window, attendees, timezone, and any existing event IDs before proposing changes.
2. Normalize all time language. Convert phrases like "tomorrow morning" or "next Tuesday" into explicit dates, times, and timezone-aware ranges.
3. Surface conflicts before edits. Call out overlapping events, travel gaps, double bookings, and missing meeting details before suggesting a create or update.
4. When the request is ambiguous, summarize the scheduling options before writing anything. Present candidate slots or the exact event diff you plan to apply.
5. Treat missing title, attendees, location, meeting link, or timezone as confirmation points rather than assumptions.
6. Only create, update, or delete events when the user has clearly asked for that action or confirmed the exact details.

## Write Safety

- Preserve exact event titles, attendees, start and end times, locations, meeting links, and notes from the source data unless the user requests a change.
- Confirm the final timezone, attendee list, location or video link, and event purpose before creating or rescheduling an event.
- Treat deletes and broad availability changes as high-impact actions. Restate the affected event before applying them.
- If multiple calendars or similarly named events are in play, identify the intended one explicitly before editing.

## Output Conventions

- Present scheduling summaries with exact weekday, date, time, and timezone.
- When sharing availability, say why a slot works or conflicts instead of listing raw times without context.
- When proposing a new or updated event, format the response as title, attendees, start, end, timezone, location or meeting link, and purpose.
- When comparing options, keep the list short and explain the tradeoff for each slot.
- When reporting conflicts, state which events overlap and how much time is affected.

## Example Requests

- "Check my availability with Priya this Thursday afternoon and suggest the best two meeting slots."
- "Move the design review to next week and keep the same attendees and Zoom link."
- "Summarize my calendar for tomorrow and flag anything that overlaps or leaves no travel time."
- "Draft the final event details for a 30 minute customer sync at 2 PM Pacific on Friday."

## Light Fallback

If calendar data is missing or the connector does not return the expected events, say that Google Calendar access may be unavailable or pointed at the wrong calendar and ask the user to reconnect or clarify which calendar should be used.
