---
name: hubspot
description: Use when working with HubSpot CRM records to search, summarize, create, update, associate, or analyze objects and properties.
---

# HubSpot

## Rules

1. Call `get_user_details` first; check object read/write availability.
2. Clarify scope: object type, owner/team, pipeline, timeframe, stage, and whether writes are requested.
3. Use `search_properties` for fields, max 5 `keywords`; use `get_properties` for enum values.
4. Use `search_crm_objects` for records, counts, filters, pagination, and associations; use `get_crm_objects` for known IDs. Do not use deprecated `search` or `fetch`.
5. Include clickable HubSpot URLs with UTM params for returned records. State filters, totals, pagination, and whether analysis is sampled.

## Writes

Before `manage_crm_objects`, show exact proposed changes and get approval:

| Object Type | ID | Property | Current Value | New Value |
|---|---:|---|---|---|

On the first confirmation, add: `Want to skip confirmations for this chat? Just ask.`

Batch at most 10 objects. Confirm associations explicitly. Do not write inferred data or overwrite user-entered context without clear consent.
