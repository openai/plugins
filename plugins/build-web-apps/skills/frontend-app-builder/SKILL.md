---
name: frontend-app-builder
description: Use for new frontend applications, dashboards, games, creative websites, hero sections, and visually driven UI from scratch, or when the user explicitly asks for a redesign/restyle/modernization. Builds from high-taste image-generated concept design with faithful implementation and browser testing.
---

# Frontend App Builder

Use this skill to turn a frontend application request into a working, visually checked app. For new apps, dashboards, games, websites, product interfaces, tools, redesigns, and other visually driven UI work from scratch, act first as a senior front-end designer unless the user explicitly says not to use Image Gen for concepting: create a concrete visual direction, use the installed @imagegen skill to produce an overall interface, screen, dashboard, game, website, or hero concept, then implement the concept in code as faithfully as possible. Aim for high-taste, agency-quality, minimal design rather than maximal visual spectacle, except when the product or game genre calls for richer art direction. Use additional generated assets when they materially improve the implemented UI or are needed to match the generated concept. For app interfaces, implement the main functionality with believable local state and real interactions so the user can click through the core idea instead of only viewing a static mockup. The accepted concept is an implementation contract, not a moodboard: do not redesign, simplify, rename, reorder, or substitute it unless the user explicitly asks for a change. Keep working until the running app matches the generated concept closely enough to pass a professional design-agency inspection and the core workflow has been verified, or until you hit a concrete blocker that you report clearly. Always run the app and verify the result in a browser; use the Browser plugin / built-in app browser first whenever it is available, and only fall back to Playwright with Chromium when Browser/IAB is unavailable or demonstrably unreliable for the needed check.

## Workflow

1. Read the existing app structure, scripts, styling system, and asset locations before editing.
2. Use a concept-first image generation pass for new apps, dashboards, games, websites, product interfaces, tools, redesigns, and visually described UI from scratch unless the user explicitly instructs you not to use Image Gen for concepting.
3. If the user asks to generate a concept first, review concepts, or hold implementation until approval, enter Concept Review Mode: generate and show the concept, iterate with the user until they are happy, and do not implement yet.
4. For concept-first implementation work, read and follow the installed @imagegen skill, then write a concise design-director brief and generate the overall app, dashboard, game, website, screen, redesign, or hero concept before implementation.
5. Choose one generated image as the accepted layout concept and keep its exact path visible in your notes. If multiple images were generated, label the rest as supporting assets and do not let them redefine the page structure.
6. Reject or iterate on generated concepts that are cluttered, overly decorative, under-specified, or trying to show too many product ideas at once.
7. Before coding, create a concept-to-implementation inventory from the accepted concept: native concept size/aspect, first-viewport composition, headline line breaks, nav/header geometry, brand mark, palette, type scale, panel/card topology, row counts, chart axes, drawers/rails, footer/status regions, asset roles, data/copy values, visible control states, and mobile continuation.
8. Define the minimum implementation plan, core interaction path, and asset list needed for the complete screen, page, or flow. Every visible concept element should map to code, an imagegen asset, or a clearly named intentional deviation.
9. If the accepted concept only shows part of the page or a single state, infer the remaining sections, states, and responsive views from the concept's visual language and implement them in the same design system.
10. Use the imagegen built-in tool path for missing visual assets such as logos, brand marks, hero imagery, product scenes, illustrations, textures, mockups, thumbnails, and empty-state art.
11. Treat the accepted concept as the visual spec. Extract layout, spacing, typography, palette, imagery, component shapes, interaction model, and responsive implications before coding.
12. Complete the inline preservation checklist below before coding; map every visible concept element to an implementation choice.
13. Implement the design in the app using the repo's existing framework, routing, component, styling, state, data, accessibility, and asset conventions.
14. Use imagegen again for individual project assets only to reproduce or isolate assets from the accepted concept, not to invent a new direction.
15. Add the main app functionality, thoughtful motion, and interactive visual behavior for concept elements that should feel alive, demonstrate the product, or reward exploration.
16. Run the app and use the Browser plugin / built-in app browser first for visual fidelity and interaction testing. If Browser/IAB is unavailable, cannot reach the local app, cannot capture the needed view, or produces unreliable screenshots such as broken fixed-header stitching, use Playwright with Chromium and record the fallback reason.
17. Perform an agency pass before final: compare the running UI against the accepted concept at the concept's native aspect/size when practical, a normal desktop viewport, and a mobile viewport. Name at least five concrete mismatches and fix them, or explicitly state that no material mismatches remain. Structural mismatches in topology, branding, copy, density, media behavior, or primary workflow block completion.
18. Verify the core workflow through the browser. Visible controls, media players, filters, forms, tabs, drawers, command palettes, canvas/game controls, and generated-result demos must update real local UI state; do not ship fake timecodes, inert buttons, hidden underlying media, or placeholder interactions.
19. Fix every material mismatch found during browser testing, then repeat the browser check. Keep iterating until the running app matches the concept and works as a product surface or a real blocker prevents further progress.
20. Do not send the final response or write any user-requested completion marker until the fidelity gate has passed with concrete evidence: accepted concept path, Browser/IAB verification method or Playwright fallback reason, mismatch list, fixes or blockers, and core workflow proof.
21. Before finishing, remove temporary QA-only files such as browser screenshots, fidelity reports, scratch notes, and intermediate generated assets unless the user explicitly asks to keep them or the task contract explicitly requires them. The accepted concept image may remain available for design iteration, and final assets used by the implementation must remain in the project's normal asset location.

## Imagegen Coordination

- The installed @imagegen skill is the source of truth for image generation and editing mechanics. Use its built-in tool mode by default; never choose its CLI fallback unless the user explicitly asks for CLI mode.
- Every Image Gen concept prompt for a website, landing page, dashboard, product interface, app, tool, or game UI should explicitly ask for a clean interface that embraces whitespace, uses restrained content density, and avoids clutter unless the genre or user request calls for intentional density. Do not ask Image Gen to fill the page with extra cards, stats, badges, charts, icons, HUD elements, controls, or sections unless the user explicitly requests them or the game/product needs them.
- Classify new full-page, dashboard, app, game UI, and section concepts as `ui-mockup` unless another imagegen taxonomy slug is clearly more precise. For redesigns, use `ui-mockup` when the screenshot is only a reference, or an edit slug such as `style-transfer` when the screenshot is the imagegen edit target.
- Treat initial website concepts as preview or design-reference outputs, but do not lose track of the accepted concept. For concept-first implementation, keep the accepted concept reopenable by exact path. Do not copy it into project docs or audit folders unless the user asks or the final deliverable explicitly needs that artifact.
- When multiple images are generated, explicitly separate roles: one `accepted layout concept` controls the UI structure, while later hero photos, product renders, textures, thumbnails, or illustrations are `supporting assets`. Supporting assets may fill slots in the accepted concept; they must not replace the accepted concept's layout, section order, density, palette, or first viewport.
- For assets referenced by code, follow imagegen's project-bound rule: copy or move the selected final into the project's normal public/static asset location and reference that workspace path.
- Do not create or keep a generic generated `hero.png` as a token use of ImageGen when it is not central to the rendered page. If a generated asset is not used, remove it before finishing unless it is the accepted concept image kept for user iteration.
- When converting a concept into implementation, use imagegen for all non-icon visual assets that are part of the design: logos, brand marks, hero imagery, product renders, illustrations, textures, thumbnails, posters, avatars, and empty-state art. Do not use SVGs as temporary stand-ins for those assets.
- Icons are the exception: recreate concept icons faithfully as SVG or use the repo's icon system only when it accurately matches the concept. Keep icons accessible and consistent with the implemented UI.
- Do not replace a concept's high-quality asset with a rough CSS drawing, flat gradient, generic stock-like crop, stretched raster, or placeholder SVG. If the concept depends on a map, poster wall, character, product pack, hero photo, furniture/material image, food/drink image, chart backdrop, or brand mark, use imagegen or a faithful crop/edit to supply that visual quality.
- For website-specific prompt scaffolding, use `references/imagegen-website-concepts.md`.

## Concept-First Image Generation

Use image generation before implementation for these requests unless the user explicitly opts out:

- A new app, dashboard, product interface, tool, game UI, or website from scratch with no existing visual design to work from.
- A new creative website, landing page, microsite, product page, portfolio, marketing page, or visually distinctive app surface.
- A new dashboard or operational interface where the information architecture, density, visual hierarchy, and data presentation need a first visual direction.
- A new game, simulation, or playful interactive interface where the art direction, HUD, board, scene, controls, or primary play surface needs a first visual direction.
- A redesign, refresh, restyle, or modernization of an existing website or app.
- A beautiful hero section, above-the-fold treatment, immersive first screen, or other section described mainly in visual terms.
- A recreation or adaptation of a specific UI style, visual reference, aesthetic, brand mood, or layout direction.
- A request where the visual system is under-specified and a strong concept would reduce ambiguity before coding.

Do not force concept generation for small UI fixes, routine forms, admin panels, straightforward CRUD screens, or tasks where the existing design system already dictates the answer. Do not use concept art when the user asks you to copy an existing design/codebase, extend an existing design, or implement within provided art/design constraints. If the user explicitly says not to use Image Gen for concepting, skip the concept step and work within the provided or existing design direction.

For redesigns, first capture or use the existing site/app screenshot when possible. Use that screenshot as input for the image-generation/editing pass so the concept preserves the real information architecture and improves the visual treatment instead of inventing an unrelated page.

Treat the generated concept as a design reference, not as a shippable asset. Implement the layout, spacing, color, typography, hierarchy, and interaction affordances in code. Do not ship a static screenshot of the generated page as the actual UI.

## Concept Review Mode

Use this mode only when the user explicitly asks to generate a concept ahead of time, review concept options, or wait for approval before implementation.

- Generate the concept with Image Gen and show it to the user.
- Iterate with the user on the concept until they are happy.
- Do not implement code while the user is still reviewing the concept.
- When the user approves the concept or asks you to implement it, treat that approved concept as the active spec and enter the strict Concept Fidelity workflow.
- After implementation starts, faithfully implement the approved concept to the T. Run the app and verify in the Browser plugin / built-in app browser first. Use Playwright with Chromium only when Browser/IAB is unavailable or unreliable for the needed check, and state the fallback reason. Keep iterating before completion until the running UI matches the approved concept or a concrete blocker is reported.

## Concept Fidelity

- Once a concept is accepted, follow it closely enough to pass inspection from the designer who created it. The implementation should be a faithful coded version of the generated design, not a loose reinterpretation or a simpler page inspired by it.
- If you generated a concept because the user asked or because this skill required concept-first work, you must adhere to what was designed. Treat that concept as the active spec until the user changes it.
- Persistence is mandatory. Do not stop at a partial implementation, a first draft, a build that merely compiles, or a page that only captures the general vibe. Continue implementing, comparing, and refining until the browser-rendered UI matches the concept's actual structure, visual details, and expected interaction model.
- Preserve the concept's visible content and information architecture by default: headline text, emphasized words, navigation items, CTA labels, proof points, section titles, section order, brand mark, first-viewport composition, and the next-section preview.
- If the concept does not contain the full contents of the requested page, continue the rest of the page in the same design language: same spacing rhythm, type scale, palette, imagery style, component geometry, and interaction model. The hidden or downstream parts should feel designed by the same system, not appended from a generic template.
- Preserve the concept's mock state unless the user asks for live data. Clone-like and product surfaces often need designed sample repositories, issues, videos, incidents, events, rows, files, and copy; replacing those with live API output or generic filler can make the implementation less faithful.
- Do not replace the concept with a brand-first, simplified, darker, heavier, or otherwise reinterpreted version because it seems easier to implement. If a change seems necessary, call it out as a deviation and minimize it.
- Before coding, translate the concept into a concrete implementation checklist: grid structure, section order, alignment, whitespace, type scale, font personality, color tokens, borders, radii, shadows, image crops, button treatments, visual effects, motion opportunities, and key responsive behavior.
- Recreate visual assets from the concept when needed. If a logo, brand mark, hero image, product mockup, texture, cutout, poster, avatar, or illustration is central to the concept, use imagegen to create that asset as accurately as possible, then store the selected final in the project asset path.
- Do not generate a second unrelated hero or product image that competes with or replaces the accepted concept. Additional imagegen work must be constrained to matching the concept's subject, composition, crop, lighting, palette, and role in the layout.
- Do not use "code-native" as an excuse to drop visual structure. Code-native implementation means recreating the concept with HTML/CSS/components where appropriate; it does not permit deleting dashboards, sidebars, tables, drawers, workflow diagrams, HUDs, media rails, illustration style, or first-viewport density.
- Usability and responsive fixes must preserve the concept's information architecture. Tune spacing, wrapping, typography, and overflow before replacing tables with cards, removing columns, switching dark to light, moving key modules below the fold, or changing the primary interaction model.
- Keep code-native UI code-native. Text, navigation, buttons, forms, cards, layout, and controls should be implemented in HTML/CSS/components, while raster assets supply imagery that cannot be cleanly built in code.
- Use browser inspection or screenshots as the fidelity check. Compare the running implementation against the concept for composition, hierarchy, spacing, typography, color, asset framing, and visible interaction states.
- No silent fidelity pass is acceptable. After browser verification, name the material mismatches you see. If there are no material mismatches, state that explicitly with the concept path and verification method. If exact fidelity is impossible because of accessibility, responsiveness, missing assets, or framework constraints, preserve the design intent, minimize the deviation, and state the exact blocker. Do not present an avoidable mismatch as complete.
- Do not leave fidelity reports, screenshots, comparison images, or other QA-only artifacts in the final workspace unless the user or benchmark explicitly requires them. If temporary screenshots were written during verification, remove them before handoff.

## Mandatory Preservation Checklist

Before coding a concept-first build, extract and preserve:

- Exact visible copy: headline, highlighted words, eyebrow, body copy, labels, CTA text, proof points, section headings, and important UI labels.
- Navigation and actions: all nav items, dropdown indicators, login/sign-in links, primary and secondary CTAs, and their relative placement.
- Brand system: logo shape, wordmark treatment, accent colors, icon style, visual motif, and any distinctive brand mark.
- First viewport: hero layout, primary visual composition, text block location, CTA group, proof points, hero asset framing, background treatment, and whether the next section is visible.
- Section structure: section order, section count, light/dark transitions, cards, dashboards, feature rows, demo panels, and footer/status elements visible in the concept.
- Continuation plan: if the concept stops before the requested full page or flow is complete, list the downstream sections, states, and responsive surfaces you will add in the same design language.
- Visual system: typography style, type scale, spacing density, radius, borders, shadows, texture, color mood, contrast, and overall weight.
- Product visuals: dashboards, cards, charts, maps, nodes, device frames, topology scenes, 3D objects, or other visual artifacts that need assets, code-native UI, animation, or simulated interaction.
- Functional surface: the primary user journey, controls that must respond, state changes the user should see, and any real underlying media/data that must not be faked.
- Responsive intent: what must remain visually recognizable on desktop and mobile.

Before finishing a concept-first build, compare the concept and running browser-rendered UI side by side, using transient screenshots when that is the clearest way to inspect. Do not claim fidelity until these match materially: copy and emphasis, nav and CTA labels, brand mark, hero composition, first-viewport balance, next-section visibility, section order, section types, proof points, product/demo elements, palette, typography, spacing, borders, radii, visual weight, motion, and simulated interactions. If they do not match, keep working: adjust code, regenerate or crop assets, tune spacing and typography, rerun the app, and compare again.

## Fidelity Gates By Surface

- Landing pages and company sites: preserve the accepted concept's first viewport, hero image role, brand/nav/CTA labels, section order, next-section preview, and any signature physical objects or photography. If the concept does not show the entire page, build the remaining sections in the same visual system without altering the above-the-fold composition.
- SaaS product pages and branded product websites: preserve the product mockup inventory, workflow diagram, feature strip, trust/proof elements, exact brand treatment, and first-viewport balance. Do not replace a diagram or dense product mockup with a generic floating card because it is easier to code.
- Operational dashboards and app interfaces: preserve density, panel topology, sidebars, headers, tables, drawers, tabs, timelines, charts, maps, columns, row counts, and dark/light palette. Implement the main workflow with clickable controls, local state changes, selection/detail behavior, filters, modes, or edits as appropriate. A dashboard concept that is table-driven must not become a card grid unless the concept already shows cards.
- Timeline, planner, scheduling, and ops tools: preserve the grid/time-axis anatomy, row spans, event density, status rails, active service/shift selectors, and first-viewport command-center fit. Do not push the main operational surface below the fold when the concept shows it immediately.
- Clone-like interfaces: preserve the recognizable skeleton before adding polish. For GitHub-like, Linear-like, YouTube-like, or similar requests, do not add marketing heroes, oversized stat cards, or custom navigation that make the result stop reading as the requested product type.
- Games and playful tools: preserve the art direction, world materials, character/sprite treatment, HUD framing, primary play surface, controls, and reward/hazard visuals. If CSS shapes cannot match the concept's illustration quality, generate or crop game assets that do.
- Games must pass a playability gate, not just a screenshot gate: scripted keyboard/pointer interaction should verify movement, jump/drag/action behavior, scoring, hazards, restart, and that collision geometry aligns with visible art.
- Media and image-heavy surfaces: preserve the player/poster/thumbnail proportions, right-rail or gallery density, photographic versus illustrated treatment, and primary media asset role. Do not replace a photographic or illustrated concept with a generic SVG poster.
- Media players must operate on the real required media. Do not hide a required video/audio element behind generated overlays except as an initial poster; verify visible media opacity, load state, real duration, play/pause, seek/progress, and that the displayed frame changes.
- Form, booking, purchase, and restaurant surfaces: verify the main transaction path such as reservation, order, inquiry, booking, add item, or save state, including success/confirmation state.
- Product/SaaS mockups: preserve the product mockup inventory: sidebars, inboxes, tables, composer panels, right rails, device frames, workflow diagrams, chips, badges, and status rows. Fix clipping/overflow before final.

## Motion And Interaction

- Add motion with the same taste level as the static design: purposeful, polished, and restrained. Use animation to clarify hierarchy, reveal state, direct attention, or make the product feel tangible.
- If the concept includes visual product elements such as dashboards, canvases, timelines, maps, 3D objects, device frames, charts, cards, nodes, or process flows, make the important ones interactive when feasible. A convincing simulated interaction with local state is better than a static prop when it helps explain the product.
- For app interfaces, implement the main user journey rather than only hover polish. Examples include creating or editing an item, switching modes, filtering data, selecting rows to reveal details, dragging or toggling controls, stepping through a workflow, or simulating a generated result with believable local state.
- Prefer subtle page-load choreography, hover/focus states, scroll-linked reveals, animated product previews, live counters, draggable/toggleable controls, or stateful demo panels over decorative motion that does not support the interface.
- Match the motion to the concept's visual language. A calm editorial site should have quiet easing and small transitions; a product demo can have richer animated state changes when they reveal capability.
- Keep interactions accessible: preserve keyboard/focus states, avoid motion that blocks reading, respect `prefers-reduced-motion`, and make sure animation does not cause layout shift or text overlap.
- Treat screenshot timing as part of fidelity. Browser evidence should capture stable UI states: wait for entrance animations to settle, avoid first-load opacity that makes key assets look washed out, eager-load local images needed in screenshots, and disable or bypass nonessential load transforms when they distort comparison.
- Verify motion in the browser, not just in code. Interact with the elements, check timing and polish, and adjust until the behavior feels like a designed part of the concept.

## UI Quality Principles

- Great interfaces start with a clear job. Make the primary user goal obvious, reduce competing choices, and keep the visual hierarchy focused on what the user should understand or do next.
- Whitespace is a design material. Use it to create hierarchy, calm, scanability, and confidence. Do not fill empty areas with decorative cards, icons, stats, labels, or filler copy.
- Content density should be intentional. Default to fewer, stronger messages and components; add density only when the product surface genuinely requires comparison, monitoring, or repeated operational use.
- Strong landing pages make the offer legible in the first viewport: clear headline, supporting copy, one primary action, one optional secondary action, and a concrete product or brand signal. Show proof only where it reinforces trust without stealing focus.
- Great product interfaces feel useful, not decorative. Prioritize real workflows, clear affordances, meaningful states, readable data, responsive controls, and helpful empty/loading/error states.
- Use progressive disclosure. Put advanced details, secondary proof, and supporting features after the primary story or behind interactions instead of cramming everything above the fold.
- Good visual systems are coherent: consistent spacing, type scale, radius, border, shadow, icon treatment, and color roles. Use contrast and accent color sparingly to guide attention.
- UI imagery should clarify the product, customer, workflow, or atmosphere. Avoid generic visual noise and avoid images that look impressive but do not explain or support the page.
- For apps and product demos, make the interface feel live with believable sample data and lightweight interaction, but keep it subordinate to the core task and design hierarchy.
- Respect accessibility and usability as part of taste: readable text, sufficient contrast, clear focus states, target sizes, responsive layout, and reduced-motion support.

## Taste Bar

- Default to restraint. The concept should look like it came from a strong digital product agency: confident hierarchy, generous whitespace, a small number of excellent elements, and no filler.
- Prefer one clear focal idea per viewport. A refined hero with one strong composition is better than multiple competing dashboards, floating panels, stats strips, icon rows, and feature grids.
- Use a restrained palette with one or two meaningful accents. Avoid neon overload, glowing sci-fi interfaces, bokeh/orb decoration, dense grids, and dark cyberpunk dashboards unless the user explicitly asks for that style.
- Keep information density appropriate to the product. SaaS and operational tools can be dense, but still need quiet structure, clear grouping, and breathing room.
- Use typography as a primary design tool: elegant readable sans-serif, occasional editorial serif, or crisp mono accents. Avoid novelty type, excessive all-caps labels, and oversized decorative text treatments.
- If the generated concept looks busy, iterate before coding with a simplification prompt: reduce decorative elements, remove unnecessary cards and badges, calm the palette, clarify the hierarchy, and keep only the elements that support the user's goal.

## Design Direction

- Think like a highly skilled front-end web designer giving a clear brief to another designer: define the page purpose, audience, hierarchy, visual mood, layout system, color palette, typography direction, imagery needs, and interaction feel.
- Follow the user's requested style and content priorities, but keep the UI clean and intentional. Avoid extra cards, badges, stats, icons, illustrations, decorative elements, and secondary sections unless they serve the user's goal.
- Prefer elegant, common-but-creative typography choices: refined sans-serif pairings, editorial serif accents, crisp mono details, or expressive display type only when it fits the product. Keep type readable and avoid novelty fonts.
- Use generated concepts to explore the whole composition first. Generate individual assets afterward only when the implementation needs specific logos, brand marks, hero imagery, product renders, textures, illustrations, thumbnails, or empty-state art.
- Keep UI text, labels, navigation, metrics, and controls in code rather than baked into generated images.
- Use concept output to extract implementable decisions: layout grid, spacing rhythm, color tokens, type scale, image treatment, component shapes, and motion/interaction cues.

## Asset Design

- Use existing brand or product assets when the user has provided them; otherwise use built-in Codex image generation instead of placeholder gradients, generic SVG decoration, or empty gray boxes.
- Prompt generated concepts and assets with concrete subject, page purpose, style, composition, aspect ratio, background needs, typography direction, density, and intended UI placement.
- Keep UI text, labels, numbers, and controls in code rather than baked into generated images.
- Store generated or edited assets in the project's normal public/static asset location and reference them through the app's existing asset pipeline.
- Prefer assets that reveal the actual product, use case, state, or atmosphere the interface needs to communicate.
- Use imagegen for logos and brand marks unless the user provides an existing vector logo. SVGs are acceptable for icons only, and those icons must faithfully match the concept rather than acting as generic placeholders.

## Implementation

- Build the real usable surface first, not a marketing wrapper around a future app.
- Match existing conventions for components, tokens, spacing, routing, state, loading, errors, and empty states.
- Keep implementation quality production-oriented: use semantic markup, accessible controls, typed data structures where the repo supports them, component boundaries that match the existing app, no duplicated one-off logic when a local helper exists, and no hardcoded layout hacks that will collapse under normal responsive or content changes.
- Preserve the accepted concept's visual hierarchy and proportions when mapping it into the repo's component system.
- Implement visible concept elements as working UI whenever practical. If an element looks like a product surface, demo, control, chart, or visualization, give it believable state, hover/focus behavior, or lightweight interaction rather than leaving it as inert decoration.
- For app interfaces, make the primary workflow experiential. The user should be able to click through the main idea, see state update, and understand how the app would work even if the data is local and simulated.
- Keep layouts responsive with stable dimensions for images, toolbars, grids, cards, and controls so generated assets do not cause shifting or overlap.
- Make the generated assets serve the interface: crop, mask, size, and lazy-load them intentionally instead of dropping them in at arbitrary dimensions.
- Supplement implementation with type checks, linting, and unit tests when the repo already uses them.

## Browser Testing

- Always run the app and verify concept-first work in a browser. Use the Browser plugin and built-in app browser when available.
- Use the Browser plugin / built-in app browser as the default verification surface for localhost apps. Load the page, inspect the first viewport, scroll, click through the main workflow, and use screenshots only as needed.
- Fall back to Playwright with Chromium only when Browser/IAB is unavailable, cannot access the page, cannot perform the interaction, or produces unreliable captures. State the fallback reason. Prefer harness-level browser tools or the Playwright CLI; do not assume a project-local Playwright package exists, and avoid fragile shell-quoted `node -e` verification scripts.
- If IAB screenshot capture stitches fixed headers incorrectly, times out, or cannot capture the needed viewport, continue Browser/IAB interaction checks but use Playwright Chromium for the screenshot comparison.
- Check at least one desktop viewport and one mobile-sized viewport when the UI is user-facing.
- For concept-first work, inspect the browser-rendered UI and use screenshots when helpful to compare it against the generated concept before finishing. Include the concept's native aspect/size when practical, plus desktop and mobile. Completion requires a side-by-side fidelity pass, not just build success, responsiveness, image loading, or interaction checks.
- Treat the first browser comparison as the start of the fidelity loop, not the finish line. Record the visible mismatches, fix them, and repeat browser verification until the page is correct.
- Verify exact preservation of concept content: headline, emphasized text, nav, CTAs, section order, proof points, brand mark, primary hero composition, next-section presence, color mood, and typography.
- For product UIs, dashboards, clones, games, and media surfaces, verify the surface-specific gates above in the browser-rendered UI. Do not substitute a generic "looks polished" judgment for a concept-structure check.
- Confirm generated assets load, are framed correctly, and do not obscure text or controls.
- Verify primary actions, navigation, hover/focus states, motion timing, interactive demos, responsive wrapping, and obvious loading or error states.
- Verify the core app workflow by clicking through it. Do not treat an interface as complete if the main controls are visually present but inert.
- If no browser verification path is available, state that as a blocker and do not claim the concept was implemented faithfully.
- In the final response, include the accepted concept path, Browser/IAB verification method or Playwright fallback reason, the material mismatches fixed, the core interaction path verified, and any remaining intentional deviations. If screenshots or reports were created only for QA, remove them before the final response unless the user explicitly asked to keep them or the benchmark contract requires them.
