---
name: "quickstart"
description: "Scaffold a running Next.js + shadcn Convex app from one sentence — convex dev + next dev already running — then build the idea live (runs locally). TRIGGER when the user wants to START a new Convex app from scratch — e.g. they ran $quickstart, said 'scaffold a new app', 'build me an app where users can ___', or 'new app'. SKIP when there's already a Convex project in the cwd."
license: "Apache-2.0"
---

# Convex Quickstart (Codex beta)

Stand up a running Next.js + shadcn "wow-shell" Convex app from one sentence, then
build the user's idea live (locally). The heavy scaffold runs as a served shell script
from the Convex quickstart backend ("anteater"); your job is to launch it, then build.

> **Auth (passkeys), the feedback panel, custom domains, and public `*.convex.app`
> publishing are de-scoped for this release** — they ship later. The scaffold runs
> **locally only**, with no login and no panel. (The error-watch monitor in STEP 5
> still applies and is valuable — keep it.)

The user's request after `$quickstart` is the **app idea** (e.g.
`$quickstart a movie-night voting app` → idea = "a movie-night voting app"). If no
idea was given, ask for a one-sentence idea, then continue.

## Degradation rule — when the scaffold can't run, write code, not ceremony

If the bootstrap can't run — a non-interactive/one-shot session, no network access, a
sandboxed temp dir, or the user just wants code rather than a running app — **don't
wait on the scaffold**. Write a standard Convex project directly:

- **ALL backend code goes under `convex/`** (`schema.ts`, queries, mutations, actions)
  — **NEVER at the project root.** Convex functions only run from the `convex/`
  directory.
- **Write ZERO scaffold/documentation files** unless explicitly asked — no
  `START_HERE.md`, `ARCHITECTURE.md`, `MANIFEST.txt`, or README walls. "Build me a
  backend" is a request for code, not a design-doc package.

## Data access + imports — read before writing any convex/*.ts

- Never an unbounded `.collect()` on a table that can grow — use `.withIndex(...)` +
  `.paginate(paginationOpts)`/`.take(n)`.
- Index, don't filter — `.index(...)` in `schema.ts` for every read path, queried via
  `.withIndex(...)`; `.filter()` is a full table scan.
- Imports: `query`/`mutation`/`action`/`internalQuery`/`internalMutation`/`internalAction`
  from `"./_generated/server"`; `api`/`internal` from `"./_generated/api"`; never from
  `"convex/server"` in application code.
- `v.literal("exact value")` for fixed string/enum members, not a bare `v.string()`.
- `"use node";` is action-only — never in a file that also exports a `query` or
  `mutation`.

## Self-verify — before declaring backend work done

Before you call any backend work finished: run `npx tsc --noEmit` and, when a
deployment is available (or via a local anonymous one:
`CONVEX_AGENT_MODE=anonymous npx convex dev --once`), push it. Fix every error
either one reports before finishing — one verify round catches the
wrong-relative-import / duplicate-symbol / unbalanced-paren class that otherwise
breaks the deploy.

## STEP 0 — launch the scaffold NOW (before anything else)

Run this **first**, before any reasoning or other tool calls — it kicks off the
~45–120s scaffold (npm install, convex dev, next dev) in the background so it's
installing while you read the rest. Substitute the user's idea for `<IDEA>`:

```bash
BASE="https://basic-anteater-667.convex.site"
IDEA="<IDEA>"
SLUG=$(curl -fsS --max-time 15 -X POST "$BASE/generate" -H 'content-type: application/json' \
  --data "$(node -e 'process.stdout.write(JSON.stringify({idea:process.argv[1],template:"nextjs-shadcn"}))' "$IDEA")" \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{process.stdout.write(JSON.parse(s).id||"")}catch{}})') || true
echo "SLUG=$SLUG"
QB=$(mktemp -t convex-qb-XXXX.sh)
curl -fsS --max-time 20 "$BASE/quickstart-bootstrap" -o "$QB" || { echo "BOOTSTRAP_FETCH_FAILED"; exit 3; }
# The bootstrap is feature-flagged via a profile. We ship the MINIMAL profile: scaffold
# only — no auth/passkeys, no feedback panel, no custom domain, and public *.convex.app
# publishing disabled (they ship later). To restore the goodness pass QB_PROFILE=full
# (or individual flags, e.g. QB_PASSKEYS=1 QB_PANEL=1 QB_DOMAIN=1).
echo "AUTH_MODE=none"   # minimal profile = no pre-baked auth; the build has no login
# QB_HARNESS=codex tags telemetry. QB_ARGS_BASE=$BASE is CRITICAL: the slug was
# generated on THIS deployment, so the bootstrap must fetch the personalized args +
# bespoke runbook from the SAME host (its default is prod, which 404s a staging slug
# → generic "My Convex App" defaults).
nohup env QB_PROFILE=minimal QB_HARNESS=codex QB_ARGS_BASE="$BASE" QB_FEEDBACK_URL="$BASE/feedback" \
  bash "$QB" $SLUG > .quickstart-bootstrap.log 2>&1 &
echo "SCAFFOLD_LAUNCHED log=.quickstart-bootstrap.log SLUG=$SLUG"
```

- If it prints `SCAFFOLD_LAUNCHED`, the scaffold is running in the background.
  **Do NOT run it again.** Note the `SLUG=`.
- If `curl` is blocked or you see `BOOTSTRAP_FETCH_FAILED`, the network/sandbox
  blocked it — tell the user they likely need to run Codex with network access /
  auto-approve (`codex --sandbox danger-full-access`), then retry.

## STEP 1 — wait for the scaffold, open the browser

Poll `.quickstart-bootstrap.log` until it contains `BOOTSTRAP_COMPLETE`.

**Codex's sandbox often reaps backgrounded (`nohup … &`) processes when the launch
call returns** — so the bootstrap may write its first line, then die before scaffolding.
If within ~20s the log has stalled (no new lines), **no app subdirectory has appeared**,
and there's no `BOOTSTRAP_COMPLETE`, the background launch was reaped. Recover by running
the bootstrap in the **FOREGROUND** — re-run the STEP 0 block but replace the
`nohup env … &` line with a plain foreground run, same env:

```bash
QB_PROFILE=minimal QB_HARNESS=codex QB_ARGS_BASE="$BASE" QB_FEEDBACK_URL="$BASE/feedback" bash "$QB" $SLUG
```

It backgrounds `convex dev` / `next dev` itself and returns at `BOOTSTRAP_COMPLETE` in
~1–2 min (set a generous command timeout, 300s+). `BOOTSTRAP_FETCH_FAILED` → server
unreachable; tell the user. When it completes the log prints:
- `OPEN_BROWSER_URL: http://localhost:<port>` — open this for the user immediately.
- The app is scaffolded in a new subdirectory with `convex dev` + `next dev` running
  and error watchers armed (`convex-errors.log` / `next-errors.log` paths are in the log).

## STEP 2 — read the runbook + build the idea live

Read the personalized runbook for the full build flow (it's served — fetch it):

```bash
curl -fsS "https://basic-anteater-667.convex.site/q/$SLUG.md"
```

Then build the user's idea following it. What's already done by the scaffold:
- **No auth this release** — the scaffold ships with **no login**. Only add auth if the
  user explicitly asks (then wire their requested provider via the `convex-expert` skill).
  *(Passkeys are de-scoped — `QB_PROFILE=minimal` sets `QB_PASSKEYS=0`.)*
- **No feedback panel this release** — narrate your build **in chat**; do NOT call
  `progress:post` / `todos:*` / `refinementQuestions:*`. *(Panel is off — `QB_PANEL=0`.)*
- **Publishing is disabled this release** — the app runs **locally** at the printed URL;
  do not publish or run `$add hosting`.

Rules while building:
- Delegate all code inside `convex/` to the **`convex-expert`** skill's rules
  (object-form syntax, validators, indexes, internal vs public).
- Watch for `convex/` + `next` errors and fix them as they appear — the easiest way
  is the `fix_errors_automatically` tool (see STEP 5), which surfaces them as events.

## STEP 3 — wrap up (runs locally; no publish this release)

When the app builds clean and the core feature works (your "v1"), tell the user it's
running **locally** at the printed URL and summarize what you built. Publishing to a
public `*.convex.app` URL and custom domains are **disabled this release** — don't
deploy, don't run `$add hosting`, and don't look for `.quickstart-domains.json`.

## STEP 5 — stay on watch with `fix_errors_automatically` (start EARLY, don't yield)

This harness has no push: a runtime error (or a slow async result) sits **unseen**
until you actively look. This plugin bundles a `convex-plugin` MCP server with one
**blocking** tool that surfaces it as an event — keep using it even though the
feedback panel is off this release (the `convex_error` / `next_error` watch is the
valuable part).

**Start watching as soon as the app is open (right after STEP 1) — not just after
v1.** The user is most engaged at the very start and will often submit a request or
question while you're still building. Call `fix_errors_automatically` between build
milestones and whenever you'd otherwise pause; on the FIRST call it returns
**immediately** if anything is already pending (it surfaces existing unhandled
requests/questions as `existing: true`), so feedback submitted before you started
watching is never lost. Then make it your standing idle action for the rest of the
session.

> **Avoid the repeated approval prompt:** each call is a separate tool invocation,
> so a one-time "Allow" re-asks every loop. Choose **"Always allow"** when prompted,
> or add to `~/.codex/config.toml`: `[mcp_servers.convex-plugin]` then
> `trust_level = "trusted"`. Also pass a long `timeoutMs` (e.g. 280000) so each
> block is long and you re-call less often.

Call the **`fix_errors_automatically`** tool with `projectDir` set to your app's
**absolute path** (the `convex-app/` subdir, where `.env.local` lives). It BLOCKS
until the next event, then returns one of:
- `feature_request` / `refinement_answer` → the user wants something — handle it
  (loop back through STEP 2/3), then call the tool again.
- `convex_error` / `next_error` → stop, read the line, fix the file, wait for
  `convex dev` / Next to recover, then call again.
- `quiet` → heartbeat timeout, nothing happened — just call it again.

**Loop on this tool instead of ending your turn.** Each call blocks, so you stay on
watch and react within seconds — no polling, no walking away. Keep looping until the
user clearly says they're done.

## After the run

Offer `$improve-convex-plugin` so the user can send this session for an AI review that
improves the quickstart.

## On failure / friction — offer to self-report (WITH the user's permission)

If the run doesn't go smoothly — you give up, hit a blocker, it takes way too long, or
the user is frustrated — don't yield silently. **Ask first, send only on a yes**:

> "That didn't go as smoothly as it should have. May I send this session — the transcript,
>  with secrets redacted — to the Convex team so they can fix what went wrong? [yes / no]"

- **On yes** → run the `improve-convex-plugin` flow (ships the redacted transcript):
  `curl -fsSL "https://basic-anteater-667.convex.site/send-transcript" | QB_HARNESS=codex bash -s -- --idea "<what broke>"`
- **On no** → respect it; send nothing.
- Either way, give the user an honest summary of where it got stuck.

Never send the transcript without an explicit yes.
