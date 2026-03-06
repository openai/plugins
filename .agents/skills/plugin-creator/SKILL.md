---
name: plugin-creator
description: Create and scaffold plugin directories for Codex with a required `.codex-plugin/plugin.json`, optional plugin folders/files, and baseline placeholders you can edit before publishing or testing.
---

# Plugin Creator

## Quick Start

1. Run the scaffold script:

```bash
  # Plugin names are normalized to lower-case hyphen-case and must be <= 64 chars.
  # The generated folder and plugin.json name are always the same.
# Run from repo root (or replace .agents/... with the absolute path to this SKILL).
# By default creates in <repo_root>/plugins/<plugin-name>.
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name>
```

2. Open `<plugin-path>/.codex-plugin/plugin.json` and replace `[TODO: ...]` placeholders.

3. Generate/adjust optional companion folders as needed:

```bash
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin --path <parent-plugin-directory> \
  --with-skills --with-hooks --with-scripts --with-assets --with-mcp --with-apps
```

`<parent-plugin-directory>` is the directory where the plugin folder `<plugin-name>` will be created (for example `~/code/plugins`).

## What this skill creates

- Creates plugin root at `/<parent-plugin-directory>/<plugin-name>/`.
- Always creates `/<parent-plugin-directory>/<plugin-name>/.codex-plugin/plugin.json`.
- Fills the manifest with the full schema shape, placeholder values, and the complete `interface` section.
- `<plugin-name>` is normalized using skill-creator naming rules:
  - `My Plugin` → `my-plugin`
  - `My--Plugin` → `my-plugin`
  - underscores, spaces, and punctuation are converted to `-`
  - result is lower-case hyphen-delimited with consecutive hyphens collapsed
- Supports optional creation of:
  - `skills/`
  - `hooks/`
  - `scripts/`
  - `assets/`
  - `.mcp.json`
  - `.app.json`

## Required behavior

- Outer folder name and `plugin.json` `"name"` are always the same normalized plugin name.
- Do not remove required structure; keep `.codex-plugin/plugin.json` present.
- Keep manifest values as placeholders until a human or follow-up step explicitly fills them.
- If creating files inside an existing plugin path, use `--force` only when overwrite is intentional.

## Reference to exact spec sample

For the exact canonical sample JSON, including the full `interface` block, use:

- `references/plugin-json-spec.md`

## Validation

After editing `SKILL.md`, run:

```bash
python3 <path-to-skill-creator>/scripts/quick_validate.py .agents/skills/plugin-creator
```
