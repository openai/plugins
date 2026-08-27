# Public Equity Investing Materializer Schema

`scripts/materialize_public_equity_sensitivities.py` accepts an optional JSON file. If no file is provided, it emits table shells with input-required notes.

## Top-Level Shape

```json
{
  "currency": "$",
  "source": {
    "source_id": "equity_model_update_v3",
    "source_posture": "model_validated",
    "as_of_date": "2026-05-12"
  },
  "base": {},
  "axes": {},
  "cases": [],
  "triggers": []
}
```

## `source` Fields

The materializer carries source fields into every deterministic output row. Use these to keep scenario math traceable when outputs feed a memo, pitch, thesis tracker, or model update.

| field | meaning |
|---|---|
| `source_id` | model, note, source package, filing, transcript, or assumption set used |
| `source_posture` | `model_validated`, `source_derived`, `user_provided`, `analyst_assumption`, `illustrative`, or similar |
| `as_of_date` | date/version for market-sensitive or model-sensitive inputs |

The same fields may be supplied at the top level, inside `source`, inside `base`, or on individual case/trigger rows. Row-level fields override base/top-level fields.

## `base` Fields

| field | meaning |
|---|---|
| `share_price` | current or anchor share price |
| `base_price_target` | base-case target price |
| `upside_price_target` | upside-case target price |
| `downside_price_target` | downside-case target price |
| `upside_probability` | probability for upside case |
| `base_probability` | probability for base case |
| `downside_probability` | probability for downside case |
| `shares_outstanding` | diluted shares or units for per-share valuation |
| `net_debt` | debt less cash and cash-like items |
| `ebitda` | EBITDA denominator for EV/EBITDA sensitivity |
| `eps` | EPS denominator for P/E sensitivity |
| `ntm_eps` | NTM EPS fallback |
| `pe_multiple` | base P/E multiple |
| `multiple` | generic base multiple fallback |
| `revenue` | revenue base for KPI sensitivity |
| `ebit_margin` | EBIT margin for operating sensitivity |
| `ebitda_margin` | EBITDA margin fallback |
| `incremental_margin` | optional flow-through margin |
| `cash` | unrestricted cash |
| `revolver_availability` | available liquidity source |
| `minimum_liquidity` | liquidity floor |
| `fcf` | free cash flow |
| `free_cash_flow` | FCF fallback |
| `maturities_12m` | next-12-month maturities or debt uses |
| `debt` | total debt for leverage |
| `success_price` | event success value |
| `deal_price` | event success fallback |
| `fail_price` | event fail value |
| `unaffected_price` | unaffected or pre-event price |
| `rate_sensitivity_pct_per_100bps` | price impact from 100 bps rate move |
| `spread_sensitivity_pct_per_100bps` | price impact from 100 bps spread move |

## `axes` Fields

| field | default |
|---|---|
| `valuation_multiples` | `[8.0, 10.0, 12.0]` |
| `eps_revisions` | `[-0.10, 0.00, 0.10]` |
| `multiple_changes` | `[-0.10, 0.00, 0.10]` |
| `revenue_growth_shocks` | `[-0.05, 0.00, 0.05]` |
| `margin_shock_bps` | `[-200, 0, 200]` |
| `event_probabilities` | `[0.25, 0.50, 0.75]` |
| `rate_changes_bps` | `[-100, 0, 100]` |
| `spread_changes_bps` | `[-100, 0, 100]` |

## `cases`

Optional case rows override the default bull/base/bear rows:

```json
{
  "scenario": "upside",
  "price_target": 150.0,
  "probability": 0.25,
  "rationale": "margin recovery and multiple normalization",
  "implication": "add if estimate revision confirms",
  "source_id": "analyst_case_v2",
  "source_posture": "analyst_assumption",
  "as_of_date": "2026-05-12"
}
```

For `price_target_scenario`, probabilities must be complete for every case and sum to 100%. If any case is missing a probability, any probability is outside `0.0` to `1.0`, or the distribution does not sum to 100%, the probability-weighted row is marked `input required` and the output includes `probability_check` plus `probability_sum`.

## `triggers`

Optional trigger rows populate `thesis_trigger_table`:

```json
{
  "trigger": "FY2 EPS cut",
  "threshold": "-5%",
  "monitoring_cadence": "post-print",
  "implication": "reassess target multiple",
  "next_step": "equity-model-update",
  "source_or_owner": "earnings model",
  "source_id": "earnings_preview_v1",
  "source_posture": "source_derived",
  "as_of_date": "2026-05-12"
}
```

## Output

Each table emits:

```json
{
  "name": "valuation_sensitivity",
  "description": "Implied price by valuation multiple.",
  "columns": ["..."],
  "rows": [{"...": "..."}],
  "notes": ["..."]
}
```

JSON output is the default because these tables usually feed another skill, workbook script, or dashboard renderer. Markdown output is an explicit support-note format for chat or memo drafting when requested. CSV output supports one table at a time. Standard output rows include `source_id`, `source_posture`, and `as_of_date`.

Run logs also include readiness metadata:

- `not-decision-ready`: no input JSON, missing base case, missing current price, or invalid/missing probabilities.
- `screen-grade`: calculations can be shown, but source/as-of posture is missing or illustrative.
- `senior-review-ready`: current price, case values, probability validation, and source/as-of posture are complete enough for senior review.
