# When to Stay Declarative

## What Problem This Solves

This reference draws the boundary between clean declarative authoring and bespoke rendering.

## When to Use It

Use this when a declarative spec starts to feel strained or when the user asks whether to switch to D3, Canvas, WebGL, or Three.js.

## Key Takeaways

- Stay declarative when the chart remains readable as data plus marks plus encodings plus transforms.
- Leave declarative grammars when layout, behavior, or scale requirements become more complex than the resulting spec.
- Leave declarative grammars for WebGL only when GPU-scale marks, particles, custom shaders, GPU picking, true 3D, or high-volume geospatial layers are the real requirement.
- High-level authoring is a feature, not a limitation, when it fits.

## Common Mistakes

- Switching to lower-level code too early because it feels more powerful.
- Staying declarative after the spec has become opaque and brittle.

## Adjacent Skills

- `../SKILL.md`
- `../../d3-data-visualization/SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../threejs-data-visualization/SKILL.md`

## Source Links

- [Vega-Lite](https://vega.github.io/vega-lite/)
- [Observable Plot](https://observablehq.com/plot/what-is-plot)
- [D3 API](https://d3js.org/api)
- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
