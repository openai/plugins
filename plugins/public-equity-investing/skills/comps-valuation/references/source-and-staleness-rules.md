# Source And Staleness Rules

## Source hierarchy

Follow `financial-source-of-truth` for source hierarchy, citation format, stale-data checks, and source conflicts. For comps work, prefer:

1. user-provided workbooks, provider exports, filings, investor decks, and source files;
2. connected financial-data sources or workspace apps;
3. primary filings, company IR, exchange data, and official announcements;
4. reputable market-data or estimate providers;
5. general web/search only as a labeled fallback.

Do not silently blend different source qualities. If a provider value, filing value, and user value disagree, disclose the conflict and choose the value with the clearest provenance for the requested decision.

## Public comps stale-data checks

For each company in the core table, carry or disclose:

- market-data as-of date;
- financial-statement period end;
- estimate source and estimate-as-of date when NTM is used;
- forward-estimate basis: verified consensus or third-party forward estimate;
- trading and reporting currency;
- FX date and spot/average convention when currencies differ;
- EV bridge basis;
- adjustment basis: reported, adjusted, consensus, company-defined, or inferred.

Never mix today's share price with stale share count, stale cash/debt, stale estimates, or stale denominators without labeling the mismatch in `QA Flags And Caveats`.

## Evidence labels

Use shared evidence labels for major inputs and conclusions:

- `fact_primary`
- `fact_secondary`
- `third_party_estimate`
- `internal_estimate`
- `management_claim`
- `seller_claim`
- `assumption`
- `inference`
- `unsupported`

Comps-specific mapping:

- company filing financials = `fact_primary`
- traded price from a reliable market-data source = `fact_secondary`, with as-of date
- consensus estimates = `third_party_estimate`
- forward estimates sourced through a public aggregator or secondary provider without a verified contributor count, estimate-set date, and methodology = `third_party_estimate`; label them in reader-facing output as `third-party forward estimates`, not `consensus`
- peer-set inclusion rationale = `inference`
- selected multiple range = `inference`
- manual peer inclusion/exclusion = `assumption` or `inference`, with rationale
- target private-company financials from CIM, banker deck, or management materials = `seller_claim` or `management_claim` unless verified

## Canonical input contract

When user files or exports are available, normalize them internally into these fields where practical:

| Table | Required fields | Helpful fields |
|---|---|---|
| `entities` | `company_id`, `company_name`, `ticker`, `sector_module`, `reporting_currency`, `is_target` | exchange, country, taxonomy, business model tags |
| `market_data` | `company_id`, `as_of_date`, `price`, `trading_currency`, `basic_shares` | share factor, ADV, provider market cap |
| `capital_structure` | `company_id`, `as_of_date`, `cash`, `st_debt`, `lt_debt` | restricted cash, trapped cash, leases, minority interest, preferreds, pensions, investments |
| `financials` | `company_id`, `ltm_period_end`, `ltm_revenue` | EBITDA, EBIT, net income, CFO, capex, FCF, FFO, AFFO, TBV, book value |
| `estimates` | `company_id`, `estimate_as_of`, `ntm_method` | NTM revenue, EBITDA, EBIT, net income, EPS, FCF, FFO, AFFO |
| `dilution` | `company_id`, `instrument_type`, `quantity` | strike, conversion price, treasury stock method notes |
| `fx_rates` | `date`, `from_ccy`, `to_ccy`, `rate`, `rate_type` | spot, average, period basis |
| `adjustments` | `company_id`, `metric`, `period_end`, `amount`, `category`, `notes` | source, approval, adjustment basis |

## Data conventions

- Use `company_id` as the stable join key. Do not rely only on ticker strings.
- Dates must be `YYYY-MM-DD`.
- Currency codes should be ISO 4217.
- Monetary values should be absolute, not per-share, unless the field is explicitly per-share.
- Shares should be actual shares, not thousands.
- Percent fields should be stored as percent, such as `18.5`, not `0.185`.

## Overrides and assumptions

- Keep sourced values distinguishable from assumptions.
- Attach a short reason to every manual override or adjustment.
- Point important inputs back to their source table, filing, provider export, connector path, or stated assumption when possible.
- Use `consensus` in reader-facing output only when the estimate source, as-of basis, and methodology are clearly supported. Otherwise use `third-party forward estimates` and identify the provider and available timestamp.
- For downloadable/exported workbook artifacts, use `comps-valuation` in `workbook` mode and preserve overrides in an audit section or notes field there. Report mode should surface the override rationale in the comps read-through, standalone HTML report, or explicitly selected dashboard payload, not emit ad hoc local files.
