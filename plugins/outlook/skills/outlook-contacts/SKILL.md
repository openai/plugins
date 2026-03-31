---
name: outlook-contacts
description: Review and manage Outlook contacts and contact folders. Use when the user wants to find the right recipient, inspect or clean up saved contacts, organize contact folders, or update contact details before an Outlook communication workflow.
---

# Outlook Contacts

Use this skill for saved-contact workflows on the unified Outlook connector.

## Start Here

- Use `list_contacts` to browse contacts and `fetch_contact` when one saved contact needs full detail.
- Use `list_contact_folders` to understand how contacts are organized before cleanup or reorganization.
- Use `create_contact`, `update_contact`, `delete_contact`, and the contact-folder actions only when the user clearly asked for those changes.

## Workflow

1. Confirm whether the job is contact lookup, contact cleanup, or contact-folder organization.
2. Use `list_contacts` or `fetch_contact` to ground the work in exact saved-contact data rather than guessing email addresses or phone numbers.
3. If the right recipient is unclear, present the candidate contacts and the fields that distinguish them.
4. For reorganization work, inspect the current contact folders first, then create, rename, or delete folders deliberately.
5. For write requests, preserve existing contact data unless the user explicitly asked to change or remove it.

## Output Conventions

- Name the exact contact or contact folder you matched.
- Distinguish saved-contact facts from inferred recipient guesses.
- For write requests, show the intended contact fields or folder change before applying broad cleanup.

## Example Requests

- "Find the right saved contact for Priya before I draft this follow-up."
- "Show me the contact folders I already use for recruiting."
- "Update this Outlook contact with the new title and phone number."
