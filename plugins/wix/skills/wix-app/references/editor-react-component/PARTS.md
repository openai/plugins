# What Qualifies as a Part

A **named part** is an element that a site owner would plausibly want to control independently in the editor. Zero config scans global class names and creates an editor element for each one. Each editor element can surface:

- **CSS properties** — styling controls (fill, typography, border, etc.)
- **Data** — content bindings (text, image, link, etc.)

An element deserves its own named part if a site owner would plausibly need to independently control either its styling **or** its data/content through the editor. Every named part gets exactly one global plain string class in JSX and one corresponding CSS rule. Elements that do not qualify should not get a global class.

## Mandatory filter — apply to every candidate element

- ❌ **State or variant** (`active`, `selected`, `current`, `disabled`, `open`, `checked`) — not a part. Implement as a BEM modifier class toggled in JSX (e.g. `image-carousel__slide--active`) and a single-class CSS rule. The modifier class is CSS-only; it is not a named part.
- ❌ **Hidden/shown state of an existing part** — the hidden and shown states of a part are not separate parts. The element itself should be a named part (so the editor can control its visibility per breakpoint); creating an additional part to represent its hidden or shown variant is wrong.
- ❌ **Pure grouping wrapper** — not a part. A `<div>` whose only role is to hold already-named siblings has no independent editor surface; let layout live in the parent's CSS.
- ❌ **Child with no independent editor surface** — not a part if its styling and data are already fully owned by the parent. This applies regardless of how many siblings it has. Two ways a child's editor surface can already be covered by the parent: (1) its CSS properties are inherited or set via the parent's rule; (2) its data is defined on the parent. **Canonical example:** an `<img>` inside a carousel slide whose `src` and `alt` come from the parent slide's data, and whose visual properties (object-fit, border-radius) could equally be set on the slide's own CSS rule — the slide already owns both data and styling, so the `<img>` is not a named part. Use a CSS module class for any structural CSS it needs.
- ❌ **Positional duplicate** — not separate parts. Elements that are semantically identical and differ only in position (e.g. prev/next buttons) are one part; differentiate position with CSS (`:first-of-type` / `:last-of-type`, `data-` attribute, or `:nth-child`).
- ✅ **Passes all checks** — a named part. Classify as **Semantic** (needs `elementProps`: data, behavior, direction, event handlers) or **Styling-only** (CSS class is sufficient).

## Sanity check — apply after producing the parts list

Before finalising, verify each proposed part against its parent:

> Would the editor controls generated for this part be a strict subset of its parent's controls?

If yes — the part adds no independent editor surface and should be removed. This catches rationalisation after-the-fact ("the parent *could* expose this CSS property too, but so could the child separately"). When in doubt, fewer parts is usully better.
