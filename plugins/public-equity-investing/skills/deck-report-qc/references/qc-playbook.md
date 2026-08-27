# QC Playbook

Use this playbook to review public-equity-investing decks, reports, memos, tearsheets, senior review materials, research notes, and committee packs.

## 1. Number consistency

Review all recurring numbers across the deliverable:
- revenue, EBITDA, EBIT, EBITDA margin, gross margin, ARR, NRR, FCF, capex, working capital, cash, debt, net debt, enterprise value, equity value, share price, fully diluted shares, EPS, book value
- growth rates, CAGR, bps movement, multiple, leverage, P/E, EV/EBITDA, P/B, NPV, NAV, price target, benchmark weight, ETF/index exposure, probability-weighted value
- public-equity market data: price, market cap, EV, multiples, estimates, consensus, short interest, volume, rate, FX, commodity, index level, spread
- Credit Markets handoff / equity-risk signal data: maturity wall, CDS/spread signal, ratings pressure, refinancing risk, liquidity runway, tender/exchange terms, event spread, probability-weighted value. Route credit-security analysis to Credit Markets.

Flag issues when:
- the same metric / company / period / unit appears with different values
- a summary page conflicts with a detailed page
- a chart value conflicts with a table or bullet
- a model-output number lacks a model/source reference
- the sign convention changes without explanation
- the denominator changes without explanation, e.g. margin on revenue vs gross revenue, leverage on reported EBITDA vs adjusted EBITDA

## 2. Unit and period discipline

Every data-heavy page should make unit and period clear:
- currency: USD, EUR, GBP, local currency, constant currency, nominal/real
- scale: dollars, thousands, millions, billions
- rate unit: percent, basis points, yield, spread
- multiple unit: x, turns, EV/EBITDA, P/E, P/B, debt/EBITDA
- time basis: fiscal year, calendar year, quarter, LTM, NTM, run-rate, annualized, as-of date
- scenario: base, downside, upside, company guidance, Street/consensus case, internal case, Credit Markets handoff case, event case

Common errors:
- `$m` on one page and `$mm` on another
- bps change described as a percent change
- FY and CY estimates mixed in the same table
- reported EBITDA, adjusted EBITDA, Street EBITDA, and internal-case EBITDA used interchangeably
- market data stale relative to the date of the report
- margin deltas shown as percentages instead of percentage points

## 3. Source and footnote hygiene

A page with material facts or market data should identify:
- source name
- source date or as-of date
- period covered
- whether the data is company-reported, regulator-filed, broker/consensus, market-data provider, management-provided, company-provided non-filed, model-derived, or internal estimate
- important caveats such as unaudited, preliminary, pro forma, non-GAAP, adjusted, constant-currency, annualized, or management estimate

Flag pages where:
- data-heavy content has no source footnote
- source footnote says only `company filings` without period/form if the point is specific
- market-sensitive data lacks an as-of date
- company/management materials are used as fact without verification language
- consensus or broker data is cited without date/provider
- source footnotes do not match the figures shown

## 4. Chart-to-narrative consistency

For every chart, inspect:
- chart title and subtitle
- x-axis and y-axis labels
- units, scale, and period
- legend and series names
- source and as-of date
- visible values and labels
- narrative bullet immediately above/below the chart

Flag if:
- chart title overstates the chart conclusion
- bullet says improvement but chart shows decline or mixed performance
- axis scale truncation exaggerates movement without disclosure
- chart uses bps but bullet uses percent, or vice versa
- chart data labels do not match the source table/model
- chart period does not match text period
- chart source is missing, stale, or inconsistent with surrounding sources

## 5. Narrative and thesis consistency

Compare:
- executive summary vs section pages
- page titles vs chart findings
- investment merits vs risks
- valuation conclusion vs model output
- recommendation vs issue log/open evidence gaps
- equity thesis vs downside, solvency, or liquidity-risk evidence
- macro conclusion vs monitoring signals

Flag contradictions, unsupported superlatives, or claims that require qualification. Examples:
- `clear market leader` without market share support
- `resilient through-cycle margins` when margins declined in downturn years
- `balance sheet risk is manageable` without liquidity, maturity, or refinancing support
- `attractive valuation` when implied valuation is above peers without explanation

## 6. Formatting and presentation polish

Check:
- page numbers, headers, footers, section dividers
- consistent title capitalization and punctuation
- font size, font family, line spacing, alignment, and indentation
- table headers, units rows, decimal precision, subtotal/total formatting
- colors, legends, callout boxes, and negative-number formatting
- footnote size, order, and source style
- orphan bullets, cut-off labels, overlapping shapes, low-resolution images

Formatting issues should not be inflated into investment-substance issues unless they obscure the analysis or create confusion.

## 7. Accessibility and readability checks

For decks circulated broadly, also flag:
- missing or duplicate slide titles
- unreadable small fonts
- low contrast or color-only encoding
- charts without clear labels
- complex tables with no obvious row/column headers
- images used as the sole carrier of important text

Do not over-focus on accessibility for internal working drafts unless the user asks. However, flag readability problems that impede senior review.
