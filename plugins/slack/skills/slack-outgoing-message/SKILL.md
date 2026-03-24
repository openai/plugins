---
name: slack-outgoing-message
description: Primary skill for composing, drafting, or refining any outbound Slack content. Use this whenever the task will require using `slack_send_message`, `slack_send_message_draft`, or `slack_create_canvas`. Use `slack` to read or analyze Slack context; use this skill to produce the final outgoing message.
---

# Slack Outgoing Message

## Overview

Use this skill whenever the task involves producing final Slack text for a draft, send, or canvas.
If another Slack skill is used to read or summarize source context, switch to this skill before finalizing outgoing text.
This skill is not complete until you reread the full `## Formatting Rules` section immediately before any outgoing Slack tool call and verify the final text follows every rule.

## Reference Notes

Read this reference **before finalizing any outgoing Slack text**:

| Task | Reference |
| --- | --- |
| Exact Slack mrkdwn syntax for emphasis, lists, links, code, and mentions | [../slack/references/mrkdwn.md](../slack/references/mrkdwn.md) |

## Formatting Rules

- Distinguish parser breaks from visible spacing:
  - Use a true blank line (`\n\n`) after quotes and also whenever a `*Section*` label follows a numbered list, bulleted list, paragraph, or code block.
  - Use a line containing only a zero-width space (`U+200B`) when you need a visible blank line separator, since Slack collapses truly empty lines.
  - Do not use vertical tabs (`U+000B`)
- After any section label, insert a line containing only a zero-width space (`U+200B`) before the next bullet, numbered item, or paragraph.
- If a quote should end before the next section, add a true blank line after the quoted line. If you also want visible spacing before the next section label, follow that with a line containing only `\u200B` (`U+200B`).
- Whenever a new `*Section*` label follows a list item, paragraph, or code block, use this safe transition pattern exactly: prior content line, true blank line, `U+200B` line, `*Section*` label, `U+200B` line, section content.
- Prefer labels like `*Section: Foo*` or `*Foo*` instead of numbered sections.

## Workflow

1. Identify the **intended destination** before drafting: channel, thread, DM, or group DM.
2. Determine whether the user wants a **draft**, a **send-ready message**, or content for a **Slack canvas**. **Default to a draft** unless the user has approved the wording or explicitly asked to send.
3. Read `../slack/references/mrkdwn.md` and use that syntax directly instead of generic Markdown.
4. Read the full `## Formatting Rules` section above.

## Tool Guardrails

- Treat optional Slack tool parameters as absent-by-default.
- `thread_ts` is valid only for replies in an existing thread. For normal channel posts, DMs, and new group DMs, omit the `thread_ts` key entirely.
- `slack_send_message_draft` cannot overwrite an existing attached draft, and do not claim that you verified the destination is draft-free before calling the tool.
- If `slack_send_message_draft` returns `draft_already_exists`, stop immediately. Tell the user there is already an attached draft in that destination and that Slack cannot overwrite it.

## Destination Safety

- If the user wants to **cc, mention, or tag** someone, first check whether that person is already in the destination channel or group DM. If they are not, **warn the user** instead of implying the mention will notify them or that they will see the message.
- Treat `@here`, `@channel`, `@everyone`, and similar broad notifications as **high-impact**. Before posting, **warn the user** that the message will notify a broad audience.

## Mention Rules

- Resolve **user mentions** before writing when the message should tag a person, and use canonical Slack mrkdwn syntax: `<@U123456>`.
- Resolve **Slack user groups** before writing when the message should tag a group, and use canonical Slack mrkdwn syntax: `<!subteam^S123456>`.
- Do not rely on bare `@name` text in outgoing Slack messages.
- If you cannot resolve the correct user or group, **tell the user** and compose the draft or message without implying the mention will work.
