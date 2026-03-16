---
name: outlook-calendar
description: Handle scheduling flows in Outlook Calendar. Use when the user asks for availability checks, conflict review, or draft create, update, reschedule, or cancel changes with timezone-aware event times and attendee validation.
---

# Outlook Calendar

## Overview

Use this skill to turn Outlook Calendar data into clear scheduling decisions and safe event updates. Favor exact dates, times, attendees, and timezone-aware details over vague time language.

## Preferred Deliverables

- Availability summaries with exact candidate slots, timezone, and relevant conflicts.
- Event change proposals that show the current event details and the intended update.
- Final event details that are ready to create, reschedule, or cancel after confirmation.

## Workflow

1. Read current calendar state first. Gather the relevant calendars, time window, attendees, timezone, and any existing event details before proposing changes.
2. Normalize relative time language into explicit dates, times, and timezone-aware ranges.
3. Surface conflicts before edits. Call out overlapping events, missing attendee details, or other constraints before proposing a create or update.
4. When the request is ambiguous, summarize the best options before drafting an event change.
5. Treat missing title, attendees, location, meeting link, or timezone as confirmation points rather than assumptions.
6. Only create, update, move, or cancel events when the user has clearly asked for that action or confirmed the exact event details.

## Write Safety

- Preserve event titles, attendees, start and end times, locations, meeting links, and notes from the source data unless the user requests a change.
- Treat deletes, cancellations, and broad schedule changes as high-impact actions. Restate the affected event before applying them.
- If multiple calendars or similarly named events are in play, identify the intended one explicitly before editing.
- If the request references relative dates like "tomorrow afternoon," restate the exact interpreted date, time, and timezone before drafting the change.

## Output Conventions

- Present scheduling summaries with exact weekday, date, time, and timezone.
- When sharing availability, explain why a slot works or conflicts instead of listing raw times without context.
- When proposing a new or updated event, format the response as title, attendees, start, end, timezone, location or meeting link, and purpose.
- Keep option lists short and explain the tradeoff for each candidate slot.
- When reporting conflicts, name the overlapping events and how much time is affected.

## Example Requests

- "Check my Outlook Calendar availability this Thursday afternoon and suggest the best two meeting slots."
- "Move the project review to next week and keep the same attendees and Teams link."
- "Summarize my calendar for tomorrow and flag anything that overlaps."
- "Draft the exact event details for a 30 minute sync with the vendor at 2 PM Pacific on Friday."

## Light Fallback

If Outlook Calendar data is missing or incomplete, say that Microsoft Outlook access may be unavailable or pointed at the wrong calendar, then ask the user to reconnect or clarify the intended calendar or event.
