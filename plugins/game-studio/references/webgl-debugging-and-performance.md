# WebGL Debugging and Performance

Use this reference when a browser 3D scene is visually wrong, unstable, or slower than expected.

## Primary tools

- [SpectorJS](https://spector.babylonjs.com/) for frame capture, pipeline inspection, draw-call review, and shader debugging.
- Browser performance tooling for main-thread work, asset decode stalls, and memory pressure.
- Engine-native debug views and stats surfaces where available.

## What to inspect first

- draw-call count
- shader compilation churn
- texture memory pressure
- geometry count and material count
- post-processing cost
- asset decode and streaming stalls
- WebGL context loss or fallback behavior

## Common causes of poor performance

- too many unique materials
- oversized textures
- heavy GLB assets loaded without optimization
- complex post-processing on top of an already expensive scene
- physics and render state fighting for ownership
- React and scene state updating each other too frequently in React-hosted 3D apps

## Debugging rules

- Capture first, then guess.
- Reduce the scene until the perf cliff becomes obvious.
- Disable post-processing before rewriting core scene code.
- Verify the asset pipeline before blaming the renderer.
- Treat context-loss handling as a browser requirement, not an edge case.
