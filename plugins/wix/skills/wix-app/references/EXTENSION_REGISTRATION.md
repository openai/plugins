
# Extension Registration

`src/extensions.ts` is the single entry point that tells the build system which extensions exist. Without a `.use()` call for an extension, it does not load.

## Registration is automatic via the CLI

For every CLI-supported extension type, `wix generate --params` updates `src/extensions.ts` for you — you do NOT need to write the import or the `.use()` call by hand. Verify the file was updated after each `wix generate` invocation.

## Extension types that require manual registration

| Type | Why manual |
| --- | --- |
| **Backend API** | Astro endpoints under `src/pages/api/` are auto-discovered by the runtime. They do not need to be added to `src/extensions.ts`. |

Every other extension type is wired up automatically by the CLI.

## Manual recovery (when the CLI output drifts)

Edit `src/extensions.ts` directly only when:

- The CLI failed mid-run and left the file out of sync
- A user hand-edited the file and broke the chain
- You're adding a Backend API helper (uncommon)

Each extension file is a default export from `<folder>/<folder>.extension.ts`. In `src/extensions.ts`, import it as a default import using the camelCase of the folder name, then chain `.use(...)`:

```typescript
import { app } from '@wix/astro/builders';
import myPage from './extensions/dashboard/pages/my-page/my-page.extension.ts';
import contactCreated from './extensions/backend/events/contact-created/contact-created.extension.ts';

export default app()
  .use(myPage)
  .use(contactCreated);
```

Re-run `wix generate --params` whenever possible — manual edits drift faster than CLI-generated ones.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Extension not appearing at all | Missing `.use()` call | Re-run `wix generate --params`; if that's not possible, add the import + `.use(<binding>)` |
| "Cannot find module" on build | Wrong import path | Verify the path matches `./extensions/<area>/<folder>/<folder>.extension.ts` relative to `src/` |
| Multiple extensions, only some work | Incomplete chain | Check every extension has both an import and a `.use()` call |
| TypeScript error on `.use()` | Wrong builder method | Ensure the extension file uses the correct builder (e.g., `extensions.dashboardPage()` not `extensions.embeddedScript()`) |
