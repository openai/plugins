---
name: hubspot-customer-prep
description: Use when preparing HubSpot customer briefs for meetings, renewals, QBRs, sales calls, escalations, handoffs, or follow-ups.
---

# HubSpot Customer Prep

Assemble a customer-ready brief while separating CRM facts from inferred recommendations. Follow [../hubspot/SKILL.md](../hubspot/SKILL.md) for access, URLs, pagination, and write approvals.

## Workflow

1. Call `get_user_details` and confirm read access to the needed object types.
2. Clarify seed record and goal: company, contact, deal, ticket, meeting type, attendees, date, and desired outcome.
3. Find the seed record with `search_crm_objects` using name, domain, email, deal name, or ticket subject. If multiple records match, return a disambiguation list with URLs.
4. Discover properties with `search_properties`: company owner/lifecycle/domain; contact title/email/last contact; deal amount/stage/close date/next step; ticket status/priority/category.
5. Use `associatedWith` searches for related contacts, companies, deals, and tickets. Fetch selected records with `get_crm_objects` when richer fields are needed.

## Brief

Return source record URLs, snapshot, people, open opportunities, support health, recommended agenda, questions to ask, follow-ups, and caveats. For tasks, next steps, associations, ownership, or stage changes, show exact proposed changes and get approval before `manage_crm_objects`.
