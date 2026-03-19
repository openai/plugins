---
name: teams
description: Summarize Microsoft Teams conversations, triage unread or recent activity, draft follow-ups, and manage Planner tasks through connected Teams data. Use when the user wants to review chats or channels, identify owners and next steps, prepare a safe reply or post, or turn follow-ups into Teams-native tasks.
---

# Teams

## Overview

Use this skill to route Microsoft Teams work into the right workflow: summarize channels, review recent activity, draft replies, send messages, or manage Planner follow-ups. Keep answers grounded in exact Teams context, preserve thread intent, and separate drafting from posting unless the user explicitly wants a send.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Compose, route, draft, or send Teams messages | [../teams-messages/SKILL.md](../teams-messages/SKILL.md) |
| Summarize one Teams channel or scoped conversation | [../teams-channel-summarization/SKILL.md](../teams-channel-summarization/SKILL.md) |
| Build a daily digest across selected chats or channels | [../teams-daily-digest/SKILL.md](../teams-daily-digest/SKILL.md) |
| Find messages that likely need a response and draft replies | [../teams-reply-drafting/SKILL.md](../teams-reply-drafting/SKILL.md) |
| Triage what likely needs the user's attention | [../teams-notification-triage/SKILL.md](../teams-notification-triage/SKILL.md) |
| Review, create, update, and delete Teams Planner tasks | [../teams-planner-task-management/SKILL.md](../teams-planner-task-management/SKILL.md) |

## Support Checks

- Confirm the requested Teams action is supported before collecting extra details. If the connector cannot do it, say so immediately and offer the closest supported path.
- Verify write capability before concluding a Teams action is unsupported. Distinguish between:
  - the needed tool not being surfaced in-session
  - the connector truly lacking the capability
  - the destination or Teams product rules blocking the action
- For any write request involving DMs, group chats, channels, or replies, resolve the exact destination first.

## Core Truths

- Unread state exists for chats only. The connector does not expose unread markers for specific channel messages.
- Mention metadata is reliable on chat and channel message-history reads. Do not rely on Teams search hits to detect mentions.
- Teams does not expose native persisted drafts here. "Draft" means return draft text unless the user explicitly asks to send or post.
- There is no Slack-canvas analogue in this Teams connector. If the user wants something posted in Teams, return or send message text rather than inventing a document workflow.
- Real outbound Teams mentions require structured mention inputs with exact Entra user IDs. Do not rely on plain `@name` text.
- For unbounded channel summaries, start with `list_channel_messages(top=50)`. Do not probe larger values by default because the underlying endpoint rejects oversized reads.

## DM Routing

- When the user refers to an existing DM or group chat, prefer resolving that chat instead of creating a new one.
- For a new direct chat, resolve the target user first and use `create_chat(chat_type='oneOnOne')` with exactly one recipient user ID.
- If one-on-one chat creation fails with a caller-membership or contract mismatch, use the known-good fallback path: create a two-person `group` chat containing the caller and the intended recipient, then send the message there.
- For note-to-self requests, prefer an obvious existing self-chat target if one is available. Otherwise use the supported one-member `group` chat fallback.

## Write Safety

- Preserve participant names, dates, links, files, decisions, and action items from the source conversation unless the user asks to change them.
- Treat channel-wide announcements, broad mentions, and shared-thread edits as high-impact. Call them out before posting.
- If multiple chats, channels, or similarly named meetings are in scope, identify the intended destination before drafting or posting.
- For answer-in-thread requests, draft first unless the user explicitly says to post, send, or reply now.
- Use canonical message paths for replies whenever possible. Do not treat free-form quoted text as a stable reply target.
- If outside context is needed to answer well, use the narrowest extra Teams context that materially changes the answer.
- If a write request fails after capability verification, say whether the blocker is connector availability, target resolution, or a Teams product rule such as chat membership requirements.

## Output Conventions

- Distinguish clearly between a private summary for the user and a message intended for Teams.
- Lead summaries with the latest status, then list decisions, owners, blockers, and next steps.
- Keep post-ready drafts concise, with one clear objective and a concrete ask when needed.
- When some channel activity is unreadable or artifact-only, say so explicitly instead of presenting it as confirmed human conversation.

## Example Requests

- "Summarize the latest Teams thread with design and tell me what follow-ups came out of it."
- "Check what likely needs my attention in Teams and separate unread chats from recent channel activity."
- "Draft a short Teams reply that confirms the rollout plan and asks for final QA sign-off."
- "Turn this Teams meeting follow-up list into Planner tasks."

## Light Fallback

If Teams data is missing or incomplete, say that Teams access may be unavailable, pointed at the wrong destination, or too broad to answer reliably, then ask the user to reconnect or narrow the scope.
