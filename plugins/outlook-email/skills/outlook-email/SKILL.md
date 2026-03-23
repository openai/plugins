---
name: outlook-email
description: Triage Outlook mail, extract tasks, clean up subscriptions, and draft responses. Use when the user asks to inspect an Outlook inbox or thread, summarize open actions and deadlines, clean up newsletters, draft replies or forwards, or organize mailbox follow-up work before any send or cleanup action.
---

# Outlook Email

## Overview

Use this skill to turn Outlook inbox and thread context into clear summaries, action lists, and ready-to-review drafts. Prefer Outlook-native list and search flows to build a shortlist, expand only the messages that matter, and treat mailbox mutations as separate explicit actions.

Outbound Outlook email writes are plain-text only. When drafting, replying, scheduling, or sending, do not plan around HTML bodies, rich formatting, tracking pixels, or formatting-dependent layouts. If the user asks for richer formatting, translate it into the clearest plain-text equivalent.

## Preferred Deliverables

- Thread briefs that capture the latest status, decisions, deadlines, and next actions.
- Inbox triage summaries that group messages by urgency, follow-up state, or owner.
- Draft replies or forwards that are ready to review before sending.
- Task and commitment summaries that identify owner, due date, blocker, and likely next step.
- Subscription-cleanup plans that separate unsubscribe, archive, and mailbox-organization actions.

## Workflow Skills

| Workflow | Skill |
| --- | --- |
| Inbox triage, urgency ranking, and reply-needed detection | [../outlook-email-inbox-triage/SKILL.md](../outlook-email-inbox-triage/SKILL.md) |
| Reply drafting, reply-all decisions, and send-vs-draft handling | [../outlook-email-reply-drafting/SKILL.md](../outlook-email-reply-drafting/SKILL.md) |
| Action-item, deadline, and commitment extraction | [../outlook-email-task-extraction/SKILL.md](../outlook-email-task-extraction/SKILL.md) |
| Newsletter and subscription cleanup | [../outlook-email-subscription-cleanup/SKILL.md](../outlook-email-subscription-cleanup/SKILL.md) |

## Outlook Reading Pattern

1. Prefer `list_messages` or `search_messages` to build the first-pass shortlist. These calls already return rich enough fields for most inbox navigation and thread-selection tasks.
2. Use `fetch_message` or `fetch_messages_batch` only when the user explicitly needs fuller body content, longer context, or tighter evidence for task extraction.
3. Use `list_attachments` and `fetch_attachment` when attachment metadata or file contents change the answer.
4. Use draft-first actions for write preparation: `create_reply_draft`, `create_forward_draft`, or `draft_email`.
5. Use mailbox-organization actions only with clear user intent: `mark_email_read_state`, `move_email`, `set_message_categories`, `create_category`, `create_mail_folder`.
6. For newsletter cleanup, inspect `get_unsubscribe_info` before assuming a safe unsubscribe path. `unsubscribe_via_mailto` only covers `mailto:` targets.

## Workflow

1. Read the mailbox or thread before drafting. Capture the subject, participants, latest message, action items, deadlines, and any attachments or links that matter.
2. Summarize first when the thread is long or when the user needs help deciding how to respond.
3. Draft replies with thread continuity. Acknowledge the latest message, preserve the user’s objective, and keep the response grounded in the actual thread.
4. If the user asks for a reply but does not explicitly ask to send it, default to a draft.
5. If the user asks you to send, first check whether the reply depends on any unstated facts, preferences, scheduling choices, or bundling decisions. If it does, stop and ask a concise confirmation question or present a draft plus the exact facts that still need confirmation before sending.
6. Do not invent meeting acceptance, availability, commitments, status updates, ownership, or cross-thread summaries unless the user explicitly provided them or the thread itself establishes them.
7. If you create a draft and the user later approves sending that draft, prefer sending or updating the existing draft artifact instead of recreating the same reply from scratch.
8. Avoid orphaned drafts. If you must change send paths after drafting, reuse the draft when possible or explicitly tell the user that a stale draft remains and what you did about it.
9. Separate mailbox analysis from action. Be explicit about whether you are summarizing, drafting, proposing a send, or suggesting triage.
10. Only send, move, archive, delete, or otherwise change Outlook mailbox state when the user has clearly asked for that action.
11. For category-based triage or verification, prefer `list_messages` or mailbox-wide search/list results over `fetch_message`. Treat `fetch_message` category readback as unreliable if it returns `categories: null` after a successful category write.
12. When forwarding via the Outlook connector, pass recipients as structured email-address objects rather than raw strings. If a forward call fails schema validation, inspect the expected recipient shape before retrying.
13. Before forwarding, confirm that the source message match is unique enough for the requested description. If the user refers to "that email" or describes a message indirectly, verify there is exactly one plausible mailbox match or stop and ask.
14. Before forwarding to a named person, confirm that the recipient identity is unique enough in mailbox context. If multiple plausible addresses exist for that person, stop and ask which one to use.
15. If the forward target and source message were inferred from search rather than directly specified by message ID or exact address, say what you matched before sending.

## What Stays In The Base Skill

Keep these workflows in the base Outlook Email skill instead of splitting them further for now:

- mailbox search and thread summarization
- forwarding when it is part of a broader mailbox task
- attachment extraction that supports triage or task extraction
- automated follow-up planning after a thread is understood
- commitment tracking across several related messages
- handoffs to Outlook Calendar, SharePoint, or other Microsoft surfaces when email turns into scheduling or document work

## Write Safety

- Preserve recipients, subject lines, dates, links, and quoted facts from the source thread unless the user asks to change them.
- Treat send, delete, move, and broad mailbox cleanup actions as explicit operations that require clear user intent.
- If multiple threads or similarly named mailboxes are in scope, identify the intended thread before drafting or acting.
- If a reply depends on missing facts, provide the draft plus a short list of what still needs confirmation instead of sending.
- Treat proposed times, acceptance of invitations, ETA promises, status claims, and references to other threads as high-risk facts that require explicit confirmation when they are not already established in the mailbox context.
- When a user says "send a reply," that authorizes the act of sending but not unstated content choices. Confirm assumptions that materially change the meaning of the reply.
- Treat the existence of a saved draft as part of mailbox state. Do not silently leave behind duplicate or superseded drafts when the user believes you sent the prepared reply.
- Treat connector schema requirements as part of write safety. For forwards, prefer the documented recipient object shape up front instead of relying on a failing trial call.
- Treat plain-text-only email bodies as part of connector safety. Do not promise HTML formatting, hidden tracking content, or markup-dependent rendering for Outlook email write actions.
- Treat source-message selection and recipient identity as write-safety checks for forwards. Do not forward based on a fuzzy match when multiple plausible threads or recipients remain in scope.

## Output Conventions

- Lead summaries with the latest status, then list decisions, open questions, and action items.
- Keep triage buckets explicit, such as urgent, waiting, needs reply, and FYI, when that helps the user scan faster.
- Draft replies should be concise, plain text, ready to paste or send, and clearly separated from private notes.
- When multiple messages matter, reference the sender and timestamp of the message that drives the next action.
- If a draft requires follow-up details, list them immediately after the draft.
- Before sending, explicitly note any assumptions you checked and any missing facts you asked the user to confirm.
- If you are sending a previously created draft, say so explicitly. If you are not sending that draft, explain why and what happened to it.
- Before forwarding an inferred message, state the matched source thread and matched recipient in one short line so the user can see what will be sent where.

## Example Requests

- "Summarize the latest Outlook thread with the customer and tell me what I still owe them."
- "Draft a reply that confirms the plan and asks for the final approval date."
- "Go through my unread Outlook inbox and group messages into urgent, waiting, and low priority."
- "Prepare a short forward that gives leadership the current status from this email thread."
- "Before you send anything, tell me what assumptions need my confirmation."
- "I drafted that earlier; now send the draft I approved."

## Light Fallback

If Outlook mailbox data is missing or incomplete, say that Microsoft Outlook access may be unavailable or scoped to the wrong mailbox or thread, then ask the user to reconnect or clarify the target.

If category writes succeed but direct message fetches return `categories: null`, say that the Outlook connector appears to have a category readback inconsistency. Verify categories from `list_messages` or broader mailbox scans instead of single-message fetches, and note the limitation clearly to the user.
