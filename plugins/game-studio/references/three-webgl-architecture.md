# Three WebGL Architecture

This is the default 3D structure for the plugin.

## Recommended module split

```text
src/
  game/
    simulation/
    content/
    input/
    save/
  render/
    app/
      createRenderer.ts
      createScene.ts
      createCamera.ts
      createLoop.ts
    loaders/
      loadGltf.ts
      loadEnvironment.ts
      loadTextures.ts
    objects/
    materials/
    lights/
    post/
    adapters/
      renderBridge.ts
  physics/
    world.ts
    colliders.ts
    sync.ts
  diagnostics/
    debugFlags.ts
    perf.ts
  ui/
    hud/
    menus/
    overlays/
```

## Responsibilities

- `simulation/`: rules, state, AI, progression, save data
- `render/app/`: renderer, scene, camera, resize, context lifecycle
- `render/loaders/`: GLTF, compression, texture, and environment loading
- `render/objects/`: scene graph construction and disposal
- `render/materials/`: material setup and shader boundaries
- `physics/`: Rapier world and simulation bridge
- `diagnostics/`: performance probes and GPU debugging hooks
- `ui/`: DOM HUD and menus

## Rules

- Scene graph objects are not the source of truth for game rules.
- Keep camera logic explicit and testable.
- Handle resize and context-loss as real browser concerns.
- Keep high-density UI in DOM even when the world is fully 3D.
- Treat GLB or glTF 2.0 as the default content format.
- Add physics and diagnostics as real subsystems, not temporary one-off utilities.
