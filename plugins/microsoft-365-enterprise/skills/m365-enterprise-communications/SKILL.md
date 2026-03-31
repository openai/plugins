---
name: m365-enterprise-communications
description: Decide whether a follow-up belongs in Outlook or Teams and draft it correctly. Use when the user wants one Microsoft workflow to choose the right communication surface, gather the right context, and prepare the message.
---

# Microsoft 365 Enterprise Communications

Use this skill when the main decision is whether a follow-up should happen in Outlook or Teams.

## Workflow

1. Determine the correct destination surface:
   - Outlook when the follow-up is email-thread based, external, long-form, or mailbox-driven
   - Teams when the follow-up is chat, channel, or thread based and belongs in the active collaboration context
2. Read the minimum context needed from the chosen surface:
   - Outlook via `search_messages`, `list_messages`, or `fetch_message`
   - Teams via `search_teams`, `fetch_teams`, `list_chat_messages`, or `list_channel_messages`
3. If recipient or scheduling context matters, pull the supporting Outlook event or contact context before drafting.
4. Draft by default unless the user clearly asked to send or post.
5. Preserve product-specific rules instead of collapsing Outlook and Teams into one generic message model:
   - Outlook email writes are plain text
   - Teams channel and chat writes require exact destination resolution
   - Teams mentions require structured user IDs

## Output Conventions

- State which surface you chose and why.
- Keep drafts clearly separated from private reasoning.
- If the message could plausibly belong in either Outlook or Teams, present the tradeoff before sending.
