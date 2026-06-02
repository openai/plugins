# Setup

Runs once, immediately after the user approves the plan and Discovery has written `.wix/site.json`. This phase's domain is: install the apps the loaded packs declare, pull the Wix env, run `npm install`, and patch `site.json` with `siteId` + `appId`. Run flow (dispatch timing, background handles, waits, batching, transitions) is owned by `BUILD.md` (Setup is its first run-step).

This article covers the **astro (supported) entry path** — Steps 1–5 below + "npm install recovery". The orchestrator scaffolds a fresh Astro project via `scaffold.sh` in `BUILD.md` run-step 0; astro is the only frontend built on disk today.

The **Existing project flow (Path B)** at the bottom is **retired** — non-astro (custom) frontends route to the not-available-yet stub (`references/custom/INSTRUCTIONS.md`) instead of running E1–E6. That section is kept as a historical reference only; see its banner.

This path assumes DISCOVERY.md's CLI-auth pre-flight has already passed (the foreground check that runs before any `AskUserQuestion`).

Mode/track routing (which path runs) is owned by `PLAN.md` § "Frontend-mode routing". Steps 1–5 below are the astro business steps.

---

## Step 1 — Read the scaffolded project config (siteId + appId)

**Do not** speculatively `Read <project-slug>/wix.config.json` before the scaffold exists — the speculative read returns `File does not exist` on every fast-Q&A run (the file isn't there yet), emits a `[MED]` anomaly in the trace, and costs 3–5 s of round-trip + recovery thinking.

Once the scaffolded project exists, read `<project-slug>/wix.config.json` and extract:
- `siteId` — the site id passed as `--site` to `npx @wix/cli@latest token` and embedded in every install body + as the `wix-site-id` header on every site-scoped REST call. Hold it in orchestrator session scratch.
- `appId` — the project's appId. Hold it in session scratch (it goes into the SDK's `createClient` inputs in later steps).

**Before `cd`, capture the current working directory as `<site-root>` and hold it in session scratch.** This is where Discovery's `init-site-json.mjs` wrote the slim `.wix/site.json` snapshot. The orchestrator is the **sole** reader/writer of that file; no subagent or downstream script reads it during the run. Hold `<site-root>` as an absolute path so the `cd` into the scaffold subdir below does not lose it.

`cd` into `<project-slug>/` so all subsequent file ops + shell calls (`npm`, `npx @wix/cli@latest env pull`) are relative to the project root.

---

## Step 2 — Patch site.json with siteId + appId

Discovery wrote `<site-root>/.wix/site.json` with `brand`, `frontend`, and `verticals`. Setup's only addition is patching `siteId` and `appId` in. This is a one-shot in-process JSON edit:

1. `Read <site-root>/.wix/site.json` (absolute path — `<site-root>` was captured in Step 1, before the `cd` into the scaffold).
2. Add the two top-level fields (`siteId`, `appId`) using the values held in session scratch.
3. `Write` the updated file back to the same absolute path.

The file's purpose at this point is **observability + resume detection** — no subagent reads it; the orchestrator is the sole reader/writer. Six lines of edit doesn't justify a script.

---

## Step 3 — Invoke the `wix-manage` skill

> **Default — just invoke it; do not deliberate.** **Always** invoke `Skill(name="wix-manage")` here. It is near-instant, and it is the *only* thing that both publishes `<wix-manage-root>` into scratch **and loads the recipe files into context** (which Step 4's installs and the whole Seed phase then reuse — SEED.md reads recipes relative to `<wix-manage-root>` and explicitly does **not** re-invoke). **Knowing the `wix-manage` directory path from an earlier `ls`/discovery is NOT a reason to skip the invocation** — a raw filesystem path is not the same as the skill being loaded (the recipes aren't in context). Do not weigh invoke-vs-skip; invoke. The only exception is the Missing-skill fallback below.

App installation is delegated to `wix-manage`. Use the harness's skill-invocation primitive — in Claude Code that's `Skill(name="wix-manage")`; other harnesses provide an analogous mechanism. **Do not** hardcode a tool-call snippet here; the prose instruction "Invoke the `wix-manage` skill" is the contract, and the harness owns the mechanics. This mirrors `wix-app/SKILL.md:241` ("Invoke the `wix-design-system` skill") and keeps the skill agent-agnostic.

After invocation, `wix-manage`'s SKILL.md is in context with absolute paths to its `references/<topic>/` files. Read its app-install recipe by absolute path:

```
Read <wix-manage-root>/references/app-installation/install-wix-apps.md
```

> **Sequencing note.** Within Step 3, the `Skill` invocation must precede the `Read install-wix-apps.md` (the Read needs the absolute path that `wix-manage`'s SKILL.md publishes).

The recipe's Step 2 documents the body shape every Step 4 install call will use:

```
tenant: { tenantType: "SITE", id: "<siteId>" }
appInstance: { appDefId: "<pack.apps[N].appDefId>" }
```

Endpoint: `POST https://www.wixapis.com/apps-installer-service/v1/app-instance/install`.

> **Recipe call shape.** Every loaded `wix-manage` recipe is authored in `curl` form. Build each call with the headers documented in `references/shared/AUTHENTICATION.md` (`Authorization: Bearer $TOKEN` + `wix-site-id: $SITE_ID` + `Content-Type: application/json`). The recipe's URL, method, and body are the source of truth — do not re-derive them.

> **Missing-skill fallback (only when the `Skill` primitive fails).** This applies **only** when the skill-invocation primitive itself is unavailable — i.e. `wix-manage` is not installed in the current harness and the `Skill(name="wix-manage")` call errors. It is **not** a "use the path you already found" shortcut: a known directory path never justifies skipping the invocation (see the default above). When the invocation genuinely fails, fall back to the install **body shape** documented above (it is REST-shaped and stable; the recipe wraps it but does not transform it), and note the missing skill in the run digest. Do not silently substitute — the canonical entry point is `wix-manage`.

---

## Step 4 — One concurrent batch

> Fire 4a + 4b + 4c as a single concurrent batch — see `PLAN.md` § "Batching discipline".

The dispatch contains three operations:

### 4a. App installs — one `curl` per `pack.apps[*]` (business track, frontend-blind)

This is **business-track** work: the install body is identical per `pack.apps[*]` regardless of the `frontend`/template — it registers Wix apps against the Site and never reads which frontend will consume them.

Mint the site-scoped REST token once and cache it for the rest of the run, then iterate every loaded pack (top-level + transitive via `requires:`) and fire one `curl` per entry in the pack's `apps:` array:

```bash
SITE_ID="<siteId>"
TOKEN=$(npx @wix/cli@latest token --site "$SITE_ID")  # once; cache in scratch for the run

# per-pack iteration; one curl per pack.apps[*]:
curl -sS -X POST "https://www.wixapis.com/apps-installer-service/v1/app-instance/install" \
  -H "Authorization: Bearer $TOKEN" \
  -H "wix-site-id: $SITE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant":      { "tenantType": "SITE", "id": "'"$SITE_ID"'" },
    "appInstance": { "appDefId": "<pack.apps[N].appDefId>", "enabled": true }
  }'
```

Use `npx @wix/cli@latest token …` (not bare `wix token …`): `@wix/cli` may not be globally installed in every harness, and `npx` resolves to the project-local copy that scaffold just produced. The first invocation auto-fetches the CLI (~3–5 s) if missing; subsequent calls are instant.

A 200 response confirms the install. On 401/403, retry the same call once with the cached token per the recovery ladder in `references/shared/AUTHENTICATION.md` — do **not** re-mint (the token is byte-identical for the run); if it still fails, surface the response body — a persistent 401 usually means the CLI session expired and `wix login` is required.

**Packs with `apps: []` (e.g. `cms`, `ecom`):** skip the curl but record a phase entry as `{phase: "app-install-<pack>", status: "skipped", notes: "no app required for this pack"}` — the explicit skipped entry keeps run observability unambiguous.

**Packs with `disabled: true` (today: `gift-cards`):** the pack still loads and contributes to the resolved set, but its `apps:` array is empty by design (the user opts in via the dashboard later). No curl. Same `skipped` phase entry as above.

### 4b. `npx @wix/cli@latest env pull --json`

Foreground shell, ~5 s. Writes `WIX_CLIENT_ID` to `.env.local`. Idempotent. Skipping this causes `Missing environment variable WIX_CLIENT_ID` build failures in downstream phases.

> **Always pass `--json`.** Without it the CLI renders an interactive spinner; captured through the tool's non-TTY pipe, every animation frame lands as a separate line of ANSI escapes (`\x1b[2K\x1b[1A…⠙ Pulling…`) and bloats the context for zero signal. `--json` selects the CLI's non-interactive render-to-string path (one clean `{"success": true}` line), and the skill doesn't parse this command's output anyway — it only needs `.env.local` on disk.

### 4c. Dispatch background `npm install`

Run `npm install` as a backgrounded shell. Capture the handle as `npm_handle` and the path to `<npm-tempfile>`. Hold both in session scratch.

```bash
npm install --no-fund --no-audit --legacy-peer-deps <package-set> \
  2> <npm-tempfile>
# dispatched with run_in_background: true; capture as npm_handle
```

`<package-set>` is composed from the resolved pack set (loaded packs from Setup Step 1, including transitives via `requires:`):

| Always | Add when pack is loaded |
|---|---|
| `@wix/sdk tailwindcss @tailwindcss/vite` | — |
| | **stores** → `@wix/stores` |
| | **ecom** (loaded directly or as `requires:` of stores) → `@wix/ecom @wix/redirects` |
| | **blog** → `@wix/blog @wix/ricos @astrojs/rss @astrojs/sitemap` |
| | **forms** → `@wix/forms` |
| | **cms** → `@wix/data @wix/wix-data-items-sdk @wix/essentials` |
| | **gift-cards** → (none — disabled-by-default pack ships no Astro-time imports) |

Concrete example for the most common case (stores prompt; resolved set = stores + ecom + gift-cards + cms):
```bash
npm install --no-fund --no-audit --legacy-peer-deps \
  @wix/sdk @wix/stores @wix/ecom @wix/redirects \
  @wix/data @wix/wix-data-items-sdk @wix/essentials \
  tailwindcss @tailwindcss/vite \
  2> <npm-tempfile>
```

> **Why three packages for cms?** `@wix/data` exposes collections / permissions / backups namespaces; the actual `items` API (used by every CMS page for queries) lives in `@wix/wix-data-items-sdk` since `@wix/data` 1.0.448 dropped the `items` re-export (see [astro/cms/CMS_FOUNDATIONS.md](./astro/cms/CMS_FOUNDATIONS.md) § "Import note"). `@wix/essentials` is required for `auth.elevate` — every CMS page elevates queries to bypass per-collection permission checks. Shipping only `@wix/data` produces `'items' is not exported by '@wix/data'` at `astro build`; shipping without `@wix/essentials` produces `Cannot find module '@wix/essentials'` at SSR time.

Per pre-flight S0.2, `pnpm install` fails against the `@wix/cli` template — use `npm install --legacy-peer-deps`.

**Why per-pack packages live here, not in pack frontmatter:** `references/verticals/_schema.md` is scoped to Discovery; it deliberately excludes `packages:` to keep that schema small. The install set is owned by SETUP.md instead — the lookup table above is the contract. **If you skip the per-pack additions and ship only the always-on three, `astro build` fails at Wave 5 with `Rollup failed to resolve import "@wix/stores"` (or whichever pack-side package the run depends on) and Setup's win on the foreground wall is paid back many times over in a recovery cycle.** When this happens, the build retries after an in-flight `npm install @wix/stores @wix/ecom`, costing ~30 s.

Do not invent packages beyond the table above. If a future vertical needs a new package, extend the table here.

---

## Step 5 — Transition to Seed

Setup does not print a summary sentence. Setup ends once the Final-scan checks pass.

---

## npm install recovery

Invoked when `npm_handle` returns non-zero. The handle is dispatched in Step 4c above; the orchestrator waits on it at the seed gate (`BUILD.md`) and runs this recovery ladder there if it failed.

If the background `npm install` fails or hangs:

1. **Foreground retry** with `npm install --no-fund --no-audit --legacy-peer-deps <packages>` (90 s timeout). If that hangs, add `--prefer-offline`; if still hanging, run `npm cache clean --force` and retry once more.
2. **Last resort:** ask the user to run `npm install --legacy-peer-deps` manually and report back. Do not silently substitute pnpm/yarn — pre-flight S0.2 confirmed pnpm fails against the `@wix/cli` template.

The package set is the union of `@wix/sdk tailwindcss @tailwindcss/vite` (always) plus each loaded pack's frontmatter `packages:` array. The current pack frontmatter does not declare `packages:` blocks — vertical packs are discovery-only at this phase, so the install set is just the always-on three. Do not invent package names.

---

## Final scan (MANDATORY)

Before transitioning to SEED.md in Step 5, verify: `siteId` + `appId` are in `.wix/site.json` (extracted from `wix.config.json`, both non-empty), the cached token mints, every loaded pack with `apps:` got a 200 OK (or a `skipped` phase entry for empty `apps:`), `.env.local` contains `WIX_CLIENT_ID`, and `npm_handle` was dispatched. If any check fails, surface the failure verbatim instead of transitioning to SEED.md.

---

## Existing project flow (Path B) — RETIRED, historical reference only

> **⚠️ This flow is no longer dispatched.** Non-astro (custom) frontends now route to the **not-available-yet stub** (`references/custom/INSTRUCTIONS.md`); the conductor does not run E1–E6 (`PLAN.md` § "Custom (non-astro) frontends — not available yet", `DISCOVERY.md` § "Custom (non-astro) — not available yet"). The E1–E6 mechanics below — especially the **E4 SDK-wiring recipe** — are retained as the **historical reference / closest prior art** for the eventual custom authoring track (`references/custom/INSTRUCTIONS.md` § "Intended future shape" step 3). Do **not** dispatch this flow; it is documentation, not a live path.

This path used to run when the user already had a working frontend on disk (Claude Design output, Vite/React app, hand-coded `index.html`) and wanted to **connect it to Wix Headless** for hosting + Business Solutions.

**Differences from Path A:**

| Aspect | Path A (new project) | Path B (existing project) |
|---|---|---|
| Project creation | `npm create @wix/new@latest headless` (via `scaffold.sh`) — fresh Astro blank template | `npm create @wix/new@latest init` — wraps the existing project, leaves source untouched |
| Frontend | Generated by Designer + Components + Pages subagents | Already exists; orchestrator does **not** generate UI |
| Seeders / Designer / Pages / BUILD | Run | **Skipped** — there is no Astro structure to populate |
| App installs | From inferred vertical packs | From a quick **project analysis** (see E2) — only apps the existing project actually needs |
| SDK wiring into source | N/A (subagents write Astro + SDK calls from scratch) | **Required (E4)** — edit the project's existing source files in place |
| Build / release | `npx @wix/cli@latest build` + `release` via `release.sh` | `npx @wix/cli@latest release` directly — **no build step**; existing `index.html` is published as-is |
| Entry file | `src/pages/index.astro` (Astro convention) | **Must be `index.html`** at the configured `outputDirectory` |

### Step E1 — Init (replaces scaffold)

`cd` into the existing project directory. Run, foreground (it's interactive-ish but non-blocking with `--yes`-style defaults; capture stdout):

```bash
npm create @wix/new@latest init
```

> Same package + invoker as Path A's scaffold (`npm create @wix/new@latest headless`), only the subcommand differs: **`init` for existing projects, `headless` for new projects**. Do not combine them (`… headless init` is a known regression).

This creates a Wix Site + Headless Project (App) connected to that Site, and writes `wix.config.json` in the project root:

```jsonc
{
  "projectType": "Site",
  "appId": "16511cb9-3d3a-4371-a04a-bcc176ae5d50",   // SDK clientId
  "siteId": "90b8c952-a7f9-4d79-a2c0-b0ec3e1c1434",  // siteId for every REST call this session
  "site": {
    "outputDirectory": "./site"  // edit to "./" if the entry file is at project root
  }
}
```

**Required follow-ups before continuing:**

1. **Entry file must be `index.html`.** If the project's entry is `index.htm`, `main.html`, etc., either rename to `index.html` or ask the user to confirm renaming. Wix Headless hosting serves `index.html` as the site root; anything else 404s.
2. **`site.outputDirectory` must point at the directory containing `index.html`.** If `index.html` is at the project root, use the `Edit` tool on `wix.config.json` to set `"outputDirectory": "./"`. Default is `"./site"` which assumes a build output directory.
3. Extract `siteId` and `appId` from `wix.config.json` and hold in session scratch (same role as Path A: `siteId` is the `wix-site-id` header on every REST call).
4. Capture `{ phase: "init", seconds, started, ended }` in `run.json.phases[]`.

Recovery ladder:
- Auth error → surface `"Run \`npx @wix/cli@latest login\` and retry."` and stop (same as Path A; full ladder in `references/shared/AUTHENTICATION.md`).
- `wix.config.json` already exists → skip E1, continue to E2.
- Network / unknown → surface stderr to the user.

### Step E2 — Analyze the project to decide which apps to install

The existing-project flow does NOT use vertical-pack inference from the user prompt. Instead, **read the project files** to decide which Wix Business Solutions are needed. Quick heuristic table:

| Signal in source files | Pack(s) to install |
|---|---|
| Mentions of "event", "wedding", "RSVP", "guests", "ceremony" | `events` (if pack exists), else CMS-backed RSVP via `cms` |
| `<form>` tags, "Contact us", "Get in touch", email collection | `forms` |
| Product listings, "buy", "$", "add to cart", price tags | `stores` (transitively pulls `ecom`, `gift-cards`) |
| Article / blog content, post listings | `blog` |
| Booking, appointments, calendar | `bookings` (if pack exists) |
| Restaurant menu, dishes | `restaurants` (if pack exists) |
| Always | `cms` (any user-editable content) |

Read `index.html` and any top-level source files (`*.jsx`, `*.tsx`, `*.html`, `*.js`) to look for these signals. Cap reading at the top 5 source files by size — don't grovel.

> If unsure between two packs, ask the user with `AskUserQuestion`. Don't install everything "just in case" — every app install adds clutter to the user's dashboard.

### Step E3 — Install apps

For each pack identified in E2, fire the install `curl` per § Step 4a above — same `tenant` / `appInstance` body, same headers, same recovery ladder (delegated to `wix-manage` per Step 3). Capture `{ phase: "app-install-<pack>", seconds }` per install.

**Skip the rest of Path A's Step 4 batch:** no `env pull` for a pure-static site (only needed if E4 below adds SDK code that reads `WIX_CLIENT_ID` at build time; if so, run `env pull` then), **no `npm install`** (the existing project manages its own deps), **no `seed-utilities.sh`** (it is frontend-track project prep for a skill-scaffolded project; integrate mode has no such project and skips Seed entirely, so the orchestrator never calls it in this flow). `.wix/site.json` itself **was** written by Discovery's "After Approval" step with `frontend: "user-provided"` — that snapshot stays for observability; do not write it again here.

### Step E4 — SDK wiring

> **The custom frontend track is the long-term home for this step.** When the custom track is built, this SDK-wiring recipe becomes per-pack wiring guides under `references/custom/<pack>/…` that inject `@wix/sdk` calls into the user's existing files (additive-only) — see `references/custom/INSTRUCTIONS.md` § "Intended future shape" step 3. Until that lands, this inline recipe is the **historical reference** (the flow itself is retired — non-astro frontends route to the stub, see the banner at the top of this section).

Installing apps in E3 only registers them against the Site — the existing frontend still ignores them until SDK calls are wired in. For each app installed in E3, find the matching feature surface in the project's source files (the same surfaces E2 detected) and wire its SDK calls inline.

1. Add `@wix/sdk` + the pack's packages (from § Step 4c's lookup table above) to the project's `package.json` (`npm init -y` first if absent), then run the project's install command with `--no-fund --no-audit --legacy-peer-deps`.
2. Edit the source files in place. Follow call patterns from `<SKILL_ROOT>/references/<pack>/INSTRUCTIONS.md` (translate Astro idioms → the project's framework; SDK calls themselves are framework-agnostic). Initialize the client once per file:

   ```js
   import { createClient, OAuthStrategy } from "@wix/sdk";
   const wix = createClient({
     modules: { /* pack modules */ },
     auth: OAuthStrategy({ clientId: "<appId from wix.config.json>" }),
   });
   ```

   **Always inline the `appId` literal from `wix.config.json`.** No env vars, no `import.meta.env`, no `window.__WIX_CLIENT_ID__` — read `wix.config.json` once and paste the appId string into every `createClient` call. Keeps the static-site case working with no build step.

Capture `{ phase: "sdk-wiring-<pack>", seconds }` per pack.

### Step E5 — Release (no build)

**Do NOT run `release.sh`** in this flow — `release.sh` runs `npx @wix/cli@latest build` first, and there is nothing to build. The existing project's `index.html` and its sibling assets already sit at the configured `site.outputDirectory`; Wix just needs to publish that directory as-is. Calling `build` here either no-ops (wastes ~5–15 s) or fails if the project has no Astro/Vite config the Wix CLI knows how to invoke.

Run release directly:

```bash
npx @wix/cli@latest release
```

Capture stdout. The CLI prints `Site published on <url>` on success — extract that URL (same parser logic as `release.sh` uses):

```bash
sed -nE 's/.*Site published on ([^[:space:]]+).*/\1/p'
```

Capture `{ phase: "release", seconds }` around the call. No `{ phase: "build" }` entry in `run.json` for this flow.

Auth-failure recovery: same as `release.sh` — if stderr mentions login, surface `"Run \`npx @wix/cli@latest login\` and retry."` and stop. Transient errors (`ECONNRESET`, `temporarily unavailable`, etc.) — retry up to 3 times with `attempt * 5` second backoff, mirroring `release.sh`.

> **If the project needs a client build** (Vite, React, Webpack, etc.), run the project's own build command manually (e.g. `npm run build`) before `npx @wix/cli@latest release`, and make sure `site.outputDirectory` points at the build output. Do not use `wix build`.

### Step E6 — Final message

Emit **exactly two URLs**, both copy-pasted verbatim from tool output / config (URL discipline from `SKILL.md` § "URL discipline" applies here too):

1. **Production URL** — bold heading / link at the top. The exact string from `Site published on <url>` in Step E5's stdout. Do not retype or modify.
2. **Dashboard URL** — `https://manage.wix.com/dashboard/<siteId>` where `<siteId>` is the value from `wix.config.json`.

Skip Path A's perf one-liner buckets that didn't run. For Path B the perf line is:

> `Connected in <Nm Ss> — init <n>s · app-install <n>s · sdk-wiring <n>s · release <n>s`

`sdk-wiring` aggregates every `sdk-wiring-<pack>` phase from E4.

Write a `project`-type memory entry capturing brand (from `wix.config.json`'s implicit project name or ask), siteId, installed apps, and **phase: `connected-existing`** so future sessions know this is an existing-project shell, not a wix-headless-scaffolded build.
