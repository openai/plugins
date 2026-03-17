---
name: google-calendar-meeting-prep
description: Build a practical meeting prep brief from a connected Google Calendar event and its nearby context. Use when the user wants to prepare for an upcoming meeting, understand what to read beforehand, pull in linked notes or docs, or get a concise brief on what the meeting appears to require.
---

# Google Calendar Meeting Prep

Use this skill when the user wants a prep brief, not just the event details.

## Relevant Actions

- Use `read_event` or `read_event_all_fields` for the focal meeting.
- Use `search_events` when recurrence history, adjacent meetings, or same-day context matters to the prep brief.

## Workflow

1. Start from the event itself: title, description, attendees, recurrence context, attachments, and any obvious linked materials.
2. If the event points to connected docs, decks, or notes and they are cheap to follow, inspect them before writing the brief.
3. Build the prep brief around what the meeting appears to be for, what decisions or inputs seem likely, and what context is attached versus missing.
4. Highlight what the user should read or prepare first rather than dumping every detail.
5. Stay close to the event and its linked context. Do broader research only if the user explicitly asks for it.

## Output Conventions

- Lead with what this meeting appears to be about.
- Call out the most relevant attachments, notes, or linked docs.
- Separate confirmed context from missing context or open questions.
- End with a short "what to do before this meeting" list when there is enough evidence to support it.
