---
name: sharepoint-powerpoint
description: Create, edit, restyle, and review PowerPoint `.pptx` files fetched from SharePoint, with emphasis on style preservation, slide cloning, theme-aware updates, and rendered visual QA. Use when the user wants reliable slide edits that should match an existing deck's design language.
---

# SharePoint PowerPoint

## Overview

Use this skill for `.pptx` work that starts from SharePoint and where visual fidelity matters. Treat PowerPoint edits as both content edits and design-preservation work. Prefer reusing the deck's own structures over creating generic new slides.

## When To Use

- Add, remove, reorder, or rewrite slides in an existing SharePoint-hosted deck.
- Insert title, section, agenda, or summary slides that should match the deck style.
- Update text in existing slides while preserving formatting.
- Inspect layouts, masters, shapes, and theme cues before changing a presentation.
- Render and visually QA slides before uploading the revised deck back to SharePoint when tooling permits.

## Core Workflow

1. Determine whether the request is content-only or style-sensitive.
2. Use the SharePoint skill to locate the exact deck and fetch the raw `.pptx` with `fetch(download_raw_file=true)`.
3. Inspect the deck before editing:
   - slide count and order
   - available slide masters and layouts
   - placeholder availability
   - representative slides for the requested slide type
   - shape structure on the representative slide
4. Choose the safest edit strategy in this order:
   - clone a representative existing slide and edit only the text-bearing shapes
   - insert slides from a matching source deck or exported single-slide deck
   - use a native layout only when the deck exposes usable layouts and placeholders
   - fall back to manual text boxes only as a last resort
5. Preserve the existing deck language:
   - reuse layout and theme when possible
   - preserve geometry, spacing, alignment, and density
   - preserve shape hierarchy and non-text objects unless the user asks to change them
6. Perform visual QA:
   - render the edited slide and adjacent slides if a render path exists
   - compare the new slide to its neighbors for background, spacing, hierarchy, and density
7. Return to SharePoint only for upload with `update_file` after local QA.
8. If style fidelity cannot be validated, stop and state that clearly.

## Style Rules

- Prefer cloning over creating.
- Prefer targeted text replacement over rebuilding the slide.
- If the deck has only one layout, a `DEFAULT` layout, or missing placeholders, assume template constraints.
- Do not treat a content-correct slide as complete until visual consistency has been checked.
- If you must use manual text boxes, inspect a representative slide first and copy:
  - text box bounds
  - paragraph alignment
  - font sizes and weights
  - theme colors
  - vertical spacing

## Tool Guidance

- Use `python-pptx` for structural edits and inspection.
- Use `lxml` and OOXML-level operations when `python-pptx` is too weak for safe slide cloning.
- Prefer PowerPoint-native export or LibreOffice-based rendering for visual QA when available.
- If no rendering tool exists, say that verification is content-level only and treat style-sensitive work as blocked unless the user accepts the risk.

## Environment Reality

Current local minimum:

- `python-pptx`
- `lxml`
- `Pillow`

Recommended for reliable QA:

- Microsoft PowerPoint native export/rendering
- or LibreOffice plus Poppler for slide-image generation

## SharePoint Routing

When a SharePoint task targets a `.pptx` and style adoption matters:

1. Use the SharePoint skill to locate and fetch the file.
2. Use this SharePoint PowerPoint skill for the actual edit.
3. Return to the SharePoint connector only for upload after local QA.

## Blocking Conditions

Stop and report limitations when:

- no clone path exists for a style-sensitive edit
- no render path exists for visual QA
- the deck template is constrained and the only remaining option is a generic low-fidelity slide insertion

## Bundled Assets

This plugin does not currently bundle PowerPoint helper scripts.

If local inspection, cloning, or rendering helpers are unavailable, prefer conservative edits and state the gap explicitly rather than implying a script-backed workflow exists.
