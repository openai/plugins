---
name: outlook-email-inbox-triage
description: Triage an Outlook inbox into actionable buckets such as urgent, needs reply soon, waiting, and FYI using connected Outlook data. Use when the user asks to triage the inbox, rank what needs attention, find what still needs a reply, or separate important mail from noise.
---

# Outlook Email Inbox Triage

## Overview

Use this skill for direct Outlook inbox-triage requests. Build on the core Outlook Email skill at [../outlook-email/SKILL.md](../outlook-email/SKILL.md), especially its read-first and write-safety guidance.

## Relevant Actions

- Use `list_messages` for recent or unread inbox passes where a bounded mailbox slice is enough.
- Use `search_messages` when the triage request includes lexical search terms, sender filters, attachment constraints, or date scoping.
- Use `fetch_message` or `fetch_messages_batch` only when snippets are not enough to classify urgency or reply-needed state.
- Use `mark_email_read_state`, `move_email`, or `set_message_categories` only if the user explicitly asks you to act on the triage results.

## Workflow

1. Default to the inbox and a clear timeframe unless the user asks for a broader audit.
2. Build a shortlist with `list_messages` or `search_messages` before reading full bodies.
3. Exclude obvious noise early if newsletters, calendar churn, or automated alerts dominate the first pass.
4. Expand only the messages whose urgency, ownership, or reply-needed status is unclear from the first pass.
5. Return explicit buckets such as `Urgent`, `Needs reply soon`, `Waiting`, and `FYI`.
6. If the user asks to clean up the mailbox after triage, keep the classification and the mailbox actions clearly separated.

## Bucket Heuristics

- `Urgent`: direct asks with time pressure, blockers, escalation risk, or operational consequences if ignored.
- `Needs reply soon`: direct asks without same-day urgency, active threads where the user is likely the next responder, or follow-ups that will go stale soon.
- `Waiting`: threads where the user already replied or where the current blocker belongs to someone else.
- `FYI`: announcements, newsletters, calendar noise, transactional mail, and items that do not currently require action.

## Output

- Include sender, subject, why each item is in its bucket, and the likely next action.
- State timeframe, search scope, and confidence.
- Treat reply-needed as an inference, not a guaranteed state.
- Avoid claiming the inbox is fully triaged if you only checked a narrow slice.
