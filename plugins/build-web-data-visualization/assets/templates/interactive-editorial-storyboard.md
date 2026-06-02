# Interactive Editorial Storyboard

Use this before implementation for scrollytelling, animated, image-supported, 3D, map, or illustrated data stories.

## Story Contract

- Working headline:
- One-sentence takeaway:
- Reader question this answers:
- Stakes:
- What the reader should know after 10 seconds:
- What the reader should know after the full interaction:

## Evidence

- Dataset(s):
- Fictional/simulated status and seed:
- Unit, denominator, geography, and time span:
- Key comparison:
- Required baseline:
- Uncertainty, missingness, and caveats:
- Source and method note:

## Fictional Data Richness Contract

Use this for fictional, illustrative, or synthetic stories.

- Entity layer:
- Temporal layer:
- Spatial or physical layer:
- Event layer:
- Outcome layer:
- Derived comparison layer:
- Regeneration path:
- Invariants that must remain true:

## Sensitive Evidence Ledger

Use this for conflict, disaster, displacement, civilian harm, migration, political violence, or humanitarian stories.

| Layer | Source | Date shown to reader | Evidence status | Styling implication |
| --- | --- | --- | --- | --- |
| Map or geography |  |  | measured / estimated / schematic |  |
| Event or movement |  |  | measured / estimated / schematic |  |
| Human impact |  |  | measured / estimated / schematic |  |
| Context or research |  |  | measured / estimated / schematic |  |

- Humane language constraints:
- Visual effects to avoid:
- Caveats that must remain visible in static export:

## Artifact Mode

Choose one primary mode and optional secondary modes:

- Data-first chart:
- Generated object marks:
- Illustrated substrate:
- Cartographic flow field:
- 3D or camera-led surface:
- Scrollytelling sequence:

Why this mode is necessary:

What would be lost in a generic chart:

## Visual Design Concept Plan

- Is Codex image generation needed for overall layout, scene, key-frame, page-integration, or asset concepts:
- Existing page, article, report, deck, or app context to inspect first:
- Overall layout concept path:
- Overall large-screen concept path:
- Overall mobile portrait concept path:
- Overall mobile landscape concept path, if needed:
- Per-scene or key-frame concept paths:
- Per-layer or generated-asset concept paths:
- User design approval status: pending / approved / rejected
- Approval response, date, or review note:
- Requested changes and iteration notes:
- Approval scope:
- Semantic design contract path:
- Concept review response:
  - large-screen concept image shown to user:
  - mobile portrait concept image shown to user:
  - mobile landscape concept image shown to user, if needed:
  - concise scene plan bullets:
  - concise interaction bullets:
  - approval question asked before project changes or implementation code:
- Concept contract fidelity:
  - locked concept or key-frame elements:
  - flexible production details:
  - material deviations requiring user approval:
  - approved deviations:
  - concept-to-result traceability notes:
- Data layers, labels, values, caveats, and source notes that remain editable:
- Label-safe regions, overlay lanes, mobile portrait constraints, and optional landscape constraints:
- Main visualization visibility and settings-return behavior on mobile:
- Touch, pinch, keyboard, spotty-connection, and capability constraints:
- Intentional deviations allowed during implementation:

## Reference Transformation

- Visual references reviewed:
- Principle learned from each reference:
- Original transformation for this story:
- Publication-specific traits intentionally avoided:
- Similarity check after first render:

## Embedded Visualization Self-Use Gate

| Visual layer | Story job | Data shape | Specialist owner | Mini-brief summary | Interaction or fallback | QA check | Fresh-pass status |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  | delegated / local / lightweight exception |
|  |  |  |  |  |  |  | delegated / local / lightweight exception |

- Delegation authorization and runtime status:
- Delegated prompt scope, if used:
- Local specialist pass, if delegation is unavailable or unauthorized:
- Shared encoding constraints across layers:
- Layers intentionally kept simple, with reason:

## Scene Plan

| Scene | Reader sees | Data layer | Annotation | Motion purpose | Concept/key-frame contract | Interactive discovery | Static fallback |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |

## Asset Plan

- Generated assets needed:
- Hand-coded SVG/Canvas/Three.js assets needed:
- Source imagery or maps needed:
- Licensing or attribution requirements:
- Consistency requirements for perspective, scale, lighting, and color:
- Accessibility text for non-data imagery:

## Interaction Plan

- Default state:
- Scroll or step states:
- Hover or tap details:
- Selection or comparison controls:
- Keyboard path:
- Touch and pinch path:
- On-screen keyboard behavior:
- Spotty connection, stale/offline, and partial-data behavior:
- AR, camera, motion, vibration, notification, or geolocation role, if any:
- Reduced-motion behavior:
- Mobile portrait behavior:
- Mobile landscape behavior, if needed:

## Editorial Review

- Does the first frame communicate the claim?
- Does the animation reveal evidence rather than decorate it?
- Were Codex image-generated large-screen and mobile concepts shown with concise plan and interaction bullets, then approved by the user before project changes or implementation code began?
- Does the implemented story preserve the binding semantic design contract, locked elements, and approved deviations from any Codex image-generated concepts?
- Is every generated or illustrated element analytically useful?
- Are labels placed by judgment and free of collisions?
- Does a screenshot preserve the story?
- Does the mobile portrait version preserve the same reading order, source context, and caveat?
- Does mobile landscape exist when the story needs a wide handheld view?
- Does the mobile path keep the main visualization visible around settings and keyboard input?
- Do touch, stale/offline, and permission-denied paths preserve the story?
- If fictional, does the simulation provide enough evidence layers to support the visual density?
- Did each embedded visualization have a specialist owner, mini-brief, QA check, and delegated or local fresh-pass status?
- For sensitive subjects, are dated states, source notes, evidence status, and human-impact caveats visible without hover?
