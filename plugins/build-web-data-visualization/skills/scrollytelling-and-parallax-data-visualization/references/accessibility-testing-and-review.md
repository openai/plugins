# Accessibility, Testing, And Review

## What Problem This Solves

This reference makes scroll-driven data stories usable for readers who do not experience the animation path, cannot use pointer precision, or prefer reduced motion.

## Accessibility Defaults

- Honor `prefers-reduced-motion` for parallax, scroll-scrubbed movement, zooming, panning, animated transitions, and moviescrollers.
- Provide a reduced-motion version that shows static key frames, numbered steps, stacked frames, or the final state rather than removing evidence.
- Preserve native scrolling, scrollbar use, and standard keyboard controls.
- Keep focus order aligned with reading order, especially when sticky visuals and overlay text reorder content visually.
- Do not hide essential labels, values, source notes, or caveats behind hover or transient frames.
- Avoid surprise autoplay and never autoplay audio.
- If parallax is essential to the information, explain the information through text and static frames too.
- Give users enough cues to understand that scrolling will advance the story.

## Reduced Motion Patterns

- **Static key frames**: render first, representative, and final frames in sequence.
- **Numbered steps**: replace continuous scroll progress with explicit states.
- **Stacked mobile/static layout**: place each text block with its corresponding chart, map, or media frame.
- **Final-state summary**: show the completed chart plus annotations when animation only reveals accumulation.
- **Manual playback**: provide play/pause/replay controls when the media itself carries evidence.

## Text Alternatives

- Summarize the claim, data scope, unit, and caveat before describing visual effects.
- For parallax, describe the semantic relationship between layers rather than the visual trick.
- For moviescrollers, describe the key frames and what changes across them.
- For pan/zoom maps, describe the starting geography, destination, and why that movement matters.
- For generated or photographic substrates, separate what the image shows from what the data proves.

## Testing Checklist

- Scene routing:
  - enter, exit, reverse scroll, fast scroll, and deep-link or restored scroll position land on valid states
  - first, key, final, and reduced-motion frames preserve the claim
  - text and visual state remain synchronized after resize
- Browser behavior:
  - wheel, touch, trackpad, scrollbar drag, arrow keys, page up/down, home/end, and space behave predictably
  - no scrolljacking, trapped focus, or accidental scroll chaining
  - passive listeners are used where native scroll should not be blocked
- Visual regression:
  - desktop and mobile key frames
  - sticky side-by-side and overlay layouts
  - media placeholders, loaded states, and error states
  - reduced-motion or stacked fallback
- Performance:
  - no forced layout loops during scroll
  - no blank Canvas or WebGL frames
  - offscreen media and animation loops pause or defer
  - mobile browser viewport changes do not break trigger positions
- Accessibility:
  - keyboard path reaches controls and content in order
  - screen-reader text communicates the data claim
  - contrast remains sufficient over media
  - motion can be disabled without losing the evidence

## Human Review Questions

- Would a reader understand the core claim from the first frame and final frame?
- Does each scroll action reveal evidence, or only add polish?
- Can a reader skim quickly and still avoid misleading intermediate states?
- Does the mobile path feel intentionally designed?
- Are source notes, dates, uncertainty, and caveats visible at the moment they matter?
- Would the story still work as a static article with selected key frames?

## Source Links

- [W3C WCAG: Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions)
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/%40media/prefers-reduced-motion)
- [web.dev: prefers-reduced-motion](https://web.dev/articles/prefers-reduced-motion)
- [web.dev: Animation and motion accessibility](https://web.dev/learn/accessibility/motion)
- [Mike Bostock: How To Scroll](https://bost.ocks.org/mike/scroll/)
- [The Pudding: Responsive scrollytelling best practices](https://pudding.cool/process/responsive-scrollytelling)
