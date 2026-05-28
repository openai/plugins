# Cutaway, Terrain, and Domain Scenes

## What Problem This Solves

Scientific and mechanism-oriented 3D scenes need more than attractive geometry. They need honest scale, clear terminology, source-aware terrain or substrate data, and interaction that helps the viewer inspect the mechanism without changing the claim.

## Domain Contract

- Name which physical quantities are measured, inferred, simulated, schematic, or decorative.
- Keep terminology precise. For earthquakes, the epicenter is the surface point and the hypocenter or focus is underground.
- Use adaptive scales when a fixed global scale would make the selected detail unreadable. State the visible range and any vertical exaggeration.
- Label exact, approximate, and illustrative layers differently.
- For terrain, bathymetry, water, or surface models, record the source, API limits, sampling density, cache boundary, missing-data behavior, and fallback.

## Cutaway Geometry

- Decide whether the cut plane is fixed in camera/world space, fixed in object space, or animated between named states.
- If an object moves through a cut, compute or clip cut faces from the current object bounds rather than tuning wall lengths by eye.
- Keep exposed surfaces and data marks in the same coordinate system as the clipped object or explicitly document why they are overlays.
- Avoid permanent walls, patches, or rectangles that do not share the object silhouette.
- Show scale bars, depth axes, sea level, and vertical exaggeration notes when scale affects interpretation.

## Water And Surface Context

- Treat negative elevation or bathymetry as part of the terrain model, not as a decorative patch.
- Water should appear as a sea-level sheet over submerged cells, with submerged terrain or ocean floor below it when the data supports that.
- Shoreline contours should appear where terrain crosses sea level.
- If a public terrain API lacks bathymetry or misses coastal/island cases, use an explicit inferred-water fallback and label it as inferred or schematic.

## Interaction

- Horizontal rotation, zoom, reset, expand, and close controls should be part of the contract before coding.
- If the user must keep seeing inside the object while rotating, define whether the slice faces the camera, the object, or a fixed inspection plane.
- Pointer and wheel listeners should be attached where the user actually gestures, not only to an internal canvas that may not receive events.
- Reduced-motion should preserve the selected inspection state without requiring animation.

## QA

- Test a shallow case, deep case, offshore case, coastal case, missing-terrain case, and no-WebGL fallback.
- Verify drag, wheel, button controls, reset, expand, close, and keyboard/touch alternatives.
- Capture at least two rotation angles for cutaway geometry so clipped faces are checked against the object boundary.
