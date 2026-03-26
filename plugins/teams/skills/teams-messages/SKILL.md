---
name: teams-messages
description: Compose, route, draft, or send Microsoft Teams messages with exact destination resolution, real user mentions, and Teams-native DM or channel routing.
---

# Teams Messages

## Overview

Use this skill to compose, rewrite, route, or send Teams messages. Apply it when the next step involves posting to a chat, replying in a thread, creating a new chat, starting a channel thread, or writing message text that could be sent later.

## Workflow

1. Identify the intended destination first: existing chat, new DM, new group chat, channel post, or thread reply.
2. Determine from the request whether the user wants draft text or an actual send, and use the matching path.
3. Resolve exact IDs before writing:
   - teams or channels: `resolve_team`, `resolve_channel`
   - existing chats: `resolve_chat`
   - people for new chats or mentions: `resolve_user`
4. Use `validate_write_target` when the destination is described in natural language and it is unclear whether the user means an existing target or a create-style action.
5. Route to the correct write action:
   - existing chat: `send_chat_message`
   - new DM or group chat: `create_chat`, then `send_chat_message`
   - new channel thread: `send_channel_message`
   - reply in an existing chat or channel thread: `reply_to_message` or `reply_to_channel_message`
   - new channel: `create_channel`

## Mention Rules

- Resolve people before writing when the message should tag someone.
- Use structured Teams mention inputs with exact Entra user IDs plus display names.
- Do not rely on plain `@name` text to create a real Teams mention.
- If the target user cannot be resolved confidently, say so and return draft text without implying the mention will work.

## Routing Rules

- For an existing direct conversation, prefer the existing two-person chat even if Teams labels it as `group` instead of `oneOnOne`.
- For a new direct chat, call `create_chat(chat_type='oneOnOne')` with exactly one resolved recipient user ID.
- If one-on-one creation fails with a caller-membership mismatch, fetch the caller profile and fall back to a two-person `group` chat containing the caller and the intended recipient.
- For note-to-self requests, prefer an obvious existing self-chat target. If none is exposed, create a one-member `group` chat containing only the caller and send the note there.
- For channel replies, prefer replying by canonical message path instead of inferring the target from quoted text alone.

## Support Boundaries

- Teams drafts here are returned text only. There is no native persisted draft object.
- Do not claim support for Teams tags, reactions, file uploads, message edits, message deletes, or Slack-style canvases.
- Do not imply broad channel-notification behavior beyond what a normal Teams post or structured mention can do.

## Output Conventions

- For drafts, return only the message text unless the user asked for explanation.
- For multiple routing candidates, present the smallest useful disambiguation rather than guessing.
- When a send is blocked, say whether the blocker is destination ambiguity, missing user resolution, or a Teams product rule.
