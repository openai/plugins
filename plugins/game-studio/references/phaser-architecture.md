# Phaser Architecture

This is the default 2D structure for the plugin.

## Recommended module split

```text
src/
  game/
    simulation/
      state.ts
      systems/
      rules/
    content/
      encounters/
      items/
      maps/
    input/
      actions.ts
      bindings.ts
    assets/
      manifest.ts
  phaser/
    boot/
    scenes/
      BootScene.ts
      MenuScene.ts
      BattleScene.ts
    view/
      sprites/
      fx/
      camera/
    adapters/
      sceneBridge.ts
  ui/
    hud/
    menus/
    overlays/
```

## Responsibilities

- `simulation/`: source of truth for rules and saveable state
- `content/`: authored data and encounter configuration
- `input/`: action map and physical control bindings
- `assets/`: stable manifest keys and asset metadata
- `phaser/scenes/`: scene orchestration, not game rules
- `phaser/view/`: render and effect helpers
- `ui/`: DOM HUD, menus, and narrative panels

## Rules

- Phaser scenes read from and write to the simulation through a defined bridge.
- Game state changes should not depend on sprite or tween lifetime.
- Camera behavior should be isolated from combat or movement rules.
- Use DOM for dense text and settings surfaces.
