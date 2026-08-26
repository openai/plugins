# Hedge Scorecard Schema

Use `scripts/score_hedge_candidates.py` when the user supplies structured hedge candidates and wants repeatable scoring or a basis-risk ledger.

```bash
python scripts/score_hedge_candidates.py hedge_candidates.csv --output-dir output
```

Required columns: `hedge`, `hedge_type`, `risk_hedged`.

Optional descriptive columns: `target_position`, `retained_exposure`, `as_of`, `source`, `live_pricing_status`, `borrow_status`, `option_chain_status`, `risk_model_status`, `basis_risk`, `basis_risk_mitigation`, `monitoring_trigger`, `implementation_status`, `notes`.

Optional scores: `exposure_fit_score`, `thesis_preservation_score`, `relationship_stability_score`, `downside_behavior_score`, `tenor_alignment_score`, `cost_carry_score`, `liquidity_score`, `implementation_complexity_score`, `basis_risk_score`.

Scores may be 0-5 or 0-100. Invalid numerics are excluded and surfaced in warnings; they are not coerced to zero. For `basis_risk_score`, higher means lower basis risk.

Outputs: `hedge_scorecard.csv`, `basis_risk_ledger.csv`, `hedge_scorecard.json`, `hedge_scorecard_support_note.md`.

Readiness status:

- `implementation-data-ready`: as-of, source, live pricing, borrow, option-chain, and risk-model fields are supplied and current/available/confirmed/validated/not_applicable.
- `needs-targeted-checks`: readiness fields exist but one or more are stale, unavailable, or not ready.
- `screen-grade`: missing as-of/source/readiness fields.
- `route_to_credit_markets`: hedge type is CDS, bond, loan, spread DV01/CS01, credit spread hedge, capital-structure hedge, distressed hedge, recovery, covenant, or another credit instrument. Use only as public-equity risk context in this plugin.

The scorecard is a PM triage artifact, not an execution instruction; confirm live pricing, liquidity, borrow, option chain, risk model, mandate permissions, and portfolio interactions before implementation. Credit hedge construction belongs in Credit Markets; Public Equity Investing may use those rows only as equity-risk context.
