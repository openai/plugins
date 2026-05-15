# Slide Content

`SlideNode` extends `BaseFrameMixin`, which means slides support the same content creation patterns as frames in Design mode: text, shapes, auto-layout, images, components, and instances.

## Adding text to a slide

```js
const slide = figma.getNodeById("SLIDE_ID");

await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });
const title = figma.createText();
title.fontName = { family: "Inter", style: "Semi Bold" };
title.characters = "Quarterly Review";
title.fontSize = 48;

slide.appendChild(title);
title.x = 100;
title.y = 80;

return { createdNodeIds: [title.id] };
```

**Font loading is required** before setting text properties. Use `listAvailableFontsAsync()` to discover available fonts. Note: "Inter" uses "Semi Bold" (with a space), not "SemiBold".

## Bulleted and numbered lists

Slides are bullet-heavy by nature. Use a **single TextNode** with `\n`-separated lines and `setRangeListOptions(start, end, { type: 'UNORDERED' | 'ORDERED' })` for native bulleted text — it gives proper hanging indents on wrapped lines.

```js
await figma.loadFontAsync({ family: "Inter", style: "Regular" });

const text = figma.createText();
slide.appendChild(text);
text.fontName = { family: "Inter", style: "Regular" };
text.fontSize = 20;
text.characters = [
  "Explore ideal outputs",
  "Eval: benchmark vs current on large files",
  "Eval: DS context into code generation · React / Vue / iOS / Android",
].join("\n");
text.fills = [{ type: "SOLID", color: { r: 0.07, g: 0.09, b: 0.13 } }];
text.lineHeight = { unit: "PERCENT", value: 145 };
text.setRangeListOptions(0, text.characters.length, { type: "UNORDERED" });

return { createdNodeIds: [text.id] };
```

**Do NOT** build bullets by laying out an ellipse + text in a horizontal auto-layout row. That pattern misaligns when text wraps to multiple lines (the wrapped line starts at the dot's x, not the first character's x — no hanging indent), and it produces a tree of vector nodes instead of a single editable text block. Use `setRangeListOptions` instead.

If only some lines should be bullets (e.g. a heading line followed by bullet items), pass a partial range: `text.setRangeListOptions(headingLength + 1, text.characters.length, { type: "UNORDERED" })`. Pass `{ type: "NONE" }` to remove list formatting from a range.

## Adding shapes

```js
const slide = figma.getNodeById("SLIDE_ID");

const rect = figma.createRectangle();
rect.resize(400, 300);
rect.fills = [{ type: "SOLID", color: { r: 0.95, g: 0.95, b: 0.97 } }];
rect.cornerRadius = 12;

slide.appendChild(rect);
rect.x = 200;
rect.y = 200;

return { createdNodeIds: [rect.id] };
```

## Adding images to a slide

**`upload_assets` is the ONLY supported way to put an image on a slide.** Do NOT use `figma.createImage()` or `figma.createImageAsync()` from inside `use_figma` — they are unsupported as image-upload entry points in Slides. Call `upload_assets` with the Slides `fileKey`; the tool returns single-use upload URLs that you POST raw image bytes to, and the image is committed and placed automatically. Pass `nodeId` (with `count: 1`) to attach the upload to an existing slide node as a fill (e.g. a rectangle already on the slide); omit `nodeId` to drop the image onto the slide as a new layer.

For the full request/response shape, see [figma-use → api-reference.md → Images](../../figma-use/references/api-reference.md#images).

## Using auto-layout within slides

```js
const slide = figma.getNodeById("SLIDE_ID");

const container = figma.createAutoLayout("VERTICAL", {
  name: "Content Block",
  itemSpacing: 16,
  paddingLeft: 40,
  paddingRight: 40,
  paddingTop: 40,
  paddingBottom: 40,
});

slide.appendChild(container);
container.layoutSizingHorizontal = "FILL";
container.layoutSizingVertical = "HUG";

return { createdNodeIds: [container.id] };
```

Remember: `layoutSizingHorizontal/Vertical = 'FILL'` must be set **after** `appendChild`.

## Working with components

Components (`SYMBOL`) are intentionally allowed in Slides mode for MCP/assistant use. You can create components and instances within slides.

```js
const component = figma.createComponent();
component.name = "Card";
component.resize(400, 200);

const instance = component.createInstance();
const slide = figma.getNodeById("SLIDE_ID");
slide.appendChild(instance);

return { createdNodeIds: [component.id, instance.id] };
```

## Positioning within slides

Slides have a fixed canvas size (typically 1920x1080). Position content using absolute `x`/`y` coordinates within the slide, or use auto-layout containers to handle positioning automatically.

**Critical: Always set `x`/`y` AFTER `appendChild`.** Setting position before parenting the node to the slide causes unpredictable coordinate offsets. See [slide-gotchas.md](slide-gotchas.md) for details and WRONG/CORRECT examples.

Recommended pattern — append first, then configure:

```js
const slide = figma.getNodeById("SLIDE_ID");

const node = figma.createRectangle();
slide.appendChild(node);
node.resize(400, 300);
node.fills = [{ type: "SOLID", color: { r: 0.2, g: 0.2, b: 0.3 } }];
node.cornerRadius = 12;
node.x = 200;
node.y = 200;

return { width: slide.width, height: slide.height, nodeId: node.id };
```
