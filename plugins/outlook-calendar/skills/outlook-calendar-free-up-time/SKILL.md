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

1. Start with the target block: today, tomorrow, this afternoon, a specific date, or a broader window.
2. Optimize for contiguous free blocks, not raw free-minute totals.
3. Identify what is fixed versus movable before proposing edits.
4. Prefer the smallest edit set that creates a meaningful uninterrupted block.
5. For shared meetings, do not treat a gap on the user's calendar as sufficient proof that a move works. Verify attendee availability or mark the suggestion as best-effort.
6. If no clean block exists, return the best partial win and the tradeoff it requires.

## Output Conventions

- Show the before-and-after effect of the proposal.
- Name the block created and the minimum meetings that would need to move.
- If suggesting multiple options, keep them short and explain the tradeoff for each.
