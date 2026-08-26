# Valuation Read-Through

## Equity value and dilution

Core formulas:

- `market_cap_basic = price * basic_shares`
- `fd_shares = basic_shares + incr_options_warrants + incr_rsus_psus + incr_convertibles_if_converted`
- `equity_value_fd = price * fd_shares`

Default for EV-based work: use fully diluted equity value.

Options and warrants:

- If `price <= strike`, incremental shares are `0`.
- If `price > strike`, use treasury stock method: proceeds repurchase shares at current price, and only the net incremental shares are added.
- Incremental shares cannot be negative.

RSUs and PSUs: treat as full incremental shares unless a specific net-settlement methodology is provided.

Convertibles: use an if-converted threshold. If treated as converted, add implied shares and exclude convertible principal from debt. Otherwise, keep principal in debt and do not add shares. Disclose the rule.

ADRs/GDRs: adjust either shares with `share_factor` or price with `share_factor`, not both.

## Enterprise value bridge

Use:

`EV = equity_value_fd + debt_like_items + other_claims - cash_like_items - non_operating_assets`

Debt-like items may include short-term debt, long-term debt, lease liabilities, preferred equity, pension deficit, ARO, and similar claims.

Other claims and non-operating assets:

- Add minority interest when denominators are consolidated at 100 percent.
- Subtract investments when they are non-operating and not already reflected in the denominator.
- If only book value is available for investments, subtract it and flag it as an approximation.

If provider market cap or EV is available, reconcile to it. Differences above roughly `3%` for market cap or `5%` for EV need explanation.

## Denominator rules

- Use reported LTM and NTM values by default.
- Use adjusted values only when the user asks or the inputs clearly separate reported and adjusted metrics.
- Never overwrite reported values with adjusted values.
- LTM denominators must carry `ltm_period_end`.
- Warn when the lag between valuation date and LTM period end is greater than `180` days.
- Treat lag greater than `365` days as critical unless the user accepts stale data.
- NTM estimates must carry `estimate_as_of`, method, and source.
- If NTM is missing, compute only LTM multiples.
- Do not fabricate forward estimates.

## Multiple pairing

- EV must pair with unlevered or enterprise-scope denominators.
- Market cap, equity value, or price must pair with equity-scope denominators.
- If using aggregate `P/E`, make sure net income is attributable to common shareholders.
- If a denominator is negative or zero, show `N/M`.
- If a denominator is near zero, flag it as unstable.

## FX

If the analysis is in a base currency:

- convert market values and balance sheet items using spot rates;
- convert income statement and cash flow denominators using average rates;
- if average is missing, use spot only with an explicit warning.

## Outliers and statistics

Do not treat every outlier as a data error. First ask whether it is a true differentiator, or whether it comes from stale shares, wrong sign, missing minority interest, unit error, or denominator distortion.

Default outlier method: IQR.

- `IQR = Q3 - Q1`
- lower bound = `Q1 - 1.5 * IQR`
- upper bound = `Q3 + 1.5 * IQR`

Do not alter underlying data. Keep raw values visible and compute summary stats with and without flagged outliers when useful.

Show valid count, median, mean, trimmed mean, p25, p75, p10, and p90 when space permits.

## Selected multiple range discipline

Do not mechanically use full peer-set min/max as the valuation range.

Default hierarchy:

1. start with core-peer median and interquartile range;
2. adjust for growth, margin, scale, leverage, cyclicality, liquidity, business mix, and data quality;
3. use secondary peers as context, not anchors, unless the core set is too small;
4. disclose whether the selected range is judgmental or mechanically derived.

Use `screening range` when data quality is incomplete, `selected range` when peer set and denominator quality are adequate, and `not supportable` when the range would be mostly guesswork.

## Implied valuation

For target valuation:

1. Choose the multiple set that best matches the target's economics and data quality.
2. Prefer median over mean when dispersion is wide.
3. Exclude `N/M` observations from selected statistics.
4. Apply the selected peer multiple to the target denominator.
5. Bridge from implied EV to implied equity value.
6. Convert to per-share value using the correct share basis.
7. Explain why the selected statistic and peer subset are appropriate.

When forward estimates or a fully diluted EV bridge are unavailable, label any implied value-per-share output as an `illustrative trailing-multiple range`, not a base case, target price, or action threshold.

## PM-Native Multiple Bridge

A comps read-through must bridge from peer median to selected multiple using growth, margin, FCF conversion, ROIC/quality, cyclicality, leverage, liquidity/float, index/ETF ownership, governance, and source confidence. State current price, supportable implied value/share or illustrative trailing-multiple range, upside/downside where supported, what is priced in, rerating/derating mechanism, and valuation posture. Include portfolio action implications only when requested or supported by supplied portfolio context.
