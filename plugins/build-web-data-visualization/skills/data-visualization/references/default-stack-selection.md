# Default Stack Selection

## What Problem This Solves

This reference gives builder-friendly defaults for selecting a stack without overfitting every problem to a favorite tool.

## When to Use It

Use this when a user asks which tool or library to choose.

## Key Takeaways

- Start with declarative grammars for standard tabular charts.
- Make stack choices against the expected page-level instance count, not just a single-chart prototype.
- Make stack choices against mobile portrait, optional mobile landscape, touch, keyboard, bandwidth, battery, and device capability constraints, not only desktop benchmarks.
- Use D3 when the chart needs custom geometry or interaction beyond the grammar.
- Use Canvas when density, continuous redraw, or repeated microcharts such as sparkline tables make DOM/SVG expensive.
- Use WebGL when GPU acceleration is essential for dense 2D marks, smooth pan/zoom, particles, flow animation, GPU picking, custom blending, shader effects, true 3D, or high-volume geospatial layers.
- Use Three.js for bespoke 3D scenes, point clouds, instancing, surfaces, volumes, camera-led stories, and custom particle systems.
- Use deck.gl for high-volume geospatial or layer-based analytical visualization: trips, arcs, paths, point clouds, heatmaps, hex bins, 3D tiles, picking, and basemap overlays.
- Use PixiJS for GPU-accelerated 2D sprites, particles, texture atlases, and expressive 2D animation when chart semantics are application-owned.
- Use native scroll, `position: sticky`, IntersectionObserver, Scrollama, CSS ScrollTimeline/ViewTimeline, Motion `useScroll`, or GSAP ScrollTrigger for scrollytelling controllers before choosing the chart renderer.
- Use enterprise Gantt components such as Bryntum, DHTMLX, Kendo UI Gantt, Syncfusion Gantt, or similar when editable scheduling, dependencies, calendars, resources, baselines, critical path, import/export, and undo are product requirements.
- Use lighter Gantt or timeline libraries such as Highcharts Gantt, Frappe Gantt, Plotly timelines, Observable Plot, or D3/SVG for read-only schedules, executive roadmaps, or editorial schedule graphics.
- Use FullCalendar resource timeline or scheduler-style components for resource booking when the resource calendar matters more than project dependency semantics.
- Use a virtualized hybrid HTML/SVG/Canvas Gantt when large row counts, dense dependency layers, or frequent hover/drag redraws make DOM/SVG expensive.
- Use PlantUML, Mermaid, Graphviz DOT, D2, Structurizr DSL, DBML, or BPMN XML for source-backed UML-like documentation before building a custom renderer.
- Use React Flow for editable React node-edge diagrams, Cytoscape.js for graph analysis and larger interactive networks, Sprotty for model-driven diagram tools, JointJS or GoJS for full-featured diagram editors, and ELK or Dagre for auto-layout.
- Use Sigma.js for large interactive graph and network visualization.
- Use Plotly WebGL traces or ECharts GL when a high-level charting API is more important than custom rendering control.
- Use kepler.gl when the requirement is an embeddable large-scale geospatial exploration UI rather than a custom map component.
- Use regl-scatterplot for specialized large scatterplot, pan/zoom, and lasso workflows before hand-writing the same raw WebGL primitive.
- Use luma.gl, regl, TWGL, or raw WebGL2 only when custom shaders or GPU pipelines are genuinely required and the team can own low-level debugging.
- Use Leaflet or MapLibre for slippy maps, tiled navigation contexts, and product-map interaction patterns before forcing D3 or deck.gl into that role.
- Use Google Maps when managed basemaps, Places, routing, or broader Google Maps Platform integration are part of the product requirement.
- Use CesiumJS for 3D globe, terrain, 3D Tiles, and time-dynamic geospatial scenes.
- Weigh maintenance cost alongside raw performance when several stacks could satisfy the chart.
- Treat WebGL performance as workload-specific. It is often faster than SVG/DOM for large marks and continuous animation, but Canvas2D can be faster or simpler for flat immediate-mode views with modest interaction and fewer GPU-specific needs.
- Particle effects are renderer features, not chart types. Recommend them only when they explain flow, direction, accumulation, recency, focus, anomaly, risk, or state.
- Device APIs such as AR/WebXR, camera, motion, vibration, notifications, and geolocation are interaction capabilities, not visualization defaults. Recommend them only with an analytical purpose, permission fallback, and mobile QA plan.

## Common Mistakes

- Defaulting to D3 because it is flexible.
- Defaulting to dashboards for every operational question.
- Treating every map as an analytical cartography problem when the real need is a product map with pan, zoom, markers, and familiar controls.
- Picking a stack that works for one instance but becomes fragile or slow when repeated across the page.
- Choosing WebGL for small, static, label-heavy charts where SVG or a declarative grammar would be clearer.
- Choosing a generic charting library for an editable Gantt product before checking scheduling, dependency, calendar, resource, import/export, accessibility, and undo requirements.
- Choosing a diagram widget before deciding whether the source of truth is XMI/UMLDI, PlantUML, Mermaid, DOT, D2, Structurizr DSL, DBML, BPMN XML, or a renderer-neutral JSON model.
- Treating project-management exports as already normalized chart data.
- Choosing raw WebGL before ruling out deck.gl, Three.js, PixiJS, Sigma.js, luma.gl, regl, or Canvas2D.
- Using particles as decoration without a data meaning, legend, reduced-motion behavior, and static fallback.
- Choosing an animation library before deciding whether the story should be scrollytelling, a stepper, small multiples, or static key frames.
- Choosing a renderer that is impressive on desktop but fails mobile touch, keyboard, spotty connection, battery, or thermal constraints.

## Adjacent Skills

- `../../scrollytelling-and-parallax-data-visualization/SKILL.md`
- `../../grammar-of-graphics-and-declarative-visualization/SKILL.md`
- `../../gantt-chart-visualization/SKILL.md`
- `../../uml-and-software-architecture-visualization/SKILL.md`
- `../../d3-data-visualization/SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../threejs-data-visualization/SKILL.md`
- `../../geospatial-and-cartographic-visualization/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [Observable Plot](https://observablehq.com/plot/what-is-plot)
- [Vega-Lite](https://vega.github.io/vega-lite/)
- [D3 API](https://d3js.org/api)
- [PlantUML](https://plantuml.com/)
- [Mermaid syntax reference](https://mermaid.js.org/intro/syntax-reference)
- [Graphviz DOT language](https://graphviz.org/doc/info/lang.html)
- [D2 documentation](https://d2lang.com/)
- [Structurizr DSL](https://docs.structurizr.com/dsl)
- [React Flow](https://reactflow.dev/learn/concepts/terms-and-definitions)
- [Cytoscape.js](https://js.cytoscape.org/)
- [Eclipse ELK](https://eclipse.dev/elk/documentation.html)
- [Scrollama](https://github.com/russellsamora/scrollama)
- [GSAP ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
- [Motion useScroll](https://motion.dev/docs/react-use-scroll)
- [MDN: CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [deck.gl](https://deck.gl/docs)
- [Three.js Docs](https://threejs.org/docs/)
- [MDN: WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [luma.gl](https://luma.gl/docs)
- [PixiJS](https://pixijs.com/8.x/guides/components/renderers)
- [sigma.js](https://www.sigmajs.org/docs/advanced/renderers/)
- [Plotly JavaScript](https://plotly.com/javascript/)
- [ECharts GL](https://ecomfe.github.io/echarts-gl/)
- [kepler.gl Docs](https://docs.kepler.gl/)
- [regl-scatterplot](https://github.com/flekschas/regl-scatterplot)
- [Leaflet Documentation](https://leafletjs.com/reference-2.0.0.html)
- [MapLibre GL JS](https://maplibre.org/projects/gl-js/)
- [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [CesiumJS](https://cesium.com/platform/cesiumjs/)
- [DHTMLX Gantt docs](https://docs.dhtmlx.com/gantt/)
- [Bryntum Gantt features](https://bryntum.com/products/gantt/features/)
- [Highcharts Gantt docs](https://www.highcharts.com/docs/gantt/getting-started-gantt)
- [Frappe Gantt docs](https://frappe.io/gantt)
- [FullCalendar resource timeline](https://fullcalendar.io/docs/timeline-view)
