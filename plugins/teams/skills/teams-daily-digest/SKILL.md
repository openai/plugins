---
name: teams-daily-digest
description: Create a daily Microsoft Teams digest from selected chats, channels, or workstreams. Use when the user asks for a daily Teams recap or summary of today's Teams activity.
---

# Teams Daily Digest

Use this skill to produce a daily digest of important Teams activity from selected chats, channels, or teams.

## Start Here

- If the user did not name chats, channels, teams, or topics, ask first before making Teams tool calls.
- Do not guess the user's "main channels."
- For requests like "today" or "this morning," anchor the digest to explicit local dates in the user's timezone.

## Workflow

1. Confirm the scope: named chats, named channels, named teams, or named topics.
2. Resolve the exact containers:
   - channels: `resolve_team`, `resolve_channel`
   - existing chats: `resolve_chat`
3. Prefer direct container reads over broad search:
   - channels: `list_channel_messages`
   - chats: `list_chat_messages`
4. If the user named a team but not a channel, use `list_recent_threads` scoped to that team to discover recent channel threads, then expand only the highest-signal channels with direct reads.
5. If the user named topics but not exact containers, use `list_recent_threads` as a shortlist and expand only chats or channels whose recent activity plausibly matches the topic.
6. Prioritize decisions, blockers, asks, ownership changes, timeline shifts, and notable replies.
7. Group the digest by channel, chat, or workstream, depending on what makes the summary easiest to scan.

## Formatting

Format the digest as:

```md
*Teams Daily Digest — YYYY-MM-DD*

*Scope:* <containers + time window + coverage note>
*Summary:* <1–2 line overview of volume and key signals>

*Details*
*<group 1>*
- ...
- ...

*<group 2>*
- ...
- ...

*Needs attention*
- ...

*Notes*
- <gaps, sparse results, or caveats>
```

- Keep the digest compact; aim for 4–10 bullets total across all sections.
- Preserve exact team, channel, and chat names.
- Include *Needs attention* only for items requiring user action, decisions, or input.
- Add a coverage note when the scope is broad, partly unreadable, or based on recent-thread discovery rather than exhaustive reads.
