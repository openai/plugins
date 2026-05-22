# Visualization Test Plan

## Scope

- Visualization or dashboard:
- Editorial takeaway protected:
- User decision or workflow protected:
- Highest-risk regressions:

## Coverage Map

- Unit tests:
- Component tests:
- Visual regression tests:
- E2E tests:
- Editorial rubric checks:
- Human visual review checks:
- Semantic design contract checks:
- Sensitive-subject checks:
- Explicit non-goals:

## Data Strategy

- Real data sources used in tests:
- Mock boundary:
- Canonical fixture:
- Edge-case fixture:
- Stress or density fixture:
- Mobile/narrow fixture:
- Mobile portrait viewport fixture:
- Mobile landscape viewport fixture, if needed:
- Keyboard-open or visual viewport fixture:
- Touch/coarse-pointer fixture:
- Generated asset fixture or stub:
- Approved concept screenshot or reference:
- Approved large-screen concept reference:
- Approved mobile portrait concept reference:
- Approved mobile landscape concept reference, if needed:
- User approval record fixture:
- Concept review bullet summary fixture:
- Visual design contract fixture:
- Canonical URL-state fixture:
- Invalid or stale URL-state fixture:
- Persisted local/IndexedDB/remote saved-view fixture:
- Collapsed-control state fixture:
- Operational workspace shell fixture:
- Outline/search/filter/inspector synchronization fixture:
- Pan/zoom/reset and clear-selection fixture:
- Mobile command-panel fixture:
- Main-visualization-visible fixture:
- Spotty connection, stale, offline, partial, and reconnect fixtures:
- Permission-denied and unsupported-capability fixtures:
- Locked/flexible concept element fixture:
- Source and method ledger fixture:

## Determinism Controls

- Viewport and container sizes:
- Desktop, mobile portrait, and optional mobile landscape sizes:
- VisualViewport or keyboard-open dimensions:
- Fonts and theme tokens:
- Locale and timezone:
- Animation and motion policy:
- Reduced-motion fixture:
- Render-ready signal:
- Annotation collision checks:
- Direct-label clipping checks:
- URL share-link restore checks:
- Browser refresh and back/forward checks:
- Persisted-state precedence checks:
- Collapsed-panel keyboard and active-summary checks:
- Operational command bar, outline, filter, viewport, and inspector synchronization checks:
- Empty-surface click versus drag checks:
- Pan/zoom/reset and URL-restore checks:
- Mobile command-panel checks:
- Main visualization visibility and return-after-settings checks:
- Touch target, hit-area, tap, drag-alternative, and pinch/zoom checks:
- Spotty connection, stale/offline/partial-data, and reconnect checks:
- AR/camera/motion/vibration/notification/geolocation fallback checks:
- Color contrast and color-deficiency checks:
- Image overlay alignment checks:
- Concept-to-implementation visual fidelity checks:
- Semantic fidelity checks:
- Contract fidelity checks:
- Key-frame or final-frame screenshot checks:
- Sensitive-story static screenshot checks:

## Release Gates

- Required checks before merge:
- Required checks before release:
- Known tolerated diffs or exclusions:
- Minimum editorial rubric score:
- Required semantic design contract fields:
- Required user design approval record:
- Required concept review summary with plan and interaction bullets:
- Required large-screen and mobile concept references:
- Required locked/flexible concept element record:
- Required mobile portrait and optional landscape contract fields:
- Required URL/persistence contract fields:
- Required contrast and redundant-encoding review:
- Required collapsible-control/accessibility review:
- Required operational workspace shell review, if used:
- Required outline/filter/viewport/inspector synchronization review, if used:
- Allowed concept deviations:
- Required still-frame fallback:
- Required main-visualization-visible mobile gate:
- Required keyboard-open mobile gate:
- Required stale/offline/partial-data gate for remote or streaming data:
- Required permission fallback gate for device capabilities:
- Required source, caveat, and evidence-status visibility:
