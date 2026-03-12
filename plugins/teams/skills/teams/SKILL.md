---
name: teams
description: Summarize Microsoft Teams chats and channels, extract action items, and draft follow-ups through connected Teams data. Use when the user wants to review a chat or channel, distill meeting discussions, identify owners and next steps, or prepare a safe reply or post without sending it by default.
---

# Teams

## Overview

Use this skill to turn Teams chats, channels, and meeting discussions into concise summaries and safe follow-ups. Read the full conversation context first, keep participant and thread intent intact, and separate drafting from posting.

## Preferred Deliverables

- Thread briefs that capture the latest status, decisions, owners, and next actions.
- Channel-ready or meeting-ready drafts that are concise and easy to post after review.
- Follow-up summaries that translate meeting discussion into clear owners, due dates, and open questions.

## Workflow

1. Read the chat, channel, or meeting thread before drafting. Capture the participants, latest replies, linked files, unresolved questions, and any explicit asks.
2. Summarize before writing when the conversation is long or the user has not yet decided what response they want.
3. Keep the draft grounded in Teams context. Preserve the intended audience, thread continuity, and any important mentions or file references.
4. If the user asks for a reply or follow-up but does not explicitly ask to send or post it, default to a draft.
5. Call out if the requested action belongs in a private chat, a channel reply, or a meeting follow-up so the destination stays clear.
6. Only post, send, or otherwise change Teams state when the user has explicitly asked for that action.

## Write Safety

- Preserve participant names, meeting details, linked files, dates, and action items from the source thread unless the user asks to change them.
- Treat channel-wide announcements, broad mentions, and edits to a shared meeting thread as high-impact actions that deserve an extra confirmation step.
- If multiple chats, channels, or similarly named meetings are in scope, identify the intended conversation before drafting.
- If a draft depends on missing facts, provide the draft plus a short list of the unresolved details.

## Output Conventions

- Lead summaries with the latest status, then list decisions, owners, blockers, and next steps.
- Keep post-ready drafts concise, with one clear objective and a concrete ask when needed.
- When summarizing meetings, group outcomes by decision, owner, and follow-up rather than replaying the conversation verbatim.
- Distinguish clearly between a private summary for the user and a message intended for Teams.
- When helpful, format follow-ups as a short list of action items with owners and due dates.

## Example Requests

- "Summarize the latest Teams thread with design and tell me what follow-ups came out of it."
- "Draft a short channel reply that confirms the rollout plan and asks for final QA sign-off."
- "Turn this meeting chat into action items with owners and dates."
- "Review the release thread in Teams and draft the follow-up I should send to the project channel."

## Light Fallback

If Teams data is missing or incomplete, say that Microsoft Teams access may be unavailable or pointed at the wrong chat or channel, then ask the user to reconnect or clarify the intended conversation.
