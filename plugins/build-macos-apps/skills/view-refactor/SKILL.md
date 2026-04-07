---
name: view-refactor
description: Refactor macOS SwiftUI views and scenes with strong defaults for small dedicated subviews, stable sidebar and selection structure, explicit command and toolbar ownership, scene-aware state, and narrow AppKit escape hatches. Use when cleaning up a macOS view file, splitting oversized scene roots, removing iOS-centric patterns, or tightening mixed SwiftUI/AppKit architecture.
---

# View Refactor

## Overview

Refactor macOS views toward small, explicit, stable scene and view types. Default
to native SwiftUI for layout, selection, commands, and settings. Reach for AppKit
only at the narrow edges where desktop behavior truly requires it.

## Core Guidelines

### 1) Model scenes explicitly

- Break the app into meaningful scene roots: main window, settings, utility windows, inspectors, or menu bar extras.
- Do not let one giant root view silently own every desktop surface.

### 2) Keep a predictable file shape

- Follow this ordering unless the file already has a stronger local convention:
- Environment
- `private`/`public` `let`
- `@State` / other stored properties
- computed `var` (non-view)
- `init`
- `body`
- computed view builders / other view helpers
- helper / async functions

### 3) Prefer dedicated subview types over many computed `some View` fragments

- Extract meaningful desktop sections like sidebar rows, detail panels, inspectors, or toolbar content into focused subviews.
- Keep computed `some View` helpers small and rare.
- Pass explicit data, bindings, and actions into subviews instead of handing down the whole scene model.

### 4) Keep selection and layout stable

- Prefer one stable split or window layout with local conditionals inside it.
- Avoid top-level branch swapping between radically different roots when selection changes.
- Let the layout be constant; let state drive the content inside it.

### 5) Extract commands, toolbars, and actions out of `body`

- Do not bury non-trivial button logic inline.
- Do not mix command routing, menu state, and layout in the same block if they can be named clearly.
- Keep `body` readable as UI, not as a desktop view controller.

### 6) Use scene and app storage intentionally

- Use `@SceneStorage` for per-window ephemeral state when it truly helps restore the scene.
- Use `@AppStorage` for durable preferences, not transient UI toggles that only matter in one window.
- Keep scene-owned state close to the scene root.

### 7) Keep AppKit escape hatches narrow

- If a representable or `NSWindow` bridge exists, isolate it behind a small wrapper or helper.
- Do not let AppKit references spread through unrelated SwiftUI views.
- If the bridge starts owning the feature, re-evaluate the architecture.

### 8) Observation usage

- For `@Observable` reference types on modern macOS targets, store them as `@State` in the owning view.
- Pass observables explicitly to children.
- On older deployment targets, fall back to `@StateObject` and `@ObservedObject` where needed.

## Workflow

1. Identify the current scene boundary and whether the file is trying to do too much.
2. Reorder the file into a predictable top-to-bottom structure.
3. Extract desktop-specific sections into dedicated subview types.
4. Stabilize the root layout around selection, scenes, and commands rather than top-level branching.
5. Move action logic, command routing, and toolbar behavior into named helpers or separate types.
6. Tighten any AppKit bridge so the imperative edge is small and explicit.
7. Keep behavior intact unless the request explicitly asks for structural and behavioral changes together.

## Common Smells

- A root view that mixes window scaffolding, settings, toolbar code, command handling, and detail layout.
- iOS-style push navigation forced into a Mac sidebar-detail problem.
- Several booleans for mutually exclusive inspectors, sheets, or utility windows.
- AppKit objects passed through many SwiftUI layers without a clear ownership reason.
- Large computed view fragments standing in for real subviews.

## Notes

- A good macOS refactor should make scene structure, selection flow, and command ownership obvious.
- When the problem is fundamentally a missing desktop pattern, use `swiftui-patterns`.
- When the problem is fundamentally a boundary with AppKit, use `appkit-interop`.
