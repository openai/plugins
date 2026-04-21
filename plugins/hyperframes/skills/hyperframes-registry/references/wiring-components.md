# Wiring Components

Components are effect snippets — HTML, CSS, and optionally JS that you merge directly into an existing composition. Unlike blocks, components have no standalone timeline; they participate in the host composition's timeline.

## General process

1. Run `hyperframes add <component-name>`
2. Open the installed file (e.g., `compositions/components/grain-overlay.html`)
3. Read the comment header for usage instructions
4. Copy the parts into your host composition:
   - **HTML elements** — inside your `<div data-composition-id="...">`
   - **CSS styles** — into your composition's `<style>` block
   - **JS setup** — into your composition's `<script>`, before your timeline code
   - **Timeline calls** — into your GSAP timeline (if the component exposes them)

## Example: grain-overlay (CSS-only, no timeline integration)

```html
<!-- Paste the overlay div into your composition -->
<div
  id="grain-overlay"
  style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 100;"
>
  <div class="grain-texture"></div>
</div>
```

Then paste the CSS keyframes and `.grain-texture` rule into your styles. No GSAP timeline calls needed — the grain animates via CSS `@keyframes`.

## Example: shimmer-sweep (needs timeline integration)

Wrap target elements, paste CSS and JS, then drive the sweep from your timeline:

```js
tl.fromTo(
  ".shimmer-sweep-target",
  {
    "--shimmer-pos": "-20%",
  },
  {
    "--shimmer-pos": "120%",
    duration: 1.2,
    ease: "power2.inOut",
    stagger: 0.15,
  },
  2.0,
);
```

## Example: grid-pixelate-wipe (scene transition)

Paste the overlay HTML and CSS, then drive `.grid-cell` scale in your timeline:

```js
// Cover screen
tl.to(
  ".grid-cell",
  { scale: 1, duration: 0.6, stagger: { amount: 0.6, from: "center" }, ease: "power2.inOut" },
  5.0,
);
// Swap scenes
tl.set("#scene-a", { opacity: 0 }, 5.6);
tl.set("#scene-b", { opacity: 1 }, 5.6);
// Reveal
tl.to(
  ".grid-cell",
  { scale: 0, duration: 0.6, stagger: { amount: 0.6, from: "edges" }, ease: "power2.inOut" },
  5.6,
);
```

## Key principles

- Components inherit the host composition's dimensions and duration
- Place component HTML at the appropriate z-index relative to your content
- Read the comment header in each snippet for customizable values
- Run `hyperframes lint` after wiring to catch structural issues
