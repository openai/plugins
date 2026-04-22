---
name: frontend-app-builder
description: Use when building frontend applications with generated visual assets and browser testing.
---

# Frontend App Builder

Use this skill to turn a frontend application request into a working, visually checked app. Design or source the needed visual assets with built-in Codex image generation, implement those designs in code, then verify the result with the Browser plugin and built-in app browser unless the user asks not to.

## Workflow

1. Read the existing app structure, scripts, styling system, and asset locations before editing.
2. Define the minimum visual direction and asset list needed for the screen or flow.
3. Prefer built-in Codex image generation for missing raster assets such as hero imagery, product scenes, illustrations, textures, mockups, icons, thumbnails, and empty-state art.
4. Implement the design in the app using the repo's existing framework, routing, component, styling, and asset conventions.
5. Use the Browser plugin / built-in app browser for frontend testing unless the user explicitly asks not to use it.
6. Fix issues found during browser testing, then repeat the browser check for the changed surfaces.

## Asset Design

- Use existing brand or product assets when the user has provided them; otherwise use built-in Codex image generation instead of placeholder gradients, generic SVG decoration, or empty gray boxes.
- Prompt generated assets with concrete subject, style, composition, aspect ratio, background needs, and intended UI placement.
- Keep UI text, labels, numbers, and controls in code rather than baked into generated images.
- Store generated or edited assets in the project's normal public/static asset location and reference them through the app's existing asset pipeline.
- Prefer assets that reveal the actual product, use case, state, or atmosphere the interface needs to communicate.

## Implementation

- Build the real usable surface first, not a marketing wrapper around a future app.
- Match existing conventions for components, tokens, spacing, routing, state, loading, errors, and empty states.
- Keep layouts responsive with stable dimensions for images, toolbars, grids, cards, and controls so generated assets do not cause shifting or overlap.
- Make the generated assets serve the interface: crop, mask, size, and lazy-load them intentionally instead of dropping them in at arbitrary dimensions.
- Supplement implementation with type checks, linting, and unit tests when the repo already uses them.

## Browser Testing

- Use the Browser plugin and built-in app browser to open the local app, inspect screenshots, and interact with the main workflow unless the user asks not to use it.
- Check at least one desktop viewport and one mobile-sized viewport when the UI is user-facing.
- Confirm generated assets load, are framed correctly, and do not obscure text or controls.
- Verify primary actions, navigation, hover/focus states, responsive wrapping, and obvious loading or error states.
- If the built-in app browser is unavailable, state that clearly and use the closest available visual/browser fallback.
