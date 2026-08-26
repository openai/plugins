---
name: industry-benchmark
description: compare a QuickBooks business or provided metric against industry peers using Intuit QuickBooks benchmarking tools. Use when the user asks how they compare to similar businesses, whether margins are healthy, whether spending is too high, what profit should look like for an industry and region, or wants regional and national peer context.
---

# Industry Benchmark

## Goal
Turn a peer-comparison question into a concise benchmark briefing by first confirming the user's benchmark choices, then using the relevant Intuit QuickBooks app benchmarking tool, and explaining whether the business is ahead, behind, or in line with regional and national peers.

## Pre-flight input
Do not immediately execute benchmarking with defaults. Start by asking the user for the inputs needed to run the benchmark before calling any Intuit QuickBooks tools.

Ask for these inputs in one concise message:

1. Benchmark mode:
   - Connected QuickBooks company: use the company's QuickBooks profile and financial data.
   - Provided actuals: use a metric value the user provides, such as annual profit, revenue, or expenses.
   - Industry research: benchmark an industry and region without the user's company data.
2. Metric:
   - Profit, revenue/income, expenses, or profit margin (%).
   - Default to profit if the user does not choose.
3. Aggregation period:
   - Yearly, monthly, or quarterly.
   - Default to yearly if the user does not choose.
4. Industry:
   - For connected QuickBooks company mode, use the company profile industry when available. If only the NAICS code is known at this preflight step, refer to it as the company's QuickBooks industry category instead of displaying the code.
   - For provided actuals or industry research, ask for the industry and, when known, the NAICS code.
   - If comparing multiple industries, limit to 5 total industries.
5. Location:
   - Ask for state, and county when the user wants a more local comparison.
   - Use a two-letter state code when calling tools.
6. Company value:
   - Required only for Provided actuals mode.
   - For profit: ask for the profit value and also ask for revenue (to show profit margin alongside profit). Revenue is optional — if the user cannot provide it, proceed with profit only.
   - For revenue, expenses, or income: ask for a single dollar value.
   - For profit margin: ask for both the profit value and the revenue value separately.
   - Not required for Connected QuickBooks company mode or Industry research mode.

Do not mention PDF generation in the initial prompt.

## Default assumptions
- Treat "my business", "my company", and "our business" as the connected QuickBooks company.
- Default metric is profit.
- Default aggregation period is yearly.
- For research or new-business questions, use a metric value of 0 and frame the result as expected peer context rather than company performance.
- Use the user's stated industry and location when available. If a required industry, NAICS code, state, or metric value cannot be inferred safely, ask a short clarification.
- Keep the answer plain-language, business-owner friendly, and focused on decision usefulness.

## Tool sequence for QuickBooks benchmark data
Use the tools exposed by the Intuit QuickBooks app connector.

Always use the text-only variants of the Intuit QuickBooks benchmarking tools listed below. These return plain text/markdown so you can synthesize the benchmark briefing yourself without rendering interactive widgets.

After the user confirms the plan:

1. For Connected QuickBooks company mode:
   - Call the Intuit QuickBooks `company_info` tool first to establish the QuickBooks connection.
   - Call `benchmarking_quickbooks_account_text` for the selected metric and aggregation period.
   - When the selected metric is `profit`, also make a second call to `benchmarking_quickbooks_account_text` with `metricType=margin` to fetch peer margin data. Include the margin values as a row in `keyNumbers`.
   - If the company profile is missing required industry, location, or NAICS information and the tool asks for it, collect only the missing information and continue.
2. For Provided actuals mode:
   - Call `benchmarking_against_industry_text` with the user's metric value, metric type, aggregation period, industry, NAICS code, company name, and location.
   - When metricType is `margin`, pass `profitValue` and `revenueValue` instead of `metricValue`.
   - When metricType is `profit` and the user has provided both profit and revenue values, make a second call to `benchmarking_against_industry_text` with `metricType=margin`, `profitValue`, and `revenueValue` to fetch peer margin data. Include the margin values as a row in `keyNumbers`.
   - Do not call QuickBooks account benchmark tools when the user already provided the company metric value.
3. For Industry research mode:
   - Call `benchmarking_against_industry_text` with metric value 0, metric type, aggregation period, industry, NAICS code, and location.
   - Use a descriptive company name such as "Industry Research" or "New Restaurant" when the tool requires one.
4. If a tool is unavailable, returns incomplete data, appears to provide only a UI without enough structured values, or authentication/profile setup blocks the benchmark, explain the gap briefly and continue with the information that succeeded. Do not invent missing numbers.

## Parameter mapping
- "How do I compare to other businesses like mine?" -> Connected QuickBooks company mode unless the user provides their own metric value.
- "Are my margins healthy?" -> Use metricType `margin`; for Provided actuals mode pass `profitValue` and `revenueValue`; for Connected QuickBooks company mode the tool fetches both automatically.
- "Am I spending too much?" -> Benchmark expenses.
- "What should my profit look like for a restaurant in Texas?" -> Industry research mode; metric type profit; industry Restaurants; state TX; metric value 0.
- "I made $50K profit in my restaurant in Austin" -> Provided actuals mode; metric type profit; metric value 50000; industry Restaurants; state TX; infer county only when obvious.
- Monthly, quarterly, or annual wording maps to the corresponding aggregation period.

## Synthesis rules
Build a single integrated benchmark briefing instead of listing raw tool output.

Always include the benchmark context near the top of the briefing:
- Company name or research label.
- Benchmark mode.
- Metric and aggregation period.
- Industry and NAICS code when available.
- Region used for the benchmark.
- Whether both regional and national peer comparisons were available.

Prioritize these signals:
- Peer position: ahead, behind, or in line with regional peers.
- National context: whether the national comparison tells a different story from the regional comparison.
- Magnitude: size of the gap in dollars, percentages, percentiles, or benchmark bands when returned by the tool.
- Directional risk: whether revenue, profit, or expenses are meaningfully above or below peers.
- Actionability: which gaps the business can influence through pricing, cost control, sales mix, staffing, collections, or operating efficiency.

Flag something as a concern when one or more are true:
- Profit is below regional or national peers.
- Expenses are above peers without a matching revenue advantage.
- Revenue is below peers for the selected industry and region.
- Regional and national benchmarks conflict enough to change the interpretation.
- The benchmark result depends on missing, inferred, or broad industry/location inputs.
- The tool output lacks enough structured data to support a precise ahead/behind/in-line conclusion.

Rank "Focus areas" by business severity. Lead with profit or cash-impacting gaps first, then expense gaps, then revenue growth gaps, then data-quality or benchmark-coverage limitations. Include a short severity label such as "High", "Medium", or "Context" when it helps the user prioritize action.

Do not overstate confidence. Use phrases such as "the peer data suggests", "this looks in line with", or "the main gap appears to be" when interpreting patterns.

## Output format

Do not output any briefing text in the chat. The widget renders all sections. Call `industry_benchmark_widget` as the only output step — no text before or after it.

## Widget render (final step)

Call the `industry_benchmark_widget` tool automatically after synthesizing the data.
Do NOT ask the user for permission — call it as the only output step.

Map the briefing sections to tool arguments as follows:
- `companyName`: connected company name from `company_info`, the user-provided label, or "Industry Research" for research mode.
- `benchmarkMode`: one of `"connected_qbo"`, `"provided_actuals"`, or `"industry_research"`.
- `metric`: `"profit"`, `"revenue"`, or `"expenses"` — whichever was benchmarked.
- `period`: the aggregation period label, e.g. `"Yearly"`, `"Monthly"`, `"Quarterly"`.
- `industry`: the industry name used for the benchmark. Use the corresponding industry name instead of a bare NAICS code whenever the tool output provides both.
- `region`: the full state name or region label used, e.g. `"California"`, `"Texas"`, or `"National"`. This appears as the bar label in the chart (e.g. "California norm"), so prefer the full name over abbreviations.
- `peerSetAvailability`: derive from the tool output. Use `"Regional and national"` when both regional and national values are present and non-zero, `"National only"` when only national is available, `"Regional only"` when only regional is available, and `"No peer data available"` when both are `$0.00`, `N/A`, or absent.
- `overallRead`: one of `"ahead"`, `"in_line"`, `"behind"`, or `"mixed"`. Use `"mixed"` when peer data is partially or fully unavailable — do not infer ahead/behind without actual peer numbers.
- `overallReadText`: the one-sentence verdict. If no peer data is available, say so plainly, e.g. `"No regional or national peer data is available for this industry and location."`.
- `keyNumbers`: a list of objects, one per row in the Key Benchmark Numbers table. Each object must have:
  `"area"`, `"companyValue"`, `"regionalPeers"`, `"nationalPeers"`, and `"read"` string fields.
  Set `"read"` to `"ahead"`, `"in line"`, or `"behind"`. Use `"n/a"` when no peer data is available for that row — do not guess.
- `whereAhead`: the bullets from the **Where you're ahead** section (list of strings). Use an empty list `[]` if no peer data is available.
- `focusAreas`: the bullets from the **Focus areas** section. Each item must have `"severity"` (`"High"`, `"Medium"`, or `"Context"`) and `"text"`. Always add `"actionLabel"` and `"actionPrompt"` for High and Medium items — e.g. `"actionLabel": "Analyze expenses"`, `"actionPrompt": "Break down my operating expenses vs industry peers"`. These render as clickable chips. When peer data is unavailable, include a single `"Context"` item noting the data gap (no action chip needed).
- `whatGapsMean`: the bullets from the **What the gaps mean** section (list of strings).
- `suggestedNextMoves`: the items from the **Suggested next moves** section. Always use objects with `"text"` (required), `"actionLabel"` (short chip label, e.g. `"View Sales report"`), and `"actionPrompt"` (the follow-up message to send, e.g. `"Show me my Sales by Product report"`). Every move that maps to a follow-up question or report must have an action chip. Plain strings are allowed only when no logical follow-up action exists.
- `naicsCode`: NAICS code if available (omit if not).
- `chartData`: (**single-industry mode only — `connected_qbo` and `provided_actuals`**) raw numbers for the primary bar chart. Extract the actual dollar/number figures from the text tool output — not formatted strings. Pass: `{ "companyValue": <number>, "regionalPeers": <number or null>, "nationalPeers": <number or null>, "metricLabel": "<period> <metric>", "metricFormat": "percent" | "currency" }`. Set `metricFormat` to `"percent"` when metricType is `margin`, otherwise omit it. Set `regionalPeers` and `nationalPeers` to `null` when the tool shows `$0.00`, `N/A`, or no data — never pass `0`. Omit `chartData` entirely for `industry_research` mode, multi-industry comparisons, or when the company value itself is not available.
- `secondaryChartData`: (**optional, single-industry mode only**) omit — the backend populates this automatically from `keyNumbers` when margin data is present.
- `multiIndustryChartData`: (**multi-industry mode only**) ranking table and carousel data. Extract the per-industry regional averages from the text tool output. Pass: `{ "industries": [{ "industry": "<name>", "naicsCode": "<code>", "regionalAverage": <number or null> }, ...], "metricLabel": "<period> <metric>", "location": "<full state name>", "userMetricValue": <number or null> }`. List industries ranked by `regionalAverage` descending (highest first). Set `regionalAverage` to `null` for industries that returned `$0.00` or `N/A`. Set `userMetricValue` to the company's raw metric value for `connected_qbo` or `provided_actuals` mode, or `null` for `industry_research`. Omit for single-industry comparisons.

## Style requirements
- Lead with the ahead/in-line/behind answer, not the tool list.
- Use exact numbers from tool outputs when available; otherwise say the metric was not available.
- Round large dollar values for readability, but preserve important precision for percentages, percentiles, and ratios.
- Tie every interpretation to a concrete benchmark value, range, percentile, or tool-returned signal.
- Distinguish regional peers from national peers whenever both are available.
- Always include Sales by Product/Service as one of the suggested next moves so the user can drill into item-level drivers behind benchmark gaps.
- Avoid accounting jargon unless it is paired with a plain-language explanation.
- Do not provide tax, legal, investment, lending, or financing advice. Frame recommendations as operational next steps.
