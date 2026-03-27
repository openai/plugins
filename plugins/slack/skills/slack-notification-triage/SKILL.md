---
name: slack-notification-triage
description: Triage recent Slack activity into a priority queue or task list for the user.
---

# Slack Notification Triage

Use this skill to produce a priority queue or task list for the user from recent Slack messages. It is for surfacing what the user likely needs to read, reply to, or do next.

## Start Here

- If the user provided a time window, use it. For requests like "today" or "this morning," resolve the user's timezone with `slack_read_user_profile`.
- Treat this as best-effort triage over recent Slack activity, not an exact unread or notification-state view.

## Workflow

1. Treat this as personal triage for the user. Focus on messages directed at the user, messages likely needing a reply, and messages that create a concrete follow-up or task for the user.
2. Resolve the current user with `slack_read_user_profile` so you have the user's Slack ID for mention-based searches.
3. If the user provided channel names, DMs, people, or topic keywords, use that scope.
4. **Named channels:** Resolve IDs through `slack_search_channels`, then call `slack_read_channel` with `limit` at `100` per channel.
5. **Named people or DMs:** Resolve people through `slack_search_users`, then use `slack_search_public_and_private` with several small searches using filters `from:<@USER_ID>`, `to:<@USER_ID>`, or `in:<@USER_ID>` to surface relevant DM or person-specific activity.
6. **Named topics:** Use `slack_search_public_and_private`, and if channels were also provided, keep the search inside those channels.
7. **No explicit scope:** Search in this order:
   - unanswered direct conversations: run `slack_search_public_and_private` over `channel_types="im"`, paging until you have a reasonable set of unique conversations, then dedupe and expand promising DMs with `slack_read_channel`
   - unanswered group DMs: repeat over `channel_types="mpim"`, again preferring unique conversations over repeated hits from one chat
   - direct mentions: `slack_search_public_and_private` with `query` set to `<@USER_ID>`
   - threads with prior user participation: `slack_search_public_and_private` with `query` set to `from:<@USER_ID> is:thread`, then `slack_read_thread`
   - threads with prior user mention: `slack_search_public_and_private` with `query` set to `<@USER_ID> is:thread`, then `slack_read_thread`
8. Use `slack_read_thread` when the thread could hold more necessary context.
9. Prioritize messages that likely need a reply or could create a concrete follow-up or task for the user. Explicit asks, review or approval requests, blockers, and bumps should rank above casual questions, FYIs, or repeated snippets from the same conversation.
10. Read the full `## Formatting Rules` section below.
11. Before sending the final answer, map the findings into the exact structure in **Formatting Rules**. Do not invent alternate section names or top-level layouts.
12. If the user also asked to draft or send follow-ups from the triage results, use `../slack-outgoing-message/SKILL.md` and align with the explicit intent:
   - explicit send/post/reply: write directly
   - explicit draft/review-first: draft
   - otherwise keep this skill analysis-only

## Formatting Rules

- For a concise Slack or chat summary, you MUST use exactly this structure unless the user explicitly requests a different format.
- If you use `../slack-outgoing-message/SKILL.md` to draft or send the final message, this output contract remains binding. The downstream skill does not relax or rename these sections.

```md
**Slack Notification Triage - YYYY-MM-DD**
**Overview**
<1-2 sentence summary of what the user most likely needs to read, reply to, or do next>

**Tasks for you**
- ...

**Worth skimming**
- ...

**Can ignore for now**
- ...

**Notes**
- <gaps, caveats, or partial coverage>
```

- Keep the triage compact; aim for 3–15 bullets total across all sections.
- Treat **Tasks for you** as the primary section whenever the triage is meant to produce a personal todo list.
- Include **Can ignore for now** only when the user explicitly asked to filter tasks.
- Start each bullet with the key update, then add the action the user may need to take.
- Preserve exact channel names and mention DMs explicitly.
- Use **Notes** for coverage limits or sparse results.
