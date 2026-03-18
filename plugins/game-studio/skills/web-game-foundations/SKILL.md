---
name: web-game-foundations
description: Set browser-game architecture before implementation. Use when the user needs engine choice, simulation and render boundaries, input model, asset organization, or save/debug/performance strategy.
---

# Web Game Foundations

## Overview

Use this skill to establish the non-negotiable architecture before implementation starts. Browser games degrade quickly when simulation, rendering, UI, asset loading, and input handling are mixed together.

Default rule: simulation state is owned outside the renderer, browser UI is not forced into the canvas unless there is a clear reason, and shipped 3D assets default to GLB or glTF 2.0 rather than ad hoc model formats.

## Use This Skill When

- the user has not settled the engine or renderer choice
- the task is about boundaries, module shape, state ownership, or asset policy
- multiple specialist skills need one shared architectural frame

## Do Not Stay Here When

- the runtime track is clearly Phaser
- the runtime track is clearly vanilla Three.js
- the runtime track is clearly React Three Fiber
- the task is purely about shipped 3D assets

Once the stack is clear, hand off to the runtime or asset specialist skill.

## Architecture Rules

1. Separate simulation from rendering.
   - Simulation owns entities, turns, timers, collisions, progression, and saveable state.
   - The renderer owns scene composition, animation playback, camera, particles, and input plumbing.
2. Keep input mapping explicit.
   - Define actions such as `move`, `confirm`, `cancel`, `ability-1`, and `pause`.
   - Map physical inputs to actions in one place.
3. Treat asset loading as a first-class system.
   - Use stable manifest keys.
   - Group by domain: characters, environment, UI, audio, FX.
   - For 3D content, standardize on GLB or glTF 2.0 unless the chosen engine ecosystem requires another format upstream.
4. Define save/debug/perf boundaries up front.
   - Save serializable simulation state, not renderer objects.
   - Keep debug overlays and perf probes easy to toggle.
5. Use DOM overlays for menus and HUD by default.
   - Canvas or WebGL should handle the playfield.
   - DOM should handle text-heavy HUD, menus, settings, and accessibility-sensitive controls.
   - In 3D, keep the persistent UI budget small so the scene stays readable and interactive.
6. Lock 3D runtime conventions early.
   - Choose consistent units, origins, pivots, and naming conventions.
   - Decide how collision proxies, LODs, and baked lighting data are authored before runtime integration starts.

## Engine Selection

- Default to Phaser for 2D games with sprites, tilemaps, top-down or side-view action, turn-based grids, and classic browser arcade flows.
- Default to vanilla Three.js for explicit 3D scenes that want direct scene, camera, renderer, and loop control in plain TypeScript or Vite.
- Default to React Three Fiber when the 3D scene lives inside a React application and needs declarative composition, shared app state, or React-first UI coordination.
- Use raw WebGL only for shader-heavy or renderer-first projects where engine abstractions would get in the way.
- Keep Babylon.js and PlayCanvas as alternative-engine paths rather than the default code-generation target.

See `../../references/engine-selection.md` for the default decision table.

## Implementation Checklist

Define these before writing core code:

- Player fantasy and primary verbs
- Core loop and loss or reset states
- Camera model
- Input action map
- Simulation modules
- Renderer modules
- Asset manifest layout
- 3D asset format and optimization rules
- HUD and menu surfaces
- Save data boundary
- Debug and perf surfaces

## Anti-Patterns

- Mixing gameplay rules directly into scene callbacks
- Treating the renderer as the source of truth for game state
- Putting all HUD and menu UI into the canvas by default
- Letting asset filenames become the public API instead of manifest keys
- Shipping unoptimized 3D assets straight from the DCC tool into the browser
- Mixing camera-control state and menu or modal state without an explicit input boundary
- Rebuilding architecture every time the game changes genre

## References

- Engine selection: `../../references/engine-selection.md`
- Phaser structure: `../../references/phaser-architecture.md`
- Three.js structure: `../../references/three-webgl-architecture.md`
- Three.js ecosystem stack: `../../references/threejs-stack.md`
- React Three Fiber stack: `../../references/react-three-fiber-stack.md`
- 3D asset shipping: `../../references/web-3d-asset-pipeline.md`
