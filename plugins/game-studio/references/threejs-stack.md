# Three.js Stack

This is the default non-React 3D runtime stack for the plugin.

## Primary components

- [Three.js documentation](https://threejs.org/docs/) for the core renderer, scene graph, materials, cameras, loaders, and examples.
- [Rapier JavaScript guide](https://rapier.rs/docs/user_guides/javascript/getting_started_js/) for physics integration.
- [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) for the default shipping asset format.
- [glTF Transform](https://gltf-transform.dev/) for optimization, packaging, and compression workflows.
- [SpectorJS](https://spector.babylonjs.com/) for WebGL frame capture and GPU debugging.

## Default stack choices

- Runtime: `three`
- Tooling: TypeScript + Vite
- Assets: GLB or glTF 2.0
- Loaders: `GLTFLoader`, `DRACOLoader`, `KTX2Loader` when the asset pipeline requires them
- Physics: Rapier JS
- UI: DOM overlays, not in-scene UI by default

## Choose this stack when

- the project is not React-first
- the team wants direct control over the render loop
- scene composition, loader setup, or custom render behavior needs imperative structure
- the game code should feel engine-like without a React abstraction layer

## Avoid this stack when

- the surrounding app is already React-heavy and wants shared declarative state
- the project needs an editor-first engine workflow more than a portable TypeScript runtime

## Companion references

- `three-webgl-architecture.md`
- `threejs-vanilla-starter.md`
- `gltf-loading-starter.md`
- `rapier-integration-starter.md`
- `web-3d-asset-pipeline.md`
- `webgl-debugging-and-performance.md`
