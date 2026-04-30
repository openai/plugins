---
name: slack-outgoing-message
description: Primary skill for composing, drafting, or refining any outbound Slack content. Use this whenever the task will require using `slack_send_message`, `slack_send_message_draft`, or `slack_create_canvas`. Use `slack` to read or analyze Slack context; use this skill to produce the final outgoing message.
---

# Slack Outgoing Message

## Overview

Use this skill whenever the task involves producing final Slack text for a send, draft, scheduled message, or canvas.
If another Slack skill is used to read or summarize source context, switch to this skill before finalizing outgoing text.

## Intent Rules

- If the user explicitly asks to send, post, reply, share, or create something in Slack, perform that write action directly. Do not create a draft or ask for approval only because the message text is being generated during the turn.
- Use a draft only when the user explicitly asks for a draft, review-first workflow, or later/manual send.
- If the destination, wording, or requested action is unclear, clarify before writing.
- If the user asks for an unsupported Slack write action, say so immediately and offer the closest supported path instead of drafting something unrelated.

## Reference Notes

Read this reference **before finalizing any outgoing Slack text**:

| Task | Reference |
| --- | --- |
| Exact Slack Markdown syntax for emphasis, lists, links, code, and mentions | [../slack/references/markdown.md](../slack/references/markdown.md) |

## Formatting Rules

- Write concise Slack-ready text that follows the live tool contract plus `../slack/references/markdown.md`.
- Prefer a short opener, a few tight bullets, and a clear ask or next step.
- For drafts, use human-readable Slack profile names for people instead of raw user IDs or Slack mention syntax.
- For direct sends, scheduled messages, and canvases, use explicit Slack mention syntax only when you resolved the target successfully.
- Preserve source links, code, owners, dates, and commitments unless the user asked for edits.
- Do not invent approvals, decisions, or follow-through.

## Workflow

1. Identify the **intended destination** before drafting: channel, thread, DM, or group DM.
2. Determine the execution mode from the user's request:
   - explicit send/post/reply/share: use the direct write action
   - explicit draft/review/later-send: use the draft action
   - future delivery: use `slack_schedule_message`
   - canvas/doc request: use `slack_create_canvas`
3. Read `../slack/references/markdown.md` and use that authoring contract.

## Tool Guardrails

- Treat optional Slack tool parameters as absent-by-default.
- `thread_ts` is valid only for replies in an existing thread. For normal channel posts, DMs, and new group DMs, omit the `thread_ts` key entirely.
- `slack_create_canvas` is an immediate write, not a draft. Use it only when the user explicitly asked for a canvas, doc, or immediate Slack write of that form.
- Use `slack_schedule_message` only when the user explicitly asked for future delivery or supplied a send time.
- `slack_send_message_draft` cannot overwrite an existing attached draft, and do not claim that you verified the destination is draft-free before calling the tool.
- If `slack_send_message_draft` returns `draft_already_exists`, stop immediately. Tell the user there is already an attached draft in that destination and that Slack cannot overwrite it.
- Current Slack app support here is centered on messages, drafts, scheduled messages, canvases, and read/search flows. Do not claim support for creating channels, editing messages, deleting messages, or resolving Slack user groups when the runtime does not expose those actions.

## Destination Safety

- If the user wants to **cc, mention, or tag** someone, first check whether that person is already in the destination channel or group DM when the connector makes that practical. If you cannot verify it, do not imply the mention will notify them.
- Treat `@here`, `@channel`, `@everyone`, and similar broad notifications as **high-impact**. Do not add them unless the user explicitly asked for them.

## Mention Rules

- For `slack_send_message_draft`, resolve each referenced person's Slack profile and write their human-readable profile name in the draft text, preferring `display_name` and falling back to `real_name` or the clearest available profile name. Do not put raw Slack user IDs or `<@U123456>` syntax in draft bodies unless the user explicitly asks for raw Slack mention markup.
- For direct sends, scheduled messages, and canvases, resolve **user mentions** before writing when the message should tag a person, and use Slack mention syntax: `<@U123456>`.
- Resolve **Slack user groups** before writing only when the runtime exposes a way to do so, and use Slack mention syntax: `<!subteam^S123456>`.
- Do not rely on bare `@name` text for actual sends, scheduled messages, or canvases.
- If you cannot resolve the correct user or group, **tell the user** and compose the draft or message without implying the mention will work.
