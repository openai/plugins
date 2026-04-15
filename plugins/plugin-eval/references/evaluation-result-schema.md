# Evaluation Result Schema

The canonical `plugin-eval` result is JSON with this top-level shape:

```json
{
  "schemaVersion": 1,
  "tool": {
    "name": "plugin-eval",
    "version": "0.1.0"
  },
  "createdAt": "2026-04-07T00:00:00.000Z",
  "target": {
    "kind": "skill",
    "path": "/abs/path/to/target",
    "entryPath": "/abs/path/to/target/SKILL.md",
    "name": "target-name",
    "relativePath": "fixtures/minimal-skill"
  },
  "summary": {
    "score": 92,
    "grade": "A",
    "riskLevel": "low",
    "topRecommendations": []
  },
  "budgets": {
    "method": "estimated-static",
    "trigger_cost_tokens": {
      "value": 48,
      "band": "good",
      "thresholds": {
        "goodMax": 48,
        "moderateMax": 92,
        "heavyMax": 150
      },
      "components": []
    },
    "invoke_cost_tokens": {
      "value": 220,
      "band": "good",
      "thresholds": {
        "goodMax": 220,
        "moderateMax": 480,
        "heavyMax": 900
      },
      "components": []
    },
    "deferred_cost_tokens": {
      "value": 180,
      "band": "good",
      "thresholds": {
        "goodMax": 180,
        "moderateMax": 520,
        "heavyMax": 1200
      },
      "components": []
    },
    "total_tokens": {
      "value": 448,
      "band": "good"
    }
  },
  "checks": [],
  "metrics": [],
  "artifacts": [],
  "extensions": [],
  "improvementBrief": {}
}
```

The evaluation result may also include:

- `observedUsage`
- `measurementPlan`

Separate benchmark runs use a `benchmark-run` payload with:

- `mode`
- `config`
- `usageLogPath`
- `summary`
- `scenarios[]`
- `nextSteps[]`

## Checks

Checks use:

- `id`
- `category`
- `severity`
- `status`
- `message`
- `evidence[]`
- `remediation[]`
- `source`

## Metrics

Metrics use:

- `id`
- `category`
- `value`
- `unit`
- `band`
- `source`

## Extensions

`extensions[]` holds metric-pack outputs. Each extension records:

- `name`
- `version`
- `manifestPath`
- `checks[]`
- `metrics[]`
- `artifacts[]`
