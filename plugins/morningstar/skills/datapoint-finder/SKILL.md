---
name: datapoint-finder
description: Finds official Morningstar datapoint names using topic-organized buckets. Use when the user asks to find, browse, or name a datapoint — e.g. "what's the datapoint for expense ratio", "find the datapoint name for Sharpe ratio", or "list datapoints for ESG".
metadata:
  author: Morningstar
  version: 1.0.0
  mcp-server: morningstar-mcp
compatibility: Designed for use with the Morningstar MCP server.
---

# Datapoint Finder

Finds official Morningstar datapoint names from topic-organized buckets.

The buckets under `references/buckets/` list datapoint names by topic — use them to find
candidate names.

## Workflow

Open the matching bucket(s) below (up to 3) and build a candidate name list — bucket names
are a starting point, add your own reasonable guesses too.

## Intent → bucket map

### Performance & Returns
| If the user is asking about… | Load bucket |
|---|---|
| Total/trailing/annual/calendar/daily/monthly **return**, YTD/1Y/3Y/5Y/10Y return, return index, growth of $10K | `perf-trailing-periodic` |
| Percentile **rank in category**, % rank vs peers, quartile, # investments in category | `perf-return-rankings` |
| Beta, standard deviation/volatility, R-squared, tracking error, up/down capture, batting average, bear-market rank, strategic beta | `perf-risk-metrics` |
| Alpha, Sharpe, Sortino, information ratio (risk-adjusted) | `perf-risk-adjusted` |

### Morningstar Ratings
| If the user is asking about… | Load bucket |
|---|---|
| Star rating, risk rating, return rating, "X-star" | `rating-star` |
| Medalist Rating, pillars (Parent/People/Process/Price/Performance), fair value per share, brand tenure/retention | `rating-medalist` |
| Quantitative rating, quant fair value, fair value uncertainty | `rating-quant-equity` |
| ESG risk rating / sustainability rating of a fund | `rating-sustainability` |
~~
### Portfolio Analysis
| If the user is asking about… | Load bucket |
|---|---|
| Country/region exposure, geographic breakdown, US vs non-US | `pa-geographic-exposure` |
| Sector/industry weights (equity econ sector, super sector) | `pa-sector-industry` |
| Asset allocation (stock/bond/cash/other %, long/short) | `pa-asset-allocation` |
| Style box, growth/value factors, sustainability/style tilts | `pa-style-factor` |
| Portfolio avg market cap, portfolio P/E·P/B·P/S, avg moat, turnover, duration, credit quality | `pa-statistics` |
| # of holdings, # bond/stock holdings, top-10 weight | `pa-holdings` |
| Target-date **glide path** (allocation by years-to-target), glide path type / landing point | `pa-glide-path` |

### Price & Distribution & Flows
| If the user is asking about… | Load bucket |
|---|---|
| Price, last close, NAV, market price, 52-wk high/low, premium/discount, AUV | `price-prices` |
| Yield (12-mo/SEC/7-day), dividends paid, capital gains, ROC, distributions | `price-distributions` |
| Trading volume, spread, days traded | `price-trading-activity` |
| Estimated net flows | `price-fund-flows` |
| Fund size, AUM, net assets, tier-level/vehicle assets | `price-aum` |

### Expense & Fee
| If the user is asking about… | Load bucket |
|---|---|
| Expense ratio (net/gross/adjusted), management/admin/custodian/advisor fees, ongoing charge | `fee-management-ongoing` |
| Transaction/trading costs, spreads, RG97 T&O costs, borrowing costs | `fee-transaction-trading` |
| Front/deferred load, exit/switching/contribution fee, sales charge | `fee-entry-exit-load` |
| Performance fee, hurdle rate, high-water mark, crystallisation | `fee-performance-based` |
| 12b-1 / distribution & sales / revenue-sharing fee, no-load flag | `fee-distribution-sales` |

### Corporate Financials
| If the user is asking about… | Load bucket |
|---|---|
| A **stock's** P/E·P/B·P/S, ROE/ROA/ROIC, margins, debt/equity, growth, economic moat, growth grade, market cap, quick ratio, tax rate | `cf-financial-ratios-metrics` |
| Income statement: revenue, cost of revenue, gross/operating profit, EBITDA, EPS, interest/tax, net income | `cf-income-statement` |
| Balance sheet: total assets/liabilities/equity, PP&E, goodwill, debt, inventory, receivables/payables, working capital | `cf-balance-sheet` |
| Cash-flow statement: operating/investing/financing cash flows, capex, dividends paid, changes in working capital | `cf-cash-flow` |
| Shares outstanding (basic/diluted/weighted-avg), share counts | `cf-share-data` |

### ESG & Sustainability
| If the user is asking about… | Load bucket |
|---|---|
| EU SFDR / EU Taxonomy disclosure & regulatory flags | `esg-eu-taxonomy` |

### Ownership
| If the user is asking about… | Load bucket |
|---|---|
| Number of shareholders, trustee / ownership facts | `own-statistics` |

### Reference Data & Fund Information
| If the user is asking about… | Load bucket |
|---|---|
| Currency, domicile, inception, status, minimums, flags (index/active, REIT, UCITS), tax transparency, glide-path/data-ready | `ref-operations` |
| Name, ticker, ISIN/CUSIP/WKN, FundId/SecId/CompanyId, share class, fund/branding name | `ref-identification` |
| Manager name/tenure/ownership/education, firm assets, advisor/custodian | `ref-management-org` |
| Morningstar Category / Global Category / theme, investment type, a stock's sector/industry | `ref-classification` |
| Benchmark/index, prospectus benchmark, index family, index selection/weighting | `ref-benchmark-index` |

## Tie-break rules for overlapping terms

- **"market cap"** → a **stock** `ST159` (`cf-financial-ratios-metrics`); portfolio average
  `HS03W` (`pa-statistics`); size breakdown lives in `pa-style-factor`.
- **"economic moat"** → a **stock** `LT181` (`cf-financial-ratios-metrics`); portfolio
  average `HS0D1` (`pa-statistics`).
- **"fair value"** → Morningstar Fair Value per Share `ST202` and Price/Fair Value `OS603`
  (`rating-medalist`); Quantitative Fair Value `QV009` / Fair Value Uncertainty `ST201`
  (`rating-quant-equity`).
- **"P/E", "P/B", "P/S"** → a **stock** (`ST412`/`ST408`/`ST415`) in
  `cf-financial-ratios-metrics`; **portfolio** (TTM, long, e.g. `HS05X`) in `pa-statistics`.
- **"yield" / "dividend yield"** → a **fund** → 12 Mo / SEC / 7-Day Yield in
  `price-distributions`; distributions paid also `price-distributions`.
- **"sector"** → **fund** weights → `pa-sector-industry`; **stock** classification →
  `ref-classification`.
- **"volume"** → trading volume/spread → `price-trading-activity`, not `price-prices`.
- **"expense ratio" / "fee level"** → `fee-management-ongoing`.
- **"rating"** → 1–5 star → `rating-star`; Medalist (Gold/Silver/Bronze) → `rating-medalist`;
  quant → `rating-quant-equity`; ESG/sustainability → `rating-sustainability`.
- **"base currency"** → Base Currency `LS05M` (`ref-operations`), never Minimum Investment.
