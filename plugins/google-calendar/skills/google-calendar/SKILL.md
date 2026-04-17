---
name: google-calendar
description: Manage scheduling and conflicts in connected Google Calendar data. Use when the user wants to inspect calendars, compare availability, review conflicts, find a meeting room, review event notes or attachments, add or adjust reminders, place temporary holds, or draft exact create, update, reschedule, or cancel changes with timezone-aware details.
---

# Google Calendar

## Overview

Use this skill to turn raw calendar data into clear scheduling decisions, reminder plans, and safe event updates. Keep answers grounded in exact dates, times, and calendar evidence.

## Preferred Deliverables

- Availability summaries with exact candidate slots, timezone, and conflicts.
- Room or resource recommendations grounded in actual calendar availability or prior meeting patterns.
- Event change proposals that show the current event and the intended update.
- Reminder change proposals with exact lead time, scope, and the meetings that qualify.
- Temporary hold proposals or final hold details with the exact slot and whether the hold is transparent.
- Final event details that are ready to create or confirm.

## Workflow

1. Read the relevant calendar state first so the request is grounded in actual events, calendars, and time windows.
2. Normalize relative time language into explicit dates, times, and timezone-aware ranges before reasoning about availability.
3. Keep reads bounded. Use explicit `time_min` and `time_max` whenever possible, avoid unbounded broad searches, and choose a small default window when the user does not state one.
4. When a bounded search returns too much, page within that same window before widening the date range. For longer historical, precedent, or preference discovery, chunk the search into smaller windows instead of one giant pull.
5. When the user leaves something ambiguous, inspect previous calendar data for a clear precedent before choosing a default. Follow established patterns when they are obvious, such as using the user's usual meeting duration if similar events are consistently 30 minutes.
6. When a participant, attendee list, manager, room, or contact detail is referenced indirectly, search a bounded relevant window and read the likely source event before asking the user for details. Use `read_event` or `search_events_all_fields` when attendee emails or full event metadata matter; the standard `search_events` summary is not enough for contact details.
7. If a found event belongs to a recurring series and the user wants a series-level change, read the master series or recurrence details before editing. Do not infer the cadence or scope from a single occurrence when `recurring_event_id` or equivalent series evidence is available.
8. Use the connector's `update_event` action for recurring edits and set `update_scope` to `this_instance`, `entire_series`, or `this_and_following` as needed. If the series is COUNT-based and the tool requires an explicit recurrence for a future-only split, preserve and restate the recurrence rule or explain that the connector cannot safely infer the split from one occurrence.
9. For room-finding requests, do not assume there is a reliable global room search. In this V1 flow, mine a reasonable window of past meetings, locations, and resource attendees to build a candidate room list, then compare availability on that concrete set.
10. For bulk reminder or classification-based edit requests, inspect a reasonable upcoming window first instead of asking for extra scoping immediately. If the prompt does not bound the horizon, use a narrow default such as the next 30 days and say so.
11. When notes, prep context, or missing details matter, inspect the event payload before proposing a change.
12. For free-slot and temporary-hold requests, if the prompt already gives the window and duration, search within that range and move directly to proposing or placing the hold. Prefer a transparent hold for temporary placeholders unless the user clearly wants a blocking focus block.
13. Surface conflicts, transparent holds, and missing meeting details before suggesting a write.
14. If the request is still ambiguous after checking for precedent or scanning a reasonable bounded window, summarize the candidate slots or exact diff before writing anything.

## Write Safety

- Preserve source event details unless the user asked to change them.
- When changing reminders, preserve title, attendees, location, meeting link, and notes unless the user asked to change them.
- For Google Calendar reminder writes, prefer the structured `reminders` object rather than free-form reminder text. Use `use_default` plus explicit `overrides` with `method` and `minutes` when the user wants custom reminder timing.
- Treat deletes and broad availability changes as high-impact actions.
- For bulk reminder or hold writes, restate the qualifying event set and time window before applying them.
- If multiple calendars or similarly named events are in play, identify the intended one explicitly before editing.
- Treat missing title, attendees, location, meeting link, or timezone as confirmation points rather than assumptions only after checking whether the missing detail is recoverable from a bounded calendar search or the relevant source event.

## Output Conventions

- Present scheduling summaries with exact weekday, date, time, and timezone.
- When sharing availability, say why a slot works or conflicts instead of listing raw times without context.
- When suggesting a room or resource, name the likely room and why it is a fit, such as prior usage, matching location, or open busy windows.
- When reporting reminder changes, name which meetings qualify, the exact lead time, and whether the scope is one event, future events, or a bounded meeting set.
- When proposing or placing a temporary hold, say whether it is transparent or busy and why that choice fits the user's request.
- When comparing options, keep the list short and explain the tradeoff for each slot.
- When the user asks for meeting notes or prep context, mention whether the answer came from the event description, an attachment, or both.

## Example Requests

- "Check my availability with Priya this Thursday afternoon and suggest the best two meeting slots."
- "Find a 1-hour slot next week where I'm free and place a temporary hold on it."
- "Find a room for the weekly team sync next Tuesday by checking rooms we've used before and which ones are free."
- "Move the design review to next week and keep the same attendees and Zoom link."
- "Add 1-hour reminders to my external-facing meetings next month and leave internal meetings unchanged."
- "Summarize my calendar for tomorrow and flag anything that overlaps or leaves no travel time."
- "Draft the final event details for a 30 minute customer sync at 2 PM Pacific on Friday."
