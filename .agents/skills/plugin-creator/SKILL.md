---
name: plugin-creator
description: Create and scaffold plugin directories for Codex with a required `.codex-plugin/plugin.json`, optional plugin folders/files, and baseline placeholders you can edit before publishing or testing. Use when Codex needs to create a new personal plugin, add optional plugin structure, or generate or update personal or repo-root `.agents/plugins/marketplace.json` entries for plugin ordering and availability metadata.
---

# Plugin Creator

## Quick Start

1. Run the scaffold script:

```bash
  # Plugin names are normalized to lower-case hyphen-case and must be <= 64 chars.
  # The generated folder and plugin.json name are always the same.
# Run from repo root (or replace .agents/... with the absolute path to this SKILL).
# By default creates in ~/plugins/<plugin-name>.
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name>
```

2. Open `<plugin-path>/.codex-plugin/plugin.json` and replace `[TODO: ...]` placeholders.

3. Generate or update the personal marketplace entry when the plugin should appear in Codex UI ordering:

```bash
# Personal marketplace entries default to ~/.agents/plugins/marketplace.json.
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin --with-marketplace
```

If the current Git repo already has `.agents/plugins/marketplace.json` and the user has not said
whether the plugin is personal or shared with their team, ask before generating a marketplace entry.
When they choose the repo marketplace, use:

```bash
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin \
  --path ./plugins \
  --marketplace-path ./.agents/plugins/marketplace.json \
  --with-marketplace
```

4. Generate/adjust optional companion folders as needed:

```bash
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin \
  --path <parent-plugin-directory> \
  --marketplace-path <marketplace-json-path> \
  --with-skills --with-hooks --with-scripts --with-assets --with-mcp --with-apps --with-marketplace
```

`<parent-plugin-directory>` is the directory where the plugin folder `<plugin-name>` will be created (for example `~/code/plugins`).

5. Before treating the plugin as finished, run the readiness check after replacing scaffold placeholders and adding real assets/configuration:

```bash
python3 .agents/skills/plugin-creator/scripts/check_plugin_readiness.py <plugin-path>
```

For marketplace-backed plugins, include the selected marketplace path:

```bash
python3 .agents/skills/plugin-creator/scripts/check_plugin_readiness.py <plugin-path> \
  --marketplace-path <marketplace-json-path>
```

Repo plugins under `<repo-root>/plugins/` are checked against `<repo-root>/.agents/plugins/marketplace.json`
automatically when that marketplace exists.

## What this skill creates

- Default marketplace-backed scaffolds are personal: `~/plugins/<plugin-name>/` plus
  `~/.agents/plugins/marketplace.json`.
- If the current Git repo already has `.agents/plugins/marketplace.json` and the user has not said
  personal vs team, ask which marketplace to update before generating a marketplace entry.
- Creates plugin root at `/<parent-plugin-directory>/<plugin-name>/`.
- Always creates `/<parent-plugin-directory>/<plugin-name>/.codex-plugin/plugin.json`.
- Fills the manifest with the full schema shape, placeholder values, and the complete `interface` section.
- Creates or updates the selected marketplace when `--with-marketplace` is set.
  - If the marketplace file does not exist yet, seed top-level `name` plus `interface.displayName` placeholders before adding the first plugin entry.
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
- Provides `scripts/check_plugin_readiness.py` to audit a completed scaffold before publishing or sharing.

## Marketplace workflow

- Personal plugins use `~/.agents/plugins/marketplace.json`.
- Repo/team plugins use `<repo-root>/.agents/plugins/marketplace.json`.
- Marketplace root metadata supports top-level `name` plus optional `interface.displayName`.
- Treat plugin order in `plugins[]` as render order in Codex. Append new entries unless a user explicitly asks to reorder the list.
- `displayName` belongs inside the marketplace `interface` object, not individual `plugins[]` entries.
- Each generated marketplace entry must include all of:
  - `policy.installation`
  - `policy.authentication`
  - `category`
- Default new entries to:
  - `policy.installation: "AVAILABLE"`
  - `policy.authentication: "ON_INSTALL"`
- Override defaults only when the user explicitly specifies another allowed value.
- Allowed `policy.installation` values:
  - `NOT_AVAILABLE`
  - `AVAILABLE`
  - `INSTALLED_BY_DEFAULT`
- Allowed `policy.authentication` values:
  - `ON_INSTALL`
  - `ON_USE`
- Treat `policy.products` as an override. Omit it unless the user explicitly requests product gating.
- The generated plugin entry shape is:

```json
{
  "name": "plugin-name",
  "source": {
    "source": "local",
    "path": "./plugins/plugin-name"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

- Use `--force` only when intentionally replacing an existing marketplace entry for the same plugin name.
- If the selected marketplace file does not exist yet, create it with top-level `"name"`, an `"interface"` object containing `"displayName"`, and a `plugins` array, then add the new entry.

- For a brand-new marketplace file, the root object should look like:

```json
{
  "name": "[TODO: marketplace-name]",
  "interface": {
    "displayName": "[TODO: Marketplace Display Name]"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": {
        "source": "local",
        "path": "./plugins/plugin-name"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

## Readiness checklist

Run `scripts/check_plugin_readiness.py` before telling the user a plugin is complete. Resolve every
`ERROR`. Treat `WARN` entries as judgment calls; use `--strict-warnings` when the plugin should be
publish-ready with no loose ends.

The readiness check covers:

- No scaffold placeholders remain in non-reference plugin files, including `[TODO: ...]`, example author URLs,
  scaffold keywords, generic TODO/TBD markers, and marketplace placeholder names.
- `.codex-plugin/plugin.json` exists, is valid JSON, uses the normalized folder name, has semantic
  versioning, and keeps required manifest/interface fields in the expected types.
- Manifest paths are relative plugin paths that begin with `./` and point to files or directories
  that actually exist.
- `interface.logo` and `interface.composerIcon` are real non-empty image assets.
- `interface.brandColor` is a valid 6-digit hex color and is not blindly left at the scaffold default.
- `interface.defaultPrompt` contains 1-3 real hero prompts, each 128 characters or fewer.
- Referenced screenshots exist as non-empty PNG image files.
- Referenced `.app.json` and `.mcp.json` files are valid JSON with non-empty `apps` or `mcpServers` objects.
- Every skill `SKILL.md` has frontmatter with `name` and `description`.
- Every skill with a `SKILL.md` has `agents/openai.yaml` metadata, unless the user explicitly wants
  to allow missing metadata and the checker is run with `--allow-missing-openai-yaml`.
- Existing `agents/openai.yaml` files include `interface.display_name` and
  `interface.short_description`; icon paths are checked when present.
- Repo plugins under `<repo-root>/plugins/` are included in `<repo-root>/.agents/plugins/marketplace.json`
  with the correct local source path, policy fields, and category.
- A marketplace passed with `--marketplace-path` has a matching, valid entry for the plugin.

Useful options:

```bash
python3 .agents/skills/plugin-creator/scripts/check_plugin_readiness.py <plugin-path> \
  --marketplace-path ./.agents/plugins/marketplace.json
```

```bash
python3 .agents/skills/plugin-creator/scripts/check_plugin_readiness.py <plugin-path> \
  --allow-missing-openai-yaml
```

When the readiness check reports issues, translate the output into a short user-facing checklist of
remaining work. Do not just paste raw checker output unless the user asks for it. Keep the checklist
actionable and grouped by severity:

```markdown
Remaining before this plugin is ready:
- [ ] Replace placeholder manifest fields: version, description, author, homepage, repository.
- [ ] Add real logo and composer icon assets under `assets/`.
- [ ] Rewrite `interface.defaultPrompt` with 1-3 real starter prompts.
- [ ] Add the plugin to `.agents/plugins/marketplace.json`.

Worth reviewing:
- [ ] Add `agents/openai.yaml` metadata for each skill, or explicitly accept the warning.
```

## Required behavior

- Outer folder name and `plugin.json` `"name"` are always the same normalized plugin name.
- Do not remove required structure; keep `.codex-plugin/plugin.json` present.
- Keep manifest values as placeholders until a human or follow-up step explicitly fills them.
- After scaffolding, point the user to the readiness checklist and command printed by
  `create_basic_plugin.py`.
- Do not call a plugin finished until `scripts/check_plugin_readiness.py` has no `ERROR` findings, or
  until the user explicitly accepts the remaining errors.
- When readiness issues remain, provide the user a concise checklist of the remaining items to finish,
  grouped into blocking errors and review-worthy warnings.
- If creating files inside an existing plugin path, use `--force` only when overwrite is intentional.
- Preserve any existing marketplace `interface.displayName`.
- When generating marketplace entries, always write `policy.installation`, `policy.authentication`, and `category` even if their values are defaults.
- Add `policy.products` only when the user explicitly asks for that override.
- Keep marketplace `source.path` relative to the selected marketplace root as `./plugins/<plugin-name>`.
- When the workflow created or updated a marketplace-backed plugin, end the final user-facing
  response with a short Codex app handoff. Say `To view this in the Codex app:` and write
  `View <normalized plugin name>` and `Share <normalized plugin name>` as Markdown links, not raw
  URLs or code spans.
- The View deeplink uses `codex://plugins/<normalized plugin name>?marketplacePath=<absolute marketplace.json path>`.
  The Share deeplink uses the same URL with `&mode=share`.
- Replace the placeholders with the real normalized plugin name and absolute `marketplace.json`
  path from the scaffolded plugin. URL-encode the path segment and query value when needed.
- Do not add `pluginName` or `hostId` query parameters to these deeplinks. Codex derives both after
  the user clicks the link.
- Do not emit the `View <normalized plugin name>` or `Share <normalized plugin name>` links when no marketplace entry was
  created or updated.

## Reference to exact spec sample

For the exact canonical sample JSON for both plugin manifests and marketplace entries, use:

- `references/plugin-json-spec.md`

## Validation

After editing `SKILL.md`, run:

```bash
python3 <path-to-skill-creator>/scripts/quick_validate.py .agents/skills/plugin-creator
```
