---
name: outlook-calendar-group-scheduler
description: Find and rank good meeting times for several people using Outlook Calendar data. Use when the user wants to schedule a meeting, compare candidate slots across attendees, find the best compromise time, or add a room/resource check after narrowing the attendee-compatible options.
---

# Outlook Calendar Group Scheduler

Use this skill when the scheduling problem is the task.

## Relevant Actions

- Use `get_schedule` for attendee and room/resource free-busy windows once you know the concrete schedule identifiers.
- Use `find_available_slots` when the problem is mostly about the user's own calendar and buffered openings.
- Use `search_events` or `list_events` when you need conflict context before ranking options.
- Use `create_event` only after the winning slot and attendee set are settled.

## Workflow

1. Ground the request first: date window, duration, timezone, required attendees, optional attendees, and hard constraints.
2. Normalize the request into explicit candidate windows before ranking anything.
3. Rank slots, do not enumerate everything.
4. Prefer slots that minimize conflict cost, are fair across timezones, and avoid splitting up the constrained attendees' only large free blocks.
5. If no perfect slot exists, return the best compromise and state exactly who is impacted.
6. If the meeting also needs a room or resource, shortlist attendee-compatible times first, then check the resource schedule against those times.

## Output Conventions

- Return 2-4 candidate slots by default.
- For each slot, say why it works and who, if anyone, would be inconvenienced.
- If there is no clean option, say what tradeoff the best slot is making.
