---
name: outlook-calendar-free-up-time
description: Find ways to open up meaningful free time in Outlook Calendar. Use when the user wants to clear part of their schedule, make room for focus time, create a longer uninterrupted block, or see the smallest set of calendar changes that would give time back.
---

# Outlook Calendar Free Up Time

Use this skill when the goal is to create time, not just inspect time.

## Relevant Actions

- Use `list_events` to map the current fragmentation and identify movable candidates.
- Use `fetch_event` when one candidate needs a closer read before proposing a change.
- Use `find_available_slots` to verify whether a better block exists on the user's own calendar.
- Use `get_schedule` before moving attendee-heavy meetings when cross-attendee availability matters.
- Use `update_event` only after the proposal is grounded and the intended event is unambiguous.

## Workflow

1. Start by identifying the target: today, tomorrow, this afternoon, a specific day, or a broader window.
2. Optimize for contiguous free blocks, not raw free-minute totals.
3. Identify which meetings are likely fixed and which are more movable before proposing changes.
4. Look for the smallest edit set that creates a meaningful uninterrupted block.
5. Prefer solutions that reduce fragmentation across the rest of the day, not just one local gap.
6. Treat `Tentative`, `Free`, self-created placeholders, and lightly attended internal holds as lower-cost candidates than hard external meetings, accepted commitments, or `Out of Office` blocks.
7. When work hours or work location are relevant, prefer openings that produce a useful block inside the user's actual workday.
8. If no clean block exists, show the best partial win and what tradeoff it requires.

## Prioritization Heuristics

- Protect hard anchors such as external meetings, major reviews, commute buffers, and stable lunch windows.
- Move lower-cost meetings first, such as tentative holds, lightweight internal syncs, or self-created placeholders.
- When two meetings are similarly movable, prefer moving a 1:1 over a larger group meeting because it creates less attendee thrash.
- Favor one or two coherent shifts over a chain of many tiny moves.
- Prefer creating one useful block over scattering a few small openings.
- Preserve existing Teams links and attendee lists unless the user wants to change them.
- If a meeting has weak attendee commitment, interpret that in context rather than as a blanket signal. Far-future weak commitment is normal; imminent weak commitment is a much stronger sign that the meeting may be movable or unstable.

## Output Conventions

- Show the before-and-after effect of the proposal.
- Name the block created and the minimum meetings that would need to move.
- If suggesting multiple options, keep them short and explain the tradeoff for each.
