---
name: magicpath
description: Use when the user mentions MagicPath, designs, UI components, themes, canvas selections, or repo-to-canvas UI work; run magicpath-ai to search, inspect, install, or author components.
allowed-tools: Bash(npx -y magicpath-ai *)
user-invocable: true
---

# MagicPath

MagicPath is a canvas and component platform. Use this skill when the user mentions MagicPath, designs, UI components, themes/design systems, team projects, selected canvas items, or bringing local/repository UI into a MagicPath canvas.

Always run MagicPath CLI commands as:

```bash
npx -y magicpath-ai <command> -o json
```

Use JSON output for data-returning commands and `-y` for non-interactive installs.

## First Step

Run:

```bash
npx -y magicpath-ai info -o json
```

If the user is not authenticated, run:

```bash
npx -y magicpath-ai login
npx -y magicpath-ai whoami -o json
```

## Pick the Workflow

- Find or install a MagicPath component: search/list, confirm the right component, inspect it, then add/adapt it.
- Work with the current canvas: use `selection -o json` for selected components/images, or `active-project -o json` for the open project.
- Use team work: run `list-teams -o json`, then pass `--team "<nameOrId>"` to project, search, theme, or member commands.
- Use a theme/design system: `list-themes -o json`, then `get-theme <id-or-name> -o json`; apply CSS variables, fonts, and prompt guidance in the target app.
- Create or edit canvas components from code: use `code start`, edit only allowed files, then `code submit --wait`.
- Bring an existing repo UI into MagicPath: follow [Working with repositories](references/working-with-repositories.md).
- Keep a MagicPath project open inside Codex's Browser when doing canvas work: follow [Working with embedded browsers](references/working-with-embedded-browsers.md).

## Find and Confirm Components

1. If the user refers to a selected design/component/image, run `selection -o json`.
2. If the user refers to the project they have open, run `active-project -o json`.
3. Otherwise search or browse:

```bash
npx -y magicpath-ai search "button" -o json
npx -y magicpath-ai list-projects -o json
npx -y magicpath-ai list-components <projectId> -o json
```

Search/list results include `generatedName`, project context, owner fields, and often `previewImageUrl`. Use previews when visual context matters.

Stop and ask for confirmation before installing or editing unless the user gave an exact `generatedName`, selected canvas item, or component/project id.

## Install Into an App

Use this when MagicPath is the source and the user's app is the destination.

1. Inspect first:

```bash
npx -y magicpath-ai inspect <generatedName> -o json
```

2. Read the target code before installing. Understand current props, callbacks, validation, layout, data flow, styling system, and accessibility behavior.
3. For React/TypeScript apps, install:

```bash
npx -y magicpath-ai add <generatedName> -y -o json
```

4. Import and render the installed component using the returned `importStatement` and `usage`.
5. Adapt the installed source in `src/components/magicpath/<name>/`:
   - Replace static text and mock data with props or real project data.
   - Wire events, loading, error, empty, disabled, focus, and keyboard states.
   - Make fixed dimensions responsive.
   - Preserve existing behavior when replacing an existing component.
   - Match the app's styling and state-management patterns.

Do not run `add` just to read code. Use `inspect` for read-only source. For non-JS projects, inspect and translate the design into the target framework instead of running `add`.

## Create or Edit Canvas Components

Use this when the MagicPath canvas is the destination.

```bash
npx -y magicpath-ai code start --project <projectId> --dir <workdir> --name "Component Name" --width <px> --height <px> -o json
npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json
npx -y magicpath-ai code submit --dir <workdir> --wait -o json
```

Rules for `code` work:

- Run `code start` before writing files so the canvas shows the pending work.
- Edit only `src/App.tsx`, `src/index.css`, `src/components/generated/**`, and temporary image assets under `assets/**`.
- Usually leave `src/App.tsx` alone except for the theme value.
- Put real implementation in `src/components/generated/<Name>.tsx`; split larger pieces into sibling files there.
- Use Tailwind v4 through `src/index.css`; do not add `tailwind.config.js`.
- Keep output responsive, centered, and free of device/browser mockups unless explicitly requested.
- Build one screen per component. For related multi-view flows, use local React state inside one component; for independent screens, create separate components in separate workdirs.
- Make interactive surfaces actually interactive: controlled inputs, real handlers, toggles, tabs, dialogs, form validation, hover/focus/disabled states, and useful transitions.
- If selected canvas images are returned by `code start`, use the downloaded `assetPath`, not the short-lived `accessUrl`.
- If `code submit` fails, fix only allowed files and resubmit.

`code context` is read-only. Do not use it as the submit path.

## Teams, People, and Ownership

- `list-teams -o json`: discover teams/workspaces.
- `list-members --team "<team>" -o json`: resolve people to user ids.
- `list-projects --team "<team>" -o json`: see team projects only.
- `list-components <projectId> --created-by <userId> -o json`: find work by a person in a team project.

Personal projects are private to their owner unless shared. Do not search another person's personal work; search team projects instead.

## Project and Share Links

Use `share` when you need a URL without opening a browser:

```bash
npx -y magicpath-ai share <generatedName> -o json
npx -y magicpath-ai share <projectId> -o json
```

Use `view` only when intentionally opening the OS browser:

```bash
npx -y magicpath-ai view <generatedName>
npx -y magicpath-ai view <projectId>
```

Never run `view` commands in parallel.

## References

- [CLI reference](references/cli-reference.md)
- [Working with repositories](references/working-with-repositories.md)
- [Working with embedded browsers](references/working-with-embedded-browsers.md)
