---
name: gmail
description: Summarize threads and draft replies in connected Gmail. Use when the user asks to inspect a Gmail mailbox or thread, extract decisions or follow-ups, triage urgency, or draft context-aware replies or forwards.
---

# Gmail

## Overview

Use this skill to turn noisy email threads into clear summaries, action lists, and ready-to-send drafts. Read the thread first, preserve message context, and avoid changing message state without explicit user intent.

## Preferred Deliverables

- Thread briefs that capture the latest status, decisions, open questions, and next actions.
- Reply or forward drafts that are ready to paste, review, or send.
- Inbox triage lists that group messages by urgency or follow-up state.

## Workflow

1. Read the mailbox or thread before drafting. Capture the current subject line, participants, latest message, open questions, deadlines, and attachments or links that matter.
2. Summarize before writing when the thread is long or the user request is ambiguous. Pull out decisions, blockers, and next actions.
3. Draft replies with thread continuity. Preserve subject intent, acknowledge the latest email, and keep the response aligned with the user's tone and objective.
4. If the user asks to reply but does not explicitly ask to send, default to a draft.
5. Separate analysis from action. Make it clear whether you are summarizing, drafting, proposing a send, or suggesting a mailbox operation.
6. Only send, archive, delete, or otherwise change mailbox state when the user has explicitly asked for that action.

## Write Safety

- Preserve exact recipients, subject lines, quoted facts, dates, and links from the source thread unless the user asks to change them.
- When drafting a reply, call out any assumptions, missing context, or information that still needs confirmation.
- Treat send, archive, trash, label, and move operations as explicit actions that require clear user intent.
- If a thread has multiple possible recipients or parallel conversations, identify the intended thread before drafting or acting.

## Output Conventions

- Summaries should lead with the latest status, then list decisions, open questions, and action items.
- Inbox triage should use explicit buckets such as urgent, waiting, and FYI when that helps the user scan quickly.
- Draft replies should be concise and ready to paste or send, with greeting, body, and closing when appropriate.
- If a reply depends on missing facts, present a short draft plus a list of unresolved details.
- When multiple emails are involved, reference the sender and timestamp of the message that matters most.

## Example Requests

- "Summarize the latest thread with Acme and tell me what I still owe them."
- "Draft a reply that confirms Tuesday works and asks for the final agenda."
- "Go through my unread inbox and group emails into urgent, waiting, and low priority."
- "Prepare a polite follow-up to the recruiter thread if I have not replied yet."

## Light Fallback

If thread or inbox data is missing, say that Gmail access may be unavailable or scoped to the wrong account and ask the user to reconnect or clarify which mailbox or thread should be used.
