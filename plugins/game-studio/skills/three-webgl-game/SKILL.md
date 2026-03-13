---
name: three-webgl-game
description: Build 3D browser games with a concrete vanilla Three.js stack. Use when the user wants plain TypeScript or Vite control over Three.js scenes, loaders, physics, GLB assets, materials, WebGL debugging, and a clean low-chrome 3D scaffold without a React wrapper.
---

# Three WebGL Game

## Overview

Use this skill for the default non-React 3D path in the plugin. This is not generic WebGL advice. It is an opinionated stack for browser 3D work:

- `three`
- TypeScript
- Vite
- GLB or glTF 2.0 assets
- Three.js loaders such as `GLTFLoader`, `DRACOLoader`, and `KTX2Loader`
- Rapier JS for physics
- SpectorJS for GPU and frame debugging
- DOM overlays for HUD, menus, and settings

Use this skill when the project wants direct scene, camera, renderer, and game-loop control. If the app already lives in React, route to `../react-three-fiber-game/SKILL.md` instead.

## Use This Skill When

- the app is plain TypeScript or Vite rather than React-first
- the project wants direct imperative control over the render loop
- the user asks for Three.js specifically
- the runtime needs engine-like control over scene, camera, loaders, and physics

## Do Not Use This Skill When

- the 3D scene lives inside an existing React app
- the main problem is shipped-asset optimization rather than runtime code
- the user explicitly chose Babylon.js or PlayCanvas

## Core Rules

1. Keep simulation state outside Three.js objects.
   - Game rules, AI, quest state, timers, and progression should not live inside meshes or materials.
2. Treat the render graph as an adapter.
   - Scene graph, cameras, materials, loaders, and post-processing are view concerns layered over simulation state.
3. Keep camera behavior explicit.
   - Orbit, follow, chase, rail, and first-person styles each need their own control boundary.
4. Keep UI out of WebGL unless the presentation absolutely depends on it.
   - Menus, HUD, inventories, and settings should default to DOM.
5. Use GLB or glTF 2.0 as the default shipping model format.
   - Do not build the runtime around DCC-native formats.
6. Use Rapier instead of ad hoc collision code when the game has meaningful 3D physics or collision response.
7. Keep the first playable view low-chrome.
   - Default to one compact objective or status cluster plus transient prompts.
   - Long notes, lore, and controls references should be collapsed until asked for.
   - Do not frame the scene with multiple equal-weight cards during normal play.

## Initial Scaffold UX

For exploration, traversal, and character-control prototypes, start with a sparse shell:

- one edge-aligned objective chip
- one transient controls hint
- one optional compact status strip

Only add larger UI surfaces when the game loop truly requires them. Journal, quest log, codex, map, and settings surfaces should open on demand, not occupy the viewport by default.

## Recommended Structure

Use the module shape in `../../references/three-webgl-architecture.md`, then keep these boundaries clean:

- `simulation/`: rules, progression, state, and AI
- `render/app/`: renderer, scene, camera, resize, context lifecycle
- `render/loaders/`: GLTF, Draco, KTX2, texture, and environment loading
- `render/objects/`: mesh instantiation and disposal
- `render/materials/`: material setup and shader boundaries
- `physics/`: Rapier world, bodies, colliders, and simulation bridge
- `ui/`: DOM overlays and menus
- `diagnostics/`: debug toggles, perf probes, and capture hooks

## Good Fit Scenarios

- Exploration demos
- Lightweight 3D combat prototypes
- Vehicle or traversal prototypes
- Scene-driven product or world showcases with gameplay
- Material, lighting, or post-process-led experiences
- 3D games where camera movement and depth readability are central

## Loaders, Assets, and Post-Processing

- Start with `GLTFLoader` for shipped 3D content.
- Add `DRACOLoader` or Meshopt-compatible optimization as part of the asset pipeline, not as a random runtime patch.
- Use `KTX2Loader` for compressed textures when the asset pipeline provides them.
- Prefer built-in Three.js render and post-processing utilities first. Add heavier abstraction only when the project actually needs it.
- Keep post-processing optional and measurable. Bloom and color effects should not hide gameplay readability.

## Shader and Material Guidance

- Start with standard Three.js materials and correct lighting before reaching for custom shaders.
- Use custom shaders only when the visual target genuinely needs them.
- Keep shader parameters driven by game state, not by incidental scene mutations.
- If a material stack gets complex, isolate it behind material factories instead of scattering shader setup across scene code.

## Browser Safety

- Handle resize explicitly.
- Expect WebGL context loss and recovery.
- Keep a fallback or degraded mode in mind for fragile GPU paths.
- Watch texture size, geometry count, draw-call growth, and post-processing cost.
- Use SpectorJS when the scene behaves incorrectly or frame cost is unclear.

## Scope Warning

Do not claim that this plugin offers equal 3D depth to the Phaser track. It supports serious 3D implementation, but the plugin is still 2D-first overall.

## References

- Shared architecture: `../web-game-foundations/SKILL.md`
- Frontend direction: `../game-ui-frontend/SKILL.md`
- 3D HUD layout patterns: `../../references/three-hud-layout-patterns.md`
- Three.js ecosystem: `../../references/threejs-stack.md`
- Three.js structure: `../../references/three-webgl-architecture.md`
- Vanilla starter: `../../references/threejs-vanilla-starter.md`
- GLB loader starter: `../../references/gltf-loading-starter.md`
- Rapier starter: `../../references/rapier-integration-starter.md`
- 3D asset pipeline: `../../references/web-3d-asset-pipeline.md`
- WebGL debugging and perf: `../../references/webgl-debugging-and-performance.md`
