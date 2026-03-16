---
name: game-studio
description: Route early browser-game work. Use when the user needs stack selection and workflow planning across design, implementation, assets, and playtesting before moving to a specialist skill.
---

# Game Studio

## Overview

Use this skill as the umbrella entrypoint for browser-game work. Default to a 2D Phaser path unless the user explicitly asks for 3D, Three.js, React Three Fiber, shader-heavy rendering, or another WebGL-first direction.

This plugin is intentionally asymmetric:

- 2D is the strongest execution path in v1.
- 3D has one opinionated default ecosystem: vanilla Three.js for plain TypeScript or Vite apps, React Three Fiber for React-hosted 3D apps, and GLB or glTF 2.0 as the default shipping asset format.
- Shared architecture, UI, and playtest practices apply to both.

## Use This Skill When

- the user is still choosing a stack
- the request spans multiple domains such as runtime, UI, asset pipeline, and QA
- the user says "help me build a game" without naming the implementation path

## Do Not Stay Here When

- the runtime is clearly plain Three.js
- the runtime is clearly React Three Fiber
- the task is clearly a shipped-asset problem
- the task is clearly frontend-only or QA-only

Once the intent is clear, route to the most specific specialist skill and continue from there.

## Routing Rules

1. Classify the request before designing or coding:
   - `2D default`: Phaser, sprites, tilemaps, top-down, side-view, grid tactics, action platformers.
   - `3D + plain TS/Vite`: imperative scene control, engine-like loops, non-React apps, direct Three.js work.
   - `3D + React`: React-hosted product surfaces, declarative scene composition, shared React state, UI-heavy 3D apps.
   - `3D asset pipeline`: GLB, glTF, texture packaging, compression, LOD, runtime asset size.
   - `Alternative engine`: Babylon.js or PlayCanvas requests, usually as comparison or ecosystem fit questions.
   - `Shared`: core loop design, frontend direction, save/debug/perf boundaries, browser QA.
2. Route to the specialist skills immediately after classification:
   - Shared architecture and engine choice: `../web-game-foundations/SKILL.md`
   - Deep 2D implementation: `../phaser-2d-game/SKILL.md`
   - Vanilla Three.js implementation: `../three-webgl-game/SKILL.md`
   - React-hosted 3D implementation: `../react-three-fiber-game/SKILL.md`
   - 3D asset shipping and optimization: `../web-3d-asset-pipeline/SKILL.md`
   - HUD and menu direction: `../game-ui-frontend/SKILL.md`
   - 2D sprite generation and normalization: `../sprite-pipeline/SKILL.md`
   - Browser QA and visual review: `../game-playtest/SKILL.md`
3. Keep one coherent plan across the routed skills. Do not let engine, UI, asset, and QA decisions drift apart.

## Default Workflow

1. Lock the game fantasy and player verbs.
2. Define the core loop, failure states, progression, and target play session length.
3. Choose the implementation track:
   - Default to Phaser for 2D browser games.
   - Choose vanilla Three.js when the project is explicitly 3D and wants direct render-loop control in a plain TypeScript or Vite app.
   - Choose React Three Fiber when the project already lives in React or wants declarative scene composition with shared React state.
   - Choose raw WebGL only when the user explicitly wants a custom renderer or shader-first surface.
4. Define the UI surface early. Browser games usually need a DOM HUD and menu layer even when the playfield is canvas or WebGL.
   - For 3D starter scaffolds, default to a low-chrome HUD that preserves the playfield and keeps secondary panels collapsed.
5. Decide the asset workflow:
   - 2D characters and effects: use `sprite-pipeline`.
   - 3D models, textures, and shipping format: use `web-3d-asset-pipeline`.
6. Close with a playtest loop before calling the work production-ready.

## Output Expectations

- For planning requests, return a game-specific plan with stack choice, gameplay loop, UI surface, asset workflow, and test approach.
- For implementation requests, keep the chosen stack obvious in the file structure and code boundaries.
- For mixed requests, preserve the plugin default: 2D Phaser first unless the user asks for something else.
- When the user asks about Babylon.js or PlayCanvas, compare them honestly but keep Three.js and R3F as the primary code-generation defaults unless the user explicitly chooses another engine.

## References

- Engine selection: `../../references/engine-selection.md`
- Three.js stack: `../../references/threejs-stack.md`
- React Three Fiber stack: `../../references/react-three-fiber-stack.md`
- 3D asset pipeline: `../../references/web-3d-asset-pipeline.md`
- Vanilla Three.js starter: `../../references/threejs-vanilla-starter.md`
- React Three Fiber starter: `../../references/react-three-fiber-starter.md`
- Frontend prompting patterns: `../../references/frontend-prompts.md`
- Playtest checklist: `../../references/playtest-checklist.md`

## Examples

- "Help me prototype a browser tactics game."
- "I need a Phaser-based action game loop with a HUD and menus."
- "I want a Three.js exploration demo with WebGL lighting and browser-safe UI."
- "I want a React-based 3D configurator with React Three Fiber."
- "Optimize my GLB assets for the web and keep the file sizes under control."
- "Set up the asset workflow for consistent 2D sprite animations."
