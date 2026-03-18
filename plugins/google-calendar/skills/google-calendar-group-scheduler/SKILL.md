---
name: google-calendar-group-scheduler
description: Find and rank good meeting times for multiple people using connected Google Calendar data. Use when the user wants to schedule a group meeting, compare candidate slots across several attendees, find the best compromise time, or add a room check after narrowing the attendee-compatible options.
---

# Google Calendar Group Scheduler

Use this skill when the scheduling problem is the task.

## Relevant Actions

- Use `get_availability` for attendee and room/resource busy windows once you know the concrete calendar IDs.
- Use `search_events` when you need event context, candidate-room history, or a clearer read on what is creating conflicts.

## Workflow

1. Ground the scheduling problem first: date window, duration, timezone, required attendees, optional attendees, and any hard constraints such as "this week", "afternoons only", or "avoid lunch".
2. Normalize the request into explicit candidate windows before ranking anything.
3. Rank slots, do not enumerate everything. Optimize for a short list of strong options.
4. Prefer slots that minimize conflict cost, are reasonably fair across timezones, and avoid fragmenting the day for the most constrained attendees.
5. If no perfect slot exists, return the best compromise and state exactly who is impacted.
6. If the meeting also needs a room, first narrow to attendee-compatible slots, then check likely rooms or resources against those shortlisted times.

## Ranking Heuristics

- Favor required-attendee fit over optional-attendee fit.
- Favor slots that avoid very early or very late local times for distributed attendees.
- Favor slots that preserve lunch and avoid consuming the only large free block in someone's day unless the meeting is clearly important.
- Favor a small number of high-confidence options over a long weak list.
- When two slots are similar, prefer the one that causes less calendar fragmentation.

## Output Conventions

- Return 2-4 candidate slots by default.
- For each slot, say why it works and who, if anyone, would be inconvenienced.
- If there is no clean option, say what tradeoff the best slot is making.
