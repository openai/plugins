---
name: google-calendar-free-up-time
description: Find ways to open up meaningful free time in a connected Google Calendar. Use when the user wants to clear up their day, make room for focus time, create a longer uninterrupted block, or see the smallest set of calendar changes that would give time back.
---

# Google Calendar Free Up Time

Use this skill when the goal is to create time, not just inspect time.

## Relevant Actions

- Use `search_events` to map the day's current fragmentation and identify movable candidates.
- Use `read_event` or `read_event_all_fields` when one candidate meeting needs a closer look before proposing a move.
- Use `update_event`, `update_event_series`, or `update_event_following` only after the proposal is clear and the correct scope of change is grounded.

## Workflow

1. Start by identifying the target: today, tomorrow, this afternoon, a specific day, or a broader window.
2. Optimize for contiguous free blocks, not raw free-minute totals.
3. Identify which meetings are likely fixed and which are more movable before proposing changes.
4. Look for the smallest edit set that creates a meaningful uninterrupted block.
5. Prefer solutions that reduce fragmentation across the rest of the day, not just one local gap.
6. If no clean block exists, show the best partial win and what tradeoff it requires.

## Prioritization Heuristics

- Protect hard anchors such as external meetings, major reviews, commute buffers, or lunch if it is already a stable part of the day.
- Move lower-cost meetings first, such as optional events, transparent holds, lightweight internal syncs, or self-created placeholders.
- Favor one or two coherent shifts over a chain of many tiny moves.
- Prefer creating one useful block over scattering a few small openings.

## Output Conventions

- Show the before-and-after effect of the proposal.
- Name the block of time created and the minimum meetings that would need to move.
- If suggesting multiple options, keep them short and explain the tradeoff for each.
