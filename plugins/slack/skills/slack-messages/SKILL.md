---
name: slack-messages
description: Compose or rewrite standalone Slack messages with correct mrkdwn, destination-aware recipient checks, and explicit mention handling.
---

# Slack Messages

## Overview

Use this skill to compose, draft, or refine Slack-ready messages and related Slack content. Apply it when the next step involves `slack_send_message`, `slack_send_message_draft`, or `slack_create_canvas`.

## Reference Notes

Read this reference **before finalizing any outgoing Slack text**:

| Task | Reference |
| --- | --- |
| Exact Slack mrkdwn syntax for emphasis, lists, links, code, and mentions | [../slack/references/mrkdwn.md](../slack/references/mrkdwn.md) |

## Workflow

1. Identify the **intended destination** before drafting: channel, thread, DM, or group DM.
2. Determine whether the user wants a **draft**, a **send-ready message**, or content for a **Slack canvas**. **Default to a draft** unless the user has approved the wording or explicitly asked to send.
3. Read `../slack/references/mrkdwn.md` and use that syntax directly instead of generic Markdown.

## Destination Safety

- If the user wants to **cc, mention, or tag** someone, first check whether that person is already in the destination channel or group DM. If they are not, **warn the user** instead of implying the mention will notify them or that they will see the message.
- Treat `@here`, `@channel`, `@everyone`, and similar broad notifications as **high-impact**. Before posting, **warn the user** that the message will notify a broad audience.

## Mention Rules

- Resolve **user mentions** before writing when the message should tag a person, and use canonical Slack mrkdwn syntax: `<@U123456>`.
- Resolve **Slack user groups** before writing when the message should tag a group, and use canonical Slack mrkdwn syntax: `<!subteam^S123456>`.
- Do not rely on bare `@name` text in outgoing Slack messages.
- If you cannot resolve the correct user or group, **tell the user** and compose the draft or message without implying the mention will work.
