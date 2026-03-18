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

1. Start from the event itself: title, body, attendees, recurrence context, location, and any obvious linked materials.
2. If the event points to related emails, docs, decks, or notes and they are cheap to follow, inspect them before writing the brief.
3. Build the brief around what the meeting appears to be for, what decisions or inputs seem likely, and what context is attached versus missing.
4. Highlight what the user should read or prepare first rather than dumping every detail.
5. Stay close to the event and its linked Microsoft context. Do broader research only if the user explicitly asks for it.

## Output Conventions

- Lead with what the meeting appears to be about.
- Call out the most relevant notes, emails, or linked docs.
- Separate confirmed context from missing context or open questions.
- End with a short `What To Do Before This Meeting` list when the evidence supports it.
