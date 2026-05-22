# Implementation Design and Tradeoffs

## What Problem This Solves

This reference makes new visualization work include a technical design, not just a chart or library recommendation.

## When to Use It

Use this before proposing or implementing:

- a new visualization
- a new dashboard or page composition
- a substantial rewrite or renderer migration
- a reusable chart component or design-system primitive

## Required Technical Design

For new work, include a concise technical design section that covers:

1. Surface shape
   - how many visualization instances may appear at once on a page
   - expected container sizes and responsive modes
   - large-screen, mobile portrait, and optional mobile landscape layouts
   - how the main visualization stays visible or is restored on mobile when settings, filters, inspectors, or the keyboard open
   - whether views are always visible, virtualized, tabbed, or expanded on demand
2. Data and interaction profile
   - rows, marks, or scene objects per instance
   - update cadence and animation expectations
   - interaction patterns such as hover, brush, zoom, filters, and linked views
   - touch, tap, drag, pinch, keyboard, visual viewport, and hover-replacement behavior
   - AR, camera, motion, vibration, notifications, geolocation, and permission fallbacks when used
   - stale/live/offline/partial/reconnect behavior for remote or streaming data
3. Shareability and persistence
   - canonical URL state for filters, selections, ranges, comparison groups, sort, tabs, zoom/map/camera state, drill-down path, and saved-view ids
   - localStorage, IndexedDB, or remote storage needs for personal preferences, collapsed panels, drafts, cached data, long configs, annotations, cross-device continuity, or team sharing
   - precedence rule for URL state versus persisted state
   - schema/versioning, validation, invalid-state fallback, privacy exclusions, and maximum URL size assumptions
   - history behavior for transient versus committed changes
4. Rendering architecture
   - chosen renderer and library
   - ownership boundaries between framework, chart logic, and rendering layer
   - export and accessibility implications
   - for WebGL: scene or layer ownership, buffer schemas, shader ownership, picking model, context lifecycle, and fallback path
5. Performance assessment
   - per-instance cost
   - multi-instance cost on the same page
   - main-thread, GPU, memory, and bundle implications
   - WebGL context count, GPU memory, texture memory, data upload cadence, draw-call count, and device pixel ratio
   - mobile battery, thermal, DPR cap, bandwidth, data-saver, and low-power assumptions
   - likely degradation or failure mode
6. Maintenance assessment
   - spec readability versus bespoke code
   - testability and debugging complexity
   - reuse across product surfaces
   - coupling risks to framework or app state
7. Recommendation
   - primary approach
   - fallback approach
   - assumptions that could change the decision

For advanced WebGL, 3D, geospatial, terrain, cutaway, particle, scrollytelling, or composite interactive work, also use `../../assets/templates/advanced-interactive-visualization-contract.md` before implementation. A short technical design is not enough when coordinate alignment, renderer ownership, camera state, fallback rendering, dense picking, or interaction timing can change the meaning of the visualization.

## Default Heuristics

- Unknown instance count is not a reason to skip the assessment. State a reasonable assumption such as one hero chart, 2 to 6 coordinated charts, or dozens of repeated mini-charts.
- A renderer that is fine once may fail when repeated across a dashboard or grid.
- Prefer higher-level, declarative, or standard abstractions when they meet the scale needs, because they usually lower maintenance cost.
- Prefer Canvas or GPU paths when repeated instance count, redraw frequency, or mark count makes DOM or SVG throughput risky.
- Prefer Canvas2D before WebGL for flat dense views when Canvas satisfies mark count, redraw cadence, hit testing, and export needs with less complexity.
- Prefer WebGL when GPU picking, shader effects, blending, particle count, 3D structure, high-volume geospatial layers, or smooth animation make Canvas2D or SVG/DOM impractical.
- Prefer shared data transforms and cached preprocessing over repeating expensive work per instance.
- Prefer URL state for meaningful analysis choices before adding private persistence. Local or remote storage should preserve drafts, preferences, saved views, and longer configs without preventing a shared link from opening the intended view.
- Prefer stable, typed view-state contracts over ad hoc query strings. Keep parsing, validation, defaults, and migration close to the visualization state model.
- Prefer collapsed or closable configuration and drill-down panels for secondary controls so the rendering surface, active selections, and source/caveat context remain visible.
- Prefer mobile-specific composition over desktop scaling. If a settings panel, keyboard, or permission prompt is needed, define how the user returns to the visualization and how active state remains visible.
- Prefer stale-but-visible remote visualizations over blank reconnect states. Show last updated time and whether data is live, stale, offline, partial, or reconnecting.
- Call out when virtualization, lazy loading, static snapshots, or server-side precomputation materially changes the recommendation.
- For particle or flow effects, specify what each particle represents, whether motion encodes value or only direction, and how reduced-motion and static exports preserve the claim.
- For WebGL/geospatial scenes, specify one primary scene owner, fallback trigger, coordinate-frame ledger, picking strategy, render-ready signal, and interaction state machine before coding.

## Common Mistakes

- Recommending a library without saying why it survives the page-level instance count.
- Optimizing a single chart demo while ignoring dashboard-level concurrency.
- Choosing the most flexible stack even when the maintenance burden is unnecessary.
- Ignoring export, accessibility, or testability until after the renderer is chosen.
- Ignoring deep links, saved views, or reload behavior until after interaction state is scattered across components.
- Encoding sensitive data, raw payloads, or huge configs directly in the URL.
- Treating WebGL as an automatic performance upgrade without assessing data upload, context pressure, and GPU memory.
- Adding particle effects before defining their data meaning and fallback.
- Shipping a desktop renderer choice that fails mobile touch, keyboard, bandwidth, battery, or thermal constraints.
- Treating AR, camera, motion, vibration, notifications, or geolocation as a feature idea without a fallback and permission plan.

## Adjacent Skills

- `../../skills/data-visualization/SKILL.md`
- `../../skills/visualization-strategy-and-critique/SKILL.md`
- `../../skills/react-and-nextjs-data-visualization/SKILL.md`
- `../../skills/typescript-data-visualization-engineering/SKILL.md`
- `../../skills/dashboards-and-real-time-visualization/SKILL.md`
- `./shareable-state-and-persistence.md`
- `./mobile-first-responsive-visualization.md`
