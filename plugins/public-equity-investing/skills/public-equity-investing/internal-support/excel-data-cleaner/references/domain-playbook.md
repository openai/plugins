# Public Equity Investing Domain Playbook

Use this reference to adapt cleaning, validation, and formatting to the user's Public Equity Investing context. This skill can clean arbitrary tables when explicitly invoked, but its default routing and examples should stay focused on public equity, ETF/index, event-driven, market-data, portfolio/risk, consensus, and issuer-reporting workflows.

## Domain Inference Signals

Infer domain from user language, sheet names, headers, values, and expected output.

- Financial statements / issuer reporting: filing, release, supplement, segment, revenue, COGS, EBITDA, EPS, FCF, capex, debt, cash, share count, fiscal year, quarter, month, guidance, actual, estimate, forecast.
- Investing / markets: ticker, CUSIP, ISIN, SEDOL, security, issuer, portfolio, NAV, return, yield, spread, basis points, benchmark, price, holdings, exposure, market value.
- Credit Markets handoff / equity-risk signal: bond, loan, coupon, maturity, rating, spread, yield, debt, liquidity, covenant, collateral, priority, recovery, restructuring, exchange offer, tender. Use this only to route out or preserve equity-risk evidence.
- Consensus / provider exports: provider, estimate date, consensus, actual, revision, mean, median, high, low, fiscal period, metric, broker, timestamp.
- Portfolio / risk: position, weight, exposure, P&L, gross, net, factor, beta, VaR, sector, geography, benchmark, hedge tag.
- Event-driven / special situations: deal, consideration, unaffected price, spread, probability, closing date, break price, regulatory approval, tender, merger, spin, index event.

If multiple domains are present, clean to the most downstream purpose. Example: a provider export used in an earnings model should preserve provider metadata, fiscal periods, actual/estimate labels, and source timestamps even if the raw table looks like a generic spreadsheet.

## Financial Statements / Issuer Reporting

### Preserve

- entity, issuer, segment, geography, product line, account/metric name.
- period, fiscal year, quarter, month, actual/estimate/forecast/guidance labels.
- currency, units, source, source date, fiscal calendar, sign convention.
- reported vs adjusted vs non-GAAP labels.

### Cleaning judgment

- Do not flip signs unless the source sign convention is explicit.
- Do not combine actual, estimate, forecast, and guidance without a scenario/status column.
- Treat period strings such as `FY26 Q1`, `Q1 FY26`, and `2026-Q1` as labels unless fiscal calendar is known.
- Preserve rollup rows separately from detail rows when the table mixes both.

### Checks

- Missing amount where metric/period exists.
- Multiple currencies without currency column.
- Period labels inconsistent.
- Duplicate issuer + metric + period + scenario rows.
- Totals embedded in detail data.

## Investing / Markets

### Preserve

- ticker, CUSIP, ISIN, SEDOL, issuer/security name, portfolio/account, broker/custodian.
- trade date, settle date, pricing date, benchmark, metric units, currency.
- basis points vs percent vs decimal return.

### Cleaning judgment

- Treat security identifiers as text.
- Do not infer ticker-to-company mappings without a trusted source.
- Do not convert return units unless unit labels are clear.
- Do not aggregate positions across accounts, currencies, share classes, or dates unless requested.

### Checks

- Missing security ID/ticker/date.
- Mixed currencies or return units.
- Duplicate portfolio + security + date rows with conflicting values.
- Negative prices, impossible yields, stale pricing dates.

## Credit Markets handoff / equity-risk signal

### Preserve for handoff

- issuer, borrower/obligor, security, tranche, CUSIP/ISIN, coupon, maturity, seniority, collateral, guarantor, rating.
- price, yield, spread, OID, call protection, recovery assumption, debt amount, liquidity metric, covenant definition.
- source document, pricing timestamp, filing period, and legal document reference.

These fields are not local analysis ownership. Preserve them so Credit Markets can continue the work, or keep only the equity read-through if the downstream decision is common equity.

### Cleaning judgment

- Keep legal/covenant terms as text and route interpretation to Credit Markets.
- Do not merge debt instruments by issuer alone; tranche and maturity matter for handoff integrity.
- Preserve restricted vs unrestricted cash and secured vs unsecured debt labels when they affect common-equity risk.

### Checks

- Missing maturity, coupon, debt balance, price/yield/spread, or source timestamp where material to equity downside or Credit Markets handoff.
- Mixed price formats, yield formats, or spread units.
- Duplicate instrument IDs with conflicting economics.
- Covenant or liquidity metric missing definition.
- Add `route_to_credit_markets` when the requested output is credit analysis, debt-security selection, covenant analysis, recovery, or restructuring.

## Consensus / Provider Exports

### Preserve

- provider, estimate date, retrieval timestamp, broker/count metadata, mean/median/high/low, actual/estimate flag.
- fiscal period, calendarized period if available, metric definition, currency, units.

### Cleaning judgment

- Do not blend providers without labeling provider and as-of date.
- Keep actuals and estimates separate.
- Do not silently overwrite consensus with company guidance or analyst assumptions.

### Checks

- Missing provider, estimate date, fiscal period, or metric definition.
- Actual and estimate rows mixed without status.
- Multiple estimate dates in one table without a clear latest flag.

## Portfolio / Risk

### Preserve

- portfolio/account, position date, security ID, issuer, strategy, sector, region, benchmark, hedge tag.
- market value, exposure, weight, P&L, return, beta, factor exposure, VaR, liquidity bucket.

### Cleaning judgment

- Do not net long and short rows unless the user requests net exposure.
- Preserve currency, fund/account, and position-date grain.
- Do not roll up by ticker if multiple share classes, currencies, or instruments exist.

### Checks

- Weights do not sum where expected.
- Missing price/date/security ID.
- Long/short sign convention unclear.
- Mixed currencies without FX treatment.

## Event-Driven / Special Situations

### Preserve

- target/acquirer/issuer, security, consideration, unaffected price, current price, spread, probability, expected close, break price.
- regulatory, shareholder, court, financing, or tender milestones.
- source date and exact document/source behind deal terms.

### Cleaning judgment

- Do not calculate spread or probability-weighted return unless terms, price, and timing are clear.
- Preserve cash vs stock vs mixed consideration labels.
- Label stale unaffected prices or old deal-spread snapshots.

### Checks

- Missing current price, consideration, closing date, probability, or break price in a return table.
- Mixed date formats for milestones.
- Deal terms unsupported by a primary source.


## ETF / Index Data

### Preserve

- index or ETF name, methodology source, constituent ticker/security ID, weight, float adjustment, rebalance date, effective date, sector/industry, country, share class, and source timestamp.

### Cleaning judgment

- Do not infer index membership or weights without an index/ETF sponsor source or user-provided export.
- Preserve additions/deletions, pro forma weights, and current weights separately.

### Checks

- Missing as-of/effective date, methodology source, ticker/security ID, or constituent weight.
- Mixed index families or ETF share classes without a source field.
