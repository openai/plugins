# Unified Temporal CLI (cloud-cli) + Client Config TOML Reference

> **The executor is `scripts/provision.sh`, not these raw commands.** During a run the agent invokes that script, which has these flags pinned and the error handling baked in. This file is the **background + source-of-truth** for what the script does: read it to understand the behavior, and when a prerelease flag drifts, update both `scripts/provision.sh` and this file together. Don't hand-run these commands during a normal setup.

Read this before changing any `temporal cloud ...` or `temporal config ...` command in the script. The `cloud-cli` is in **prerelease**, so command and flag names change. If a command or flag here is not accepted, run the matching `--help` and use what it reports — never guess flags.

## What this CLI is

- The unified CLI exposes a `temporal cloud` command group (binary name `temporal-cloud`). It is the prerelease successor to the older `tcld` Cloud CLI; the subcommand shapes mirror `tcld`.
- It is **separate** from a local `temporal server start-dev` workflow. This setup never starts a local server.
- Source / releases: https://github.com/temporalio/cloud-cli

## Prerelease disclaimer (show before download)

Surface this to the user before installing, quoted verbatim:

> **Pre-release:** This extension is offered as a pre-release and is subject to change. Please reach out to Temporal Support if you have questions.

## Install

macOS (Homebrew, prerelease tap) — **confirm Homebrew is installed first** (`command -v brew`); if it is absent, do not auto-install it, point the user to https://brew.sh or use the download fallback below:

```bash
command -v brew && brew install temporalio/prerelease/temporal-cloud
```

The tap is `temporalio/prerelease`, but the formula/binary is named `temporal-cloud` (not `cloud-cli`). If `brew install temporalio/prerelease/cloud-cli` fails with a formula-not-found error, use `temporal-cloud` as shown above.

Other platforms: download the latest archive from
https://github.com/temporalio/cloud-cli/releases/latest , extract, and put the
`temporal-cloud` binary on your `PATH`. Build from source with `make build` (needs Go).

Verify:

```bash
temporal cloud version      # or: temporal-cloud --version
temporal cloud --help
```

## Authenticate

```bash
temporal cloud login        # opens a browser for OAuth
temporal cloud whoami       # confirm the authenticated identity
```

For non-interactive use, most commands also accept `--api-key <key>`.

If the user has no Cloud account yet, send them to https://temporal.io/get-cloud first.

## List regions

Before creating a namespace, **always** list the available **provider-prefixed** regions and have the user **select from the output** — **do not hand-prefix a bare region, and do not accept a region typed from memory without confirming it against the list** (a remembered region can be valid yet wrong for the account, creating the namespace in the wrong place — which has paged on-call teams):

```bash
temporal cloud region list                 # list available regions; `temporal cloud region get <id>` for one
```

Note: in the current prerelease (cloud version 0.0.1) the region commands live under the **`region`** group (`temporal cloud region list` / `region get`) — there is **no** `namespace list-regions` subcommand. Use `--help` to confirm the exact subcommand name in the installed version. Pass to `--region` only a value the user selected from this command's output (shape `<provider>-<region>`); never a bare region you prefixed yourself, and never one typed from memory that you haven't confirmed against the list.

## Create an API-key namespace

Prerelease CLI — these flags are verified during the start-up check (against https://github.com/temporalio/cloud-cli and `--help`). Use the verified flags directly here; if that check found drift, this block should already be updated to match. As of the current prerelease:

```bash
temporal cloud namespace create \
  --name quickstartai-<sdk>-<timestamp> \
  --region <provider>-<region> \
  --api-key-auth-enabled \
  --retention-days 30 \
  --auto-confirm
```

- Confirmed flag names (these differ from older `tcld`): the namespace name flag is `--name` (not `--namespace`); API-key auth is the boolean `--api-key-auth-enabled` (not `--auth-method api_key`).
- **`--name` takes the bare name only** (e.g. `quickstartai-go-20260617-143205`) — Cloud appends `.<account-id>` itself (its `--help` even says the name "becomes part of the namespace ID"). The bare name must be **≤39 characters**; the appended account-id does not count toward that limit.
- **`--auto-confirm` is required for unattended runs** (otherwise an interactive confirm prompt hangs the skill). **Never `--auto-confirm` a *delete*.**
- **Region is provider-prefixed**: `us-east-1` → `aws-us-east-1` (and `gcp-...` for GCP). List exact values with the region-list command above.
- **Create synchronously (no `--async`).** It blocks for **a few minutes** (repeated `Operation pending…` lines — normal provisioning, not a hang) until the namespace lands on Cloud. `--async` is still unusable (returns before the namespace is provisioned). Don't abort during the wait.
- **Get the handle from `namespace list -o jsonl`, NOT from the create output.** As of the current prerelease, `create`'s default text output drifted to a **diff format** (`-{}` / `+{"name": …}`) that no longer carries the `<name>.<account-id>` handle. `namespace list -o jsonl` **works** — the earlier "list/get/-o json return empty" note is stale — and returns `{"Namespaces":[{"namespace":"<handle>","spec":{"name":"<bare>"},"endpoints":{"mtlsGrpcAddress":"<handle>.tmprl.cloud:7233", …}}, …]}`. `lookup_handle_by_name` matches our `spec.name` → `.namespace`, with an account-id-construct fallback (the account-id is account-stable). Still never decode the API-key token or read config files for the account-id.
- **Detached-but-synchronous (overlap):** `provision-and-scaffold` runs this synchronous create as a background job **within one invocation** while it clones + installs deps in the foreground, then joins and resolves the handle via `lookup_handle_by_name`. Still **never `--async`**; only the *process* is backgrounded, and only inside that single call.
- The `address` for the client config TOML is the **namespace endpoint** = the handle + `.tmprl.cloud:7233`, e.g. `<namespace-handle>.tmprl.cloud:7233` — build it directly from the handle (no `namespace get` needed). Use this, **not** the regional `grpcAddress` (`<region>.<provider>.api.temporal.io:7233`) — region-agnostic, works with API keys, survives HA failover (Temporal's recommended endpoint).

## Create an API key

Flags verified during the start-up check (against https://github.com/temporalio/cloud-cli and `--help`). As of the current prerelease, the subcommand for the logged-in user is `create-for-me` with these flags.

> **⚠️ Secret-safety: never run this command without redirecting stdout into a `0600` file.** The response carries the one-time `eyJ…` token; run it bare and the token prints to the terminal (and into any agent transcript). `scripts/provision.sh create-key` is the sanctioned caller — it always redirects. The form below is the *only* form to copy:

```bash
umask 077
temporal cloud apikey create-for-me \
  --display-name <key-name> \
  --description "money-transfer Cloud setup" \
  --expiry-duration 24h \
  --auto-confirm \
  -o json > "$KEYFILE"     # never to the terminal
```

- Confirmed against the prerelease CLI (differs from older `tcld`): subcommand `apikey create-for-me`; `--display-name` is **required** (not `--name`); expiry is `--expiry-duration` (not `--duration`). A separate `apikey create` may exist for service accounts; use `create-for-me` for the current user.
- `--auto-confirm` is **required** — like `namespace create`, this command prompts interactively; without it a captured run returns exit 0 with empty output and no key created.
- **Re-verify auth first.** The earlier `login` can expire mid-run. Run `temporal cloud whoami` right before this; if it errors/empties, `temporal cloud login` again before retrying.
- **Empty output + exit 0 ⇒ diagnose, don't improvise.** It means a suppressed confirm prompt (add `--auto-confirm`) **or an expired login** (re-check `whoami`/`login`). Fix the cause and re-run once.
- Capture path (verified against cloud version 0.0.1 with fresh auth): `-o json` **works** — redirect it to a `0600` file (`umask 077`), e.g. `... --auto-confirm -o json > "$HOME/.key.json"`. The secret is the **`.token`** field and the non-secret id is **`.keyId`**. In Step 6, read `.token` from that file and write it **directly into the TOML** under `[profile.cloud-setup]` via a script (never `config set --value`, never a rendered diff — both would expose the secret), then `chmod 600` the file and delete the temp capture file.
- `temporal cloud apikey list` may return **empty output even when keys exist** on this prerelease build — do **not** treat that as a failed creation. The authoritative confirmation of key creation is the `create-for-me` response (`asyncOperation.state == STATE_FULFILLED` + a returned `keyId`); the ultimate validity check is the Worker authenticating in Phase 4.
- **The secret is displayed only once.** It cannot be retrieved later — if lost, create a new key. Never echo it into chat or commit it to a repo.

## Client config TOML

Temporal SDKs and the CLI share a client-config TOML with named profiles.

Default file locations:

| OS      | Path |
|---------|------|
| macOS   | `$HOME/Library/Application Support/temporalio/temporal.toml` |
| Linux   | `~/.config/temporalio/temporal.toml` |
| Windows | `%AppData%\temporalio\temporal.toml` |

Override with the `TEMPORAL_CONFIG_FILE` environment variable.

**Use a named `cloud-setup` profile — never write to `[profile.default]`.** The user may already have a `default` profile (local dev, another Cloud namespace) that this would silently overwrite. A named profile lives alongside it and is selected explicitly.

**Auth-override gotcha:** a profile that carries an `api_key` becomes the CLI's auth source for any command that loads it, **overriding the `temporal cloud login` (browser) session**. Implications:
- Run management commands (`login`, `whoami`, `namespace …`, `apikey …`) **without** `--profile`, so they keep using the login session. Use `--profile cloud-setup` only for data-plane `workflow` commands (which need the key). This is why writing the key to `default` is harmful — it would hijack every command.
- After the key is deleted or expires, any command that loads that profile fails auth against a namespace that may no longer exist. Remove the `[profile.cloud-setup]` block to clean up, or pass `--disable-config-file` to bypass the profile and fall back to the login session.

Profile structure:

```toml
[profile.cloud-setup]
address = "<namespace-handle>.tmprl.cloud:7233"   # namespace endpoint
namespace = "<namespace-handle>"
api_key = "<the-one-time-key>"

[profile.cloud-setup.tls]
disabled = false   # TLS is REQUIRED for Temporal Cloud — set it explicitly.
# An empty [profile.cloud-setup.tls] section left TLS ambiguous and caused
# "unable to connect / tls not set to true" failures; `disabled = false` is unambiguous.
```

**Write the whole `[profile.cloud-setup]` block directly into the TOML file — do not use `temporal config set`.** `config set` rewrites the shared file and can strip the `oauth` block out of `[profile.default]` (where the `temporal cloud login` session lives), breaking `temporal cloud whoami` and cleanup. Writing the block yourself touches only `cloud-setup`. Write `address` and `namespace` directly, and the `api_key` the same way — from the captured value via shell redirection (never `config set --value`, which records the secret in shell history and exposes it in `ps`). Then restrict permissions so other local accounts can't read the credential:

```bash
chmod 600 "$HOME/Library/Application Support/temporalio/temporal.toml"
```

Other useful commands (always scope them to the profile):

```bash
temporal --profile cloud-setup config list   # show the profile (do not print api_key to the user)
temporal --profile cloud-setup config get <property>
temporal --profile cloud-setup config delete <property>
```

Once the `cloud-setup` profile is set, `temporal --profile cloud-setup workflow list` / `workflow describe` operate against the Cloud namespace. Plain commands without the flag still use the user's `default` — so always pass `--profile cloud-setup`.

## Cloud UI deeplink

To send the user to their **specific Workflow run** in the browser (preferred — lands them on the run's history so they can watch it / see the failure-and-recovery), use the run URL:

```
https://cloud.temporal.io/namespaces/<namespace-handle>/workflows/<workflow-id>/<run-id>
```

The bare list URL (`…/workflows`) is a fallback only — surface the run-specific URL when you have the Workflow ID + Run ID (from the starter output or `workflow describe -o json`). `<namespace-handle>` is the namespace's full handle from `namespace create` — `<name>.<account-id>`, e.g. `quickstartai-go-20260617-143205.fmrip`.
## Auth-failure stderr wording (await-auth / workflow list)

`temporal --profile cloud-setup workflow list` is the auth-readiness poll. On failure
the Cloud API gateway (Envoy) returns a gRPC status whose `desc` is a **JWT-filter**
message — the wording is **JWT-anchored, never "api key"-anchored**. Captured against
the prerelease CLI:

| Condition | Exact stderr | Classification |
|---|---|---|
| Empty / missing key | `Error: failed reaching server: rpc error: code = Unauthenticated desc = Jwt is missing` | **transient** (can occur mid-propagation) |
| Bad / wrong-issuer key | `Error: failed reaching server: rpc error: code = Unauthenticated desc = Jwt issuer is not configured` | **transient** |
| Expired key | `Error: failed reaching server: rpc error: code = Unauthenticated desc = Jwt is expired` | **permanent → `key-expired` fast-fail** |
| mTLS-only namespace (wrong endpoint) | `Error: failed reaching server: connection error: desc = "error reading server preface: remote error: tls: certificate required"` | **transient** (TLS layer, not auth) |

Why only `expired` fast-fails: a valid key that is merely *propagating* has a **future
`exp`**, so it can never emit `Jwt is expired` — matching `expired` (anchored to
jwt/key/token) is safe against wrong-fast-failing a key that just needs a moment. The
other descs are ambiguous (can appear during propagation), so they stay transient and
resolve as `auth-timeout` with the redacted stderr line attached. This is the source of
truth for `await_auth_permanent()` in `scripts/provision.sh`.

> Note: `Jwt is missing` / `issuer is not configured` and the mTLS/TLS error were
> captured live. `Jwt is expired` is the standard Envoy JWT-filter default and the
> expected wording for a real expired key; it was not captured live (the prerelease
> `apikey create-for-me` emits the one-time secret only to a TTY, so a short-expiry
> key couldn't be minted+polled non-interactively). If a live capture ever differs,
> update the table and `await_auth_permanent()` together.

## API-key mint output drift (create-key)

The prerelease `apikey create-for-me -o json` does **not** put the one-time secret on
redirectable stdout: with stdout+stderr redirected (non-TTY) it returns **empty output
with exit 0** and, in that mode, may not persist a key at all. The secret is emitted to
the controlling **TTY** / as human text. This is why `cmd_create_key` captures BOTH
streams, falls back to a JWT-pattern scrape, and finally to a hidden `/dev/tty` paste —
and why the offline `key-empty` scenario (empty both streams, exit 0) is faithful.
