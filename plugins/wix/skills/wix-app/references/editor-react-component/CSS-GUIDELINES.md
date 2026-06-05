# CSS guidelines

These rules govern the CSS authored for each generated site
component. The rules exist so the rendered component is editable in
the Wix visual editor, fits any user-resizable container, and can be
parsed by zeroConfig to produce a correct manifest. Each rule states
_why_; when an edge case isn't covered literally, follow the intent.

## Naming and class application

### Apply classes via the `classnames` helper; merge `className` on the root

All CSS lives in a single CSS module file imported as `import styles from './[ComponentName].module.css';`. There is no separate global CSS import.

There are two kinds of classes, determined by whether the element is a named part:

| Element type | className | Why |
|---|---|---|
| Named part | `classNames('heading', styles.heading)` | Global string → zeroConfig creates an editor element; module class → applies the component's own CSS |
| Non-part (layout/structural) | `styles.contentWrapper` | Module class only — invisible to zeroConfig, no spurious editor element created |

**Named parts** get both a global plain string and a module class. The global string (`'<component-name>'` for root, `'<part-name>'` for inner parts — kebab-case) is what zeroConfig scans. The module class is what carries the component's structural CSS for that element.

**Non-part elements** (layout wrappers, grouping containers, structural helpers) get only a module class. CSS module classes are mangled and invisible to zeroConfig.

The root also merges the consumer-provided `className` prop via the `classnames` helper.

**Why:** zeroConfig creates one editor element per global class. A global class on a non-part produces a spurious editor element with no meaningful surface.

```tsx
import classNames from 'classnames';
import styles from './ProfileCard.module.css';

// ✅ Root: global string + module class + consumer className
<div className={classNames(className, 'profile-card', styles.root)} id={id}>

  {/* ✅ Named part: global string + module class */}
  <h2 className={classNames('heading', styles.heading)}>{heading}</h2>

  {/* ✅ Non-part layout wrapper: module class only */}
  <div className={styles.contentWrapper}>
    <span className={classNames('label', styles.label)}>{label}</span>
  </div>
</div>

// ✅ Internal sub-components — same pattern on part slots
<CardHeader className={classNames('header', styles.header)}>
  <CardTitle className={classNames('title', styles.title)}>{title}</CardTitle>
</CardHeader>
```

### Use single-class selectors

Every selector is exactly one class, written as a flat top-level
rule. Compound selectors (`.a.b`), descendant
selectors (`.a .b`), child combinators (`.a > .b`), sibling
combinators (`.a + .b`), tag selectors, and CSS nesting (the `&`
syntax) are not permitted in component CSS.

**Why:** zeroConfig pairs each editor element with the single CSS
rule keyed on its class. A compound or relational selector means
either two elements share a rule or one element's appearance depends
on context — either way the editor cannot decide which rule to
modify when a user changes a property. CSS nesting compiles to
descendant selectors and has the same effect.

```css
/* ✅ Do: Single-class selector — unambiguous mapping to an editor control */
.profile-card {
}
.title {
}
.content {
}

/* ❌ Compound selector — rule applies only when both classes match the same element */
.profile-card.featured {
}

/* ❌ Descendant selector — rule depends on ancestor structure */
.profile-card .title {
}

/* ❌ Child combinator — rule depends on direct parent */
.profile-card > .content {
}

/* ❌ Sibling combinator — rule depends on a sibling element */
.title + .subtitle {
}

/* ❌ CSS nesting — compiles to a descendant selector */
.profile-card {
  & .title {
    color: black;
  }
}
```

## Layout and responsiveness

### Root fills its container

The root element sets `width: 100%`, `height: 100%`, and
`box-sizing: border-box`. The component never assumes a specific
pixel size for its outer box.

**Why:** Wix users place components in resizable slots whose
dimensions aren't known at authoring time. A root with hardcoded
width or height overflows or leaves gaps inside its slot.

```css
/* ✅ Do: Root fills any slot the user creates */
.profile-card {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
```

### Pipe sizing through every layer below the root

Every element between the platform-sized root and the leaf content
must explicitly participate in the sizing chain — one unsized
wrapper collapses the entire subtree to intrinsic size.

Use `flex: 1; min-width: 0` (or `min-height: 0` on the block axis)
on children that should grow, and `flex: 0 0 auto` on children that
should stay fixed-size.

**Why:** flex/grid children default to `auto` sizing and shrink to
content. A wrapper `<div>` without explicit sizing breaks the chain
even when the root fills its slot correctly.

```css
/* ✅ Do: grower fills remaining space */
.wrapper {
  display: flex;
  flex: 1;
  min-width: 0;
}

/* ✅ Do: fixed child keeps intrinsic size */
.control {
  flex: 0 0 auto;
}
```

### Set `box-sizing: border-box` on every selector

Apply `box-sizing: border-box` to every class in component CSS, not
just the root. The default `content-box` is never wanted in this
codebase.

**Why:** the editor exposes padding and border-width as live
controls. With `content-box`, increasing either grows the element's
outer box, which makes neighbouring elements visibly shift while the
user is dragging a slider — the component "shakes" in the editor.
`border-box` keeps the outer dimension stable; padding and border
eat into the existing box instead, so the layout stays still while
the user tunes values.

```css
/* ✅ Do: border-box — outer size stays stable while the editor tunes padding and border */
.profile-card,
.title,
.button {
  box-sizing: border-box;
}

/* ❌ content-box — outer size grows when the editor adjusts padding or border */
.profile-card {
  box-sizing: content-box; /* the default — don't rely on it */
}
```

### Adapt to container size, not viewport

Layout responds to the size of the component's parent, not to the
browser viewport. Use intrinsic flex/grid sizing (`auto-fit`,
`minmax(...)`, `1fr`) and `clamp()` for fluid scaling. `@media`
queries keyed on viewport dimensions (`width`, `height`,
`orientation`) are not permitted in component CSS.

**Why:** the Wix editor owns viewport-level breakpoints. A component
that branches on viewport width competes with the editor's
responsiveness model and renders the same container size differently
across viewports, breaking the editor's WYSIWYG contract.

```css
/* ✅ Do: Container-driven sizing — adapts to the slot, not the viewport */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: clamp(1rem, 2.5vw, 2rem);
}

/* ❌ Viewport breakpoint — fights the editor's responsiveness model */
@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
```

### Use logical properties on the inline axis

For any property that should flip between LTR and RTL — horizontal
margin, padding, border, positional offset — use logical properties
keyed on the inline axis: `margin-inline`, `margin-inline-start`,
`margin-inline-end`, `padding-inline`, `padding-inline-start`,
`padding-inline-end`, `border-inline-start`, `border-inline-end`,
`inset-inline-start`, `inset-inline-end`. Do not use `margin-left` /
`margin-right`, `padding-left` / `padding-right`, `border-left` /
`border-right`, `left`, or `right`.

Block-axis properties (`margin-top`, `margin-bottom`, `padding-top`,
`padding-bottom`, `border-top`, `border-bottom`, `top`, `bottom`)
stay as physical properties — they don't flip with text direction
in horizontal writing modes, which is what site components ship in.

**Why:** the Wix editor lets the site owner switch a site's text
direction between LTR and RTL. Logical inline properties flip
automatically with `direction: rtl` set by an ancestor, so one CSS
file produces correct layouts in both directions. Physical
left/right properties stay locked regardless of direction, which
breaks RTL layouts (icons end up on the wrong side of text, padding
piles up on the wrong edge, sticky offsets point the wrong way).

```css
/* ✅ Do: Inline logical properties — flip automatically in RTL */
.profile-card {
  padding-inline: 24px;
  margin-inline-start: 8px;
  border-inline-start: 4px solid currentColor;
}

/* ❌ Don't: Physical left/right — stays locked in RTL and breaks the layout */
.profile-card {
  padding-left: 24px;
  padding-right: 24px;
  margin-left: 8px;
  border-left: 4px solid currentColor;
}

/* ✅ Do: Block axis stays physical — top/bottom don't flip with direction */
.banner {
  position: sticky;
  top: 0;
  padding-block: 12px;
}
```

### Set the root layout via `--display`, never `display`

The root rule declares `--display: <value>` and does not set
`display` itself. The platform reads `--display` and applies the
resolved `display` value at runtime. This rule applies to the root
selector only — inner element classes set `display` directly as
normal.

**Why:** the editor toggles a component's visibility (and other
display modes) by overriding the `--display` custom property on the
root. If the root rule also sets `display` directly, that
declaration wins over the platform's override and the editor has to
rewrite the rule to take effect, which is fragile. Inner elements
aren't toggled this way, so they use `display` normally.

```css
/* ✅ Do: Root declares --display only — platform applies it, editor can override */
.profile-card {
  --display: flex;
}

/* ❌ Don't: Root sets display directly — competes with the platform override */
.profile-card {
  --display: flex;
  display: var(--display);
}

/* ✅ Do: Inner elements set display normally — the --display rule is root-only */
.header {
  display: flex;
  align-items: center;
}
```

### Choose one of four layout shapes for the component root

A component's root layout typically fits one of four shapes — reach
for the simplest one that satisfies the design.

**Why:** a small, shared vocabulary of layouts produces predictable
manifests and predictable editor behavior. The editor's
auto-generated controls (gap, padding, alignment) are tuned for
these shapes.

```css
/* ✅ Do: Single column — stacked content (profile card, pricing card, CTA block) */
.profile-card {
  --display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
  padding: clamp(1rem, 3vw, 2rem);
}

/* ✅ Do: Two-column split — media + text pair (testimonial, feature row, media card) */
.media-card {
  --display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(1rem, 3vw, 2rem);
  align-items: center;
}

/* ✅ Do: Multi-column grid — list of children (product list, testimonial list, gallery) */
.testimonial-list {
  --display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: clamp(1rem, 2.5vw, 2rem);
}

/* ✅ Do: Inline row — fixed controls on edges, growing center
   (numeric stepper, search bar, toolbar, split button, pagination).
   Pair with stretch-chain rules: controls flex: 0 0 auto,
   center area flex: 1; min-width: 0. */
.numeric-stepper {
  --display: flex;
  flex-direction: row;
  align-items: center;
}
```

## CSS variables and props

### Use literal CSS values; introduce a variable only when interpolation requires it

Write CSS values as literals. Introduce a CSS custom property _only_
when the value is consumed inside a CSS function or compound
expression that cannot be written as a plain value — for example
inside `repeat()`, `calc()`, `min()`, `max()`, or `clamp()`. Do not
add a React prop for a value the user wouldn't meaningfully tune.

**Why:** every CSS variable that crosses into a React prop becomes a
control in the editor. Exposing routine values like `gap` or
`padding` as props clutters the editor UI, and the editor already
auto-surfaces those properties from the CSS rule itself —
duplicating them as props gives the user two competing controls for
the same thing.

```css
/* ❌ Don't: Unnecessary variable — value isn't interpolated anywhere */
.profile-card {
  --gap: 16px;
  gap: var(--gap);
}

/* ✅ Do: Literal value — nothing to interpolate */
.profile-card {
  gap: 16px;
}

/* ✅ Do: Variable required — value is consumed inside repeat() */
.card-grid {
  --columns: 3;
  grid-template-columns: repeat(var(--columns), 1fr);
}
```

## Other rules

### Keep all styling in CSS

Static styling lives in the component's CSS. Do not use the JSX
`style={{ ... }}` attribute on rendered elements. Dynamic values
that genuinely vary per instance go through CSS custom properties
(see the rule above), still set in CSS.

**Why:** zeroConfig reads CSS rules to derive the editor's control
surface. An inline `style` attribute is invisible to the extractor,
so any value baked into JSX cannot be edited in the visual editor —
the user sees no control for it.

```tsx
// ❌ Inline style — invisible to zeroConfig, no editor control
<div className="profile-card" style={{ padding: 20, borderRadius: 8 }} />

// ✅ Do: Defaults in CSS — surfaced to the editor as controls
<div className="profile-card" />
```

```css
/* ✅ Do: Defaults belong in CSS so the editor can surface them */
.profile-card {
  padding: 20px;
  border-radius: 8px;
  background: #ffffff; /* Use `background`, never `background-color` — the schema key is "background"; zeroConfig can't match "background-color" so the default is lost in the design panel */
}
```

### Default aesthetic: polished and generous

When the user does not specify a visual style, default to a polished,
modern look. The editor lets the user override every value, so a
refined default costs nothing.

| Property | Guidance |
|---|---|
| `border-radius` | 8–12 px containers, `50%` for controls and interactive groups (buttons, pills, input rows) |
| `box-shadow` | Prefer soft, diffused shadows over hard borders (e.g. `0 2px 8px rgba(0,0,0,0.06), 0 0 1px rgba(0,0,0,0.08)`) |
| Spacing | 8–16 px inside controls, 16–32 px for containers. Avoid cramped layouts |
| Typography | Body ≥ 16 px, labels ≥ 14 px, headings larger. `font-weight: 500`–`600` |
| Palette | Root background transparent (blends with page). Use subtle fills (`#f1f5f9`/`#e2e8f0`) on *inner controls* only (buttons, input areas, pill containers). Text `#1e293b`/`#334155`, borders `#e2e8f0`. `#475569` for large/secondary text only |
| Accent | Use a muted accent color (e.g. `#6366f1`, `#7c83db`) sparingly on interactive icons, active indicators, and primary actions — just enough to signal interactivity without dominating |
| Contrast | WCAG AA minimum: 4.5:1 body text, 3:1 large text / UI controls |
| Hierarchy | Interactive elements visually distinct from static via weight, fill, or elevation |
| Touch targets | Interactive elements ≥ 44×44 px |

### Don't author state styles (`:hover`, `:focus`, `:disabled`, `[data-state]`)

State pseudo-classes and state attribute selectors are not allowed
in component CSS. That includes `:hover`, `:focus`, `:focus-visible`,
`:active`, `:disabled`, and attribute selectors like
`[data-state='open']` or `[aria-selected='true']`.

**Why:** the editor owns state styling. Hover, focus, disabled, and
similar interaction states are exposed to the site owner as
editable visual states — the platform writes those rules itself
based on what the user configures. State styles authored in the
component compete with the platform's rules and produce two
sources of truth for the same state.

```css
/* ❌ Don't: hover/focus/disabled state — platform owns these */
.button:hover {
  background-color: #f0f0f0;
}
.button:focus {
  outline: 2px solid blue;
}
.button:disabled {
  opacity: 0.5;
}

/* ❌ Don't: state attribute selectors — same problem */
.panel[data-state='open'] {
  background-color: #fafafa;
}

/* ✅ Do: Style the resting state only — platform layers state styling on top */
.button {
  background-color: #ffffff;
  color: #111;
}
```

### Express selection / mode variants with JS-toggled modifier classes

The previous rule banned **interaction states** (`:hover`, `:focus`,
`:focus-visible`, `:active`, `:disabled`, `[data-state]`,
`[aria-selected]`) — those are user-controlled and platform-owned.
**Selection / mode variants** (`selected`, `active`, `current`,
`open`, `expanded`) are different: they are part of the component's
own data model and the component owns their styling.

Express each variant as a **JS-toggled modifier class**, applied
alongside the base class via `classNames`. Each class — base and
modifier — is its own **single-class** CSS rule. The decision of
which class applies is made in JSX from props/state, not by a CSS
selector.

**Why:** the modifier class is decided in JSX, not in CSS. zeroConfig
still sees one selector per rule (both classes are single-class
rules), so the editor's mapping stays unambiguous. `PARTS.md`
excludes "state or variant" from the named-parts taxonomy — the
modifier is CSS-only, not a part.

```tsx
/* ✅ Do: JS-toggled modifier class, applied alongside the base */
<button
  className={classNames(
    styles.toggleSegment,
    isSelected && styles.toggleSegmentSelected,
  )}
/>
```

```css
/* ✅ Do: each class is its own single-class rule */
.toggleSegment {
  background: transparent;
  color: #475569;
  font-weight: 500;
}

.toggleSegmentSelected {
  background: #ffffff;
  color: #0f172a;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.1);
}

/* ❌ Don't: compound selector — banned by the single-class-selector rule */
.toggleSegment.selected {
}

/* ❌ Don't: attribute selector keyed on ARIA — banned by the no-state-CSS rule */
.toggleSegment[aria-selected='true'] {
}

/* ❌ Don't: pseudo-class — that's an interaction state, platform-owned */
.toggleSegment:checked {
}
```

### Don't add transitions or animations unless functionally required

Component CSS does not declare `transition` or `animation` for
decorative purposes. Use them only when the motion is part of the
component's behavior (e.g. an accordion panel sliding open, a
carousel translating between slides). When transitions are required,
list the specific properties — never `transition: all`,
`transition-property: all`, or the implicit `all` of a duration-only
shorthand (`transition: 0.2s ease`).

**Why:** the editor mutates many CSS properties live as the user
configures the component — colors, font, padding, border width,
even layout properties on parent classes. Animating those mutations
makes the editor visibly laggy: values meant to update instantly
slide instead. State transitions like hover and focus are owned by
the platform (see the rule above), so the component shouldn't
author them either.

```css
/* ❌ Don't: decorative transition with no functional reason */
.button {
  transition: background-color 0.2s ease;
}

/* ❌ Don't: transition: all — animates every property the editor touches */
.button {
  transition: all 0.2s ease;
}

/* ❌ Don't: implicit all — duration-only shorthand resolves to transition-property: all */
.button {
  transition: 0.2s ease;
}

/* ✅ Do: Functional transition with specific properties named (e.g. accordion expand) */
.panel {
  transition: height 0.2s ease;
}
```

### Set `pointer-events: auto` on the root and every interactive element

The root selector and every nested class that the user can click,
hover, or focus (links, buttons, controls) explicitly set
`pointer-events: auto`.

**Why:** the editor renders components inside wrappers that disable
pointer events at the wrapper level so the editor itself can capture
clicks for selection. Explicit `auto` on the component's own
elements ensures interaction reaches them at runtime on the
published site, where the wrapper is gone.

```css
/* ✅ Do: pointer-events: auto — interaction reaches component elements through the editor wrapper */
.profile-card,
.title,
.button {
  pointer-events: auto;
}
```
