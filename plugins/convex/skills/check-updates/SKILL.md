---
name: check-updates
description: "Check the CURRENT Convex app's pinned components against the latest recommended versions and offer to upgrade them — e.g. the passkey auth component's new email-first sign-in. TRIGGER when the user runs /check-updates or $check-updates, asks 'are my components up to date', 'any updates', 'upgrade auth', 'upgrade my components', or wants the newest features after a quickstart. Applies each upgrade behind a build gate (verify-or-revert) with the user's consent."
license: Apache-2.0
---

# Check + apply component updates

Run from the app's project root (where `package.json` lives — the `convex-app/`
subdir for a quickstart). Detect stale components against the anteater registry:

```bash
curl -fsSL https://basic-anteater-667.convex.site/check-updates.mjs -o /tmp/cu.mjs && node /tmp/cu.mjs
```

- **`COMPONENTS_UP_TO_DATE`** → tell the user everything's current. Done.
- **`COMPONENTS_STALE=<n>`** + a JSON array → for each entry, summarize for the user:
  the component, `installed → current`, the `summary` (what's new), and whether it's
  `breaking`. Then **ASK before changing anything** — "Upgrade `<name>` to get
  <summary>? [y/n]". Never upgrade without an explicit yes.

On a yes, apply that entry's `migration`:
1. **Install** the new ref (`migration.install`) with the project's package manager.
2. **Apply `migration.steps` in order** — the call-site changes. Read the existing code
   first; make the minimal change each step describes. Delegate any `convex/` edits to
   the `convex-expert` skill/subagent.
3. **GATE — verify or revert.** Run every command in `migration.gate` (e.g.
   `pnpm exec tsc --noEmit`, `pnpm exec next build`). If ANY fails, **revert**
   (`git checkout -- .`, or reinstall the old ref) and tell the user it didn't apply
   cleanly — never leave the app half-migrated.
4. **Smoke** — give the user the `migration.smoke` check to run (the runtime behavior the
   build gate can't prove), e.g. register → sign out → sign in by the same email.

Rules:
- **`breaking: true`** needs extra care: confirm explicitly, snapshot first (commit/branch),
  and if the steps aren't mechanical, ask the user rather than guessing.
- **Don't auto-publish.** If the app is already live on `*.convex.app` / a custom domain,
  the upgrade only reaches the live site on re-publish — confirm before re-deploying
  (no surprise downtime on a live domain).
- One component at a time; gate each before the next.
