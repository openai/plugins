# Imagegen Interface Concept Prompts

Use this reference with the installed @imagegen skill when Frontend App Builder needs an overall visual concept before implementation. For new apps, dashboards, product interfaces, tools, games, websites, redesigns, and visually driven UI work from scratch, generate this concept unless the user explicitly says not to use Image Gen for concepting or asks you to follow existing code/design/art instead.

If the user asks to generate a concept ahead of time, review concept options, or wait for approval before implementation, stop after showing the generated concept and iterate with the user. Do not implement until the user approves the concept or asks to implement it. Once implementation starts, the approved concept becomes the active spec and must be implemented faithfully with browser verification.

## Quality Bar

Every interface concept should optimize for high-taste restraint:

- Agency-quality, minimal, polished, and intentional.
- One clear focal idea per viewport.
- Generous whitespace and strong hierarchy.
- Restrained color system with one or two purposeful accents.
- Elegant, readable typography with tasteful contrast.
- Fewer components, better executed.
- Clean UI with restrained content density by default.
- No extra content, sections, cards, metrics, labels, or decorative UI unless they directly support the user's request.
- Landing pages should make the offer, product signal, and primary action obvious without cramming the first viewport.
- Product interfaces and dashboards should feel useful and believable, with clear workflows, readable states, intentional density, and controls that can become clickable local-state interactions in the implementation.
- The concept must be implementable as a product surface, not just attractive art: show the primary workflow anatomy, real media/product area when relevant, and enough layout detail for faithful code translation.
- Game interfaces should establish the play surface, HUD/control placement, visual mood, and interaction affordances without cluttering the player's focus.

Avoid over-designed output unless the user explicitly asks for it:

- Busy sci-fi dashboards, cyberpunk HUD overlays, neon grids, excessive glow, and floating metric panels.
- Crammed feature-card walls, unnecessary badges, redundant icon rows, fake charts, and fake metrics.
- Decorative elements that do not clarify the product, action, or story.
- Generic stock-style layouts, placeholder gray boxes, unreadable UI text, fake brand names, and watermarks.
- Filling whitespace with content just because the canvas has room.
- Dense first screens unless the user specifically requested an operational dashboard, data-heavy interface, or game HUD that genuinely needs that density.

## Full Page Or App Concept

Use for new creative websites, landing pages, product pages, portfolios, microsites, dashboards, app screens, tools, game UIs, and visually distinctive app surfaces.

```text
Use case: ui-mockup
Asset type: full-page or app interface concept for implementation reference
Primary request: <user request>
Page purpose: <what the page must help the user do or understand>
Audience: <target visitor or operator>
Content priorities: <must-show sections, states, workflow steps, or information, in order>
Style/medium: high-taste agency-quality web UI mockup, minimal polished production-ready interface
Composition/framing: <desktop/mobile/wide hero/section stack/dashboard canvas/game screen/viewport or aspect ratio>; one clear focal idea, generous whitespace, restrained section count, no visual crowding
Typography direction: elegant readable web typography; <sans/serif/mono/display notes>
Color palette: <brand colors or tasteful palette>; restrained with one or two purposeful accents
Imagery: <product, people, environment, abstract, none>
Interaction feel: <quiet utility, editorial, premium product, playful, game-like, technical, etc.>
Motion/interaction direction: <subtle page-load choreography, hover/focus behavior, animated product preview, simulated interactive demo, scroll reveal, core app workflow, etc.>
Constraints: keep UI clean, intentional, and uncluttered; embrace whitespace; use less content unless the user explicitly asks for more or the dashboard/game requires intentional density; fewer elements, better hierarchy; include enough visual language to extend the rest of the page if the concept only shows one viewport; make app controls and workflow states implementable with local state; avoid unnecessary badges, cards, charts, icons, stats, HUD elements, controls, or decorative sections; keep exact copy and controls for code implementation
Avoid: busy dashboards, cyberpunk HUD overlays, neon grids, excessive glow, floating metric panels, crammed feature grids, overbuilt game HUDs, placeholder gray boxes, unreadable dense text, fake brand names, watermarks
```

## Redesign From Screenshot

Use when an existing site or app should be refreshed, restyled, modernized, or adapted to a new visual style.

```text
Use case: style-transfer
Asset type: website redesign concept for implementation reference
Input images: Image 1: edit target or visual reference screenshot of the existing website
Primary request: redesign the existing page with <requested style or goal>
Preserve: information architecture, core content hierarchy, navigation meaning, product/brand cues, and page purpose
Improve: visual hierarchy, spacing, typography, color, imagery, component polish, and overall composition through simplification, restraint, and better whitespace
Typography direction: <requested or inferred direction>
Color palette: <brand palette or tasteful modernization>; calmer, fewer accents
Motion/interaction direction: <how important visual elements should move, respond, or demonstrate product state and core workflow>
Constraints: change the visual treatment only; make it more minimal, premium, whitespace-forward, and agency-quality; reduce clutter rather than adding content; preserve the real workflow and controls so the implementation can be interactive; do not invent unrelated sections, fake metrics, fake logos, or new product claims; keep exact production copy for code implementation
Avoid: clutter, excessive decoration, cyberpunk HUD elements, neon grid overlays, floating metric cards, unreadable text, watermarks
```

If the screenshot is only a loose reference, label it as a reference image rather than an edit target and generate a new `ui-mockup` concept.

## Hero Or Section Concept

Use when the user asks mainly for a beautiful hero, above-the-fold treatment, pricing section, feature section, or other visually defined page slice.

```text
Use case: ui-mockup
Asset type: website section concept for implementation reference
Primary request: <requested section>
Section role: <what this section needs to communicate or let the user do>
Surrounding page context: <product/category/brand and adjacent sections if known>
Composition/framing: <full-width hero, split composition, editorial stack, product-led layout, etc.>
Typography direction: <clear type direction>
Imagery/materials: <raster imagery, product render, texture, or no generated asset>
Motion/interaction direction: <hover state, animated product state, scroll reveal, toggle, draggable comparison, etc.>
Constraints: design the section as implementable HTML/CSS UI; use one strong focal point; embrace whitespace; keep controls, labels, and final text in code; avoid unnecessary UI elements or excess content
Avoid: generic gradients, decorative filler, excessive cards, floating panels, unreadable UI text, watermarks
```

## After Generation

- Inspect the concept before coding. Extract the exact content, information architecture, and design system choices instead of treating the generated image as loose inspiration.
- Reject busy concepts before implementation. If it looks crammed, ask imagegen for a calmer version with fewer elements, more whitespace, a stronger focal point, and a more restrained palette.
- List the concrete implementation decisions: exact copy, nav items, CTA labels, section order, brand mark treatment, hero composition, layout, color tokens, type scale, spacing, radius, borders, shadows, image treatment, motion behavior, interactivity, core workflow, and responsive changes.
- Capture a concept-to-implementation inventory before coding: native concept size/aspect, first-viewport composition, headline line breaks, nav/header geometry, brand mark, panel/card topology, row counts, chart axes, drawers/rails, footer/status regions, data/copy values, asset roles, and visible control states.
- Treat the accepted concept as the visual specification for implementation. The coded result should match the concept's composition, hierarchy, proportions, palette, typography direction, and asset treatment as closely as possible.
- If the concept does not show the full requested page, extend the rest of the implementation in the same design language: spacing, type scale, palette, component geometry, imagery style, density, and interaction model.
- Generate individual raster assets after the overall concept is accepted when they are needed for fidelity: logos, brand marks, hero imagery, product mockups, editorial imagery, cutouts, textures, posters, thumbnails, avatars, or illustrations that are visible in the concept.
- Additional image generation should reproduce or isolate assets from the accepted concept. Do not create a second hero, character, product mockup, dashboard, or visual motif that changes the design direction.
- Do not use SVGs as stand-ins for generated visual assets. Use SVG only for icons, and recreate those icons faithfully or use an existing icon system only when it matches the concept accurately. Use imagegen for logos and brand marks unless the user provided an existing vector asset.
- Bring concept elements to life when they imply product behavior. Dashboards, charts, cards, maps, timelines, device frames, canvases, product mockups, or process flows should get believable hover states, animated state changes, lightweight controls, or simulated interactive demos when feasible.
- For app interfaces, implement the main user journey so the user can click through the product idea with believable local state, not just inspect a static composition. Controls shown in the concept should work against real local UI state.
- For media concepts, ensure posters and generated imagery do not hide required real video/audio playback. The implementation must verify the real media loads, plays, seeks, and changes visible frames.
- For clone-like UI concepts, preserve the recognizable skeleton and designed mock state before adding polish or live data.
- Keep final UI text, form fields, navigation, and interactive controls in code.
- Move only project-consumed final assets into the workspace. Preview concepts can stay in imagegen's default generated image location unless the user asks to keep them.
- Verify the implemented page in the Browser plugin / built-in app browser first. Load the app, inspect the first viewport, scroll, and click through the core workflow before falling back to Playwright.
- Use Playwright with Chromium only when Browser/IAB is unavailable, cannot access the page, cannot perform the needed interaction, or produces unreliable captures. State the fallback reason.
- Verify the implemented page against the concept before finishing. Compare the running UI, using transient screenshots when helpful, for layout, spacing, typography, color, image crops, motion, interactivity, and overall polish, then iterate on the code or assets until the result would pass a professional design-agency inspection. Keep going through this loop; do not stop at a partial implementation, a build that merely compiles, or a page that only captures the general vibe.
- Perform an agency pass before final: compare the concept-native aspect when practical, desktop, and mobile; name at least five concrete mismatches and fix them, or explicitly state that no material mismatches remain. Structural mismatches in topology, branding, copy, density, media behavior, or primary workflow block completion.
- Remove temporary QA-only screenshots, reports, scratch notes, and intermediate generated assets before handoff unless the user or benchmark explicitly requires them. The accepted concept image may remain available for user iteration.
