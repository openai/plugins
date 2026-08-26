# DCF Plan Schema

## Purpose
`plan.json` is the complete shared input contract for the default banker formula workbook path and the deterministic support pipeline. It must contain enough source-labeled assumptions to produce a base, downside, upside, sensitivities, checks, and P0 handoff without relying on hidden defaults.

## Required top-level fields
- `meta`
- `source_basis`
- `timeline`
- `historicals`
- `forecast`
- `wacc`
- `terminal_value`
- `ev_to_equity_bridge`
- `scenarios`
- `sensitivities`

## `meta`
Required:
- `company`
- `industry`
- `currency`
- `units`
- `valuation_date` as `YYYY-MM-DD`
- `as_of_date` as `YYYY-MM-DD`
- `accounting_basis`
- `valuation_purpose`
- `model_type`: `fcff` or `fcfe`

## `source_basis`
Array of evidence entries. Required topics:
- `historicals`
- `forecast`
- `wacc`
- `terminal_value`
- `share_count`
- `net_debt`

Required fields per entry:
- `id`: unique string referenced elsewhere in the plan
- `topic`: one of the required topics or another useful topic such as `market_data`, `management_guidance`, `consensus`, `leases`, `pensions`, `tax`, `working_capital`
- `label`: evidence label
- `source_name`
- `source_type`
- `as_of_date`
- `confidence`: `high`, `medium`, or `low`
- `notes`

Allowed evidence labels:
- `reported`
- `company_guidance`
- `consensus`
- `management_case`
- `user_provided`
- `connected_app`
- `web_research`
- `analyst_estimate`
- `placeholder`
- `derived`

Decision-grade work should use mostly `reported`, `company_guidance`, `consensus`, `management_case`, `user_provided`, `connected_app`, `web_research`, and `derived` labels, with citations or source details. Heavy `analyst_estimate` support is screen-grade. Any `placeholder` affecting value is screen-grade at best.

## `timeline`
Required:
- `start_year`: last actual year or stub base year
- `horizon_years`: integer from 1 to 15
- `periodicity`: `annual` or `quarterly`

The current bundled pipeline is annual-oriented. Quarterly inputs can validate only if all scenario vectors match the horizon periods; otherwise convert to annual before running.

## `historicals`
Required for FCFF:
- `latest_year`
- `revenue`
- `ebitda`
- `ebit`
- `cash_taxes`
- `da`
- `capex`
- `change_nwc`
- `net_working_capital`
- `unlevered_fcf`
- `source_id`

Optional, but required to display a PP&E roll-forward:
- `ppe`: source-backed ending PP&E balance for `latest_year`

Required for FCFE also include:
- `net_income`
- `levered_fcf` if available

## `forecast`
Required:
- `cash_flow_basis`: `fcff` or `fcfe`
- `mid_year_convention`: boolean
- `source_id`

FCFF scenarios must include revenue growth, EBIT margin, tax rate, D&A percent of revenue, capex percent of revenue, and NWC percent of revenue.

FCFE scenarios must additionally include either `net_income_margin` or sufficient income-statement assumptions, plus `net_borrowing` if the capital structure is expected to change.

## `wacc`
Required:
- `risk_free_rate`
- `beta`
- `equity_risk_premium`
- `size_premium`
- `pre_tax_cost_of_debt`
- `marginal_tax_rate`
- `target_debt_pct`
- `target_equity_pct`
- `source_id`

Optional:
- `company_specific_premium`
- `country_risk_premium`
- `preferred_pct`
- `pre_tax_cost_of_preferred`

Weights should sum to approximately 100%. WACC must be positive and greater than perpetual terminal growth for perpetual-growth terminal value.

## `terminal_value`
Required:
- `method`: `perpetual_growth` or `exit_multiple`
- `source_id`

If `method = perpetual_growth`, include `perpetual_growth_rate`.
If `method = exit_multiple`, include `exit_ebitda_multiple`.
Best practice is to include both `perpetual_growth_rate` and `exit_ebitda_multiple` so the model can cross-check implied values.

## `ev_to_equity_bridge`
Required when per-share value is requested:
- `cash`
- `debt`
- `leases`
- `minorities`
- `associates`
- `pensions`
- `preferred_stock`
- `non_operating_assets`
- `options`
- `other_debt_like_items`
- `diluted_shares`
- `net_debt_source_id`
- `share_count_source_id`

Positive bridge convention:
- Add cash, non-operating assets, associates.
- Subtract debt, leases, minorities, pensions, preferred stock, options net settlement, and other debt-like items.

## `scenarios`
Must include `base`, `downside`, and `upside`.

Required FCFF scenario fields:
- `description`
- `revenue_growth`: scalar or list with `horizon_years` values
- `ebit_margin`: scalar or list with `horizon_years` values
- `tax_rate`: scalar or list
- `da_percent_revenue`: scalar or list
- `capex_percent_revenue`: scalar or list
- `nwc_percent_revenue`: scalar or list
- `terminal_growth_rate` when perpetual growth is used
- `wacc_adjustment`: numeric, may be zero

Optional fields:
- `exit_ebitda_multiple`
- `net_borrowing`
- `net_income_margin`
- `commentary`

## `sensitivities`
Required arrays:
- `wacc_delta`
- `terminal_growth_delta`
- `exit_multiple_delta`
- `revenue_growth_delta`
- `ebit_margin_delta`

Each array should contain negative, zero, and positive cases. Directionality checks use these outputs.

## Screen-grade vs decision-grade
Screen-grade inputs may use rough analyst estimates, placeholders, stale market data, or high-level assumptions. They can support triage but not capital allocation.

Decision-grade inputs require:
- current valuation date and market data;
- source-labeled historicals from filings or company materials;
- explicit bridge to latest cash, debt, leases, pensions, minorities, options, and shares;
- defensible WACC support;
- terminal value cross-checks;
- scenario and sensitivity support;
- no unresolved hard failures;
- warnings that are immaterial or explicitly accepted by the user.

For businesses whose valuation question is driven by operating KPIs, include the relevant source-backed driver schedule or disclose why the current workbook uses revenue as a proxy. Marketplace/platform examples include GBV or transaction volume, take rate, bookings/nights, active users, and frequency.
