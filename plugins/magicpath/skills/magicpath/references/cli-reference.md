# MagicPath CLI Reference

Run commands through `npx -y magicpath-ai`. Prefer `-o json` for structured output and `-y` for non-interactive installs.

## Auth and Context

```bash
npx -y magicpath-ai info -o json
npx -y magicpath-ai login
npx -y magicpath-ai whoami -o json
```

`info` returns auth state, user context, teams, projects, and CLI version.

## Discovery

```bash
npx -y magicpath-ai search "query" -o json
npx -y magicpath-ai search "query" --team "Acme" -o json
npx -y magicpath-ai search "query" --personal -o json
npx -y magicpath-ai list-projects -o json
npx -y magicpath-ai list-components <projectId> -o json
```

Useful flags: `--limit`, `--offset`, `--after`, `--sort-by name|createdAt`, `--order asc|desc`, `--team <nameOrId>`, `--personal`, and `--created-by <userId>`.

Results may include `ownerType`, `ownerName`, `createdBy`, `lastEditedBy`, `generatedName`, and `previewImageUrl`.

## Teams and People

```bash
npx -y magicpath-ai list-teams -o json
npx -y magicpath-ai list-members --team "Acme" -o json
```

Use member ids with `list-components <projectId> --created-by <userId> -o json`.

## Themes

```bash
npx -y magicpath-ai list-themes -o json
npx -y magicpath-ai list-themes --team "Acme" -o json
npx -y magicpath-ai get-theme <id-or-name> -o json
npx -y magicpath-ai get-theme "Brand" --team "Acme" -o json
```

Theme output can include light/dark CSS variables, default theme, fonts, and a natural-language styling prompt.

## Inspect, Install, Share, and View

```bash
npx -y magicpath-ai inspect <generatedName> -o json
npx -y magicpath-ai add <generatedName> -y -o json
npx -y magicpath-ai add <generatedName> --dry-run -o json
npx -y magicpath-ai share <generatedName> -o json
npx -y magicpath-ai share <projectId> -o json
npx -y magicpath-ai view <generatedName>
npx -y magicpath-ai view <projectId>
```

`inspect` reads source without writing files. `add` installs React/TypeScript source into the current app. `share` returns a URL without browser navigation. `view` opens the browser and should not be parallelized.

## Canvas Context and Images

```bash
npx -y magicpath-ai selection -o json
npx -y magicpath-ai active-project -o json
npx -y magicpath-ai image list <projectId> -o json
npx -y magicpath-ai image add <projectId> ./image.png -o json
```

Use `selection` for selected components/images. Use `active-project` when the user says "this project" or "the project I have open."

## Create Projects

```bash
npx -y magicpath-ai create-project --name "My Project" -o json
npx -y magicpath-ai create-project --name "My Project" --team "Acme" -o json
```

If the user has teams and does not say personal or team, ask which workspace before creating.

## Author or Edit Canvas Components

```bash
npx -y magicpath-ai code start --project <projectId> --dir <workdir> --name "Name" --width <px> --height <px> -o json
npx -y magicpath-ai code start --component <componentId> --dir <workdir> -o json
npx -y magicpath-ai code start --component <componentId> --revision <revisionId> --dir <workdir> -o json
npx -y magicpath-ai code context <componentId> --dir <workdir> -o json
npx -y magicpath-ai code submit --dir <workdir> --width <px> --height <px> --wait -o json
npx -y magicpath-ai code status <jobId> -o json
```

`code start` begins a stateful authoring session and writes scaffold files. `code submit` publishes edits back to the canvas. `code context` is read-only.

Editable files in a code workdir are limited to `src/App.tsx`, `src/index.css`, `src/components/generated/**`, and temporary `assets/**`.
