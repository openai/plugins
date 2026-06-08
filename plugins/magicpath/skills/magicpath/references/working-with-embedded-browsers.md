# Working With Embedded Browsers

Use this when the host exposes an embedded browser, such as Codex's Browser capability, and the user is creating, editing, reviewing, or selecting work on a MagicPath project canvas.

Keep the embedded browser on the project canvas. Do not navigate it to individual component previews unless the user explicitly asks.

## Open a Project Canvas

Do not use `view <projectId>` when you want an embedded browser URL; `view` opens the operating-system browser. Get the project URL instead:

```bash
npx -y magicpath-ai share <projectId> -o json
```

Navigate the embedded browser to the returned `url`.

## New Project Flow

1. Create the project:

```bash
npx -y magicpath-ai create-project --name "Name" -o json
```

2. Run `share <project.id> -o json`.
3. Open the returned project URL in the embedded browser.
4. Start canvas authoring with `code start`.
5. Keep the browser on that project while submitting and reviewing.

If the embedded browser redirects to sign-in or home, tell the user to sign in there, then navigate back to the same project URL. CLI auth and browser auth are separate.

## Existing Project Flow

If the user refers to the open project, run:

```bash
npx -y magicpath-ai active-project -o json
```

If one project is returned, open its shared URL if it is not already visible. If multiple or none are returned, ask which project.

Use:

```bash
npx -y magicpath-ai selection -o json
```

when the user refers to selected canvas components or images.

## Quiet Operations

Do not navigate the browser for background commands like `info`, `whoami`, `list-projects`, `list-components`, `list-teams`, `search`, `list-themes`, `get-theme`, `inspect`, `add`, or polling build status.

Return a component share link with `share <generatedName> -o json` when the user asks for a link. Navigate to that component only when they ask to open or view that specific design.
