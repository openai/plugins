---
name: slack-channel-summarization
description: Summarize activity from one Slack channel and return a concise recap, post-ready update, or summary doc.
---

# Slack Channel Summarization

Use this skill to summarize activity from one Slack channel, using a requested time window when provided or the last 100 messages otherwise, and optionally deliver the result back into Slack.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Draft, send, or rewrite the final Slack update | [../slack-messages/SKILL.md](../slack-messages/SKILL.md) |

## Start Here

- If the user did not name a channel, ask which channel to review.
- If the user provided a window, use it. For requests like "today" or "this week," resolve the user's timezone with `slack_read_user_profile`.
- If the user did not provide a window, default to the last `100` messages in the channel.

## Workflow

1. Resolve the named channel with `slack_search_channels`.
2. Collect the initial pass with `slack_read_channel` and `limit: 100`. If the user gave a window, set `oldest` and `latest`. If not, read the latest messages.
3. Read a thread using `slack_read_thread` when the parent message looks important to the summary, for example a decision, blocker, launch, incident, or open question. Default to the last `50` replies unless the request requires more.
4. Consolidate the channel activity into a short summary grouped by topic. The summary should include recurring conversations, key decisions or follow-ups, notable updates, and important threads.
5. Match the delivery format to the request:
   - short recap or brief: reply in chat or draft/send a compact Slack message
   - summary doc: use `slack_create_canvas`
6. If the user wants the result delivered in Slack, draft by default unless they explicitly asked to send.

## Formatting

For a concise Slack or chat summary, format as:

```md
*Channel Summary — <channel>*
*Overview:* <1–2 sentence summary of the main themes and biggest updates>

*Topic: <topic 1>*
- ...
- ...

*Topic: <topic 2>*
- ...
- ...

*Notes*
- <gaps, caveats, or sparse activity>
```

- Group the summary into 2–4 topics when possible.
- Keep each topic to 1–5 bullets.
- Use the overview to explain what the channel was focused on overall.
- Start each bullet with the main update. Add an owner or next step only when it is clear from the channel.
- Within each topic, capture decisions, action items, notable updates, and thread outcomes.
- Note if a thread is still open or unresolved instead of implying it concluded.
- Omit *Notes* when there are no caveats, gaps, or sparse-activity disclaimers to add.
- For a canvas, expand each topic into a short section and use `slack_create_canvas`.
