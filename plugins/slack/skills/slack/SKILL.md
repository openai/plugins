---
name: slack
description: Summarize Slack conversations and draft channel-ready posts. Use when the user asks for channel or thread summaries, unread-activity review, tone-aware replies, status updates, or Slack-native formatting.
---

# Slack

## Overview

Use this skill to turn channel and thread context into concise, post-ready Slack communication. Read the conversation first, preserve the intended audience and tone, and format messages with Slack-native mrkdwn.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Compose final outbound Slack text, drafts, sends, and canvases | [../slack-outgoing-message/SKILL.md](../slack-outgoing-message/SKILL.md) |
| Bounded channel recaps and thematic Slack summaries | [../slack-channel-summarization/SKILL.md](../slack-channel-summarization/SKILL.md) |
| Daily digests across selected channels or topics | [../slack-daily-digest/SKILL.md](../slack-daily-digest/SKILL.md) |
| Find messages that likely need a response and prepare reply drafts | [../slack-reply-drafting/SKILL.md](../slack-reply-drafting/SKILL.md) |
| Triage for what the user needs to read, reply to, or do next | [../slack-notification-triage/SKILL.md](../slack-notification-triage/SKILL.md) |

## Reference Notes

| Task | Reference |
| --- | --- |
| Slack mrkdwn formatting rules and examples | [references/mrkdwn.md](./references/mrkdwn.md) |

## Support Checks

- Confirm the requested action is supported before asking the user for more input. If Slack does not support the action, say so immediately and offer the closest supported path instead of collecting unnecessary details.
- For broad Slack analysis requests, fail fast if the connector cannot establish the needed coverage or signals reliably. Do not invent channel names, imply the user is in a channel, or present workspace-wide conclusions as authoritative. Ask for a candidate list, a narrower scope, or a question that can be answered from specific channels, threads, profiles, or search results.

## DM Routing

- When the same message is meant for multiple specific people, first look for an existing group DM with the right people and prefer that over duplicate one-to-one DMs.
- If there is no suitable group DM, do not silently fan out separate DMs. Ask whether the user wants individual DMs instead, or ask them to create the group DM if that is the better path and the connector cannot create it.

## Write Safety

- Preserve exact channel names, thread context, links, code snippets, and owners from the source conversation unless the user asks for changes.
- Treat @channel, @here, mass mentions, and customer-facing channels as high-impact. Call them out before posting.
- Keep post-ready drafts short enough to scan quickly unless the user asks for a long-form announcement.
- If there are multiple channels or threads with similar topics, identify the intended destination before drafting or posting.

## Output Conventions

- Prefer a short opener, a few tight bullets, and a clear ask or next step.
- Use mrkdwn formatting rules from `references/mrkdwn.md` for emphasis, lists, links, quotes, mentions, and code.
- Distinguish clearly between a private summary for the user and a post-ready message for Slack.
- When summarizing a thread, lead with the latest status and then list blockers, decisions, and owners.
- When drafting a reply, match the tone of the channel and avoid over-formatting.

## Example Requests

- "Summarize the incident thread in #ops and draft a calm update for leadership."
- "Turn these meeting notes into a short Slack post for the team channel."
- "Read the product launch thread and draft a reply that confirms the timeline."
- "Rewrite this long update so it lands well in Slack and still keeps the important links."

## Light Fallback

If Slack messages are missing, say that Slack access may be unavailable, the workspace may be disconnected, or the wrong channel or thread may be in scope, then ask the user to reconnect or clarify the destination.
