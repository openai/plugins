# FA Alerts Monitoring - Sub-flow Reference

**Tools used:** `query_alerts`

This file defines the Alerts Monitoring workflow. It is loaded by the master `SKILL.md`
when user intent resolves to viewing, filtering, or triaging FA system alerts.

**Core question answered by this workflow:**

> "What alerts do I have - and which ones need my attention right now?"

FA system alerts notify credit teams of changes, risk events, and required actions related
to portfolio companies. This workflow helps users find, filter, and act on alerts quickly.

---

## Pipeline Overview

```
Stage 1:  Retrieve and Filter Alerts
  - Stage 2:  Triage and Prioritise
    - Stage 3:  Summarise and Recommend Actions
```

---

## Trigger Examples

- "Show me my alerts."
- "What unread alerts do I have?"
- "Show me all high-severity alerts."
- "Are there any alerts for Company X?"
- "What new alerts came in today?"
- "Show me all open alerts."
- "Which alerts need my immediate attention?"

---

## Stage 1 - Retrieve and Filter Alerts

**Purpose:** Call `query_alerts` with the appropriate filters to retrieve the relevant
alert set for the user's query.

**Tool call sequence:**

1. Determine the appropriate filter parameters based on the user's request:

   | User request | Filter to apply |
   |---|---|
   | "My alerts" / "All alerts" | No filter - retrieve all alerts |
   | "Unread alerts" | `read_status = unread` |
   | "New alerts" | `read_status = unread`, optionally filter by recent date |
   | "Alerts for Company X" | `company_name = X` or `duns = <DUNS>` |
   | "High severity alerts" | `severity = high` |
   | "High and medium severity" | `severity IN (high, medium)` |
   | "Alerts by type" | `alert_type = <type>` |
   | Count only | Include count aggregation parameter |

2. Call `query_alerts` with the resolved filter parameters.
   - If the user specified a company name but not a DUNS: resolve the DUNS first via
     `fa_search_tool` or `query_portfolio` before filtering alerts by company.
   - Request the following fields per alert: company name, DUNS, alert type, severity,
     alert date, read/unread status, alert description / message, any associated account
     or entity reference.
   - Apply sort: `severity` descending, then `alert_date` descending (most recent first).

3. If the result set is large (e.g. > 50 alerts): summarise by severity and type first,
   then present the top N highest-severity or most recent unread alerts in detail. Ask
   the user if they want to see more.

**Required outputs:**

- Total alert count matching the filter
- Count breakdown by severity (High / Medium / Low)
- Count breakdown by read status (Unread / Read)
- Alert list with: company name, alert type, severity, date, read status, brief description

**Failure condition:** If `query_alerts` returns an error or empty result:
1. Retry once with the same parameters.
2. If still failing: document the failure and advise the user that alerts could not be
   retrieved. Do not simulate alert data.

---

## Stage 2 - Triage and Prioritise

**Purpose:** Organise the returned alerts into a prioritised view so the user can act
on the most important items first.

**Triage logic:**

| Priority tier | Criteria | Action signal |
|---|---|---|
| Immediate action | High severity + Unread + Recent (within 24 hours) | Flag as "Requires immediate attention" |
| Review today | High severity + Unread (any date) OR Medium severity + Unread + Recent | Flag as "Review today" |
| Monitor | Medium severity + Read OR any Low severity | Flag as "Monitor - no immediate action" |
| Informational | Low severity + Read | Summarise only; do not surface in detail unless asked |

**Apply triage to the retrieved alert set:**

1. Group alerts by priority tier.
2. Within each tier, sort by alert date descending.
3. For "Immediate action" and "Review today" alerts: show full detail (company name,
   alert type, severity, date, description).
4. For "Monitor" and "Informational" alerts: show a summary count and brief description
   only, unless the user requests detail.

**Required outputs:**

- Tiered alert list with priority tier labels
- Immediate action alerts presented in full detail
- Review today alerts presented in full detail
- Monitor / Informational alerts presented as a count summary

**Narrative:** State how many alerts require immediate attention, how many are for review
today, and how many are informational. Be specific about which companies and alert types
are at the top of the list.

---

## Stage 3 - Summarise and Recommend Actions

**Purpose:** Translate the alert triage into a clear action plan for the credit team.

**Output format:**

1. **Alert summary header:**
   - Total alerts retrieved
   - Unread count
   - Breakdown by severity

2. **Immediate action items:**
   For each "Immediate action" alert:
   - Company name, DUNS
   - Alert type and brief description
   - Why it requires immediate attention
   - Recommended action

3. **Review today items:**
   For each "Review today" alert:
   - Company name, DUNS
   - Alert type and brief description
   - Recommended action

4. **Monitor items:**
   - Summary count only (e.g. "12 low-severity alerts are being monitored - no action
     required at this time.")

5. **Recommended actions by alert type:**

   | Alert type | Recommended action |
   |---|---|
   | Bankruptcy / insolvency | Escalate immediately to credit committee; freeze further credit exposure |
   | Payment delinquency | Initiate collections contact; review credit limit |
   | Credit limit breach | Review credit terms; reduce limit or require immediate payment |
   | Risk score deterioration | Pull updated company report; consider credit review |
   | Legal filing (suit, lien, judgment) | Notify credit manager; assess impact on collectability |
   | Ownership change | Review implications for credit policy; verify new ownership |
   | Business closure / dissolution | Escalate immediately; assess exposure and collection options |

**Required outputs:**

- Alert summary (total, unread, by severity)
- Immediate action items with recommended actions
- Review today items with recommended actions
- Monitor summary count
- Full audit trail

**Narrative:** Lead with the most urgent items. Be direct about what needs attention and
what action to take. Close with a clear summary of what is being monitored.

---

## Handoff Contracts

| Handoff | Payload |
|---|---|
| Stage 1 - Stage 2 | Full alert list with fields: company, DUNS, alert type, severity, date, read status, description |
| Stage 2 - Stage 3 | Tiered alert list (Immediate / Review today / Monitor / Informational) with priority labels |
| Stage 3 - Output | Alert summary, action items by tier, recommended actions by type, audit trail |

---

## Known Tool Integration Notes

| Tool | Issue | Handling |
|---|---|---|
| `query_alerts` | Supports filtering by company, alert type, severity, and read status | Always specify filters based on user intent to avoid over-fetching large alert sets |
| `query_alerts` | May return a large result set for broad queries | Summarise by severity and type first; present detail for high-priority alerts only |
| `query_alerts` | Company name filter may require DUNS for precision | Resolve DUNS via `fa_search_tool` or `query_portfolio` when the user specifies a company by name |

---

## Behavioural Requirements (Alerts - specific)

- Always lead with the highest-severity, unread, most recent alerts.
- Never mark alerts as read without the user's explicit instruction to do so.
- If the user asks for alerts for a specific company: resolve the company to a DUNS first
  before filtering - company name matching in `query_alerts` may be imprecise.
- For very large alert sets (> 100 alerts): do not dump the full list. Summarise and ask
  the user which tier or type they want to explore.
- Always include the complete audit trail at the bottom of the output.

