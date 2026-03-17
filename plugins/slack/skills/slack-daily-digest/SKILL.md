---
name: slack-daily-digest
description: Create a daily Slack digest from selected channels or topics. Use when the user asks for a daily Slack recap or summary of today's Slack activity.
---

# Slack Daily Digest

Use this skill to produce a daily digest of today's important Slack activity from selected channels or topics.

## Start Here

- If the user did not name channels or topics, ask first before making any Slack tool calls.
- Do not guess the user's main or starred channels.

## Workflow

1. Confirm channels or topic keywords.
2. Resolve the user's timezone with `slack_read_user_profile`. For "today," use local start-of-day through now and state that window in the digest.
3. Named channels: Resolve IDs through `slack_search_channels`, then call `slack_read_channel` for today's window with `limit` at `50` per channel.
4. Named topics: Use `slack_search_public_and_private` for each topic phrase. If channels were also provided, run one search per topic and channel with `query` set to `<topic phrase> in:<#CHANNEL_ID>` so the search stays inside the selected channels. If no channels were provided, set `query` to the topic phrase. Then read the returned channels with `slack_read_channel` or parent threads with `slack_read_thread` when a result looks important.
5. Prioritize decisions, blockers, incidents, asks, ownership changes, deadline changes, and status changes.

## Formatting

Format the digest as:

```md
*Daily Slack Digest — YYYY-MM-DD*

*Scope:* <channels + topics + time window + coverage note>
*Summary:* <1–2 line overview of volume + key signals>

*Details (by <channel|topic>)*
*<Group 1>*
- ...
- ...

*<Group 2>*
- ...
- ...

*Needs attention*
- ...

*Notes*
- <gaps, absences, or caveats>
```

- Use short group headers and keep each group to 1–3 bullets.
- Keep the digest compact; aim for 4–10 bullets total across all sections.
- Start each bullet with the key update, then add implication, owner, blocker, or action if relevant.
- If grouping by topic, include the channel when helpful.
- If grouping by channel, include the topic when helpful.
- Preserve exact channel names.
- Include *Needs attention* only for items requiring user action, decisions, or input.
- Include *Notes* for gaps, absences, sparse results, or caveats.
