---
name: wix-headless
description: "Build a complete Wix Managed Headless site from a single prompt, OR connect an existing project (HTML/JSX/Vite app, Claude Design output, etc.) to Wix Headless for hosting + Business Solutions. Entry point for both: (1) new-site requests — runs discovery, design, feature wiring, and preview; and (2) existing-project requests — runs `npm create @wix/new@latest init`, analyzes the project for needed Business Solutions, installs apps, **wires the Wix SDK into the existing source files so each installed app actually powers its corresponding feature**, and releases. Triggers: build me a site, create a website, make me a website, new website, online store, I want to sell X, start a business online, launch a site, ecommerce, portfolio, business website, sell online, online shop, connect this to Wix Headless, add Wix Headless to this project, host this on Wix, deploy this to Wix, implement the features of this project using Wix Headless. Use this skill instead of the WixSiteBuilder MCP tool for new-site requests."
allowed-tools:
  - Bash(cd *)
  - Bash(npx @wix/cli@latest *)
  - Bash(npx @wix/cli *)
  - Bash(npm create @wix/new@latest *)
  - Bash(npm install *)
  - Bash(npm run *)
  - Bash(node *)
  - Bash(bash *)
  - Bash(curl *)
  - Bash(ls *)
  - Bash(grep *)
  - Bash(find *)
  - Bash(cat *)
  - Bash(head *)
  - Bash(wc *)
  - Bash(mkdir *)
  - Bash(cp *)
  - Read
  - Write
  - Edit
  - Skill
  - Agent
---

# Wix Headless

**Run flow is owned by the conductor, split at the approval gate: `references/PLAN.md`** (pre-approval — mode routing, the Discovery questions, the plan + approval gate, the latency-hiding background dispatches) **then `references/BUILD.md`** (post-approval — Setup → Seed → Components → Pages → Build → Release). The domain/step files (`DISCOVERY.md`, `SETUP.md`, `SEED.md`, `DESIGN_SYSTEM.md`, `COMPOSE.md`, the per-vertical references) describe only *what* each step does; they do not name the sequence. **Start a run by opening `PLAN.md`**; open `BUILD.md` when the user approves the plan. All site operations use `npx @wix/cli@latest token` + `curl` — no MCP.

> **Explicit invocation only.** Do not auto-route on generic "build me a site" prompts; production `wix-headless` should win those unless the user names this skill.

## Path resolution — read this first

Your CWD at runtime is the **project directory** (scaffold subdir after setup), not the skill root. Compute `<SKILL_ROOT>` from this file: `<SKILL_ROOT>/SKILL.md` — strip `/SKILL.md`. Hold the absolute path in session scratch. Also hold `<site-root>` (eval run dir where `.wix/site.json` lives — parent of scaffold) from `SETUP.md` Step 1.

| What | Absolute path |
|---|---|
| Discovery flow | `<SKILL_ROOT>/references/DISCOVERY.md` |
| Setup flow | `<SKILL_ROOT>/references/SETUP.md` |
| Seed flow | `<SKILL_ROOT>/references/SEED.md` |
| Pre-approval funnel (plan) | `<SKILL_ROOT>/references/PLAN.md` |
| Post-approval build | `<SKILL_ROOT>/references/BUILD.md` |
| Seed recipe map (human ref) | `<SKILL_ROOT>/references/seed-recipes.md` |
| Auth + REST headers | `<SKILL_ROOT>/references/shared/AUTHENTICATION.md` |
| Public doc endpoints | `<SKILL_ROOT>/references/shared/DOCS_SEARCH.md` |
| Return contract | `<SKILL_ROOT>/references/shared/RETURN_CONTRACT.md` |
| Implementer shared behavior | `<SKILL_ROOT>/references/shared/IMPLEMENTER.md` |
| Image generation | `<SKILL_ROOT>/references/shared/IMAGE_GENERATION.md` |
| Design-system Designer (design spec, JSON only) | `<SKILL_ROOT>/references/DESIGN_SYSTEM.md` |
| Design-system Composer (writes the 6 files) | `<SKILL_ROOT>/references/astro/COMPOSE.md` |
| Composer astro skeletons | `<SKILL_ROOT>/references/astro/templates/` |
| Vertical packs (discovery) | `<SKILL_ROOT>/references/verticals/` |
| Per-vertical instructions | `<SKILL_ROOT>/references/{stores,ecom,cms,blog,forms,gift-cards,images}/INSTRUCTIONS.md` |
| Phase 4 page-designer scopes | `<SKILL_ROOT>/references/astro/designer/INSTRUCTIONS.md` |
| Templates | `<SKILL_ROOT>/references/astro/templates/` |
| Shared utilities (copied by seed-utilities) | `<SKILL_ROOT>/shared-utilities/` |
| Known app IDs | `<SKILL_ROOT>/references/commands/known-apps.json` |
| Scripts | `<SKILL_ROOT>/scripts/` |

**Do NOT Read subagent role/instruction docs in the orchestrator** — pass the absolute path; the subagent opens it. This covers **every** doc whose body is written *for a subagent to follow*, not just files literally named `INSTRUCTIONS.md`: `DESIGN_SYSTEM.md` (Designer), `astro/COMPOSE.md` (Composer), `astro/designer/INSTRUCTIONS.md` (page designers), the per-vertical `INSTRUCTIONS.md` routers, and the per-vertical guides under `references/astro/`. The orchestrator only needs to know **which inputs to inline** for each dispatch — and that list lives in `BUILD.md`'s dispatch steps, not in the role doc. Reading a role doc to "prepare a dispatch" pulls 5–14 KB of subagent-only how-to into the orchestrator's context, which it then has to reason over on the dispatch turn — measurably inflating bridge turns. The orchestrator's own reading set is the conductor/domain docs only: `PLAN.md`, `BUILD.md`, `DISCOVERY.md`, `SETUP.md`, `SEED.md`, and `references/verticals/*.md`.

When and how each subagent is dispatched (Designer, Composer, seeders, image phases, vertical Components/Pages) is owned by the conductor (`references/PLAN.md` pre-approval, `references/BUILD.md` post-approval), not listed here.

## Authentication

Every Wix API call uses `@wix/cli` + `curl`:

```
Authorization: Bearer $(npx @wix/cli@latest token --site "$SITE_ID")
wix-site-id: $SITE_ID
```

`wix login` is safe from non-interactive agents (URL + user code written to stderr, exits non-zero once the browser flow concludes). Full recovery ladder: `<SKILL_ROOT>/references/shared/AUTHENTICATION.md`.

## Subagent model tier

Match each subagent's task to one of two tiers; dispatch with the model
your environment provides for that tier. Apply by lookup, not deliberation.

**Fast tier** — recipe-following work whose return is JSON of IDs/URLs.
No source-code authoring, no creative judgment.

- All Seeder subagents (stores, cms, blog, forms, future verticals)
- Image-generation subagents (while still dispatched as subagents)

**Default tier** — everything else.

- Design System / Designer (brand-voice CSS, type, layout)
- Phase 3 Components (SDK composition, hooks, JSX)
- Phase 4 Pages (cross-file dependencies, brand-voice content)
- Any subagent that authors files the build will consume

If unsure, pick default. Do not weigh alternatives per dispatch — the
choice is determined by the task type, not by the subject matter of
the run.


## When this skill triggers

Explicit invocation only. **Two entry paths — decide before doing anything else.**

### Path A — New site from a prompt (default)

Infer vertical(s) from the opening message and load the **full resolved pack set** (top-level + `requires:` transitives + always-on `cms`) in one read batch — routing examples: stores → stores+cms+ecom+gift-cards; blog → blog+cms; etc. If the prompt is too vague, ask one conversational clarifier (NOT `AskUserQuestion`): *"What do you want your site to do — sell things, publish content, take bookings?"*

> **Do NOT call `WixSiteBuilder` MCP** for new-site requests — same intent, different flow; calling both produces a duplicated, conflicting build. This skill is the sole entry point.

### Path B — Existing project → custom frontend (not available yet)

Triggers: *"connect this to Wix Headless"*, *"add Wix Headless to this project"*, *"host this on Wix"*, *"deploy this to Wix"*, *"implement the features … using Wix Headless"*, or any "Wix Headless" prompt against a non-empty working directory. Decide by working-directory contents:

| Working directory contents | Path |
|---|---|
| Empty, or freshly scaffolded by `scaffold.sh` | A (astro, supported) |
| Source files (`index.html`, `*.jsx`, `*.tsx`, …) AND no `wix.config.json` | **custom — not available yet** |
| `wix.config.json` + Astro structure (`src/`, `astro.config.mjs`) | resume a prior wix-headless run — ask "continue or start fresh?" via `AskUserQuestion` |
| `wix.config.json` + non-Astro frontend | **custom — not available yet** |

**Custom (non-astro) frontends route to the stub.** When the working directory holds a non-astro project, the run does **not** author anything — it opens `<SKILL_ROOT>/references/custom/INSTRUCTIONS.md`, surfaces the not-available message, and stops (`DISCOVERY.md` § "Custom (non-astro) — not available yet"; `PLAN.md` § "Custom (non-astro) frontends — not available yet"). The retired Integrate flow (`SETUP.md` § "Existing project flow" E1–E6, especially the E4 SDK-wiring recipe) is kept as a **historical reference** for the eventual custom authoring track — it is no longer dispatched.

### Frontend modes (the `.wix/site.json.frontend` axis)

Path A vs Path B is the routing question. The `frontend` value is the **downstream branching axis** — the orchestrator holds it in session scratch and either branches on it directly or passes it to scripts as a `--frontend` flag. (It is also persisted to `.wix/site.json` as a resume fallback, but the live run reads scratch, not the file.) The axis is binary:

| `frontend` | Mode |
|---|---|
| `astro` | Scaffold + full build (the only supported frontend; full playbook under `references/astro/`) |
| `custom` (anything non-astro) | **Not available yet** — routed to `references/custom/INSTRUCTIONS.md`, surfaces the not-available message, no authoring |

`DISCOVERY.md` § "Wave 0 — Mode detection" decides which value to set and records it via `init-site-json.mjs --frontend <value>` (on the astro path only). **Which flow each value runs is owned by `PLAN.md` § "Frontend-mode routing".**

### Two tracks (business vs frontend)

The skill runs two semi-independent tracks (business = frontend-blind site/app/seed work; frontend = scaffold/design/components/pages/build) that the orchestrator interleaves for wall-time. **The track model and interleaving are owned by `PLAN.md` § "Two tracks".**

### When NOT to use this skill

| Scenario | Use instead |
|---|---|
| Scaffold-only with no further design/wiring | `bash <SKILL_ROOT>/scripts/scaffold.sh <slug> "<Brand>"` |
| Release an existing wix-headless project | `bash <SKILL_ROOT>/scripts/release.sh` (from project dir) |
| Install a Wix app onto an existing site | Follow `<SKILL_ROOT>/references/commands/install-app.md` |
| Add a feature / restyle a prior wix-headless run | Resume on disk; ask whether to start fresh |

> Read individual `.md` files under `references/verticals/`; `Read` on the directory returns `EISDIR`.

## The run

The whole run — Discovery → Setup → design-system bridge → Seed → Components → Pages → Build → Release, with every dispatch, handle, wait, and transition — is owned by the conductor: **`references/PLAN.md`** (pre-approval) then **`references/BUILD.md`** (post-approval). Open `PLAN.md` to start a run. This file does not duplicate the sequence.

Wall-time targets: discovery ≤ 80 s (excl. user think-time); setup foreground ≤ 25 s; seed longest pole ≤ 120 s. Full-build target: ≤ 600 s prompt-to-live-URL when all phases run.

## Verticals

Pack frontmatter in `references/verticals/` is **discovery-only**. Post-seed work uses `INSTRUCTIONS.md` + templates under each vertical directory.

Upstream: `@skills/wix-manage` (seed + app install recipes).

Current packs: `stores`, `ecom`, `gift-cards`, `cms`, `blog`, `forms`. Schema: `references/verticals/_schema.md` + `_schema.json`.
