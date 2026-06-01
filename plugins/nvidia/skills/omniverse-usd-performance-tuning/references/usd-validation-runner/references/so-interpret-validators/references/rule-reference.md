<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Validator Rule Reference

The mapping below is the local source of truth for the digitaltwin workflow's
`Fix tier` and `Operation` columns. Scene Optimizer validator mechanics and
operation docs live upstream in
[usd-optimize](https://github.com/NVIDIA-omniverse/usd-optimize/) and the
prebuilt Scene Optimizer package. Resolve guidance from an extracted package
root via `$SCENE_OPTIMIZER_PACKAGE_ROOT`, then `$SO_HOME`. If no package
root exists, download/extract the published `scene_optimizer_core_...release.zip`
package (direct archive URLs are in `references/upstreams/usd-optimize.md`) or
use the package path, URL, or extracted root supplied by the user. Do not clone
the source repo just to read SO guidance. To verify a rule's backing operation,
inspect upstream
`source/core/python/omni/scene/optimizer/validators/<module>.py`; the
authoritative registered-rule lists live in upstream `_default_rule_classes()`
and `_expensive_rule_classes()`.

### SceneOptimizer rules (default)

| Rule | Backing op | Tier | Notes |
|------|-----------|------|-------|
| SceneOptimizerCoincidingGeometryChecker | `findCoincidingGeometry` | T3 | Analysis-only; prefer `deduplicateGeometry` before destructive deletion. Use upstream `.agents/operations/findCoincidingGeometry.md` for mechanics. |
| SceneOptimizerColocatedVerticesChecker | `meshCleanup` | T1 | `meshCleanup` merges colocated vertices. |
| SceneOptimizerDuplicateFacesChecker | `meshCleanup` | T1 | `meshCleanup` removes duplicate faces. |
| SceneOptimizerDuplicateGeometryChecker | `deduplicateGeometry` | T1 | Converts identical meshes to USD instances. |
| SceneOptimizerDuplicateHierarchiesChecker | `usd-hierarchy-dedupe-candidates` + `apply-restructure` | T3 | Structural signal; use the hierarchy candidate finder + restructure gate, not a direct mesh op. |
| SceneOptimizerDuplicateMaterialsChecker | `optimizeMaterials` | T1 | Merges duplicate material definitions. |
| SceneOptimizerEmptyLeafChecker | `pruneLeaves` | T1 | Removes leaf prims with no geometry. |
| SceneOptimizerFlatHierarchiesChecker | `findFlatHierarchies` | T3 | Analysis-only. Fix: `flattenHierarchy` operation. |
| SceneOptimizerFlattenHierarchyChecker | `flattenHierarchy` | T2 | Has params; tune using upstream `.agents/operations/flattenHierarchy.md`. |
| SceneOptimizerFuzzyDuplicateGeometryChecker | `deduplicateGeometry` | T1 | Same op, different threshold. |
| SceneOptimizerIndexedPrimvarChecker | `optimizePrimvars` | T1 | Converts to indexed primvars; may be deferred when the op is pre-selected. See [`validation-scoping.md`](../../validation-scoping.md) -> Deferred. |
| SceneOptimizerInvisiblePrimsChecker | `removePrims` | T2 | Confirm intent before removing — invisible may be deliberate. |
| SceneOptimizerIsolatedVerticesChecker | `meshCleanup` | T1 | `meshCleanup` removes isolated verts. |
| SceneOptimizerMeshDensityChecker | `countVertices` | T2 | Informational; use lossless reducers first, decimate only after the `decimateMeshes` upfront prompt. |
| SceneOptimizerNonManifoldChecker | `meshCleanup` | T2 | Mesh topology may need repair (non-manifold geometry); skip for visualization-only workflows. See [`validation-scoping.md`](../../validation-scoping.md) -> Deferred. |
| SceneOptimizerNormalsChecker | `generateNormals` | T1 | Regenerates missing/invalid normals. |
| SceneOptimizerPrimitiveFitChecker | `fitPrimitives` | T2 | Primitive replacement; use upstream `.agents/operations/fitPrimitives.md` for parameter semantics. |
| SceneOptimizerRedundantTimeSamplesChecker | `optimizeTimeSamples` | T1 | Removes redundant samples on animated attributes. |
| SceneOptimizerRtxMeshCountChecker | `rtxMeshCount` | T2 | Informational threshold check. Reduce mesh count via `deduplicateGeometry` + `flattenHierarchy` + `removeSmallGeometry`. |
| SceneOptimizerSmallMeshChecker | `removeSmallGeometry` | T1 | Removes meshes below a screen-space threshold. |
| SceneOptimizerSparseMeshChecker | `sparseMeshes` | T2 | Tune density thresholds. |
| SceneOptimizerUnusedUVsChecker | `removeUnusedUVs` | T1 | Removes unbound UV sets; may be deferred when the op is pre-selected. See [`validation-scoping.md`](../../validation-scoping.md) -> Deferred. |
| SceneOptimizerWindingsChecker | `meshCleanup` | T1 | Fixes inconsistent face winding. |
| SceneOptimizerZeroAreaFacesChecker | `meshCleanup` | T1 | Removes degenerate faces. |
| SceneOptimizerZeroExtentChecker | `removeSmallGeometry` | T1 | Analysis finds zero-extent meshes; fix removes them. Use `computeExtents` first when the issue is stale metadata. |

### SceneOptimizer rules (expensive — only present with `--include-expensive`)

| Rule | Backing op | Tier | Notes |
|------|-----------|------|-------|
| SceneOptimizerOccludedMeshesChecker | `findOccludedMeshes` → `removePrims` | T3 | **Two-step detect→act chain.** Analysis identifies fully-occluded prim paths; feed those paths to `removePrims` for deletion. Runs FIRST in Phase 4 op chain (before meshCleanup, dedupe, decimate). Scoped to SA containment pairs with `enclosure_opaque: true` only — transparent enclosures are excluded. Two-stage user approval: (1) approve analysis cost, (2) approve deletion of discovered internals. |
| SceneOptimizerFindOverlappingMeshesChecker | `findOverlappingMeshes` | T3 | Analysis-only. Fix: review and remove/merge in DCC. |

### Base asset-validator rules (`omni.asset_validator.DefaultPlugin`)

The full list lives in the upstream `omniverse-asset-validator` package; we don't
mirror it here. Many base rules detect issues that map cleanly onto a Scene
Optimizer operation — surface the equivalent op so the user has an automated fix
path even when the rule itself is upstream.

**Stage / metadata (no SO equivalent — manual fix):**

- `KindChecker`, `DefaultPrimChecker`, `StageMetadataChecker` — stage-metadata
  rules. **T3 / manual.** Fix via USD Python API:
  `stage.SetDefaultPrim(...)`, `prim.SetMetadata('kind', 'component')`,
  `UsdGeom.SetStageUpAxis(...)`, etc. Check the CSV `Suggestion` column.
- `OmniOrphanedPrimChecker`, `OmniDefaultPrimChecker` — Omni-flavored variants.
  T3 / manual.
- `LayerSpecChecker` — type/value mismatches in layer specs. T3 / manual.

**External references (no SO equivalent — manual fix):**

- `MissingReferenceChecker` — unresolvable references. T3 / manual. Common cause:
  asset flattened on another machine with absolute paths. Fix by re-flattening
  with the textures available, or rewriting absolute paths to relative.
- `MaterialPathChecker` — `info:mdl:sourceAsset` attributes pointing at missing
  files. T3 / manual. Same root cause as `MissingReferenceChecker`.
- `NormalMapTextureChecker` — `UsdUVTexture inputs:file` unresolvable. T3 / manual.

**Geometry rules with SO operation equivalents:**

| Base rule | Equivalent SO op | Tier |
|-----------|------------------|------|
| `ExtentsChecker` | `computeExtents` | T1 |
| `IndexedPrimvarChecker` | `optimizePrimvars` | T1 |
| `WeldChecker` | `meshCleanup` (welds colocated verts) | T1 |
| `NormalsValidChecker` | `generateNormals` | T1 |
| `ZeroAreaFaceChecker` | `meshCleanup` | T1 |
| `UnusedMeshTopologyChecker` | `meshCleanup` (removes unreferenced points) | T1 |
| `ManifoldChecker` | `meshCleanup` (some topology repairs need DCC work) | T2 |

**Deferral** (mirrors the SceneOptimizer table above):

- `IndexedPrimvarChecker` — defer to the post-op pass when `optimizePrimvars`
  is pre-selected by the assessment (CAD/BIM); the checker would just confirm
  what the assessment already told you.
- `ManifoldChecker` — skip entirely for visualization-only workflows
  (digital twins, AEC, rendering). Run only when the user's target is
  simulation-ready (physics, Booleans, 3D printing).

See `usd-validation-runner/references/validation-scoping.md` -> Deferred for
the conditional logic.

When marking these in the summary table, label the tier as `T1-equiv` /
`T2-equiv` so the user knows the fix is a Scene Optimizer op, not the
validator's own `--fix` (this repo's validators don't ship a `--fix` mode).

For rules not in this list, treat as **T3 / manual** and surface the CSV
`Suggestion` column verbatim. Don't invent fix commands.

---
