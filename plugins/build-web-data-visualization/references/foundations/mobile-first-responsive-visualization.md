# Mobile-First Responsive Visualization

## Purpose

Use this reference whenever a visualization will be viewed in a browser, app, dashboard, story, report preview, or embedded page that could reasonably reach mobile users. Mobile is a primary surface, not a compressed desktop afterthought.

Default assumption: design for both large screen and mobile portrait unless the user explicitly scopes the work away from one of those surfaces. Add a mobile landscape design when the evidence, interaction, or device capability benefits from a wide handheld orientation.

## Research Grounding

Mobile visualization is not only a smaller viewport problem. Mobile devices differ by screen size, aspect ratio, input precision, one-handed use, movement, noisy surroundings, connection quality, battery, sensors, and permission-gated capabilities. Responsive visualization should adapt layout, scale, encoding, attention cues, and interaction to those changing constraints instead of only resizing one chart.

Use these principles with the rest of the plugin's evidence, accessibility, and contract workflows:

- design sibling states for large screen and mobile, not one squeezed composition
- preserve the same claim, caveat, source context, and primary evidence across states
- reduce density by prioritizing, aggregating, faceting, stepping, or disclosure before shrinking labels
- make touch, keyboard, screen reader, reduced-motion, and static export paths real
- treat device capabilities such as AR, camera, motion, vibration, and notifications as opt-in analytical enhancements with alternatives

## Required Concept Set

For advanced concept-first visualization work, generate and review at least:

- large-screen concept, usually around desktop or laptop proportions
- mobile portrait concept, usually around a narrow phone viewport

Add a mobile landscape concept when any of these are true:

- the visualization uses a wide substrate such as a timeline, route, map, field, court, network, Gantt chart, matrix, waveform, video, or 3D scene
- the mobile interaction benefits from two-handed use, pinch/zoom, brushing, scrubbing, or comparison across a horizontal range
- AR, camera, or motion makes orientation part of the experience
- the on-screen keyboard would otherwise hide the main evidence during search, annotation, or filter editing
- the design would be tempted to ask users to rotate the device

Do not ask the user to approve only the large-screen concept unless they explicitly asked for desktop only. If image generation is unavailable, provide the paired concept prompts and stop at the same approval gate.

## Mobile Design Contract

Record these facts before implementation:

- target mobile portrait viewport and optional landscape viewport
- what remains visible without scrolling on first load
- how the main visualization stays present while controls, filters, details, or settings are open
- how users return to the main visualization after applying or dismissing settings
- touch, tap, drag, swipe, pinch, wheel, keyboard, and screen-reader paths
- hover replacement: tap, focus, selection, step-through, or always-visible labels
- touch target policy and spacing
- on-screen keyboard behavior and visual viewport handling
- connection, stale-data, offline, and reconnect behavior for live or remote data
- sensor/capability audit: AR, camera, motion/orientation, vibration, notifications, geolocation, and whether each is justified
- reduced-motion, battery, thermal, data-saver, and low-power behavior
- static screenshot/export behavior for mobile

## Main Visualization Stays Present

Mobile layouts must not place a left rail, filter builder, prose block, or settings stack above the visualization merely because it appears first in the desktop DOM. The default mobile view should lead with the main evidence or an insight summary plus the main evidence immediately below it.

Use these patterns:

- put secondary controls in a bottom sheet, drawer, popover, segmented control, inline toolbar, or collapsible section
- keep active filters, selections, caveats, and source status visible while controls are collapsed
- after a setting is applied, return focus and scroll position to the affected visualization or keep it visible during the edit
- use a full-screen editor only when the setting task needs it, and provide Apply, Cancel, and Reset paths that return to the chart
- avoid "settings first, chart later" mobile stacks unless the setting itself is the product's primary task

## Layout And Encoding

- Favor one primary thought per mobile screen. Secondary analysis can be reached through tabs, steppers, drill-down, small multiples, or expandable details.
- Recompute scales, ticks, labels, and annotations from measured container size. Do not rely on a desktop `viewBox` scaled down until text is unreadable.
- Prefer direct labels and chart-adjacent keys. Move long labels to a numbered key or detail panel when they collide, but keep essential categories visible.
- Reduce axis ticks, legend items, map markers, network labels, and annotation density on mobile while preserving the claim.
- Convert dense tables to critical columns, row cards, in-cell bars/sparklines, or an expand-on-row detail view.
- Use stable aspect ratios and explicit plot height. Preserve plot area rather than letting titles, legends, notes, or controls consume the whole mobile viewport.
- For maps, use fewer markers, shorter labels, mobile-specific marker visibility, narrow aspect ratios, and keys for long labels.
- For diagrams and node-link views, prefer a curated initial viewport focused on the most important region over shrinking the whole graph.

## Touch And Gesture Rules

- Do not rely on hover for essential values, labels, or caveats.
- Use Pointer Events for unified mouse, pen, and touch handling when implementing custom interactions.
- Make coarse-pointer targets at least WCAG 2.2 minimum size, and prefer larger 44-48 CSS px hit areas for primary mobile controls when space allows.
- Use larger invisible hit regions for small marks.
- Provide simple pointer alternatives for drag-only actions, such as buttons, steppers, selected-item controls, or direct numeric inputs.
- If the chart captures drag, wheel, or pinch, explicitly define browser gesture ownership with `touch-action`, scroll containment, reset controls, and an alternate path.
- Prefer two-finger zoom, explicit zoom buttons, or an expanded inspection mode over hijacking one-finger page scroll.
- For dense marks, add nearest-item selection, previous/next step-through, search, or lasso alternatives rather than depending on pixel-perfect taps.

## Keyboard And Visual Viewport

The on-screen keyboard changes the visual viewport without necessarily changing the layout viewport. Any mobile design with search, filters, notes, formulas, thresholds, comments, or annotations must account for that.

- Keep the main evidence visible or quickly restorable when an input focuses.
- Avoid placing the only Apply or Close action where the keyboard will cover it.
- Anchor critical overlays to the visual viewport when possible.
- Use short forms, segmented controls, sliders, steppers, chips, or presets when they avoid unnecessary typing.
- Preserve focus order and do not trap users inside a panel that hides the chart without a clear exit.

## Mobile Capabilities Audit

Use permission-gated and sensor capabilities only when they add analytical value:

- AR/WebXR: use for spatial scale, placement, inspection, room/site context, terrain, physical assets, or embodied comparison. Provide a non-AR 2D/3D fallback.
- Camera: use for scan, overlay, measurement, field capture, object/site comparison, or data entry when the camera materially reduces work. Ask only after a user action and explain the benefit.
- Motion/orientation: use for coarse orientation, reveal, tilt-to-inspect, field orientation, or stability cues. Do not make motion the only precise input path.
- Vibration/haptics: use sparingly for meaningful confirmation, threshold crossing, alerts, or event feedback, such as a goal, anomaly, completed upload, or critical warning. Never rely on vibration alone.
- Notifications/alerts: use only for user-requested thresholds, long-running jobs, monitoring events, or time-sensitive changes. Provide in-app status and permission recovery paths.
- Geolocation: use only when the user's location changes the analysis or filtering, and provide manual location or region selection.

For any capability, record purpose, permission timing, fallback, privacy risk, battery/data cost, and how users can still complete the task when denied or unsupported.

## Streaming And Spotty Connections

For streaming, live, remote, or API-backed visualizations on mobile:

- do not blank the visualization during reconnects; keep the last known good state with a stale indicator
- show last updated time, update cadence, and whether the view is live, delayed, cached, partial, or offline
- use exponential backoff, resumable cursors, snapshot-plus-delta repair, and late/out-of-order event handling where relevant
- degrade to lower update frequency, smaller windows, aggregated summaries, or static snapshots on poor connections or data-saver signals
- queue local edits or annotations when safe, then resolve conflicts explicitly
- make stale, partial, empty, and error states visually distinct from normal data

Treat `navigator.onLine` and connection APIs as hints, not as the only source of truth.

## Performance And Power

- Test on mobile-sized viewports and, when possible, real mobile hardware or throttled profiles.
- Cap device pixel ratio or rendering quality for Canvas/WebGL when battery, memory, or thermal pressure matters.
- Pause offscreen scenes, hidden tabs, inactive routes, and non-visible animation loops.
- Lazy-load heavy images, video, tile layers, 3D assets, and WebGL bundles while reserving layout space.
- Prefer responsive image sizes and mobile-specific crops for generated substrates and backgrounds.
- Keep repeated microcharts virtualized or shared when hundreds of instances would create memory pressure.

## QA Checklist

Before shipping, verify:

- large-screen and mobile portrait concept images exist for concepted work, with mobile landscape when justified
- desktop, mobile portrait, and optional landscape screenshots preserve the same claim and caveat
- the main visualization appears before or alongside controls on mobile first load
- opening, applying, closing, or resetting settings keeps or restores the visualization
- touch, tap, drag, pinch, keyboard, reduced-motion, and screen-reader paths work
- on-screen keyboard does not hide the only critical action or permanently obscure the evidence
- active filters, selections, source/caveat, stale/live state, and reset path are visible
- spotty connection, reconnect, offline/stale, empty, and partial-data states are tested
- permission-gated capabilities have user-initiated prompts, fallbacks, and no page-load prompt
- text, labels, hit targets, and data marks remain legible at 360-430 px widths
- static export or screenshot preserves the evidence without hover, autoplay, or permissions

## Source Links

- [Responsive Visualization Design for Mobile Devices](https://www.tableau.com/research/publications/responsive-visualization-design-mobile-devices)
- [W3C WAI: WCAG 2.2 target size and dragging movement updates](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)
- [MDN: Pointer events](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events)
- [MDN: VisualViewport](https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport)
- [MDN: NetworkInformation](https://developer.mozilla.org/en-US/docs/Web/API/NetworkInformation)
- [MDN: Navigator.onLine](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine)
- [MDN: MediaDevices.getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [MDN: WebXR Device API](https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API)
- [MDN: Vibration API](https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API)
- [MDN: DeviceMotionEvent](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent)
- [MDN: Notifications API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API)
- [web.dev: Web permissions best practices](https://web.dev/articles/permissions-best-practices)
- [Datawrapper: responsive chart height control](https://www.datawrapper.de/blog/responsive-height-control)
- [Datawrapper: mobile locator map guidance](https://www.datawrapper.de/academy/locator-maps-for-mobile-devices)
