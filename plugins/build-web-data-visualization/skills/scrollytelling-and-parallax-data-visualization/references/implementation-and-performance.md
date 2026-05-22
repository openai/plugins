# Implementation and Performance

## What Problem This Solves

This reference chooses the lightest implementation architecture for scroll-driven data stories and names the performance risks before animation is added.

## Stack Selection

- **CSS native scroll + `position: sticky`**: default for pinned sections, side-by-side layouts, overlay panels, and native document flow.
- **IntersectionObserver**: use for enter/exit triggers, lazy loading, render activation, and coarse scene changes without scroll handlers.
- **Scrollama**: use when a lightweight scrollytelling controller is enough: step triggers, progress callbacks, custom offsets, and sticky graphic patterns.
- **CSS ScrollTimeline or ViewTimeline**: use for simple transform/opacity animations tied to scroll progress when browser support and fallback are acceptable.
- **Motion `useScroll`**: use in React for scroll-linked values, parallax transforms, progress ranges, and composition with motion values.
- **GSAP ScrollTrigger**: use for complex scrubbed timelines, pinning, labels, snapping, velocity-aware behavior, and rich choreography.
- **D3/SVG**: use when data-bound marks, labels, annotations, and exportable vector states are the main visual layer.
- **Canvas2D**: use when dense flat marks or repeated redraws make SVG too expensive and hit testing remains manageable.
- **WebGL, deck.gl, PixiJS, or Three.js**: use when GPU-scale marks, particles, flows, custom blending, map layers, or 3D camera states are necessary.
- **Video or frame sequences**: use for moviescrollers only when the frame content is evidence. Prefer encoded video for continuous footage; prefer image sequences when precise frame control or annotation alignment matters.

## Architecture Rules

- Keep scroll state separate from render state. The scroll controller emits scene id, direction, and progress; renderers translate those into visual states.
- Precompute scene ranges and geometry on resize, not inside every scroll event.
- Use named scene ids and ranges instead of magic thresholds scattered through components.
- Let CSS handle sticky positioning whenever possible.
- If JavaScript listens to scroll, batch work with `requestAnimationFrame`, keep handlers tiny, and avoid read/write cycles.
- Use passive wheel/touch listeners unless the interaction must intentionally cancel native behavior.
- Do not animate the pinned container itself when using libraries that measure pinning; animate children inside the pinned area.
- Pause or disable animation loops when the story is offscreen, route-hidden, tabbed away, or reduced-motion is active.

## Performance Defaults

- Animate `transform` and `opacity` first. Avoid animating layout or paint-heavy properties such as `top`, `left`, `width`, `height`, and expensive filters unless profiling proves they are safe.
- Reserve aspect ratios and dimensions for all images, videos, canvases, maps, and WebGL containers to avoid layout shift.
- Lazy-load offscreen media, but eager-load first-viewport and LCP assets.
- Use responsive images and appropriately sized video posters.
- Cache text metrics, scales, paths, map projections, WebGL buffers, and media frame metadata.
- Avoid DOM-heavy scenes with hundreds of individually animated nodes. Move dense marks to Canvas or WebGL, or reduce the scene.
- Budget the whole page: sticky visuals, text panels, videos, maps, WebGL contexts, fonts, and overlays all compete for memory and frame time.
- Profile on realistic mobile hardware, not only desktop.

## Mobile Guidance

- Decide early whether mobile stays scrolly or becomes stacked. Stacked frames are often better when transitions are not the evidence.
- Avoid relying on CSS `vh` for trigger heights on mobile browsers where browser chrome can change viewport height while scrolling. Measure `window.innerHeight` and update thoughtfully when needed.
- Keep text panels short. Long panels can force readers to choose between reading text and watching the visual state.
- Remove hover-only details; replace them with fixed labels, tap targets, or visible annotations.
- Test fast thumb scroll, reverse scroll, orientation change, address-bar collapse, and low-power devices.

## Rich Media Guidance

- Use posters and placeholders that preserve layout before media is ready.
- Do not autoplay audio. Cue video starts visibly and provide replay or step access when the video is explanatory.
- For moviescrollers, clamp frame progress and handle skipped ranges so fast scroll still lands on valid frames.
- For map fly-throughs, keep intermediate camera states interpretable and avoid motion that hides the actual geography being explained.
- For parallax, keep depth ratios subtle and semantic: background moves slower, foreground anchors evidence, and labels remain stable enough to read.

## Debugging And Profiling

- In Chrome DevTools Performance, inspect scroll recordings for long tasks, forced reflow, layout, paint, raster, and dropped frames.
- Enable FPS or rendering diagnostics when tuning animation.
- Verify scroll remains responsive while images, video, maps, or WebGL assets load.
- Add render-ready markers before screenshot capture or visual regression tests.
- Test reduced-motion paths and static key frames with the same seriousness as the animated path.

## Source Links

- [Scrollama](https://github.com/russellsamora/scrollama)
- [GSAP ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
- [Motion useScroll](https://motion.dev/docs/react-use-scroll)
- [MDN: CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [Chrome: Animate elements on scroll with scroll-driven animations](https://developer.chrome.com/articles/scroll-driven-animations)
- [Chrome: Scroll-driven animations performance case study](https://developer.chrome.com/blog/scroll-animation-performance-case-study/)
- [web.dev: High-performance CSS animations](https://web.dev/articles/animations-guide)
- [web.dev: Avoid layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)
- [Chrome: Passive event listeners](https://developer.chrome.com/blog/passive-event-listeners)
- [MDN: Lazy loading](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Lazy_loading)
- [The Pudding: Responsive scrollytelling best practices](https://pudding.cool/process/responsive-scrollytelling)
