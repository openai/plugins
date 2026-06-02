# Metric Pack Manifest

Metric packs are user-authored local evaluators that output `plugin-eval`-compatible findings.

## Manifest Shape

```json
{
  "name": "team-rubric",
  "version": "1.0.0",
  "supportedTargetKinds": ["skill", "plugin"],
  "command": ["node", "./emit-team-rubric.js"]
}
```

## Runtime Contract

- The manifest is passed to `plugin-eval analyze --metric-pack <manifest.json>`.
- The command runs from the manifest directory.
- The target path and target kind are appended as CLI arguments.
- The process also receives:
  - `PLUGIN_EVAL_TARGET`
  - `PLUGIN_EVAL_TARGET_KIND`
  - `PLUGIN_EVAL_METRIC_PACK_MANIFEST`

## Output Contract

The metric pack must print JSON to stdout in this shape:

```json
{
  "checks": [
    {
      "id": "team-style",
      "category": "custom",
      "severity": "warning",
      "status": "warn",
      "message": "Custom rubric finding",
      "evidence": ["detail"],
      "remediation": ["fix detail"]
    }
  ],
  "metrics": [
    {
      "id": "team-score",
      "category": "custom",
      "value": 4,
      "unit": "points",
      "band": "good"
    }
  ],
  "artifacts": []
}
```

## Merge Rules

- Metric-pack findings are stored under `extensions[]`.
- Metric packs do not overwrite the core summary.
- Metric packs should use unique IDs so repeated runs remain easy to compare.
