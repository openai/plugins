---
name: outlook-calendar-daily-brief
description: Build polished one-day Outlook Calendar briefs. Use when the user asks for today, tomorrow, or a specific date summary with an agenda, conflict flags, free windows, remaining-meeting readouts, or a calendar brief, and Outlook Calendar is available.
---

# Outlook Calendar Daily Brief

Use this skill to turn one day of Outlook Calendar events into a readable brief rather than a raw event dump.

## Relevant Actions

- Prefer `list_events` with explicit start and end datetimes for the day window.
- Use `fetch_event` or `fetch_events_batch` only if the brief needs fuller event details than the list surface returns.
- Use `find_available_slots` only when the user explicitly wants concrete free windows after buffers.

## Workflow

1. Resolve the day window explicitly in the user's mailbox timezone if it is known, otherwise in the user's stated timezone.
2. Read the day's events from the intended calendar. Default to the primary calendar unless the user names a shared calendar.
3. Separate real meetings from lightweight holds, travel buffers, or transparent blocks before writing the brief.
4. Call out overlaps, compressed transitions, overloaded stretches, and any meaningful remaining free windows.
5. Return a brief that reads like a schedule understanding aid, not a raw connector dump.

## Output Conventions

- Lead with a compact readout of how heavy or fragmented the day looks.
- Include `Agenda` and a short `What Needs Attention` section when conflicts or thin buffers exist.
- Use exact weekday, date, time, and timezone for every event block.
- Keep the brief compact and practical. Do not expose raw Outlook IDs or raw connector payload fields.
