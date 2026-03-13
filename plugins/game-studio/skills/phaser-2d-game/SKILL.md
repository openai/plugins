---
name: phaser-2d-game
description: Implement 2D browser games with Phaser, TypeScript, and Vite. Use when the user wants the default 2D path for gameplay systems, scenes, cameras, sprite animation, HUD integration, and browser-friendly game structure.
---

# Phaser 2D Game

## Overview

Use this skill for the main execution path in this plugin. Phaser is the default stack for 2D browser games here because it handles rendering, timing, sprites, cameras, and scene orchestration well without forcing gameplay rules into the framework.

Preferred stack:

- Phaser
- TypeScript
- Vite
- DOM-based HUD or menus layered over the game canvas

## Architecture

1. Keep gameplay state outside Phaser scenes.
   - Systems own rules, turn order, movement, combat, inventory, objectives, and progression.
   - Phaser scenes adapt system state into sprites, camera motion, animation playback, and effects.
2. Make scenes thin.
   - Boot and asset preload
   - Menu or shell scene
   - Gameplay scene
   - Optional overlay or debug scene
3. Keep renderer-facing objects disposable.
   - Sprite containers, emitters, tweens, and camera rigs are view state, not source of truth.
4. Favor stable asset manifest keys over direct file-path references throughout gameplay code.

## Implementation Guidance

- Use one integration boundary where the scene reads simulation state and emits input actions back.
- Prefer deterministic system updates over scene-local mutation.
- Treat HUD and menus as DOM when text, status density, or responsiveness matter.
- Keep animation state derived from gameplay state rather than ad hoc sprite flags.

## 2D Modes Covered Well

- Turn-based grids and tactics
- Top-down exploration
- Side-view action platformers
- Character-action combat with sprite animation
- Lightweight management or deck-driven battle scenes

## Camera and Presentation

- Choose the camera model early: locked, follow, room-based, or tactical-pan.
- Keep camera logic separate from game rules.
- Use restrained screen shake, hit-stop, and parallax. Effects should improve readability, not obscure it.

## UI Integration

- Use DOM overlays for HUD, command menus, settings, and narrative panels.
- Keep the canvas responsible for the world, combat readability, and motion.
- Avoid shoving dense text or complex settings UIs into Phaser unless the project explicitly needs an in-canvas presentation.

## Asset Organization

- `characters/`
- `environment/`
- `ui/`
- `fx/`
- `audio/`
- `data/`

Keep manifest keys human-readable and stable.

## Default Directory Shape

See `../../references/phaser-architecture.md` for a concrete module split.

## Anti-Patterns

- Game rules inside `update()` loops without a system boundary
- Scene-to-scene state passed through mutable global objects
- HUD text rendered in the game canvas just because it is convenient
- Asset paths embedded everywhere instead of a manifest layer
- Overusing generic React dashboard patterns for game UI

## References

- Shared architecture: `../web-game-foundations/SKILL.md`
- Frontend direction: `../game-ui-frontend/SKILL.md`
- Sprite workflow: `../sprite-pipeline/SKILL.md`
- Phaser structure: `../../references/phaser-architecture.md`
