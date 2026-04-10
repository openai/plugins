---
name: outlook-email-task-extraction
description: Extract action items, deadlines, commitments, and owners from Outlook email threads and mailbox searches. Use when the user wants a task list from one thread, several related messages, or a mailbox slice, including who owes what and when.
---

# Outlook Email Task Extraction

## Overview

Use this skill when the user wants work pulled out of email rather than a general summary. Focus on who owns the next move, what the due date is, what is blocked, and what still needs confirmation.

## Relevant Actions

- Use `search_messages` or `list_messages` to define the message set in scope.
- Use `fetch_message` or `fetch_messages_batch` when body text is needed to resolve owners, due dates, or cross-message dependencies.
- Use `list_attachments` or `fetch_attachment` when the ask or deadline lives in an attached file rather than the email body.
- Use `set_message_categories` only if the user explicitly wants tasks or commitments tagged back into Outlook after extraction.

## Workflow

1. Define the scope clearly: one thread, one sender, one topic, unread mail, or a bounded date window.
2. Extract explicit asks, commitments, deadlines, blockers, approvals, and follow-ups from the messages in scope.
3. Separate user-owned tasks from tasks owned by other people.
4. Distinguish explicit deadlines from inferred urgency.
5. When several messages refer to the same task, merge them into one task record with the freshest status.
6. If the user wants follow-up help after extraction, keep that as a second step so the task list stays auditable.

## Output

- Use a task-oriented format with `Task`, `Owner`, `Due`, `Status`, and `Evidence` when possible.
- Quote or paraphrase the message that establishes the task owner or due date.
- Call out ambiguity explicitly when ownership or due date is implied rather than stated.
- If there are no concrete tasks, say that clearly instead of forcing a weak extraction.
