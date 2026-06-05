# Model Methodology

This reference distills a Takahashi-Alexander style cashflow model pattern. Use it to forecast private capital cashflows from Chronograph actuals. Treat future commitments and pacing overlays as user-provided assumptions and model estimates.

## Model Modes

- Existing portfolio forecast: forecast runoff from current Chronograph commitments.
- Future commitment pacing overlay: model planned new commitments as assumptions.
- Combined liquidity view: add existing portfolio forecast and future pacing overlay.

## Example Planning Assumptions

Use these as illustrative starting points when the user has not provided custom assumptions. Do not treat them as client-specific defaults.

| General fund type | Initial contribution rate | Contribution rate | Bow | Life | Yield | Growth |
|---|---:|---:|---:|---:|---:|---:|
| Buyout / Private Equity | 25% | 50% | 2.5 | 12 | 0% | 13% |
| Venture / Growth | 25% | 50% | 3.0 | 15 | 0% | 10% |
| Real Assets | 40% | 40% | 5.0 | 12 | 5% | 8% |
| Energy / Natural Resources | 30% | 50% | 1.0 | 15 | 15% | 8% |
| Other / Mixed | 30% | 45% | 2.0 | 12 | 8% | 8% |

Ask for user assumptions when strategy mix materially affects the answer. If unavailable, use a clearly labeled illustrative assumption set.

## Assumption Selection

Use assumptions in this order:

1. User-provided assumptions.
2. User-provided strategy mix mapped to the example assumption sets.
3. A clearly labeled illustrative assumption set.
4. Chronograph fund type metadata.

## Input Data

For each fund or commitment, collect:

- Fund ID and fund name.
- Commitment ID if working at commitment level.
- Vintage year.
- Fund type or a mapped general fund type.
- Commitment amount.
- Actual called, distributed, NAV, and unfunded as of the current reporting date.
- Historical called and distributed if the output needs actual annual cashflows.

## Periods

Use annual forecast periods by default. If the as-of date is not a year end, the first forecast year should be prorated for remaining quarters in the year. For a quarterly model, apply the same formulas at quarter granularity.

Let:

- `age = forecast_year - vintage_year`
- `remaining_unfunded_prior = prior period unfunded`
- `nav_prior = prior period NAV`
- `initial_call_rate = assumption for years 1-2`
- `call_rate = assumption for years 3+`
- `bow`, `life`, `yield`, and `growth` from the assumption table

## Forecast Contributions

The workbook calls capital from prior unfunded. For annual periods:

```text
rate = initial_call_rate if age <= 2 else call_rate
forecast_contribution = max(rate * remaining_unfunded_prior, 0)
```

For a stub first forecast year, prorate by remaining quarters:

```text
stub_factor = remaining_quarters_in_year / 4
forecast_contribution = stub_factor * rate * remaining_unfunded_prior
```

Cap contributions so they do not exceed prior unfunded unless the user explicitly wants a looser model.

## Forecast Distribution Rate

The workbook uses a Takahashi-Alexander style bow curve:

```text
life_progress = age / life
distribution_rate = 1 if life_progress >= 1 else max(yield, life_progress ^ bow)
```

Clamp negative ages to zero. If vintage year is missing, ask for a vintage or use a conservative assumption only if the user approves.

## Forecast Distributions

The workbook applies the distribution rate to prior NAV after growth, with a special first forecast period that avoids a drop below prior actual distributions within the same year.

Simple annual implementation:

```text
forecast_distribution = distribution_rate * nav_prior * (1 + growth)
```

For income-oriented strategies, `yield` creates a floor through the distribution rate formula. Distributions should not exceed a sensible total value unless the user asks for unconstrained output.

## Forecast NAV

Roll NAV forward:

```text
forecast_nav = max(nav_prior * (1 + growth) + forecast_contribution - forecast_distribution, 0)
```

For quarterly periods:

```text
quarterly_growth = (1 + annual_growth) ^ 0.25 - 1
forecast_nav = max(nav_prior * (1 + quarterly_growth) + contribution - distribution, 0)
```

## Forecast Unfunded

Roll unfunded forward:

```text
forecast_unfunded = max(remaining_unfunded_prior - forecast_contribution, 0)
```

## Net Cashflow and Exposure

```text
net_cashflow = distributions - contributions
exposure = nav + unfunded
```

Use net cashflow from the LP perspective: contributions are cash outflows, distributions are inflows.

## Checks

Include these checks in analysis or Excel outputs:

- Contributions do not exceed beginning unfunded.
- Ending unfunded equals beginning unfunded less contributions.
- Ending NAV equals beginning NAV grown plus contributions less distributions.
- Net cashflow equals distributions less contributions.
- Planned commitments are not counted as contributions until called.
- Combined totals equal existing portfolio plus pacing overlay.
