---
name: fa-jobs-to-be-done
description: Use when the user asks for D&B Finance Analytics workflows such as customer onboarding, credit decisioning, credit limit validation, portfolio risk management, company reports, ownership trees, folder management, or alerts. Use only the D&B Finance Analytics MCP tools for these workflows.
metadata:
  mcp_server: finance_analytics_mcp_server
  codex_plugin: dnb-finance-analytics
---

# Finance Analytics Jobs To Be Done

This skill routes D&B Finance Analytics requests to the partner-supplied workflow
references in `fa-skills/references/`.

## Tool Source

Use the D&B Finance Analytics MCP server only. Do not substitute Morningstar,
Moody's, generic web search, local files, or another MCP server for Finance
Analytics data.

Before making a tool call, confirm the Finance Analytics MCP tools are available.
If they are not visible, tell the user the D&B Finance Analytics connection is not
available and stop rather than fabricating data.

Expected Finance Analytics tools include:

- `fa_search_tool`
- `query_portfolio`
- `get_company_report`
- `get_live_report`
- `account_decisioning_tool`
- `application_decisioning_tool`
- `manage_folder`
- `get_company_ownership_tree`
- `query_alerts`
- `get_portfolio_status`
- `get_portfolio_public_records`
- `get_companies_and_accounts_count`
- `get_dashboard_overview`
- `get_risk_distribution`
- `get_dashboard_status`

Tool names may be exposed with a Codex namespace such as
`mcp__finance_analytics_mcp_server__query_portfolio`; use the namespaced form when
available.

## Route The Request

Load exactly one workflow reference based on the user's intent:

| Intent signals | Load this reference |
| --- | --- |
| onboard, new customer, new account, add to portfolio, can I do business with | `fa-skills/references/fa-onboarding-workflow.md` |
| credit decisioning, company overview for credit, financial profile, company report | `fa-skills/references/fa-credit-decisioning.md` |
| approve credit, credit limit, increase credit, validate credit, extend credit | `fa-skills/references/fa-credit-validation.md` |
| portfolio risk, top risky companies, portfolio overview, risk distribution, risky accounts | `fa-skills/references/fa-portfolio-management.md` |
| alerts, unread alerts, new alerts, alert severity, alerts for a company | `fa-skills/references/fa-alerts-monitoring.md` |

If the user's intent is ambiguous, ask one clarifying question before calling tools.

The partner bundle did not include dedicated persona files or an aging-forecast
workflow file. For persona-specific language, load `fa-skills/references/fa-plain-language.md`.
For aging forecast requests, explain that no aging-forecast workflow was supplied in
this skill bundle and ask whether the user wants to proceed with available portfolio
or report workflows instead.

## Output Layer

Before producing user-facing output, load:

- `fa-skills/references/fa-plain-language.md`

Use it for tone, numeric presentation, status summaries, and suppression of internal
tool or entity identifiers.

## Required Behavior

- Never fabricate or fill gaps with assumed D&B data.
- Retry a failed or unexpectedly empty Finance Analytics tool call once with the
  same parameters.
- If a tool still fails, document what was attempted, what was missing, and how the
  gap affects the result.
- Favor precision over recall when resolving companies or making risk assessments.
- Never make a binding credit approval or decline; frame credit outputs as suggested
  decisions based on available data.
- Include an audit trail when the selected workflow requires one.
- Do not pause mid-pipeline unless a blocking ambiguity must be resolved before a
  critical decision.

## Workflow

1. Identify the user intent.
2. Load `fa-plain-language.md`.
3. Load the matching workflow reference.
4. Follow that reference's tool order and output structure.
5. Cite the D&B Finance Analytics app as the data source when returning substantive
   credit, portfolio, report, ownership, or alert results.
