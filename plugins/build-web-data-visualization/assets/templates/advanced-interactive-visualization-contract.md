# Advanced Interactive Visualization Contract

Use this after a visual concept is approved and before implementation begins for ambitious WebGL, 3D, geospatial, cutaway, particle, scrollytelling, or multi-layer interactive visualizations. Pair it with `visual-design-contract.md`; this file captures the implementation facts that prevent a polished concept from turning into a long correction loop.

## Approval And Evidence

- Approved concept set path or screenshot summary:
- Large-screen concept path or screenshot:
- Mobile portrait concept path or screenshot:
- Mobile landscape concept path or screenshot, if needed:
- User approval date or note:
- One-sentence claim or purpose:
- Primary audience:
- Dataset(s), sources, licenses, and update cadence:
- Measured, inferred, simulated, schematic, and decorative layers:
- Source/API limits, cache strategy, offline or fallback data:
- Mobile connection strategy:
  - last-known-good state:
  - stale/live/offline/partial indicators:
  - reconnect/backoff behavior:
  - low-bandwidth or data-saver degradation:
- Units, denominators, geography, time span, and uncertainty:
- Truth invariants the implementation must preserve:

## Renderer Ownership

- Primary renderer and why it is necessary:
- Fallback renderer and exactly when it appears:
- Layers owned by WebGL/Canvas/SVG/HTML:
- Rule for avoiding duplicate primary scenes:
- Render-ready signal before screenshots or interaction tests:
- WebGL context lifecycle, resize, DPR, context-loss, and cleanup plan:
- Static screenshot/export path:
- Large-screen, mobile portrait, and optional mobile landscape render bounds:
- Mobile DPR, quality, battery, and thermal budget:

## Coordinate Frames

| Layer | Coordinate system | Transform owner | Alignment check |
| --- | --- | --- | --- |
|  |  |  |  |

- Projection or globe convention:
- Longitude origin and wrap policy:
- Latitude, depth/elevation, and vertical exaggeration policy:
- Texture, basemap, marker, label, and hit-test alignment checks:
- Shortest-path camera or rotation rule:

## Visual Encoding Ledger

| Data or state | Visual channel | Scale/range | Must not imply |
| --- | --- | --- | --- |
|  |  |  |  |

- Color-role ledger:
- Contrast hierarchy for focal data, selected state, annotations, context, and controls:
- Glows, pulses, particles, halos, thickness, blur, and motion mappings:
- Selection, hover, focus, alert, disabled, stale, and loading states:
- Legend/key text that proves the mapping:
- Essential values that must be visible without hover:
- Essential values that must be visible on mobile without hover:

## Shareability And Persistence

| State | URL | Storage tier | Restore behavior |
| --- | --- | --- | --- |
|  |  |  |  |

- Canonical URL parameters or saved-view id:
- State excluded from URL:
- LocalStorage preferences:
- IndexedDB or remote saved-view payload:
- URL versus persisted-state precedence:
- Schema/version and invalid-state fallback:
- Copy-link, saved-view, reset, refresh, and back/forward behavior:
- Collapsed or closable controls, inspectors, and drill-down areas:
- Active state summary visible outside collapsed panels:

## Operational Workspace Shell

- Shell type:
  - single visualization
  - tri-pane workspace
  - dashboard console
  - map or diagram operations tool
- Command or status bar:
- Outline or navigation rail:
- Filter or control rail:
- Central visualization viewport:
- Inspector or analysis rail:
- Default selected entity or focus region:
- Empty-surface click versus drag behavior:
- Mobile command bar:
- Mobile outline, filter, and details panel behavior:
- Synchronized state between outline, filters, marks, viewport, and inspector:

## Interaction State Machine

| State | Entered by | Visual response | Exit/resume rule |
| --- | --- | --- | --- |
| default |  |  |  |
| hover/preview |  |  |  |
| selected/committed |  |  |  |
| expanded/detail |  |  |  |

- Drag, wheel, pinch, keyboard, touch, reset, close, and escape behavior:
- Pan/zoom controls and empty-surface clear-selection behavior:
- Browser scroll/gesture ownership:
- Mobile portrait interaction path:
- Mobile landscape interaction path, if needed:
- On-screen keyboard and visual viewport behavior:
- Touch target and hit-area policy:
- Drag alternatives and dense-mark step-through controls:
- AR, camera, motion, vibration, notification, and geolocation capability audit:
  - purpose:
  - permission timing:
  - fallback when denied or unsupported:
- Dense mark picking strategy:
- Hover disambiguation and step-through controls:
- Idle animation pause/resume policy:
- Reduced-motion behavior:

## Domain Scene Contract

- Context substrate or basemap:
- Labels and multiscale label policy:
- Cutaway, terrain, bathymetry, mechanism, or physical model:
- Adaptive scale rules:
- Mobile portrait adaptation:
- Mobile landscape adaptation, if needed:
- What is exact versus illustrative:
- What happens when domain data is missing:

## QA Checklist

- Build/type/lint command:
- Desktop screenshot:
- Mobile portrait screenshot:
- Mobile landscape screenshot, if needed:
- WebGL nonblank or canvas-pixel check:
- Fallback screenshot:
- Interaction smoke tests:
- Operational shell, outline, filter, viewport, and inspector synchronization checks:
- Touch, pinch, keyboard-open, and settings-return smoke tests:
- Spotty-connection, stale/offline/partial-data checks:
- Permission-denied or unsupported-capability checks:
- Coordinate alignment spot checks:
- Concept-to-result fidelity review:
- Accessibility and reduced-motion checks:
- Known deviations and whether they are approved:
