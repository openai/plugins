---
name: custom-frontend
description: "Routing target for the custom (non-astro) frontend track. Custom is any frontend the user brings that is not astro. The frontend-authoring track is NOT available yet — astro is the only supported frontend. This stub surfaces the not-available message and records the intended future shape; it does not attempt to author a site."
---

# Custom (non-astro) frontend — not available yet

**Astro is the only supported frontend today.** This doc is the routing target for every non-astro `frontend` value. When the conductor routes here, it does **not** attempt frontend authoring — it surfaces the message below and stops the frontend track.

## What to tell the user

> Custom (non-astro) frontends are not available yet — **astro is the supported frontend**. Re-run with the astro frontend, or check back later.

Do **not** scaffold, design, compose, or wire anything. Do **not** fall back to a half-built site. There is no per-pack custom authoring to dispatch — that work is deferred (see "Intended future shape" below).

## Why this is a stub

The frontend track is the only track that branches on the `frontend` axis (`PLAN.md` § "Two tracks"). It routes to exactly one of:

| `frontend` | Frontend-track instructions | Status |
|---|---|---|
| `astro` | `<SKILL_ROOT>/references/astro/` (full playbook) | **Supported** |
| custom (anything else) | this file | **Not available yet** |

Astro is the one Wix-preferred frontend the skill builds end-to-end. Every other frontend is the user's own choice; standing up the authoring track for those is deferred until the custom track is prioritized.

## Intended future shape (documented, not built)

When the custom track is prioritized, it will follow the premise below. **None of this runs today** — it is recorded here as the target so the eventual build has a spec.

1. **Scaffold** — `npm create @wix/new@latest init` wraps the user's *existing* project (vs `headless` for astro), writes `wix.config.json`, and sets `site.outputDirectory` to the directory containing the entry file. (`wix release` is framework-tolerant via `wix.config.json.site.outputDirectory`.)
2. **Business track (shared, frontend-blind)** — Setup (app installs from a project analysis, `env pull` if needed) and Seed run the **same** frontend-blind path as astro. Per the two-track model, a product/collection/post/form is the same regardless of what renders it, so this track does not change for custom.
3. **Frontend authoring (the deferred new work)** — per-pack wiring guides under `references/custom/<pack>/…` that inject `@wix/sdk` calls into the user's existing files, **additive-only**, via a heuristic inject-point ladder: explicit `data-wix-*` attribute → semantic class → return a recommendation rather than guessing. This is what the custom track delivers when it is built.
4. **Release** — `npx @wix/cli@latest release` directly, **no build** (the user's project is published as-is, or the user runs their own build first).

### Historical reference

The retired "Integrate" (Path B) flow — `SETUP.md` § "Existing project flow" E1–E6, especially the **E4 SDK-wiring recipe** — is the closest prior art for step 3 above. It is kept as a **historical reference only**, not a Beta deliverable. Do not dispatch it; the conductor no longer routes non-astro frontends into it.
