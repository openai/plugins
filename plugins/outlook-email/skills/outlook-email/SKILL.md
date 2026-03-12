---
name: outlook-email
description: Triage Outlook inboxes, summarize email threads, extract action items, and draft replies or forwards through connected Outlook data. Use when the user wants to inspect a mailbox or thread, understand the latest status, identify what still needs a response, or prepare a safe draft without sending it by default.
---

# Outlook Email

## Overview

Use this skill to turn Outlook inbox and thread context into clear summaries, action lists, and ready-to-review drafts. Read the thread first, preserve recipients and message intent, and treat sending as a separate explicit step.

## Preferred Deliverables

- Thread briefs that capture the latest status, decisions, deadlines, and next actions.
- Inbox triage summaries that group messages by urgency, follow-up state, or owner.
- Draft replies or forwards that are ready to review before sending.

## Workflow

1. Read the mailbox or thread before drafting. Capture the subject, participants, latest message, action items, deadlines, and any attachments or links that matter.
2. Summarize first when the thread is long or when the user needs help deciding how to respond.
3. Draft replies with thread continuity. Acknowledge the latest message, preserve the user’s objective, and keep the response grounded in the actual thread.
4. If the user asks for a reply but does not explicitly ask to send it, default to a draft.
5. Separate mailbox analysis from action. Be explicit about whether you are summarizing, drafting, proposing a send, or suggesting triage.
6. Only send, move, archive, delete, or otherwise change Outlook mailbox state when the user has clearly asked for that action.

## Write Safety

- Preserve recipients, subject lines, dates, links, and quoted facts from the source thread unless the user asks to change them.
- Treat send, delete, move, and broad mailbox cleanup actions as explicit operations that require clear user intent.
- If multiple threads or similarly named mailboxes are in scope, identify the intended thread before drafting or acting.
- If a reply depends on missing facts, provide the draft plus a short list of what still needs confirmation.

## Output Conventions

- Lead summaries with the latest status, then list decisions, open questions, and action items.
- Keep triage buckets explicit, such as urgent, waiting, needs reply, and FYI, when that helps the user scan faster.
- Draft replies should be concise, ready to paste or send, and clearly separated from private notes.
- When multiple messages matter, reference the sender and timestamp of the message that drives the next action.
- If a draft requires follow-up details, list them immediately after the draft.

## Example Requests

- "Summarize the latest Outlook thread with the customer and tell me what I still owe them."
- "Draft a reply that confirms the plan and asks for the final approval date."
- "Go through my unread Outlook inbox and group messages into urgent, waiting, and low priority."
- "Prepare a short forward that gives leadership the current status from this email thread."

## Light Fallback

If Outlook mailbox data is missing or incomplete, say that Microsoft Outlook access may be unavailable or scoped to the wrong mailbox or thread, then ask the user to reconnect or clarify the target.
