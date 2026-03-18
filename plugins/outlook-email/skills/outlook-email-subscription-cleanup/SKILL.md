---
name: outlook-email-subscription-cleanup
description: Clean up Outlook newsletters and recurring subscription email safely. Use when the user wants to unsubscribe, separate newsletters from human mail, move recurring senders into folders, or organize low-signal subscription traffic without losing important messages.
---

# Outlook Email Subscription Cleanup

## Overview

Use this skill for newsletter and subscription cleanup. Outlook organization is folder- and category-oriented, so prefer unsubscribe inspection first, then category or folder organization when the user wants the remaining mail tamed.

## Relevant Actions

- Use `search_messages` or `list_messages` to build the sender or newsletter shortlist.
- Use `get_unsubscribe_info` before attempting an unsubscribe action.
- Use `unsubscribe_via_mailto` only when the connector exposes a `mailto:` unsubscribe target.
- Use `list_categories`, `create_category`, and `set_message_categories` when the user wants newsletter tagging instead of moving mail.
- Use `find_mail_folder`, `create_mail_folder`, and `move_email` when the user wants recurring subscription traffic separated into folders.

## Workflow

1. Build a shortlist of recurring low-signal senders or newsletter-like messages.
2. Separate true subscriptions from transactional mail, alerts, or automated messages that may still matter operationally.
3. Inspect unsubscribe metadata before claiming a safe unsubscribe path exists.
4. If unsubscribe is not supported through the connector, fall back to category or folder organization instead of pretending the cleanup is complete.
5. Keep irreversible or high-volume mailbox changes explicit in the response. Say what you plan to unsubscribe, move, or tag before doing it.
6. Prefer a small, explainable cleanup pass over a broad noisy sweep.

## Output

- Group results by `Unsubscribe`, `Keep but Organize`, and `Needs Human Review`.
- For unsubscribe candidates, say whether the path is a supported `mailto:` action or only an informational header.
- For organization actions, say which category or folder each sender should map to.
- If the cleanup scope is heuristic, state the query or mailbox slice you used.
