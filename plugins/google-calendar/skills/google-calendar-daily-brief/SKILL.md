---
name: google-calendar-daily-brief
description: Build polished one-day Google Calendar briefs. Use when the user asks for today, tomorrow, or a specific date summary with an agenda, conflict flags, free windows, remaining-meeting readouts, or a calendar brief, and the Google Calendar connector is available.
---

# Google Calendar Daily Brief

## Overview

Use this skill to turn one day of Google Calendar events into a readable daily brief instead of a raw event dump. Use the Google Calendar app from this plugin for the source data, then use the bundled formatter as the default rendering path.

## Workflow

1. Resolve the date window explicitly in the user's timezone.
2. Fetch the day's events through the Google Calendar app/connector for the relevant calendar. Default to `calendar_id=primary` unless the user names a different calendar.
3. Pass the raw JSON response to `scripts/render_day_brief.py`.
4. Return the rendered Markdown as the answer. Lightly adapt the lead-in or emphasis if the user asked for a narrower scope, a more compact answer, or a specific focus.

## Relevant Actions

- Prefer `search_events` for the one-day event list that feeds the formatter.
- Use `search_events_all_fields` only if the brief needs richer event metadata than the standard event summary surface returns.

## Data Source Rules

- Use the Google Calendar app/connector from this plugin, not web search and not a manually reconstructed schedule.
- Query with explicit day boundaries such as `[local_midnight, next_local_midnight)` in the user's timezone.
- Prefer the app's event search/list call that accepts `calendar_id`, `time_min`, `time_max`, and `timezone`.
- Preserve titles exactly as returned by Google Calendar.

## Default Shape

The formatter's default shape is a good baseline:

- date header
- short top summary lines
- `Day Shape`
- `Agenda`
- optional `What Needs Attention`
- `Useful Readout`
- optional `Remaining Today`

Keep the tone compact and practical. Do not use a fenced code block for the agenda.

## Formatter

Run the formatter whenever you want the full daily brief:

```bash
python3 scripts/render_day_brief.py \
  --time-min 2026-03-11T00:00:00-07:00 \
  --time-max 2026-03-12T00:00:00-07:00 \
  --timezone America/Los_Angeles \
  --now 2026-03-11T17:02:19-07:00
```

Provide the Google Calendar JSON payload on stdin. The script accepts either:

- the raw object returned by the calendar app, with an `events` field, or
- a bare JSON array of event objects

Use `--now` when summarizing today so the script can emit `Remaining Today`. Omit it for future days if you do not need that section.

## Formatting Rules

- Keep markers restrained. Use only the formatter's default markers unless the user explicitly asks for more decoration.
- Keep the agenda table to two columns only: `Time` and `Meeting`.
- Use bare compact agenda times like `10:00-10:15` without meridiem in each row.
- Allow short inline conflict annotations in the meeting column only for the representative event in a conflict cluster.
- Keep the fuller overlap explanation in `What Needs Attention`.
- Do not wrap agenda table cells in backticks or inline code.
- Keep `Day Shape` and `Useful Readout` narrative rather than metric-heavy.
- Treat all-day transparent markers as context, not meetings.
- Base free-window and lunch-window calculations on opaque timed events.
- Preserve event ordering by start time.
