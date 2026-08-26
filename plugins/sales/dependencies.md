# Sales Dependencies

Sales workflows refer to capabilities, not required products. A placeholder such as `~~CRM` means whichever available plugin, app, connector, MCP tool, or equivalent user-provided source can supply that category of evidence.

The providers below are examples and routing hints, not installation requirements, an exhaustive provider catalog, or evidence that a provider is installed, authorized, or ready. A custom internal connector or another available tool can satisfy the same category when it exposes equivalent information.

## Dependency Categories

| Category | Placeholder | Example plugins | Other apps or sources |
| --- | --- | --- | --- |
| CRM | `~~CRM` | [@Salesforce](plugin://salesforce@openai-curated-remote), [@HubSpot](plugin://hubspot@openai-curated-remote) | Close, an authoritative CRM export, or grounded account and opportunity details |
| Calendar | `~~Calendar` | [@Google Calendar](plugin://google-calendar@openai-curated-remote), [@Outlook Calendar](plugin://outlook-calendar@openai-curated-remote) | A supplied invitation, meeting link, agenda, or attendee list |
| Meeting Transcripts | `~~Meeting Transcripts` | [@Zoom](plugin://zoom@openai-curated-remote), [@Granola](plugin://granola@openai-curated-remote) | ChatGPT Record, Fireflies, Otter.ai, Zoom recording analysis, transcript exports, grounded call notes, or pasted transcripts |
| Email | `~~Email` | [@Gmail](plugin://gmail@openai-curated-remote), [@Outlook Email](plugin://outlook-email@openai-curated-remote) | Outreach, supplied email threads, or pasted customer communication |
| Internal Messaging | `~~Internal Messaging` | [@Slack](plugin://slack@openai-curated-remote), [@Teams](plugin://teams@openai-curated-remote) | Internal chat tools, exported conversations, or pasted messages |
| Knowledge & Files | `~~Knowledge & Files` | [@Google Drive](plugin://google-drive@openai-curated-remote), [@SharePoint](plugin://sharepoint@openai-curated-remote), [@Notion](plugin://notion@openai-curated-remote) | Other document stores, uploaded files, account plans, notes, or pasted source materials |
| Sales Intelligence | `~~Sales Intelligence` | [@ZoomInfo](plugin://zoominfo@openai-curated-remote), [@Apollo.io](plugin://apollo@openai-curated-remote), [@Clay](plugin://clay@openai-curated-remote) | HG Insights, Rox, Actively, Meticulate, other enrichment tools, or supplied company and contact exports |
| Scheduling | `~~Scheduling` | A suitable installed scheduling plugin | Calendly, another scheduling app, or a supplied scheduling link |
| Work Management | `~~Work Management` | [@Monday.com](plugin://monday-com@openai-curated-remote) | Another task tracker, uploaded project plan, or supplied work items |
| Document Signing | `~~Document Signing` | A suitable installed document-signing plugin | DocuSign, another signing app, or supplied agreement and signature status |
| Presentation Authoring | `~~Presentation Authoring` | [@Presentations](plugin://presentations@openai-primary-runtime) | An available first-party presentation authoring capability that can create the requested editable deck |

Only resolve categories that are material to the selected skill and current request.
Every focused workflow enumerates its relevant dependency categories and may mark at most one category `[Blocking]`.
All other categories are optional; they can improve the answer but must not delay the first useful output.

## Category Resolution

1. Identify the dependency categories used by the selected workflow.
2. Treat every listed category as useful but non-blocking unless the focused skill explicitly marks it `[Blocking]` for the current request.
3. Allow at most one blocking dependency per focused workflow.
4. A blocking category is satisfied by either a suitable available provider or equivalent context already grounded in the conversation, pasted notes, links, exports, or files. Do not request an installation merely because a connector is absent when the necessary evidence is already available.
5. Check the live and lazy-loadable tool registry for the user-named provider and other credible providers in the same category before making a negative availability claim. The initially surfaced app or plugin list is only a hint and is never sufficient evidence that a provider is missing. If a provider is found but its tools are missing on the first discovery pass, retry discovery once before describing it as unavailable.
6. Treat one suitable provider as sufficient. Consult additional providers only when they materially improve coverage, freshness, confidence, or actionability.
7. Provider names and links in this document are suggestions, not proof of runtime availability, installability, authorization, or source freshness. Establish readiness from the available native provider capability and the smallest relevant source read.

## Missing Sources And Fallbacks

Apply these rules whenever a selected category has no verified usable source:

1. Continue from equivalent user-provided context when it already supplies the required evidence.
2. Search the available install or connection surfaces for suitable providers when an additional source would materially improve the request. Use the category examples above as discovery hints, not as proof that a plugin or app can be installed in the current environment.
3. For a `[Blocking]` category, briefly explain the missing evidence and why the first output cannot proceed without it or an equivalent supplied source. When a suitable provider is actually available to install, offer the native install or connection surface before requesting fallback context. Prefer a user-named provider; otherwise recommend the strongest available match or offer a bounded choice when the differences matter.
4. If no suitable provider exists, or installation is declined or fails, ask for the smallest useful upload, export, pasted excerpt, meeting invitation, or other grounded source. Pause only when the focused workflow cannot produce a supported first output without that evidence.
5. For a non-blocking category, do not launch installation, request fallback context, or delay the first useful output. Produce a safe partial answer, explain the material limitation, and offer the missing provider or context only afterward as an optional improvement.
6. Prefer a canonical plugin over a standalone app only when choosing between new installation options. Never replace, supplement, or reinstall an already usable provider merely because another option is more canonical.

## Source Authority

- Prefer `~~CRM` for account ownership, customer status, opportunities, contacts, forecast posture, and pipeline truth. When an authoritative CRM export or user-supplied record stands in for a live CRM, identify its scope, freshness, and any resulting limitations.
- Use `~~Meeting Transcripts` or equivalent grounded transcript-like material for direct customer quotations, call decisions, objections, and commitments. CRM records and internal summaries can narrow the search but are not substitutes for transcript evidence.
- Use `~~Calendar` for meeting identity, attendees, timing, and invitation details when those facts control the workflow.
- Use `~~Email`, `~~Internal Messaging`, and `~~Knowledge & Files` for their actual source evidence; do not let them override authoritative CRM fields or invent unavailable transcript content.
- Use `~~Sales Intelligence` for company, contact, market, and enrichment context. It does not replace CRM-owned opportunity or customer truth.
- Use public web research only for additional enrichment or an appropriate fallback, and never use browser automation as a substitute for an unavailable authoritative connector.

## Provider And Authoring Handoffs

- When a selected third-party provider supplies its own installed plugin skill or instructions, follow that provider-owned guidance before provider-specific reads, record interpretation, or approved changes. Sales does not bundle separate provider-specific skills.
- For a requested customer-facing presentation, follow the selected Sales owner first, then read and follow the [Sales Presentations skill](skills/sales-presentations/SKILL.md) and use the available [@Presentations](plugin://presentations@openai-primary-runtime) authoring plugin.
