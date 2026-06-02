# Imagegen Interface Concept Briefing Guidance

Use this reference with the installed @imagegen skill when Frontend App Builder needs an overall visual concept. This is guidance, not a prompt template. Write a natural design-director brief tailored to the task.

## Must Include

Copy concrete details from the user request, screenshots, existing app, or plan. Do not reduce them to a generic category like "modern landing page" or "clean dashboard."

- Scope: complete page, complete app screen, multi-state product surface, dashboard, game screen, or coordinated section/state concepts. For multi-section pages, name the section set and ask for a large readable concept screenshot for each major section.
- Purpose and audience: what the page/product helps the user do, and who it is for.
- Exact visible content: headlines, labels, CTAs, section names, nav items, table fields, sample entities, dates, prices, statuses, media requirements, and required copy. After a concept is accepted, this becomes the visible-copy lock.
- Structure: first viewport composition, downstream section order, sidebars, rails, drawers, grids, tables, charts, media areas, forms, footer/status regions, and responsive continuation.
- Interaction model: selected state, hover/focus affordances, filters, tabs, mode switches, creation/editing flow, success state, playback state, game HUD, or other local-state behavior the implementation must support.
- Visual system: palette mood, typography personality, content text scale, UI chrome/control text scale, density, spacing rhythm, radii, shadows, borders, container model, card usage, icon style, image treatment, brand mark direction, and reference style.
- Implementation constraints: code-native app UI text and controls, fully rendered product/background assets with their own text and branding when appropriate, separable assets, reusable component families, clear design-system tokens, accessible/responsive layout, and practical production design-spec handoff. For complex dashboards, tools, editors, or multi-panel product surfaces, assume a React + Vite implementation unless the user or repo specifies otherwise, with a component structure a strong front-end engineer would recognize.
- Negative constraints: no header-only crops for full-surface work, no extra product areas, no fake metrics, no decorative filler, no default card grids, no hero eyebrow/kicker/pretitle/badge/pill above the main heading unless explicitly requested or present in the reference, no gradients that conflict with the design direction, no pasted-in images that fail to blend with the background, no unrelated sections, no new claims, and no moving true app UI text into images.

## Quality Bar

Every concept should feel like a professional product mockup by a senior product designer:

- Clean, airy, distinctive, and not repetitive by default.
- One clear creative idea or visual point of view.
- Full requested surface, not just a hero, unless the user only asked for a hero.
- Strong first viewport with clear offer, product signal, and primary action.
- Coherent full-page rhythm across sections, states, and responsive continuation, without repetitive card stacks or repeated section formulas.
- Cohesive section-to-section flow: connect sections with shared spacing, palette, type rhythm, media treatment, and subtle transitions, not by inventing major new UI components.
- Excellent typography and intentional whitespace, including buttons, tabs, inputs, sidebars, table cells, labels, and other control chrome.
- Simpler by default: fewer, stronger visual elements instead of filling the page with illustrations, iconography, decorative widgets, or complex UI chrome.
- Consistent visual system: palette, gradients, spacing, components, icon style, imagery, shadows, borders, and container model.
- Icon fidelity matters when icons are present: preserve metaphor, stroke weight, filled vs outline style, corner shape, size, color, alignment, spacing, and states.
- Color fidelity is mandatory: the implementation must match the generated design's actual background, surface, text, border, shadow, and accent colors. If the concept uses a white background, it must stay white, not cream, ivory, beige, warm gray, or softened off-white.
- Hero media treatment must be preserved. If the hero image has no color overlay or tint in the concept, do not add one in implementation. Edge fades, masks, or background gradients may blend image edges into the page, but they must not wash the image with a color overlay.
- Clear design-system signal: typography scale, control text styles, reusable component families, variants, spacing rhythm, and tokens that can be extracted before coding.
- High-quality assets for logos, brand marks, hero imagery, product renders, background scenes, illustrations, textures, thumbnails, posters, avatars, or empty states. Product/background assets should be fully rendered with consistent branding and in-image text when that text belongs to the asset.
- Purposeful motion/interaction cues that can be implemented later.
- Specific, non-generic copy when the user has not supplied exact copy.

Default to roughly 7/10 creativity: distinctive and art-directed, but still implementable. "Clean" means airy, edited, legible, not cluttered, and not repetitive.

Avoid: unnecessary cards, hero eyebrow/kicker labels, pills, badges, stats, icon rows, excessive illustrations, decorative iconography, overcomplicated header UI, fake charts, fake metrics, fake jargon, generic brand names, bokeh/orb decoration, neon grids, excessive glow, mismatched gradients, pasted-looking images, unreadable text, and filling whitespace just because it exists.

## Visual Direction Defaults

Before writing the Image Gen brief, choose a compact visual direction that fits the product and audience. Do not expose this as a rigid template; use it to make the brief more specific.

- Baseline settings: roughly 7/10 creativity, low-to-medium visual density, generous spacing, high implementation clarity, strong typography discipline, and image-led moments when real visuals improve the page.
- Choose one theme paradigm, one background character, one typography character, one hero or primary-screen architecture, one section rhythm, 2-4 signature component motifs, and 1-2 motion cues. Keep every generated section/state/detail concept inside that same design world.
- For heroes and first viewports, ask for one clear focal point, a short headline or primary task, restrained supporting copy, a visible primary CTA or control, and enough breathing room for a small laptop viewport. Avoid stuffing the first screen with proof chips, badges, fake stats, or multiple competing panels.
- Default headers should stay quiet: brand mark, essential navigation, and one primary action or control. Avoid icon-heavy nav, extra buttons, search bars, status widgets, segmented controls, decorative illustrations, or dense product chrome in the header unless explicitly requested or required by the workflow.
- Prefer one or two high-quality image or illustration moments over many small decorative visuals. Use iconography only when it clarifies navigation, controls, or product meaning.
- Prefer open layouts, strong bands, rails, lists, tables, canvases, and purposeful single frames over nested cards, giant rounded section wrappers, default bento grids, or overcompartmentalized dashboards.
- Long pages should vary rhythm across sections: density, image-to-text ratio, alignment, scale, whitespace, and visual tempo should change deliberately while preserving one palette, typography system, component family, and spacing logic.
- Multi-section pages should feel like one cohesive website through shared gutters, background bands, alignment, typography rhythm, recurring media frames, color cadence, and restrained transitions. Do not add major new carousels, accordions, pricing cards, dashboards, forms, tab systems, feature grids, or other component families unless the user requested them or the accepted concepts show them.
- Ask for media and generated imagery in implementation-friendly frames: stable aspect ratios, consistent crop/radius/shadow logic, and clear placement in the layout. Avoid random image sizes, pasted-looking crops, or uncontrolled collage systems unless the user requests that style.
- UI restraints: small labels, utility pills, pseudo-system markers, fake metrics, and decorative dashboard jargon should appear only when they communicate real structure or product meaning.

## Image Count And Clarity

Inside Codex, readability and extraction quality outrank compact presentation.

- For a 1-section request, generate 1 primary section concept. For 2-10 requested or implied sections, default to 2-10 coordinated primary section concepts, one fresh image per major section, when that improves readability.
- Use an optional full-page overview only for overall rhythm, section order, and transition logic. Do not treat the overview as the only implementation spec if it compresses text, buttons, cards, or spacing.
- Generate extra extraction-oriented detail concepts when a section's text, button style, card anatomy, pricing/testimonial details, typography, palette, image treatment, or spacing is not clearly readable.
- For dashboards, tools, editors, and dense app screens, generate the full primary screen plus focused state/detail concepts for dense areas such as sidebars, tables, inspector panels, modals, charts, toolbars, forms, and selected states.
- Never crop, slice, zoom, or reuse part of an older full-page image as the main section/detail reference. Ask Image Gen for a fresh standalone section or detail image that keeps the same palette, typography mood, component family, density, asset treatment, and brand world.
- Do not reduce image count for convenience when doing so makes the later implementation rely on guesswork.

## Surface Guidance

Full page or app:

- Ask for enough structure to implement the whole requested surface: first viewport, section rhythm, product/workflow anatomy, downstream sections or states, and responsive continuation.
- Marketing/product pages need a strong hero and clear CTA before proof or feature density. Do not put an eyebrow, kicker, pretitle, badge, or pill above the hero heading unless the user asked for it or the reference already uses it. Use interactive hero UI only for SaaS/software previews, product demos, or purposeful interactive animation; otherwise prefer faithful branded product/background imagery.
- App screens, dashboards, and tools need the real interaction model: sidebars, panels, tables, timelines, charts, controls, modes, selected states, and primary workflow.
- For complex app screens, dashboards, editors, and tools, make the generated concept clear enough to break into a real component architecture: app shell, navigation, major feature regions, reusable controls, table/chart/form modules, sample data/state boundaries, and responsive layout behavior. Do not design a surface that can only be implemented as one giant static component.
- Games need the play surface, HUD/control placement, art direction, reward/hazard language, interaction affordances, and a follow-on production asset pass for sprites, tiles/platforms, collectibles, hazards, goals, props, and background/parallax layers.

Redesign from screenshot:

- Use the screenshot as the edit target when preserving information architecture matters.
- Preserve navigation meaning, product/brand cues, content hierarchy, controls, and page purpose.
- Improve spacing, typography, visual hierarchy, color, image treatment, and component polish without inventing unrelated sections, fake metrics, new claims, or new product areas.

Hero or section:

- Only use this path when the user asks for a section, hero, pricing block, feature section, or other page slice.
- Include surrounding context and enough visual language to continue the page consistently.

Content-heavy pages:

- For multi-section websites and long landing pages, default to coordinated section concepts: one fresh, large, readable image per major section, with an optional overview only for full-page rhythm.
- Avoid one huge full-page screenshot when it would reduce section detail, make text/buttons/cards too small, weaken hierarchy, or make implementation matching harder.
- Keep one accepted layout concept responsible for overall structure and section order.
- All supporting concepts must share brand language, typography, palette, component geometry, asset style, spacing, and density.

## Asset Planning

- Keep real app UI text, form fields, nav, metrics, and controls in code.
- Product images, background assets, posters, packaging, signage, hero photos, and brand scenes should be rendered completely by Image Gen with the text, logos, marks, labels, and branding that belong in the asset. Quote exact asset text and require verbatim rendering when text matters.
- If the concept includes a logo, brand mark, product label, package, poster, sign, product render, or branded background object, use Image Gen editing to create standalone matching assets before coding so the implementation keeps coherent branding.
- Request transparent backgrounds or clean cutouts when assets need to layer into code-native UI.
- For games, generate transparent character/state sprites or sprite sheets, terrain/platform tiles, collectibles, hazards, goal/checkpoint objects, props, and 2-3 parallax/background layers when the concept calls for depth. Keep HUD text, score, controls, collision boxes, physics, and game state code-native.
- Use generated assets for logos, brand marks, hero imagery, product renders, editorial imagery, background scenes, cutouts, textures, posters, thumbnails, avatars, empty-state art, and illustrated objects.
- Do not crop a full-page concept into production UI as a shortcut. Recreate or isolate needed assets with Image Gen.
- SVG is fine for faithful icons. Use Image Gen for logos, brand marks, and non-icon visual assets.
- Supporting asset concepts must match the accepted layout concept; they must not introduce a new visual direction.

## After Generation

- Reject concepts that are header-only for full-surface asks, cluttered, generic, repetitive, under-specified, unreadable, over-decorated, or impractical to implement.
- For every generated section/state/detail image, extract the section purpose, visual priority, readable text, typography relationships, spacing, button/control styling, component/container logic, colors, image treatment, and unclear details.
- Extract an icon inventory before coding: every visible icon, glyph, chevron, logo-like mark, toolbar symbol, status symbol, and empty-state symbol, including meaning, outline vs filled style, stroke width, size, color, container, alignment, spacing, and state treatment.
- If any required detail is still unclear, generate a new standalone section/state/detail image before coding. Do not crop the previous image as a shortcut.
- Extract a design system before coding: native aspect, layout, section order, copy, nav, CTAs, palette, spacing scale, content typography, UI chrome typography, reusable component families, variants, container model, assets, state, and responsive continuation. Explicitly identify whether each background is true white, off-white, cream, gray, dark, or tinted.
- Treat the accepted concept as the visual spec. Match composition, hierarchy, palette, gradients, typography, spacing, imagery, components, container model, and asset treatment. Do not strip text or branding out of generated product/background assets just because app UI text should stay code-native.
- Do not reinterpret the palette for taste. Do not replace white backgrounds with cream/off-white, warm up neutral backgrounds, cool down surfaces, or shift accent colors unless the accepted concept visibly does that.
- Do not add a color overlay, tint, or translucent wash over a hero image unless the accepted concept clearly has one. If a hero image needs help blending into the surrounding page, prefer a matching generated asset, transparent cutout, edge fade, mask, or background gradient around the image instead of an overlay on top of the image.
- Do not substitute generic nearby icons for the accepted design's icons. Use the repo's existing icon set or lucide only when it matches the concept; otherwise create a small custom SVG/icon variant that preserves the icon metaphor, fill/stroke style, optical weight, size, color, alignment, and state behavior. Custom SVG icons must be production-quality vector assets with a clear `viewBox`, clean geometry, consistent stroke widths, aligned joins/caps, balanced negative space, optical centering, scalable paths, no jagged or placeholder-looking shapes, and `currentColor` or explicit fills only when they match the design system.
- For multi-section pages, implement and verify one section or contiguous viewport at a time. Compare the browser screenshot to that section's concept, fix visible drift, then move to the next section. Use the relevant section image as evidence, not only the overview.
- When stitching section concepts together, use existing design-system continuity instead of inventing major new UI. New component families are allowed only when present in the accepted concept, requested by the user, or needed for a concrete functional requirement that is recorded as an intentional deviation.
- Build an allowed above-the-fold copy list from the accepted concept and user-provided copy. Do not add new hero, nav, eyebrow/kicker, CTA, label, subtitle, category, or proof text unless it is recorded as an intentional deviation. Semantic H1 or heading-level changes must not invent visible explanatory copy.
- Do not add decorative hero eyebrows, pills, badges, gradients, or overlays that were not in the accepted design. Images must blend with the surrounding background through matching color, lighting, crop, transparency, edges, and shadow.
- Do not add UI that does not exist in the design. Generate missing section/state concepts when visual consistency is uncertain.
- For games, do not replace the accepted art direction with code-drawn placeholder shapes for characters, terrain, collectibles, hazards, goals, or backgrounds. Use Image Gen assets unless a concrete blocker or approved deviation is recorded.
- Preserve the accepted container model. Do not add cards, floating panels, bordered tiles, or card grids where the spec uses open layout, bands, lists, tables, rails, canvases, or full-bleed composition.
- Use Browser/IAB first for verification; use Playwright Chromium only when Browser/IAB is unavailable or unreliable.
- Before final handoff, use `view_image` on the accepted concept and latest browser screenshot in the same QA pass. This cannot be skipped or replaced with browser inspection or functional testing alone.
- Capture the implementation at the accepted concept's native dimensions when practical; otherwise record the blocker and also verify the current browser viewport.
- Write a fidelity ledger before final: mismatch, concept evidence, render evidence, and fix made or reason not fixed. Inspect at least five concrete comparison points before claiming fidelity.
- Judge whether the implementation is agency-signoff faithful and whether a great, highly skilled design agency would sign off on it; include type-scale drift and default-looking control text in that judgment. If not, keep iterating until it would sign off or a concrete blocker remains.
- Remove temporary QA screenshots, reports, scratch notes, and unused generated assets unless the task requires keeping them.
