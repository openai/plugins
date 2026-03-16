---
name: web-3d-asset-pipeline
description: Prepare and optimize browser-game 3D assets. Use when the user asks for GLB or glTF shipping work, including Blender cleanup and export, collision or LOD setup, compression, texture packaging, and runtime validation.
---

# Web 3D Asset Pipeline

## Overview

Use this skill for shipped 3D assets, not runtime scene code. The default output format for browser 3D work in this plugin is GLB or glTF 2.0. The goal is predictable runtime assets, not whatever the DCC tool happened to export first.

This guidance is engine-agnostic and can serve Three.js, React Three Fiber, Babylon.js, or PlayCanvas.

## Use This Skill When

- the task is about GLB or glTF shipping format
- the task is about model cleanup, texture packaging, compression, LOD, or collision proxies
- the runtime stack is already chosen and the remaining problem is asset quality or size

## Do Not Use This Skill When

- the task is about scene, camera, renderer, or game-loop structure
- the task is purely about React versus vanilla Three.js routing
- the user is still deciding between runtime engines

## Default Pipeline

1. Author and clean the source asset in a DCC tool such as Blender.
2. Export to GLB or glTF 2.0.
3. Optimize with glTF Transform.
4. Validate naming, pivots, transforms, material reuse, and texture budgets.
5. Add collision proxies, LOD strategy, and baked-lighting assumptions as needed.
6. Ship the optimized asset and load it with engine-native GLTF support.

## Format Rules

- Default shipping format: GLB or glTF 2.0.
- Do not treat FBX, OBJ, or DCC-native formats as the long-term runtime contract.
- Apply or normalize transforms before shipping.
- Keep units, pivots, and orientation conventions consistent across the whole asset set.

## Optimization Rules

- Use glTF Transform for pruning, deduplication, simplification, and packaging.
- Use geometry compression intentionally.
  - Draco is a valid option when decode cost and compatibility fit the runtime.
  - Meshopt is often a strong default for web delivery.
- Compress textures deliberately.
  - Use KTX2 or BasisU when the runtime stack supports it.
  - Use WebP or AVIF where they make sense in the broader asset pipeline.
- Reuse materials and textures where possible to cut memory and draw-call cost.

## Runtime-Ready Asset Rules

- Keep model hierarchy names stable and meaningful.
- Set pivots and origins for gameplay interaction, not just for DCC convenience.
- Author explicit collision proxies for physics-heavy scenes.
- Decide whether lighting is dynamic, baked, or hybrid before final export.
- Plan LODs for large environments or repeated props.
- Keep texture resolution proportional to on-screen use, not source-art ambition.

## Common Failure Modes

- Shipping raw DCC exports without cleanup
- Too many unique materials
- Texture sizes far above visible need
- Missing collision proxies
- Scale or pivot mismatches between assets
- Runtime code compensating for asset mistakes that should be fixed upstream

## References

- Three.js stack: `../../references/threejs-stack.md`
- React Three Fiber stack: `../../references/react-three-fiber-stack.md`
- GLB loader starter: `../../references/gltf-loading-starter.md`
- Rapier starter: `../../references/rapier-integration-starter.md`
- 3D asset pipeline reference: `../../references/web-3d-asset-pipeline.md`
- Alternative engines: `../../references/alternative-3d-engines.md`
