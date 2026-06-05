# FA Portfolio Risk Management - Sub-flow Reference

**Tools used:** `query_portfolio`, `get_risk_distribution`, `get_dashboard_overview`,
`get_companies_and_accounts_count`, `get_dashboard_status`, `manage_folder`

This file defines the Portfolio Risk Management workflow. It is loaded by the master
`SKILL.md` when user intent resolves to portfolio-wide risk assessment, risk
distribution analysis, top risky companies, or portfolio organisation actions.

**Core question answered by this workflow:**

> "How risky is my portfolio right now - and what do I need to act on?"

This workflow gives a Credit Manager or Financial Analyst a clear view of the portfolio's
risk posture: where the risk is concentrated, which accounts require immediate attention,
and what actions are recommended.

---

## Pipeline Overview

```
Stage 1:  Portfolio Health Check
  -> Stage 2:  Risk Distribution and Top Risky Accounts
    -> Stage 3:  Recommended Actions and Portfolio Organisation
```

---

## Trigger Examples

- "Give me a portfolio risk overview."
- "What are my top 10 riskiest customers?"
- "Show me the risk distribution across the portfolio."
- "Which accounts have high outstanding balances past due?"
- "Portfolio overview."
- "Who are my high-risk companies?"
- "Move all high-risk accounts to the Review folder."
- "What is the overall health of my portfolio?"

---

## Stage 1 - Portfolio Health Check

**Purpose:** Establish the current size, shape, and status of the portfolio before
drilling into risk detail.

**Tool call sequence:**

1. Call `get_dashboard_status` to check that the portfolio dashboard is operational.
2. Call `get_companies_and_accounts_count` to retrieve the total number of companies
   and accounts in the portfolio.
3. Call `get_dashboard_overview` to retrieve the portfolio-level summary - active
   accounts, total outstanding exposure, summary risk flags.

**Required outputs:**

- Portfolio status (operational / degraded)
- Total company count
- Total account count
- Total outstanding exposure (aggregate)
- Portfolio-level summary flags (e.g. number of bankruptcies, number of high-risk accounts)

**Narrative:** Summarise the portfolio at a glance. State how many companies and accounts
are being monitored, total exposure, and any headline risk flags from the dashboard.

**Failure condition:** If `get_dashboard_status` returns a degraded or unavailable state,
annotate and proceed with the tools that remain available. Do not halt the workflow for a
dashboard status issue - continue to Stage 2 using `query_portfolio` and
`get_risk_distribution` directly.

---

## Stage 2 - Risk Distribution and Top Risky Accounts

**Purpose:** Map the risk distribution across the portfolio and surface the accounts
requiring the most immediate attention.

**Tool call sequence:**

1. Call `get_risk_distribution` to retrieve the distribution of risk levels across the
   portfolio (e.g. counts and percentages at Low / Moderate / High / Severe risk bands).
2. Call `query_portfolio` to retrieve the list of companies sorted by risk severity. Use
   the following filter and sort logic:
   - Primary sort: `overall_business_risk` descending (highest risk first)
   - Secondary sort: `total_past_due_dollars` descending
   - Include fields: company name, DUNS, `overall_business_risk`, `max_credit_recommendation`,
     `paydex_current`, `failure_score`, `delinquency_score`, `total_outstanding_dollars`,
     `total_past_due_dollars`, `credit_limit_utilization`, `db_bankruptcy_present`
   - Return top 10-20 accounts by default unless the user specifies a different count
3. If the user asked specifically about accounts with high past-due balances: apply an
   additional filter on `total_past_due_dollars` > 0 or above a stated threshold.

**Required outputs:**

- Risk distribution table: count and percentage of portfolio at each risk band
- Top risky accounts table: ranked list with risk level, outstanding, past due, PAYDEX
- Accounts with bankruptcy present: flagged separately
- Accounts with credit limit utilisation > 90%: flagged separately (high concentration risk)

**Narrative:** Describe the risk distribution - what percentage of the portfolio is in
each risk band. Identify the top risky accounts by name and summarise why they are flagged
(high outstanding, high past due, poor payment score, bankruptcy). Highlight any accounts
requiring immediate action.

**Failure condition:** If `get_risk_distribution` fails: derive a risk distribution
approximation from `query_portfolio` results by grouping on `overall_business_risk`.
Annotate that the distribution is approximated from portfolio data.

---

## Stage 3 - Recommended Actions and Portfolio Organisation

**Purpose:** Translate the risk picture into concrete actions. Optionally organise
high-risk accounts into designated portfolio folders.

**Tool call sequence (for portfolio organisation requests):**

1. Call `manage_folder` with action `LIST` to retrieve the current folder structure.
2. For each account requiring movement:
   - Identify the appropriate target folder based on risk level:
     - High / Severe risk -> "High Risk" or "Review" folder
     - Accounts with bankruptcy -> "Bankruptcy / Workout" folder
     - Accounts with high utilisation -> "Credit Review" folder
   - Call `manage_folder` with action `MOVE` or `COPY` to place the account in the
     target folder.
   - If the target folder does not exist: call `manage_folder` with action `CREATE`
     first, then `MOVE` or `COPY`.
3. Confirm all folder movements by summarising what was moved and where.

**Recommended actions (always include in output, even when no folder actions are taken):**

| Risk signal | Recommended action |
|---|---|
| OBR = High or Severe | Place on watch list; reduce or suspend credit extension; request updated financial information |
| Bankruptcy present | Escalate to credit committee immediately; freeze further credit exposure |
| Past due > 90 days | Initiate collections contact; review credit limit |
| Credit utilisation > 90% | Review credit limit against MCR before extending further credit |
| PAYDEX < 50 | Flag for payment behaviour review; consider requiring prepayment or reduced terms |
| Failure score class >= 4 | Elevate monitoring frequency; consider insurance or collateral requirements |

**Required outputs:**

- List of recommended actions per high-risk account (name, risk signal, recommended action)
- Folder organisation confirmation (if folder actions were taken)
- Summary of what changed vs what remains for human review

**Narrative:** Summarise the recommended actions clearly. For each flagged account, state
the specific risk signal and what the credit team should do about it. If folder organisation
was performed, confirm what was moved and where.

**Failure condition:** If folder management tools fail, document the failure, output the
recommended actions list, and advise the user to perform folder organisation manually.

---

## Persona Handling

This workflow is used by both Credit Managers and Financial Analysts with different
information needs. The persona layer (loaded at Step 2.5 of the master skill) governs
how the output is framed:

| Persona | Focus |
|---|---|
| Credit Manager | Decision-focused: which accounts need action, what is the credit exposure, what should I approve or restrict |
| Financial Analyst | Trend-focused: how is the portfolio evolving, what are the concentration patterns, what do the distributions tell us |
| Plain language | Accessible summary: what the portfolio looks like, what needs attention, what to do next |

---

## Handoff Contracts

| Handoff | Payload |
|---|---|
| Stage 1 -> Stage 2 | Portfolio status, company/account counts, total exposure, dashboard summary flags |
| Stage 2 -> Stage 3 | Risk distribution, top risky accounts list, bankruptcy flags, high-utilisation flags |
| Stage 3 -> Output | Recommended actions per account, folder organisation confirmation, full audit trail |

---

## Known Tool Integration Notes

| Tool | Issue | Handling |
|---|---|---|
| `query_portfolio` | Supports rich filtering and sorting - use field-level filters for targeted queries | Always specify sort fields and required output fields explicitly to avoid over-fetching |
| `get_risk_distribution` | Returns aggregated risk bands - does not return individual company data | Always pair with `query_portfolio` for account-level detail |
| `manage_folder` | `LIST` must be called before `MOVE` or `COPY` - never assume folder names | Always LIST first; create new folders if required target does not exist |
| `get_dashboard_overview` | May return stale data if dashboard has not been refreshed | Note data freshness in the output; advise user if dashboard status shows degraded |
| `get_companies_and_accounts_count` | Returns portfolio-level totals only | Use alongside `query_portfolio` for account-level breakdown |

---

## Behavioural Requirements (Portfolio Management - specific)

- Never make binding credit decisions or modifications from this workflow. The output
  is an informational risk view and a set of recommendations - the credit manager retains
  authority over all credit actions.
- Always show the risk distribution before showing individual accounts - context before
  detail.
- If the user asks to move accounts to folders: confirm what will be moved, then execute.
  Do not move accounts without confirmation if the scope is broad (e.g. "move all high-risk
  accounts") - ask for confirmation before executing bulk folder operations.
- Always include the complete audit trail at the bottom of the output.


