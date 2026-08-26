# Comparable Company Analysis Framework

Use this reference when selecting peers, choosing multiples, and translating the model into investment judgment.

## What makes a good comparable

A strong peer is similar in the drivers investors actually value. Screen by:

- Business model and revenue model.
- Product/service mix.
- End-market and customer base.
- Geography and regulatory regime.
- Size and scale economics.
- Growth profile and margin trajectory.
- Unit economics or sector KPIs.
- Capital intensity and working capital profile.
- Leverage and balance-sheet risk.
- Cyclicality, commodity exposure, and interest-rate sensitivity.
- Management quality, governance, liquidity, index inclusion, and ownership structure where relevant.

Avoid the lazy peer set: companies in the same broad industry with materially different economics.

## Peer tiers

Use tiers instead of one undifferentiated list:

- **Target**: The subject company.
- **Core**: Closest public comparables; should drive valuation range.
- **Secondary**: Relevant but less directly comparable due to size, geography, margin, growth, business mix, or maturity.
- **Adjacent**: Useful context, but should not mechanically drive valuation.
- **Watchlist**: Potential peers requiring more diligence.
- **Excluded**: Obvious candidates that are not used, with rationale.

A MD/PM-grade model explains both inclusion and exclusion.

## Screen-grade fallback when data is missing

If market data, consensus estimates, EV bridge inputs, workbook dependencies, or uploaded source files are unavailable, do not return an empty failure. Produce a labeled fallback artifact instead.

Lead every fallback output with:

`Comps posture: screen-grade; missing market data and/or estimates are explicitly labeled.`

The fallback artifact should include:

- Target row and proposed peer candidates.
- Peer tier, peer role, and inclusion/exclusion logic.
- Missing market-data caveat.
- Required source fields for price, shares, EV bridge, LTM denominators, NTM estimates, and peer rationale.
- A statement that no selected valuation range, premium/discount conclusion, or decision-grade multiple is available until sources are populated.

Use `scripts/materialize_screening_comps.py` for this deterministic fallback. It writes `peer_framework.csv`, `missing_data_requests.csv`, `source_requirements.csv`, `screen_grade_comps_support_note.md`, `run_log.json`, and `manifest.json` without requiring workbook dependencies.
It also writes `screen_grade_comps_framework.xlsx` as the first-read artifact with `Cover`, `Peer Framework`, `Missing Data Requests`, and `Source Requirements` tabs. The CSV, Markdown, JSON, log, and manifest files are hidden support artifacts unless explicitly requested.

## Multiple selection

Choose multiples that match the economic model:

### Enterprise-value multiples

Use when comparing total business value independent of capital structure:

- EV/Revenue: useful for early-stage, high-growth, or low/negative-profitability businesses; must be paired with growth and margin context.
- EV/EBITDA: common for operating businesses and capital-intensive sectors, but check lease, SBC, capex, and working-capital differences.
- EV/EBIT: useful when D&A/capex intensity matters and EBITDA overstates cash economics.
- EV/FCF or FCF yield: useful when FCF conversion is central; check working capital, capex timing, and taxes.

### Equity-value multiples

Use when value is best assessed at the common-equity level:

- P/E: appropriate when earnings are positive and comparable; sensitive to leverage, tax, non-recurring items, and accounting noise.
- P/B or P/TBV: common for banks, insurers, and asset-heavy financials; interpret with ROE/ROTCE and capital quality.
- Dividend yield: relevant for yield-oriented assets, utilities, REITs, and mature companies.

### Sector-specific multiples

Use sector metrics when they are the market's true shorthand:

- SaaS/software: EV/Revenue, EV/ARR, Rule of 40, NRR/GRR, FCF margin, growth-adjusted revenue multiple.
- Internet/marketplaces: EV/Revenue, take rate, GMV, contribution margin, cohort retention, CAC/LTV.
- Media/telecom: EV/EBITDA, subscriber metrics, ARPU, churn, spectrum or infrastructure economics.
- Retail/restaurants: EV/EBITDA, same-store sales, unit growth, AUV, store margins, lease-adjusted leverage.
- Industrials: EV/EBITDA, EV/EBIT, backlog, book-to-bill, capex intensity, cycle exposure.
- Energy/materials: EV/EBITDA, EV/production, reserves/resources, sustaining capex, commodity sensitivity.
- Healthcare services: EV/EBITDA, reimbursement risk, same-store/volume growth, payor mix.
- Biotech/pre-revenue: cash runway, stage-adjusted pipeline value, EV/pipeline asset; revenue/EBITDA metrics may be meaningless.
- Banks: P/TBV, P/B, ROE/ROTCE, NIM, CET1, credit quality; generally avoid standard EV multiples.
- Insurers: P/B, P/TBV, ROE, combined ratio, reserve adequacy.
- Asset managers: P/AUM, EV/fee-related earnings, net flows, fee rate, performance fees.
- REITs: P/AFFO, EV/EBITDA, cap rates, NOI growth, leverage, occupancy.

## Handling negative or distorted denominators

- Negative EBITDA, EBIT, EPS, or FCF should generally be shown as `NM`.
- Near-zero denominators can create false outliers; exclude with rationale or use a different metric.
- For cyclical sectors, use normalized mid-cycle earnings or cycle-adjusted metrics.
- For one-time disruptions, isolate non-recurring effects and show both reported and adjusted outputs if useful.
- Do not force a multiple just because a template has the row.

## Premium and discount logic

The selected multiple should reflect the target's relative fundamentals:

Reasons for premium:

- Higher sustainable growth.
- Better margins or margin expansion runway.
- Higher ROIC or FCF conversion.
- More recurring revenue, better retention, stronger pricing power.
- Stronger balance sheet or lower risk.
- Scarcity value, strategic asset quality, or superior liquidity.

Reasons for discount:

- Lower growth or weaker visibility.
- Lower margins, poor FCF conversion, or high capital intensity.
- Higher leverage, customer concentration, regulatory risk, cyclicality, or commodity exposure.
- Smaller scale or lower liquidity.
- Weaker management credibility or poor execution history.

Always connect the premium/discount to evidence in the workbook.

## Statistics and outliers

Calculate statistics, but do not outsource judgment to them:

- Use medians more than means when distributions are skewed.
- Use 25th/75th percentiles for valuation ranges.
- Use peer-tier medians and all-peer medians separately.
- Consider harmonic mean for some ratio central-tendency situations, but explain if used.
- Exclude outliers only with documented rationale.
- Keep excluded outliers visible where helpful; do not silently delete inconvenient data.

## Valuation range selection

A strong valuation range should be:

- Narrow enough to be decision-useful.
- Broad enough to reflect uncertainty.
- Anchored in Core peer evidence.
- Adjusted for growth, margins, returns, leverage, business quality, and data confidence.
- Supported by a sensitivity table.
- Explained in a narrative that a skeptical IC or board member could challenge.

## Private-company considerations

If valuing a private company:

- Use public comps for market benchmarks but consider illiquidity, size, governance, and information asymmetry.
- Adjust for control/minority basis depending on use case.
- Check whether the target's metrics are audited, reviewed, or management-provided.
- Be explicit about marketability discount, control premium, or transaction-context adjustments if used.

## Common mistakes

- Using broad industry peers without business-model similarity.
- Mixing reported and adjusted EBITDA.
- Mixing fiscal-year and calendar-year periods.
- Ignoring leverage when using equity multiples.
- Ignoring capex when using EBITDA in capital-intensive businesses.
- Treating vendor EV as correct without checking share count, cash, debt, converts, preferred, or minority interest.
- Hiding negative multiples or replacing them with zero.
- Using stale prices with fresh financials or vice versa without disclosure.
- Stating a valuation range without explaining why the target deserves it.

## Equity PM Multiple Bridge

The workbook should expose a selected-multiple bridge from peer median to selected value. Required bridge factors: growth, margin, ROIC/quality, FCF conversion, leverage, liquidity/float, cyclicality, index/ETF ownership, short interest/borrow, governance, and data confidence. Route debt comps, bond comps, loan comps, CDS, spread/yield relative value, recovery waterfalls, and credit-security valuation to Credit Markets.
