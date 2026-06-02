# Observed Usage Inputs

`plugin-eval` can ingest local JSON or JSONL files that contain token telemetry from real runs.

## Supported Shapes

The parser accepts these common patterns:

- a Responses API object with a top-level `usage`
- a `response.done` event with `response.usage`
- a wrapper object with `response.usage`
- arrays of the objects above
- JSONL files where each line is one object

## Example

```json
{
  "id": "resp_123",
  "usage": {
    "input_tokens": 180,
    "output_tokens": 96,
    "total_tokens": 276,
    "input_token_details": {
      "cached_tokens": 48
    },
    "output_tokens_details": {
      "reasoning_tokens": 22
    }
  },
  "metadata": {
    "scenario": "cold-start refactor task"
  }
}
```

## CLI

```bash
plugin-eval analyze ./skills/my-skill --observed-usage ./runs/responses.jsonl
plugin-eval measurement-plan ./skills/my-skill --observed-usage ./runs/responses.jsonl --format markdown
```

## Interpretation

- Static budgets remain the deterministic local estimate.
- Observed usage adds a second signal based on real sessions.
- The tool compares `trigger_cost_tokens + invoke_cost_tokens` against the observed average input tokens.
- Cached and reasoning tokens are reported when present so warm-cache runs do not get mistaken for cold-start runs.
