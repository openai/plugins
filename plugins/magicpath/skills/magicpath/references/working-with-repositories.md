# Working With Repositories

Use this when the user wants existing UI from a local path or Git repository recreated on the MagicPath canvas. This is the inverse of `add`/`inspect`: the source is the repo, and the destination is a new or edited MagicPath canvas component.

Do not use `add`, `inspect`, or `code context` for this workflow.

## 1. Get the Code

- Local repo: read the path directly after confirming the target if ambiguous.
- Online repo: clone shallowly into scratch space, separate from the MagicPath `--dir`.
- Private repo: ask for access or a local checkout if clone fails; do not guess credentials.
- Monorepo: identify the relevant app/package before reading deeply.

## 2. Read the Design Foundation

Before building, inspect:

- Framework and dependencies from `package.json`.
- Global CSS such as `globals.css`, `index.css`, `app.css`, or `styles/**`.
- Design tokens: CSS variables, theme files, `tailwind.config.*`, color/font/radius/shadow values.
- Font loading strategy.
- Light/dark theme handling.
- Shared primitives such as `components/ui`, icons, buttons, cards, and layout shells.

## 3. Resolve the Target

For one component, trace the component file, child imports, constants/data, CSS, icons, assets, and the parent layout that gives it size and position.

For a page or whole project, identify the route/page entry and walk the component tree. If the user did not specify the page, ask one short question and stop.

Use one MagicPath component for one cohesive interactive screen or flow. Use separate components/workdirs for genuinely independent screens.

## 4. Plan the Canvas Build

- Choose useful `--width` and `--height` values, such as `1440x900` for desktop or `390x844` for mobile.
- Translate the repo's styling into React + Tailwind v4 in MagicPath's generated structure.
- Convert CSS variables into `src/index.css` and reference them from classes or CSS.
- Copy real image assets into `<workdir>/assets/`; do not hotlink repo blob URLs or inline base64.
- For Vue, Svelte, Angular, SwiftUI, or plain HTML, reproduce the visual output and behavior in React rather than copying framework syntax.

## 5. Build and Submit

Start before editing so the canvas shows a pending component:

```bash
npx -y magicpath-ai code start --project <projectId> --dir <workdir> --name "Name" --width <px> --height <px> -o json
```

Then edit only:

- `src/App.tsx`
- `src/index.css`
- `src/components/generated/**`
- `assets/**`

Submit and wait:

```bash
npx -y magicpath-ai code submit --dir <workdir> --width <px> --height <px> --wait -o json
```

If build diagnostics return, fix allowed files and resubmit. Do not start a new component to avoid a fixable failure.

## Fidelity Rules

- Match the source UI's colors, spacing, radii, typography, shadows, and behavior.
- Keep the component responsive and centered.
- Do not add phone/browser/device frames unless explicitly requested.
- Use local mock data for backend-driven content.
- Wire real state for tabs, drawers, forms, menus, active nav items, and multi-step flows.
- Keep a single frame for one screen; use internal state for navigation within a cohesive flow.
