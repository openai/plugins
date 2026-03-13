---
name: slack
description: Use whenever working with Slack. Find channels or users, read channels or threads, search messages or files, draft or send messages, schedule posts, read profiles, or create and read canvases. Also use when the user needs general Slack help, tool selection, or a clear explanation of which Slack actions are and are not supported.
---

# Slack

Use this skill for connector-wide Slack guidance. Keep it focused on support boundaries and workflow choices. For exact inputs and limits, use the specific Slack tool skill.

## Supported

- Find channels by name or description and users by name, email, or profile text.
- Read channel history, direct messages, and full thread context.
- Search public messages and files, or search private channels, DMs, and group DMs.
- Draft, send, and schedule messages to channels, DMs, and thread replies.
- Read user profiles.
- Create new canvases and read existing canvas content.

## Not Supported

- Editing or deleting messages, editing scheduled messages, adding reactions, uploading files, managing channel membership, creating channels, creating group DMs, and marking conversations read are not supported.
- Search is keyword-based. Use Slack search modifiers; semantic search is not supported.
- Search can return files, but this connector does not provide a general read or download tool for arbitrary file contents. Canvas content is the only document content with a dedicated read tool.
- Sending, scheduling, and drafting are not supported in externally shared Slack Connect channels.
- Canvases can be created and read, but not updated in place. Canvas creation is also not available on free teams.
- Unread or inbox coverage is not a general Slack capability here. Work from a specific channel, thread, or search scope instead.
- Workspace-wide audits, recommendations, or rankings that require complete Slack coverage are not reliable here. Do not claim you can list every channel the user is in, measure their reactions, comments, or overall engagement across Slack, see scroll behavior, or identify dead channels globally unless the user provides a narrowed set to inspect.

## Workflow

- Confirm the requested action is supported before asking the user for more input. If Slack does not support the action, say so immediately and offer the closest supported path instead of collecting unnecessary details.
- Default to a draft unless the user has approved the wording or explicitly asked to send.
- For broad Slack analysis requests, fail fast if the connector cannot establish the needed coverage or signals reliably. Do not invent channel names, imply the user is in a channel, or present workspace-wide conclusions as authoritative. Ask for a candidate list, a narrower scope, or a question that can be answered from specific channels, threads, profiles, or search results.
- If the user wants to cc someone on a message, make sure the destination already includes them. If the person is not in the channel or group DM, warn the user instead of implying they will see the message.
- Resolve user mentions before writing. If the message should actually tag a person, look up the canonical Slack user ID first and write the message with Slack mrkdwn mention syntax: `<@U123...>`. Only use `<!subteam^S123...>` for a Slack user group if the user already provided the exact group ID. Do not rely on bare `@name` text in outgoing Slack messages.
- When the same message is meant for multiple specific people, first look for an existing group DM with the right people and prefer that over duplicate one-to-one DMs.
- If there is no suitable group DM, do not silently fan out separate DMs. Ask whether the user wants individual DMs instead, or ask them to create the group DM if that is the better path and the connector cannot create it.
- If a handle is ambiguous, disambiguate before sending. If the user wants literal `@text` instead of a real tag, preserve it literally.
