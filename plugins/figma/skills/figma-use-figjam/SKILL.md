---
name: figma-use-figjam
description: "This skill helps agents use Figma's use_figma MCP tool in the FigJam context. Can be used alongside figma-use which has foundational context for using the use_figma tool."
disable-model-invocation: false
---

# use_figma — Figma Plugin API Skill for FigJam

This skill contains FigJam-specific context for the `use_figma` MCP tool. The [figma-use](../figma-use/SKILL.md) skill provides foundational context for plugin API execution via MCP as well as the full Figma plugin API for more advanced use-cases that are not described here.

**Always pass `skillNames: "figma-use-figjam"` when calling `use_figma` for FigJam operations.** This is a logging parameter used to track skill usage — it does not affect execution.

## Reference Docs

- [plan-board-content](references/plan-board-content.md) - Read this for any board content request — board template, retro, brainstorm, ice breaker, meeting board, scaffold
  - Covers planning of generated board content, including sequential outline, sections, intents, and hierarchical text
  - Delegates to other references for specific API details
- [create-section](references/create-section.md) — Create and configure FigJam sections (sizing, naming, colors, content visibility, organizing nodes, column layouts)
- [create-sticky](references/create-sticky.md) — Create and configure FigJam sticky notes (colors, sizing, text, author visibility, batch creation)
- [create-connector](references/create-connector.md) — Create and configure FigJam connectors (endpoints, arrows, line types, labels, colors, diagram wiring)
- [create-text](references/create-text.md) — Create and configure FigJam text nodes (font loading, preset fonts and colors, sizing, lists, mind map operations)
- [position-figjam-nodes](references/position-figjam-nodes.md) — Position, size, and reparent nodes on the canvas (including within sections)
- [create-shape-with-text](references/create-shape-with-text.md) — Create and configure FigJam shapes with embedded text (shape types, color presets, sizing to fit text, diagram layouts)
- [create-code-block](references/create-code-block.md) — Create and configure FigJam code block nodes (languages, syntax highlighting, positioning, embedding in sections)
- [create-table](references/create-table.md) — Create and configure FigJam tables (rows, columns, cell text, color presets, resizing)
- [edit-text](references/edit-text.md) — Edit existing text nodes (font loading, styled ranges, find/replace, FigJam Charcoal default color)
- [create-label](references/create-label.md) — Create and configure FigJam label nodes (small numbered/lettered circle callout markers, sequences, positioning)
- [batch-modify](references/batch-modify.md) — Patterns for modifying many existing nodes at once (bulk style changes, repositioning, property updates)
