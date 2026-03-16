---
name: react-three-fiber-game
description: Build React-hosted 3D browser games with React Three Fiber. Use when the user wants pmndrs-based scene composition, shared React state, and 3D HUD integration inside a React app.
---

# React Three Fiber Game

## Overview

Use this skill when the 3D runtime lives inside a React application. This is the default React-native 3D path in the plugin and should be preferred over vanilla Three.js when the app shell, settings, storefront, editor surface, or surrounding product already uses React.

Recommended stack:

- `@react-three/fiber`
- `three`
- `@react-three/drei`
- `@react-three/rapier`
- `@react-three/postprocessing`
- `@react-three/a11y` when accessibility-sensitive interaction matters
- DOM overlays in the normal React tree

## Use This Skill When

- the project already uses React
- the 3D scene must share state with the rest of the app
- declarative scene composition is a net gain
- the team wants pmndrs helpers instead of building every helper layer by hand

## Do Not Use This Skill When

- the app is not React-based
- the project wants a cleaner imperative runtime with minimal React coordination
- the problem is asset packaging rather than runtime composition

## Best Fit Scenarios

- 3D configurators and tool-rich browser products
- React apps with embedded game or scene surfaces
- 3D menus, editors, or world maps in an existing React app
- 3D game UIs that depend on shared app state and non-canvas shells

## Core Rules

1. Keep simulation state outside render components.
   - React components should describe scene composition, not become the source of truth for gameplay rules.
2. Use React state and scene state deliberately.
   - Shared UI state can live in app state.
   - High-frequency simulation should not force the whole app through unnecessary React churn.
3. Use pmndrs helpers intentionally.
   - Drei for controls, loaders, helpers, environments, and common scene primitives.
   - `@react-three/rapier` for physics integration.
   - `@react-three/postprocessing` for optional effects.
   - `@react-three/a11y` when the interaction model benefits from accessible scene semantics.
4. Keep HUD, settings, and menus in DOM by default.
5. Keep starter scaffolds visually restrained.
   - Start with one compact objective or status surface and transient prompts.
   - Keep notes, maps, and multi-step checklists collapsed until opened.
   - Do not surround the `Canvas` with equally weighted glass cards.

## Architectural Guidance

- Use a dedicated scene root component that owns the `Canvas`.
- Keep camera rigs and control components isolated from gameplay systems.
- Keep loader and asset wrappers predictable.
- Keep DOM overlays and the 3D scene coordinated through explicit state boundaries.
- If a system needs tight imperative control, isolate it rather than forcing everything into declarative patterns.
- If the scene is immediately playable, keep the initial overlay budget low and let the world do more of the onboarding.

## Anti-Patterns

- Treating React components as the gameplay state store
- Pushing heavy per-frame mutation through broad app state
- Using R3F only because React is available, even when the project needs a cleaner imperative runtime
- Building HUD or inventory UI inside the 3D scene by default
- Shipping an initial scaffold with large cards occupying every side of the viewport

## References

- Shared architecture: `../web-game-foundations/SKILL.md`
- Frontend direction: `../game-ui-frontend/SKILL.md`
- 3D HUD layout patterns: `../../references/three-hud-layout-patterns.md`
- React Three Fiber stack: `../../references/react-three-fiber-stack.md`
- React starter: `../../references/react-three-fiber-starter.md`
- GLB loader starter: `../../references/gltf-loading-starter.md`
- Rapier starter: `../../references/rapier-integration-starter.md`
- 3D asset pipeline: `../../references/web-3d-asset-pipeline.md`
- WebGL debugging and perf: `../../references/webgl-debugging-and-performance.md`
