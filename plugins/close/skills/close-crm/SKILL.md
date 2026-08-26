---
name: close-crm
description: Use Close CRM via MCP to research leads, review pipeline and activity, prepare follow-ups, answer Close product questions, and safely create or update CRM records.
---

# Close CRM

Use this skill when a request involves the user's Close organization, leads, contacts, opportunities, activities, notes, tasks, workflows, templates, voice agents, custom objects, custom activities, or Close product knowledge.

Close is communication-centered CRM. Treat calls, emails, SMS, meetings, notes, tasks, opportunities, and lead/contact records as connected context when answering sales questions.

## Working Method

1. Start with the narrowest read tool that can answer the request.
2. Resolve names to records before acting. If multiple records plausibly match, ask the user which one they mean.
3. Use returned IDs for follow-up fetches and mutations. Never invent IDs, field names, statuses, pipelines, users, custom-field values, workflow IDs, voice-agent IDs, or object IDs.
4. For organization-specific configuration, discover the available definitions first. Use tools such as `get_fields`, `find_lead_statuses`, `find_pipelines_and_opportunity_statuses`, `find_lead_custom_fields`, `find_contact_custom_fields`, `find_opportunity_custom_fields`, `find_custom_activities`, and `find_custom_object_types` before filtering, aggregating, or writing those fields.
5. Present findings with record names, owners, dates, amounts, statuses, and Close URLs when the tools return them.
6. Clearly label inference. Do not present inferred deal risk, sentiment, next action, or qualification status as a CRM fact.

## Tool Selection

- General lead or company lookup: use `lead_search`, then `fetch_lead` for the chosen lead.
- Recent communication: use `activity_search` for calls, meetings, email threads, SMS, and related activity, then fetch specific records when more detail is needed.
- Opportunities and pipeline: use `find_opportunities`, `fetch_opportunity`, and `fetch_pipeline_and_opportunity_statuses`.
- Tasks and follow-up: use `find_tasks` and `fetch_task`; create or update tasks only after the user has clearly asked for that action.
- Reporting: use `get_fields` before `aggregation` so filters and groupings match the organization's schema.
- Product and setup questions: use `close_product_knowledge_search` for current Close features, setup, API behavior, and limitations.
- Voice-agent changes: inspect existing agents and reports first. Use `propose_voice_agent_update` before `apply_voice_agent_update`.

## Writes And Safety

- Treat the OAuth scope selected by the user as the maximum permission, not blanket authorization.
- Read-only analysis needs no confirmation.
- Before creating or updating Close data, summarize the exact target record and material values if the user's request did not already specify them clearly.
- Do not broaden a request for one record into a bulk update.
- Do not claim that an email, SMS, call, or workflow was sent, scheduled, applied, or recorded unless a tool actually performed that action.
- Only delete data after an explicit deletion request and confirmation that identifies the exact records and irreversible impact.
- For voice-agent changes, propose the update first and apply it only after the user approves the proposal.

## Response Style

- Lead with the answer or recommended action.
- Keep CRM facts separate from recommendations.
- For briefs and reviews, prefer concise bullets grouped by account context, recent activity, open work, risks, and next steps.
- When data is missing, say what you checked and what was not found.
- When a write is needed but not yet authorized, present the proposed values and ask for confirmation in plain language.

## Common Workflows

See `references/workflows.md` for detailed account brief, pipeline review, and follow-up planning patterns adapted from the Close Cursor plugin.

Close MCP documentation: https://developer.close.com/mcp
