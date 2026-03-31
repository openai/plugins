---
name: outlook-email-shared-mailboxes
description: Work with delegated or shared Outlook Email mailboxes. Use when the user explicitly wants to read another mailbox, send from or on behalf of a shared mailbox, mark shared mail read or unread, move shared mail, or browse folders in a shared mailbox.
---

# Outlook Email Shared Mailboxes

Use this skill only when the user is working with a delegated or shared Outlook mailbox. These actions are separate from signed-in-user mailbox actions on purpose.

## Required Target

- Require the exact delegated/shared mailbox owner email address or UPN before reading or writing shared mail.
- Pass that identity as `mailbox_user_principal_name`.
- Do not discover, infer, or guess mailbox identities from display names alone.

## Action Routing

- Read signed-in user's mailbox: use the base Outlook Email skill, not this workflow.
- Read shared mailbox messages: `list_shared_messages`.
- Browse shared mailbox folders: `list_shared_mail_folders`.
- Fetch one shared mailbox message: `fetch_shared_message`.
- Send a new plain-text email from or on behalf of the shared mailbox: `send_email_on_behalf`.
- Mark shared mail read or unread: `mark_shared_email_read_state`.
- Move shared mail: `move_shared_email`.

## Workflow

1. Confirm the mailbox target and preserve the exact `mailbox_user_principal_name`.
2. For folder-specific work, list shared folders first and use exact folder IDs instead of guessing folder paths.
3. For message reads, keep the shared mailbox target attached to every message ID. A message ID from a shared mailbox should later be fetched or mutated with the corresponding shared action.
4. For sends, drafts, moves, and read-state changes, say which mailbox is being used before performing the write.
5. If the user shifts from a shared mailbox to their own mailbox, switch back to the signed-in-user actions.

## Safety

- Treat `send_email_on_behalf` as high impact. It sends immediately from another mailbox and supports plain text only.
- Do not use `send_email` when the user said to send from a shared mailbox.
- Do not use `move_email` or `mark_email_read_state` on message IDs obtained from shared mailbox actions.
- If a write fails because shared/delegated scopes are unavailable, say the shared-mailbox action or scope is the blocker rather than claiming the normal mailbox action cannot work.

## Example Requests

- "List unread mail in the support shared mailbox support@example.com."
- "Send this status note from ops-notices@example.com to the incident responders."
- "Move that message in the billing shared mailbox to its Escalations folder."
