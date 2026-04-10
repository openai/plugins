---
name: liquid-glass
description: Implement, refactor, or review modern macOS SwiftUI UI for the new design system and Liquid Glass. Use when adopting Liquid Glass, updating NavigationSplitView, toolbars, search, sheets, and controls, removing custom backgrounds that fight system materials, or building custom glass surfaces with glassEffect, GlassEffectContainer, and glassEffectID.
---

# Liquid Glass

## Overview

Use this skill to bring a macOS SwiftUI app into the modern macOS design system
with the least custom chrome possible. Start with standard app structure,
toolbars, search placement, sheets, and controls, then add custom Liquid Glass
only where the app needs a distinctive surface.

Prefer system-provided glass and adaptive materials over bespoke blur, opaque
backgrounds, or custom toolbar/sidebar skins. Audit existing UI for extra fills,
scrims, and clipping before adding more effects.

## Workflow

1. Read the relevant scene or root view and identify the structural pattern:
   `NavigationSplitView`, `TabView`, sheet presentation, detail/inspector
   layout, toolbar, or custom floating controls.
2. Remove custom backgrounds or darkening layers behind system sheets,
   sidebars, and toolbars unless the product explicitly needs them. These can
   obscure Liquid Glass and interfere with the automatic scroll-edge effect.
3. Update standard SwiftUI structure and controls first.
4. Add custom `glassEffect` surfaces only for app-specific UI that standard
   controls do not cover.
5. Validate that glass grouping, transitions, icon treatment, and foreground
   activation are visually coherent and still usable with pointer and keyboard.
6. If the UI change also affects launch behavior for a SwiftPM GUI app, use
   `build-run-debug` so the app runs as a foreground `.app` bundle rather
   than as a raw executable.

## App Structure

- Prefer `NavigationSplitView` for hierarchy-driven macOS layouts. Let the
  sidebar use the system Liquid Glass material instead of painting over it.
- For hero artwork or large media adjacent to a floating sidebar, use
  `backgroundExtensionEffect` so the visual can extend beyond the safe area
  without clipping the subject.
- Keep inspectors visually associated with the current selection and avoid
  giving them a heavier custom background than the content they inspect.
- If the app uses tabs, keep `TabView` for persistent top-level sections and
  preserve each tab's local navigation state.
- Do not force iPhone-only tab bar minimize/accessory behavior onto a Mac app.
  On macOS, prefer a conventional top toolbar and native tab/search placement.
- If a sheet already uses `presentationBackground` purely to imitate frosted
  material, consider removing it and letting the system's new material render.
- For sheet transitions that should visually originate from a toolbar button,
  make the presenting item the source of a navigation zoom transition and mark
  the sheet content as the destination.

## Toolbars

- Assume toolbar items are rendered on a floating Liquid Glass surface and are
  grouped automatically.
- Use `ToolbarSpacer` to communicate grouping:
  - fixed spacing to split related actions into a distinct group,
  - flexible spacing to push a leading action away from a trailing group.
- Use `sharedBackgroundVisibility` when an item should stand alone without the
  shared glass background, for example a profile/avatar item.
- Add `badge` to toolbar item content for notification or status indicators.
- Expect monochrome icon rendering in more toolbar contexts. Use `tint` only to
  convey semantic meaning such as a primary action or alert state, not as pure
  decoration.
- If content underneath a toolbar has extra darkening, blur, or custom
  background layers, remove them before judging the new automatic scroll-edge
  effect.
- For dense windows with many floating elements, tune the content's scroll-edge
  treatment with `scrollEdgeEffectStyle` instead of building a custom bar
  background.

## Search

- For a search field that applies across a whole split-view hierarchy, attach
  `searchable` to the `NavigationSplitView`, not to just one column.
- When search is secondary and a compact affordance is better, use
  `searchToolbarBehavior` instead of hand-rolling a toolbar button and a
  separate field.
- For a dedicated search page in a multi-tab app, assign the search role to one
  tab and place `searchable` on the `TabView`.
- Make most of the app's content discoverable from search when the field lives
  in the top-trailing toolbar location.
- On iPad and Mac, expect the dedicated search tab to show a centered field
  above browsing suggestions rather than a bottom search bar.

## Controls

- Prefer standard SwiftUI controls before creating custom glass components.
- Expect bordered buttons to default to a capsule shape at larger sizes. On
  macOS, mini/small/medium controls preserve a rounded-rectangle shape for
  denser layouts.
- Use `buttonBorderShape` when a button shape needs to be explicit.
- Use `controlSize` to preserve density in inspectors and popovers, and reserve
  extra-large sizing for truly prominent actions.
- Use the system glass and glass-prominent button styles for primary actions
  instead of recreating a translucent button background by hand.
- For sliders with discrete values, pass `step` to get automatic tick marks or
  provide specific ticks in a `ticks` closure.
- For sliders that should expand left and right around a baseline, set
  `neutralValue`.
- Use `Label` or standard control initializers for menu items so icons are
  consistently placed on the leading edge across platforms.
- For custom shapes that must align concentrically with a sheet, card, or
  window corner, use a concentric rectangle shape with the
  `containerConcentric` corner configuration instead of guessing a radius.

## Custom Liquid Glass

- Use `glassEffect` for custom glass surfaces. The default shape is capsule-like
  and text foregrounds are automatically made vibrant and legible against
  changing content underneath.
- Pass an explicit shape to `glassEffect` when a capsule is not the right fit.
- Add `tint` only when color carries meaning, such as a status or call to
  action.
- Use `glassEffect(... .interactive())` for custom controls or containers with
  interactive elements so they scale, bounce, and shimmer like system glass.
- Wrap nearby custom glass elements in one `GlassEffectContainer`. This is a
  visual correctness rule, not just organization: separate containers cannot
  sample each other's glass and can produce inconsistent refraction.
- Use `glassEffectID` with a local `@Namespace` when matching glass elements
  should morph between collapsed and expanded states.

## Review Checklist

- Standard structures and controls were updated first before adding custom
  glass.
- Opaque backgrounds, dark scrims, and custom toolbar/sheet fills that fight the
  system material were removed unless intentionally required.
- `searchable` is attached at the correct container level for the intended
  search scope.
- Toolbar grouping uses `ToolbarSpacer`, `sharedBackgroundVisibility`, and
  `badge` instead of one-off hand-built chrome.
- Icon tint is semantic, not decorative.
- Custom glass elements that sit near each other share a
  `GlassEffectContainer`.
- Morphing glass transitions use `glassEffectID` with a namespace and stable
  identity.
- Any SwiftPM GUI app used to test the result is launched as a `.app` bundle,
  not as a raw executable.

## Guardrails

- Do not rebuild system sidebars, toolbars, sheets, or controls from scratch if
  standard SwiftUI APIs already provide the modern macOS behavior.
- Do not apply custom opaque backgrounds behind a `NavigationSplitView`
  sidebar, system toolbar, or sheet just because an older version needed
  one.
- Do not scatter related glass elements across multiple
  `GlassEffectContainer`s.
- Do not tint every icon or glass surface for visual variety alone.
- Do not assume an iPhone tab/search behavior is the right answer on macOS.
  Prefer desktop-native toolbar, split-view, and inspector placement.
- Do not leave a GUI SwiftPM app launching as a bare executable when reviewing
  Liquid Glass behavior; missing foreground activation can make a design bug
  look like a rendering bug.

## When To Use Other Skills

- Use `swiftui-patterns` when the main question is scene architecture,
  sidebar/detail layout, commands, or settings rather than Liquid Glass-specific
  treatment.
- Use `view-refactor` when the main issue is file structure, state
  ownership, and extracting large views before design changes.
- Use `appkit-interop` when the design requires window, panel, responder-chain,
  or AppKit-only control behavior.
- Use `build-run-debug` when you need to launch, verify, or inspect logs
  for the app after the visual update.
