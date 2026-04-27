# Imagegen Interface Concept Briefing Guidance

Use this reference with the installed @imagegen skill when Frontend App Builder needs an overall visual concept. This is guidance, not a prompt template. Write a natural design-director brief tailored to the task.

## Must Include

Copy concrete details from the user request, screenshots, existing app, or plan. Do not reduce them to a generic category like "modern landing page" or "clean dashboard."

- Scope: complete page, complete app screen, multi-state product surface, dashboard, game screen, or coordinated section/state concepts.
- Purpose and audience: what the page/product helps the user do, and who it is for.
- Exact visible content: headlines, labels, CTAs, section names, nav items, table fields, sample entities, dates, prices, statuses, media requirements, and required copy. After a concept is accepted, this becomes the visible-copy lock.
- Structure: first viewport composition, downstream section order, sidebars, rails, drawers, grids, tables, charts, media areas, forms, footer/status regions, and responsive continuation.
- Interaction model: selected state, hover/focus affordances, filters, tabs, mode switches, creation/editing flow, success state, playback state, game HUD, or other local-state behavior the implementation must support.
- Visual system: palette mood, typography personality, content text scale, UI chrome/control text scale, density, spacing rhythm, radii, shadows, borders, container model, card usage, icon style, image treatment, brand mark direction, and reference style.
- Implementation constraints: code-native app UI text and controls, fully rendered product/background assets with their own text and branding when appropriate, separable assets, reusable component families, clear design-system tokens, accessible/responsive layout, and practical production design-spec handoff.
- Negative constraints: no header-only crops for full-surface work, no extra product areas, no fake metrics, no decorative filler, no default card grids, no hero eyebrow/kicker/pretitle/badge/pill above the main heading unless explicitly requested or present in the reference, no gradients that conflict with the design direction, no pasted-in images that fail to blend with the background, no unrelated sections, no new claims, and no moving true app UI text into images.

## Quality Bar

Every concept should feel like a professional product mockup by a senior product designer:

- Clean, airy, distinctive, and not repetitive by default.
- One clear creative idea or visual point of view.
- Full requested surface, not just a hero, unless the user only asked for a hero.
- Strong first viewport with clear offer, product signal, and primary action.
- Coherent full-page rhythm across sections, states, and responsive continuation, without repetitive card stacks or repeated section formulas.
- Excellent typography and intentional whitespace, including buttons, tabs, inputs, sidebars, table cells, labels, and other control chrome.
- Consistent visual system: palette, gradients, spacing, components, icon style, imagery, shadows, borders, and container model.
- Clear design-system signal: typography scale, control text styles, reusable component families, variants, spacing rhythm, and tokens that can be extracted before coding.
- High-quality assets for logos, brand marks, hero imagery, product renders, background scenes, illustrations, textures, thumbnails, posters, avatars, or empty states. Product/background assets should be fully rendered with consistent branding and in-image text when that text belongs to the asset.
- Purposeful motion/interaction cues that can be implemented later.
- Specific, non-generic copy when the user has not supplied exact copy.

Default to roughly 7/10 creativity: distinctive and art-directed, but still implementable. "Clean" means airy, edited, legible, not cluttered, and not repetitive.

Avoid: unnecessary cards, hero eyebrow/kicker labels, pills, badges, stats, icon rows, fake charts, fake metrics, fake jargon, generic brand names, bokeh/orb decoration, neon grids, excessive glow, mismatched gradients, pasted-looking images, unreadable text, and filling whitespace just because it exists.

## Surface Guidance

Full page or app:

- Ask for enough structure to implement the whole requested surface: first viewport, section rhythm, product/workflow anatomy, downstream sections or states, and responsive continuation.
- Marketing/product pages need a strong hero and clear CTA before proof or feature density. Do not put an eyebrow, kicker, pretitle, badge, or pill above the hero heading unless the user asked for it or the reference already uses it. Use interactive hero UI only for SaaS/software previews, product demos, or purposeful interactive animation; otherwise prefer faithful branded product/background imagery.
- App screens, dashboards, and tools need the real interaction model: sidebars, panels, tables, timelines, charts, controls, modes, selected states, and primary workflow.
- Games need the play surface, HUD/control placement, art direction, reward/hazard language, interaction affordances, and a follow-on production asset pass for sprites, tiles/platforms, collectibles, hazards, goals, props, and background/parallax layers.

Redesign from screenshot:

- Use the screenshot as the edit target when preserving information architecture matters.
- Preserve navigation meaning, product/brand cues, content hierarchy, controls, and page purpose.
- Improve spacing, typography, visual hierarchy, color, image treatment, and component polish without inventing unrelated sections, fake metrics, new claims, or new product areas.

Hero or section:

- Only use this path when the user asks for a section, hero, pricing block, feature section, or other page slice.
- Include surrounding context and enough visual language to continue the page consistently.

Content-heavy pages:

- If one image would cram the design, generate coordinated section or state concepts.
- Keep one accepted layout concept responsible for overall structure.
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
- Extract a design system before coding: native aspect, layout, section order, copy, nav, CTAs, palette, spacing scale, content typography, UI chrome typography, reusable component families, variants, container model, assets, state, and responsive continuation.
- Treat the accepted concept as the visual spec. Match composition, hierarchy, palette, gradients, typography, spacing, imagery, components, container model, and asset treatment. Do not strip text or branding out of generated product/background assets just because app UI text should stay code-native.
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
