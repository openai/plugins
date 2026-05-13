---
name: hubspot-pipeline-health
description: Use when reviewing HubSpot pipeline health, forecasts, stale deals, slipping close dates, or open deal risks.
---

# HubSpot Pipeline Health

Turn open deal data into a concise pipeline-health readout. Follow [../hubspot/SKILL.md](../hubspot/SKILL.md) for access, URLs, pagination, and write approvals.

## Workflow

1. Call `get_user_details` and confirm deal read access.
2. Clarify pipeline, owner/team, timeframe, and closed-deal inclusion. Default to open deals in the current quarter or next 90 days.
3. Discover deal fields: `dealname`, `amount`, `dealstage`, `pipeline`, `closedate`, owner, forecast, next step, last activity/contact.
4. Use `get_properties` for pipeline/stage/forecast enums, then `search_crm_objects` for open deals. Check `total` and page or segment large pipelines.
5. Use `get_crm_objects` for high-signal deals; use `associatedWith` for companies/contacts only when context changes the recommendation.

## Risk And Output

Flag deals with past or near close dates, stale activity, missing owner/contact/next step, missing amount/stage/close date, late stage with weak recent touch, or stage concentration without clear next actions. State which signals were unavailable.

Return coverage, 2-4 executive takeaways, an at-risk deals table with URLs, pipeline hygiene patterns, recommended follow-ups, and caveats. Use `manage_crm_objects` only after the core confirmation table.
