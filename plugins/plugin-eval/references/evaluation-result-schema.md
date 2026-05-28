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
    "method": "estimated-static-policy-aware",
    "invocation_policy": {
      "implicit_skill_count": 1,
      "explicit_only_skill_count": 2,
      "implicit_skills": ["router"],
      "explicit_only_skills": ["specialist-a", "specialist-b"]
    },
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
    "explicit_only_invoke_cost_tokens": {
      "value": 900,
      "band": "heavy",
      "thresholds": {
        "goodMax": 220,
        "moderateMax": 480,
        "heavyMax": 900
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

For plugins or skills with `agents/openai.yaml` policies, `budgets.method` may be
`estimated-static-policy-aware`. In that mode, `policy.allow_implicit_invocation: false`
excludes the skill from `trigger_cost_tokens` and `invoke_cost_tokens`. The excluded skill
payloads are reported under `explicit_only_invoke_cost_tokens` for visibility, but they are
not scored as implicit active context.

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
