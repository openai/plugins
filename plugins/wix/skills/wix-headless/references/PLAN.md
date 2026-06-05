# Plan — the pre-approval funnel

This file owns the run **from the first Discovery question to the user's approval of the plan** — mode routing, the questions, the background dispatches that hide latency, and the plan/approval gate. Its job is to get the user to the commitment moment **fast**, so keep it lean.

**On approval, open `BUILD.md`** — the post-approval conductor that owns execution (Setup → design-system bridge → Seed → Components → Pages → Build → Release). Everything past the approval gate lives there, so it is not read until the user has committed.

**The contract with the other files.** The domain/step files answer *what each step does* (the questions Discovery asks, the recipes, the prompt templates). This file + `BUILD.md` answer *when, in what order, in parallel with what, gated on what*. The step files do not name the sequence or chain to each other; the conductor (this file → `BUILD.md`) names when to apply each one. Neither prescribes a tool API — map each step to whatever subagent / parallel-execution primitive your runtime offers.

## Concurrency vocabulary

The terms below appear throughout this skill. They describe the *shape* of work; the runtime decides how to implement them:

- **Subagent** — an isolated worker with its own context. The orchestrator sends it a prompt (an `Instruction file` path + inputs); the subagent reads the instruction file, performs the scope, and returns a structured result.
- **Concurrent batch** — N subagents (or N tool calls) launched together so they execute in parallel rather than serially.
- **Background subagent** — a subagent the orchestrator does not block on; it runs while the orchestrator continues with downstream work and reports its result asynchronously.
- **Foreground subagent** — a subagent the orchestrator blocks on before continuing.
- **Wait (gate)** — the orchestrator pauses until specified background work (subagents or background `Bash` jobs like the scaffold) finishes. **Waiting means awaiting the harness's background-task completion notification — never a `sleep`/poll loop against an output file.** A poll loop burns the whole wait as blocked orchestrator time and delays everything gated behind it (e.g. sleep-polling the scaffold lands the Composer late). The completion notification is the only signal you need; the same rule covers the `wix login` wait (`shared/AUTHENTICATION.md`) and the no-sidecar-poll rule for image phases (`images/INSTRUCTIONS.md`).
- **Result** — the structured JSON block each subagent returns at the end of its run, per `references/shared/RETURN_CONTRACT.md`.

## Two tracks (business vs frontend)

The run is two semi-independent tracks that the orchestrator interleaves for wall-time:

- **Business track** (frontend-blind) — create/connect the site, **install Wix apps**, **seed backend data**. Inputs: `siteId`, `verticals`, `intent`, `brand`. It never reads `frontend`/template — a product (or collection, post, form) is the same regardless of what renders it. Its domain content lives in `SETUP.md` (app installs) + `SEED.md` (seeders).
- **Frontend track** (frontend-aware) — scaffold/prep the local project, Designer + design tokens, Composer, components, pages, SDK wiring, build. Every `frontend`/template branch lives here. Its domain content lives in `scaffold.sh` + `seed-utilities.sh` + `DESIGN_SYSTEM.md` / `astro/COMPOSE.md` + the per-vertical references (frontend guides under `references/astro/`).

The only cross-track data flow is **one-way, business → frontend**: seeders produce entity IDs which the orchestrator inlines into the frontend track's Page-subagent prompts. There is no frontend → business dependency.

## Frontend-mode routing

`frontend` (captured by `DISCOVERY.md` § "Wave 0 — Mode detection") is the axis the frontend track branches on. The orchestrator holds it in scratch and uses it in two ways: it branches inline in the PLAN/BUILD orchestration on the scratch value, and it passes `--frontend <value>` to `scaffold.sh` and `init-site-json.mjs` (and `--template astro` to `seed-utilities.sh`). The axis is binary — **astro (supported) vs custom (anything else, not available yet)**:

| `frontend` | Mode | Flow |
|---|---|---|
| `astro` | Scaffold (supported) | Wave 0 below → on approval → `BUILD.md`. The full playbook lives under `<SKILL_ROOT>/references/astro/`. |
| anything else (custom) | Not available yet | Open `<SKILL_ROOT>/references/custom/INSTRUCTIONS.md`, surface its not-available message, and **stop** — no scaffold, no Designer/Composer, no Setup/Seed authoring, no `BUILD.md` build flow, no half-built site. |

> **Astro is the one Wix-preferred frontend the skill builds end-to-end.** Every non-astro value (a user-provided project, a Vite/React SPA, anything else) is a **custom** frontend; the custom authoring track is deferred. Route it to the stub and tell the user astro is the supported path. The intended future shape for custom is recorded in `references/custom/INSTRUCTIONS.md`.

This is the **track-selection routing layer**: `SETUP.md`'s steps assume the routing already happened; the conductor owns the branch.

## Wave 0 — Discovery → plan → approval (Path A)

**The funnel dispatches nothing.** Its only job is to talk to the user, present the plan, and get approval. (The scaffold and Designer used to be dispatched here to hide their wall behind Q&A think-time — but the Designer is now ~10–15 s and the scaffold ~23 s, so the hiding isn't worth it, and those dispatches were what distracted the agent from actually showing the plan. **Both now dispatch in `BUILD.md`, post-approval.**) So the funnel is exactly three things:

1. **Mode detection + pre-flight, then the interview** — apply `DISCOVERY.md` (mode detection, CLI auth, Q0 vertical inference, Q1 brand, Q2 vibe, Q2.5 imagery). **Read only what the next question needs** — do not pre-read `BUILD.md`; read the vertical packs for plan composition (not before the vibe question).
2. **Compose and PRESENT the plan — as a standalone assistant message.** The moment Q&A ends and the aesthetic-direction craft is done, **render the full plan** (Design Direction from the Q2 craft + the Pages/Features tables, per `DISCOVERY.md` § plan) as a normal message the user reads. **The user MUST SEE the rendered plan before being asked to approve.** Do **not** fold the plan into the approval question, do **not** replace it with a one-line "here's the plan" + dispatch, and do **not** do any other work (no scaffold, no Designer, no scaffold-output reads) between the craft and the plan — there is nothing to dispatch here, so present the plan immediately.
3. **Approval gate** — *only after* the plan message has been sent, ask the approval question (`AskUserQuestion`).

**On approval** — `init-site-json.mjs --frontend <value>` writes the slim `.wix/site.json`, then **open `BUILD.md`** and continue from its run-step 0 (which dispatches the scaffold + Designer, then runs Setup).

## Custom (non-astro) frontends — not available yet

When `frontend` is anything other than `astro`, the run routes to the **custom stub** and stops the frontend track. Open `<SKILL_ROOT>/references/custom/INSTRUCTIONS.md`, surface its not-available message, and do **not** attempt authoring — no scaffold, no Designer/Composer, no Setup/Seed, no `BUILD.md`, no half-built site. The user is told astro is the supported frontend.

> **Retired: the Integrate (Path B) flow.** The skill used to run a live "Integrate" sequence for `user-provided` frontends — `DISCOVERY.md` § "Integrate-mode short flow" → `SETUP.md` § "Existing project flow" E1–E6 (E1 init → E2 analyze → E3 install apps → E4 SDK wiring → E5 release). That flow is **no longer dispatched**: non-astro frontends now hit the stub instead. The E1–E6 mechanics (especially the E4 SDK-wiring recipe) are kept in `SETUP.md` as a **historical reference** for the eventual custom authoring track (`references/custom/INSTRUCTIONS.md` § "Intended future shape"), not as a Beta deliverable.

## User-facing output (keep the machinery invisible)

This rule governs the **whole run**, both files. The user should see **milestones in plain language, never the orchestration machinery.** Between the Discovery approval and the final summary the run is largely silent — the orchestrator is dispatching, waiting, and gating, none of which is the user's concern.

**Never put internal orchestration vocabulary in a user-facing message.** That includes: background-handle names (`*_handle`), dispatch markers ("→ dispatch:", "dispatching X", "launching Wave 3"), subagent START/END, "seed gate" / "all handles complete", wave/step numbers ("Wave 3", "Step 4.5"), in-flight **subagent/handle status tables** (especially any "Handle" column), and internal paths (`wix-manage-root`, the scaffold subdir). These describe *how the conductor works*, not *what the user is getting*.

**The only user-facing messages in a Path A run are:**
1. **Discovery** — the questions, the plan, and the approval gate (`DISCOVERY.md`'s domain).
2. **One brief seed-progress sentence** (`SEED.md` Step 5) — plain prose naming what was seeded, no tables.
3. **The final summary** (`BUILD.md` § "Final Message").

Everything else is silent. If a long phase (Components, Pages) would otherwise look stalled, at most **one short plain-language line** ("Building your product and category pages…") — never a status table, handle list, or wave number. The in-flight subagent tables that runs have emitted ("Phase 3 Components running: | Subagent | Handle |…", "🎉 Seed gate open! All handles complete") are the anti-pattern this rule removes.

## Batching discipline

This rule governs **every** concurrent batch in the run — the Wave-0 pack reads (here), and the BUILD-entry scaffold + Designer dispatch, the Setup app-installs, and the Wave-3 seed batch (all in `BUILD.md`). The step files describe *what* is in each batch; the rule that they go out as one batch lives here.

Historical runs lost 1–2 minutes per phase to serialized dispatch — N operations emitted one-per-turn instead of in a single concurrent batch. Even when each ran fast, the inter-dispatch gaps (12–39s in measured runs) accumulated to >25% overhead per phase.

Two mitigations; use both:

1. **Fire the whole batch as one assistant message** — N `Agent`/`Bash` tool_uses as siblings. **No narration between dispatches** ("Now installing apps:", "Dispatching seeders:"). Any text adjacent to a dispatch closes the batch and forces the rest into separate turns, adding seconds per dispatch. This holds even for a 2-item batch (a measured 2-seeder run lost 12 s to one interstitial sentence).
2. **Use background-on-dispatch for anything that doesn't block downstream work.** Even if the runtime serializes the launch turns, background dispatch lets the work overlap in execution. Measured compression on a sequential-launch / background-execute model: ~2× wall-time vs. serial.

If your runtime forces serialization across turns, make every subagent that can run in the background a background subagent — the Designer, Composer, seeders, and image phases all dispatch background so the foreground never blocks on them.
