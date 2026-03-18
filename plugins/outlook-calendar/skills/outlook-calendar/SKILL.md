---
name: outlook-calendar
description: Handle Outlook Calendar workflows. Use when the user asks for schedule understanding, availability checks, meeting scheduling, intelligent rescheduling, meeting prep, reminder updates, RSVP responses, recurring maintenance, travel coordination, deadline planning, or safe create, update, reschedule, or cancel changes with timezone-aware event times and attendee validation.
---

# Outlook Calendar

## Overview

Use this skill to turn Outlook Calendar data into clear scheduling decisions and safe event updates. Favor exact dates, times, attendees, and timezone-aware details over vague time language.

Use this base skill when the request spans multiple Outlook calendar workflows or when no more focused Outlook calendar skill is a better fit.

## Specialized Skills

- For one-day schedule understanding and agenda readouts, prefer [outlook-calendar-daily-brief](../outlook-calendar-daily-brief/SKILL.md).
- For creating a meaningful focus block through intelligent moves, prefer [outlook-calendar-free-up-time](../outlook-calendar-free-up-time/SKILL.md).
- For ranking the best group meeting options, prefer [outlook-calendar-group-scheduler](../outlook-calendar-group-scheduler/SKILL.md).
- For meeting prep briefs grounded in the event and nearby Microsoft context, prefer [outlook-calendar-meeting-prep](../outlook-calendar-meeting-prep/SKILL.md).
- Keep reminder planning, RSVP replies, recurring-series maintenance, travel-aware scheduling, and deadline planning in this base Outlook skill.

## Preferred Deliverables

- Availability summaries with exact candidate slots, timezone, and relevant conflicts.
- Event change proposals that show the current event details and the intended update.
- Reschedule proposals that show the current event, one to three exact replacement slots, and whether attendee availability was verified or remains unverified.
- Final event details that are ready to create, reschedule, or cancel after confirmation.
- Meeting-note drafts that are phrased as shared, meeting-ready agenda or prep bullets rather than assistant-facing analysis.
- Reminder or deadline plans that make clear whether the outcome is an Outlook event reminder, a calendar hold, an invite response, or a separate automation.

## Workflow

1. Read current calendar state first. Gather the relevant calendars, time window, attendees, timezone, and any existing event details before proposing changes.
2. Normalize relative time language into explicit dates, times, and timezone-aware ranges.
3. Normalize timezone representation before proposing or applying changes. Determine the user's effective mailbox timezone and the event-local timezone that the Outlook connector expects, and do not assume IANA timezone names can be passed through unchanged.
4. For cross-timezone requests such as travel, flights, trains, or events tied to a different city, interpret each stated local time in the timezone of the city where that timestamp occurs before converting it into the Outlook event payload.
5. Surface conflicts before edits. Call out overlapping events, missing attendee details, or other constraints before proposing a create or update.
6. When the request is ambiguous, summarize the best options before drafting an event change.
7. Treat missing title, attendees, location, meeting link, or timezone as confirmation points rather than assumptions.
8. When the request asks for "relevant docs", "background docs", "past notes", or similar meeting context, treat document retrieval as part of the required read path before drafting invite content.
9. For document retrieval across Microsoft surfaces, use the actual connector/tool surfaces directly:
   - Outlook mail context: use the Outlook Email app tools.
   - SharePoint or OneDrive docs: use the Microsoft SharePoint app tools such as `search`, `list_recent_documents`, and `fetch`.
   - Do not use generic MCP resource discovery such as `list_mcp_resources` to discover SharePoint content for this workflow.
10. If a SharePoint search is relevant but no specific site or path is known, search by short participant/project keywords first, then fetch the best candidate documents before summarizing.
11. For reschedules where the user did not specify the destination time, propose one to three exact replacement slots and get confirmation on the chosen slot before moving the event.
12. Check attendee availability before rescheduling when the connector can do so. If recipient availability cannot be verified, say that explicitly and treat any move as best-effort rather than silently assuming the slot works.
13. Only create, update, move, or cancel events when the user has clearly asked for that action or confirmed the exact event details.
14. When changing multiple Outlook events in one turn, prefer direct sequential Outlook tool calls unless the batch or parallel wrapper has already been validated in-session for that exact tool surface.
15. Treat invite-note edits as content edits, not just calendar edits. Before writing synthesized notes, derive the exact text to be inserted and check that it reads like content intended for invite attendees rather than a summary back to the user.
16. When the user asks to "look up context and add a summary" to an invite, first collect the source material and then decide whether the write can be safely applied without confirmation:
    - Safe to apply directly only when the inserted text is short, source-grounded, and phrased as a neutral agenda, decisions, open questions, or next steps section.
    - If the inserted text requires substantive synthesis, interpretation, prioritization, or tone choices, show the exact proposed note to the user before applying it.
17. For meeting-prep writes, prefer updating the body with a concise agenda or discussion focus section over a generic "summary" unless the existing invite already uses a summary style.
18. If multiple information surfaces are available, prefer this retrieval order for meeting prep unless the user names a specific source: current event body, prior related event bodies, Outlook Email, SharePoint/OneDrive docs, then lower-signal notes sources.
19. Before any create or reschedule write, restate the final interpreted weekday, date, local clock time, and timezone for the event. If the task spans multiple cities or time zones, restate each relevant timestamp separately.

## Write Safety

- Preserve event titles, attendees, start and end times, locations, meeting links, and notes from the source data unless the user requests a change.
- Confirm the final timezone before creating or rescheduling an event. Do not rely on a default timezone when the request mentions a city, airport, travel leg, local departure time, local arrival time, or another timezone-sensitive context.
- Treat deletes, cancellations, and broad schedule changes as high-impact actions. Restate the affected event before applying them.
- For reschedules, do not treat an open slot on the user's calendar as sufficient proof that the meeting can be moved there. Either verify attendee availability or obtain user confirmation that a best-effort move is acceptable.
- When a user asks to "move," "reschedule," or "push" a meeting without naming the new time, do not pick a replacement slot unilaterally. Present exact options first unless the user explicitly delegated slot selection.
- If a batch or parallel wrapper returns tool-dispatch errors such as `unsupported call`, do not keep retrying the wrapper blindly. Fall back to the direct Outlook calendar tool surface, apply edits sequentially, and note the limitation in the response.
- If multiple calendars or similarly named events are in play, identify the intended one explicitly before editing.
- If the request references relative dates like "tomorrow afternoon," restate the exact interpreted date, time, and timezone before drafting the change.
- Preserve the original timezone semantics of the source event unless the user asked to change them. When moving an event, distinguish between "same local clock time in a different timezone" and "same absolute instant converted into another timezone."
- Treat Outlook timezone names as a required formatting step. Convert from user-facing timezone references such as cities, offsets, abbreviations, or IANA names into the Outlook-compatible timezone expected by the connector before writing.
- For travel and cross-timezone tasks, never compute departure and arrival times in a single timezone. Departure timestamps must stay anchored to the departure city's local timezone, and arrival timestamps must stay anchored to the arrival city's local timezone until after interpretation.
- If a cross-timezone request leaves any timestamp interpretation ambiguous, stop and ask rather than silently choosing one timezone basis.
- Do not write attendee-facing invite notes that include assistant provenance or meta commentary such as "source quality," "context found in Outlook," "I found," or similar narration about the research process.
- Do not write invite notes in a user-briefing voice. Avoid language that reads like a report to the requester instead of shared meeting content.
- Avoid third-person framing that makes one attendee sound like the subject of analysis when a neutral, shared meeting framing is available. Prefer "Discussion topics," "Open items," "Agenda," or direct issue statements over sentences centered on "Ari said..." unless quoting or attribution is materially necessary.
- When source material is incomplete or unverified, omit the uncertain item, label it as a question for the meeting, or present a draft for confirmation. Do not silently convert uncertain context into asserted meeting notes.
- If prior notes or documents are missing, do not mention that absence inside the invite body unless the user explicitly wants an audit trail in the invite itself.
- If SharePoint retrieval is requested or strongly implied by "relevant docs," do not stop after a failed discovery attempt on a non-SharePoint surface. Re-route to the Microsoft SharePoint connector path or state clearly that the SharePoint connector itself is unavailable.
- Treat tool-surface selection errors separately from content absence. A failed connector-discovery step does not justify concluding that no relevant SharePoint docs exist.

## Output Conventions

- Present scheduling summaries with exact weekday, date, time, and timezone.
- When a task spans multiple time zones, label every timestamp with its local timezone rather than collapsing them into a single timezone summary.
- When sharing availability, explain why a slot works or conflicts instead of listing raw times without context.
- When proposing a new or updated event, format the response as title, attendees, start, end, timezone, location or meeting link, and purpose.
- Keep option lists short and explain the tradeoff for each candidate slot.
- When reporting conflicts, name the overlapping events and how much time is affected.
- When a workflow turns into a reminder, RSVP, recurring-series, or travel-buffer task, say explicitly which Outlook action or follow-up path is being used rather than presenting it as a generic edit.
- For invite-note drafts, prefer a compact structure such as `Agenda`, `Open items`, `Decisions needed`, or `Next steps`.
- Meeting-note text should be concrete and low-drama. Avoid headings like `Prep summary` unless the user asked for that exact label.
- If the note is synthesized from multiple artifacts, collapse the synthesis into meeting-ready bullets rather than exposing the retrieval path or evidentiary narrative.
- When summarizing retrieved prep context back to the user before a write, separate findings by source, for example `Calendar`, `Email`, and `SharePoint docs`, so it is clear which Microsoft surfaces were actually checked.

## Access Notes

- In this environment, SharePoint access for document retrieval comes from the Microsoft SharePoint app tools, not from MCP resource listing.
- If app-tool discovery is needed, use the app/tool discovery path that exposes `mcp__codex_apps__microsoft-sharepoint` tools. Do not assume a server named `sharepoint` exists for `list_mcp_resources`.
- If a wrapper cannot dispatch discovery correctly, fall back to direct SharePoint app-tool calls once the tool surface is available rather than abandoning SharePoint retrieval.
- Outlook connector writes may expect mailbox/Windows timezone names rather than IANA timezone names. Treat timezone conversion as part of write preparation, not as an optional display concern.

## Example Requests

- "Check my Outlook Calendar availability this Thursday afternoon and suggest the best two meeting slots."
- "Move the project review to next week and keep the same attendees and Teams link."
- "Summarize my calendar for tomorrow and flag anything that overlaps."
- "Draft the exact event details for a 30 minute sync with the vendor at 2 PM Pacific on Friday."
- "Help me decide whether to accept this invite, decline it, or propose a better time."
- "Clean up this recurring staff meeting without breaking the whole series."
- "Add the right reminder coverage for my review next week and the deadline after it."

## Light Fallback

If Outlook Calendar data is missing or incomplete, say that Microsoft Outlook access may be unavailable or pointed at the wrong calendar, then ask the user to reconnect or clarify the intended calendar or event.
