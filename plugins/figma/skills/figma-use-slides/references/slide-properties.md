# Slide-Specific Properties

## isSkippedSlide

Read and set whether a slide is skipped during presentation playback.

```js
const slide = figma.getNodeById("SLIDE_ID");

// Read
const isSkipped = slide.isSkippedSlide;

// Set — skip a slide
slide.isSkippedSlide = true;

// Unskip
slide.isSkippedSlide = false;
```

## focusedSlide (Page property)

Get or set the currently focused slide on a page. This is a property of `PageNode`, not `SlideNode`.

```js
// Get the focused slide
const focused = figma.currentPage.focusedSlide;
if (focused) {
  return { focusedSlideId: focused.id, name: focused.name };
}

// Set the focused slide
const slide = figma.getNodeById("SLIDE_ID");
figma.currentPage.focusedSlide = slide;
```

## focusedNode (Page property)

Get or set the currently focused node on a page. Works with any focusable node.

```js
const focused = figma.currentPage.focusedNode;
if (focused) {
  return { id: focused.id, type: focused.type, name: focused.name };
}
```

## InteractiveSlideElementNode

Interactive elements embedded in slides (polls, embeds, etc.). These are read-only — you cannot create them via the Plugin API, but you can detect and inspect them.

```js
const slide = figma.getNodeById("SLIDE_ID");
const interactive = slide.findAll(n => n.type === "INTERACTIVE_SLIDE_ELEMENT");
return interactive.map(n => ({
  id: n.id,
  type: n.interactiveSlideElementType,
}));
```

Possible `interactiveSlideElementType` values: `'POLL'`, `'EMBED'`, `'FACEPILE'`, `'ALIGNMENT'`, `'YOUTUBE'`.

## Known Limitations

- **`getSlideTransition()` / `setSlideTransition()`**: These methods are declared in the type definitions but throw "not implemented" at runtime. Do not use them.
- **`SlideGridNode.clone()`**: Throws at runtime — you cannot copy the slide grid.
- **Slide themes**: `slideThemeId` is available as a read-only property on slide nodes for identifying which theme is applied, but theme manipulation APIs are limited.
- **`figma.createTable()` and `figma.createGif()`**: These FigJam node types (TABLE, MEDIA) are currently blocked in Slides mode by the Plugin API, even though the Slides editor supports tables and media. To work with tables and media in Slides, use the editor UI directly. This is a pre-existing Plugin API limitation, not specific to `use_figma`.

<!-- TODO(dschwartz): Before production launch, fix NODE_TYPES_BLOCKED_IN_SLIDES in
     share/plugin-api/src/api/constants.ts to unblock TABLE and MEDIA for Slides
     (same pattern as the SYMBOL unblock for MCP/assistant). Remove this limitation
     note once fixed. -->
