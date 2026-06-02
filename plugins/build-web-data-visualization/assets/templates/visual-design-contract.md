# Visual Design Contract

Use this after the user approves a Codex image-generated concept set or layout sketch for an advanced data visualization. The contract turns the approved large-screen and mobile concepts into binding implementation requirements that preserve both visual intent and data meaning. Do not use this contract to authorize implementation while user approval is pending or rejected, and do not treat approved concepts as loose design references.

## Approved Concept

- Concept path or screenshot reference:
- Large-screen concept path or screenshot reference:
- Mobile portrait concept path or screenshot reference:
- Mobile landscape concept path or screenshot reference, if needed:
- Concept scope:
  - visualization only
  - existing page integration
  - report or deck layout
  - scrollytelling scene
  - animation key frame
  - generated asset or substrate
  - operational workspace or console shell
- Native aspect ratio or intended output size:
- Target large-screen viewport or output size:
- Target mobile portrait viewport:
- Target mobile landscape viewport, if needed:
- Target surface:
- Existing page, report, deck, or app context inspected:
- User approval status: pending / approved / rejected
- Approval response, date, or review note:
- Approval scope:
- Concept review bullets shown before approval:
  - plan:
  - interactions:
- Requested changes before approval:
- Intentional deviations from the concept:

## Contract Fidelity

- Locked concept elements that must carry into implementation:
  - artifact mode:
  - reading path:
  - dominant focal area:
  - relative layout and scale:
  - visual hierarchy:
  - color roles:
  - label-safe regions:
  - source/caveat placement:
  - interaction or motion staging:
  - mobile portrait continuation:
  - mobile landscape continuation, if needed:
  - export continuation:
- Flexible production details:
  - exact spacing:
  - typography tokens:
  - renderer-specific geometry:
  - breakpoint mechanics:
  - asset crops:
- Material deviations requiring user approval:
- Deviations already approved or accepted as meaning-preserving:
- Concept-to-result traceability notes:

## Evidence Lock

- One-sentence takeaway:
- Insight title:
- Dataset(s):
- Fields bound to visible marks:
- Unit, denominator, geography, and time span:
- Required comparison, baseline, or threshold:
- Source and method note:
- Uncertainty, missingness, aggregation, or caveat:
- Truth invariants the implementation must preserve:

## Semantic Mapping

| Concept element | Data/source layer | Editable/data-bound layer | Visual role | Caveat or constraint |
| --- | --- | --- | --- | --- |
|  |  | yes / no |  |  |
|  |  | yes / no |  |  |
|  |  | yes / no |  |  |

- Labels, values, axes, legends, and source notes that must remain editable:
- Generated imagery or raster elements and their analytical role:
- Label-safe regions, anchor points, and overlay constraints:
- Elements that are decorative and can be removed if they compete with evidence:

## Layout And Reading Path

- Default first thing the reader should notice:
- Secondary context:
- Annotation sequence:
- Direct-label strategy:
- Color roles:
- Contrast hierarchy and focal accent:
- Typography and hierarchy notes:
- Operational workspace shell, if used:
  - command or status bar:
  - outline or navigation rail:
  - filter/control rail:
  - central visualization viewport:
  - inspector or analysis rail:
  - default selection or focus region:
- Mobile portrait adaptation:
- Mobile command bar or panel model:
- Main visualization visibility rule on mobile:
- Settings, filters, or detail panels:
  - collapsed or closable behavior:
  - active-state summary when closed:
  - return-to-visualization behavior after Apply/Cancel/Reset/close:
- On-screen keyboard behavior:
- Touch target and hit-area policy:
- Hover replacement:
- Drag, swipe, pinch, and zoom ownership:
- Mobile landscape rationale and layout, if used:
- Spotty connection, stale, offline, or partial-data behavior:
- AR, camera, motion, vibration, notification, or geolocation capabilities:
  - analytical purpose:
  - permission timing:
  - fallback when denied or unsupported:
- Static export or screenshot requirements:

## Shareability And Persistence

- URL-backed state:
- State intentionally excluded from URL:
- Copy-link or share affordance:
- Saved-view id, slug, or remote snapshot behavior:
- LocalStorage preferences:
- IndexedDB drafts, cached state, or annotations:
- URL versus persisted-state precedence:
- Invalid, stale, or missing URL-state fallback:
- Browser back/forward behavior:
- Collapsed or closable configuration areas:
- Active filters, selections, caveats, and source context visible when panels are collapsed:

## Motion Or Interaction

- Animation or interaction purpose:
- Explanatory verb:
- First frame:
- Key frames or states:
- Final frame:
- Reduced-motion behavior:
- Keyboard and touch path:
- Mobile gesture path:
- Pan, zoom, reset, escape, and clear-selection behavior:
- On-screen keyboard path:
- Vibration, alert, or notification behavior:
- Camera, AR, motion, or geolocation behavior:
- What motion or interaction must not imply:

## Fidelity QA

- Visual fidelity checks:
- Evidence fidelity checks:
- Interaction fidelity checks:
- Contract fidelity checks:
- Accessibility checks:
- Mobile/export checks:
- Mobile portrait checks:
- Mobile landscape checks, if needed:
- Operational workspace shell checks:
- Outline, search, filter, viewport, and inspector synchronization checks:
- Pan/zoom/reset and clear-selection checks:
- Main-visualization visibility checks:
- Keyboard-open viewport checks:
- Touch target and gesture checks:
- Stale/offline/partial-data checks:
- Permission denied or unsupported capability checks:
- Material mismatches found:
- Fixes or accepted deviations:
