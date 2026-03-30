# Availability Response

Use this resource when the user wants Outlook Calendar to propose meeting options, check when they are free, draft a response with candidate times, or place a temporary hold.

## Defaults

- For broad availability requests without a stated window, default to a near-term business window. Prefer the current workweek when it still has useful time left, otherwise use the next 7 days.
- For broad availability requests without a stated time of day, prefer business hours from Outlook working-hours data. If Outlook does not expose working hours, use standard weekday business hours that fit the user's locale and work culture rather than early mornings, evenings, or weekends.
- Prefer a short list of strong options over an exhaustive dump of open time.

## Outlook-Specific Focus

- Distinguish firm conflicts from softer constraints such as `Tentative`, `Free`, or `Working Elsewhere`.
- If a slot is available only because another item is marked `Free` or `Working Elsewhere`, explain that nuance rather than presenting it as a fully clean opening.
- If the answer depends on partial shared-calendar visibility, say that directly.

## Temporary Holds and Replies

- If the user asks for a temporary hold and does not provide a title, use a simple Outlook-style placeholder such as `Temporary hold`.
- If the user asks for a hold and does not provide a narrower search window, choose a reasonable near-term slot using the defaults above rather than stopping for avoidable clarification.
- If drafting a response to send elsewhere, make it directly sendable and keep the wording polished and practical.
- If applying a temporary hold, say whether it is tentative, private, or expected to be removed later.

## Output Conventions

- Return 2-3 options by default unless the user asked for more.
- Label each option with exact weekday, date, time, and timezone.
- Say why each slot is good, not just that it is open.
