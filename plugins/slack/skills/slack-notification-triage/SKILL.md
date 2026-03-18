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
7. **No explicit scope:** Run several small `slack_search_public_and_private` searches using filters such as `to:me`, `<@USER_ID>`, and `is:thread`, then expand the strongest results with `slack_read_thread` for threads or `slack_read_channel` for surrounding channel context.
8. Use `slack_read_thread` when the thread could hold more necessary context.
9. Prioritize messages that likely need a reply or could create a concrete follow-up or task for the user.

## Formatting

Format the triage as:

```md
*Slack Notification Triage — YYYY-MM-DD*

*Summary:* <1–2 line overview of what the user most likely needs to read, reply to, or do next>

*Tasks for you*
- ...

*Worth skimming*
- ...

*Can ignore for now*
- ...

*Notes*
- <gaps, caveats, or partial coverage>
```

- Keep the triage compact; aim for 3–15 bullets total across all sections.
- Treat *Tasks for you* as the primary section whenever the triage is meant to produce a personal todo list.
- Include *Can ignore for now* only when the user explicitly asked to filter tasks.
- Start each bullet with the key update, then add the action the user may need to take.
- Preserve exact channel names and mention DMs explicitly.
- Use *Notes* for coverage limits or sparse results.
