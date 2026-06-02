# Authentication

Every Wix API call this skill makes goes through `@wix/cli` + `curl` — no MCP, no SDK. This file documents the auth shape (header layout, token minting, recovery ladder) so individual phase docs don't have to repeat it.

## Prerequisites

- `@wix/cli` resolvable via `npx`. The scaffold installs it project-local, so `npx @wix/cli …` works without a global install.
- An authenticated CLI session. Test with `npx @wix/cli@latest whoami` — exits **0** when logged in (prints the authenticated email + user id), **non-zero** when logged out.

The primary place this check runs is DISCOVERY.md § "Pre-flight" — foreground, before any `AskUserQuestion`. `scaffold.sh` repeats the check defensively for its standalone-invocation path. **If the check fails, run `npx @wix/cli@latest login` yourself with `run_in_background: true`** per the next section — do not tell the user "run wix login and retry" and stop. Punting to the user breaks the flow: the harness backgrounds the user-issued command, the agent doesn't know which output file to read, and you end up paying ~60 s + a manual user interrupt to recover.

The "stop and tell the user" path is a **last-resort fallback** for when the background-run mechanism itself is broken (e.g. the harness rejects `run_in_background: true`, or the task output file never gets created). Try the agent-driven flow first.

## `wix login` from a non-interactive agent

`wix login` (or `npx @wix/cli@latest login`) emits one JSON event per line on **stdout** and blocks until the human finishes the browser step. The first event you care about is `awaiting_user`:

```json
{"event":"awaiting_user","expiresInSeconds":600,"userCode":"TPV5HUG5","verificationUri":"https://users.wix.com/login/device-login?color=developer&studio=true"}
```

(Earlier revisions of this doc claimed the CLI wrote human-readable prose to stderr with no JSON events — that was wrong. The events are JSON on stdout. There may be incidental Node warnings interleaved; line-by-line JSON parsing with a `try` around each line handles that cleanly.)

### How to invoke — exact shape

The Bash command is just the CLI invocation, **nothing else**:

```bash
npx @wix/cli@latest login
```

Pass `run_in_background: true` on the Bash tool call. **Do not** add shell `&`, **do not** redirect to your own `mktemp` file, **do not** chain with `echo`/`sleep`. The harness wraps the process for you and writes stdout+stderr to its own task output file at `/tmp/claude-<uid>/<project>/tasks/<task-id>.output`. The tool's `<bash-stdout>` reply gives you that path verbatim — that's the file you read. Stacking shell `&` on top of `run_in_background` creates two layers of backgrounding: the harness captures only the parent shell's `pid:` / `file:` echoes while wix-login's actual JSON events write somewhere else.

### Reading the output

Poll the harness's task-output file until the `awaiting_user` JSON line appears. Use `Read` on the path returned in `<bash-stdout>` — `TaskOutput` also works. The first useful event is on line 1 (a Node `TimeoutNaNWarning` may follow on lines 3-5; ignore it, the agent only cares about the JSON line). Parse the JSON, extract `verificationUri` + `userCode`.

### The critical step: surface, don't re-invoke

When you see the `awaiting_user` event:

1. **Surface URL + code to the user in plain prose. Send the message. Do not write more Bash. Do not re-invoke wix-login "to do it properly this time".** Seeing the `awaiting_user` event means the first invocation is working correctly — reading its output is the right next step. Restarting wix-login throws away the live device-login session and the second instance has nothing to wait for (the user never sees the new code because by the time it's emitted, you've already messaged them the first one or are mid-restart). One invocation, one read, one message, one wait.
2. The message shape:

   > *"You need to authenticate with Wix. Open `<verificationUri>` in your browser and enter the code `<userCode>` — I'll continue once you've completed the login."*

3. **Then wait** for the harness `task-notification` with `<status>completed</status>`. That's the terminal signal that the wix-login process exited (the user finished the browser flow). Do not re-run `whoami` in a sleep loop while waiting; the notification is the only signal you need.

On `<status>completed</status>` with exit 0, run `whoami` once to confirm and proceed. On non-zero exit (rare — typically a timeout if the user took >600 s, or a network error), surface the tail of the output file to the user and stop.

## Token minting

```bash
SITE_ID="<siteId>"  # from wix.config.json after scaffold
TOKEN=$(npx @wix/cli@latest token --site "$SITE_ID")
```

- Mints a **site-scoped REST token**. **Mint it exactly once per run and never re-mint.** The CLI returns a **byte-identical** token on every call within a run (it caches internally), so re-minting buys nothing — it only costs ~1.25 s of CLI startup per call. Cache the value in session scratch and inline it into every `curl`. This holds on errors too: a re-minted token is the same string and will produce the same result, so re-minting is never a useful reaction to a failed call (the one exception is after a fresh `wix login`, which establishes a new CLI session — see the recovery ladder).
- Use `npx @wix/cli@latest token …` rather than bare `wix token …`. `@wix/cli` may not be globally installed in every harness; `npx` resolves the project-local copy the scaffold produced. The first invocation auto-fetches the CLI (~3–5 s) if missing; subsequent calls are instant.
- The first `--site "$SITE_ID"` invocation in a run is the source of truth for `SITE_ID`. Bind it in session scratch; do not re-derive from `wix.config.json` mid-run.

## REST call shape

Every call against `wixapis.com` uses two headers:

```bash
curl -sS -X POST "https://www.wixapis.com/<endpoint>" \
  -H "Authorization: Bearer $TOKEN" \
  -H "wix-site-id: $SITE_ID" \
  -H "Content-Type: application/json" \
  -d '<body>'
```

- **`Authorization: Bearer $TOKEN`** — the `Bearer` prefix is required. Variants (`Authorization: $TOKEN`, lowercase `bearer`) are not accepted by all endpoints; standardising on `Bearer` avoids the per-endpoint guessing game.
- **`wix-site-id: $SITE_ID`** — required by site-scoped REST families (Stores v3, CMS v2, Blog v3, Forms v4, Categories v1, Apps-Installer v1, etc.). Harmless on the few endpoints that don't read it, so include it on every call by default rather than discovering its absence via a 403.
- **`Content-Type: application/json`** — required on every POST/PATCH body. The CLI token does not set it.

The body is the recipe's documented JSON payload, with `siteId` inlined where the recipe documents it as a field. Wrapper fields from MCP-era recipes (`reason`, `sourceDocUrl`, `siteId` as an outer arg) are not part of the REST shape and drop on the floor.

## Recovery ladder

**Do not re-mint the token as a recovery step** (see token-minting note above — a re-minted token is byte-identical). Retry the *same* call with the *same* cached token.

| Symptom | First response | If it still fails |
|---|---|---|
| `401 Unauthorized` | Retry the same call once with the cached token. | The CLI session expired — run `wix login` per the flow above (that establishes a *new* session, so the token minted afterward genuinely differs). Re-minting without a fresh login returns the same expired-context token and will not help. |
| `403 Forbidden` | Retry the same call once. | The token shape is fine but the caller lacks the permission. The two real causes: (a) the relevant app is not installed yet (re-check `apps-installer-service` returned 200 for that app in Setup Step 4a), (b) the resource requires a provisioning step the recipe doesn't run. Surface the response body; do not loop on retries. |
| `404 Not Found` on a documented URL | Re-read the recipe — URL path segments are easy to typo (e.g. `/blog/v3/bulk/draft-posts/create`, **not** `/blog/v3/draft-posts/bulk/create`). | Recipe bug; surface and stop. |

**Do not** spend turns A/B-testing the header shape (Bearer vs no-Bearer, with/without `wix-site-id`) or cycling tokens. The shape above is the contract; if a single retry with the cached token doesn't fix it, the issue is upstream and recipe-level debugging will not recover it.

## Account-scoped calls

`npx @wix/cli@latest token` (no flags) mints an **account-scoped** token. `npx @wix/cli@latest token --site "$SITE_ID"` mints a **site-scoped** token. The CLI's `--site` flag is what toggles between the two scopes; there is no separate `--account` flag because omitting `--site` is itself the account-scoped form.

The account-scoped token authenticates against `manage.wix.com` endpoints (e.g. `POST /credit-transactions/v1/credit-transactions/get-account-balance`).

```bash
# Account-scoped — for /credit-transactions, /accounts, /subscriptions, etc.
ACCOUNT_TOKEN=$(npx @wix/cli@latest token)

# Site-scoped — for everything site-operating (apps install, products, blog, cms, …)
SITE_TOKEN=$(npx @wix/cli@latest token --site "$SITE_ID")
```

**Do not share tokens across scopes.** Site-operating calls (`wixapis.com/stores/v3/...`, `/blog/v3/...`, `/wix-data/v2/...`) need the **site** token + `wix-site-id` header; using the account token returns `403 SITE_TOKEN_REQUIRED`. Account-level calls (`manage.wix.com/credit-transactions/...`, `/subscriptions/...`) need the **account** token alone — no `wix-site-id` header; using the site token returns `403 ACCOUNT_TOKEN_REQUIRED`.

Today the only account-scoped call in the skill is the Discovery Q3 balance lookup (`DISCOVERY.md` § 2.5.2). If a future phase needs another, mint a fresh account token at the call site (do not cache across the run alongside the site token — keep them in separate scratch slots so misuse is hard).

**Historical note.** Earlier revisions of this file said the CLI did not expose an account-scoped primitive and concluded the balance lookup was unrecoverable. That was a misreading of `wix token --help` — the help output reads `Get a site-scoped access token` against `--site`, implying (correctly) that omitting `--site` returns the default, account-scoped token. The balance lookup was disabled for no good reason for several runs.
