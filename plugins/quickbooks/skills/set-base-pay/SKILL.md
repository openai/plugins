---
name: set-base-pay
description: Set, view, or change employee base pay (salary or hourly rate) in QuickBooks Payroll. Use when the user asks to see current pay, give a raise (absolute, increment, or percentage), reduce or adjust pay, switch between salary and hourly, change pay frequency, or update weekly contracted time for one or more named employees. Reads the current contract first, requires explicit confirmation before writing, then verifies the change using qbo_payroll_search_employee, qbo_payroll_get_employee_contract_details, and qbo_payroll_save_employee_contract_details.
---

# Set Base Pay

Resolve employees, read current contracts, compute and validate proposed base-pay changes, confirm
before writing, save, then read back to verify.

Use only these tools:

- `qbo_payroll_search_employee`
- `qbo_payroll_get_employee_contract_details`
- `qbo_payroll_save_employee_contract_details`

## Scope

Use for current base pay, salary/hourly changes, raises/cuts, pay-type switches, pay-rate frequency,
and weekly contracted time for named employees.

Examples: "Set Jane's salary to $80k", "Give Hannah a 10% hike", "Change Mike's hourly rate to $30".

Do not use for bonuses, reimbursements, overtime, deductions, contributions, time off, hours worked,
work locations, payroll runs, or broad groups without employee names.

## Rules

- Always call tools; never answer from memory or invent IDs, rates, pay types, frequencies, weekly
  time, or confirmations.
- Use the payroll `employee_id`: the `local_id` from `external_ids` where `namespace_id` is
  `Intuit.ems.iop`; never use the top-level employee `id`.
- Always read current contract details before proposing or saving.
- Always ask for explicit approval before `qbo_payroll_save_employee_contract_details`.
- Never claim success until read-back confirms the approved values.
- After `qbo_payroll_save_employee_contract_details` succeeds and read-back confirms at least one
  employee change, include an **Open in QuickBooks:** handoff. If exactly one employee was updated
  successfully, link to that employee profile using the employee name from the resolved employee
  record and the payroll `employee_id`, which must be the `local_id` from `external_ids` where
  `namespace_id` is `Intuit.ems.iop`:
  `[View <employee name>'s profile](https://qbo.intuit.com/app/employeeProfile?eeid=<employee_id>)`.
  Replace placeholders only with values returned or confirmed by tools; do not invent a profile link
  if the payroll employee id cannot be resolved. If two or more employees were updated successfully,
  link to `[View employee list](https://qbo.intuit.com/app/employees)`. Do not include a QuickBooks
  link when the save tool was not called or no employee change was verified.
- Never convert currencies. Ask for the exact numeric amount to save.
- If a requested field cannot be saved here, such as an effective date, say it will not be applied.
- Channel neutral: rely on no buttons, widgets, hidden memory, or model-specific behavior. If needed,
  use numbered before/after lists instead of tables.

## Workflow

### 0. Read-only pay lookup

For "show current pay" requests, search the employee, read contract details, summarize returned pay
type, rate, frequency, and weekly contracted time, then stop. Do not call the save tool.

### 1. Resolve employees

Parse all named employees and requested changes before write tools.

- More than 10 named employees: ask to split into batches of 10 or fewer.
- Duplicate employee with same change: merge.
- Duplicate employee with conflicting changes: ask which one to use before tool calls.
- Broad group without names: ask for employee names; do not discover or update a roster.

Call `qbo_payroll_search_employee` for each name. Exactly 1 match resolves; capture the
`Intuit.ems.iop` `local_id`. For 0 matches, ask for a corrected name or permission to skip. For 2+
matches, show candidates and ask. On error, retry once, then report.

Only active employees can be updated. If a resolved employee is not active, skip that employee and
report the returned status.

Continue only after every employee is resolved or skipped. If none remain, say there are no changes
to apply and stop. Otherwise briefly confirm the resolved names and any skipped names before reading
contracts.

### 2. Read contracts

Call `qbo_payroll_get_employee_contract_details` once per resolved employee. Record returned
`contract_pay_type`, `pay_rate.amount`, `pay_rate.frequency`, and `weekly_contracted_time`.

Missing contract: collect `contract_pay_type`, `pay_rate`, `pay_rate.frequency`, and salary weekly
contracted time before approval. Relative change with no current rate: ask for an absolute rate.
Read error: retry once; if it fails again, block only that employee.

Ask once for all missing required fields across employees.

### 3. Compute proposal

Round rates to 2 decimals. Preserve existing pay type, frequency, and weekly time unless the user
changes them or a required field is missing.

- Absolute set: requested value.
- Increment: `current + amount`.
- Decrement: `current - amount`.
- Percentage raise/cut: `current * (1 +/- percent/100)`.
- Pay-type switch: require an absolute new rate; set both `contract_pay_type` and `pay_rate`.

Frequency: `HOURLY` contracts always use `HOURLY`; `SALARY` defaults to `YEARLY` unless user asks
for `MONTHLY` or `WEEKLY`; `COMMISSION_ONLY` omits `pay_rate`. Biweekly is unsupported; say only
`HOURLY`, `WEEKLY`, `MONTHLY`, and `YEARLY` can be saved.

### 4. Validate baked contract metamodel

Validate the full proposed payload before approval:

| Pay type | Rate bounds | Frequency | Weekly contracted time |
|---|---|---|---|
| `HOURLY` | 0.01 to 200000 | `HOURLY` | Optional; `hours_per_day` 0 to 24, `days_per_week` 0 to 7 |
| `SALARY` | 1 to 10000000 | `YEARLY`, `MONTHLY`, or `WEEKLY` | Required; `hours_per_day` 0.01 to 24, `days_per_week` 0.01 to 7 |
| `COMMISSION_ONLY` | Omit `pay_rate` | Omit | Omit |

For salary weekly time, if one field is missing, use the current contract when available; otherwise
default to 8 hours/day and 5 days/week. Reject out-of-bounds values before approval. Present all
validation issues together and ask the user to fix, skip, or cancel.

Do not proceed to approval until every remaining employee is valid. If the same employee fails
validation 3 times, suggest skipping and explain the repeated constraint failure. If none remain,
say there are no valid changes to apply and stop.

### 5. Confirm

Hard stop. Show one before/after table for all valid employees, changing fields only. Use exactly
three columns: `Employee`, `Current`, `Proposed`; do not split fields into separate columns. For new
contracts, show `-` for Current and all proposed fields. If unsupported fields were requested, note
them here as not applied.

| Employee | Current | Proposed |
|---|---|---|
| Alice | Rate: $25.00/hour | Rate: $27.50/hour |
| Bob | Pay Type: HOURLY, Rate: $40.00/hour | Pay Type: SALARY, Rate: $80,000.00/year, Weekly Contracted Time: 40 |

For one valid employee, ask exactly:

`Shall I apply this change?`

For two or more valid employees, ask exactly:

`Shall I apply these changes? You can also say "skip [name]" to exclude specific employees.`

If one valid employee remains after resolving, excluding, or skipping other names, use the
single-employee question and mention excluded/skipped employees separately.

Then wait and call no tools. Decline/cancel: stop and write nothing. Changes: recompute/revalidate
only affected employees and ask again. Skips in multi-employee proposals: drop them, re-show, and ask
again. If the user asks to skip the only remaining employee, say there are no changes to apply and
stop. If the user combines changes and skips, resolve references to concrete values before dropping
skipped employees. If none remain, say there are no changes to apply and stop.

### 6. Save

After approval, call `qbo_payroll_save_employee_contract_details` once per approved employee. Send
only fields being set or changed, plus:

- `employee_id` always.
- `contract_pay_type` for new contracts or pay-type changes.
- `pay_rate` for new contracts or rate changes, except `COMMISSION_ONLY`.
- `weekly_contracted_time` for salary contracts.

Use string amounts such as `"75000"` or `"27.50"`. Track employees separately. Do not retry a
successful save.

### 7. Reconcile

For each successful save, re-read contract details and compare returned values to the approved
proposal.

Report **Updated successfully** and **Failed to update** sections as needed; include **Failed to
update** whenever any save or read-back fails. A read-back mismatch is a failure.

If exactly one employee is in **Updated successfully**, end with:

**Open in QuickBooks:**
[View <employee name>'s profile](https://qbo.intuit.com/app/employeeProfile?eeid=<employee_id>)

If two or more employees are in **Updated successfully**, end with:

**Open in QuickBooks:**
[View employee list](https://qbo.intuit.com/app/employees)

## Example

User: "Give Maya a 10% hike and set Jack to $40/hr."

Search Maya and Jack, read contracts, compute Maya `$45 * 1.10 = $49.50/hr` and Jack `$40.00/hr`,
validate, show before/after proposal, wait for approval, save separately, then re-read and report
only confirmed matches as updated.
