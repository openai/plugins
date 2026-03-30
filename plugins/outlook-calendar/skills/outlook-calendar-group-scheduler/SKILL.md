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

## Outlook Product Framing

- Treat free/busy visibility, work hours, and work location as first-class scheduling evidence when full event detail is unavailable.
- Treat attendee response state and organizer logistics as part of scheduling, not just the final event body.
- When rooms or resources are visible, treat them as Outlook-style scheduling constraints rather than a separate "room finder" workflow.

## Workflow

1. Ground the scheduling problem first: date window, duration, timezone, required attendees, optional attendees, and any hard constraints such as "this week", "afternoons only", or "avoid lunch".
2. If the scheduling window is ambiguous, assess the meeting stakes before choosing a default search window. For relatively high-stakes meetings, go back to the user and suggest tightening the timeline, for example to the next week. For lower-stakes or more casual group scheduling, default to a near-term search such as the next 1 to 3 weeks.
3. Normalize the request into explicit candidate windows before ranking anything.
4. Rank slots, do not enumerate everything. Optimize for a short list of strong options.
5. Treat `Busy` and `Out of Office` as harder constraints than `Tentative` or `Working Elsewhere` unless the user says otherwise.
6. Prefer slots that minimize conflict cost, fit within work hours, and avoid avoidable hybrid-work friction such as forcing an in-office room meeting onto remote-heavy attendees.
7. When rooms, resources, or building context are available, prefer slots that keep the meeting logistically coherent instead of treating time as the only variable.
8. If shared-calendar visibility is partial, say when a recommendation is based on free/busy signals rather than full event detail.

## Ranking Heuristics

- Favor required-attendee fit over optional-attendee fit.
- Favor slots that avoid very early or very late local times for distributed attendees.
- Favor slots that stay inside work hours and avoid consuming the only large free block in someone's day unless the meeting is clearly important.
- Favor a small number of high-confidence options over a long weak list.
- When two slots are similar, prefer the one that causes less calendar fragmentation.
- When one attendee is only `Tentative` or `Working Elsewhere`, describe that as a softer constraint instead of silently treating it as unavailable.
- When one option aligns better with attendees' work locations or room logistics, explain that advantage explicitly.

## Output Conventions

- Return 2-4 candidate slots by default.
- For each slot, say why it works and who, if anyone, would be inconvenienced.
- If there is no clean option, say what tradeoff the best slot is making.
