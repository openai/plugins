---
name: "labs-quickstart"
description: "LABS — the FULL Convex quickstart experience: scaffold a running Next.js + shadcn app from one sentence with passkey (WebAuthn) sign-in and a live in-app Chef feedback panel pre-baked, build the idea live, then PUBLISH it to a public https://<app>.convex.app URL (with the user's confirmation before publishing). TRIGGER when the user runs $labs-quickstart, or asks for the full/labs quickstart, a published/public app, sign-in/passkeys, or the in-app feedback panel from scratch. For a plain local-only scaffold use $quickstart instead. SKIP when there's already a Convex project in the cwd."
license: "Apache-2.0"
---

# Convex Labs Quickstart ($labs-quickstart)

The **full** quickstart experience (labs): a running Next.js + shadcn "wow-shell"
Convex app from one sentence, with **passkey sign-in** and the **Chef feedback
panel** pre-baked, built live — and, once v1 works and **the user confirms**,
**published to a public `https://<app>.convex.app` URL**. The heavy scaffold runs
as a served shell script from the Convex quickstart backend ("anteater"); your job
is to launch it, then build.

> Want just a plain, local-only scaffold (no login, no panel, no publishing)?
> That's the **`$quickstart`** skill — use it instead.

The user's request after `$labs-quickstart` is the **app idea** (e.g.
`$labs-quickstart a movie-night voting app` → idea = "a movie-night voting app").
If no idea was given, ask for a one-sentence idea, then continue.

## Degradation rule — when the scaffold can't run, write code, not ceremony

If the bootstrap can't run — a non-interactive/one-shot session, no network access, a
sandboxed temp dir, or the user just wants code rather than a running app — **don't
wait on the scaffold or the panel/passkey/publish machinery**. Write a standard Convex
project directly:

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
# The bootstrap is feature-flagged via a profile. LABS ships the FULL profile:
# passkey auth pre-baked, the Chef feedback panel wired, and public *.convex.app
# publishing enabled — EXCEPT custom domains, which stay off (QB_DOMAIN=0).
# Only fall back from pre-baked passkeys if the idea asked for a different auth
# method (else the agent rips it out mid-build). Emit AUTH_MODE for STEP 2.
if printf '%s' "$IDEA" | grep -qiE 'oauth|google (sign|login|auth)|github (login|auth)|sso|saml|magic[ -]?link|password[- ]?only|email.?(\+|and|/).?password|clerk|workos|auth0|\.tgz'; then echo "AUTH_MODE=custom"; else echo "AUTH_MODE=passkeys"; fi
# QB_HARNESS=codex tags telemetry; QB_ARGS_BASE/QB_FEEDBACK_URL keep the args +
# panel feedback on the same host the slug was generated on.
nohup env QB_PROFILE=full QB_DOMAIN=0 QB_HARNESS=codex QB_ARGS_BASE="$BASE" QB_FEEDBACK_URL="$BASE/feedback" \
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
QB_PROFILE=full QB_DOMAIN=0 QB_HARNESS=codex QB_ARGS_BASE="$BASE" QB_FEEDBACK_URL="$BASE/feedback" bash "$QB" $SLUG
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
- **Auth:** check `AUTH_MODE` in the launch log. If `AUTH_MODE=custom` (the idea
  asked for OAuth/password/magic-link/a specific auth component), passkeys were NOT
  pre-baked — wire the **requested** provider per its README (delegate `convex/` code
  to the `convex-expert` skill) and skip the passkey button. If `AUTH_MODE=passkeys`
  (default), **passkeys** are pre-baked (`@convex-dev/auth` pinned build,
  `convex/auth.ts`, `...authTables`, `ConvexAuthProvider`, JWT keys set) — you add the
  **email-first sign-in UI**: an email input + one call to
  `usePasskeyAuth().signInOrRegisterWithPasskey({ email })`, which signs the user in if
  they already have a passkey for that email or registers a new one (the build enables
  enumeration-by-email + autofill). Use the returned `registered` flag for the
  welcome message; give the input `autoComplete="username webauthn"` for autofill.
  ⚠ The email is self-asserted/unverified — authorize off the Convex user `_id`
  (`getAuthUserId`), never `user.email`.
- The **Chef feedback panel** is wired — keep the `FeatureRequestPanel` mount (a
  floating panel in the layout, e.g. `app/_chef-panel.tsx` / `<ChefPanel />`) — **never
  delete or unmount it**. **Narrate your build through the panel, not chat** —
  `npx convex run progress:post '{"message":"…"}'`,
  `npx convex run todos:plan '{"items":[…]}'` / `todos:advance`, ask the user
  clarifying questions with `npx convex run refinementQuestions:ask '{"text":"…"}'`,
  and resolve incoming feature requests with
  `npx convex run featureRequests:setState '{"id":"…","state":"…"}'`.
- **Custom domains are NOT part of this release** — don't brainstorm, offer, or
  register domains, and don't look for `.quickstart-domains.json`. (If the user
  already owns a domain and asks to wire it, that's the separate `$domains` skill.)

Rules while building:
- Delegate all code inside `convex/` to the **`convex-expert`** skill's rules
  (object-form syntax, validators, indexes, internal vs public).
- Watch for `convex/` + `next` errors and fix them as they appear — the easiest way
  is the `fix_errors_automatically` tool (see STEP 4), which surfaces them as events.

## STEP 3 — publish to *.convex.app (ASK THE USER FIRST)

When the app builds clean and the core feature works (your "v1"), **offer to
publish** — do not publish silently:

> "v1 is working locally. Want me to publish it to a public
>  `https://<app>.convex.app` URL anyone can open?"

Publish **only on a clear yes**. On a no, the app keeps running locally — done.

On yes, three parts (the served runbook has the full detail — it wins on conflict):

**1. Rebind passkeys to the public page origin** (WebAuthn is origin-bound; the
page moves to `<app>.convex.app` while the auth HTTP routes stay on the
deployment's `*.convex.site`). `<app>` = the deployment name (the subdomain of
`NEXT_PUBLIC_CONVEX_URL`). Use the `NAME=VALUE` form (never `env set NAME "$VALUE"`
— values starting with `-` parse as flags):

```bash
npx convex env set "SITE_URL=https://<app>.convex.app"
npx convex env set "AUTH_PASSKEY_RP_ID=<app>.convex.app"
npx convex env set "AUTH_PASSKEY_ORIGIN=https://<app>.convex.app"
```

**2. Static export** — `next.config.ts` must be exactly
`{ output: "export", images: { unoptimized: true } }` (never silence the linter or
type-checker to force a build — fix the real cause). Export emits to `out/`.

**3. Publish through the moderated gateway** (no static-hosting component needed):

```bash
curl -fsSL https://basic-anteater-667.convex.site/publish-convex-app -o publish-convex-app.mjs
npm install -D fflate
node publish-convex-app.mjs            # build → zip out/ → moderated gateway upload
```

It prints `https://<app>.convex.app` — pass that URL to the user, and verify the
passkey ceremony works on the published page (register a test passkey; an
RP-ID/origin error means the three env vars above don't match the `.convex.app`
host). If the gateway returns 403 (content moderation), it prints the reasons — a
legitimate app should pass; report a false positive to the user, don't evade it.
Publishing needs a cloud Convex deployment; if anonymous/local, `npx convex dev`
into a cloud project first.

## STEP 4 — stay on watch with `fix_errors_automatically` (start EARLY, don't yield)

This harness has no push: a user request typed into the Chef panel or a runtime
error sits **unseen** until you actively look. This plugin bundles a `convex-plugin`
MCP server with one **blocking** tool that surfaces it as an event and fixes it.

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
  `curl -fsSL "https://basic-anteater-667.convex.site/send-transcript" | QB_HARNESS=codex bash -s -- --base https://basic-anteater-667.convex.site --idea "<what broke>"`
- **On no** → respect it; send nothing.
- Either way, give the user an honest summary of where it got stuck.

Never send the transcript without an explicit yes.
