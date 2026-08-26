# Scenario / Expected-Value Table Schema

Use this schema when a long/short pitch needs deterministic scenario math.

## CSV columns

Required:
- `scenario`: case name such as `Bull`, `Base`, `Bear`, `Deal closes`, `Break`, or `Restructuring`.
- `probability`: decimal or percent probability; probabilities must sum to 100%.
- `current_value`: current price, spread reference, bond price, recovery reference, or other entry value.
- `target_value`: scenario target price, spread, recovery, or payoff value.
- `key_drivers`: concise driver description.
- `timing`: expected catalyst or realization window.

Optional:
- `trigger`: event or evidence that realizes the scenario.
- `source`: source tag, model output, or explicit assumption label.
- `source_as_of` or `source_date`: `YYYY-MM-DD` freshness date for the evidence behind the row.
- `retrieval_date`: optional date the source was retrieved.
- `borrow_fee`, `carry_cost`, `holding_period_days`: short-side borrow/carry math. Percent values are accepted.
- `break_price`: downside/break value for event-driven pitches.
- `recovery_value`, `bond_price`, `yield_or_spread`: Credit Markets pitch fields.

## Script

Run:

```bash
python scripts/materialize_trade_scenarios.py scenarios.csv --side long --markdown-out scenarios_support_note.md --json-out scenarios.json
```

Supported `--side` values:
- `long`: return = `(target_value - current_value) / current_value`
- `short`: gross return = `(current_value - target_value) / current_value`; net return subtracts borrow and carry over the holding period when supplied
- `event`: keeps event posture, calculates spread-style return, and preserves `break_price`
- `credit`: keeps credit posture and preserves recovery, bond-price, and spread fields

Default outputs are written to `/tmp/public_equity_investing_long_short_pitch/` unless explicit output paths are passed. Use `--run-date YYYY-MM-DD` for deterministic source freshness checks.

## Required pitch interpretation

The table is not the pitch. It only materializes scenario math. The final pitch still needs:
- variant perception
- expression and constraints
- catalyst path
- sizing/risk discussion
- borrow/carry for shorts
- disconfirmers and kill criteria
- add/trim/exit/cover rules
- monitoring dashboard
