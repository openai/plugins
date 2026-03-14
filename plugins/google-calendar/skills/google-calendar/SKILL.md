---
name: google-calendar
description: Manage Google Calendar scheduling, availability, room/resource lookup, and event details through connected Google Calendar data. Use when the user wants to inspect calendars, compare availability, find a meeting room, review event notes or attachments, or prepare clear event-change proposals with timezone-aware details.
---

# Google Calendar

## Overview

Use this skill to turn raw calendar data into clear scheduling decisions. Keep answers grounded in exact dates, times, and calendar evidence.

## Preferred Deliverables

- Availability summaries with exact candidate slots, timezone, and conflicts.
- Room or resource recommendations grounded in actual calendar availability or prior meeting patterns.
- Event change proposals that show the current event and the intended update.
- Final event details that are ready to create or confirm.

## Workflow

1. Read the relevant calendar state first so the request is grounded in actual events, calendars, and time windows.
2. Normalize relative time language into explicit dates, times, and timezone-aware ranges before reasoning about availability.
3. For room-finding requests, do not assume there is a reliable global room search. In this V1 flow, mine a reasonable window of past meetings, locations, and resource attendees to build a candidate room list, then compare availability on that concrete set.
4. When notes, prep context, or missing details matter, inspect the event payload before proposing a change.
5. Surface conflicts, transparent holds, and missing meeting details before suggesting a write.
6. When the request is ambiguous, summarize the candidate slots or exact diff before writing anything.

## Write Safety

- Preserve source event details unless the user asked to change them.
- Treat deletes and broad availability changes as high-impact actions.
- If multiple calendars or similarly named events are in play, identify the intended one explicitly before editing.
- Treat missing title, attendees, location, meeting link, or timezone as confirmation points rather than assumptions.

## Output Conventions

- Present scheduling summaries with exact weekday, date, time, and timezone.
- When sharing availability, say why a slot works or conflicts instead of listing raw times without context.
- When suggesting a room or resource, name the likely room and why it is a fit, such as prior usage, matching location, or open busy windows.
- When comparing options, keep the list short and explain the tradeoff for each slot.
- When the user asks for meeting notes or prep context, mention whether the answer came from the event description, an attachment, or both.

## Example Requests

- "Check my availability with Priya this Thursday afternoon and suggest the best two meeting slots."
- "Find a room for the weekly team sync next Tuesday by checking rooms we've used before and which ones are free."
- "Move the design review to next week and keep the same attendees and Zoom link."
- "Summarize my calendar for tomorrow and flag anything that overlaps or leaves no travel time."
- "Draft the final event details for a 30 minute customer sync at 2 PM Pacific on Friday."
