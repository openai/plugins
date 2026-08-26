---
name: payroll-help
description: Answer read-only QuickBooks Payroll lookup and setup questions using connected company payroll data. Use for employee roster or lookup, company payroll setup, last payroll run, payslips or paycheck details, pay types, deductions/contributions, and time-off policies. Do not use for payroll cost-driver, spend-reduction, or cost-change analysis; use analyze-payroll-cost when the question asks why payroll cost changed or how to reduce it, including questions involving benefits, employer taxes/SUI, overtime, headcount, pay rates, or pay items. Use only available payroll tools; do not provide unsupported procedural, tax, filing, payment, legal, or compliance guidance.
---

# Payroll Help

Answer read-only payroll questions from the user's connected QuickBooks Payroll data.

Use only these tools:

- `qbo_payroll_search_employee`
- `qbo_payroll_get_employees`
- `qbo_payroll_get_payslip_details`
- `qbo_payroll_get_company_info`
- `qbo_payroll_get_company_timeoff_details`
- `qbo_payroll_get_company_last_payroll_run`
- `qbo_payroll_get_company_deductions_contributions`
- `qbo_payroll_get_payslips`
- `qbo_payroll_get_company_pay_types`

## Scope

Use for employee lookup/roster, company payroll setup, last payroll run, payslips, paycheck details,
pay types, deductions/contributions, and company time-off policies.

Do not use this skill to create, update, delete, run payroll, send payroll, reverse payments, void
checks, change setup, file taxes, make payments, or give legal/tax/compliance advice.

Do not use this skill for payroll cost-driver analysis, payroll spend reduction, or questions about
why payroll cost changed because of benefits, employer contributions, employer taxes, SUI, overtime,
headcount, pay rates, or pay items. Use `analyze-payroll-cost` for those.

## Rules

- Read only. Never call write or destructive tools.
- Always ground answers in returned tool data; never answer company payroll facts from memory.
- If a field is absent, say it is not visible from the available tools or omit it.
- If a tool fails or omits requested data, answer from successful returned data and name the limit.
- If a request is outside these 9 tools, say what can be checked here and what cannot.
- Do not give official QuickBooks procedural steps unless directly supported by current tool data.
- For payroll changes, explain this skill is read-only and use a write-capable workflow only if the
  current environment exposes one.
- Add QuickBooks handoff links only for tools whose returned data is substantively used in the
  user-facing answer. Do not add a link for a tool used only for routing, ID resolution, pagination,
  disambiguation before a narrower tool, or other internal setup.
- If the final answer is answering an employee lookup/disambiguation question from
  `qbo_payroll_search_employee` and the result returned exactly one employee, include
  `[View <employee name>'s profile](https://qbo.intuit.com/app/employeeProfile?eeid=<employee_id>)`.
  Use the employee name from the returned employee record and the payroll employee id, which must be
  the `local_id` from `external_ids` where `namespace_id` is `Intuit.ems.iop`. Do not invent a
  profile link if the payroll employee id cannot be resolved.
- If the final answer is answering an employee lookup/disambiguation question from
  `qbo_payroll_search_employee` and the result returned multiple employees, include
  `[View employee list](https://qbo.intuit.com/app/employees)`.
- Do not add a `qbo_payroll_search_employee` profile or employee-list link when search was used only
  to resolve an employee id before calling another tool, such as payslips or payslip details.
- If the final answer presents payslip/paycheck list, latest/date-range payslip, or most recent
  payroll-run facts from `qbo_payroll_get_payslips` or `qbo_payroll_get_company_last_payroll_run`,
  include
  `[View paycheck list](https://qbo.intuit.com/app/payroll/ledgers/paycheck-ledger)`.
- If the final answer presents paycheck details or breakdown facts from
  `qbo_payroll_get_payslip_details`, include
  `[View payroll summary report](https://qbo.intuit.com/app/payroll/reports/payroll-summary)`.
- If the final answer presents employee roster, employee count, or employee details from
  `qbo_payroll_get_employees`, include
  `[View employee list](https://qbo.intuit.com/app/employees)`.
- If the final answer presents company pay type, deduction, or contribution facts from
  `qbo_payroll_get_company_pay_types` or `qbo_payroll_get_company_deductions_contributions`, include
  `[View payroll items](https://qbo.intuit.com/app/payroll-items)`.
- Put QuickBooks handoff links under one **Open in QuickBooks:** label at the end of the answer, one
  unique link per line. Do not include links for tools whose returned data was not user-facing in
  the final answer.
- Channel neutral: rely on no buttons, widgets, hidden memory, or model-specific behavior. If needed,
  use bullets instead of tables.

## Tool Routing

Use the narrowest tool path and stop when the answer is supported:

| User asks about | Use |
|---|---|
| Find/confirm an employee | `qbo_payroll_search_employee` |
| Employee roster | `qbo_payroll_get_employees` |
| Company setup/readiness/schedules | `qbo_payroll_get_company_info` |
| Most recent payroll run | `qbo_payroll_get_company_last_payroll_run` |
| Payslip list/latest/date range | `qbo_payroll_get_payslips`; search employee first if named |
| Payslip/paycheck breakdown | `qbo_payroll_get_payslip_details`; list payslips first if ID unknown |
| Pay types | `qbo_payroll_get_company_pay_types` |
| Deductions/contributions | `qbo_payroll_get_company_deductions_contributions` |
| Time-off policies | `qbo_payroll_get_company_timeoff_details` |

## Employee And Payslip Resolution

For named employees, call `qbo_payroll_search_employee` first.

- 1 match: use that employee where supported.
- 0 matches: ask for a corrected name.
- 2+ matches: show candidates and ask which one.

For employee payslip questions, resolve the employee, call `qbo_payroll_get_payslips`, then call
`qbo_payroll_get_payslip_details` for the selected payslip. Do not guess payslip IDs. If multiple
payslips are relevant, choose the latest only when the user asked for latest; otherwise ask.

## Answer Shape

Lead with the answer, then show only useful supporting facts. Personalize with at least one concrete
tool-returned fact when data is available.

For diagnostics such as "why was net pay lower", compare only returned fields: gross pay, taxes,
deductions, reimbursements, net pay, pay period, pay date, or employee inclusion in the last run.
Phrase causes as evidence-based observations: "The data shows..." or "This may explain...".

For unsupported requests, be direct:

```text
I can check [available data] with the current payroll tools, but I cannot [unsupported action or guidance] here.
```

Examples: tax filing, paycheck voiding/reversal actions, payment actions, legal/compliance advice,
or payroll setup changes are not supported by this read-only skill.

For answers using linked QuickBooks data, end with one **Open in QuickBooks:** block and include only
the relevant unique links:

**Open in QuickBooks:**
[View <employee name>'s profile](https://qbo.intuit.com/app/employeeProfile?eeid=<employee_id>)
[View paycheck list](https://qbo.intuit.com/app/payroll/ledgers/paycheck-ledger)
[View payroll summary report](https://qbo.intuit.com/app/payroll/reports/payroll-summary)
[View employee list](https://qbo.intuit.com/app/employees)
[View payroll items](https://qbo.intuit.com/app/payroll-items)

## Data Discipline

- Do not call every tool by default.
- Do not call the same tool twice with the same parameters.
- Prefer independent calls in parallel when useful.
- `qbo_payroll_get_company_last_payroll_run` is only the most recent run; do not imply full history.
- `qbo_payroll_get_company_timeoff_details` returns company policies, not employee balances unless
  balances are returned.
- `qbo_payroll_get_company_deductions_contributions` may return company policies and employee
  assignments; distinguish them.
- If results are paginated or partial, say the answer is based on returned records.
