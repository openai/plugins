# Public Equity Investing Examples

## Example 1: Issuer financial supplement with messy headers

User: "Clean this earnings supplement export and make it model-input ready."

Expected behavior:

- Infer financial statement / issuer reporting domain.
- Preserve issuer, segment, metric, fiscal period, actual/estimate/guidance labels, currency, units, and source date.
- Remove report title rows and obvious subtotals from `clean_data`, preserving them in `raw_source` and logging the action.
- Standardize period labels but do not infer a fiscal calendar if not provided.
- Format amounts with thousands separators; preserve currency and unit columns if mixed.
- Create checks for duplicate issuer + metric + period + scenario rows, missing amounts, missing periods, and totals embedded in detail data.

## Example 2: Consensus/provider estimate export

User: "Clean this consensus export before I refresh the model."

Expected behavior:

- Infer consensus / provider export domain.
- Preserve provider, estimate date, broker/count metadata, actual/estimate flag, fiscal period, metric definition, currency, and units.
- Keep actuals and estimates separate; do not overwrite one with the other.
- Flag missing estimate dates, mixed providers, duplicate metric + period rows, and stale snapshots.
- Output a clean table plus data dictionary, quality checks, and assumptions audit.

## Example 3: Credit Markets handoff preservation / equity-risk signal sheet

User: "Profile this bond trading sheet, preserve the fields, and route the credit note to Credit Markets."

Expected behavior:

- Infer `credit_markets_handoff` domain and route credit-note ownership to Credit Markets.
- Preserve issuer, instrument ID, tranche, coupon, maturity, seniority, price, yield, spread, rating, and pricing timestamp.
- Treat CUSIPs/ISINs as text.
- Do not merge instruments by issuer alone.
- Flag missing maturities, mixed spread units, negative/impossible yields, duplicate CUSIPs with conflicting economics, and missing source timestamps; do not interpret the credit economics locally.

## Example 4: Portfolio holdings / risk export

User: "Clean this holdings file so I can use it for exposure and hedge analysis."

Expected behavior:

- Infer portfolio / risk domain.
- Preserve portfolio/account, position date, security ID, issuer, long/short sign convention, market value, exposure, weight, benchmark, and hedge tags.
- Do not net long and short rows unless explicitly requested.
- Flag missing security IDs, mixed currencies, unclear signs, stale prices, and weights that do not sum where expected.

## Example 5: Event-driven deal tracker

User: "Clean this merger arb tracker and make the spread fields reliable."

Expected behavior:

- Infer event-driven / special situations domain.
- Preserve target, acquirer, consideration, unaffected price, current price, spread, probability, expected close, break price, and regulatory milestones.
- Do not calculate spread or probability-weighted return unless deal terms, price, and timing are clear.
- Flag stale price dates, unsupported deal terms, mixed consideration types, and missing break-price assumptions.

## Example 6: Explicit user instructions

User: "Clean the attached CSV. Keep only rows where Status = Active, convert dates to yyyy-mm-dd, do not remove duplicates, and output snake_case headers."

Expected behavior:

- Follow the explicit filter, date, duplicate, and header instructions.
- Preserve raw source.
- Log that inactive rows were filtered per user instruction.
- Do not apply exact duplicate removal even if duplicates exist; flag duplicates in quality checks if useful.
- Use snake_case headers in `clean_data`.

- Add `route_to_credit_markets` when the requested output is a credit note, covenant review, recovery analysis, or debt-security decision.
