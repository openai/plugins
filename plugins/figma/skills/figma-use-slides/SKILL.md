---
name: figma-use-slides
description: "This skill helps agents use Figma's use_figma MCP tool in the Slides context. Can be used alongside figma-use which has foundational context for using the use_figma tool."
disable-model-invocation: false
---

# use_figma — Figma Plugin API Skill for Slides

This skill contains Slides-specific context for the `use_figma` MCP tool. The [figma-use](../figma-use/SKILL.md) skill provides foundational context for plugin API execution via MCP as well as the full Figma plugin API for more advanced use-cases that are not described here.

**Always pass `skillNames: "figma-use-slides"` when calling `use_figma` for Slides operations.** This is a logging parameter used to track skill usage — it does not affect execution.

## Critical Rules (Slides-specific)

1. **Newly created Slides files have a default light theme.** When a Slides file is created via `create_new_file`, a default light theme is automatically initialized. This theme is structural scaffolding — you should overwrite the theme's color variables and text styles with your own design direction for the deck you're building. Do not rely on or be influenced by the default light theme tokens.
2. **MUST `appendChild` to the slide BEFORE setting `x`/`y` position.** Slides have an internal coordinate origin; positioning before parenting causes silent offsets that produce broken/overlapping layouts. Do all property configuration after appending for safety. See [slide-gotchas.md](references/slide-gotchas.md).
3. **SLIDE_GRID and SLIDE_ROW are opaque nodes** — do not access `.fills`, `.effects`, or layout properties on them. Only `SLIDE` nodes (type `'SLIDE'`) extend `BaseFrameMixin`. **Exception:** `SLIDE_ROW.name` IS settable — that's how plugins rename slide sections (e.g. `slideRow.name = "Intro"`). See [slide-lifecycle.md](references/slide-lifecycle.md).
4. **`get_metadata` does NOT work on Slides files.** Use `use_figma` read-only scripts for validation. Return created node positions in `closePlugin()` output and verify no overlapping bounding boxes.
5. **Do NOT call `figma.createPage()` in Slides.** It throws `TypeError: figma.createPage no such property 'createPage' on the figma global object` — `createPage()` is a Design-file API only (`figma.com/design/...`); the Slides URL is `figma.com/slides/...`. Use the slide grid (`SLIDE_GRID` / `SLIDE_ROW` / `SLIDE`) to organize deck structure instead — see [slide-lifecycle.md](references/slide-lifecycle.md) and [slide-grid.md](references/slide-grid.md).

## Design Thinking

Not every task needs the same depth of design thinking. Before doing anything, identify which gear you're in:

- **Content/property edits** — changing text, swapping a color, updating a number, fixing alignment, resizing an element. Skip design thinking. Just make the change and match what's already there.
- **Structural additions** — adding slides, reworking a section's layout, changing the deck's color palette, introducing a new visual element. Design thinking applies, but in *inherit* mode: the existing deck is your design language. Inspect it, match its palette, type, spatial habits, and motifs. Extend the deck's existing character rather than reinventing it.
- **New deck creation** — building a deck from scratch or from a blank file. Full design thinking applies as described below.

For structural additions to existing decks: run the inspection scripts (below) and take screenshots before making changes. The answers to "what color story?" and "what type treatment?" are already in the file — your job is to read them and stay consistent. The design principles in [slide-design.md](references/slide-design.md) describe what you're *matching*, not what you're *choosing*.

### New deck design process

Before writing any Plugin API code for a new deck, decide what it should *feel* like. Figma users have high visual expectations — a deck that looks like it came out of a generic template generator will stand out for the wrong reasons.

1. **Read the brief.** What is the deck communicating, and to whom? An investor pitch, a team retrospective, a product launch, and a technical deep-dive all demand different visual treatments. The design should be inseparable from the content.
2. **Check for a design language.** Before inventing anything, look at what the user already gave you. Brand guidelines in the prompt — color palettes, typography specs, logo rules, tone descriptors — are design decisions that have already been made. A link to a reference Figma file is a design language you should study, not glance at. The more specific the user's inputs, the less you should invent on your own. When the user provides a reference, your job shifts from *designer* to *interpreter*: extract the design language and apply it faithfully to new content.
3. **Take a position — on what's left.** If the user supplied a full brand system, your creative latitude is in layout, pacing, and composition — not in color or type. If they gave you a single reference slide for inspiration, you have more room but should still echo its character. If they gave you nothing, then you own every decision — choose a color story, a type treatment, a way of organizing space, and follow through on it across every slide. A deck with a clear perspective (even a quiet one) always reads better than one that plays it safe on every decision. The scope of "take a position" scales inversely with what the user provided.
4. **Give it a signature.** Every good deck has at least one element you'd recognize if you saw it out of context: a distinctive palette, an unexpected layout cadence, a recurring shape language. When working from brand guidelines, the signature should *come from* that brand language — amplify something that's already there rather than adding something foreign. When designing from scratch, decide what the signature is before you start building.

### Reading a reference file

When the user provides a link to a Figma file as a reference, study it before designing anything. What you extract depends on what the file is:

- **A Slides file**: `get_metadata` does not work on Slides files. Use `get_screenshot` to capture individual slides for visual reference, and `use_figma` with the reference file's `fileKey` to run read-only scripts that extract theme variables, color palettes, font choices, and layout patterns.
- **A Design file**: `get_design_context` gives you comprehensive design data — colors, typography, layout structure. `get_screenshot` gives you visual reference. Use both.

What to look for in a reference file: the color palette (which hue leads, what the accent is, how dark/light backgrounds are used), the type choices (families, weights, how hierarchy is handled), the spatial habits (where content anchors, how much whitespace, whether things bleed off edges), and any recurring motifs (shapes, line treatments, decorative elements). These are the decisions you inherit — everything else is yours.

How closely to follow the reference depends on what the user asked for. "Make it look like this" means replicate the design language with new content. "Use this for inspiration" means echo the character but make it your own. "Here's our brand deck" means extract the brand system and apply it consistently. When in doubt, stay closer to the reference — it's easier for a user to ask you to diverge than to ask you to undo invented choices that conflict with their brand.

Load [slide-design.md](references/slide-design.md) for specific guidance on color, type, layout patterns, composition, and what to avoid. When you have a reference file or brand guidelines, treat slide-design.md's principles as defaults for the decisions the user *didn't* make — not as overrides for the ones they did.

## Sections

A section is a horizontal row in the slide grid — every row is a section. Names show up in the editor (next to the row) and in Presenter View (so speakers can jump between groups). They're an organizational aid for whoever is editing the deck — the user owns where the breaks fall, not you.

### When asked to organize a deck

"Organize this deck" is ambiguous — grouping, reordering, deduping, or restructuring. Read the deck before reaching for `AskUserQuestion`.

**Default: propose, don't ask.** Most decks have cues — title bookend, numbered use cases, repeated *Before / After* pairs, transition slides ("Then X enters the chat"), a *Thank you*. When cues exist, pick a sectioning and surface it in one confirmation message. Bounded calls inside the proposal (one *Use Cases* row vs. three, where a transition slide lives) are reversible — pick one and move on.

**Fallback: ask when cues are absent.** If slides are in arbitrary order or there's no spine, ask which ranges go together and what to call them. Don't slice by thirds as a substitute for reading.

### Naming + scoping

Names should be short (1–3 words), concrete (*Demo* beats *Show & tell*), and consistent within a deck. Two to five sections is typical; more only for long or repeating decks. Names aren't slide titles — they help find a group, not describe its content.

### Renaming a section

`getSlideGrid()` returns `SlideNode[][]` — the inner arrays are plain JS arrays of slides, NOT `SLIDE_ROW` nodes. Setting `.name` on those arrays silently no-ops. To rename a section, traverse the node tree and set `.name` on the actual `SLIDE_ROW`:

```js
const slideGrid = figma.currentPage.children.find(c => c.type === "SLIDE_GRID");
slideGrid.children[0].name = "Intro";
```

## Speaker Notes

Speaker notes are the presenter's private companion to each slide. They appear in Presenter View (visible only to the speaker, not the audience) and serve as a script, cue sheet, or talking-points reference during a live presentation.

### When to write speaker notes

- **When asked**: If the user asks for speaker notes, presenter notes, talking points, or a script for a deck, write notes for every slide that has substantive content (skip section dividers or purely decorative slides unless there's something to say).
- **Presenter-ready decks**: If the user explicitly asks for a deck that is ready to present live, speaker notes are useful. Add them when they help the presenter understand pacing, transitions, or context that is not visible on the slide.
- **Sparse or visual slides**: If a slide is built around a chart, image, metaphor, or provocative question, notes can help explain what the presenter should say. Use screenshots or `node.screenshot()` for image-heavy, chart-heavy, or visually sparse slides when visual context matters, but don't screenshot every slide by default — images spend context budget.
- **Don't add notes unprompted**: For normal slide edits, layout work, or updates to existing decks, do not populate speaker notes unless the user asks. Adding notes changes the presentation flow and can surprise the deck owner.

### What good speaker notes look like

Speaker notes are for the *presenter*, not the audience. They should feel like a trusted colleague leaning over and whispering "here's what to say." Good notes:

- **Complement the slide, not repeat it.** If the slide says "Revenue grew 40%", the notes shouldn't say "Revenue grew 40%." They should say *why* it grew, what the audience should take away, or what question this usually prompts.
- **Are concise and scannable.** A presenter glancing down mid-sentence needs to find their place instantly. Use short bullet points, not dense paragraphs. Each point should be one idea.
- **Include transitions.** The best notes tell the presenter how to *move* between slides: "After the applause dies down..." or "This builds on the previous point — call back to the 40% figure."
- **Carry context the slide can't.** Data sources ("Source: Q4 FY25 internal metrics, not yet public"), caveats ("Skip this slide if the CFO is in the room"), timing cues ("This is the halfway point — you should be at ~10 minutes"), and anticipated questions ("They'll ask about margins — see appendix slide 14").
- **Match the presentation's register.** Notes for an investor pitch are precise and rehearsed. Notes for a team retro are casual and flexible. Notes for a keynote might include stage directions. Match the tone to the context.

### What to avoid in speaker notes

- **Full scripts**: Wall-of-text notes encourage reading verbatim, which makes for a terrible presentation. If the user explicitly asks for a script, write one, but default to bullet points.
- **Formatting for the audience**: Notes aren't visible to the audience. Don't optimize them for readability by non-presenters.
- **Redundancy with the slide**: If the slide is self-explanatory ("Thank You" with contact info), notes aren't needed. It's fine to leave a slide's notes empty.

### Formatting

`slide.speakerNotes` accepts a markdown string. Prefer bullet lists as the primary structure; bold is useful for emphasis on key phrases the presenter shouldn't skip. See [slide-properties.md](references/slide-properties.md#supported-formatting) for the full list of supported (lists, bold, italic, strikethrough) and unsupported (headings, code blocks, inline code, links) markdown.

## Inspecting Slides Files

There is no dedicated read tool for Slides files yet. Use `use_figma` with read-only scripts for inspection, and `get_screenshot` / `await node.screenshot()` for visual context.

- **Inspect before creating.** Before creating anything, run a read-only `use_figma` to discover what already exists — slides, text, components, naming conventions. The [figma-use](../figma-use/SKILL.md) Section 6 "Inspect first" pattern applies here.
- **`get_metadata` does NOT work on Slides files** — it only supports `figma` (Design) editor type.
- **`console.log()` output is NOT returned** — only the `return` value comes back. Always `return` the data you need.
- **Use `get_screenshot` for visual context** — pass a valid `nodeId` to get a screenshot. You can also use `await node.screenshot()` inline within `use_figma` scripts.

### Quick inspection scripts

**List all slides in the deck:**
```js
const grid = figma.getSlideGrid();
return grid.map((row, rowIdx) =>
  row.map((slide, colIdx) => ({
    id: slide.id,
    name: slide.name,
    row: rowIdx,
    col: colIdx,
    isSkipped: slide.isSkippedSlide,
    speakerNotes: slide.speakerNotes,
  }))
);
```

**Get text content from a specific slide:**
```js
// Read-only text inventory — skip invisible instance interiors for speed.
figma.skipInvisibleInstanceChildren = true;

const slide = figma.getNodeById("TARGET_SLIDE_ID");
// findAllWithCriteria uses an indexed type lookup — much faster than
// findAll(n => n.type === 'TEXT') on slides with many shapes/images.
const textNodes = slide.findAllWithCriteria({ types: ["TEXT"] });
const fontsToLoad = new Set();
for (const t of textNodes) {
  if (t.fontName !== figma.mixed) {
    fontsToLoad.add(JSON.stringify(t.fontName));
  } else {
    const segments = t.getStyledTextSegments(["fontName"]);
    for (const seg of segments) fontsToLoad.add(JSON.stringify(seg.fontName));
  }
}
for (const f of fontsToLoad) {
  await figma.loadFontAsync(JSON.parse(f));
}
return textNodes.map(t => ({
  id: t.id,
  name: t.name,
  characters: t.characters,
  x: t.x,
  y: t.y,
  width: t.width,
  height: t.height,
}));
```

## Reference Docs

Load only the references your task needs:

- [slide-gotchas](references/slide-gotchas.md) — Pitfalls specific to Slides (coordinate offsets, opaque node types, validation workarounds)
- [slide-lifecycle](references/slide-lifecycle.md) — Create, clone, delete, and reorder slides and slide rows
- [slide-grid](references/slide-grid.md) — Work with the slide grid layout (`getSlideGrid`, `setSlideGrid`)
- [slide-content](references/slide-content.md) — Build content within slides (text, shapes, auto-layout — SlideNode extends BaseFrameMixin)
- [slide-properties](references/slide-properties.md) — Slide-specific properties (`speakerNotes`, `isSkippedSlide`, `focusedSlide`, `focusedNode`, `slideThemeId`, `InteractiveSlideElementNode`)
- [slide-design](references/slide-design.md) — Design principles for visually interesting, varied decks (color strategy, typography, layout variety, spatial composition, anti-patterns)
