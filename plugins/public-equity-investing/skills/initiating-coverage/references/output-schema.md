# Output Schema

Use this schema for structured handoff to `thesis-tracker`, `equity-model-update`, `long-short-pitch`, `memo-builder`, or deck workflows.

```json
{
  "company": "string",
  "ticker": "string or null",
  "report_mode": "string",
  "prepared_date": "YYYY-MM-DD",
  "data_cutoff": "YYYY-MM-DD or null",
  "evidence_confidence": "high | medium | low",
  "rating_or_view": "string or null",
  "target_price": 0.0,
  "currency": "string or null",
  "md_pm_answer": "string",
  "thesis_pillars": [
    {
      "title": "string",
      "claim": "string",
      "evidence_label": "fact | company_claim | street_estimate | model_derived | banker_or_pm_judgment | assumption | mixed | needs_source",
      "confidence": "high | medium | low",
      "source_ids": ["S1"],
      "disconfirming_signal": "string"
    }
  ],
  "key_debates": [
    {
      "debate": "string",
      "consensus_view": "string",
      "our_view": "string",
      "evidence": "string",
      "what_would_change_our_mind": "string",
      "source_ids": ["S1"]
    }
  ],
  "model_drivers": [
    {
      "driver": "string",
      "historical_baseline": "string",
      "forecast_assumption": "string",
      "sensitivity": "string",
      "evidence_label": "string",
      "source_ids": ["S1"]
    }
  ],
  "valuation": {
    "primary_method": "string",
    "target_price_math": "string",
    "implied_multiple": "string or null",
    "upside_case": "string",
    "downside_case": "string",
    "key_sensitivities": []
  },
  "catalysts": [],
  "risks": [],
  "source_register": [],
  "assumptions_register": [],
  "stale_data_flags": [],
  "open_questions": []
}
```
