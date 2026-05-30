# USD Validation Runner (master router)

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## When to Use

Use this reference for validation-only requests or when the performance workflow reaches the validation-routing phase.

## Instructions

1. Identify whether the request is validation-only or a validation phase inside the optimization workflow.
2. Select the smallest validation stack that can change the user-visible decision or operation plan.
3. Ask before full Asset Validator sweeps or Tier 3 expensive cross-component checks.
4. Route execution to the owning validation reference or skill and preserve evidence paths for later reporting.


## Pre-flight Checklist

Before running validators, re-read and confirm:

- [ ] `references/validation-scoping.md` — tier selection, phase-aware subsets,
   deferred validators, full-sweep approval gate.
- [ ] SA report's `phase_recommendation` and `summary_counts` drive tier selection.
- [ ] Apply `runtime-artifact-token-budget.md` for large CSV/log output.
- [ ] Route findings to `so-interpret-validators` for op-chain construction —
   do not map findings to ops yourself.
## Output Format

Return a scoped validation plan or validation summary naming the selected validator stack, skipped expensive checks, approval gates, artifact paths, and findings that affect the optimization plan.

## Purpose

Use this reference whenever a workflow needs to surface USD validity or performance
validator issues. It picks the smallest validation stack that can affect the
optimization plan, records the evidence contract, and routes concrete execution
to the owning skill or reference.

This reference **does not** execute optimization operations and **does not** choose fix strategies.

Use this reference as the entry point for validation-only requests such as
"validate this USD", "run Asset Validator", or "show validation issues". For
broad performance diagnosis, slow loading, high memory, low FPS, or "what
should I optimize?", start with
`omniverse-usd-performance-tuning` so structure assessment can scope validation
before expensive validator runs.

For `omniverse://` targets, start with `omniverse-authentication` before this
skill attempts runtime probing or stage open.

Tier tables and the JSON plan template live in
`references/validation-scoping.md` under this reference. This router points at that
reference for tier detail rather than duplicating it, which keeps validation
policy portable for future SO/OAV repo splits.

## Prerequisites

- Target stage or asset paths and resolver context.
- Available validator runtime (Omni Asset Validator inside Kit, project-managed AV install, or installed Scene Optimizer APIs).
- Artifact directory for logs, CSV/JSON findings, and provider summaries.
- Baseline, waiver, or failure policy for pre/post processing gates.
- (For perf-stack scoping) `usd-structure-assessment` report with `phase_recommendation` and `flagged_assets`.

## Session-start runtime gate (mandatory when this is the entry skill)

If this reference is the **entry skill** for the user's request (i.e., the
agent invoked `/usd-validation-runner` directly rather than through
`omniverse-usd-performance-tuning`), run the session-start gate from
`skills/omniverse-usd-performance-tuning/references/setup-usd-performance-tuning/references/runtime-context-header.md` *Mandatory session-start gate*
before any routing. The gate determines `output_path`, checks
`<output_path>/setup-preflight.json`, invokes `setup-usd-performance-tuning`
if the preflight is missing, then surfaces Format A + the 4-option
confirmation. Do not pick a validator stack until the user has
confirmed the runtime.

If invoked **downstream of an entry skill that already fired the gate
in the same session**, skip the gate and proceed.

## Limitations

- Validation depends on tools installed outside this repo.
- Scene Optimizer validation results are valid only after imports and checker classes are verified in the active runtime.
- Validation evidence is not cleanup; auto-fixes require separate change recording.

## Troubleshooting

- If `omni_asset_validate` is unavailable, record it as missing rather than fabricating a pass.
- If Scene Optimizer validator imports fail, do not report SO-specific results.
- If the bundled `validator-venv` is slow or lacks dependencies, prefer a Kit or project-managed Asset Validator environment.

---

## Validator Stack Matrix

The router picks one or more stacks based on the intent and the structure assessment `phase_recommendation`. Each stack lists the owned reference that describes the concrete validation command; this reference orchestrates the routing.

**All validation cost-control policy lives in
`references/validation-scoping.md`.** That reference owns tier tables,
the full-sweep approval gate, deferred-validator rules, spot-check
policy, phase-aware subset selection, and the per-rule timeout pattern.
Read it when building a perf-stack plan. The key principles:

- Structure assessment first — never start with a full default AV sweep.
- Full-sweep approval gate — ask before a default rule set on large/unknown assets.
- SO analysis stays in the validation plan regardless of execution path.
- Spot-check before dropping signal — masked-stage with ≥25% mesh coverage.

### Pre-Mutation USD Stack

For "is this asset USD-correct enough to mutate?", run only the checks needed
to protect the requested mutation.

| Step | Owner | When |
|---|---|---|
| 1 | Inline minimum-openability check | Always before mutation. Confirm the stage opens, root/default prim is valid enough for the task, asset paths resolve, and scale/up-axis metadata is known or recorded as missing. |
| 2 | `references/validate-usd-asset-validator.md` | When executable NVIDIA Omniverse Asset Validator coverage is needed. Scope by targeted rules/categories unless the user explicitly approves a full sweep. |
| 3 | External profile/package validators | Only when the user explicitly requests a domain profile such as SimReady or a package-validation workflow. Do not keep those command references in this package. |

### Performance stack (scoped)

For "is this asset performant?" The chain is: scope -> run -> interpret. Tier and phase-aware scoping live in `references/validation-scoping.md`; the router instructs the agent to load that reference and emit a plan, then invoke the downstream tools.

| Step | Tool / reference | When |
|---|---|---|
| 1 | (Read `references/validation-scoping.md`) | Build the tier plan from the structure assessment's `flagged_assets` + `phase_recommendation`. |
| 2 | `so-run-validators` | Execute the tier plan against the asset. |
| 3 | `so-interpret-validators` | Read artifacts, classify findings (T1/T2/T3), recommend fixes. |

### Phase-aware subset selection

Owned by `references/validation-scoping.md` → *Decision Tree*. Document the
chosen subset in the validation plan so Phase 6 re-validation can reproduce
the same scope.

---

## Routing decision

For a given request, pick the stack(s) using this table:

| Intent | Stacks |
|---|---|
| "Validate this USD before any mutation." | Pre-mutation USD stack: minimum-openability plus targeted Asset Validator coverage when needed. |
| "What's wrong with this asset?" (broad performance ask) | `usd-structure-assessment` first, then Performance stack scoped per the structure assessment. Add pre-mutation USD stack only when the request is about USD validity or mutation safety. |
| "Run perf validators only." | Performance stack only. |
| "Validate the optimized output (Phase 6 re-validation)." | Same stacks that ran in Phase 2c, for a fair before/after comparison. |
| "Validate a SimReady package/profile." | Defer to the external SimReady/Foundation validation workflow; keep only local USD and performance evidence in this package. |

If intent is ambiguous, ask the user before expanding scope - especially before
invoking Tier 3 perf validators or a default full-stage Asset Validator sweep
(both can be very slow and can produce very large logs/reports).

For performance work, the validation output should be a compact
operation-oriented summary, not a raw issue dump. Use
`so-interpret-validators/references/rule-reference.md` for rule-to-operation
mapping instead of maintaining another mapping in this router.

---

## Commands

`references/validate-usd-asset-validator.md` owns Asset Validator runtime
details. `so-run-validators` owns Scene Optimizer performance-validator
execution. This router keeps only the common direct invocation shape:

Base Asset Validator (used by `validate-usd-asset-validator`). Probe the
selected runtime before using optional output flags; use JSON output when
the selected runtime advertises it, otherwise fall back to CSV. The commands
below are invocation shapes, not default scope choices. A bare full-stage
invocation is allowed only after the full-sweep gate has been approved.

```bash
omni_asset_validate --help
omni_asset_validate /path/to/asset.usd \
  --category Geometry \
  --csv-output /path/to/artifacts/issues.csv
```

Minimum openability baseline is a USD-open check, not a default Asset
Validator run:

```python
from pxr import Usd

stage = Usd.Stage.Open("/path/to/asset.usd")
if stage is None:
    raise RuntimeError("stage did not open")
root = stage.GetDefaultPrim()
print({
    "opened": True,
    "default_prim": root.GetPath().pathString if root else None,
    "up_axis": stage.GetMetadata("upAxis"),
    "meters_per_unit": stage.GetMetadata("metersPerUnit"),
})
```

For SO-specific validators, follow `so-run-validators`; SO validator rules
auto-register via `@register_rule` decorators when both packages share the
same Python environment.

### Programmatic per-rule API

For one-rule-at-a-time validation (used by the per-rule timeout pattern in
`references/validation-scoping.md`), drive the engine directly:

```python
import omni.scene.optimizer.validators  # auto-registers SO rules
from omni.asset_validator import CategoryRuleRegistry, ValidationEngine
from pxr import Usd

registry = CategoryRuleRegistry()
rule = next(
    rule
    for rule in registry.get_rules("Usd:Performance")
    if rule.__name__ == "PrimitiveFitChecker"
)

engine = ValidationEngine(init_rules=False)
engine.enable_rule(rule)
stage = Usd.Stage.Open("path/to/asset.usd")
results = engine.validate(stage)                           # synchronous
for issue in results.issues():
    ...
```

Inside Kit, import `omni.asset_validator.core` instead of `omni.asset_validator` (the `.core` submodule is the in-Kit name). The standalone package uses the plain `omni.asset_validator` import.

Use this API when you need:

- Per-rule timeouts on a large stage (see `references/validation-scoping.md` *Per-rule timeout pattern*).
- A single rule's findings without running the full default set.
- Cross-runtime parity checks (same stage, same rule, both Kit and standalone).

Do not route validation through the Scene Optimizer package's bundled
`validator-venv` — it may lack `numpy`, making large-stage validation slow.
Use a project-managed venv with both `omniverse-asset-validator` and the SO
package on PYTHONPATH.

---

## Required gates

Pre-processing (before any mutation):

- Stage opens.
- Asset paths resolve.
- Minimum-openability and selected Asset Validator checks complete.
- Known blocker findings are either fixed or waived.

Post-processing (Phase 6 re-validation):

- Stage opens.
- Validation is no worse than baseline unless explicitly accepted.
- Generated outputs are recorded.
- Processor report and validation report are attached to the optimization plan.

---

## Output

Emit `validation-report.json` matching `scripts/validation-report.schema.json`. The report must point to provider artifacts including `issues.csv`, `provider-summary.json`, and `run.log`, and include the chosen tier/phase scoping so Phase 6 can reproduce it.

---

## Rules

- Validation is evidence, not cleanup by itself.
- Convert findings into candidate operations via
  `so-interpret-validators/references/rule-reference.md`; do not hand the
  user raw validator jargon as the recommendation.
- Do not auto-fix without recording which layers or files changed.
- Do not continue after structural USD failures unless the plan is diagnosis-only.
- Do not call Scene Optimizer operation skills until validation evidence has been captured or the user has explicitly chosen to proceed without it.
- All cost-control rules (tiers, gates, thresholds) live in
  `references/validation-scoping.md`. Do not invent thresholds inline.

## References

- `references/validation-scoping.md` - tier 1/2/3 tables, JSON plan template, scene-aware adjustment, phase-aware subset rules. Read this when building a perf-stack plan.
- `skills/omniverse-usd-performance-tuning/references/usd-validation-runner/references/so-run-validators/references/infrastructure.md` - SO validator infrastructure (programmatic API, REQUIRES_MESH cache, entry-point allow-list, CLI gotchas, libusd alignment). Read this when debugging SO validator setup.
- `skills/omniverse-usd-performance-tuning/references/workflow.md` - canonical 7-phase flow context for where validation sits.
