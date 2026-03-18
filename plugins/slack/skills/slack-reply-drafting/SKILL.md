---
name: slack-reply-drafting
description: Draft Slack replies from available context. Use when the user wants help finding messages that likely need a response and preparing reply drafts.
---

# Slack Reply Drafting

Use this skill to identify messages that likely need a reply and produce Slack-ready draft responses from the available context.

## Related Skills

| Workflow | Skill |
| --- | --- |
| Refine, draft, or send the final Slack text | [../slack-messages/SKILL.md](../slack-messages/SKILL.md) |

## Start Here

- If the user provided channels, threads, DMs, people, or topics, use that scope instead of the default search.
- If no source scope was provided, default to searching:
  - unanswered direct conversations
  - direct mentions
  - threads with prior user participation and newer replies
  - threads with prior user mention and newer replies
- For time-specific requests, resolve the user's timezone with `slack_read_user_profile`.

## Support Boundaries

- **Draft by default.** Do not send unless the user explicitly asked to send.
- Do not invent facts, commitments, approvals, or decisions. If the context is not enough to answer confidently, draft a clarifying reply instead of guessing.

## Workflow

1. **Resolve the current user** with `slack_read_user_profile` so you have the user's `user_id` and can resolve the time window if necessary.
2. **Resolve the time window** if the user supplied one.
3. If the user provided an explicit scope, use the cheapest matching path:
   - specific thread: `slack_read_thread`
   - named channel: `slack_search_channels`, then `slack_read_channel`
   - named person or DM: `slack_search_users`, then `slack_search_public_and_private`
   - bounded keyword search: `slack_search_public_and_private`
4. If no scope was provided, search these default categories:
   - unanswered direct conversations: `slack_search_public_and_private` across `im,mpim`, then `slack_read_channel` to keep conversations where the latest relevant message is from someone else
   - direct mentions: `slack_search_public_and_private` with `query` set to `<@USER_ID>`
   - threads with prior user participation: `slack_search_public_and_private` with `query` set to `from:<@USER_ID> is:thread`, then `slack_read_thread` for newer replies
   - threads with prior user mention: `slack_search_public_and_private` with `query` set to `<@USER_ID> is:thread`, then `slack_read_thread` for newer replies after the mention
5. Keep only candidates where the latest relevant message is from someone else, or where newer replies appeared after the user's last reply or mention.
6. Expand only the threads or surrounding messages needed to answer accurately. Answer the question first, then add clarification or next steps when the context supports it.
7. If the context is incomplete, write the smallest useful clarifying reply instead of pretending the answer is known.
8. Create the draft with `slack_send_message_draft` in the source channel or DM, and include `thread_ts` for thread replies.

## Drafting Rules

- Use the [../slack-messages/SKILL.md](../slack-messages/SKILL.md) skill to draft outgoing Slack text.

## Formatting

Format multiple drafts as:

```md
*Reply Drafts — <scope>*

*<channel / DM / thread info>*
Draft: <link to draft>

*<channel / DM / thread info>*
Draft: <link to draft>
```

- Keep each item minimal: a short header plus the draft link.
- The header should identify the channel, DM, or thread.
- If the user asked for a single reply, return just that item.
- If no unreplied messages are found, say so directly and explain the scope checked.
