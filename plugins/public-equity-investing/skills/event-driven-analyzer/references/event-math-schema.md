# Event Math Schema

Use this reference when preparing JSON inputs for `scripts/event_math.py`. The helper calculates deterministic event math from supplied terms only; it does not fetch market data or validate legal probability.

## CLI

```bash
python scripts/event_math.py --mode cash_merger --input input.json --pretty
python scripts/event_math.py --mode stock_deal --input input.json --pretty
python scripts/event_math.py --mode scenario_ev --input input.json --pretty
python scripts/event_math.py --mode scenario_ev --input input.json --allow-probability-sum-mismatch --pretty
python scripts/event_math.py --mode cvr --input input.json --pretty
```

`scenario_ev` validates that scenario probabilities sum to 1.0 and hard-fails mismatches by default. Use `--allow-probability-sum-mismatch` only for diagnostic output when intentionally inspecting an incomplete or non-normalized tree; do not use that output as a probability-weighted conclusion in a memo.

## `cash_merger`

Required:

- `current_price`
- `deal_price`

Optional:

- `days_to_close`
- `break_price`
- `expected_dividends`
- `financing_cost`
- `other_carry`

Outputs include adjusted deal value, gross return, annualized return, and market-implied probability when `break_price` is supplied.

## `stock_deal`

Required:

- `target_price`
- `acquirer_price`
- `exchange_ratio`

Optional:

- `target_shares`
- `days_to_close`
- `expected_target_dividends`
- `expected_acquirer_dividends`
- `borrow_cost`

Outputs include deal value, adjusted deal value, gross return, annualized return, and hedge shares per target shares.

## `scenario_ev`

Required:

- `current_price`
- `scenarios`

Each scenario requires:

- `name`
- `probability`
- `terminal_value`

Each scenario may also include `days_to_resolution`. Probabilities should be decimals between 0.0 and 1.0 and must sum to 1.0 unless the CLI is run with `--allow-probability-sum-mismatch`. With the default strict validation, bad sums return a non-zero exit code instead of JSON output. With the explicit allow flag, the output includes `probabilities_sum_to_100pct: false` and a diagnostic note; revise the inputs before using the math in a PM memo.

## `cvr`

Required:

- `milestones`

Each milestone requires:

- `name`
- `payment`
- `probability`
- `years`

Optional:

- `discount_rate`
- `liquidity_discount`

Outputs include gross present value and net present value after liquidity discount.
