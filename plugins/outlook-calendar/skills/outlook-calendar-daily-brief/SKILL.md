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
2. Use the Outlook Calendar connector's `list_events` action for the day window and relevant calendar. Default to the primary personal calendar unless the user names a different one.
3. Build the brief around the actual workday shape, not just a chronological list.
4. Separate real meetings from lightweight holds, travel buffers, or transparent blocks before writing the brief.
5. Distinguish true busy time from `Tentative`, `Free`, `Out of Office`, or `Working Elsewhere` blocks when the source data exposes those statuses.
6. If the day has meaningful work-location or out-of-office context, mention it near the top because Outlook users often use that information to interpret the schedule.
7. Call out overlaps, compressed transitions, overloaded stretches, and any meaningful remaining free windows.
8. When shared-calendar visibility is partial, say that clearly instead of implying the agenda is complete.
9. Return a brief that reads like a schedule understanding aid, not a raw connector dump.

## Data Source Rules

- Use the Outlook Calendar connector from this plugin, not web search and not a manually reconstructed schedule.
- Query with explicit day boundaries such as `[local_midnight, next_local_midnight)` in the user's timezone.
- Preserve titles exactly as returned by Outlook Calendar.
- If the connector only exposes busy windows for a calendar, build the brief around availability patterns and say that event-level detail was not available.

## Output Contract

Render the brief in this order:

1. `**Weekday, Month Day**`
2. Up to four short summary lines with restrained markers:
   - `📍` day marker such as office / travel / PTO when the source data supports it
   - `⚠` conflict-zone count
   - `🍽` lunch-window note when useful
   - `🟢` best free windows
3. `**Day Shape**` paragraph
4. `**Agenda**` Markdown table with columns `Time | Meeting`
5. `**What Needs Attention**` only when there are conflicts, dense handoffs, or unusual Outlook-status ambiguity
6. `**Useful Readout**` with 2-4 short bullets
7. `**Remaining Today**` only when the requested day is today and there are future events left

Keep the tone compact and practical. Do not use a fenced code block for the agenda.

## Formatting Rules

- Keep markers restrained. Use only the markers in the output contract unless the user explicitly asks for more decoration.
- Keep the agenda table to two columns only: `Time` and `Meeting`.
- Use compact agenda times and include the timezone in the section header or summary, not on every row.
- Treat all-day status markers such as PTO or OOF as context even when they are not meetings.
- When the source data includes Outlook status, mention it only when it changes the user's real availability.
- Mention work-location or building context only when it affects meeting logistics or how the day should be interpreted.
- Keep overlap explanations in `What Needs Attention`, not inline in every agenda row.
- If the day contains only tentative holds or shared-calendar busy markers, say that plainly.
- If the user is asking about `today`, emphasize what is still upcoming and what may require prep.
- If the user is asking about a future day, emphasize density, conflict zones, large open blocks, and unusual holds.

## Outlook-Specific Notes

- `Working Elsewhere` and `Free` should not be treated as the same thing as a hard busy meeting.
- `Tentative` often means the slot may still be usable, but only if the user accepts that ambiguity.
- Shared calendars may expose only free/busy signals, not full titles or notes.

## Fallback

If the Outlook Calendar connector is unavailable or returns no events unexpectedly, say that Microsoft Outlook access may be unavailable or scoped to the wrong calendar and ask the user to reconnect or clarify the intended calendar.
