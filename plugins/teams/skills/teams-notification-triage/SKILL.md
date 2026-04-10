---
name: teams-notification-triage
description: Triage recent Microsoft Teams activity into a priority queue or task list for the user.
---

# Teams Notification Triage

Use this skill to produce a priority queue or task list from recent Teams activity. This is a proxy workflow over the available Teams signals, not a native notification-feed view.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Turn confirmed follow-ups into Microsoft Planner tasks | [../teams-planner-task-management/SKILL.md](../teams-planner-task-management/SKILL.md) |

## Start Here

- If the user provided a time window, use it and anchor it to explicit local dates.
- Treat this as best-effort triage over unread chats, recent threads, and recent message-level mentions.
- Do not claim access to unread channel markers or a native Teams notification feed.

## Workflow

1. Resolve the current user with `get_profile` so you can match message-level mentions to the signed-in user ID when needed.
2. If the user provided channels, chats, teams, or people, keep the triage inside that scope.
3. With no explicit scope, prioritize:
   - `list_chats(unread_only=True)` for unread chat signal
   - `list_recent_threads` for recent channel and chat activity
4. Expand only the containers needed to determine what matters:
   - unread chats first via `list_chat_messages`
   - then recent channels or chats via `list_channel_messages` or `list_chat_messages`
5. For mention checks, inspect message-history results and use `TeamsMessageResult.mentions`. Do not use Teams search results as the source of truth for mention detection.
6. Prioritize messages likely needing a reply, creating a follow-up, or changing the user's plan.
7. If some channel activity is unreadable or artifact-only, say so and keep it out of the main triage buckets.
8. If the user asks you to track tasks from triage, show the proposed task list first or route to the Planner skill; do not silently create tasks while presenting an attention queue.

## Formatting

Format the triage as:

```md
*Teams Attention Triage — YYYY-MM-DD*

*Summary:* <1–2 line overview of what most likely needs attention>

*Tasks for you*
- ...

*Worth skimming*
- ...

*Can ignore for now*
- ...

*Notes*
- <coverage limits, proxy caveats, or unread-channel limitation>
```

- Keep the triage compact; aim for 3–15 bullets total.
- Treat *Tasks for you* as the primary section whenever the goal is a personal action list.
- Make *Tasks for you* a triage bucket, not proof that a Planner task exists. Say "Planner task" only after reading or writing Planner.
- Include *Can ignore for now* only when the user explicitly asked to filter noise.
- Preserve exact chat, team, and channel names.
- Use *Notes* to explain proxy behavior, coverage gaps, or the lack of channel unread markers.
