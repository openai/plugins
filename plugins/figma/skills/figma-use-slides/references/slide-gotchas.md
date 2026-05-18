# Slide Gotchas & Common Mistakes

> Part of the [figma-use-slides skill](../SKILL.md). Pitfalls specific to working in Slides files.

## Contents

- Position after appendChild (critical)
- Canonical text-edit recipe (font load → await → mutate → return IDs)
- Sequential awaits — batch independent async calls with `Promise.all`
- Prefer indexed lookups over `findAll`/`findOne` full-tree scans
- Scope traversal to the smallest known ancestor (a slide, not the page)
- Set `figma.skipInvisibleInstanceChildren = true` for read-only traversal
- SLIDE_GRID and SLIDE_ROW are opaque nodes
- Validation without get_metadata
- Building multi-element slides incrementally


## Canonical text-edit recipe (font load → await → mutate → return IDs)

The same canonical recipe used in Design files applies inside slides — see [figma-use → gotchas.md → Canonical text-edit recipe](../../figma-use/references/gotchas.md#canonical-text-edit-recipe-font-load--await--mutate--return-ids) for the full WRONG/CORRECT pair. Two slide-specific reminders:

1. **Inter preload doesn't cover deck-theme fonts.** Decks frequently switch the theme font to families like `Roboto Mono`, `Merriweather`, or a brand font — those still need an explicit `loadFontAsync` for every (family, style) you mutate.
2. **When restyling existing slide text, load the node's *current* font, not a hardcoded default.** Slide theme tokens push fonts onto nodes that may differ from what you'd guess. Use `getStyledTextSegments(['fontName'])` and `loadFontAsync` each segment's font before any mutation.

```js
// Restyle existing slide text without assuming the font
await Promise.all(
  textNode.getStyledTextSegments(['fontName'])
    .map(s => figma.loadFontAsync(s.fontName))
)
textNode.characters = "Updated"
return { mutatedNodeIds: [textNode.id] }
```


## Prefer indexed lookups over `findAll` / `findOne` full-tree scans

Same rule as in design files (see [figma-use → gotchas.md → Prefer indexed lookups](../../figma-use/references/gotchas.md#prefer-indexed-lookups-over-findall--findone-full-tree-scans)). On slide trees, the most common offenders are `slide.findAll(n => n.type === 'TEXT')` (use `slide.findAllWithCriteria({ types: ['TEXT'] })`) and `slide.findAll(n => n.type === 'INTERACTIVE_SLIDE_ELEMENT')` (same fix). If you have a slide or element ID, use `figma.getNodeByIdAsync(id)` — never re-scan the tree.


## Scope traversal to the smallest known ancestor

Slides specifically: **search inside the specific slide**, not the whole page. `slide.findAllWithCriteria(...)` walks one slide; `figma.currentPage.findAllWithCriteria(...)` walks every slide in the deck. When you have the target slide's ID (passed by the caller or returned from a prior call), always start the traversal there.

```js
// AVOID — scans every slide in the deck
const texts = figma.currentPage.findAllWithCriteria({ types: ['TEXT'] })

// PREFER — one slide only
const slide = await figma.getNodeByIdAsync(SLIDE_ID)
const texts = slide.findAllWithCriteria({ types: ['TEXT'] })
```

See [figma-use → gotchas.md → Scope traversal to the smallest known ancestor](../../figma-use/references/gotchas.md#scope-traversal-to-the-smallest-known-ancestor).


## Set `figma.skipInvisibleInstanceChildren = true` for read-only traversal

Same rule as in design files (see [figma-use → gotchas.md → Set figma.skipInvisibleInstanceChildren](../../figma-use/references/gotchas.md#set-figmaskipinvisibleinstancechildren--true-for-read-only-traversal)). One line at the top of any read-only slide-inspection script. Decks tend to be component-heavy (icons, logo lockups, repeating frames), so this flag is especially impactful.

```js
figma.skipInvisibleInstanceChildren = true
const slide = await figma.getNodeByIdAsync(SLIDE_ID)
const texts = slide.findAllWithCriteria({ types: ['TEXT'] })
```

Leave the flag off if you specifically need to read invisible content inside an instance (e.g., inspecting all variants of a deck-template instance).


## Sequential awaits — batch independent async calls with `Promise.all`

Same rule as in design files (see [figma-use → gotchas.md → Sequential awaits](../../figma-use/references/gotchas.md#sequential-awaits--batch-independent-async-calls-with-promiseall)). When building decks, the typical offenders are `loadFontAsync` for theme/brand fonts, `getNodeByIdAsync` for cached slide IDs, and `import*ByKeyAsync` for library variables and styles — all independent per call and all batchable.

```js
// WRONG — sequential round-trips per slide
for (const id of slideIds) {
  const slide = await figma.getNodeByIdAsync(id)
  // ... mutate
}

// CORRECT — fetch all slides in one batch, then mutate sequentially
const slides = await Promise.all(slideIds.map(id => figma.getNodeByIdAsync(id)))
for (const slide of slides) {
  // ... mutate
}
```

`setCurrentPageAsync` is the exception — page-context switches must stay sequential.


## Position after appendChild (critical)

Setting `x`/`y` on a node **before** appending it to a slide causes unpredictable coordinate offsets. The slide's internal coordinate system is only applied once the node is a child.

```js
// WRONG — position set before parenting, coordinates shift by an unpredictable offset
const rect = figma.createRectangle();
rect.resize(400, 200);
rect.x = 100;
rect.y = 300;
slide.appendChild(rect);  // rect may end up at (-140, 60) instead of (100, 300)!

// CORRECT — append to the slide first, then set all properties
const rect = figma.createRectangle();
slide.appendChild(rect);
rect.resize(400, 200);
rect.fills = [{ type: "SOLID", color: { r: 0.2, g: 0.3, b: 0.8 } }];
rect.cornerRadius = 8;
rect.x = 100;
rect.y = 300;
```

**Why this happens:** Newly created nodes default to page-level coordinates. When reparented into a slide, those coordinates are reinterpreted relative to the slide's internal origin, which may not be (0, 0). By appending first, you ensure all subsequent property assignments operate in the slide's local coordinate space.

**Safest pattern:** Always `appendChild` to the slide first, then configure everything — position, size, fills, text, corner radius. While non-positional properties (fills, fontSize, etc.) are technically safe before appending, doing everything after is simpler and avoids needing to remember which properties are coordinate-dependent.

```js
// Recommended helper pattern for building slide content
const addToSlide = (node, slide, props) => {
  slide.appendChild(node);
  if (props.resize) node.resize(props.resize[0], props.resize[1]);
  if (props.x !== undefined) node.x = props.x;
  if (props.y !== undefined) node.y = props.y;
  return node;
};
```


## SLIDE_GRID and SLIDE_ROW are opaque nodes

Only `SLIDE` nodes extend `BaseFrameMixin`. The parent containers do not:

| Node type | Mixin | Has fills? | Has children? | Has layout props? |
|---|---|---|---|---|
| `SLIDE_GRID` | OpaqueNodeMixin | No | Yes (rows) | No |
| `SLIDE_ROW` | OpaqueNodeMixin + ChildrenMixin | No | Yes (slides) | No |
| `SLIDE` | BaseFrameMixin | Yes | Yes (content) | Yes |

```js
// WRONG — throws "no such property 'fills' on SLIDE_GRID node"
const grid = figma.currentPage.children[0];
const bg = grid.fills;

// WRONG — throws on SLIDE_ROW
const row = grid.children[0];
row.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];

// CORRECT — access fills on the SLIDE node itself
const slide = row.children[0];  // type: 'SLIDE'
slide.fills = [{ type: "SOLID", color: { r: 0.06, g: 0.09, b: 0.16 } }];
```


## Validation without get_metadata

`get_metadata` does not work on Slides files. Use `get_screenshot` for visual validation and `use_figma` read-only scripts for structural validation.

**Post-creation validation pattern:**
```js
const slide = figma.getNodeById("SLIDE_ID");
const children = slide.children.map(c => ({
  name: c.name,
  type: c.type,
  x: Math.round(c.x),
  y: Math.round(c.y),
  w: Math.round(c.width),
  h: Math.round(c.height),
  text: c.type === "TEXT" ? c.characters.substring(0, 50) : undefined,
}));

// Check for overlapping bounding boxes
const overlaps = [];
for (let i = 0; i < children.length; i++) {
  for (let j = i + 1; j < children.length; j++) {
    const a = children[i], b = children[j];
    if (a.x < b.x + b.w && a.x + a.w > b.x &&
        a.y < b.y + b.h && a.y + a.h > b.y) {
      overlaps.push([a.name, b.name]);
    }
  }
}

return { children, overlaps, hasOverlaps: overlaps.length > 0 };
```

Run this after creating slide content to catch layout issues before they compound.


## Building multi-element slides incrementally

When building slides with many elements (charts, cards, grids), work in small batches and validate between each:

1. **Create the slide and background** — verify fills applied correctly
2. **Add text elements** (titles, labels) — verify positions and font loading
3. **Add shapes/data visualization** — verify no overlaps with text
4. **Add decorative elements** — verify they don't obscure content

Return all created node IDs from each step so subsequent calls can reference or clean up nodes if needed.
