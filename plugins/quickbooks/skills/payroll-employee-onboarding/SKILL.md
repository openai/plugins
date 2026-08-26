---
name: payroll-employee-onboarding
description: Onboard a new hire into QuickBooks Payroll from user-provided details or onboarding source files such as offer letters and employee rosters. Use when the user wants to add a new payroll employee, onboard a new employee so they can be paid, deduplicate a new hire before creation, assign an existing payroll work location, set initial contract/base pay during onboarding, or review payroll-readiness gaps. Requires confirmation before write actions and reports remaining setup to finish in QuickBooks Payroll. Do not use for existing-employee pay changes outside onboarding, payroll runs, taxes, direct deposit, benefits, deductions, time off, or compliance advice.
---

# Payroll Employee Onboarding

Guide the user through QuickBooks Payroll employee onboarding with tool-backed checks, batched write approvals, and read-back verification.

Assume the customer has connected their QuickBooks account to ChatGPT before using the QuickBooks Payroll tools. If the tools are unavailable or not authenticated, explain that the QuickBooks connection is required before payroll onboarding can continue.

Use only these payroll tools for QuickBooks Payroll reads and writes:

- `qbo_payroll_search_employee`
- `qbo_payroll_get_company_info`
- `qbo_payroll_create_employee`
- `qbo_payroll_update_employee`
- `qbo_payroll_assign_employee_work_location`
- `qbo_payroll_get_employee_contract_details`
- `qbo_payroll_save_employee_contract_details`

Use available document, spreadsheet, file, OCR, or Gmail/email tools only to retrieve and extract onboarding source data before the payroll workflow. Do not use non-payroll tools for QuickBooks Payroll writes.

## Supported Writes

Use the write tools only for fields they currently support:

- `qbo_payroll_create_employee`: create an employee with first name and last name. Optionally include home address, primary email, phone numbers, hire date, job title, and employment classification.
- `qbo_payroll_update_employee`: sparsely update supported profile fields: first name, last name, home address, primary email, phone numbers, hire date, job title, and employment classification. Send at least one populated mutable field; do not send employee_id-only updates.
- `qbo_payroll_assign_employee_work_location`: assign an existing company work location by `employee_id` and `work_location_id`. It cannot create a new company work location or write an arbitrary work address, and it may replace the prior work-location assignment for that employee.
- `qbo_payroll_save_employee_contract_details`: create or update initial onboarding contract/pay details for one employee. Supported fields are `contract_pay_type`; `pay_rate` with `amount` and `frequency` (`HOURLY`, `WEEKLY`, `MONTHLY`, `YEARLY`) for hourly or salary setup; and `weekly_contracted_time` for salary setup. `contract_pay_type` is required for the first save. For `COMMISSION_ONLY`, omit `pay_rate` and `weekly_contracted_time`.

Existing-employee base-pay changes outside onboarding belong to the base-pay workflow, not this onboarding workflow.

Do not claim current write support for gender, birth date, SSN/tax identifier, employment status, pay schedule assignment, direct deposit, bank account details, tax setup, time off, manager assignment, benefits, deductions, reimbursements, bonuses, commissions beyond the exposed contract pay type, or creating/updating company work-location addresses.

## Core Rules

- Always search before creating. `qbo_payroll_create_employee` is not idempotent; never blindly retry it after a timeout or uncertain response.
- If a likely existing employee is found, warn the user that creating another record may produce a duplicate. If the user explicitly confirms they still want a new employee record, proceed with creation.
- Get explicit user approval before writes, but batch approvals whenever possible. One approval can cover create/update, work-location assignment, and contract save when each planned action and payload is listed.
- Show the exact values that will be written. Do not hide meaningful changes behind summaries such as "standard setup". For staged writes where the only unknown is a system-generated employee id from the immediately preceding create/read-back, the approval may name that placeholder as "the IOP payroll employee_id resolved from the newly created/selected employee"; resolve and verify it before use, and stop for reconfirmation if resolution is ambiguous.
- Use the payroll employee id from the `external_ids` entry whose `namespace_id` is `Intuit.ems.iop`; use its `local_id` for update, work-location, and contract calls.
- Do not invent employee ids, work-location ids, addresses, pay types, rates, or missing required values.
- Never collect, request, display, or store SSNs, tax identifiers, bank account numbers, routing numbers, or direct-deposit account details in chat. Direct the user to finish these through the guided QuickBooks Payroll setup flow or another approved secure surface.
- Create or update only fields listed in Supported Writes. For setup required before payroll can run that is not completed in this chat flow, present it as an in-product QuickBooks Payroll next step instead of improvising.
- Treat `USER_ERROR` or `needs_clarification` as input problems. Ask for corrected values, then reconfirm before retrying the write.
- After a write, read back through the relevant available tool before reporting success.
- After read-back verifies at least one employee was created, updated, assigned a work location, or
  had initial contract/pay details saved, include an **Open in QuickBooks:** handoff. If exactly one
  employee had verified onboarding changes, use the employee name from the resolved or read-back
  employee record and the payroll employee id, which must be the `local_id` from `external_ids`
  where `namespace_id` is `Intuit.ems.iop`:
  `[View <employee name>'s profile](https://qbo.intuit.com/app/employeeProfile?eeid=<employee_id>)`.
  Replace placeholders only with values returned or confirmed by tools; do not invent a profile link
  if the payroll employee id cannot be resolved. If two or more employees had verified onboarding
  changes, use `[View employee list](https://qbo.intuit.com/app/employees)`. Do not include a
  QuickBooks link when no employee change was verified.
- Keep personally identifiable information concise in chat. Repeat only the fields needed for confirmation and avoid exposing extra employee data from search results.
- Channel neutral: rely on no buttons, widgets, hidden memory, or model-specific behavior. If needed, use clear text confirmations and numbered lists instead of UI-only controls.

## Confirmation Ergonomics

Default to a compact two-touch flow:

1. **Intake/draft confirmation**: show extracted or provided safe fields, ask for corrections, collect missing non-sensitive values, and ask which supported setup steps to perform (profile, work location, contract/pay). This single prompt should cover classification, start date, work location intent, and pay setup intent when those are relevant.
2. **Consolidated write approval**: after read-only checks, present one approval request that lists every write that will happen, including tool/action, payload values, duplicate warnings, before/after changes, selected work-location id, and contract/pay values.

Use read-only payroll tools without separate approval once the user has confirmed the employee identity/draft, or when the user directly provides a clear employee identity in chat. For uploaded, emailed, or ambiguous source data, confirm the extracted identity/draft before payroll lookup. Fetch company info only after work-location intent, and fetch contract details only after an employee is unambiguously resolved and pay setup is in scope. Do not ask extra questions merely to run eligible read-only checks.

Ask a follow-up confirmation only when there is a real decision or new risk: likely duplicate, multiple possible matches, unclear work-location match, missing required value, unsupported requested setup, user correction that changes the payload, ambiguous create/read-back, or a generated employee id that cannot be resolved exactly.

When a response needs user input, put the user-facing question or requested action at the very end of the message. Provide duplicate warnings, setup context, missing safe fields, and examples before the final ask. Do not ask a decision question in the middle of a response and then continue with additional setup guidance. If several safe values are needed, combine them into one concise final prompt so the user can focus on exactly what to answer next.

## Input Guardrails

Validate user-provided values before write calls:

- Reject blank or whitespace-only values.
- Keep names, job titles, address fields, phone numbers, and similar free-text fields to 100 characters or fewer.
- Keep enum-style values to 32 characters or fewer.
- Keep ids such as `employee_id` and `work_location_id` to 64 characters or fewer.
- Use `YYYY-MM-DD` for dates such as hire date.
- Use a valid email format when email is provided.
- For employment classification, use only `FULL_TIME`, `PART_TIME`, or `TEMPORARY` unless the tool schema indicates another accepted value; ask for clarification before sending any other value.
- For profile addresses, use supported address components only: `addressLine1`, `addressLine2`, `city`, `stateProvinceCode`, `postalCode`, and `countryCode`. County is not writable through the current create/update employee tools.
- For contract pay, represent money as strings in `pay_rate.amount`, for example `"75000"` or `"27.50"`; use `contract_pay_type` values such as `HOURLY`, `SALARY`, or `COMMISSION_ONLY`; and use `pay_rate.frequency` values `HOURLY`, `WEEKLY`, `MONTHLY`, or `YEARLY`. For `COMMISSION_ONLY`, omit `pay_rate` and `weekly_contracted_time`; do not invent commission rates, plans, or formulas. Do not map pay-schedule terms such as biweekly or every Friday into `pay_rate.frequency`; route pay schedule setup to QuickBooks Payroll.

## Intake Sources

Accept onboarding input from any supported, readable source the user provides:

- Direct chat details, such as name, start date, title, work location, and pay.
- Uploaded offer letters in document, PDF, image, email, or other readable formats.
- Uploaded spreadsheets or rosters, including Excel and CSV files.
- Offer letters or offer emails the user asks you to retrieve from Gmail or email, only if those tools are available and authorized.

For spreadsheets with multiple employees, process one employee at a time unless the user explicitly asks for batch onboarding.

When retrieving from Gmail, ask for enough search detail to find the right message, such as candidate name, sender, subject, date range, or attachment clue. If multiple likely offer letters are found, show a concise numbered list and ask the user to choose one. Do not proceed from an uncertain email or attachment.

If an uploaded file or email cannot be read reliably, ask the user for the missing fields instead of guessing.

## Workflow

### 1. Prepare Onboarding Draft

Extract or collect only fields needed for supported payroll writes and readiness reporting: employee name, email, phone, home address, hire/start date, job title, employment classification, work location label or id, pay type, pay rate amount and frequency, salary amount, and salary weekly contracted time.

Treat extracted data as a draft, not confirmed truth. Show the draft values, identify missing or conflicting fields, and ask the user to confirm or correct them before writes. In the same intake prompt, ask which supported steps to complete and collect safe missing fields such as classification or hire date. Do not include SSNs, tax identifiers, or bank/direct-deposit details in the draft even if they appear in a source document.

### 2. Identify The Employee

Ask for the employee's legal first and last name if the user has not provided them. For broad requests such as "onboard the new team", ask for one employee at a time.

After the draft identity is confirmed, call `qbo_payroll_search_employee` before any create. This is read-only; do not ask for a separate approval just to search:

- If no matching employee appears, proceed to the create proposal and approval step.
- If one likely match appears, show enough identifying information to disambiguate. Put any other safe setup context or missing fields before the disambiguation question, then end the message by asking whether this is the same person.
- If multiple matches appear, present a short numbered list. Put any other safe setup context or missing fields before the selection question, then end the message by asking whether the new hire is one of them.
- If the user confirms an existing employee and wants to use that record, skip creation and continue only with requested updates, work location, or contract setup.
- If the user confirms an existing employee but still wants a separate new record, show the duplicate warning and ask for explicit approval to create another employee record with the same or similar identity.

### 3. Create The Employee

Collect the minimum required profile fields for `qbo_payroll_create_employee`; at minimum this normally includes `first_name` and `last_name`. Offer to include only supported optional profile details when useful: email, phone, home address using supported address components, hire date, job title, or employment classification.

Before calling `qbo_payroll_create_employee`, summarize the exact create payload and ask for explicit approval. Prefer a consolidated approval that also covers requested work-location and contract/pay writes when their values are known from read-only checks. If search found a likely duplicate, include this warning in the confirmation: creating this employee may create a duplicate payroll record.

If the create response is incomplete, times out, or is ambiguous, call `qbo_payroll_search_employee` again before considering any retry. If the intended new employee appears to have been created, do not create again. If only the pre-existing employee appears, explain the uncertainty and ask whether the user wants to retry creating a separate new record.

### 4. Resolve The Payroll Employee Id

After creation, call `qbo_payroll_search_employee` for the employee. Extract the `local_id` from the `external_ids` entry where `namespace_id` is `Intuit.ems.iop`.

If the payroll id cannot be resolved, stop and explain the blocker. Do not guess an id and do not proceed to update, work-location assignment, or contract setup.

If the prior consolidated approval covered staged post-create writes using the generated IOP employee id, proceed only when exactly one matching employee is found and the resolved id is unambiguous. If there is any mismatch, stop and ask for a fresh approval with the exact resolved payload.

### 5. Update Profile Fields

Use `qbo_payroll_update_employee` when the user wants to correct or add supported employee profile fields after creation, or when the user chooses an existing employee record as the target for this onboarding flow. Existing-employee profile changes outside onboarding should route to the appropriate payroll workflow instead of this skill.

Send only fields the user intends to change. Treat updates as sparse but overwriting for each included field. Do not include unchanged fields for convenience. Never send unsupported fields such as gender, birth date, SSN/tax identifier, employment status, pay schedule, pay, bank details, direct deposit, or tax setup through this tool.

Before updating, show a before/after list for each changed field when previous values are available. Include the update in the consolidated approval when possible. After updating, search or otherwise read back the employee details available through the tools before reporting success.

### 6. Assign Work Location

Do not call `qbo_payroll_get_company_info` just because work location is missing. During intake, ask whether the user wants to assign a work location now or skip it.

Call `qbo_payroll_get_company_info` only when the user wants to assign, select, or verify a work location and has not already provided a valid `work_location_id`. This is read-only; after the user has expressed location intent, do not ask separately before fetching it. Present available company/work addresses with their ids or stable labels.

If the provided work location does not clearly match a company work location, do not assign it automatically. Show the closest available company locations and ask the user to choose one, provide a valid `work_location_id`, or skip assignment.

Include the selected company location in the consolidated approval and explain that assigning a work location may replace the prior assignment. After approval, call `qbo_payroll_assign_employee_work_location` with the IOP payroll `employee_id` and selected `work_location_id`.

Verify the assignment using the best available read-back from the payroll tools or the assignment response. Do not claim success if the result is ambiguous.

### 7. Configure Contract And Pay

During intake, ask whether the user wants to configure contract/pay details. If yes, first call `qbo_payroll_get_employee_contract_details` for the employee and preserve existing values unless the user asks to change them. This is read-only; do not ask separately before fetching existing contract details. For a newly created employee, call this after resolving the IOP employee id; if a prior consolidated approval covered pay setup, proceed only when the contract read-back is empty or matches the expected baseline. If existing contract details appear unexpectedly, stop and ask for fresh approval with before/after values.

Collect only the contract fields supported by the tool for the intended pay setup: `contract_pay_type`, `pay_rate.amount`, `pay_rate.frequency`, and `weekly_contracted_time` where applicable. Common rules:

- First-time contract setup requires `contract_pay_type`.
- `HOURLY` setup requires `pay_rate.amount` and `pay_rate.frequency` of `HOURLY`.
- `SALARY` setup requires `pay_rate.amount`, a `pay_rate.frequency` of `YEARLY`, `MONTHLY`, or `WEEKLY`, and contracted weekly time.
- `COMMISSION_ONLY` setup omits `pay_rate` and `weekly_contracted_time`; do not collect or invent commission rates, plans, or formulas in this workflow.
- `pay_rate.frequency` must be one of `HOURLY`, `WEEKLY`, `MONTHLY`, or `YEARLY` when a `pay_rate` is included.
- Partial updates should preserve omitted values from the current contract details, except `COMMISSION_ONLY` should not carry over stale salary or hourly `pay_rate` fields.

Before calling `qbo_payroll_save_employee_contract_details`, show the exact contract changes. Include the contract save in the consolidated approval when possible. After saving, call `qbo_payroll_get_employee_contract_details` again and summarize only read-back values.

### 8. Report Payroll Setup Status

Always produce a concise payroll setup status before the final summary. This is a completion gate: do not end any payroll onboarding turn after intake, approval, writes, failed writes, skipped writes, or verification until the response includes payroll setup status. Lead with what was set up and verified through read-back. Then explain that, to start paying the employee, the user should finish the guided setup in QuickBooks Payroll for any remaining payroll, tax, compliance, payment, or policy details.

Customer-facing wording should sound like a QuickBooks Payroll handoff, not a missing-tools inventory. Avoid section titles or statuses such as "unsupported fields", "not supported by current tools", or "missing tools" unless the user explicitly asks about tool capability. Prefer phrasing like "Complete in QuickBooks Payroll" or "Finish in QuickBooks Payroll".

Assess these readiness areas:

- **Employee profile**: report safe profile fields that were created or updated, such as name, hire date, job title, classification, email, phone, and home address when provided and written. If profile details needed for payroll were not supplied, route the user to complete them in QuickBooks Payroll rather than framing them as chat/tool gaps.
- **Contract and pay details**: report contract pay type, pay rate amount, pay rate frequency, and weekly contracted time when saved or read back. For `COMMISSION_ONLY`, report the contract pay type without pay rate or weekly contracted time. Other compensation setup should be presented as a QuickBooks Payroll follow-up step.
- **Employment status**: report from read-back/search when available. Do not claim the chat workflow set active or detailed employment status unless read-back confirms it.
- **Work location address**: report the assigned existing company work location when verified. If the desired location cannot be matched or assigned, tell the user to select or update the work location in QuickBooks Payroll.
- **Pay schedule**: tell the user to assign or verify the payroll pay schedule in QuickBooks Payroll. Do not confuse this with `pay_rate.frequency`, which is only the pay-rate frequency saved on contract details.
- **Pay method and direct deposit**: tell the user to choose the pay method and complete direct-deposit setup in QuickBooks Payroll when applicable. Never collect or display bank details in chat.
- **Tax and compliance setup**: tell the user to complete federal, state residence, state work, and local tax setup in QuickBooks Payroll, including filing status, non-US TD1 information, wage codes, SSN, or tax identifier where applicable. Never collect or display tax identifiers in chat.
- **Benefits, deductions, time off, bonuses, and policies**: tell the user to configure any applicable payroll policies in QuickBooks Payroll.

For each area, use customer-facing statuses such as:

- `Set up`: confirmed through read-back or explicit user confirmation.
- `Finish in QuickBooks Payroll`: required payroll setup, sensitive data, or product-guided setup that should be completed after logging in to QuickBooks Payroll.
- `Skipped for now`: user chose not to configure the item during this session.
- `Needs clarification`: a safe value is required before performing a requested supported write in this chat.

For multiple employees, report a compact batch status table first, with one row per employee and columns for profile, contract/pay, work location, and overall status. The overall status must name the concrete remaining setup areas, not use umbrella phrases such as "needs payroll setup", "needs location plus payroll setup", "not ready", or "incomplete". Prefer wording such as "Finish work location, pay schedule, tax/compliance, pay method, and policies in QuickBooks Payroll" or "Finish pay schedule, tax/compliance, pay method, and policies in QuickBooks Payroll". Then provide one shared `Finish in QuickBooks Payroll` list for common next steps such as tax setup, pay method/direct deposit, pay schedule, and policies. Add employee-specific follow-ups only for exceptions or differences. Do not repeat the full setup checklist under every employee unless their needs differ.

Ground the status in read-back values and confirmed user input. Do not claim an area is ready from unconfirmed extracted data alone.

Before sending the final response, verify that each requested employee has an explicit row or sentence covering employee profile, contract/pay, work location, and concrete remaining QuickBooks Payroll setup. If any area was skipped, unavailable, failed, or needs product-guided completion, state that area directly.

### 9. Final Summary

End with a short status summary grounded in tool results:

- Employee profile created or updated.
- Payroll employee id resolved.
- Work location assigned or skipped.
- Contract/pay details saved or skipped.
- Payroll setup status and QuickBooks Payroll next actions shared with the customer.

If exactly one employee had verified onboarding changes, end with:

**Open in QuickBooks:**
[View <employee name>'s profile](https://qbo.intuit.com/app/employeeProfile?eeid=<employee_id>)

If two or more employees had verified onboarding changes, end with:

**Open in QuickBooks:**
[View employee list](https://qbo.intuit.com/app/employees)

## Out Of Scope

Do not use this workflow for payroll runs, paycheck deletion or voiding, taxes, benefits deductions, reimbursements, bonuses, time tracking, time-off policy assignment, or manager/reporting-line assignment unless this skill is updated to include explicit supported tools and workflow instructions for those tasks. If the user asks for an unsupported action, explain the limitation and offer to complete the supported onboarding steps.
