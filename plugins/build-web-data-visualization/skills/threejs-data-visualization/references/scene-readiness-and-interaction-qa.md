# Scene Readiness and Interaction QA

## What Problem This Solves

Ambitious WebGL visualizations often fail in ways that screenshots and type checks do not catch: the canvas is blank, a fallback sits on top of the live scene, interaction events update state but the render loop never moves, labels are offset from marks, or dense marks cannot be selected reliably.

## Scene Ownership

- One renderer owns the primary focal scene at a time.
- Fallbacks should be hidden while the primary renderer has produced a valid first frame.
- Loading shells may sit behind or below the scene, but must not create a second visible copy of the same globe, map, chart, or 3D object.
- DOM and SVG overlays can own labels, legends, controls, and callouts, but should share the same coordinate transform or projection contract.

## Coordinate And Camera Checks

- Write a coordinate-frame ledger for every scene layer: texture, basemap, marks, labels, hit tests, overlays, and fallback.
- For globes, record longitude origin, wrap policy, texture offset, marker transform, and label transform.
- Test known landmarks: one event or label in Alaska, Japan, Australia, Europe/Africa, and the Pacific seam when relevant.
- For cyclic rotation, normalize the target to the nearest equivalent angle before animating.
- Keep reset and named focus states deterministic.

## Picking And Dense Marks

- Prefer screen-space nearest-mark picking when raycasting glow meshes, sprites, or wide halos makes nearby marks ambiguous.
- Hover should preview the exact item that click will select.
- Selection styling must be visually distinct from data encoding. For example, do not use extra magnitude-like rings for selected state if rings encode magnitude.
- Add step-through controls when nearby points remain difficult to target.

## Render Loop And Readiness

- Use one clock model. Do not mix elapsed and delta APIs in a way that drains frame delta.
- Expose or infer a render-ready signal after the first nonblank frame.
- Include context-loss handling or at least a recoverable fallback.
- In screenshots, check canvas pixels or visible scene bounds instead of only asserting DOM presence.
- Verify pointer drag, wheel, pinch or button zoom, reset, close, and keyboard paths against the live scene.

## Common Mistakes

- A fallback globe or map remains visible behind the live WebGL scene.
- WebGL feature probes are so strict that capable browsers silently get static fallbacks.
- Hit testing intersects decorative glow or sphere geometry instead of the data point.
- Camera focus spins the long way around a cyclic axis.
- Interaction state changes but the render loop uses near-zero delta, making the scene feel dead.
