<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Validation Scoping — Canonical Cost Guardrails

> **This is the single source of truth** for validation cost control in the
> digitaltwin-performance-skill workflow. Other references
> (`usd-validation-runner`, `validate-usd-asset-validator`, `workflow.md`)
> point here for tier detail, approval gates, and scoping rules rather than
> duplicating them.

---

## Decision Tree (read this first)

```
┌─ What did structure assessment say? ─────────────────────────────────────┐
│                                                                          │
│  phase_recommendation = "structuring"                                    │
│    → Structural validators only (do not validate geometry about to be    │
│      restructured)                                                       │
│                                                                          │
│  phase_recommendation = "optimization"                                   │
│    → Tier 1: always (full stage)                                         │
│    → Tier 2: per flagged asset (or 10% sample if budget allows)          │
│    → Tier 3: only on specifically flagged targets, ALWAYS ask first      │
│                                                                          │
│  phase_recommendation = "already_optimized"                              │
│    → Tier 1 only; ask user before expanding scope                        │
│                                                                          │
│  No structure assessment available                                       │
│    → Run structure assessment first. Do not begin with validators.       │
│                                                                          │
├─ Is a full-stage Asset Validator sweep requested? ───────────────────────┤
│                                                                          │
│  Trigger the FULL-SWEEP APPROVAL GATE (§ below) when ANY of:            │
│    • Stage size is unknown                                               │
│    • Customer-scale factory/CAD/BIM/MEP/plant/city                       │
│    • SA reports large prim/mesh/prototype/material counts                │
│    • Request is performance triage (not formal conformance)              │
│                                                                          │
│  Offer: targeted rules (recommended) | full sweep + timeout | defer      │
│                                                                          │
├─ Is full-stage AV too expensive but signal is still needed? ─────────────┤
│                                                                          │
│  Use MASKED-STAGE SPOT CHECKS (§ below)                                  │
│    • ≥25% mesh coverage or explain why not                               │
│    • Label as sample evidence, not full-stage evidence                   │
│                                                                          │
├─ Is a full-stage category sweep planned on a very large mesh count? ─────┤
│                                                                          │
│  Do NOT run uncapped Basic/Layer/Geometry/etc. over the whole stage.      │
│  Use masked spot checks, or run each selected category/rule in a          │
│  subprocess with an explicit wall-clock budget and report TIMEOUT rows.   │
│                                                                          │
├─ Stage has >30K prototype meshes and per-rule attribution is needed? ────┤
│                                                                          │
│  Use PER-RULE TIMEOUT pattern (§ below)                                  │
│                                                                          │
├─ Validating post-decompose targets (payloads, assembly root)? ───────────┤
│                                                                          │
│  Each target re-enters THIS tree independently (§ Post-Restructure       │
│  Validation Strategy). Treat each payload/assembly as a fresh validation │
│  request — tier selection, approval gate, and spot-check threshold apply │
│  based on THAT target's prim count, not the original composed stage.     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Purpose

Translate structure assessment findings into a concrete validation plan that
avoids running expensive validators on assets that do not need them. Use this
after `usd-structure-assessment` produces its report and before invoking
`so-run-validators`.

## Inputs

- Structure assessment report: `flagged_assets`, `validation_scope`, `phase_recommendation`.
- User time/resource budget and approval posture for expensive checks.
- Goal type: diagnosis-only or diagnosis plus execution.
- Validator names available in the installed runtime.

---

## Validator Tiers

### Tier 1: Fast (seconds per asset)

Metadata and traversal only. Safe to run on all assets.

- `printStats`
- `countVertices`
- `rtxMeshCount`
- `removeSmallGeometry` (analysis mode)
- `findFlatHierarchies` (analysis mode)
- `pruneLeaves` (analysis mode)
- `removePrims` (analysis mode — orphaned overs)

### Tier 2: Medium (seconds to minutes per asset)

Per-mesh inspection. Run on flagged assets or all if budget allows.

- `meshCleanup` (analysis mode)
- `optimizeMaterials` (analysis mode)
- `removeUnusedUVs` (analysis mode)
- `computeExtents` (analysis mode)
- `generateNormals` (analysis mode)

### Tier 3: Expensive (minutes per asset, minutes to hours cross-component)

Spatial or pairwise analysis. Run only on specifically flagged assets/pairs.
**Always ask the user before running.**

- `deduplicateGeometry` (analysis mode) — on repetition-flagged assets
- `findCoincidingGeometry` (analysis mode) — on repetition-flagged pairs
- `findOccludedMeshes` (analysis mode) — on containment-flagged pairs
- `fitPrimitives` (analysis mode) — on outlier-flagged or primitive-like assets
- `sparseMeshes` (analysis mode) — on outlier-flagged assets

### Deferred to Post-Optimization Pass

These validators are expensive AND their findings do not influence operation
selection — the corresponding operations already run unconditionally based on
structural signals. Running these first adds cost without changing the plan.

| Validator | Why deferred |
|---|---|
| `optimizePrimvars` / `IndexedPrimvarChecker` | `removeUnusedUVs` + `optimizePrimvars` already run for CAD/BIM. Checker produces 100K+ warnings (~6 min, ~156 MB) confirming what SA already told you. |
| `SceneOptimizerNonManifoldChecker` / `ManifoldChecker` | Per-edge topology; only relevant for simulation targets. Visualization-only workflows skip entirely. |
| `SceneOptimizerUnusedUVsChecker` | Same signal as IndexedPrimvar — the operation is already selected. |

**Exception:** If the assessment does NOT indicate these operations should run
(e.g., a non-BIM scene where UV removal is uncertain), DO run the validators —
their findings provide the evidence to justify the operation.

---

## Full-Sweep Approval Gate

Trigger before any command that enables the default AV rule set over the whole
composed stage when ANY condition holds:

1. Stage size is unknown.
2. Target is customer-scale factory/CAD/BIM/MEP/plant/city.
3. SA reports large prim/mesh/prototype/material counts, many
   payloads/references, or a monolithic root layer.
4. Request is performance triage rather than formal conformance.

**Offer the user three options:**

- **Recommended:** minimum-openability + targeted category/rule checks.
- **Full sweep:** default AV rule set with explicit timeout and artifact dir.
- **Defer:** skip AV until after SA or after mutation.

When approved, record `scope: "full_stage"`, `approved_by_user: true`,
`timeout_seconds`, and artifact paths. If not approved, do not launch.

---

## Scoping Rules

1. **Structure assessment is the first filter.** Use `summary_counts` plus
   duplicate-hierarchy candidates to decide which validators can change the
   optimization plan. Do not start with a full default AV sweep.

2. **Start with cheap, optimization-oriented evidence.** Duplicate
   geometry/materials, empty leaves, flat hierarchies, high vertex/mesh count
   summaries, unused UVs (when tolerant of noise), small/zero-extent geometry
   (when scoped).

3. **Keep SO analysis in the validation workflow.** Use AV-registered SO
   checkers when available; otherwise run equivalent read-only SO analysis via
   `so-run-validators` in the same plan. Do not treat it as a separate phase.

4. **Run Tier 2 per-asset** on:
   - All assets flagged by SA (any reason).
   - A sample of unflagged assets if budget allows (e.g., 10% random).

5. **Run Tier 3 only on flagged targets:**
   - `deduplicateGeometry`: only `repetition`-flagged.
   - `findOccludedMeshes`: only `containment`-flagged pairs.
   - `fitPrimitives` / `sparseMeshes`: only `outlier_extent` or
     primitive-like. For CAD/BIM/MEP, pipe/duct/conduit/fitting names or high
     prototype mesh counts are enough evidence. Heavy existing instancing does
     not remove this signal.

6. **Cross-component validators** require the composed stage with relevant
   payloads visible. Use `Usd.Stage.OpenMasked()` with a population mask
   covering only the flagged pair (and their dependency closures), OR run
   the validator via standalone `Usd.Stage.Open()` on each target file.
   Do NOT rely on `LoadNone` + selective `stage.Load()` — the Asset Validator
   discards load rules and re-opens with LoadAll (see §"LoadRules Behavior
   With the Asset Validator" below).

7. **If no assets are flagged**: Tier 1 only. Report the scene as likely
   well-structured. Ask before running Tier 2-3.

8. **Defer noisy/slow full-stage rules.** Do not run
   `IndexedPrimvarChecker`, `CoincidingGeometryChecker`, `ExtentsChecker`,
   `AlmostExtremeExtentChecker`, `ArticulationChecker`, `ColliderChecker`, or
   `KindChecker` globally in the preliminary pass. Run them only when the
   scope makes their output actionable (physics checks for simulation assets,
   coinciding geometry for repetition-suspect groups, etc.).

9. **Cap selected category sweeps on large stages.** A category-scoped AV run
   is still a full-stage traversal for that category. If
   `summary_counts.mesh_count` or prototype/proxy mesh contribution is very
   large, do not launch uncapped `Basic`, `Layer`, `Geometry`, `Material`, or
   multi-category sweeps over the full composed stage. Prefer masked-stage spot
   checks. If a category sweep is still needed, run each selected category or
   rule in its own subprocess with an explicit wall-clock budget, record
   `timeout_seconds` / `timeout_reason`, and treat partial results as scoped
   evidence rather than full conformance.

10. **Prefer summaries over issue dumps.** Summarize findings into target
   counts and operation candidates. Apply `runtime-artifact-token-budget.md`
   for CSV/log/summary handling.

---

## Scene-Aware Tier Adjustment

The static tier assignments above are defaults. Adjust based on
`phase_recommendation` and scene characteristics:

| Scene signal | Adjustment |
|---|---|
| CAD/BIM/MEP, pipe/duct-heavy, many primitive-like prototypes | Promote `fitPrimitives` analysis into first SO pass (even when heavily instanced — instancing skips mesh dedup, not prototype primitive fitting). |
| Well-structured, artistic | Promote `deduplicateGeometry` + `optimizeMaterials`; demote `fitPrimitives`. |
| Instancing ratio >80% | Skip `deduplicateGeometry`. |
| Scene has 0 extents | Always include `computeExtents`. |
| Enclosed building | Scope `findOccludedMeshes` to within-floor/within-discipline, or skip entirely. |

When `removeUnusedUVs` and `fitPrimitives` both target the same CAD/BIM
content, interpret `fitPrimitives` candidates against the post-UV-cleanup
state; a pre-cleanup `nonconstPrimvarMeshCount` bucket is still a
primitive-fit opportunity.

---

## Masked-Stage Spot Checks

> **See also:** "Post-Restructure Validation Strategy" below for how to validate
> after `apply-restructure` or `decompose-for-selective-loading`. Masked-stage
> techniques apply within that framework when individual targets (assembly skeleton
> or a single large payload) are themselves too expensive for a full sweep.

Use when full-stage AV is too expensive but prim-level findings can still
change the optimization plan. This is the preferred alternative to dropping
validation entirely on customer-scale assets.

### When to use

- Stage is customer-scale (CAD/BIM/MEP/factory/city, tens of thousands of
  prototype meshes).
- SA can identify representative candidate subtrees.
- Rule set is mostly `CheckPrim`-style geometry/material/schema checks.
- Result is optimization evidence, not formal conformance.

### Sample selection

1. Build a cheap full-stage inventory first: top branches by mesh count,
   semantic names, top prototype/fingerprint groups, material-heavy branches,
   instance-heavy branches.
2. Include all SA-flagged targets that may change the operation plan.
3. Cover **≥25% of mesh-bearing content** by mesh count, `rtxMeshCount`, or
   instance-proxy mesh contribution. If floor is impractical, record why and
   mark result as limited sample evidence.
4. Include high-risk exemplars: largest mesh, deepest hierarchy,
   material-heavy mesh, repeated module, top prototype/fingerprint family,
   dominant mesh-bearing semantic classes (pipe/duct/conduit/fitting for MEP;
   equivalent for other scenes).
5. Do not sample bare generated prototype roots unless the masked stage is
   verified to expose descendant meshes.

### Implementation

```python
from pxr import Sdf, Usd, UsdGeom
from omni.asset_validator import CategoryRuleRegistry, ValidationEngine

asset_abs = "/path/to/customer-scale.usd"
root_layer = Sdf.Layer.FindOrOpen(asset_abs)
default_prim_path = f"/{root_layer.defaultPrim}" if root_layer.defaultPrim else None

sampled_paths = ["/Root/Prototypes/PipeFamily_A", "/Root/Mechanical/Level_02/AHU_01"]
closure_paths = ["/Root/Looks", "/Root/Materials"]

mask = Usd.StagePopulationMask()
for path in [*sampled_paths, *closure_paths, default_prim_path]:
    if path:
        mask.Add(path)

stage = Usd.Stage.OpenMasked(root_layer, mask)
assert stage.GetDefaultPrim().IsValid(), "masked stage excluded default prim"

# Verify mesh coverage (proxy/prototype-aware)
mesh_count = sum(
    1 for prim in Usd.PrimRange.Stage(
        stage, Usd.TraverseInstanceProxies(Usd.PrimDefaultPredicate)
    ) if prim.IsA(UsdGeom.Mesh)
)
# Must be ≥25% of total_scene_mesh_count; raise if 0

registry = CategoryRuleRegistry()
normals_rule = next(
    rule for rule in registry.get_rules("Geometry") if rule.__name__ == "NormalsValidChecker"
)

engine = ValidationEngine(init_rules=False)
engine.enable_rule(normals_rule)
results = engine.validate(stage)
```

### Constraints

- Preserve default prim in the mask.
- Add material scopes / relationship targets when running material rules.
- Avoid stage-global / layer-global / dependency rules in spot mode.
- Label output `scope: "masked_stage_spot_check"` with sampled paths,
  semantic tags, mesh coverage %, and evidence scope.
- Reject empty samples: if proxy/prototype-aware counts report 0 meshes,
  resample instead of reporting "0 findings."

---

## Post-Restructure / Post-Decompose Validation Strategy

After `apply-restructure` (mode=restructure) or `decompose-for-selective-loading`
produces an assembly root + N payload/prototype files, do NOT open the full composed
stage with all payloads loaded for a blanket validator sweep. That re-couples what was
just decomposed and doubles validation work.

### Validation Distribution

- **Assembly skeleton** — open with `Usd.Stage.OpenMasked()` excluding payload prim
  paths. Run structural validators only: reference resolution, kind hierarchy, layer
  structure, defaultPrim, extent hints, assetInfo. Single pass.

- **Assembly root as optimization target** — if the assembly root retains mesh
  content after extraction (ground planes, shared environment geometry,
  non-extracted sub-hierarchies), it is itself a Phase 4 target. Validate and
  optimize it like any other target via the decision tree. The manifest records
  this with `target_class: "assembly_root"`.

- **Each payload/prototype (standalone)** — open each file independently with
  `Usd.Stage.Open(payload_file)`. Plan validation through the decision tree for
  each target (tier selection and approval thresholds apply per-target based on
  that target's prim count — a small payload may qualify for spot-check rather
  than a full sweep). These are independent and can run in parallel.

- **Cross-payload pairs** — open with `Usd.Stage.OpenMasked(root, mask)` covering
  only the two relevant payload subtrees. Run Tier 3 only (findCoincidingGeometry,
  etc.) per flagged pair.

### Rules

1. Validate each payload as a standalone file. Do not rely on the assembly context
   for per-payload geometry validation.
2. Validate payloads in parallel — they are independent by definition.
3. The assembly-skeleton pass confirms composition integrity (all refs resolve,
   no dangling payload arcs, kind/model hierarchy correct).
4. Cross-payload Tier 3 validators use `OpenMasked` to expose only the specific
   pair, not all payloads.
5. Report results per-target (assembly vs each payload) so the user sees which
   specific payload has issues.
6. Each target in the per-target loop re-enters THIS decision tree as if it were
   a fresh validation request — the tree's tier selection, spot-check threshold,
   and approval gate apply per-target based on that target's prim count.

### Why NOT re-compose

Opening the full composed stage with all payloads loaded for validation after
decompose:
- Defeats the purpose of decomposition (cost is the same as the original).
- Produces per-prim findings attributed to composed paths that don't map cleanly
  to individual payload files.
- Prevents parallel validation of independent payloads.
- Triggers the same cost gate the user already approved once (double-prompting).

---

## LoadRules Behavior With the Asset Validator

The Asset Validator's `ComplianceChecker` opens a **new stage** from
the input's root layer with default `LoadAll` semantics. The original stage's
load rules (e.g. `LoadNone`) are discarded.

`StagePopulationMask` IS preserved — if the input stage was opened with
`Usd.Stage.OpenMasked()`, the mask carries through to the validator's internal stage.

This is observable behaviour across current AV versions; do not assume future
releases will behave the same. Probe the AV API/version when possible.

### Consequences

- Passing a `LoadNone` stage to the AV is equivalent to passing a `LoadAll` stage.
- All payload content will be loaded and traversed regardless of the load predicate.
- `Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies())` visits everything loaded.
- Elapsed time and findings will reflect the full composed stage, not the skeleton.

### What works

- `Usd.Stage.OpenMasked()` — physically excludes prims from the stage's view. The AV
  preserves the population mask, so masked prims remain invisible to checkers.
- Opening each payload file standalone (preferred — see "Validation Distribution" above).

### What does NOT work

- `Usd.Stage.Open(root, Usd.Stage.LoadNone)` — load rules are discarded by AV.
- `stage.Load(specific_path)` after `LoadNone` — same problem, AV re-opens from root.
- Any load-state scoping strategy that relies on `StageLoadRules` being preserved.

---

## Per-Rule Timeout Pattern

For stages with very high mesh/prototype counts where total validation would
exceed the time budget. Run each category or rule in its own subprocess with an
explicit budget so a single slow checker does not consume the whole pass.

```python
import subprocess, json, sys
from omni.asset_validator import CategoryRuleRegistry, ValidationEngine
from pxr import Usd

def validate_one_rule(stage_path, category, rule_name, per_rule_budget_s):
    registry = CategoryRuleRegistry()
    rule = next(
        rule for rule in registry.get_rules(category) if rule.__name__ == rule_name
    )
    engine = ValidationEngine(init_rules=False)
    engine.enable_rule(rule)
    stage = Usd.Stage.Open(stage_path)
    results = engine.validate(stage)
    return list(results.issues())

# Driver:
RULES = [
    ("Geometry", "ManifoldChecker"),
    ("Geometry", "WeldChecker"),
]
results = {}
for category, rule_name in RULES:
    try:
        out = subprocess.run(
            [sys.executable, __file__, stage_path, category, rule_name],
            timeout=per_rule_budget_s, capture_output=True, check=True,
        )
        results[f"{category}.{rule_name}"] = json.loads(out.stdout)
    except subprocess.TimeoutExpired:
        results[f"{category}.{rule_name}"] = {
            "status": "timed-out",
            "budget_s": per_rule_budget_s,
        }
```

**When to use:** >30K prototype meshes, very large `summary_counts.mesh_count`,
suspected single-rule hang, or iterating on one rule without re-running others.
For small/medium stages, use the standard tier plan via `so-run-validators`.

---

## Output — Validation Plan JSON

```json
{
  "tier1": {
    "scope": "full_stage",
    "validators": ["printStats", "countVertices", "rtxMeshCount", "..."]
  },
  "tier2": {
    "scope": "per_asset",
    "assets": ["path/to/A.geom.usd", "path/to/B.geom.usd"],
    "validators": ["meshCleanup", "optimizePrimvars", "..."]
  },
  "tier3": {
    "scope": "targeted",
    "tasks": [
      { "validator": "findOccludedMeshes", "targets": [["CabinetA", "PipeB"]] },
      { "validator": "deduplicateGeometry", "targets": ["ChairA", "ChairB"] }
    ]
  },
  "spot_checks": {
    "scope": "masked_stage_spot_check",
    "sampled_paths": ["</Root/Prototype_A>", "</Root/Mechanical/PipeFamily_01>"],
    "mesh_coverage_percent": 28.4,
    "evidence_scope": "sample"
  },
  "skip": ["list of unflagged assets - no deep validation planned"],
  "estimated_time": "fast | minutes | long"
}
```

This plan is passed to `so-run-validators` (executor) by `usd-validation-runner` (router).

---

## Hard Rules

1. Never run all validators on all assets by default.
2. Never run Tier 3 without structural evidence from the assessment.
3. Always ask before Tier 3 cross-component checks.
4. Never start a performance workflow with a full default AV sweep.
5. Prefer masked-stage spot checks over dropping validation when full-stage
   is too expensive.
6. Always report what was skipped and why — the user may override.

---

## Duration Hints (typical: ~100K prims, ~200K meshes)

| Scope | Expected |
|---|---|
| Tier 1 (full stage) | ~5 min |
| Tier 2 (per flagged asset) | ~30 min |
| Tier 3 (cross-component) | hours — always confirm |
| Structural validators only | ~2 min |
| Masked-stage spot check | ~5-10 min |

---

## Prerequisites

- Structure assessment report (specifically `flagged_assets` and `validation_scope`).
- User time/resource budget.
- Access to validator names in the installed runtime.

## Limitations

- Scope quality depends on the structure assessment; weak evidence stays visible.
- Tier cost estimates are defaults — they scale with scene size.
- SO validator names must match the installed runtime.

## Troubleshooting

- No assets flagged → Tier 1 only, ask before expanding.
- Tier 3 requested without evidence → return to `usd-structure-assessment`.
- Named validator unavailable → record gap, choose nearest supported source.
