---
name: teams-reply-drafting
description: Draft Microsoft Teams replies from available context. Use when the user wants help finding messages that likely need a response and preparing reply drafts.
---

# Teams Reply Drafting

Use this skill to identify Teams messages that likely need a reply and produce draft responses grounded in the available conversation context.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Refine or send the final Teams text | [../teams-messages/SKILL.md](../teams-messages/SKILL.md) |
| Create Microsoft Planner tasks instead of replying in Teams | [../teams-planner-task-management/SKILL.md](../teams-planner-task-management/SKILL.md) |

## Start Here

- If the user provided channels, threads, chats, people, or a time window, use that scope instead of the default fallback.
- If no source scope was provided, treat this as best-effort reply drafting from available Teams signals rather than an exact "messages needing reply" detector.
- Use draft replies when the user asked for drafting or review, and send when the requested action is to post or reply now.

## Workflow

1. If the user gave explicit scope, use the cheapest matching path first:
   - specific message or thread path: `fetch`, then `reply_to_message` only if the user wants to send
   - named channel: `resolve_team`, `resolve_channel`, then `list_channel_messages`
   - named chat or DM: `resolve_chat`, then `list_chat_messages`
2. If no explicit scope was provided, start with:
   - `list_chats(unread_only=True)` for unread direct conversations and group chats
   - `list_recent_threads` for recent channel or chat activity
3. Expand only the conversations needed to answer accurately:
   - unread chats first
   - then recent messages containing direct questions or clear asks
   - then recent mentions detected from message-history reads
4. To detect recent mentions, get the caller profile and match `TeamsMessageResult.mentions` against the caller's user ID from direct message-history reads. Do not rely on Teams search hits for mention detection.
5. If the context is incomplete, write the smallest useful clarifying reply instead of guessing.
6. If a message contains a follow-up but no reply is needed, say that directly. If the user wants it tracked, route the follow-up to the Planner skill instead of drafting a performative Teams reply.

## Drafting Rules

- Answer the question first, then add clarification or next steps only when the context supports it.
- Keep in-thread replies short unless the thread clearly requires a longer answer.
- Preserve thread-specific facts, dates, links, and owners.
- If there are multiple plausible reply targets, stop and ask which conversation the user means before drafting anything send-ready.

## Formatting

Format multiple drafts as:

```md
*Teams Reply Drafts — <scope>*

*<chat / channel / thread info>*
Draft:
<draft text>

*<chat / channel / thread info>*
Draft:
<draft text>
```

- Keep each item minimal: a short header plus the draft text.
- If the user asked for a single reply, return only that item.
- If nothing likely needing a reply is found, say so directly and explain the scope checked.
