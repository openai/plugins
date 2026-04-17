---
name: gmail
description: Manage Gmail inbox triage, mailbox search, thread summaries, action extraction, reply drafting, and email forwarding through connected Gmail data. Use when the user wants to inspect a mailbox or thread, search email with Gmail query syntax, summarize messages, extract decisions and follow-ups, prepare replies or forwarded messages, or organize messages when they clearly ask for send, archive, delete, or label actions.
---

# Gmail

## Overview

Use this skill to turn noisy email threads into clear summaries, action lists, and ready-to-send drafts. Prefer Gmail-native search and read workflows, preserve message context, and avoid changing message state without explicit user intent.

## Preferred Deliverables

- Thread briefs that capture the latest status, decisions, open questions, and next actions.
- Reply or forward drafts that are ready to paste, review, or send.
- Inbox triage lists that group messages by urgency or follow-up state.

## Workflow Skills

| Workflow | Skill |
| --- | --- |
| Inbox triage, urgency ranking, and follow-up detection | [../gmail-inbox-triage/SKILL.md](../gmail-inbox-triage/SKILL.md) |

## Reference Notes

| Task | Reference |
| --- | --- |
| Search planning, refinement, pagination, and body-fetch strategy | [references/search-workflow.md](./references/search-workflow.md) |
| Label application, relabeling, and label-based cleanup | [references/label-actions.md](./references/label-actions.md) |
| Reply drafting, reply-all decisions, and tone matching | [references/reply-workflow.md](./references/reply-workflow.md) |
| Email forwarding, context notes, and intent framing | [references/forward-workflow.md](./references/forward-workflow.md) |

## Mailbox Analysis Pattern

For mailbox analysis requests such as triage, follow-up detection, topic summaries, cleanup, thread understanding, or "what matters here" questions, use this pattern:

1. Strongly prefer Gmail-native `search_emails` first. Use Gmail query syntax for most mailbox tasks because it gives the model precise control over dates, senders, unread state, attachments, subjects, and exclusions, and `search_emails` returns richer summaries than `search_email_ids` without requiring an extra hop.
2. `search_emails` returns message-level summaries, not thread-grouped results. If several messages look related or a conversation may matter, expand the specific items of interest with `read_email_thread`.
3. Use `tags` only in the connector's expected shape: `list[str]`. Do not pass a single string. Prefer uppercase Gmail system labels when filtering by built-in labels.
4. Label search is supported. Use Gmail query syntax for label-aware search, for example `label:foo`, and use `tags` for built-in/system-label filtering when that is cleaner.
5. Common system labels to use in `tags` include `INBOX`, `STARRED`, `TRASH`, `DRAFT`, `SENT`, `SPAM`, `UNREAD`, and `IMPORTANT`. For All Mail, prefer Gmail query syntax such as `in:anywhere` rather than guessing a tag value.
6. Use Gmail-native `batch_read_email` when you need the body of multiple shortlisted emails, and escalate to `read_email_thread` only when the surrounding conversation changes the answer.
7. Use `search_email_ids` only when the next tool specifically needs message IDs and the richer `search_emails` response would not help you decide what to do.
8. Summarize before writing when the request is ambiguous, and keep analysis separate from actions like send, archive, trash, or label changes unless the user explicitly asked for them. A direct command in the current request, such as "label recruiter cold emails" or "delete emails related to calendar updates," is explicit user intent once the matching messages are reasonably identified.

## Write Safety

- Preserve exact recipients, subject lines, quoted facts, dates, and links from the source thread unless the user asks to change them.
- When drafting a reply, call out any assumptions, missing context, or information that still needs confirmation.
- Treat send, archive, trash, label, and move operations as explicit actions that require clear user intent in the current request. When the user directly asks for the action and the target messages are reasonably identifiable, proceed after the needed search or inspection instead of asking for another confirmation.
- Ask a concise confirmation question before acting only when the target set is ambiguous, the match quality is low, the action would send externally with inferred content or recipients, or the user asked for analysis without asking for a mailbox change.
- If a thread has multiple possible recipients or parallel conversations, identify the intended thread before drafting or acting.
- When supporting context such as policy docs, CRM notes, or Slack history is unavailable, do not foreground that limitation unless it materially changes the recommendation. Prefer a draft grounded in the email thread itself, and mention missing internal context only as a brief confidence note when necessary.

## Output Conventions

- Summaries should lead with the latest status, then list decisions, open questions, and action items.
- Inbox triage should use explicit buckets such as urgent, waiting, and FYI when that helps the user scan quickly.
- When ranking urgency or follow-up state, state the search scope and coverage, such as "from the most recent 15 inbox messages" or "from unread inbox messages matching this query."
- When the task depends on whether the user "opened" or ignored email, treat that as an inference from Gmail read state unless the connector exposes stronger engagement data.
- Avoid absolute claims like "the only urgent email" unless the mailbox scan was comprehensive enough to support that conclusion.
- When the result comes from a narrowed search or shortlist, report that confidence and mention what was excluded.
- Draft replies should be concise and ready to paste or send, with greeting, body, and closing when appropriate.
- If a reply depends on missing facts, present a short draft plus a list of unresolved details.
- When multiple emails are involved, reference the sender and timestamp of the message that matters most.
- Avoid repetitive meta-explanations about inaccessible internal sources in normal deliverables. If the user wants provenance, summarize the evidence used; otherwise keep the output focused on the draft, summary, or next action.

## Example Requests

- "Summarize the latest thread with Acme and tell me what I still owe them."
- "Draft a reply that confirms Tuesday works and asks for the final agenda."
- "Go through my unread inbox and group emails into urgent, waiting, and low priority."
- "Prepare a polite follow-up to the recruiter thread if I have not replied yet."

## Light Fallback

If thread or inbox data is missing, say that Gmail access may be unavailable or scoped to the wrong account and ask the user to reconnect or clarify which mailbox or thread should be used.
