# Library Selection for Builders

## What Problem This Solves

This reference helps TypeScript users choose between declarative tools, product-oriented chart libraries, and bespoke rendering.

## When to Use It

Use this when the user asks which TS or React charting library to adopt.

## Key Takeaways

- Use Observable Plot or Vega-Lite embeds for many standard tabular charts.
- Use D3 when the chart geometry or interaction is too custom for a higher-level abstraction.
- Use visx, ECharts, Chart.js, or similar product libraries when speed of integration matters more than custom semantics.
- Use Canvas2D when flat dense rendering, immediate-mode drawing, and custom hit testing justify moving away from SVG/DOM.
- Use WebGL when mark count, smooth pan/zoom, particles, flow animation, custom blending, shader effects, GPU picking, high-volume geospatial layers, or true 3D justify GPU complexity.
- Use Three.js for custom 3D scenes, point clouds, surfaces, volumes, instancing, and camera-led stories.
- Use deck.gl for high-volume geospatial and layer-based GPU visualization; use MapLibre, Mapbox, Google Maps, or ArcGIS as basemap hosts when needed.
- Use PixiJS for GPU-accelerated 2D sprite, particle, and texture-atlas visualizations.
- Use Sigma.js for large interactive graphs.
- Use Plotly WebGL traces or ECharts GL when a high-level charting API is the product fit.
- Use luma.gl, regl, TWGL, or raw WebGL2 only when custom shader and GPU pipeline ownership is truly required.

## Common Mistakes

- Choosing a library only by popularity.
- Starting bespoke when an embed or chart component would satisfy the product need.
- Choosing WebGL for small, static, label-heavy charts that need accessibility and export more than frame rate.
- Choosing raw WebGL before ruling out higher-level GPU libraries.
- Adding particles without a clear data meaning, reduced-motion behavior, and static fallback.

## Adjacent Skills

- `../SKILL.md`
- `../../grammar-of-graphics-and-declarative-visualization/SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../threejs-data-visualization/SKILL.md`

## Source Links

- [Observable Plot](https://observablehq.com/plot/what-is-plot)
- [Vega-Lite](https://vega.github.io/vega-lite/)
- [D3 API](https://d3js.org/api)
- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [Three.js Docs](https://threejs.org/docs/)
- [deck.gl Introduction](https://deck.gl/docs)
- [luma.gl Overview](https://luma.gl/docs)
- [regl](https://regl-project.github.io/regl/)
- [TWGL](https://twgljs.org/docs/)
- [PixiJS Renderers](https://pixijs.com/8.x/guides/components/renderers)
- [sigma.js Renderers](https://www.sigmajs.org/docs/advanced/renderers/)
- [Plotly JavaScript](https://plotly.com/javascript/)
- [ECharts GL](https://ecomfe.github.io/echarts-gl/)
