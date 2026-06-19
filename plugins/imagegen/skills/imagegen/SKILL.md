---
name: imagegen
description: Generate or edit raster images with Codex. Use when a task needs a new photo, illustration, texture, sprite, mockup, transparent-background cutout, transformation, or visual variant from references. Do not use for SVG, vector, code-native graphics, or small edits to an existing editable source format.
---

# Image generation

Use Codex's built-in `image_gen` tool for normal generation and editing. Keep the workflow direct: understand the requested asset, call the tool, inspect the result, and put project-bound output where the project can use it.

## Route the request

Choose `generate` when the user wants a new image or supplies images only as references for subject, style, composition, or mood.

Choose `edit` when the user wants to change an existing image while preserving any part of it. Preserve stated and implied invariants aggressively.

Do not use image generation for:

- SVG or vector artwork that should remain editable as code
- simple diagrams, wireframes, shapes, or icons better made in HTML, CSS, canvas, or SVG
- matching an established repo-native icon, logo, or illustration system
- a small edit when an editable native source already exists

## Use the built-in tool

1. Inspect any local edit target before changing it.
2. For edits where every target has a local path, pass those paths as `referenced_image_paths`.
3. For attached or recent conversation images without local paths, include only the minimum number of recent images needed.
4. For a new image, omit image-reference parameters.
5. State the asset's intended use, composition, constraints, exact text, and required invariants in the prompt.
6. Inspect the result. Iterate with one targeted change at a time when needed.

Do not use the CLI merely for quality, dimensions, batches, or file-path control. For multiple assets or variants, issue one built-in call per distinct deliverable.

The generation result tells Codex where the output was saved. Do not depend on this skill to infer the path, and do not claim the built-in tool accepts an output-path argument.

## Handle output

For preview or brainstorming, show the result inline. It may remain in Codex's generated-image storage.

For a project asset:

1. Copy or move the selected output into the workspace.
2. Use a semantic filename.
3. Do not overwrite an existing asset unless the user requested replacement; otherwise create a versioned sibling.
4. Update consuming project references when the task calls for integration.
5. Report the final workspace path and prompt.

Never leave a project-referenced asset only in Codex's generated-image storage.

## Shape prompts

Preserve a specific user prompt; normalize it without inventing creative requirements. For a broad prompt, add only details that materially improve the result.

Use a compact brief when useful:

```text
Asset type: <where the image will be used>
Primary request: <the user's request>
Input images: <image number and role, when present>
Scene/backdrop: <environment>
Subject: <main subject>
Style/medium: <photo, illustration, 3D, and so on>
Composition/framing: <viewpoint, crop, placement, negative space>
Lighting/mood: <lighting and mood>
Text (verbatim): "<exact text>"
Constraints: <what must remain or must not appear>
```

For edits, repeat `change only X; keep Y unchanged` on each iteration. Label every input image by role. Put literal in-image text in quotes and require verbatim rendering.

Read [prompting.md](references/prompting.md) for difficult composition, identity, typography, or invariant work. Read [sample-prompts.md](references/sample-prompts.md) only when a concrete recipe would help.

## Make a transparent cutout

Use the built-in tool first for a simple opaque subject:

1. Generate the subject on a perfectly flat key-color background that does not occur in the subject. Prefer `#00ff00`; use `#ff00ff` for green subjects.
2. Require a uniform background with no shadow, gradient, texture, floor plane, reflection, or lighting variation.
3. Copy the generated source into the workspace or a temporary workspace directory.
4. Run `scripts/remove_chroma_key.py` from this skill directory with soft matte and despill:

   ```bash
   python <imagegen-skill-dir>/scripts/remove_chroma_key.py \
     --input <source> \
     --out <final.png> \
     --auto-key border \
     --soft-matte \
     --transparent-threshold 12 \
     --opaque-threshold 220 \
     --despill
   ```

5. Verify an alpha channel, transparent corners, plausible subject coverage, and clean edges. Retry once with `--edge-contract 1` for a thin fringe.

Ask before switching to true model-native transparency when the request involves hair, fur, feathers, smoke, glass, liquid, translucency, reflection, or soft shadows, or when chroma-key removal fails. Explain that this path uses the API-backed CLI, requires `OPENAI_API_KEY`, and currently uses `gpt-image-1.5` because `gpt-image-2` does not support `background=transparent`.

## Use the CLI only by explicit choice

Load [the imagegen CLI skill](../imagegen-cli/SKILL.md) only when the user explicitly asks for the CLI, API, model selection, masks, direct file controls, or confirms the true-transparency fallback.

If the built-in tool is unavailable, tell the user that the CLI fallback exists and requires `OPENAI_API_KEY`; proceed only after the user chooses it.
