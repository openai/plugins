---
name: outlook-email-reply-drafting
description: Draft Outlook email replies safely from connected mailbox context. Use when the user wants to reply to a thread, decide whether to reply-all, prepare a draft before sending, or turn the latest Outlook message into a polished response.
---

# Outlook Email Reply Drafting

## Overview

Use this skill when the reply itself is the task. Read enough mailbox context to understand the latest ask, then default to a draft unless the user clearly asked you to send.

## Relevant Actions

- Use `search_messages` or `list_messages` to find the right thread when the user names a topic rather than a concrete message.
- Use `fetch_message` or `fetch_messages_batch` when the latest snippet is not enough to understand tone, commitments, or the actual ask.
- Use `create_reply_draft` for reply and reply-all drafts tied to an existing message.
- Use `reply_to_email` only when the user explicitly asked to send and the content is fully grounded.
- Use `draft_email` only for net-new messages or when the task is not a direct reply to an existing message.

## Workflow

1. Identify the exact source message or thread before drafting.
2. Read the most recent message first, then enough nearby context to understand participants, status, commitments, and tone.
3. Decide whether reply-all is necessary based on shared context, not just recipient count.
4. Fetch the user's profile with `get_profile` before writing any greeting, self-reference, or signature that uses their name. Treat that as the primary source of truth, prefer other first-party profile/contact context only if needed, and ask the user before guessing.
5. Draft the reply in the thread's tone unless the user asks for a deliberate change.
6. If the draft depends on missing facts, produce the best draft you can and list the unresolved details separately.
7. If the user later approves sending, reuse the thread-grounded draft instead of recreating the reply from scratch.

## Safety

- Preserve dates, commitments, names, links, and quoted facts unless the user asks to change them.
- Do not infer the user's name from their email address or invent a likely first name. Use `get_profile` first when the reply includes the user's name or signature.
- Do not invent availability, approvals, ownership, or promises that are not already established in mailbox context.
- Treat reply-all as a deliberate choice. If the audience is ambiguous, explain the safest default.
- If the user says "send" but the content still depends on unstated choices, stop and ask the narrowest necessary confirmation question.

## Output

- Provide a ready-to-send draft with greeting, body, and closing when appropriate.
- When the draft includes the user's name or sign-off, use the real name from `get_profile`.
- If important assumptions remain, list them immediately after the draft.
- If you are recommending a reply-all decision, say why in one short line.
