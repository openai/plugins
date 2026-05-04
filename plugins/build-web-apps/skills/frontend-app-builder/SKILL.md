---
name: frontend-app-builder
description: Use for new frontend applications, dashboards, games, creative websites, hero sections, and visually driven UI from scratch, or when the user explicitly asks for a redesign/restyle/modernization. Builds from clean, airy, high-taste, readable image-generated concept design with section-specific references, faithful implementation, and browser testing.
---

# Frontend App Builder

Use this skill to create polished frontend apps, dashboards, games, creative websites, hero sections, redesigns, and other visually driven UI. Act first as a senior front-end designer, then as an engineer implementing an approved design spec.

## Core Standard

The two priorities of this skill outrank everything else:

1. Create enough great-looking Image Gen design first: clean, airy, distinctive, complete, readable, section-specific when needed, and not repetitive by default.
2. Do not stop until the accepted design and browser implementation match 10/10. Keep fixing visual, interaction, responsive, asset, and typography mismatches until `view_image` comparison would pass agency sign-off.

## Hard Rules

1. Use Image Gen for the visual concept unless the user explicitly opts out or the task is a small UI fix inside an existing design system.
2. Design the complete requested surface before coding. For a full page, app, dashboard, game, or product interface, a header or hero concept is not enough. For multi-section websites and long landing pages, prefer coordinated section-by-section concepts, plus an optional overview for rhythm, over one tall image that loses detail. For apps, dashboards, games, or compact product surfaces, generate the full primary screen plus any needed state, responsive, or asset concepts first.
3. Inside Codex, default multi-section website concepting to one fresh, large, readable Image Gen screenshot per major section. If the request has 1-10 sections, expect roughly 1-10 primary section images. Generate additional section/detail screenshots whenever text, buttons, card anatomy, typography, spacing, or colors are too small to extract. Do not crop or zoom an old full-page image as the main reference; regenerate a fresh standalone section or detail image that preserves the same design system.
4. In Plan mode, generate the design first, then use `request_user_input` to get design approval before planning implementation details.
5. Once accepted, the concept is a production design spec. No creative liberties during implementation: do not reinterpret layout, visible copy, hierarchy, container model, styling, imagery, density, or sections unless the user approves it or a concrete blocker requires it. General design heuristics never override the accepted concept.
6. The completion bar is agency-signoff faithful implementation: 10/10 fidelity to the accepted spec plus production-quality code. If the browser-rendered UI would receive design-review comments, keep fixing it.
7. Before coding, build a small design system from the accepted image: tokens, typography, component families, variants, spacing, icon treatment, and container rules. Include both content typography and UI chrome typography for tools, editors, and dashboards. Implement from that system so repeated elements stay consistent.
8. For new complex app UIs such as dashboards, admin tools, editors, data-heavy tools, and multi-panel product surfaces, default to React + Vite unless the user specifies another framework, the existing repo already dictates one, or the task is explicitly a single-file/static deliverable.
9. Hero eyebrow, kicker, pretitle, badge, or pill labels above the main heading are prohibited by default. Use one only when the user explicitly requested it or the accepted/reference design already contains it.
10. Verify in the Browser plugin / built-in browser first. Use Playwright Chromium only when Browser/IAB is unavailable or unreliable, and state the fallback reason.
11. Final handoff is blocked until you use `view_image` on both the accepted concept and the latest browser screenshot. This cannot be skipped or replaced with browser inspection alone. Judge the pair directly: is this agency-signoff faithfully implemented, and would a great, highly skilled design agency sign off on this exact implementation of the accepted design? If not, keep fixing.
12. Remove temporary QA artifacts before handoff unless the user or task explicitly asks to keep them.

## Image Gen Workflow

Read and follow the installed @imagegen skill. For website-specific briefing guidance, use `references/imagegen-website-concepts.md`.

Before calling Image Gen:

- Copy the user's concrete requirements into the brief: product/page purpose, audience, required sections or states, workflow, supplied copy, nav labels, CTA labels, data fields, required media, responsive needs, and implementation constraints.
- Ask for the complete requested surface: full page, app screen, dashboard, game screen, or coordinated section/state set. If the deliverable is more than a hero, say the concept must include downstream sections, states, or responsive continuation. If the section count is known or implied, name each section/state that needs its own concept screenshot.
- Repeat the implementation constraints: code-native app UI text and controls, fully rendered product/background assets with their own text and branding when appropriate, separable assets, reusable component families, intentional container model, no default card grids, no invented hero eyebrows/kickers/badges/pills, and practical HTML/CSS/component implementation.
- Preserve information architecture from user content, screenshots, or existing apps. Do not let Image Gen invent unrelated sections, fake metrics, new product claims, extra dashboards, new navigation, or a different product story.
- For multi-section websites or long landing pages, default to one coordinated concept image per major section. Use an optional overview only for structure and rhythm; never rely on one giant compressed board when it makes text, button details, card structure, spacing, or typography hard to analyze.
- For dense apps, dashboards, editors, product surfaces, and complex sections, generate separate state or detail concepts for the areas that would become unreadable in a single full-screen image: tables, sidebars, inspectors, modals, toolbars, charts, forms, cards, pricing blocks, testimonials, or media modules.
- If any concept screenshot is too small, blurry, cropped, crowded, or ambiguous for implementation, generate a fresh standalone section/state/detail screenshot before coding. Keep the same palette, typography mood, component family, asset treatment, density, and section order. Do not crop, slice, zoom, or reuse a tiny part of an earlier image as the source of truth.
- For games, plan a dedicated Image Gen asset pass in addition to the concept: transparent character/state sprites or sprite sheet, terrain/platform tiles, collectibles, hazards, goal/checkpoint objects, props, and 2-3 parallax/background layers when the environment has depth. HUD text, scoring, controls, physics, and collision remain code-native.

Reject or iterate on concepts that are header-only for a full-surface ask, cluttered, generic, repetitive, under-specified, unreadable, over-decorated, off-spec with hero eyebrows/kickers/badges/pills not explicitly requested or present in the reference, or not practical to implement faithfully.

## Design Quality Bar

The concept should look like a professional product mockup by a senior product designer:

- One clear creative idea or visual point of view.
- Strong first viewport with clear offer, product signal, and primary action.
- Full-page rhythm: sections, states, transitions, and mobile views feel designed as one system, without repetitive card stacks or repeated section formulas.
- Cohesive section-to-section flow: connect sections with shared spacing, palette, type rhythm, media treatment, and subtle transitions, not by inventing major new UI components.
- Excellent typography: clear hierarchy, scale, weight, line height, label treatment, and control/chrome text that never falls back to browser-default sizing.
- Intentional whitespace and density; no filler cards, hero eyebrow/kicker labels, pills, badges, fake metrics, or icon rows unless explicitly requested or present in the accepted design.
- Simpler by default: use fewer, stronger visual elements instead of filling the page with illustrations, iconography, decorative widgets, or complex UI chrome.
- Coherent visual system: palette, spacing, radius, borders, shadows, gradients, icon style, imagery, and component geometry.
- Icon fidelity matters when icons are present. Match the accepted design's icon metaphor, stroke weight, fill style, corner shape, size, color, alignment, and spacing instead of swapping in generic nearby icons.
- Color fidelity is mandatory. Match the accepted design's actual background, surface, text, border, shadow, and accent colors; if the design uses a white background, use white rather than cream, ivory, beige, warm gray, or any softened off-white substitute.
- Hero media treatment must match the accepted design. If the hero image has no color overlay or tint in the concept, the implementation must not add one. Use edge fades, masks, or background gradients only to blend image edges into the page; do not wash the image with a color overlay.
- High-quality generated assets for logos, brand marks, hero imagery, product renders, background scenes, illustrations, textures, posters, avatars, empty states, and game sprites/tiles/background layers. Product/background assets should be fully rendered with consistent branding and in-image text when that text belongs to the asset.
- Purposeful motion that clarifies hierarchy, reveals state, or makes the product feel tangible.
- Specific, non-generic copy when the user has not provided exact copy.

Default to clean, airy, tasteful 7/10 creativity: distinctive enough to feel designed, restrained enough to build, and not repetitive. Interpret "clean" as edited and legible, not empty or sterile.

## Visual Direction Defaults

Use these defaults when the user has not given stronger art direction. Adapt them to the product type instead of forcing every app into a marketing-site style.

- Baseline: roughly 7/10 creativity, low-to-medium density, generous spacing, high implementation clarity, high typography discipline, and image-led moments when the domain benefits from real visuals.
- Before generating concepts, choose a coherent visual direction: one theme paradigm, background character, typography character, hero or primary-screen architecture, section/app rhythm, 2-4 signature component motifs, and 1-2 motion cues. Commit to the combination so the design feels intentional instead of a generic template.
- Hero or first viewport: keep one obvious focal point, a short readable headline or primary task, restrained supporting copy, a visible primary action, and enough negative space to work on a small laptop. Do not overcrowd the opening view with stats, chips, badges, fake controls, or competing mini-panels.
- Header simplicity: default to a clean brand mark, essential navigation, and one primary action or control. Avoid icon-heavy nav, extra buttons, search bars, status widgets, segmented controls, decorative illustrations, or dense product chrome in the header unless the user explicitly asks for them or the product workflow requires them.
- Visual economy: prefer one or two high-quality image or illustration moments over many small decorative visuals. Use iconography only where it clarifies navigation, controls, or product meaning.
- Container discipline: avoid nested cards, giant rounded wrappers around every section, default bento/card grids, and over-framed dashboards unless the concept or product type truly needs them. Prefer open layouts, bands, rails, lists, tables, canvases, or a single purposeful framing move.
- Section rhythm: long pages should vary density, image-to-text ratio, alignment, scale, whitespace, and visual tempo while keeping one coherent brand system. Do not repeat the same centered block or left-text/right-card formula through the whole page.
- Section continuity: when multiple section concepts need to become one page, use connective tissue from the existing design system: gutters, bands, alignment, repeated typography, recurring media frames, color rhythm, and small transitional spacing shifts. Do not invent major new carousels, accordions, pricing cards, dashboards, forms, nav systems, feature grids, or other component families unless the user requested them or the accepted concepts show them.
- Media framing: generated imagery should usually sit in clear, implementation-friendly frames with stable aspect ratios, consistent crop logic, radius, shadows, and spacing. Avoid random image sizes or collage chaos unless the user explicitly asks for that direction.
- UI restraints: small labels, utility pills, pseudo-system markers, fake metrics, and decorative dashboard jargon are allowed only when they clarify the product. If they are just visual filler, remove them before acceptance.

## Concept Review Mode

Use only when the user asks to generate concepts first, review options, or wait for approval.

- Generate and show the concept.
- Iterate until the user approves.
- Do not implement while the user is still reviewing.
- Once approved, treat the concept as the active spec and follow the fidelity workflow below.

## Before Coding

Turn the accepted concept into a design system and implementation inventory before coding:

- Exact visible copy, nav items, CTA labels, section headings, proof points, data labels, and important UI text.
- Per-section/state image inventory: source concept screenshot, native aspect, visual priority, readable text, typography relationships, spacing, button/control styling, component/container rules, dominant colors, and any unresolved details that required a fresh extraction screenshot.
- Allowed above-the-fold copy list: every visible hero, nav, eyebrow/kicker/pretitle, badge/pill, CTA, label, and proof string allowed from the accepted concept or user-provided copy.
- First viewport composition, section order, downstream states, responsive continuation, and next-section preview.
- Section continuity plan: how adjacent sections connect using the accepted design system, and which major component families are allowed. Treat unshown major components as prohibited unless the user requested them or a required workflow cannot function without them.
- Brand mark, imagery roles, product mockups, dashboards, tables, charts, maps, media rails, forms, HUDs, or other visual artifacts.
- Hero/media treatment inventory: whether each image has no overlay, a color overlay, a gradient overlay, edge fade, mask, transparent background, or matching background color. Record this explicitly before coding.
- Standalone asset needs: if the concept includes a logo, brand mark, product label, packaging, poster, sign, product render, or branded background object, create matching standalone assets with Image Gen editing before implementation so branding stays coherent.
- Game asset needs: if the concept is a game, create matching production art assets with Image Gen before implementation. Include transparent sprite/state assets, tiles/platforms, collectibles, hazards, goal objects, props, and parallax/background layers as needed; use code for collision boxes and game state, not as a substitute for visible art.
- Design tokens sampled or approximated from the image: background, surface, text, muted text, border, shadow, accent, semantic colors, radii, elevation, spacing scale, and motion timing.
- Color lock: explicitly identify whether the concept background is true white, off-white, cream, gray, dark, or tinted, then implement that exact choice. Do not warm up, cool down, mute, or otherwise "tastefully" reinterpret the palette.
- Typography system: font family/fallback, type scale, weights, line heights, tracking, label treatment, heading/body/caption styles, control text styles, and responsive type behavior.
- Icon inventory: every visible icon, glyph, chevron, logo-like mark, toolbar symbol, status symbol, and empty-state symbol; record meaning, source family, outline vs filled style, stroke width, size, color, container, alignment, spacing, and selected/hover/disabled treatment.
- Component families and variants: buttons, navigation, rows, panels, media frames, product mockups, cards only where present, tables, forms, chips, icons, empty states, responsive variants, hover/focus/selected states.
- Component architecture plan for complex app UIs: app shell, navigation, major feature regions, reusable UI primitives, data/state helpers, chart/table/form modules, asset modules, and responsive layout boundaries. A great front-end implementation should have clear component ownership, not one giant `App` component or one-off copied markup.
- Container model: cards, panels, rails, bands, lists, tables, canvases, drawers, sidebars, modals, or full-bleed sections.
- Core workflow: controls that must respond, selected states, filters, tabs, edits, creation flow, success state, playback, game controls, or generated-result demo.

If the concept omits required downstream sections, states, mobile views, or readable detail for a complex area, generate matching section/state/detail concepts when visual consistency or extraction is uncertain. Otherwise extend in the exact same visual system.

## Implementation

- Build the real usable surface first, not a marketing wrapper around a future app.
- Follow the repo's framework, routing, component, styling, state, accessibility, and asset conventions.
- When creating a new complex app UI without an existing framework constraint, use React + Vite by default. Structure it like a senior front-end engineer would: small focused components, a clear app shell, reusable primitives for repeated controls, feature-specific modules for dashboards/tables/charts/forms, separated sample data and state helpers, and shared tokens/styles. Keep `App` as composition glue instead of a monolithic screen implementation.
- Implement through the design system extracted from the image. Similar elements must use the same component or shared style primitive; differences should be explicit variants, not one-off copied CSS.
- Implement the accepted concept exactly. Preserve copy, hierarchy, section order, density, colors, typography, spacing, radii, borders, shadows, asset framing, and interaction model.
- For multi-section pages, implement in slices that match the accepted section concepts. Start with the first viewport, compare its browser screenshot to the section concept, fix visible drift, then continue section by section. Do not defer all visual comparison until the whole page is coded, and do not merge or simplify section-specific design decisions just because a broad overview image is easier to follow.
- Connect sections into one cohesive page without adding unapproved major UI components. Use spacing, background bands, alignment, typography rhythm, repeated motifs, and media framing to bridge gaps. Do not invent new carousels, accordions, pricing blocks, dashboards, forms, tab systems, feature-card grids, or other large components to make the page feel complete unless they appear in the accepted concept, were requested by the user, or are recorded as a concrete functional necessity.
- Do not add new visible above-the-fold copy, hero eyebrows/kickers, explanatory labels, subtitles, or category text after concept acceptance unless it appears in the accepted concept, came from the user, or is recorded as an intentional deviation. If semantic HTML, SEO, or accessibility requires changing an H1 or heading level, change the element semantics first; do not invent compensating visible copy.
- Do not add decorative hero eyebrow labels, pills, badges, gradients, glows, or overlays that were not in the accepted design. Do not substitute a gradient treatment unless it matches the concept's palette, direction, intensity, and placement. If the accepted hero image has no color overlay, do not add a translucent tint, wash, or colored layer over it. If the image needs help blending into a non-matching page background, use a matching asset, transparent cutout, edge fade, mask, or background gradient around the image rather than a color overlay on top of the image. Do not replace white backgrounds with cream/off-white or otherwise shift the accepted color temperature.
- Define typography on controls deliberately. Do not rely on browser defaults or inherited `16px` sizing for buttons, tabs, inputs, toolbars, sidebars, inspector panels, layer rows, status bars, command palettes, or export/share controls.
- Preserve the container model. Do not add cards, bordered panels, floating containers, tiles, or card grids where the spec uses open whitespace, bands, rails, lists, tables, canvases, or full-bleed composition.
- Keep real interactive app UI text, navigation, buttons, forms, tables, controls, and labels code-native. This does not apply to text and branding that belong inside product images, posters, packaging, signs, background scenes, hero photos, or other raster assets. Do not ship a static screenshot as UI.
- Use Image Gen for central non-icon assets. Render product images and background assets completely with the needed text, logos, marks, labels, packaging, signage, and branding. When the asset must layer into the UI, request a transparent background or clean cutout. Quote exact asset text and require verbatim rendering when text matters.
- If the accepted design includes branded product imagery, use Image Gen editing to create standalone versions of the logo/product/packaging/signage assets from the concept or a matching asset pass. Include transparent-background variants when those assets need to layer into the UI. Do not rebuild branded raster assets from generic CSS, mismatched fonts, or approximate labels.
- For games, use Image Gen for visible production art: character/state sprites or sprite sheets, terrain/platform tiles, collectibles, hazards, goals/checkpoints, foreground props, and parallax/background layers. Do not fall back to canvas-drawn shapes because collision, scaling, or animation is simpler. Keep HUD text, score, controls, hit boxes, physics, and game state code-native, and tune collision geometry to the rendered assets. Any code-drawn or vector game art must be listed as an intentional deviation or concrete blocker.
- Do not replace concept assets with rough CSS drawings, generic gradients, placeholder SVGs, or stock-like crops. Images must sit naturally in the composition: background color, lighting, edges, crop, shadow, and transparency should blend with the surrounding design. SVG is fine for faithful icons and directional glyphs.
- Use SVG/icon components for arrows, chevrons, carets, disclosure indicators, pagination arrows, and carousel arrows; do not use plain text glyphs unless the concept intentionally does.
- Implement icons as faithfully as other visual elements. Prefer the repo's existing icon set or lucide only when it matches the accepted design's style; otherwise create a small custom SVG/icon variant that matches the concept. Custom SVG icons must be production-quality vector assets: clear `viewBox`, clean geometry, consistent stroke widths, aligned joins/caps, balanced negative space, optical centering, scalable paths, no jagged or placeholder-looking shapes, and `currentColor` or explicit fills only when they match the design system. Do not replace filled icons with outline icons, rounded icons with sharp icons, thick strokes with thin strokes, or specific metaphors with generic symbols. Keep icon color, optical size, baseline alignment, padding, and interactive states consistent with the extracted icon inventory.
- Make app interfaces experiential: local state, meaningful selected states, working filters/tabs/forms, editable or creatable items, success states, playback controls, game controls, or simulated generated output where appropriate.
- Use interactive UI inside a hero only when it genuinely fits: SaaS/software product previews, product demos, or purposeful interactive animation. Do not force fake interactive chrome into a branded, editorial, product, venue, food, consumer, or background-led hero. Faithful implementation and consistent branding are more important than adding interactivity.
- Add motion only where it supports the design. Respect accessibility and `prefers-reduced-motion`.
- Keep implementation production-oriented: semantic markup, stable responsive dimensions, no fragile hardcoded hacks, and type/lint/test checks when the repo supports them.

## Verification

Run the app and verify the visible product, not just the build.

1. Use Browser/IAB first. Load the app, inspect the first viewport, scroll, and click through the core workflow.
2. Check desktop, current browser viewport, and a mobile-sized viewport.
3. Capture or locate the accepted concept and the latest implementation screenshot. Use `view_image` on both in the same QA pass before final handoff; do not skip this step or substitute a browser glance for it.
4. Capture the implementation at the accepted concept's native dimensions when practical. If not practical, record the blocker and also verify the current browser viewport.
5. Write a fidelity ledger before final: mismatch, concept evidence, render evidence, and fix made or reason not fixed. For multi-section or multi-state specs, include evidence from the relevant section/state concept screenshots, not only the overview. Inspect at least five concrete comparison points covering copy, layout, typography, palette/gradients, asset treatment, spacing/container model, responsive behavior, or motion.
6. Compare side by side for copy, nav, CTA labels, section order, first-viewport balance, next-section visibility, palette, gradient treatment, font personality, type scale, spacing, borders, radii, container model, asset/background blending, motion, and simulated interactions.
7. Run an above-the-fold copy diff against the allowed copy list. Added, removed, renamed, or reordered visible copy must be fixed or listed as an intentional deviation; unapproved additions fail fidelity.
8. Audit typography everywhere, not just the hero or main canvas. Check headings, body, captions, labels, toolbar controls, sidebar rows, tabs, inputs, inspector fields, status bars, command palettes, export/share buttons, table cells, chart labels, and mobile line breaks. Use computed CSS sizes/weights/line-heights when the screenshot suggests drift.
9. Audit icons wherever they appear: nav, buttons, cards, toolbar controls, sidebars, tables, status indicators, empty states, pagination, carousels, and mobile controls. Check metaphor, stroke/fill style, size, color, alignment, optical weight, spacing, and state changes against the accepted concept.
10. For canvas/editor apps, audit app chrome separately from canvas/document text. Default zoom and pan are part of the spec; persisted local state must not hide seed, scale, or typography fixes during verification.
11. Ask explicitly: is this agency-signoff faithfully implemented, and would a great, highly skilled design agency sign off on this exact implementation of the accepted design? If anything would get a design-review comment, write a concrete repair checklist and keep editing. Do not final-answer with fixable visual issues.
12. Verify generated assets load, are framed correctly, and do not obscure text or controls.
13. Verify the core workflow updates real local UI state. Do not ship inert controls, fake media progress, hidden required media, or placeholder interactions.

Functional QA does not count as fidelity QA. Passing build checks, clicking controls, or verifying local state cannot replace the concept-to-screenshot comparison, native-size check, and written mismatch ledger.

Hard stops: clipped primary content, accidental wrapping, prototype-looking layout, rough seeded data, placeholder boxes, generic stock-like assets, unfinished cards, code-drawn game placeholders replacing concept art, invented visible copy, invented hero eyebrows/kickers/pills/badges, mismatched colors or gradients, white backgrounds changed to cream/off-white, unapproved hero image color overlays or tints, missing or generic substituted icons, mismatched icon style or stroke weight, images that do not blend with the background, stale debug artifacts, unreadable text, type-scale drift, browser-default control typography, mobile overflow, unprofessional responsive collapse, or any visible drift from the accepted spec.

## Surface Gates

- Landing/company sites: preserve first viewport, hero role, brand/nav/CTA labels, section order, next-section preview, and signature imagery.
- Product/SaaS pages: preserve product mockups, workflow diagrams, feature strips, proof elements, and brand treatment.
- Dashboards/tools: preserve density, sidebars, headers, tables, tabs, timelines, charts, maps, row counts, and selected/detail behavior. Do not turn table-driven concepts into card grids.
- Canvas/editor tools: preserve default zoom/pan, canvas/document text scale, chrome density, toolbars, sidebars, inspector controls, layer rows, status bars, command surfaces, and autosaved/seed-state behavior.
- Timeline/planning tools: preserve grid/time-axis anatomy, row spans, event density, status rails, and command-center fit.
- Clone-like interfaces: preserve the recognizable skeleton before adding polish. Do not add marketing heroes or custom navigation that breaks the product type.
- Games: preserve the art direction with Image Gen assets for sprites, tiles/platforms, collectibles, hazards, goals/checkpoints, props, and background/parallax layers. Verify assets load, scale, animate or swap state correctly, align with collision geometry, and support movement, action/jump/drag behavior, scoring, hazards, and restart.
- Media surfaces: verify real media load, duration, play/pause, seek/progress, and visible frame changes.
- Forms/booking/purchase/restaurant flows: verify the main transaction path and confirmation state.

## Final Response

Include the accepted concept path, rendered screenshot method, Browser/IAB verification method or Playwright fallback reason, `view_image` inspection of the accepted concept and latest implementation screenshot, native-size viewport checked or blocker, at least five inspected comparison points, above-the-fold copy diff result, remaining intentional deviations, and an explicit statement that the implementation was faithfully verified against the accepted design. Also include material mismatches fixed and core interaction path verified. If no material mismatches remain, say so directly.
