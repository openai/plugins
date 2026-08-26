---
name: business-health-check
description: synthesize a QuickBooks business health briefing from multiple Intuit QuickBooks app reports. Use when the user asks broad questions such as "how's my business doing?", "give me the big picture", "what should I be worried about?", "summarize my financials", "anything unusual this month?", or wants one conversational view of profit and loss, cash flow, balance sheet, receivables aging, and sales performance without opening separate reports.
---

# Business Health Check

## Goal
Turn a broad financial-health question into a concise CFO-style briefing by first confirming the user's reporting choices, then pulling the relevant Intuit QuickBooks app reports, using the tools' built-in previous-period comparison where available, and explaining what is going well, what needs attention, and what changed.

## Pre-flight input
Do not immediately execute reports with defaults. Start by asking the user for the inputs needed to run the health check before calling any Intuit QuickBooks tools.

Ask for these inputs in one concise message:

1. Reporting period:
   - Offer common choices such as current month-to-date, last month, current quarter-to-date, last quarter, year-to-date, or a custom date range.
   - If the user chooses a custom range, collect explicit start and end dates.
2. Report scope:
   - Standard: Profit and Loss, Cash Flow, Balance Sheet, A/R Aging Summary, and Sales by Customer Summary.
   - Expanded: Standard plus Sales by Product/Service Summary.
   - Custom: only the reports the user selects.
3. Accounting method:
   - Default to accrual if the user does not choose.
   - If the user chooses cash basis, do not run A/R Aging Summary; explain that A/R Aging Summary is accrual-only and omit it from the plan.
4. Comparison:
   - Default to the tools' built-in previous-period comparison where available.
   - Define previous period as the immediately preceding period of the same length as the selected reporting period. For example, Jun 1-17 compares to May 15-31.
   - If built-in comparison data is not available from a report, say comparison is not available for that report rather than making extra prior-period report calls.

Do not mention omitted optional reports, such as Sales by Product/Service when Standard scope is selected, in the initial prompt. Only mention an omitted report during pre-flight when it is necessary to explain an incompatible user choice, such as cash basis and A/R Aging Summary.

Do not mention PDF generation in the initial prompt.

## Default assumptions
- Treat "my business", "my company", and "our business" as the connected QuickBooks company.
- If the user asks to use defaults, use current month-to-date for activity reports and an as-of-today Balance Sheet snapshot.
- Use accrual basis unless the user explicitly chooses cash basis.
- Use the tools' built-in previous-period comparison where available. Do not make separate current/prior report calls just to compute the previous period.
- Keep the answer plain-language, business-owner friendly, and focused on decision usefulness.

## Tool sequence for QuickBooks account data
Use the tools exposed by the Intuit QuickBooks app connector.

Always use the text-only variants of each Intuit QuickBooks tool listed below. These return plain text/markdown so you can synthesize the briefing yourself without rendering interactive widgets.

After the user confirms the plan:

1. Call the Intuit QuickBooks `company_info` tool first to establish the QuickBooks connection.
2. Pull the selected reports using the text-only tool variants:
   - `profit_loss_quickbooks_account_text` for revenue, COGS, expenses, gross margin, net income, and monthly breakdown.
   - `cash_flow_quickbooks_account_text` for operating/investing/financing cash movement, net cash increase, and ending cash.
   - `qbo_accounting_get_balance_sheet_text` for assets, liabilities, equity, cash, A/R, A/P, current ratio, debt-to-equity, and working capital.
   - `qbo_accounting_get_ar_aging_summary_text` for receivables concentration and overdue buckets.
   - `qbo_accounting_get_sales_by_customer_summary_text` for customer revenue concentration and customer-level changes.
   - `qbo_accounting_get_sales_by_product_summary_text` for product/service sales mix and product-level changes when the user selected Expanded scope or specifically requested product/service detail.
3. For prior-period comparison:
   - Use built-in comparison parameters or trend data returned by the selected report tools where available, e.g. `compare_to="PREVIOUS_PERIOD"` on sales reports.
   - Treat "previous period" as the immediately preceding same-length period used by the tools.
   - Do not issue separate prior-period report calls just to compute a comparison. If a selected report does not return comparison data, call that out in the briefing.
   - For balance-sheet trend/change, use a single Balance Sheet call with `split_by="MONTH"`, `"QUARTER"`, or `"YEAR"` only when the user selected a trend view or the tool can return the needed columns in one report call.
4. If a tool is unavailable, returns incomplete data, or authentication/profile setup blocks the report, explain the gap briefly and continue with the reports that succeeded. Do not invent missing numbers.

## Period mapping
- "this month" / "this month to date" -> P&L, cash flow, and sales current month-to-date dates if available; Balance Sheet as-of today unless the user selects a trend view.
- "last month" -> `LAST_MONTH` or exact first/last dates for tools that require date parameters.
- "this quarter" -> `THIS_QUARTER`; "last quarter" -> `LAST_QUARTER`.
- "this year" / "YTD" -> `THIS_YEAR_TO_DATE` for period activity and `THIS_YEAR`/end-date snapshot for balance sheet when needed.
- Exact month/year -> use first and last day of that month as `start_date` and `end_date` when supported.
- For any selected date range, the default previous-period comparison is the immediately preceding same-length period. Example: Jun 1-17 compares to May 15-31.

## Synthesis rules
Build a single integrated briefing instead of listing raw reports.

Always include the report context near the top of the briefing:
- Connected company name from `company_info`.
- Reporting period for the main analysis.
- Accounting method used by the reports, when returned by the tools.
- Prior/comparison period, especially when different reports use different comparison windows.

Prioritize these signals:
- Profitability: revenue trend, gross margin, net profit, major expense movements, COGS shifts.
- Cash: operating cash flow, ending cash, cash increase/decrease, working capital, current ratio.
- Balance sheet strength: assets vs liabilities, equity, debt-to-equity, A/R and A/P balances.
- Receivables: total A/R, positive overdue amount, 31+ / 61+ / 91+ buckets, top customers owed, aging deterioration.
- Sales: top customers, customer concentration, product/service mix, fast-growing or declining customers/products.
- Unusual items: large one-time expenses, sudden margin changes, cash drops despite profit, sales concentration, growing overdue receivables, negative A/R balances, A/P pressure, negative working capital, rising debt, product mix shifts.

Flag something as a concern when one or more are true:
- Profit is down while revenue is flat/up.
- Gross margin declines materially from prior period.
- Cash falls while net income is positive.
- Operating cash flow is negative.
- Current ratio is below 1.0 or working capital is negative.
- Overdue A/R is a meaningful share of receivables or 61+/91+ buckets are increasing.
- One customer or product appears to drive a large share of sales.
- A/P aging indicates vendor bills are building or moving into older buckets.
- A/R is negative or an aging bucket contains a negative amount. Treat this as an accounting cleanup, credit, overpayment, or payment-application flag, not as overdue receivables or collections risk unless the data also shows positive overdue balances.

Rank "Needs attention" by business severity. Lead with liquidity and cash risks first, then revenue or margin deterioration, then receivables/payables exposure, then accounting cleanup or data-quality flags such as negative A/R. Include a short severity label such as "High", "Medium", or "Cleanup" when it helps the user prioritize action.

Do not overstate confidence. Use phrases such as "the data points to", "the main watchout is", or "this looks like" when interpreting patterns.

## Output format

Do not output any briefing text before the widget. Call `business_health_check_widget` first as the primary output step.

After the widget renders, output a short conversational follow-on in plain text — 3 short paragraphs, no headers, no bullet points:

1. **Overall verdict sentence**: one sentence covering what is going well and the headline metric (compact numbers, no cents). Example: "Q2 looks healthy on the fundamentals: revenue grew 9% to $612K, gross margin climbed to 64%, and you added $11K of cash while covering every payroll cycle."
2. **The #1 thing to act on**: one short paragraph on the top "Needs attention" item. Connect data points across reports — tie the overdue amount to a near-term obligation (payroll, vendor bill), name the specific customer or bucket, and say why it moves the broader picture. Use compact numbers. Example: "The thing I'd act on this week is collections. $118K is past due, and more than half of it is Meridian Group at 61 to 90 days, which lands right before your Jul 15 payroll run. Meridian is also 38% of Q2 revenue, so their payment behavior moves your whole cash picture."
3. **Offer to help**: one sentence that mirrors the top action chip and invites the user to take the next step. Example: "Want me to draft the collection reminders, starting with Meridian?"

Keep the total follow-on under 100 words. Use plain conversational language — no jargon, no report names, no section labels. Do not repeat the severity badges or metric labels from the widget.

## Widget render (final step)

Call the `business_health_check_widget` tool automatically after synthesizing the data.
Do NOT ask the user for permission — call it as the only output step.

Map the briefing sections to tool arguments as follows:
- `companyName`: connected company name from `company_info`.
- `period`: the reporting period label used in the briefing (e.g. "June 2026 (MTD)").
- `accountingMethod`: e.g. "Accrual" or "Cash".
- `comparisonPeriod`: the comparison period label. Use a quarter label when the dates map to a standard quarter (e.g. if the prior period is Dec 31, 2025 to Mar 31, 2026 or Jan 1 to Mar 31, 2026, write "Q1 2026"). Otherwise use "Month D to Month D, YYYY" format. Do NOT append "where available" or any other qualifier — just the period label. Use "not available" only if no comparison data was returned at all.
- `overallRead`: one of "strong", "stable", "mixed", or "needs_attention" — matching the Overall read verdict.
- `overallReadText`: the one-sentence verdict from the **Overall read** field.
- `keyNumbers`: a list of objects, one per row in the Key Numbers table. Each object must have:
  `"area"`, `"currentRead"`, and `"whatChanged"` string fields.
  - `"area"`: short label only — e.g. "Revenue", "Gross margin", "Net income", "Cash position", "Working capital", "A/R overdue". Do NOT include ratios or sub-labels (write "Working capital", not "Working capital / current ratio").
  - `"currentRead"`: the raw value ONLY — copied verbatim from the exact labeled location in the tool output listed below. Do NOT calculate, round, or restate. Do NOT include the metric name in the value (write `"42.6%"`, not `"42.6% gross profit margin"`). The widget formats dollar values to K/M automatically.
    - **Revenue**: copy the dollar value next to `"Total Income"` in the P&L text summary (e.g. `"$422,150.00"`).
    - **Gross margin**: copy the percentage next to `"Gross Profit Margin"` in the P&L text summary (e.g. `"42.6%"`). This value is pre-computed by the tool — do not divide or recalculate.
    - **Net income**: copy the dollar value next to `"Net Income"` in the P&L text summary (e.g. `"-$18,320.00"`). May be negative.
    - **Cash position**: copy the dollar value from the `"CASH AT END OF PERIOD"` row in the Cash Flow report table (e.g. `"$19,097,951.09"`).
    - **Working capital**: copy the dollar value from the `"Working capital: $X"` phrase in the Balance Sheet text summary (e.g. `"$1,484,291.75"`). May be negative.
    - **A/R overdue**: copy the dollar value from the `"$X overdue"` phrase in the A/R Aging text summary (e.g. `"$87,450.00"`). If the value is negative (credit balance) or zero, use `"$0"` — do not omit the row and do not copy a negative value.
  - `"whatChanged"`: one concise sentence of 15 words or fewer — plain language, no cents, e.g. "Up 9% vs Q1, led by expanded retainer and two new clients." Do not mention current ratio if total liabilities are negligible (under $1,000).
  Also set `"trend"` when you have prior-period comparison data:
  - `"positive"` if the metric improved vs the prior period (e.g. revenue up, margin up, cash up, overdue A/R down)
  - `"negative"` if the metric worsened vs the prior period (e.g. revenue down, margin down, net income down, overdue A/R up)
  - Omit `"trend"` (or set `"no_change"`) if the change is flat or no comparison data is available.
  Always set `"trend"` when the P&L, cash flow, or balance sheet tools return prior-period data — do not leave it blank just because the direction is unfavorable.
  Also set `"reportLabel"` to the short name of the source report for each row:
  - `"P&L"` for Revenue, Gross margin, Net income — all three must use exactly `"P&L"`, never the area name
  - `"Cash Flow"` for Cash position / ending cash
  - `"Balance Sheet"` for Working capital / current ratio
  - `"A/R Aging"` for A/R overdue / receivables
  - Omit `"reportLabel"` if the metric does not map to a specific report.
- `goingWell`: the bullets from the **What's going well** section (list of strings). Open each bullet with the key metric or finding in `**bold**`, followed by the supporting context in plain text. Example: `"**Revenue is up 9%** on the expanded Meridian retainer and two new engagements, without margin slipping."` Do not bold the entire sentence — bold only the opening key phrase (2–5 words). Use compact numbers for all dollar amounts (e.g. `$54K`, `$1.4M`) — no raw values with cents.
- `needsAttention`: the bullets from the **Needs attention** section. Each item must have `"severity"` ("High", "Medium", or "Cleanup") and `"text"`.
  - `"text"` must be one concise sentence of 20 words or fewer. Lead with the issue category and key number, e.g. "Collections: $118K overdue, led by Meridian Group at $76K now 61–90 days past due."
  - Use compact numbers in `"text"` (e.g. `$118K`, `$1.4M`, `38%`) — do not paste raw unformatted dollar values like `$1,374,317.33`.
  - Connect data points across reports where relevant — e.g. tie overdue A/R to an upcoming payroll or cash position, tie concentration risk to the overdue customer. One sentence only.
  - Do not repeat the severity label in the text (the badge already shows it).
  - Optionally set `"description"`: one sentence of context or interpretation that explains the business impact, e.g. "That cash is tied up ahead of the Jul 15 payroll run; the 61–90 bucket doubled since Q1."
  - Optionally set `"actionLabel"` and `"actionPrompt"` together: a short chip label (2–3 words, verb-first) and the follow-up prompt it sends. These are template patterns — substitute real customer names, amounts, and periods from the synthesized data into the `actionPrompt` text. Example pairings:
    - Overdue A/R → `"actionLabel": "Draft reminders"`, `"actionPrompt": "Chase my overdue invoices, starting with [customer name and amount from the 61–90 bucket]."`
    - Payroll / expense spike → `"actionLabel": "Explain payroll cost"`, `"actionPrompt": "Show me details of my latest payroll run and suggestions to keep it down"`
    - Customer concentration → `"actionLabel": "See customer mix"`, `"actionPrompt": "Show my sales by customer for [period]"`
    - Negative A/R / cleanup → `"actionLabel": "How to fix"`, `"actionPrompt": "How do I apply the [customer] credit in QuickBooks"`
    - Product / service mix → `"actionLabel": "Run the breakdown"`, `"actionPrompt": "Run sales by service line for [period]"`
    - Omit `actionLabel`/`actionPrompt` if no clear immediate action applies.
- `whatChanged`: the bullets from the **What changed since last period** section (list of strings). Open each bullet with the key change in `**bold**`, followed by the quantified detail in plain text. Example: `"**Two analysts joined in April**, lifting payroll 11% as they ramp to billable."` Bold only the opening key phrase (2–5 words). Use compact numbers for all dollar amounts (e.g. `$54K`, `$1.4M`) — no raw values with cents.
- `reportLinks`: a dict mapping report label → URL, built from the `**[View in QuickBooks](URL)**` line at the start of each text tool's response. Only include keys where a URL was actually returned. Use exactly these keys: `"P&L"`, `"Cash Flow"`, `"Balance Sheet"`, `"A/R Aging"` — never use area names like `"Revenue"`, `"Gross margin"`, or `"Net income"` as keys. The P&L tool's URL maps to `"P&L"` only — Revenue, Gross margin, and Net income all share this one key. Example: `{"P&L": "https://qbo.intuit.com/app/report/builder?rptId=abc&type=temp", "A/R Aging": "https://..."}`. Omit the argument entirely if no tool returned a URL.
- `suggestedNextMoves`: the items from the **Suggested next moves** section. Each item must have `"text"` (one actionable step sentence, 20 words or fewer). Optionally include `"description"` (one supporting sentence explaining why this move matters) and `"actionLabel"` + `"actionPrompt"` (a short chip label and the follow-up prompt it sends). Use the same template patterns as `needsAttention` — substitute real customer names, amounts, and periods from the synthesized data. Omit `actionLabel`/`actionPrompt` if no clear immediate QBO follow-up applies.

## Style requirements
- Lead with the answer, not the report list.
- Use exact numbers from tool outputs when available; otherwise say the metric was not available.
- Round large dollar values for readability, but preserve important precision for ratios and percentages.
- Format date ranges as "Month D to Month D, YYYY" (e.g. "Apr 1 to Jun 30, 2026") — no dashes, no ISO dates. Use this style in the `period` field.
- Tie every flag to a concrete financial metric or report result.
- If A/R is negative, avoid labeling it as "overdue A/R" in the key numbers. Explain it as an accounting cleanup, credit, overpayment, or payment-application signal unless positive overdue receivables are also present.
- Always include Sales by Product/Service as one of the suggested next moves so the user can drill into the product, service, or item-level drivers behind the headline sales movement.
- Avoid accounting jargon unless it is paired with a plain-language explanation.
- Do not provide tax, legal, investment, or lending advice. Frame recommendations as operational next steps.