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
6. When a named channel was resolved to a channel ID, render that channel in the final digest as a Slack channel mention like `<#CHANNEL_ID>` instead of plain `#channel-name`, especially in **Scope**.
7. Read the full `## Formatting Rules` section below.
8. If the user asked to post or send the digest in Slack, use `../slack-outgoing-message/SKILL.md` and follow the user's explicit intent:
   - explicit send/post/share: write directly
   - explicit draft/review-first: create a draft
   - no Slack delivery request: return the digest in chat

## Formatting Rules

- For a concise Slack or chat summary, you MUST use exactly this structure unless the user explicitly requests a different format.
- If you use `../slack-outgoing-message/SKILL.md` to draft or send the final message, this output contract remains binding. The downstream skill does not relax or rename these sections.

```md
**Daily Slack Digest - YYYY-MM-DD**
**Scope**
- <clickable channel mentions for resolved channels + topics + time window>
- <coverage note or omitted-channel caveat, if any>

**Summary**
<1-2 sentence summary of volume + key signals>

**Topic: <group 1>**
- ...
- ...

**Topic: <group 2>**
- ...
- ...

**Needs attention**
- ...

**Notes**
- <gaps, absences, or caveats>
```

- Group the digest by topic or channel, whichever better matches the request.
- Use short group headers and keep each group to 1–3 bullets.
- Keep the digest compact; aim for 4–10 bullets total across all sections.
- Start each bullet with the key update, then add implication, owner, blocker, or action if relevant.
- If grouping by topic, include the channel when helpful.
- If grouping by channel, include the topic when helpful.
- For resolved channels, prefer Slack channel mentions like `<#CHANNEL_ID>` so the names are clickable. Use plain text only when you do not have a channel ID.
- Include **Needs attention** only for items requiring user action, decisions, or input.
- Include **Notes** for gaps, absences, sparse results, or caveats.
