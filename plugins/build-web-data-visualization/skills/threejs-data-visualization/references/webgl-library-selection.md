# WebGL Library Selection

## What Problem This Solves

This reference helps choose the right WebGL-capable library for 2D, 2.5D, 3D, geospatial, graph, particle, scientific, and product visualization work.

## When to Use It

Use this when the user asks for WebGL, GPU acceleration, Three.js, raw WebGL, particles, animated flows, high-density marks, large graphs, geospatial WebGL, or a renderer comparison.

## Decision Tree

1. Can the chart be expressed as a standard tabular chart with modest marks?
   - Use Observable Plot, Vega-Lite, Plotly, ECharts, D3/SVG, or another higher-level tool before WebGL.
2. Is the problem dense but flat, with simple marks and mostly immediate-mode drawing?
   - Try Canvas2D first. Move to WebGL when animation, mark count, blending, picking, or shader effects exceed Canvas2D comfort.
3. Is it high-volume geospatial, trips, arcs, point clouds, hex bins, heatmaps, or map overlays?
   - Use deck.gl for analytical layers. Pair with MapLibre, Mapbox, Google Maps, or ArcGIS when a product basemap is needed.
4. Is it vector-tile product mapping with style layers, heatmaps, clustering, terrain, globe, or map camera controls?
   - Use MapLibre GL JS or Mapbox GL JS. Add deck.gl for heavy analytical overlays.
5. Is it a 3D globe, 3D Tiles, terrain, time-dynamic geospatial scene, or high-precision WGS84 visualization?
   - Use CesiumJS.
6. Is it a custom 3D analytical scene, point cloud, surface, volume, instanced glyph field, camera-led story, or custom particle system?
   - Use Three.js.
7. Is it a full 3D simulation-like experience needing physics, GPU particles, rich materials, WebXR, or a game-engine style scene graph?
   - Consider Babylon.js.
8. Is it GPU-accelerated 2D sprites, texture atlases, millions of lightweight particles, or expressive 2D animation?
   - Use PixiJS.
9. Is it a large interactive graph where graph-specific rendering, layout integration, labels, and hover affordances matter?
   - Use Sigma.js.
10. Is it a high-density scientific chart where a declarative API matters more than full rendering control?
   - Use Plotly WebGL traces such as `scattergl`, `pointcloud`, or 3D traces, or ECharts GL if the product already uses ECharts.
11. Is it a large geospatial exploratory application rather than a custom visualization component?
   - Consider kepler.gl when the user needs an embeddable analysis UI with filters, layers, trips, and map configuration built on deck.gl and MapLibre.
12. Is it a specialized 2D scatterplot with extreme point counts and lasso interactions?
   - Consider regl-scatterplot before building the same primitive from raw WebGL.
13. Is the goal custom shaders without a scene engine?
   - Use luma.gl when you want a modern vis.gl GPU foundation, regl for compact command-style WebGL, TWGL for low-boilerplate raw WebGL helpers, or raw WebGL2 for maximum control.

## Library Notes

- Three.js is the general-purpose default for bespoke 3D data scenes. It has a mature scene graph, cameras, controls, `BufferGeometry`, `InstancedMesh`, `Points`, `ShaderMaterial`, and `RawShaderMaterial`.
- deck.gl is the general-purpose default for high-volume analytical layers, especially geospatial layers. It includes picking, layer transitions, binary attributes, aggregation layers, trips, arcs, paths, point clouds, 3D tiles, and basemap integrations.
- luma.gl sits below deck.gl and is appropriate when a custom GPU pipeline should still use typed device abstractions, shader modules, buffers, textures, animation loops, and WebGL/WebGPU-aware APIs.
- raw WebGL2 is appropriate only when the team must own the full GPU pipeline: shaders, buffers, VAOs, framebuffers, textures, transform feedback, extensions, context loss, and debugging.
- regl is a good low-level choice when the developer wants command descriptions that reduce WebGL shared-state bugs while retaining shader control.
- TWGL is a small helper layer for raw WebGL projects where reducing boilerplate matters more than adopting a renderer.
- PixiJS is excellent for 2D particles, sprites, texture atlases, GPU-accelerated graphics, and playful or editorial animation. It is not a chart grammar, so scales, axes, accessibility, and exact readouts remain application responsibilities.
- Sigma.js is purpose-built for graphs. Use it for large interactive networks before building a graph renderer from scratch.
- MapLibre GL JS is the open-source default for GPU vector-tile maps. Mapbox GL JS is appropriate when Mapbox platform integration and hosted map tooling are product requirements.
- CesiumJS is the default for globe, terrain, 3D Tiles, time-dynamic geospatial analysis, and 3D/2D/2.5D geographic modes.
- Babylon.js is rarely the first choice for charts, but it is valuable for simulation-like 3D, GPU particles, rich materials, WebXR, and large-world rendering.
- Plotly and ECharts GL are pragmatic when high-level configuration, product integration, and common chart types matter more than renderer ownership.
- kepler.gl is a ready-made large-scale geospatial exploration application and embeddable React component built on deck.gl and MapLibre. Use it when the product can adopt its UI and state model instead of building a custom map.
- regl-scatterplot is a specialized WebGL scatterplot for very large point sets, pan/zoom, and lasso workflows.
- Stardust and d3fc WebGL can be useful for GPU mark rendering, but confirm maintenance status and ecosystem fit before choosing them for long-lived products.

## Recommendation Format

When recommending a WebGL stack, include:

- primary renderer and one fallback
- why SVG/DOM and Canvas2D are not the best fit
- expected mark count, animation cadence, and interaction model
- accessibility and export strategy
- reduced-motion and static fallback
- GPU memory, context count, and mobile/device assumptions
- what code owns scales, transforms, picking, labels, and data updates

## Common Mistakes

- Choosing Three.js for a product map that MapLibre or deck.gl would handle more directly.
- Choosing raw WebGL before proving deck.gl, luma.gl, regl, PixiJS, or Three.js cannot handle the job.
- Using a game engine for a chart whose difficulty is labels, scales, and interaction.
- Choosing WebGL for small static charts where SVG export, text, and accessibility matter more than raw frame rate.
- Ignoring licensing, bundle size, SSR constraints, and framework lifecycle cleanup.

## Adjacent Skills

- `../SKILL.md`
- `../../data-visualization/references/default-stack-selection.md`
- `../../typescript-data-visualization-engineering/SKILL.md`
- `../../geospatial-and-cartographic-visualization/SKILL.md`

## Source Links

- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [Three.js Docs](https://threejs.org/docs/)
- [deck.gl Introduction](https://deck.gl/docs)
- [luma.gl Overview](https://luma.gl/docs)
- [regl](https://regl-project.github.io/regl/)
- [TWGL](https://twgljs.org/docs/)
- [PixiJS Renderers](https://pixijs.com/8.x/guides/components/renderers)
- [sigma.js Renderers](https://www.sigmajs.org/docs/advanced/renderers/)
- [MapLibre GL JS](https://maplibre.org/projects/gl-js/)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/guides/)
- [CesiumJS](https://cesium.com/platform/cesiumjs/)
- [Babylon.js Specifications](https://www.babylonjs.com/specifications/)
- [Plotly JavaScript](https://plotly.com/javascript/)
- [ECharts GL](https://ecomfe.github.io/echarts-gl/)
- [kepler.gl Docs](https://docs.kepler.gl/)
- [regl-scatterplot](https://github.com/flekschas/regl-scatterplot)
- [Stardust Documentation](https://stardustjs.github.io/documentation/)
- [D3FC](https://d3fc.io/index.html)
