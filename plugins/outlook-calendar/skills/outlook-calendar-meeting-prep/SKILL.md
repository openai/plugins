---
name: outlook-calendar-meeting-prep
description: Build a practical meeting prep brief from an Outlook Calendar event and its nearby Microsoft context. Use when the user wants to prepare for an upcoming meeting, understand what to read beforehand, pull in linked notes or docs, or get a concise brief on what the meeting appears to require.
---

# Outlook Calendar Meeting Prep

Use this skill when the user wants a prep brief, not just the event details.

## Relevant Actions

- Use `fetch_event` for the focal meeting.
- Use `fetch_events_batch` or `search_events` when recurrence history, adjacent meetings, or same-day context matters.
- Use Outlook Email and Microsoft SharePoint tool surfaces when the event clearly points to related mail or docs.

## Workflow

1. Start from the event itself: title, description, attendees, response state, recurrence context, Teams details, and any obvious linked materials.
2. If the event points to connected docs, decks, threads, or notes and they are cheap to follow, inspect them before writing the brief.
3. Build the prep brief around what the meeting appears to be for, what decisions or inputs seem likely, and what context is attached versus missing.
4. Highlight what the user should read or prepare first rather than dumping every detail.
5. Stay close to the event and its linked context. Do broader research only if the user explicitly asks for it.
6. If the event comes from a shared calendar with limited detail, say what is confirmed versus what remains opaque.
7. If context gathering, note lookup, or related-event retrieval takes more than 5 minutes, recheck that the target meeting is still upcoming before updating the invite or presenting it as the next meeting.
8. If you write back into the Outlook event description, keep it short: usually one concise agenda block and, at most, one short prep block rather than a long meeting brief.
9. Preserve the event's existing body format when editing. If the event already uses plain text, keep the update plain text unless richer structure is necessary. If you are creating new formatted content with bullets or links, use HTML deliberately rather than mixing rich structure into plain text.

## Output Conventions

- Lead with what the meeting appears to be about.
- Call out the most relevant notes, emails, or linked docs.
- Separate confirmed context from missing context or open questions.
- End with a short `What To Do Before This Meeting` list when the evidence supports it.

## Outlook-Specific Focus

- Call out whether attendees have accepted, tentatively accepted, declined, or not responded when that changes the prep picture.
- Mention the presence of a Teams meeting link, room resource, or organizer note when those shape logistics.
- Treat organizer notes, response tracking, and last-minute RSVP drift as part of the meeting story, because Outlook users often rely on the invitation itself as the operational source of truth.
- Separate confirmed context from inferred context, especially when the event description is sparse.

## Output Conventions

- Lead with what this meeting appears to be about.
- Call out the most relevant notes, attachments, links, or Teams details.
- Separate confirmed context from missing context or open questions.
- End with a short "what to do before this meeting" list when there is enough evidence to support it.
- If updating the invite body, compress the brief aggressively so the description stays readable inside Outlook without scrolling through a long memo.
- If the original invite body already has formatting conventions, match them rather than switching formats midstream.
