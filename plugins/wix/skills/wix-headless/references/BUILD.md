# Build — the post-approval conductor

Opened the moment the user approves the plan in `DISCOVERY.md`. This file owns the **execution flow** — Setup → design-system bridge → Seed → Components → Pages → Build → Release: every subagent dispatch, background handle, wait/gate, and the imagery gates. Read it top to bottom from the approval point.

The **pre-approval** flow (mode routing, the Discovery questions, the plan + approval gate, and the background scaffold + Designer dispatches that hide latency) is in `PLAN.md`; it hands off here on approval. Three cross-cutting rules referenced below — **Two tracks**, **Batching discipline**, and **User-facing output** — also live in `PLAN.md`.

## Phase axis

Each phase belongs to one of the two tracks (`PLAN.md` § "Two tracks"). All phases are background (`bg`); this table is the *what* and *which track*, the sections below are the *when*.

| Phase | Track | Tier | What | When (bg) |
|---|---|---|---|---|
| **Phase 1 — Seed** | business | Fast | Per-pack seeders → orchestrator collects `seeded` map in scratch | Seed wave |
| **Phase 2 — Design System** | frontend | Default | **Designer** returns tokens + brand-voice JSON (no files); **Composer** writes the 6 files (`global.css`, `astro.config.mjs`, `Layout`, `Nav`, `Footer`, `index`) by substituting into pinned skeletons | Designer: BUILD entry (run-step 0) · Composer: Setup-window bridge |
| **Image Phase 1 — Decorative** | frontend | Fast | Hero/about/page-header decoratives | Seed wave (imagery-gated) |
| **Phase 3 — Components** | frontend | Default | Per-vertical React islands, styling contract inlined per prompt | Step 4.5 |
| **Phase 4 — Pages** | frontend | Default | Per-vertical routes; each agent writes its routes once with both visual design and live data queries | Step 7 |
| **Image Phase 2 — Entity** | business | Fast | Product / blog / CMS item images PATCHed onto Wix entities | Step 4.5 (imagery-gated) |

> **Set the model tier on every dispatch.** Tier policy lives in `SKILL.md` § "Subagent model tier" — apply by table lookup. The tier is selected via the dispatch primitive's model parameter, not the prompt; if you omit it, Default-tier roles silently run under-powered on the orchestrator's default model.

## The run from approval (Setup → Release)

The user just approved; `init-site-json.mjs` wrote the slim `.wix/site.json`. **Nothing is dispatched yet** — the funnel intentionally dispatched nothing so it could present the plan fast. Start by firing the two background jobs the rest of the run needs, then run Setup.

### 0. Dispatch scaffold + Designer (background, immediately on entry)

Fire both as one concurrent batch (`PLAN.md` § "Batching discipline") — they are independent:
- **Scaffold** — `scaffold.sh <slug> "<brand>" --frontend <value>` (background, capture `scaffold_handle` + its stderr tempfile). Slug derivation + the command shape are `DISCOVERY.md` § "After Q1". `npm install` is **not** chained here (Setup Step 4c dispatches it). The stderr tempfile is for **post-hoc error inspection only** (read it *if* the scaffold reports a failure) — it is **not** a progress file to poll.
- **Designer** — background, capture `designer_handle`. Dispatch with **Instruction file = `<SKILL_ROOT>/references/DESIGN_SYSTEM.md`** (the subagent opens it — **do not Read it in the orchestrator**, per `SKILL.md` § "Path resolution"). Inline Discovery's aesthetic craft held in scratch: brand, aesthetic direction, palette, type, mood, page color strategy. Judgment-only (~10–15 s; JSON `data.designTokens` + `data.shell`, no files). Do **not** pass application inputs (packs, nav links) — those go to the Composer.

The Designer's ~13 s overlaps the scaffold's ~23 s. Setup waits on `scaffold_handle` at Step 1; the bridge (step 2) waits on `designer_handle`.

### 1. Setup Step 1 (foreground)

Apply `SETUP.md` Step 1 only: wait `scaffold_handle` (load `wix-manage` in the same batch), then patch `site.json` with `siteId`/`appId`. **Do not run Setup Step 4 (the app-install batch) yet** — it goes in run-step 2 below, alongside the bridge.

> **How to wait — await the notification, never sleep-poll** (`PLAN.md` § "Concurrency vocabulary" → "Wait (gate)"). "Wait `scaffold_handle`" means await the harness's background-task **completion notification**. Do **not** run a `sleep`/poll loop against the scaffold's stdout/stderr/output file — that blocks the turn for the whole scaffold wall (~20–30 s, longer if you over-sleep) and pushes back the run-step 2 super-batch, landing the Composer late. A late Composer is the longest-pole regression called out at run-step 2 (~60–90 s of wall lost). Burn zero orchestrator time here: the notification is the only signal you need.

### 2. Setup Step 4 batch **+** design-system bridge — ONE concurrent super-batch

**Pin:** Setup Step 4 (business) and the design-system bridge (frontend) are independent and MUST go out as **one** assistant message (`PLAN.md` § "Batching discipline" — no narration between the tool calls, or the batch splits and the Composer starts late). `designer_handle` has been running since run-step 0, so it has returned by now: the bridge's wait→emit→dispatch collapses into two direct calls in the batch.

**Dispatch block — emit all of the following as siblings in ONE assistant message; no text between the tool calls:**

*business track (frontend-blind — `SETUP.md` owns the recipes/package set):*
1. `Bash` × N — app installs, one curl per `pack.apps[*]` → `SETUP.md` § Step 4a.
2. `Bash` — `npx @wix/cli@latest env pull --json` → `SETUP.md` § Step 4b (the `--json` flag suppresses the interactive spinner that otherwise bloats context).
3. `Bash` (background) — `npm install …`, capture `npm_handle` + its stderr tempfile → package set in `SETUP.md` § Step 4c.

*frontend track (Designer tokens already in scratch):*
4. `Bash` — emit tokens: pipe the Designer's `data.designTokens` JSON into `emit-design-tokens.mjs` (reads tokens from **stdin**, project dir as **`argv[2]`**; empty stdin → exits 2 `stdin was empty — pass the designTokens JSON object` and the bridge stalls). Quoted heredoc so the JSON survives unchanged. Writes `.wix/design-tokens.css` + `.wix/site.d.ts`; keep `designTokens` + `shell` in scratch for the Composer prompt.

   ```bash
   node <SKILL_ROOT>/scripts/emit-design-tokens.mjs "<project-dir>" <<'TOKENS'
   { ...paste the Designer's data.designTokens JSON object here, verbatim from scratch... }
   TOKENS
   ```
5. `Agent` (background) — Composer, capture `composer_handle`. Dispatch with **Instruction file = `<SKILL_ROOT>/references/astro/COMPOSE.md`** (the subagent opens it — **do not Read it in the orchestrator**; it is 14 KB of subagent-only substitution how-to, and reading it here just bloats the dispatch turn you're composing). Inline: tokens + shell + brand + nav links + packs. **SKIP** (record `{phase: "compose", status: "skipped"}`) if `frontend !== "astro"` (defensive — custom frontends never reach `BUILD.md`).

> **Rationale — do not re-derive.** The two tracks are independent: the Composer's only inputs are the Designer's tokens (ready from run-step 0) and the verified scaffold (ready at Setup Step 1) — neither depends on seeders, app installs, env, or npm. App installs / `env pull` / `npm install` are business-track work the bridge has zero dependency on. Firing the bridge alongside the Step 4 batch lets its ~80–160 s authoring wall absorb into Setup + the whole seed window; firing it *after* the Step 4 batch — or worse, in the seed wave — makes it start late and land as a fresh longest pole that ends *after* the seeders (~60–90 s of Composer wall lost in past runs). The Composer self-retries its pre-write scaffold reads if the scaffold is somehow still in flight (`COMPOSE.md` § "Pre-write").

### 3. Seed wave (Wave 3) — business track + co-scheduled frontend prep

**One concurrent batch** (§ "Wave 3" below for the detailed dispatch): `seed-utilities.sh --template <…>` (frontend project prep) + per-pack seeders (background) + Image Phase 1 Decorative (background, gated — § "Imagery gates"). Apply `SEED.md` for the recipe map + seeder prompt template. **No design-system dispatch here** — `composer_handle` is already running from the bridge in step 2.

### 4. Seed gate

Wait on the seeders + `composer_handle` + `npm_handle`; once `composer_handle` returns, run the post-Composer Layout-import verify; aggregate seeder returns into the `seeded` scratch map. Run `patch-decorative-slots.mjs` only when `imagery === "ai-generated"` and Image Phase 1 Decorative returned; otherwise skip and record `{phase: "decorative-slot-patch", status: "skipped"}`. Because the Composer started back in Setup, by the time the seeders return its wall is typically already complete — so the design-system phase no longer extends the seed window.

### 5. Continue

**Step 4.5** (Phase 3 Components + Image Phase 2) → **Step 7** (Phase 4 Pages) → **Build & Release** → **Final message** — all detailed below.

## Imagery gates

The `imagery` value (`"ai-generated"` | `"themed-blocks"`, captured in `DISCOVERY.md` Q2.5, default `"themed-blocks"`) gates **both** image phases. The conductor owns the gate; the step files describe what each image scope does when it runs.

- **Image Phase 1 — Decorative** (Wave-3 batch). Dispatch the `image-phase-1-decorative` subagent (`<SKILL_ROOT>/references/images/INSTRUCTIONS.md`) **only when `imagery === "ai-generated"`**. When `"themed-blocks"` (default): do **not** dispatch — decorative slots render as solid color blocks via the Composer-emitted decorative-slot CSS (color blocks tokenised against the Designer's palette); record `{phase: "image-phase-1-decorative", status: "skipped", notes: "themed-blocks mode"}` and **skip the post-seed `patch-decorative-slots.mjs`** too (`{phase: "decorative-slot-patch", status: "skipped"}`). Dispatching it regardless wastes ~140–175 s + 0.3–0.5 Wix AI credits.
- **Image Phase 2 — Entity** (Step 4.5 batch). Same gate — dispatch only on `ai-generated`; on `themed-blocks` skip and record `{phase: "image-phase-2-entity", status: "skipped"}`. Detailed dispatch + the hard build gate are in § "Step 4.5" and § "Wait: Phase 4 → Build" below.

---

## Wave 3 — Seed + frontend prep + Image Phase 1

The seed-wave dispatch list (the run's step 3). No design-system dispatch here — `composer_handle` is already running from the Setup-window bridge. Launch as **one concurrent batch** (`PLAN.md` § "Batching discipline"):

- `seed-utilities.sh --template astro` — frontend-track project prep (idempotent), run from the project dir. Apply `SEED.md` § "Pre-batch".
- Per-pack seed subagents (background) — apply `SEED.md` for the recipe map + seeder prompt template.
- Image Phase 1 Decorative (background) — `<SKILL_ROOT>/references/images/INSTRUCTIONS.md`, scope `image-phase-1-decorative` — **only when `imagery === "ai-generated"`** (§ "Imagery gates").

The **seed gate** that follows (wait on seeders + `composer_handle` + `npm_handle`, Layout-import verify, aggregate `seeded`, optional decorative patch) is run-step 4 above — then continue to **Step 4.5** below.

### Subagent prompt template

See `SEED.md` § "Subagent prompt template" for the base fields (Instruction file, Phase instruction, Scope, Project directory, siteId, Auth, Brand context). Phase 3 Components and Phase 4 Pages dispatches additionally inline the full styling-contract JSON, and Phase 3 / Phase 4 / Image Phase 2 inline the relevant pack-specific slice from the orchestrator's `seeded` scratch as JSON. Subagents do NOT read `.wix/site.json` during the run.

**`Instruction file` must point to one of these vertical instruction files:**
- `<SKILL_ROOT>/references/stores/INSTRUCTIONS.md` — Phase 3 Components + Phase 4 Pages
- `<SKILL_ROOT>/references/ecom/INSTRUCTIONS.md` — Phase 3 Components (cart/checkout — passive, required by stores)
- `<SKILL_ROOT>/references/cms/INSTRUCTIONS.md` — Phase 4 CMS Pages
- `<SKILL_ROOT>/references/blog/INSTRUCTIONS.md` — Phase 3 Components + Phase 4 Pages
- `<SKILL_ROOT>/references/forms/INSTRUCTIONS.md` — Phase 3 Components + Phase 4 Pages
- `<SKILL_ROOT>/references/gift-cards/INSTRUCTIONS.md` — Phase 3 Components + Phase 4 Pages (passive/dashboard-gated)
- `<SKILL_ROOT>/references/images/INSTRUCTIONS.md` — `image-phase-1-decorative` + `image-phase-2-entity`
- `<SKILL_ROOT>/references/DESIGN_SYSTEM.md` — Phase 2 Designer (design spec, JSON only); `<SKILL_ROOT>/references/astro/COMPOSE.md` — Phase 2 Composer (writes the 6 design-system files)
- `<SKILL_ROOT>/references/astro/designer/INSTRUCTIONS.md` — **page-design specification** (not a separately-dispatched scope). The merged Phase 4 `pages` scopes above apply this for the visual-design spec of their routes (layout, contract classes, decorative slots, per-scope structure for `home`/`static`/`store-pages`/`blog-pages`/`contact-page`) while writing live SDK data in the same pass. There is no separate placeholder-writing page-designer dispatch — single-write merged (see § "Step 7 Dispatch").

For **image subagents**, the prompt additionally includes: page list (for decorative brief), entity types to cover (products, about-content, etc.).

Phase 3 Components subagents (Step 4.5) additionally receive the full styling-contract JSON inlined in their prompt — they do not read `.wix/design-tokens.css` + `.wix/site.d.ts` from disk. See § "Styling contract coordination" below.

### Subagent return

Every subagent returns a structured JSON block at the end of its run, per `references/shared/RETURN_CONTRACT.md`. The orchestrator parses each return as it arrives.

---

## Step 4.5 — Phase 3 Components + Image Phase 2 Entity (one concurrent batch, all background)

**Gate (from the seed gate, run-step 4):** the `seeded` map is populated and the Composer has returned. Verify **both** `.wix/design-tokens.css` **and** `.wix/site.d.ts` exist on disk, and the Composer wrote `src/layouts/Layout.astro` + `src/styles/global.css` — the `cp` pre-batch and Layout imports below depend on them. If either design-tokens file is missing, do not dispatch Step 4.5 — surface the missing path and stop. (`patch-decorative-slots.mjs` was already run or skipped at the seed gate per § "4. Seed gate" — do not re-run it here.)

Read `.wix/design-tokens.css` + `.wix/site.d.ts` once.

**Pre-batch (same message, before subagent dispatches):** copy the per-pack component-CSS templates into the project. This is a deterministic `cp` — the templates are static and use direct `var(--token)` references against the standard designer vocabulary, so no subagent is needed to author them. The Phase 3 Components subagents below write only `.tsx` React islands; this step writes the matching `src/styles/components-<pack>.css`. **If you skip this `cp` step, `astro build` fails at Step 8 with `Could not resolve "../styles/components-<pack>.css"` from `src/layouts/Layout.astro`** — the Composer's Layout imports those files unconditionally for every pack that declares `components`. If the Phase 3 subagents write only `.tsx`, the build falls back to slow orchestrator recovery (`cp` + manual rewrite to strip `@apply`).

For each loaded pack whose vertical INSTRUCTIONS declares a `components` scope (today: `stores`, `ecom`, `blog`, `forms`, `gift-cards`), copy the template:

```bash
for pack in <loaded packs with components>; do
  cp "<SKILL_ROOT>/references/astro/templates/$pack/components-$pack.css" \
     "src/styles/components-$pack.css"
done
```

Record `{ phase: "copy-component-css", packs: [...], seconds }` in `run.json`. Idempotent — re-running overwrites identical content. Packs without a `components-<pack>.css` template (today: `cms` — SSR inline, no component CSS) are skipped silently.

**Also pre-copy the Phase-3 utility templates in the same `cp` batch.** Each vertical's INSTRUCTIONS declares utility files under "Pre-copied by the orchestrator (do NOT write these yourself)" that its `components` scope only *imports* — the conductor must put them on disk before dispatch so no subagent races to author them. Today that is the **stores** pack:

```bash
# only if the stores pack is loaded
cp "<SKILL_ROOT>/references/astro/templates/stores/back-in-stock.ts" "src/utils/back-in-stock.ts"
```

If you skip this, the `components` subagent falls back to writing `src/utils/back-in-stock.ts` itself, and on multi-pack runs two scopes can race the same path (`File has not been read yet` / `modified since read`). Record `{ phase: "copy-utils", scope: "components", files: [...] }`.

Then dispatch in a single concurrent batch:

1. **One Phase 3 Components subagent per loaded pack** that declares `components`. Each prompt carries:
   - All standard fields (see "Subagent prompt template" above)
   - The **full styling-contract JSON inlined** — not a file path
   - A note: *"`src/styles/components-<pack>.css` is already on disk (copied from the skill template by the orchestrator). Do NOT write that file — write only `.tsx` islands and any `.astro` shells in your scope."*

2. **One Image Phase 2 Entity subagent** — imagery-gated (§ "Imagery gates"): not dispatched on `themed-blocks` (default). On `ai-generated`, when `seeded` scratch has entities, dispatch it — the prompt inlines the relevant `seeded.<pack>` slice (entity IDs + names + descriptions) + brand context (no disk reads). Instruction file: `<SKILL_ROOT>/references/images/INSTRUCTIONS.md` § "Scope: image-phase-2-entity".

The Phase 3 Components group is **background** regardless. Image Phase 2 (when dispatched) is also background — it starts immediately and continues running through Step 7 dispatch with no polling.

**Why Image Phase 2 lives here, not in Step 7.** Image Phase 2 only depends on entity IDs/names/descriptions + brand context (all inlined in its prompt). It does not read or write anything Phase 3 Components or Phase 4 Pages produce — its PATCH/PUT targets are Wix-side entities (`stores/v3/products`, `wix-data/v2/items`, `blog/v3/posts`). Launching it here lets it overlap entirely with Phase 3 (and often Phase 4 too) instead of becoming a post-Phase-4 tail blocker.

---

## Wait: Phase 3 → Step 7

Phase 3 Components must complete before Step 7 dispatches — Phase 4 Pages mount the islands Components wrote, so launching early causes missing-island build failures. (Image Phase 2, if dispatched, keeps running through Phase 4 and is gated only at Build.)

**Data carry-forward:** Phase 4 subagents receive the relevant `seeded.<vertical>` slice inlined from scratch — **Stores** → `seeded.stores` (`productIds`, slugs, categories), **CMS** → `seeded.cms` (`collectionIds`, `itemIds`). The orchestrator built the `seeded` map at the seed gate — do not re-dispatch seeders. Subagents do NOT read `.wix/site.json`.

---

## Step 7 Dispatch — Phase 4 (Pages)

### Pre-batch (same message, before subagent dispatches)

Pre-copy the Phase-4 utility templates each pack's INSTRUCTIONS declares under "Pre-copied by the orchestrator (do NOT write these yourself)" — the conductor puts them on disk so no `pages-*` scope authors them. Today that is the **stores** pack's category helper:

```bash
# only if the stores pack is loaded
cp "<SKILL_ROOT>/references/astro/templates/stores/categories.ts" "src/utils/categories.ts"
```

`categories.ts` is a static, brand-agnostic SDK wrapper. **It must be pre-copied, not written by a subagent.** `pages-categories`, `pages-products`, and `pages-home-and-nav` all *import* it; if it isn't on disk, two of those concurrently-dispatched scopes each fall back to writing it and race the same path (`File has not been read yet`). Record `{ phase: "copy-utils", scope: "pages", files: ["src/utils/categories.ts"] }`.

### Concurrent batch

For each loaded pack's `pages`:
- One Phase 4 subagent per scope — **background**. Each writes its routes ONCE with both visual design and live data queries (the merged design+wire model). Earlier flows split this into a placeholder-writing dispatch followed by a page-rewrite dispatch; that double-write was eliminated.

> **Shared-shell patchers serialize within the Phase 4 batch; non-overlapping scopes run concurrently.** Scopes that patch a shared shell file at a marker — `src/components/Navigation.astro` (`<!-- nav:links -->`, CartBadge) or `src/pages/index.astro` (`<!-- home:<pack> -->`, featured grid) — read-modify-write a file another scope also patches. Dispatching two such patchers concurrently trips the harness staleness guard (`File has been modified since read`). **Dispatch the shell-patching scopes one at a time** — launch one, wait for its return, then launch the next — so each sees the previous one's marker insertion. See the ecommerce-run example below: `home-and-nav` and `gift-cards pages` serialize (both touch `Navigation.astro` + `index.astro`); the private-file scopes (`product-pages`, `category-pages`, `cart-checkout`, `cms-pages`) stay in the concurrent batch. The serialized chain runs alongside the concurrent batch, not after it.

> **Image Phase 2 is NOT dispatched here.** When it was launched at Step 4.5 (i.e. on an `ai-generated` run), it has been running concurrent with Phase 3 + Phase 4 and is typically finished or near-finished by the time Step 7 fires; the Step 8 hard gate waits for it before invoking `release.sh`. **On a `themed-blocks` run (the default), Image Phase 2 was not dispatched at all** — no gate wait, no images, the build runs as soon as Phase 4 finishes.

### Example (ecommerce run — stores pack contributes 4 Phase 4 scopes + cms pack 1)

Five subagents launched concurrently:

1. **product-pages** — `products/index.astro`, `products/[slug].astro`, `ProductCard.astro`
2. **category-pages** — `category/[slug].astro`, `CategoryRail.astro` (imports the pre-copied `utils/categories.ts`)
3. **cart-checkout** — `cart.astro`, `thank-you.astro`
4. **home-and-nav** — patch `index.astro` product grid + `Navigation.astro` (CartBadge mount + Shop submenu insert at `<!-- nav:links -->`)
5. **cms-pages** — wire About + FAQ to live `@wix/data` queries

Scopes 1, 2, 3, 5 own their files exclusively → one concurrent background batch. `home-and-nav` (scope 4) patches the shared `Navigation.astro` + `index.astro` shells; on a run that also loads gift-cards, the gift-cards `pages` scope patches the same two shells — so those two serialize against each other per the shared-shell rule above. `product-pages` and `home-and-nav` import `CategoryRail.astro` and the pre-copied `utils/categories.ts`, but those imports resolve at build time (Step 8), not write time, so they don't force ordering against `category-pages`.

### Phase 4 prompt additions

```
Scope: <scope name from pack.pages[*].name>
Files to own (absolute paths): <from pack.pages[*].files>
Phase 1 Seed data: <the relevant seeded.<vertical> slice inlined here as JSON, from the orchestrator's scratch>
Design tokens: the styling-contract JSON is inlined above; .wix/design-tokens.css + .wix/site.d.ts are also on disk (already imported by the build)
```

Each scope subagent writes its `.astro` files directly with live SDK queries, wires up analytics events, and mounts the React islands written by Phase 3 Components.

Scope subagents MUST NOT:
- Modify files outside their declared scope
- Modify CSS (`global.css` owned by the Composer; `components-<pack>.css` owned by Phase 3 Components)
- Modify React islands (owned by Phase 3 Components)

---

## Wait: Phase 4 → Build

Wait on all Step 7 Phase 4 Pages subagents to return, then:

- **If `imagery === "ai-generated"`** (Step 4.5 dispatched `image-phase-2-entity`): wait for that handle to return, with a hard **120 s timeout** from when Phase 4 Pages finish. On timeout, proceed to Build and record `{code: "IMAGE_PHASE_2_TIMEOUT"}` in `run.json`. Image Phase 2 has been running in parallel since Step 4.5, so under that dispatch model the timeout rarely fires.
- **If `imagery === "themed-blocks"`** (Step 4.5 skipped `image-phase-2-entity`): no wait — proceed to Build immediately.

Skipping this gate on an ai-generated run ships previews with no product images and leaves `run.json` recording `image-phase-2-entity` as `"in_progress"`.

Also ensure the background `npm install` (`npm_handle` from `SETUP.md` Step 4c, waited on at the seed gate) completed successfully before Build. On non-zero exit, follow the recovery ladder in `SETUP.md` § "npm install recovery".

---

## Subagent rate / credit limits

Some runtimes apply per-session rate or credit limits to subagents. When a subagent return looks truncated, treat it as a rate-limit hit and recover.

### Detection

A subagent has hit a rate / credit limit when its return contains any of:
- Literal text `"You've hit your limit"`, `"quota exceeded"`, `"rate limit"`
- Total return under ~100 tokens with no fenced JSON block
- Return ending mid-sentence without a completion indicator

### Recovery procedure

1. **Check the subagent's declared output files on disk.** Each scope's reference lists the files it owns (e.g., the Phase 4 store-pages scope owns `products/index.astro`, `products/[slug].astro`, `cart.astro`, `thank-you.astro`, `ProductCard.astro`). Read each expected path.
2. **If all expected files exist on disk and look syntactically valid** (no empty files, no unterminated strings): synthesize a `status: "complete"` entry for `run.json` with `notes: "Sub-agent hit rate limit after writing all files; files on disk are valid."` Proceed with the next dispatch.
3. **If expected files are missing or empty:** retry the subagent once with an identical prompt. If the retry also hits the limit, mark the phase `status: "partial"` in `run.json` with `errors: [{code: "RATE_LIMIT", message: "Subagent rate-limited; <N> of <M> files produced"}]` and decide per-case — the orchestrator may fall back to inline emission of the missing files if they're trivial (single-file scope), or fail the run.
4. **Do not loop.** Retrying the same subagent more than once after a rate limit wastes budget — the limit is session-scoped and persists.

Record the rate-limit event in `run.json` `notes[]` regardless of recovery outcome — it's important observability for tuning scope sizes.

## Build & Release

1. `npx @wix/cli@latest build` — if it fails, inspect `.wix/debug.log` for the specific error, fix, retry. Common failure modes are listed in `references/shared/RETURN_CONTRACT.md` § "Common failure modes".
2. `npx @wix/cli@latest release` — extract the published URL from the `Site published on <url>` line in stdout. This command also populates the **Frontend link** in headless settings natively, so transactional emails link to the deployed frontend without any extra API calls.

---

## Final Message — summary FIRST, then run.json, in ONE turn

**Ordering is strict and user-perceived latency depends on it.** The summary prose is the **first content of your final turn**; the `Write .wix/run.json` is the **last tool call in that same message**. Composing `run.json` takes ~15–25 s (it aggregates every subagent return), so writing it *before* the summary makes the user wait that whole time to see their live URL — for no reason, since `run.json` is a silent observability artifact they never read.

Hard rules:
- **Do NOT write `run.json` before the summary.** A run that emits the `run.json` `Write` first (or in an earlier turn) is wrong even if the content is identical — it just delays the URL.
- **Do NOT emit a pre-narration turn** ("Site is live, writing run.json…", "delivering the summary…"). That is orchestration machinery (`PLAN.md` § "User-facing output") and it splits the single turn. The summary prose itself is the first thing the user sees after release.
- **One turn:** summary prose → then the `Write` tool call, as siblings in the same assistant message. The turn does not close until the `Write` completes, so the record still lands on disk before control returns — you get on-disk durability without making the user wait for it.

The summary prose contains, in order:

1. **Production URL** — bold link, first line (the exact `Site published on <url>` string; do not retype it).
2. **Dashboard link** — `https://manage.wix.com/dashboard/<siteId>`.

**Do not present timings.** No total-wall figure, no per-phase breakdown ("scaffold 26s · design-system 13s · …"), no "built in ~N min." Phase timings are machinery and the self-reported number is easy to get wrong (it has under-reported true wall in past runs); they belong in `run.json`, not the user-facing summary. The user wants their site, not a stopwatch.

Then, in the same turn after the summary prose, write `.wix/run.json` silently — the observability record aggregating every subagent return (format per `references/shared/RETURN_CONTRACT.md` § "Final run.json format"), including the phase timings. Use the subagent returns already in session context — do not re-read anything to compose it.

---

## Styling contract coordination

The **design tokens** (`.wix/design-tokens.css` + `.wix/site.d.ts`) are the coordination artifacts between subagents. Read by every downstream phase that touches styled markup.

### Producer: Phase 2 (Designer Wave 0 + Composer Setup-window bridge)

Dispatch timing: the Designer is dispatched at BUILD entry (run-step 0); the Composer at the Setup-window bridge (run-step 2 above). Net: `emit-design-tokens.mjs` writes `.wix/design-tokens.css` + `.wix/site.d.ts` (pure projections of the Designer's `data.designTokens`); the **Composer** writes the `@theme` palette into `global.css` from the same tokens plus the other 5 files. `designTokens` is the single source of truth — the script projects it, the Composer applies it.

### Consumer: Phase 3 Components (Step 4.5)

Phase 3 is dispatched in Step 4.5 above. The styling contract is passed inline in each Phase 3 prompt.

### Consumers: Phase 4 Pages (Step 7)

Contract already exists when Phase 4 launches. Subagents receive the contract contents inline in their prompt (no polling).

---

## Diagnostic: did the concurrent batch actually run in parallel?

If a build feels slow, check whether dispatches that should have been concurrent actually overlapped in execution. Two failure modes:

1. **Serialized launch:** the orchestrator emitted subagent invocations one at a time across multiple turns instead of as a single batch. Symptom: multi-second gaps between subagent starts in the run log.
2. **Serialized execution:** the runtime dispatched the batch but executed it sequentially (rare; most runtimes parallelize properly).

The fix for (1) depends on the runtime — check whether your dispatch primitive supports a single concurrent batch and whether anything between the subagent invocations (status updates, narration, file writes) is splitting the batch into multiple turns. Even when (1) cannot be fixed, **background dispatch alone gives ~2× compression** by overlapping execution. Make every subagent that doesn't block downstream work a background subagent.
