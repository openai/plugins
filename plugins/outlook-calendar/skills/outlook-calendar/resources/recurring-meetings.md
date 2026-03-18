# Recurring Meetings Behavior

Use this resource when a request depends on recurring-meeting scope, cadence, or workplace norms rather than only the event title and time.

## Outlook and Graph Semantics

- Outlook and Microsoft Graph distinguish between a single occurrence, future instances, and the full recurring series.
- Graph event objects can represent `singleInstance`, `occurrence`, `exception`, or `seriesMaster`.
- A recurring meeting may also carry recurrence metadata such as `seriesMasterId`, `recurrence`, and original-start information, but not every connector surface exposes that metadata clearly.
- If the tool output only shows an occurrence-like event and does not expose reliable series-master metadata, treat the read as an instance view rather than a fully trustworthy series view.
- If the user asks to `adjust future instances`, `modify the series`, `skip next week's meeting`, or similar, treat that as a recurrence-scope request rather than a simple one-off event edit.
- If the tool surface cannot prove whether a write is targeting one occurrence, future instances, or the whole series, say so clearly before editing.

## Outlook Product Expectations

- Outlook users expect recurring edits to preserve logistics such as the attendee list, Teams meeting details, room booking, organizer intent, and invite-note format unless the user asks to change them.
- Recurring edits are higher risk than one-off edits because they can silently change attendee expectations across many dates.
- `This event`, `the whole series`, and `future meetings` are real Outlook concepts. Use that language directly when clarifying scope.
- If a request sounds series-wide but the connector behaves instance-by-instance, explain that limitation instead of claiming a true series-level update.

## Workplace Norms

- Use the person's configured work days and work hours as the default frame for recurring work meetings when Outlook exposes them.
- If work hours are unavailable, default work recurrences to weekdays rather than nights or weekends unless the existing pattern or the user's wording says otherwise.
- Prefer stable recurring slots for standing meetings. Avoid proposing frequent time-of-day drift unless the user is intentionally redesigning the pattern.
- Avoid silently moving work recurrences into Friday late afternoon or outside work hours unless the existing series already uses that pattern or the user asked for it.

## Cadence Heuristics

- Prefer weekly for true standing coordination such as team syncs, active project check-ins, or regular 1:1s.
- Prefer biweekly as the lighter default for operational syncs when the user is creating a new recurring work meeting without a clearly stated need for weekly cadence.
- Prefer monthly for reviews, steering meetings, and broader status or planning rituals.
- Avoid suggesting daily recurrence unless the meeting is clearly a standup, incident cadence, or another operational rhythm that truly benefits from daily repetition.
- Treat 1:1s as a special case: longer and more frequent can be reasonable, and consistency usually matters more than aggressive compression.

## Series Length and Buffers

- For project-bound recurring meetings, prefer a bounded series when the work has an obvious horizon rather than an indefinite recurrence.
- If the user is optimizing calendars, consider Outlook-native meeting hygiene such as ending recurring meetings a bit early or preserving transition time between them.
- When extending recurring meetings, check whether the longer duration creates repeated conflicts before recommending a series-wide change.

## Skill Guidance

- Restate the interpreted recurrence scope before any write: one occurrence, future instances, or whole series.
- If the connector output is missing series-master evidence, explicitly say that recurrence scope is being inferred from the visible occurrence pattern.
- When proposing a recurring change, describe both the current pattern and the intended future pattern.
- If the user's request is under-specified, ask the smallest useful recurrence question instead of a generic scheduling question.
