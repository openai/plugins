# Close CRM Workflow Patterns

These patterns are adapted from the Close Cursor plugin workflows for ChatGPT and the Close MCP server.

## Account Brief

Use when the user asks to prepare for a call, summarize an account, brief them on a lead, or catch them up on a deal.

1. Find and disambiguate the lead.
2. Fetch the selected lead and relevant contacts.
3. Gather active opportunities, recent calls, meetings, email threads, notes, and incomplete tasks.
4. Summarize:
   - company and key contacts;
   - active opportunities with stage, value, owner, confidence, and close date when available;
   - recent calls, meetings, and email threads;
   - open or overdue tasks;
   - risks, open questions, and a recommended next step.
5. Do not modify CRM data.

## Pipeline Review

Use when the user asks about pipeline health, deal risk, stale opportunities, close-date risk, forecasting, or what to prioritize.

1. Clarify the scope if needed: owner, status, pipeline, date range, segment, or "my active opportunities."
2. Discover the relevant pipeline and opportunity status fields before filtering.
3. Find active opportunities in scope.
4. Identify:
   - opportunities with overdue or missing next steps;
   - stale deals with no meaningful recent activity;
   - close dates, confidence, or values that deserve attention;
   - important actions to take next.
5. Summarize criteria used, keep facts separate from recommendations, and include Close links when available.
6. Do not modify CRM data unless the user explicitly asks for a specific follow-up action.

## Follow-Up Plan

Use when the user asks what to send next, how to follow up, or how to keep a deal moving.

1. Find and disambiguate the lead.
2. Review recent calls, meetings, emails, SMS, notes, opportunity state, and incomplete tasks.
3. Provide:
   - a short relationship summary;
   - the strongest next action and why;
   - a suggested message or call outline;
   - recommended task timing and owner when supported by the data.
4. Do not send messages, create tasks, or change Close records unless the user explicitly asks after reviewing the plan.

## Record Updates

Use when the user asks to create or update a lead, contact, opportunity, note, task, status, template, workflow, custom object, custom activity, or voice-agent configuration.

1. Resolve the target record and any dependent IDs.
2. Discover organization-specific fields or statuses before writing.
3. Summarize the intended mutation if any material value is ambiguous.
4. Perform only the requested write.
5. Report what changed, which record was changed, and any returned Close URL.

## Destructive Actions

Use when the user asks to delete records or apply irreversible changes.

1. Verify the exact target records with IDs or unambiguous names.
2. Explain the irreversible impact.
3. Ask for explicit confirmation before using destructive tools.
4. After the action, report the deleted or changed records clearly.
