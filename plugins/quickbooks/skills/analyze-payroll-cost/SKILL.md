---
name: analyze-payroll-cost
description: Analyze QuickBooks Payroll cost, payroll spend changes, top-paid employees, pay item drivers, and practical payroll cost-control ideas using connected payroll run, employee, payslip, paycheck, and company context data. Use when the user asks why payroll expense increased or decreased, who was paid the most, what drove payroll spend, how to reduce payroll spend, how current payroll compares with a prior period, or whether overtime, headcount, pay rates, employer taxes such as SUI, benefits, employer contributions, reimbursements, bonuses, commissions, allowances, or pay-item mix affected payroll cost. Read only; use available payroll tools and do not invent payroll facts.
---

# Analyze Payroll Cost

Analyze payroll spend, explain changes, identify top-paid employees or pay-item drivers, and suggest
data-grounded cost review areas. This skill is read-only.

Use only these tools:

- `qbo_payroll_get_company_last_payroll_run`
- `qbo_payroll_get_payslips`
- `qbo_payroll_get_payslip_details`
- `qbo_payroll_search_employee`
- `qbo_payroll_get_employees`
- `qbo_payroll_get_company_info`

## Scope

Use for questions like:

- "Explain why payroll expense increased this pay period."
- "Whom did I pay the most this pay period?"
- "What drove payroll cost?"
- "How can I reduce payroll spend?"
- "How can I reduce my payroll costs while still growing my business?"
- "Compare this payroll run to the prior pay period."
- "Did SUI, benefits, employer contributions, or pay items drive payroll cost?"

Do not use this skill to update employees, change pay, run payroll, void checks, reverse payments,
change setup, or give legal/tax/compliance advice.

## Rules

- Always ground analysis in returned tool data; never answer from generic payroll memory.
- Do not invent employees, payslips, pay items, taxes, deductions, hours, gross pay, net pay, totals,
  dates, or drivers.
- Do not treat missing data as zero. Missing employees, payslips, pay items, hours, taxes,
  deductions, or employer costs are unavailable.
- Do not imply a full payroll-expense total unless all relevant returned cost components support it.
  Label every total by basis: gross pay, net pay, employer cost, or returned payroll-run total.
- If prior-period data is unavailable, say the comparison is limited and analyze returned data only.
- Separate fact from interpretation: "The data shows..." for facts, "This may indicate..." for likely
  causes.
- Cost-control ideas must be operational and data-grounded, not directives or HR/legal/tax advice.
- For actual compensation changes, use a write-capable workflow only if the environment exposes one.
- If one tool call fails, answer from successful returned data and include a clear limits note.
- `qbo_payroll_get_company_last_payroll_run` returns only the most recent payroll run, which may be
  for one pay schedule when the company has multiple schedules. Do not treat it as company-wide
  payroll history or company-wide period spend by itself.
- Include a brief QuickBooks handoff in the final answer so the user can continue reviewing the
  payroll data in product. If `qbo_payroll_get_payslips` data is used in the final analysis, include
  `[View paycheck list](https://qbo.intuit.com/app/payroll/ledgers/paycheck-ledger)`
  after a final `**Open in QuickBooks:**` label line.
  If `qbo_payroll_get_payslip_details` data is used in the final analysis, include this link exactly
  once after the same label line: `[View payroll summary report](https://qbo.intuit.com/app/payroll/reports/payroll-summary)`.
  If both tools are used in the final analysis, format the handoff as three lines: the
  `**Open in QuickBooks:**` label, then the paycheck list link, then the payroll summary report link.
- Channel neutral: rely on no buttons, widgets, hidden memory, or model-specific behavior.

## Tool Routing

Start with `qbo_payroll_get_company_last_payroll_run` for current/latest payroll-run questions, but
label it as the latest returned run and its returned pay schedule. If the user asks a company-wide
period question, profitability question, month-to-date question, or pay-schedule comparison question,
also use `qbo_payroll_get_company_info` for pay-schedule context and `qbo_payroll_get_payslips` for
the relevant date range when returned payslip coverage is needed.

Use `qbo_payroll_get_payslips` for date ranges, prior-period comparison, past paychecks, or
employee-level data. Use `qbo_payroll_get_payslip_details` only after a payslip ID is known and
detail is needed for pay items, taxes, deductions, gross-to-net, or variance drivers.

Use `qbo_payroll_search_employee` for named employees. Use `qbo_payroll_get_employees` only for
roster-wide context. Use `qbo_payroll_get_company_info` only for company/pay schedule context; do not
use it for payroll-cost math unless it returns a relevant value.

When company info returns multiple pay schedules, mention each returned schedule when schedule
context matters. Analyze spend from returned payroll run or payslip amounts, not from schedule
frequency or active employee counts alone. If returned payslips do not establish coverage for every
schedule in the requested period, say the analysis is limited to the returned payslips and do not
claim a company-wide total.

Do not call every tool by default.

## Analysis Rules

For spend changes:

1. Compute current-period total from returned data.
2. Compute prior/comparison total only if returned or fetchable.
3. Calculate dollar and percent change only when both the current-period total and prior/comparison-period total exist.
4. Decompose by employee first, then pay item when details exist.
5. Highlight the largest contributors and limits.

For top-paid questions, rank by the requested metric. If none is specified, use gross pay when
available; otherwise use the clearest returned amount and label it. Include pay period/pay date when
returned. Default to top 5 for broad rankings.

For cost-reduction questions, identify largest visible buckets and unusual changes, then suggest
review areas tied to returned data: overtime, bonus/commission/allowance timing, reimbursements,
benefits or employer contributions, employer tax changes, scheduling, headcount, pay-rate changes,
high-rate labor mix, or pay-item mix. Avoid recommending employee-specific pay cuts unless the user
asks.

For growth-oriented cost questions, keep suggestions payroll-data grounded and frame them as review
areas such as scheduling, coverage planning, staffing mix, reimbursement controls, or variable-pay
approval review. Do not claim revenue, margin, or growth impact unless returned data supports it.

## Data Handling

Track only returned fields: pay period, pay date, employee, gross pay, net pay, employer taxes/costs,
employee taxes, deductions/contributions, pay items, hours, rates, and quantities.

Do not fill missing values. If totals do not reconcile because components are missing, say that. If
date filtering, prior-period retrieval, or pagination is unavailable or incomplete, say the analysis
is based only on returned records.

## Answer Shape

Lead with the answer, then show supporting numbers.

For spend-change analysis:

```text
Short answer: Payroll spend [increased/decreased] by [amount/percent if available] for [period], mainly because [top drivers].

Key numbers:
- Current period: [total and basis]
- Prior period: [total and basis, if available]
- Change: [amount and percent, if available]

Top drivers:
1. [Employee/pay item]: [amount/change] - [evidence]

Cost-control ideas to review:
- [Data-grounded idea]

Limits: [missing data, pagination, unsupported comparison, or failed tool call]

**Open in QuickBooks:**
[View paycheck list](https://qbo.intuit.com/app/payroll/ledgers/paycheck-ledger)
[View payroll summary report](https://qbo.intuit.com/app/payroll/reports/payroll-summary)
```

For unsupported requests, say what payroll-cost analysis can show and what the current toolset cannot
show. Example: profitability requires revenue or margin data, which this payroll-only skill does not
provide.
