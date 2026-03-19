---
name: teams-channel-summarization
description: Summarize activity from one Microsoft Teams channel or one scoped Teams conversation and return a concise recap or post-ready follow-up.
---

# Teams Channel Summarization

Use this skill to summarize one Teams channel, using a requested time window when provided or a safe recent read otherwise, and optionally turn the result into a Teams-ready follow-up.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Draft or send the final Teams follow-up | [../teams-messages/SKILL.md](../teams-messages/SKILL.md) |

## Start Here

- If the user did not name a team or channel, ask which team and channel to review.
- If the user provided a relative window such as "today" or "this week," anchor it to explicit local dates in the user's timezone.
- If the user did not provide a window, default to a recent bounded read rather than silently claiming full-history coverage.

## Workflow

1. Resolve the team and channel with `resolve_team` and `resolve_channel`.
2. If the user gave a time window, call `list_channel_messages` for that window.
3. If the user did not give a window, start with `list_channel_messages(top=50)` and top-level messages only.
4. Expand replies only when they materially affect the summary:
   - use `list_channel_messages(... include_replies=True)` for a small bounded pass when thread outcomes matter
   - use `fetch` for exact wording or a specific message the user points to
5. Consolidate the activity into a concise summary grouped by topic, decision, blocker, or workstream.
6. If the user wants the result delivered in Teams, return a post-ready channel summary by default and send only if they explicitly ask to post it.

## Formatting

Format a concise summary as:

```md
*Teams Channel Summary — <team> / <channel>*
*Window:* <explicit date range or recent snapshot>
*Overview:* <1–2 sentence summary of the main themes and biggest updates>

*Topic: <topic 1>*
- ...
- ...

*Topic: <topic 2>*
- ...
- ...

*Notes*
- <gaps, unresolved threads, or coverage caveats>
```

- Group the summary into 2–4 topics when possible.
- Keep each topic to 1–5 bullets.
- Start each bullet with the main update. Add an owner or next step only when it is clear from the channel.
- If the user asked for a recent snapshot rather than full history, label it explicitly as a snapshot.
- If the channel contains only unreadable placeholders or artifacts, say that directly instead of presenting it as confirmed human activity.
