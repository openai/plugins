---
name: outlook-calendar
description: Handle Outlook Calendar workflows. Use when the user asks for schedule understanding, availability checks, meeting scheduling, intelligent rescheduling, meeting prep, reminder updates, RSVP responses, recurring maintenance, travel coordination, deadline planning, or safe create, update, reschedule, or cancel changes with timezone-aware event times and attendee validation.
---

# Outlook Calendar

## Overview

Use this skill to turn raw Outlook Calendar data into clear scheduling decisions and safe event updates. Favor exact dates, times, attendee details, and calendar evidence over ambiguous natural-language plans.

If recurrence scope or cadence matters, consult `resources/recurring-meetings.md` before proposing a recurring change.
If a request depends on flights, commute blocks, airport timing, or in-person travel logistics, consult `resources/travel-coordination.md` before proposing a change.
If a request depends on prep alerts, meeting reminder timing, or deciding which meetings deserve reminders, consult `resources/reminder-planning.md` before proposing a change.
If a request depends on proposing candidate times, checking when the user is free, or placing a temporary hold, consult `resources/availability-response.md` before proposing a change.

## Specialized Skills

- For one-day schedule understanding and agenda readouts, prefer [outlook-calendar-daily-brief](../outlook-calendar-daily-brief/SKILL.md).
- For creating a meaningful focus block through intelligent moves, prefer [outlook-calendar-free-up-time](../outlook-calendar-free-up-time/SKILL.md).
- For ranking the best group meeting options, prefer [outlook-calendar-group-scheduler](../outlook-calendar-group-scheduler/SKILL.md).
- For meeting prep briefs grounded in the event and nearby Microsoft context, prefer [outlook-calendar-meeting-prep](../outlook-calendar-meeting-prep/SKILL.md).
- Keep reminder planning, RSVP replies, recurring-series maintenance, travel-aware scheduling, and deadline planning in this base Outlook skill.

Use this base skill when the request spans multiple Outlook calendar workflows or when no more focused Outlook calendar skill is a better fit.

## Specialized Skills

- For one-day schedule understanding and agenda readouts, prefer [outlook-calendar-daily-brief](../outlook-calendar-daily-brief/SKILL.md).
- For creating a meaningful focus block through intelligent moves, prefer [outlook-calendar-free-up-time](../outlook-calendar-free-up-time/SKILL.md).
- For ranking the best group meeting options, prefer [outlook-calendar-group-scheduler](../outlook-calendar-group-scheduler/SKILL.md).
- For meeting prep briefs grounded in the event and nearby Microsoft context, prefer [outlook-calendar-meeting-prep](../outlook-calendar-meeting-prep/SKILL.md).
- Keep reminder planning, RSVP replies, recurring-series maintenance, travel-aware scheduling, and deadline planning in this base Outlook skill.

## Preferred Deliverables

- Availability summaries with exact candidate slots, timezone, and conflicts.
- Event change proposals that show the current event and the intended update.
- Shared-calendar summaries that explain when Outlook is showing free/busy only versus full event detail.
- Meeting-status explanations that decode Outlook concepts such as `Busy`, `Tentative`, `Free`, `Out of Office`, and `Working Elsewhere`.
- Meeting-readiness summaries that incorporate attendee response state, organizer intent, and whether a Teams link, room, or work-location detail already exists.
- Final event details that are ready to create, reschedule, or cancel directly when the request is clear.
- Meeting-note drafts that are phrased as shared, meeting-ready agenda or prep bullets rather than assistant-facing analysis.
- Reminder or deadline plans that make clear whether the outcome is an Outlook event reminder, a calendar hold, an invite response, or a separate automation.

## Workflow

### Grounding

1. Read mailbox profile context first when available so the request is grounded in the signed-in identity, locale, timezone, and default calendar assumptions.
2. Resolve calendar scope before reasoning. If multiple calendars are available, identify the intended one explicitly and prefer the default personal calendar unless the user names a shared, delegated, team, or resource calendar.
3. Read current calendar state first. Gather the relevant events, time window, attendee responses, and any existing event IDs before proposing changes.
4. Normalize all time language. Convert phrases like `tomorrow morning` or `next Tuesday` into explicit dates, times, and timezone-aware ranges.

### Scheduling Reasoning

5. Surface conflicts before edits. Call out overlapping events, travel gaps, double bookings, overload, and missing meeting details before suggesting a create or update.
6. Start from Outlook scheduling surfaces, not generic calendar abstractions. Account for attendee response state, organizer vs attendee role, shared-calendar visibility, work hours, work location, and room or resource context when available.
7. When the request depends on workday norms, prefer Outlook-native cues such as work hours, location plans, and partial free/busy visibility over generic assumptions about what counts as open work time.
8. Treat recurring meetings carefully. Determine whether the user means one occurrence, future instances, or the whole series, and if the scope is not explicit or not verifiable from the tool output, stop and confirm before editing.
9. Treat prompts about past meetings as retrospective by default. Analyze what happened and propose future scheduling changes unless the user explicitly asks to edit or annotate past events.

### Confirmation and Writes

12. When the request is ambiguous, summarize the scheduling options or the exact event diff before writing anything.
13. Treat missing title, attendees, location, Teams link, or timezone as confirmation points rather than assumptions.
14. For reschedules where the user did not specify the destination time, propose one to three exact replacement slots and get confirmation on the chosen slot before moving the event.
15. Check attendee availability before rescheduling when the connector can do so. If recipient availability cannot be verified, say that explicitly and treat any move as best-effort rather than silently assuming the slot works.
16. When notes, Teams links, rooms, or missing details matter, inspect the event payload before proposing a change and say when the source data appears partial.
17. For meeting-prep or invite-note requests, collect the relevant source material first, then apply a short, grounded write directly unless the request is still ambiguous or under-specified.
18. Before any create or reschedule write, restate the final interpreted weekday, date, local clock time, and timezone for the event. If the task spans multiple cities or time zones, restate each relevant timestamp separately.
19. Only create, update, move, or cancel events when the user has clearly asked for that action.

## Read Path

- Use `list_events` as the default tool for bounded calendar reads when the user is asking about a specific day, week, or date window.
- Prefer an explicit time window with both `start_datetime` and `end_datetime` instead of an unbounded fetch whenever the user intent is tied to a concrete range such as today, tomorrow, next week, or the next 3 days.
- Normalize relative ranges into exact ISO-8601 timestamps with an explicit UTC offset before calling `list_events`.
- Use the default event shape for ordinary schedule review. Only narrow fields if the task truly needs a smaller payload and the connector contract for that field set is known to be safe.
- Use `search_events` when the user is trying to find a meeting by phrase, attendee, or event title rather than asking for a simple time-window read.
- Use `fetch_event` after discovery when one concrete event needs deeper inspection before editing.
- If multiple information surfaces are available for meeting prep, prefer this retrieval order unless the user names a specific source: current event body, prior related event bodies, Outlook Email, SharePoint or OneDrive docs, then lower-signal notes sources.
- For document retrieval across Microsoft surfaces, use the actual connector or tool surfaces directly:
  - Outlook mail context: use the Outlook Email app tools.
  - SharePoint or OneDrive docs: use the Microsoft SharePoint app tools such as `search`, `list_recent_documents`, and `fetch`.
  - Do not use generic MCP resource discovery such as `list_mcp_resources` to discover SharePoint content for this workflow.

## Outlook-Specific Checks

- Distinguish true busy time from softer constraints such as `Tentative`, `Free`, `Out of Office`, or `Working Elsewhere`.
- If the source data includes attendee response state, organizer role, Teams details, room booking, or work-location context, preserve those details unless the user asked to change them.
- Shared calendars may expose only free/busy signals rather than full event details. Say that directly instead of implying the view is complete.
- If a slot is free only because another item is marked `Free` or `Working Elsewhere`, describe that nuance.
- If a meeting is online, preserve the existing Teams or online-meeting setup unless the user asks to change it.

## Write Safety

- Preserve exact event titles, attendees, start and end times, locations, Teams or online-meeting details, reminders, and notes from the source data unless the user requests a change.
- Preserve the original invite body format when editing. If the existing event body is plain text, keep the update plain text unless the user explicitly wants richer formatting. If the existing body is HTML, preserve HTML structure instead of flattening it into text.
- Keep Outlook event descriptions brief by default. Unless the user explicitly asks for a detailed write-up, limit description updates to at most one or two short blocks or paragraphs of operationally useful content.
- When creating invite content from scratch, prefer plain text for short linear notes and use HTML only when the content needs real structure such as bullets, links, or clearly separated sections.
- Do not write attendee-facing invite notes that include assistant provenance or meta commentary.
- When source material is incomplete or unverified, omit the uncertain item, label it as a question for the meeting, or present a draft only when unresolved details still block a safe write.
- Treat deletes and broad availability changes as high-impact actions. Restate the affected event or calendar before applying them.
- If multiple calendars or similarly named events are in play, identify the intended one explicitly before editing.
- For cross-timezone requests such as travel, flights, or events tied to a different city, interpret each stated local time in the timezone of the city where that timestamp occurs before converting it into the Outlook event payload.
- Treat Outlook timezone names as a required formatting step. Convert from user-facing timezone references such as cities, offsets, abbreviations, or IANA names into the Outlook-compatible timezone expected by the connector before writing.
- If a cross-timezone request leaves any timestamp interpretation ambiguous, stop and ask rather than silently choosing one timezone basis.

## Product Terminology

- Translate Outlook-native terms into plain language when they matter to the task, and briefly note when a term may be ambiguous across products.
- In Outlook Calendar, `reminder` normally means the built-in pre-meeting or pre-event alert on the calendar event itself, not a separate task or Apple Reminders item.
- If the user says `reminder` while clearly working inside Outlook Calendar, default to the Outlook event alert meaning, but say so briefly when the distinction could matter.
- If the phrasing could reasonably mean either an Outlook event alert or a separate task-style reminder, acknowledge the ambiguity and clarify which meaning you are using before writing.
- Treat `event body`, `description`, `invite notes`, and `meeting notes in the event` as closely related Outlook concepts, but preserve the actual event body rather than inventing a separate notes surface.
- Treat `Teams link`, `online meeting`, and `join info` as logistics attached to the event, and preserve them unless the user explicitly wants them changed.
- Treat `tentative`, `busy`, `free`, `out of office`, and `working elsewhere` as Outlook availability states, not casual prose, and explain them in user language when they affect the recommendation.

## Output Conventions

- Present scheduling summaries with exact weekday, date, time, and timezone.
- When a task spans multiple time zones, label every timestamp with its local timezone rather than collapsing them into a single timezone summary.
- When sharing availability, explain why a slot works or conflicts instead of listing raw times without context.
- When Outlook status matters, translate it into user language, such as tentative hold, true busy, out of office, working elsewhere, or visible only as shared-calendar busy time.
- When attendee responses matter, name them directly instead of flattening everything into available or unavailable.
- When proposing a new or updated event, format the response as title, attendees, start, end, timezone, location or Teams link, status if relevant, and purpose.
- Keep option lists short and explain the tradeoff for each candidate slot.
- When reporting conflicts, name the overlapping events and how much time is affected.
- When a workflow turns into a reminder, RSVP, recurring-series, or travel-buffer task, say explicitly which Outlook action or follow-up path is being used rather than presenting it as a generic edit.
- When comparing options, keep the list short and explain the tradeoff for each slot.
- When the source data is incomplete, say whether the limitation seems to come from shared-calendar permissions or missing meeting metadata.
- For retrospective schedule prompts, separate `What happened` from `What to change next time` so the user gets analysis even when no safe write should occur.
- For invite-note drafts, prefer a compact structure such as `Agenda`, `Open items`, `Decisions needed`, or `Next steps`.
- Prefer short Outlook-style descriptions over memo-like notes. The default target is one concise agenda block plus, at most, one short prep block.

## Example Requests

- "Check my Outlook Calendar availability this Thursday afternoon and suggest the best two meeting slots."
- "Move the project review to next week and keep the same attendees and Teams link."
- "Summarize my calendar for tomorrow, including which holds are only tentative."
- "Go through yesterday's meetings and tell me how I should schedule similar meetings next time to reduce context switching."
- "Draft the exact event details for a 30 minute sync with the vendor at 2 PM Pacific on Friday."
- "Help me decide whether to accept this invite, decline it, or propose a better time."
- "Clean up this recurring staff meeting without breaking the whole series."
- "Add the right reminder coverage for my review next week and the deadline after it."

## Light Fallback

If Outlook Calendar data is missing or the connector does not return the expected events, say that Microsoft Outlook access may be unavailable or pointed at the wrong calendar and ask the user to reconnect or clarify which calendar should be used.
