# WebGL Scene Architecture and Encodings

## What Problem This Solves

This reference helps structure a Three.js, deck.gl, PixiJS, regl, raw WebGL, or hybrid WebGL scene as a readable analytical view rather than a graphics demo.

## When to Use It

Use this when planning camera model, scene graph, scaling, overlays, shader contracts, GPU buffers, particles, or scene encodings.

## Key Takeaways

- Orthographic projection often reads better for chart-like views.
- Keep data-to-scene transforms explicit and reversible.
- Use DOM overlays for legends, labels, and exact readouts when possible.
- Separate analytical layers from context layers: basemap, substrate, marks, particles, labels, controls, and selection overlays.
- Keep WebGL responsible for dense marks, effects, and spatial transforms; keep HTML/SVG responsible for text, forms, keyboard focus, and accessible summaries.
- Use typed arrays and stable attribute schemas so render code can update small buffers or uniforms instead of rebuilding objects.
- Define a picking strategy early: deck.gl picking, Three.js raycasting, color/ID buffers, spatial indexes, or a companion CPU index.
- Keep 2D and 3D encodings perceptually disciplined. Position and length should carry primary quantitative meaning before color, opacity, glow, or motion.

## Architecture Patterns

- Three.js chart scene: explicit scale functions create `BufferGeometry`, `InstancedMesh`, `Points`, or custom `ShaderMaterial`; DOM overlays provide labels and exact values.
- deck.gl layer stack: layer props and accessors map data to positions, colors, widths, elevation, picking, and transitions; MapLibre, Mapbox, Google Maps, or ArcGIS owns the basemap when needed.
- PixiJS 2D stage: sprites, graphics, or `ParticleContainer` render dense 2D marks and particles; app state owns scales, filters, and accessibility mirrors.
- regl/TWGL/raw WebGL: typed arrays, shaders, uniforms, and draw commands define the whole visualization; use this for custom pipelines, not standard chart chrome.
- Hybrid stack: D3 or app code owns scales and data joins; WebGL owns dense mark layers; SVG/HTML owns axes, labels, annotations, controls, and focusable affordances.

## Encoding Guidance

- Spatial encodings: use x/y/z for measured dimensions, geography, network layout, embeddings, terrain, time slices, or simulation states.
- Color: reserve hue for categorical or semantic state; use luminance or sequential ramps for magnitude; avoid neon glows that mask density.
- Opacity: useful for density and fading trails, but document whether overlapping opacity means count, recency, uncertainty, or simply visual decay.
- Size: useful for salience and magnitude, but clamp or scale carefully so large marks do not hide neighboring data.
- Motion: use a named verb such as flow, accumulate, reveal, compare, transition, pulse, or highlight.
- Lighting and materials: use simple unlit materials for analytical marks unless surface shape or depth is the evidence.
- Camera: provide named states and reset controls; avoid unconstrained orbit when orientation carries meaning.

## Common Mistakes

- Letting camera freedom destroy orientation.
- Encoding too many variables at once with position, color, size, opacity, and motion.
- Baking labels, legends, sources, or caveats into a GPU texture when they need to remain editable and accessible.
- Treating particles as extra marks without documenting what emission rate, speed, lifetime, and opacity mean.
- Using perspective exaggeration or lighting shadows that distort quantitative reading.

## Adjacent Skills

- `../SKILL.md`
- `../../typescript-data-visualization-engineering/SKILL.md`
- `../../accessibility-and-inclusive-visualization/SKILL.md`

## Source Links

- [Three.js Points](https://threejs.org/docs/pages/Points.html)
- [Three.js PointsMaterial](https://threejs.org/docs/pages/PointsMaterial.html)
- [Three.js ShaderMaterial](https://threejs.org/docs/pages/ShaderMaterial.html)
- [Three.js RawShaderMaterial](https://threejs.org/docs/pages/RawShaderMaterial.html)
- [deck.gl View docs](https://deck.gl/docs/api-reference/core/view)
- [deck.gl Layer Catalog](https://deck.gl/docs/api-reference/layers)
- [PixiJS Renderers](https://pixijs.com/8.x/guides/components/renderers)
- [sigma.js Renderers](https://www.sigmajs.org/docs/advanced/renderers/)
