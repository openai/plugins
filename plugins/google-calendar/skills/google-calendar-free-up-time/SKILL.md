---
name: google-calendar-free-up-time
description: Find ways to open up meaningful free time in a connected Google Calendar. Use when the user wants to clear up their day, make room for focus time, create a longer uninterrupted block, or see the smallest set of calendar changes that would give time back.
---

# Google Calendar Free Up Time

Use this skill when the goal is to create time, not just inspect time.

## Relevant Actions

- Use `search_events` to map the day's current fragmentation and identify movable candidates.
- Use `read_event` or `read_event_all_fields` when one candidate meeting needs a closer look before proposing a move.
- Use `create_event` when the user explicitly wants a temporary hold or focus block once the target slot is grounded.
- Use `update_event` only after the proposal is clear and set `update_scope` to `this_instance`, `entire_series`, or `this_and_following` once the correct scope of change is grounded.

## Workflow

1. Start by identifying the target: today, tomorrow, this afternoon, a specific day, or a broader window. If the user already gave a concrete window or duration, work inside it before asking follow-up questions.
2. Optimize for contiguous free blocks, not raw free-minute totals.
3. Identify which meetings are likely fixed and which are more movable before proposing changes.
4. If the user explicitly wants a temporary hold or focus block rather than a reschedule plan, choose the best qualifying free slot and create the hold once the slot is clear.
5. Look for the smallest edit set that creates a meaningful uninterrupted block.
6. Prefer solutions that reduce fragmentation across the rest of the day, not just one local gap.
7. If no clean block exists, show the best partial win and what tradeoff it requires.

## Prioritization Heuristics

- Protect hard anchors such as external meetings, major reviews, commute buffers, or lunch if it is already a stable part of the day.
- Move lower-cost meetings first, such as optional events, transparent holds, lightweight internal syncs, or self-created placeholders.
- Favor one or two coherent shifts over a chain of many tiny moves.
- Prefer creating one useful block over scattering a few small openings.

## Output Conventions

- Show the before-and-after effect of the proposal.
- Name the block of time created and the minimum meetings that would need to move.
- When creating a hold, state the exact slot and whether the hold is transparent or busy.
- If suggesting multiple options, keep them short and explain the tradeoff for each.
