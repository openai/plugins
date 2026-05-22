# GPU Scaling and Interaction

## What Problem This Solves

This reference covers the performance and interaction decisions that make WebGL analytical views workable at scale, whether 2D, 2.5D, or 3D.

## When to Use It

Use this when the scene uses many points, instances, particles, edges, flows, tiles, sprites, or frequent interaction.

## Key Takeaways

- Favor `BufferGeometry`, instancing, and shader-friendly data layouts.
- Maintain predictable camera controls with reset and focus behaviors.
- Pair 3D exploration with 2D summaries or supporting views when possible.
- Use binary data, typed arrays, and stable buffer layouts for dense data.
- Minimize draw calls, state changes, texture swaps, and full-buffer uploads.
- Keep animation cheap: prefer time uniforms, attribute interpolation, shader-based decay, and small dynamic buffers over rebuilding geometry.
- Use level of detail, aggregation, sampling, tile pyramids, culling, and frustum checks before relying on raw GPU power.
- Budget for the whole page: WebGL context count, GPU memory, texture memory, device pixel ratio, overlays, and concurrent animation loops.
- Provide context-loss handling and a non-WebGL fallback for critical workflows.

## Common Mistakes

- Using full-scene brute force when instancing or aggregation would work.
- Relying on 3D navigation alone to communicate exact values.
- Creating one WebGL context per tiny chart in a dashboard instead of sharing, virtualizing, or using Canvas/SVG for small multiples.
- Redrawing every frame because an animation loop exists, even when nothing changed.
- Animating thousands of CPU-side objects instead of GPU attributes, sprites, or shader uniforms.
- Ignoring mobile GPUs, high `devicePixelRatio`, power usage, and thermal throttling.
- Assuming WebGL is faster than Canvas2D without measuring the specific workload.

## Performance Checklist

- Estimate marks, links, particles, labels, and visible instances per viewport.
- Estimate update cadence: static, hover-only, filter updates, streaming, or full animation.
- Choose a data upload strategy: one-time buffer, partial `bufferSubData`, texture update, binary deck.gl attributes, or tiled chunks.
- Keep static and dynamic attributes separate so selection or time changes do not invalidate every buffer.
- Use aggregation for overplotting: screen grids, hex bins, contours, heatmaps, clusters, or vector tiles.
- Cap pixel ratio or resolution for heavy scenes; provide quality settings when needed.
- Pause offscreen scenes with IntersectionObserver or route-level lifecycle hooks.
- Dispose geometries, materials, buffers, textures, render targets, and event handlers on unmount.
- Test context loss, resize, DPR changes, zoom, pan, hover, lasso, and reduced-motion states.

## Interaction Checklist

- Pick only what users can reasonably act on; do not make every particle hoverable if particles are decorative carriers of flow.
- Use GPU picking or a spatial index for dense marks; use CPU hit testing only when mark counts and interaction frequency permit it.
- Keep hover previews fast and noncommittal; use click, lasso, or brush for committed selection.
- For dense networks, expose filtering, focus-neighborhood, edge bundling, or aggregation before adding more particles.
- For 3D scenes, provide orientation aids, home view, focus view, and keyboard-accessible camera state changes.
- For animated flows, provide pause, scrub, speed, and final-state controls when time is part of the analysis.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`
- `../../testing-data-visualizations/SKILL.md`

## Source Links

- [MDN: WebGLRenderingContext](https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext)
- [MDN: WebGL2RenderingContext](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext)
- [MDN: WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- [MDN: WEBGL_lose_context](https://developer.mozilla.org/en-US/docs/Web/API/WEBGL_lose_context)
- [deck.gl Introduction](https://deck.gl/docs)
- [deck.gl Animations and Transitions](https://deck.gl/docs/developer-guide/animations-and-transitions)
- [deck.gl Primitive Layers](https://deck.gl/docs/developer-guide/custom-layers/primitive-layers)
- [luma.gl Overview](https://luma.gl/docs)
- [PixiJS ParticleContainer](https://pixijs.com/8.x/guides/components/scene-objects/particle-container)
