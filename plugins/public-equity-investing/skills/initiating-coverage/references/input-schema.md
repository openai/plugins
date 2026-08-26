# Input Schema

Use this schema when the user or another skill provides structured initiation inputs.

```json
{
  "company": "string",
  "ticker": "string or null",
  "exchange": "string or null",
  "sector": "string or null",
  "report_mode": "sell_side_initiation | buy_side_deep_dive | long_only_initiation | hedge_fund_initiation | credit_adjacent_initiation | sector_initiation | model_first_initiation | report_refresh",
  "audience": "string or null",
  "data_cutoff": "YYYY-MM-DD or null",
  "current_price": 0.0,
  "currency": "string",
  "rating_framework": "string or null",
  "user_view": "string or null",
  "thesis_hypotheses": ["string"],
  "sources": [
    {
      "source_id": "S1",
      "source_name": "string",
      "source_type": "filing | transcript | earnings_release | investor_deck | model | consensus | provider | web | user_provided | other",
      "date_published": "YYYY-MM-DD or null",
      "period_covered": "string or null"
    }
  ],
  "financials": {
    "historical": [],
    "consensus": [],
    "forecast": []
  },
  "valuation": {
    "primary_method": "string or null",
    "target_price": 0.0,
    "upside_case": 0.0,
    "downside_case": 0.0,
    "assumptions": []
  },
  "catalysts": [],
  "risks": [],
  "open_questions": []
}
```

Required minimum fields for structured validation:
- company,
- report_mode,
- sources,
- thesis_hypotheses or user_view.

If `target_price` is included, `current_price`, `currency`, and valuation assumptions should be present.
