---
name: comp-sheet
description: Build an industry comp sheet Excel model with deep operational KPIs
---

Build a multi-company industry comp sheet Excel model for the company named in the user's request. If no ticker or company is provided, ask for one before proceeding.

This produces an interactive `.xlsx` workbook — the kind of comp sheet every analyst on a coverage team maintains. Multi-company, multi-tab, with deep operational KPIs alongside standard financials.

**Before starting, read `../data-access.md` for data access methods and `../design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

Follow these steps:

## 1. Company & Peer Setup

Look up the target company by ticker using `discover_companies`. Capture `company_id`, `latest_calendar_quarter` (anchor for all period calculations — see `../data-access.md` Section 1.5), and `latest_fiscal_quarter`. Note the firm name for report attribution (default: "Daloopa") — see `../data-access.md` Section 4.5.

Then identify 6-10 comparable companies using the same logic as the comps skill:
- **Direct competitors** in the same market
- **Business model peers** (similar revenue model)
- **Size peers** (similar market cap range)
- **Growth profile peers** (similar growth rate)

Look up all peer company_ids via Daloopa. If a peer isn't available in Daloopa, include it with market data only and note the limitation.

List the full peer group with brief justification for each.

## 2. Deep Data Gathering

For each company (target + all peers), pull from Daloopa:

**Calculate 8 quarters backward from `latest_calendar_quarter`. Pull financials:**
- Revenue, Gross Profit, Operating Income, Net Income, Diluted EPS
- Operating Cash Flow, Capital Expenditures, D&A
- Free Cash Flow (compute as OCF - CapEx)
- R&D Expense, SG&A (where available)

**Segment revenue breakdown** (all available segments, 8 quarters)

**Company-specific operational KPIs** — use the 9-sector taxonomy to know what to search for:
- **SaaS/Cloud**: ARR, net revenue retention, RPO/cRPO, customers >$100K, cloud gross margin
- **Consumer Tech**: DAU/MAU, ARPU, engagement metrics, installed base, paid subscribers
- **E-commerce/Marketplace**: GMV, take rate, active buyers/sellers, order frequency
- **Retail**: same-store sales, store count, average ticket, transactions
- **Telecom/Media**: subscribers, churn, ARPU, content spend
- **Hardware**: units shipped, ASP, attach rate, installed base
- **Financial Services**: AUM, NIM, loan growth, credit quality metrics, fee income ratio
- **Pharma/Biotech**: pipeline stage, patient starts, scripts, market share
- **Industrials/Energy**: backlog, book-to-bill, utilization, production volumes, reserves

**Stock prices & valuation multiples:**
Use `get_stock_prices` (see `../data-access.md` Section 1.7) to pull prices for ALL companies in a single batch call. Get:
- Current price: `dates` = 3 most recent calendar days for all company_ids
- Quarter-end prices: `dates` = quarter-end dates matching the financial periods (for historical multiples)

Then compute valuation metrics by combining stock prices with Daloopa fundamentals:
- **Market Cap** = Close price × Diluted shares outstanding
- **Enterprise Value** = Market Cap + Total Debt - Cash
- **P/E (trailing)** = Market Cap / Net Income (trailing 4Q)
- **EV/EBITDA** = EV / EBITDA (trailing 4Q)
- **P/S** = Market Cap / Revenue (trailing 4Q)
- **P/B** = Market Cap / Total Equity
- **EV/FCF** = EV / Free Cash Flow (trailing 4Q)
- **FCF Yield** = FCF (trailing 4Q) / Market Cap
- **Dividend Yield** = Dividends Paid (trailing 4Q) / Market Cap

For beta, use web search (see `../data-access.md` Section 2). For forward multiples, use consensus estimates if available (Section 3).

## 3. KPI Discovery & Mapping

After pulling data, build the KPI mapping:
- Which KPIs are available for which companies? Build a coverage matrix.
- Group KPIs into categories:
  - **Segment Revenue**: product/service line breakdowns
  - **Growth KPIs**: subscriber growth, unit growth, same-store sales growth
  - **Unit Economics**: ARPU, ASP, take rate, retention
  - **Efficiency**: R&D % of revenue, SBC % of revenue, CapEx % of revenue
  - **Engagement**: DAU/MAU, retention, churn
- Flag KPIs that are comparable across peers vs company-specific

## 4. Compute Derived Metrics

For each company, calculate:

**Margins:**
- Gross Margin, Operating Margin, Net Margin, FCF Margin (each quarter)

**Growth rates:**
- Revenue YoY, EPS YoY, segment revenue YoY (each quarter where year-ago data exists)

**Capital metrics:**
- Net Debt (Total Debt - Cash)
- Net Debt/EBITDA
- Shareholder Yield (Buybacks + Dividends) / Market Cap

**Historical multiples (from quarter-end prices pulled in Section 2):**
- Compute P/E, EV/EBITDA, P/S, EV/FCF at each quarter-end to show how multiples have trended
- This lets the reader see whether the current multiple is elevated or depressed vs. the company's own history

**Implied valuation:**
- For each valuation methodology (P/E, EV/EBITDA, P/S, EV/FCF):
  - Peer median multiple × target metric = implied value
  - Convert to implied share price
- Compute median implied price across methodologies

## 5. Build Excel Workbook

Generate the Excel workbook directly as a local `.xlsx` file. For Codex, prefer bundled spreadsheet tooling or Python/openpyxl when available.

The workbook must contain 8 tabs with the following structure:

### Tab 1: Comp Summary
One-page overview with all companies side-by-side:
- Company name, ticker, price, market cap
- All valuation multiples (P/E, EV/EBITDA, P/S, P/B, EV/FCF, div yield)
- Latest quarter revenue, EBITDA, net income
- Growth rates (revenue YoY, EPS YoY)
- Key margins (gross, operating, net, FCF)
- Implied valuation for target (median across methodologies)
- Premium/discount vs peers

### Tab 2: Revenue Drivers
Unit economics decomposition per company (trailing 4 quarters):
- Total revenue (4Q sum)
- Segment revenue breakdown (% of total)
- Key unit economics: units × ASP, or subscribers × ARPU, etc.
- Growth trajectory by segment

### Tab 3: Operating KPIs
Cross-company KPI comparison matrix:
- Rows = KPIs (grouped by category from step 3)
- Columns = companies
- Show latest quarter value + YoY change where applicable
- Highlight cells where data is unavailable (sparse matrix)

### Tab 4: Financial Summary
Side-by-side income statements (trailing 4 quarters):
- Revenue, COGS, Gross Profit
- R&D, SG&A, Operating Income
- Interest, Tax, Net Income
- Diluted EPS
- Compute 4Q sums for each line item

### Tab 5: Growth & Margins
Trend analysis (up to 8 quarters):
- Revenue growth YoY (%)
- EPS growth YoY (%)
- Gross margin (%)
- Operating margin (%)
- Net margin (%)
- FCF margin (%)
- Show trends across all periods for each company

### Tab 6: Valuation Detail
Implied prices by methodology:
- P/E implied (peer median P/E × target EPS)
- EV/EBITDA implied
- P/S implied
- EV/FCF implied
- Median implied price
- Current price
- Premium/discount (%)

### Tab 7: Balance Sheet & Capital
Leverage and capital returns:
- Total Debt, Cash, Net Debt
- Net Debt/EBITDA
- Trailing 4Q: OCF, CapEx, FCF
- FCF Yield
- Shareholder Yield (buybacks + dividends)

### Tab 8: Raw Data
Full quarterly appendix for each company:
- All 8 quarters of financial data
- All KPIs by quarter
- All growth rates and margins by quarter
- Complete data backing the summary tabs

**Styling requirements:**
- Apply the design system color palette (Navy #1B2A4A headers, Steel Blue #4A6FA5 accents)
- Number formatting per `../design-system.md` conventions
- Bold headers, freeze panes on all tabs
- Conditional formatting: green for positive growth, red for negative
- Auto-adjust column widths

The workbook generation should:
1. Use the best available spreadsheet-generation library
2. Construct all 8 worksheets programmatically
3. Apply styling (bold headers, number formats, colors)
4. Generate the `.xlsx` file
5. Save the workbook as `reports/{TARGET_TICKER}_comp_sheet_{DATE}.xlsx`

## 6. Output Summary

After generating the Excel workbook, provide a concise summary highlighting:

**Target positioning vs peers**:
- Where does it rank on growth, margins, and valuation?
- Quartile positioning across key metrics

**Most differentiated KPIs**:
- Which operational metrics set the target apart (positive or negative)?
- Notable outliers in the KPI matrix

**Implied valuation range**:
- What does the peer group suggest the stock is worth?
- Premium/discount vs current price
- Which methodology drives the highest/lowest implied value?

**Key risk**:
- What's the biggest vulnerability the comp sheet reveals (e.g., premium valuation with decelerating KPIs, margins below peers, concentration risk)?

All financial figures in the summary must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})
