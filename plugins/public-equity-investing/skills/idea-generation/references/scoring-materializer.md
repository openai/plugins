# Scoring Materializer

Use `scripts/score_ideas.py` when the user provides a structured candidate list and wants a ranked idea log. The script does not fetch market data and does not create a final recommendation; it materializes supplied scores into a repeatable PM triage artifact.

Default output directory is `/tmp/public_equity_investing_idea_generation_output`; pass `--output-dir` for a project-specific location.

## Input

Required:

- `ticker` or `security`

Optional descriptive fields:

- `company`
- `idea_type`
- `direction`
- `sector`
- `variant_view`
- `catalyst`
- `first_rejection_risk`
- `next_step`
- `source`
- `source_as_of`, `source_date`, or `as_of_date` in `YYYY-MM-DD` format

Optional numeric score fields, preferably 0-5:

- `valuation_score`
- `growth_score`
- `revisions_score`
- `quality_score`
- `momentum_score`
- `catalyst_score`
- `risk_reward_score`
- `liquidity_score`
- `crowding_score`
- `portfolio_fit_score`
- `variant_perception_score`

Scores above 5 are allowed and normalized against a 100-point scale. Invalid numeric values are not coerced to zero; they are excluded from the composite and surfaced in the warnings column.

## Outputs

The script writes:

- `ranked_ideas.csv`
- `idea_scorecard.json`
- `idea_scorecard_support_note.md`

Use `--run-date YYYY-MM-DD` in tests or dated research packets so stale/future source warnings are deterministic.

Rows with no valid numeric scores are labeled `needs_scoring_inputs`. The scorecard should be followed by human PM triage before any pitch, memo, or model handoff.
