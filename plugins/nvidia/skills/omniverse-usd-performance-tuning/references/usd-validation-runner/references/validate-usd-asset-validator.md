<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Validate USD Asset Validator

## Purpose

Use this validation reference when a stage or asset needs executable NVIDIA
Omniverse Asset Validator coverage. This is a validation-only reference: it
reports issues and recommended next steps, but does not apply fixes unless
explicitly requested.

## Prerequisites

- Run `setup-usd-performance-tuning` first to select a Kit or standalone validation runtime.
- Confirm the target is a USD asset path or asset directory. If basic USD
  viability is unknown, first perform the runner's minimum-openability check:
  stage opens, root/default prim is valid enough for the task, asset paths
  resolve, and scale/up-axis metadata is known or recorded as missing.
- Require either a Kit runtime with `omni.asset_validator.core` or a standalone `omniverse-asset-validator` environment. Install or select a runtime before reporting `blocked_missing_dependency`.
- For unknown, customer-scale, or structurally large assets, require explicit
  user approval before running the default full-stage Asset Validator rule set.
  The default path is minimum-openability plus targeted rules/categories.

## Runtime Selection

First resolve the runtime with `setup-usd-performance-tuning`. There are two
supported paths:

- **Kit path**: use the selected Kit/USD Composer/Kit venv runtime and run
  Asset Validator through `omni.asset_validator.core` inside that same Kit
  process. Do not require `uv` or `omni_asset_validate` on `PATH` for this path.
- **Standalone path**: use a project-managed `omniverse-asset-validator`
  environment. If that standalone environment is missing, invoke
  `install-asset-validator-standalone`.

Do not use the Scene Optimizer package's bundled
`validator-venv/bin/omni_asset_validate` as the preferred Asset Validator
runtime. That venv is package-local and has been observed without `numpy`,
which can make validation much slower on large USD stages. Prefer a
project-managed environment that can import both `omniverse-asset-validator`
and the selected Scene Optimizer package.

Report `blocked_missing_dependency` only when neither path is available and the
missing runtime cannot be installed or selected.

## Kit Path

Use this path when setup returned `ready-kit`, when SO validators are needed, or
when validating remote `omniverse://` assets from the same authenticated Kit
runtime.

> **Standalone is the preferred runtime.** The standalone path is lighter (no
> Kit overhead), deterministic, and achieves the same validator coverage: SO
> validators auto-register via `@register_rule` decorators when both
> `omniverse-asset-validator` and the SO package are importable in the same
> Python environment. Fall back to Kit when standalone is unavailable or when
> render-time profiling is needed (Kit-only capability).

1. Use the Python launcher selected by setup:
   - Classic Windows Kit: `<kit>\python.bat`
   - Classic Linux Kit: `<kit>/python.sh` or `<kit>/python`
   - Windows Kit venv: `<venv>\Scripts\python.exe`
   - Linux Kit venv: `<venv>/bin/python`
2. Set `OMNI_KIT_ACCEPT_EULA=yes`.
3. Start Kit with `--no-window` and `--enable omni.asset_validator.core`.
4. Validate through `omni.asset_validator.core.ValidationEngine`.

Minimal Kit pattern:

```python
import os

os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "yes")

try:
    from kit_app import KitApp
except ImportError:
    from omni.kit_app import KitApp

app = KitApp()
app.startup(["--no-window", "--enable", "omni.asset_validator.core"])

from omni.asset_validator.core import ValidationEngine

asset_abs = "/path/to/asset.usd"
engine = ValidationEngine()
engine.disable_all_rules()
engine.enable_rules("omni.asset_validator.DefaultPlugin.StageMetadataChecker")
results = engine.validate(asset_abs)
issues = results.issues() if callable(results.issues) else results.issues

print("ASSET_VALIDATOR_ISSUES", len(issues))
app.shutdown()
```

If Scene Optimizer performance validators are also required, use
`so-run-validators` after setup verifies `omni.scene.optimizer.core` in the same
Kit runtime.

## Standalone Path

Use this path when the user chooses standalone validation or no Kit runtime is
available. Use a project-managed `omniverse-asset-validator` install created or
verified by `install-asset-validator-standalone` in the same venv where the SO
package is on PYTHONPATH. SO validators auto-register via `@register_rule`
decorators: no manual `register_all()` call is needed for rule discovery. For
targeted or category-scoped runs, select registered rule classes with
`CategoryRuleRegistry` and enable them with `ValidationEngine(init_rules=False)`
plus `enable_rule()`.

Do not use the SO bundled `validator-venv` — it may lack `numpy` and is
slower on large stages.

## Workflow

1. Confirm the input is a USD asset path or an asset directory.
2. Confirm the minimum-openability check has passed, or run it first when
   basic USD viability is unknown.
3. Choose the narrowest Asset Validator scope that answers the request:
   targeted rule, targeted category, or explicit full-stage pass. For
   performance work, prefer rules/categories that can change the
   optimization plan; do not use a full-stage default sweep as the
   preliminary baseline.
4. For large assets where full-stage coverage is too expensive but validation
   signal is still useful, use the *Masked-Stage Spot Check Pattern* below on
   representative prims/subtrees before escalating to a full sweep.
5. If the chosen scope is a default full-stage pass on an unknown,
   customer-scale, or structurally large asset, stop and ask for approval.
   Name the risk plainly: long runtime, high log/report volume, and possible
   repeated issue rows. Offer targeted category/rule checks as the recommended
   alternative.
6. Run validation with `validate-usd-asset-validator`.
7. Normalize issues by severity, rule, message, location, and suggested fix
   when available. For high-volume findings, summarize by rule and target
   class rather than dumping every repeated issue into the user-facing report.
8. If the raw Asset Validator report is large, summarize it with the
   *Large Report Summarization* policy below before reading results into
   context.
9. Fail the report on Asset Validator errors or failures.
10. Warn on Asset Validator warnings unless the active workflow profile promotes them to failures.
11. Hand off performance-oriented findings to `so-run-validators` /
   `so-interpret-validators`. For external domain profiles or package
   conformance, route to the owning external workflow rather than adding those
   references here.

## Timeout and Approval Policy

All validation cost-control policy (full-sweep approval gate, timeout
guidance, spot-check thresholds) lives in
`validation-scoping.md` → *Full-Sweep Approval Gate* and
*Decision Tree*. Apply those rules before any full-stage invocation.

When a timeout is used, record `timeout_seconds` and `timeout_reason`. If the
validator times out, report `status: TIMEOUT` and keep partial logs/artifacts
for follow-up.

## Standalone CLI Pattern

Project-managed standalone environment:

```bash
omni_asset_validate --help
omni_asset_validate asset.usda --category Geometry --csv-output geometry-report.csv
```

Use only the output flags advertised by the selected runtime. Some versions
or wrappers also support JSON output; when they do not, CSV is the
conservative standalone artifact.

Treat category-scoped CLI invocations as scoped full-stage traversals. On large
or unknown-size assets, apply `validation-scoping.md` first: prefer masked
spot checks, or run each category/rule with an explicit wall-clock budget and
record any timeout.

Do not use a bare default invocation such as
`omni_asset_validate asset.usda --csv-output asset-validator-report.csv` on a
large or unknown asset until the full-sweep approval gate has passed. Do not use
`--fix` unless the user explicitly asks for auto-repair behavior.

## Standalone Python API Pattern

Use the Python API from the selected standalone environment when structured
issue extraction is needed:

```python
from omni.asset_validator import ValidationEngine

engine = ValidationEngine()
results = engine.validate("asset.usda")
issues = results.issues() if callable(results.issues) else results.issues
```

## Masked-Stage Spot Check Pattern

Policy, sample selection rules, and implementation pattern live in
`validation-scoping.md` → *Masked-Stage Spot Checks*. Use that
reference for the canonical `Usd.Stage.OpenMasked()` pattern, mesh coverage
floor (≥25%), and sample manifest fields.

Inside Kit, use `omni.asset_validator.core.ValidationEngine` instead of the
standalone import. For a live Kit stage, pass both root and session layers:

```python
default_prim = original_stage.GetDefaultPrim()
if default_prim:
    mask.Add(default_prim.GetPath())
masked_stage = Usd.Stage.OpenMasked(original_stage.GetRootLayer(), original_stage.GetSessionLayer(), mask)
if default_prim and not masked_stage.GetDefaultPrim().IsValid():
    raise RuntimeError(f"masked stage excluded default prim {default_prim.GetPath()}")
```

## Large Report Summarization

Apply this policy before reading any Asset Validator JSON, CSV, stdout, or log
artifact into agent context.

First inspect artifact size (`wc -c` on POSIX, `Get-Item <path> | Select
Length` in PowerShell). Treat the artifact as large when it is over 5 MB, when
it has more than 10,000 CSV rows, or when it was produced by a full-stage pass
over an unknown or customer-scale asset. A 166 MB validation report is always a
large artifact.

For large artifacts, keep the raw report on disk and create or use a compact
summary first:

- If a packaged summarizer exists for the selected runtime, run it and read
  only its compact JSON output.
- If no summarizer exists, create a temporary stdlib-only script beside the
  artifact (for example `<artifact_dir>/_summarize_asset_validator_report.py`).
  The script is a run artifact, not repository content, unless the user
  explicitly asks to add tooling.
- For CSV reports, stream rows with Python's `csv.DictReader`; do not load the
  whole file or print raw rows.
- For JSON reports, parse in the helper process and emit compact counts. It is
  acceptable for the helper process to load JSON if the runtime has enough
  memory, because the raw JSON still never enters agent context. If the JSON is
  too large or the shape is unknown, emit top-level keys and an error summary,
  then ask for a CSV export or narrower rule/category run.

The compact summary should include:

- `report_path` and `report_bytes`
- `issue_counts` by severity
- top rules/categories by issue count
- grouped failures by `(rule, severity, message, suggestion)`
- up to 10 example locations per group
- `truncated: true|false`
- parse errors or skipped records, if any

Read only that compact summary into context. The final user-facing validation
report may include capped examples and artifact paths, but it must not include
the full raw `issues` list when the raw report is large.

## Categories

Common categories include:

- `Basic`
- `Geometry`
- `Layer`
- `Layout`
- `Material`
- `Physics`
- `Other`

## Output Report

Reports should include:

- `asset_path`
- `validator_skill`
- `validator_tool`
- `passed`
- `categories`
- `rules`
- `issue_counts`
- `issues`
- `timeout_seconds`
- `timeout_reason`
- `warnings`
- `errors`
- `next_step`

## Pass/Fail Policy

Fail when:

- the Asset Validator dependency is missing
- the asset cannot be opened by Asset Validator
- any issue has severity `ERROR` or `FAILURE`

Warn when:

- issues have severity `WARNING`
- the selected category or rule set is narrower than the requested validation goal
- auto-fix suggestions exist but were not applied

## Limitations

- This validation reference reports Asset Validator results only; it does not apply `--fix` or repair USD content unless the user explicitly asks for auto-repair behavior.
- Rule coverage depends on the selected Kit or standalone Asset Validator version and installed categories.
- Scene Optimizer performance validators are separate and should run through `so-run-validators` when setup verifies `omni.scene.optimizer.core`.
- Remote `omniverse://` targets require an authenticated Kit runtime; standalone validation is for local paths.
- Masked-stage spot checks are optimization evidence, not a substitute for a
  full conformance pass when the user asks for formal validation coverage.

### Payload Loading Behavior

The Asset Validator discards `StageLoadRules` and re-opens with `LoadAll` —
all payloads are loaded regardless of caller configuration. `StagePopulationMask`
IS preserved (`OpenMasked` works for scoping). Do not rely on `LoadNone` for
validation scoping; use `OpenMasked` or validate standalone files.

See `validation-scoping.md` §"LoadRules Behavior With the Asset Validator" for
full consequences and workarounds.

## Troubleshooting

- If neither runtime path is available, run `setup-usd-performance-tuning` again or use `install-asset-validator-standalone` to create a project-managed standalone validator.
- If the SO bundled validator venv is missing dependencies such as `numpy`, select the Kit path or project-managed standalone path and record any fallback limitation.
- If validation times out on a large stage, keep the partial report/log, narrow the scope, or ask the user for an explicit larger time budget.
- If Asset Validator passes but external profile/package conformance is still
  needed, hand off to that owning external workflow and keep this package's
  report focused on USD/Asset Validator evidence.

## Next Steps

Use this handoff:

| Asset intent | Next skill |
|---|---|
| Performance validation needed | `so-run-validators` |
| Findings need operation recommendations | `so-interpret-validators` |
| External profile/package conformance needed | Owning external validation workflow |
