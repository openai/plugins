# Story Patterns and Scene Contracts

## What Problem This Solves

This reference helps choose the right scroll narrative pattern and turn it into explicit scene data before implementation.

## When To Use It

Use this before designing or implementing a parallax story, sticky graphic, scroll-driven timeline, rich-media visual article, map fly-through, or data-bound scene sequence.

## Key Takeaways

- Scrollytelling is author-led. It works best when the reader benefits from a paced sequence of evidence.
- Parallax is not a genre by itself. It is a depth or reveal technique that must clarify scale, place, foreground/background relationship, or media synchronization.
- Each step must add evidence. If the graphic only becomes more dramatic, simplify it.
- Every scene should work as a still frame. The scroll transition is connective tissue, not the only explanation.
- Text and visualization must tell the same story. Do not put important evidence in the graphic that the text does not address.
- Give the reader a sense of what is coming and how long the experience is. A visible next section, progress cue, or stepped fallback can prevent disorientation.

## Technique Vocabulary

- **Graphic sequence**: a sticky visual switches, fades, or swaps between key frames as text steps pass. Use for stepwise highlights, visual timelines, and media-supported explanations where the intermediate states are not important.
- **Animated transition**: a sticky visual interpolates between chart, map, or annotation states. Use when transformation, accumulation, comparison, or state change is the evidence.
- **Pan and zoom**: scrolling controls a viewport over a map, photograph, diagram, or large visualization. Use when spatial context matters and the camera move has an annotation purpose.
- **Moviescroller**: scrolling advances video, rendered frames, or a 3D camera path. Use when exact timing, frame-level inspection, or mechanism matters more than free playback.
- **Show-and-play**: a video or animation starts, pauses, or reveals when the reader reaches it. Use sparingly; cue it clearly and avoid surprise audio.
- **Parallax depth layer**: foreground, midground, and background layers move at different rates. Use when depth, occlusion, scale, or contextual anchoring clarifies the data.
- **Sticky side-by-side**: text scrolls in one column while the graphic stays pinned beside it. Use for desktop evidence walkthroughs where text and visual must remain simultaneously inspectable.
- **Sticky overlay**: text panels scroll over a full-viewport visual or media scene. Use for cinematic or map/video-backed stories, while preserving label readability and avoiding blocked evidence.
- **Stacked mobile fallback**: each step becomes an inline static or lightly animated frame. Use when mobile performance, viewport height, or pointer precision makes sticky scrollytelling fragile.

## Choose Scroll, Stepper, Or Static

Use scroll when:

- the natural article interaction is reading downward
- staged reveal helps the reader follow chronology, spatial movement, accumulation, or mechanism
- the visual changes are meaningful even if the reader scrolls quickly or backward
- the reader does not need random access as the primary interaction

Use a stepper when:

- states are discrete and exact comparison matters
- replay, pause, next/back, or direct step access is important
- the story length should be obvious
- the scroll version would require precision scrolling

Use static charts or small multiples when:

- every state can be compared simultaneously
- the motion does not add evidence
- mobile stacking would produce the same understanding with less complexity
- the story is short enough that ordinary inline figures are clearer

## Scene Contract

Represent every scene as data before binding it to a library:

| Field | Purpose |
| --- | --- |
| `id` | Stable scene identifier for routing, testing, and analytics. |
| `readerText` | The visible text or caption associated with the scene. |
| `takeaway` | The claim this scene proves. |
| `dataLayers` | Visible, hidden, dimmed, highlighted, or filtered data layers. |
| `mediaAssets` | Images, video segments, frame sequences, maps, generated assets, or 3D resources. |
| `annotationState` | Labels, callouts, source notes, caveats, and focus cues. |
| `cameraOrTransform` | Pan, zoom, parallax offsets, chart interpolation, map view, or 3D camera state. |
| `triggerRange` | Enter/exit offsets or progress range, preferably named rather than magic numbers. |
| `motionVerb` | Reveal, compare, accumulate, transform, move, zoom, pan, highlight, or play. |
| `reducedMotion` | Static key frame, numbered steps, stacked frame, or disabled optional movement. |
| `staticFrame` | Screenshot/export state that preserves the scene's claim. |

## Storyboard Checklist

- The first frame communicates the subject, the claim, and the fact that more content follows.
- Each scene has one job; avoid combining a new text claim, new camera state, new chart encoding, and new media action all at once.
- The graphic remains readable while text moves over or beside it.
- Text panels do not cover the exact evidence they describe.
- The reader can scroll quickly, reverse direction, and resize without landing in nonsense states.
- Mobile has a deliberately designed path, not just a squeezed desktop layout.
- Source notes, units, dates, and caveats remain close to the evidence.

## Red Flags

- Scrolljacking, snap-only sections, or custom wheel gestures that break native scroll.
- Parallax layers that create spectacle without clarifying the data.
- Essential values available only during a fleeting transition.
- Text and graphic telling separate storylines.
- A full-viewport pinned area where nothing visibly scrolls, leaving the reader unsure whether the page is responding.
- Long experiences with no progress cue or direct way to revisit a scene.

## Source Links

- [Narrative Visualization: Telling Stories with Data](https://idl.uw.edu/papers/narrative)
- [Scrolling into the Newsroom](https://www.benjamins.com/catalog/idj.22005.oes)
- [data.europa: Scrollytelling introduction](https://data.europa.eu/apps/data-visualisation-guide/scrollytelling-introduction)
- [data.europa: Graphic sequence](https://data.europa.eu/apps/data-visualisation-guide/scrollytelling-graphic-sequence)
- [data.europa: Animated transition](https://data.europa.eu/apps/data-visualisation-guide/scrollytelling-animated-transition)
- [data.europa: Pan and zoom](https://data.europa.eu/apps/data-visualisation-guide/scrollytelling-pan-and-zoom)
- [data.europa: Moviescroller](https://data.europa.eu/apps/data-visualisation-guide/scrollytelling-moviescroller)
- [data.europa: Show-and-play](https://data.europa.eu/apps/data-visualisation-guide/scrollytelling-show-and-play)
- [Mike Bostock: How To Scroll](https://bost.ocks.org/mike/scroll/)
- [The Pudding: Responsive scrollytelling best practices](https://pudding.cool/process/responsive-scrollytelling)
- [The Pudding: How to implement scrollytelling with six different libraries](https://pudding.cool/process/how-to-implement-scrollytelling/)
