---
name: slack
description: Summarize Slack channels and threads, draft post-ready Slack messages, and format content in Slack mrkdwn through connected Slack data. Use when the user wants to review unread activity, distill long threads, prepare status updates, reply in the right tone, or translate notes into Slack-ready message formatting.
---

# Slack

## Overview

Use this skill to turn channel and thread context into concise, post-ready Slack communication. Read the conversation first, preserve the intended audience and tone, and format drafts with Slack-native mrkdwn instead of generic prose.

## Preferred Deliverables

- Thread briefs that capture status, blockers, decisions, and owners.
- Channel-ready updates with clean mrkdwn and an explicit ask or next step.
- Reply drafts that match the tone and urgency of the thread.

## Workflow

1. Read the channel or thread before drafting. Capture who is involved, the latest status, unresolved questions, owners, and any links or code snippets that should be preserved.
2. Summarize the thread before writing when the conversation is long or the user asks for a response strategy first.
3. Draft messages in Slack-native mrkdwn. Use concise blocks, clear lists, clean code fences, and deliberate mentions.
4. If the user asks for a reply but does not explicitly ask to post, default to a draft.
5. If the request is ambiguous, present a proposed message and explain who it is aimed at and what it is trying to accomplish.
6. Only post to a channel or DM when the user has explicitly asked for the message to be sent.

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
