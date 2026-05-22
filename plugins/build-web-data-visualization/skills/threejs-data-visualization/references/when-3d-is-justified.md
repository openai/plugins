# When 3D or GPU Rendering Is Justified

## What Problem This Solves

This reference prevents decorative 3D or decorative GPU effects from being mistaken for analytical progress. It also gives WebGL a path into 2D work when GPU rendering is the practical choice.

## When to Use It

Use this whenever the user asks for 3D, WebGL, GPU acceleration, particles, animated flows, or when a 2D chart is being considered for migration into Three.js, deck.gl, PixiJS, regl, raw WebGL, or another GPU stack.

## Key Takeaways

- Use 3D when the data is inherently spatial, volumetric, or trajectory-based.
- Use WebGL 2D when mark count, redraw cadence, picking, blending, or animation exceeds practical SVG/DOM limits and Canvas2D would require too much custom batching or pixel work.
- Keep SVG/DOM when labels, exact comparisons, accessibility semantics, editable vector export, or print-first consumption dominate.
- Keep Canvas2D when the visualization is dense but mostly flat, immediate-mode, and does not need GPU-specific features such as instancing, custom shaders, or blending at scale.
- A 3D view should reveal structure that 2D hides, not merely look more impressive.
- A particle or glow effect should communicate direction, accumulation, focus, uncertainty, or state. If it cannot be named with an explanatory verb, do not add it.
- WebGL can be more performant than SVG/DOM for large mark counts and continuous animation, but it is not automatically faster than Canvas2D. Data upload, draw-call count, texture memory, context overhead, and shader complexity can erase the advantage.

## Choose 3D When

- z position, depth, terrain, volume, or camera angle is part of the evidence
- slicing, clipping planes, orbit, or perspective reveals occluded structure
- the data is a point cloud, volumetric scalar field, 3D surface, simulation, trajectory, sensor space, or globe/terrain scene
- a story uses camera movement to compare meaningful surfaces or locations, with static key frames that still prove the claim

## Choose WebGL 2D When

- the task is still flat, but has hundreds of thousands or millions of points, links, glyphs, particles, or sprites
- interaction requires smooth pan, zoom, filtering, lassoing, hover picking, or linked selection under heavy mark counts
- flow maps, trip animations, network edge traffic, particle advection, heat shimmer, or animated focus cues are analytically useful
- a product map needs GPU vector tiles, extrusions, heatmaps, or custom WebGL layers

## Prefer Alternatives When

- standard charts fit a declarative grammar
- bespoke but moderate charts need precise SVG labels, annotations, and export
- dense 2D rendering needs simple marks and frequent full redraws that Canvas2D can handle with less setup
- the audience must inspect exact numbers more than patterns, direction, or structure
- many repeated small multiples would create WebGL context pressure

## Common Mistakes

- Using depth for categorical separation that a small multiple could express better.
- Ignoring how screenshots and exports will flatten the scene.
- Adding particles that imply individual people, transactions, or certainty when the data is aggregated or estimated.
- Re-uploading full buffers every animation frame when only a time uniform, selection mask, or small dynamic attribute changed.
- Treating WebGL as a universal performance fix without measuring CPU preprocessing, GPU upload, memory, and interaction costs.

## Adjacent Skills

- `../SKILL.md`
- `../../geospatial-and-cartographic-visualization/SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../d3-data-visualization/SKILL.md`

## Source Links

- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [MDN: WebGL2RenderingContext](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext)
- [Three.js BufferGeometry](https://threejs.org/docs/pages/BufferGeometry.html)
- [Three.js InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html)
- [deck.gl Introduction](https://deck.gl/docs)
- [deck.gl Aggregation Layers](https://deck.gl/docs/api-reference/aggregation-layers/overview)
