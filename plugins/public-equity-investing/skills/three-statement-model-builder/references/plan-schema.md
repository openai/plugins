# Plan Schema: Three Statement Model Builder

## Purpose

`plan.json` is the single source of truth for the default banker formula workbook path and deterministic operating-model support pipeline. The user may provide it directly, or ChatGPT may create it from prompt context, files, connected apps, filings, and clearly labeled assumptions.

## Top-level structure

Required top-level keys:

```json
{
  "meta": {},
  "source_basis": [],
  "timeline": {},
  "historicals": {},
  "revenue": {},
  "costs": {},
  "working_capital": {},
  "ppe": {},
  "debt": {},
  "tax": {},
  "equity": {},
  "scenarios": {},
  "sensitivities": {}
}
```

Optional key:

```json
{"other_balance_sheet": {"other_assets": 0.0, "other_liabilities": 0.0}}
```

## Metadata

Required:
- `company_name`
- `industry`
- `currency`
- `units`
- `as_of_date`
- `accounting_basis`: `us_gaap`, `ifrs`, `management`, `cash_basis`, or `unspecified`

Recommended:
- `model_purpose`
- `prepared_for`

## Source basis

`source_basis` must be a non-empty list. Each source requires:
- `id`
- `label`
- `source_type`
- `as_of_date`
- `evidence_label`
- `covers`
- `confidence`
- `notes`

Supported evidence labels:
- `source_reported`
- `company_provided`
- `connector_sourced`
- `public_filing`
- `web_verified`
- `management_guidance`
- `analyst_estimate`
- `benchmark`
- `assumption`
- `placeholder`

`source_basis` must cover `historicals` and at least one material forecast driver such as `revenue`, `costs`, `working_capital`, `ppe`, `debt`, or `forecast`.

## Timeline

Required:
- `start_year`: integer
- `horizon_periods`: annual periods or quarterly periods depending on `periodicity`
- `periodicity`: `annual` or `quarterly`

Annual labels are emitted as `FY2026`. Quarterly labels are emitted as `Q1-FY2026`, `Q2-FY2026`, etc.

## Historical financials

Required historical objects:
- `income_statement`
- `balance_sheet`
- `cash_flow`
- `debt_schedule`
- `ppe`
- `working_capital`

Minimum income statement fields per period:
- `revenue`
- `cogs`
- `opex`
- `da`
- `interest`
- `taxes`
- `net_income`

Minimum balance sheet fields per period:
- `cash`
- `ar`
- `inventory`
- `other_current_assets`
- `ppe_net`
- `other_assets`
- `ap`
- `accrued_expenses`
- `deferred_revenue`
- `debt`
- `other_liabilities`
- `common_equity`
- `retained_earnings`

The latest historical balance sheet must balance. If the historical balance sheet does not balance, the model is not decision-ready until corrected or explicitly explained.

## Revenue

Supported revenue models:

### `segments`

```json
{
  "model": "segments",
  "source_id": "src_mgmt_plan",
  "segments": {
    "segment_a": {
      "base_revenue": 100.0,
      "growth_rates": {"FY2026": 0.08, "FY2027": 0.07},
      "evidence_label": "company_provided",
      "source_id": "src_mgmt_plan"
    }
  }
}
```

### `total_growth`

```json
{"model": "total_growth", "base_revenue": 100.0, "growth_rates": {"FY2026": 0.05}}
```

### `volume_price`

```json
{
  "model": "volume_price",
  "base_units": 1000.0,
  "base_price": 10.0,
  "unit_growth_rates": {"FY2026": 0.04},
  "price_growth_rates": {"FY2026": 0.03}
}
```

## Costs

Required:

```json
{
  "cogs": {"method": "gross_margin", "gross_margin": {"FY2026": 0.40}},
  "opex": {"method": "pct_revenue", "pct_revenue": {"FY2026": 0.20}}
}
```

COGS methods: `gross_margin`, `pct_revenue`.
Opex methods: `pct_revenue`, `amount`.

## Working capital

Current supported method: `days`.

Required assumptions:
- `ar_days`
- `inventory_days`
- `ap_days`
- `other_current_assets_pct_revenue`
- `accrued_expenses_pct_revenue`
- `deferred_revenue_pct_revenue`

## PP&E

Required:
- `capex_method`: `pct_revenue` or `amount`
- `capex_pct_revenue` or `capex_amount`
- `depreciation_method`: `pct_beginning_ppe`, `pct_revenue`, or `amount`
- matching depreciation assumption map

## Debt

Required:
- `beginning_debt`
- `beginning_revolver_drawn`
- `revolver_commitment`
- `mandatory_amortization`
- `optional_draws`
- `interest_rate`
- `cash_sweep`
- `covenants`

Cash sweep requires:
- `enabled`
- `min_cash`
- `sweep_pct`

Covenants may include:
- `min_liquidity`
- `max_net_leverage`
- `min_interest_coverage`

## Tax

Required:
- `book_tax_rate`
- `cash_tax_rate`
- `nol_balance`

The model distinguishes book taxes from cash taxes and tracks NOL usage at a high level.

## Equity

Required:
- `common_equity`
- `dividends`
- `buybacks`
- `issuance`

Dividends reduce retained earnings. Buybacks reduce common equity. Issuance increases common equity.

## Scenarios

Required scenarios:
- `base`
- `downside`
- `upside`

Each scenario requires:
- `description`
- `evidence_label`
- `overrides`

Scenarios use deep-merge overrides against the base plan. A scenario that changes labels but not outputs is a hard failure.

## Sensitivities

Supported lists:
- `revenue_growth_shocks`
- `gross_margin_shocks`
- `dso_day_shocks`
- `capex_pct_revenue_shocks`
- `interest_rate_shocks`

## Screen-grade vs. decision-grade

A plan is screen-grade when it uses placeholders, limited evidence, or illustrative assumptions but passes mechanical checks.

A plan can be decision-grade only when material historicals and drivers are sourced, reconciled, current for the purpose, and free of material hard failures or unresolved warnings.
