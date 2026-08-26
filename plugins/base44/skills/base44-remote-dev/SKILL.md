---
name: base44-remote-dev
description: >-
  Develop a Base44 app remotely from your own coding agent (Claude Code,
  claude.ai, or any MCP client) by connecting it to the Base44 sandbox. Cloud
  agents connect over MCP; local agents can connect over MCP or drive the same
  sandbox with the `base44 sandbox` CLI subcommands (the CLI uses shorter
  names — e.g. read_file is `sandbox read`, list_directory is `sandbox ls`,
  run_command is `sandbox run`). Covers connecting/
  authenticating, the available sandbox tools (run_command, read_file,
  write_file, edit_file, grep, list_directory, create_checkpoint,
  get_app_preview_url, get_app_status, list_user_apps, and the connector tools
  list_connectors / initiate_connector_connection), the edit→preview→verify loop, how changes
  persist, builder/external-agent concurrency, the in-editor "Send to Coding
  Agent" button + onboarding README URLs, and tips like reading the Vite
  dev-server logs. Triggers on "develop my Base44 app remotely", "connect
  Claude Code to Base44", "bring my own agent", "edit a Base44 app over MCP",
  "Base44 sandbox MCP", or "Send to Coding Agent".
---

<!--
  Vendored from base44-dev/apper PR #11608
  (docs/features/bring-your-own-model/base44-remote-dev/SKILL.md).
  Keep in sync with the upstream source if it changes.
-->

# Remotely develop a Base44 app over MCP

Connect your own coding agent to a Base44 app's sandbox and develop in it
directly — run commands, read and edit files, grep, list directories — while
Base44 supplies the sandbox and you supply the agent and the LLM.

This works with any MCP-capable client. The examples use Claude Code.

> **Easiest start:** in the Base44 app editor, click **Send to Coding Agent**. For a local agent
> it gives you a ready-to-paste prompt (which fetches a README and drives the sandbox over MCP or
> the `base44 sandbox` CLI — Section 10);
> for the web it gives a prompt to paste into a **claude.ai** chat (with the Base44 MCP connector)
> plus an **Open Claude** button. The button is the discovery surface — the rest of this skill is
> the reference.

> **Two transports:** web agents use **claude.ai** with the Base44 **MCP connector** (Sections
> 1–9) — note this is the regular claude.ai chat, *not* Claude Code on the web (`claude.ai/code`),
> which runs in its own repo-backed sandbox. A local agent can connect that same MCP server, or
> drive the sandbox with the **`base44 sandbox` CLI** (a Base44 CLI token, Section 10) — same tools,
> same behavior, same error codes; the CLI just exposes them under shorter command names
> (`sandbox read`, `sandbox ls`, …).

---

## 1. Connect the MCP server

The Base44 MCP endpoint is:

```
https://app.base44.com/mcp
```

Register it with Claude Code (run from any folder):

```bash
claude mcp add --transport http base44 https://app.base44.com/mcp
```

Add `--scope user` if you want it available in every project rather than just
the current folder.

`claude mcp add` only writes the config — it does not authenticate yet.

## 2. Authenticate

Start Claude Code and open the MCP menu:

```bash
claude
```

then, inside Claude Code:

```
/mcp
```

Select **base44** → **Authenticate**. A browser opens for the Base44 OAuth
flow (PKCE) — log in and approve. When it succeeds, `/mcp` shows **base44** as
connected and lists its tools.

**Pure-CLI / headless clients** that can't open a browser use the OAuth device
flow (`/oauth/device/code`) instead — request a code, approve it in a browser
on another device, and the client receives the token.

### Scopes

| Tools | Required scope |
|---|---|
| `read_file`, `grep`, `list_directory`, `get_app_preview_url`, `get_app_status`, `list_user_apps` | `apps:read` (granted by default) |
| `write_file`, `edit_file`, `run_command`, `create_checkpoint` | `sandbox:write` |

`sandbox:write` is **not** granted by default — shell and file mutation
require it explicitly. If the read tools work but the mutating ones return
`NOT_AUTHORIZED`, your token is missing `sandbox:write`; reconnect and grant
sandbox access (the device flow can request it explicitly).

---

## 3. Pick the app and orient yourself

Every tool takes a required `appId`. Find your apps with `list_user_apps`, then
pin the id in your requests so the agent passes it on every call.

Start **read-only** to build a mental model before changing anything:

```
Using the base44 tools on appId <APP_ID>:
1. list_directory on the app root (recursive, depth 2)
2. read_file src/App.jsx and src/pages.config.js
3. grep for the component I want to change
Summarize the structure before editing.
```

> **Cold start:** if the app has no running sandbox, the first tool call
> transparently brings one up from your last commit — it just takes a bit
> longer. Subsequent calls are fast.

> **CLI names:** over the `base44 sandbox` CLI (Section 10) these read tools are
> `list_directory` → `sandbox ls`, `read_file` → `sandbox read`, and
> `grep` → `sandbox grep`.

---

## 4. Make changes

- **`edit_file`** (`sandbox edit` in the CLI) — preferred for changing existing files. Provide exact
  `old_text`→`new_text` edits. Each `old_text` must be unique in the file
  unless you set `replace_all`. All edits in a call apply atomically
  (all-or-nothing) and you get a unified diff back. Pass `dry_run: true` to
  preview the diff without writing.
- **`write_file`** (`sandbox write` in the CLI) — for creating new files. To overwrite an existing file you
  must pass `overwrite: true` (it never silently clobbers).
- **`run_command`** (`sandbox run` in the CLI) — run any bash command in the sandbox (build, install,
  scaffolding, codemods). The working directory defaults to the app root; `cd`
  does not persist across calls, so use the `cwd` parameter or chain commands
  (`cd sub && cmd`). Timeout defaults to 120s (max 600s); output is capped at
  ~1 MB.
- **`create_checkpoint`** (`sandbox checkpoint` in the CLI) — save a named
  restore point the user can later roll back to. Takes an optional `name`
  (message/title; auto-generated if omitted). Any pending changes are **flushed
  and committed first** so the checkpoint anchors to your latest code; it then
  returns the checkpoint id, name, and git commit hash. Use it to mark a
  known-good state before or after a chunk of edits. (If a recent auto-commit
  can't be confirmed durable yet, it refuses with the retryable
  `COMMIT_FLUSH_PENDING` rather than checkpoint stale state — retry shortly.)

Example:

```
On appId <APP_ID>, use edit_file to change the homepage heading in
src/pages/Home.jsx from "Welcome" to "Welcome back". Show me the diff first
with dry_run, then apply it.
```

---

## 5. Preview and verify (the edit → check loop)

There is no live log-streaming tool, but you can close the feedback loop:

- **See it live:** `get_app_preview_url` brings up the dev server and returns
  the preview URL. Vite HMR reflects your edits as you make them.
- **Build status:** `get_app_status` returns `ready` / `processing` / `error`.
- **Surface build/type/lint errors on demand** with `run_command`:
  ```bash
  npm run build       # bundler/compile errors
  npx tsc --noEmit    # type errors
  npm run lint        # lint errors
  ```
- **Read the dev-server (Vite) logs** — the managed dev server writes to
  `/tmp/vite.log`. Tail it via `run_command` to see HMR/compile errors:
  ```bash
  tail -c 32000 /tmp/vite.log
  ```
  (This is outside the app tree, so it's only reachable through `run_command`,
  not the file tools — and therefore needs `sandbox:write`.)

A solid loop: `edit_file` → `npm run build` (or tail `/tmp/vite.log`) → fix any
errors → `get_app_preview_url` to eyeball it.

> **Browser-runtime errors** (a component that compiles but throws on render,
> a failing client API call) appear in the browser console, not in
> `/tmp/vite.log`. Open the preview URL to catch those.

---

## 6. How your changes persist

You don't need to "save." Every mutating call schedules a **debounced
auto-commit** (~5 seconds): the change is committed and pushed to Base44's code
storage, so it:

- survives sandbox death (the sandbox is recreated from the last commit),
- appears in the builder's Library/Data tabs,
- keeps backend-function deploys consistent, and
- is included when you publish the app.

Practical implications:

- There's a small loss window (~5s) — don't kill the session immediately after
  the last edit; give it a moment to commit.
- Edits to entities, agents, workflows, backend functions, and page routing are
  synced into Base44 automatically after the commit. Plain page/component/CSS
  edits live in git and need nothing extra.

---

## 7. Concurrency: you vs. the Base44 builder

You and the in-app Base44 builder can't mutate the same app at once:

- **While you're actively using the sandbox tools**, the Base44 builder chat is
  blocked ("An external agent is currently working on this app"). Your session
  is implicit — recent tool calls *are* the session; it ends after a short idle
  period (~10 min).
- **If the Base44 builder is mid-build**, your mutating tools return
  `BUILDER_BUSY`. Poll `get_app_status` and retry once it's `ready`. Read-only
  tools still work during a build.

---

## 8. Guardrails & limits

- **Paths are confined to the app.** File tools operate only within the app
  directory; traversal/absolute paths are rejected (`PATH_OUTSIDE_SANDBOX`).
- **`.agents/` is off-limits to file tools** (`PROTECTED_PATH`) — it holds
  agent-managed config and secrets (`.agents/.env`). Don't try to read or edit
  it through the file tools.
- **Rate limits** apply per app: reads ~120/min, mutations ~60/min, commands
  ~30/min. If you hit `RATE_LIMITED`, slow down.
- **`delete_file` isn't a dedicated tool** — delete via `run_command rm`.

### Error codes you may see

`NOT_AUTHORIZED` (missing scope/flag) · `APP_NOT_FOUND` (wrong id or no access)
· `PATH_OUTSIDE_SANDBOX` · `PROTECTED_PATH` · `NOT_FOUND` · `BINARY_FILE` ·
`EDIT_TEXT_NOT_FOUND` · `EDIT_TEXT_NOT_UNIQUE` (make `old_text` unique or use
`replace_all`) · `OVERWRITE_NOT_ALLOWED` (pass `overwrite: true`) · `TIMEOUT` ·
`OUTPUT_TRUNCATED` · `BUILDER_BUSY` ·
`COMMIT_FLUSH_PENDING` (a pending auto-commit isn't durable yet; retry shortly —
e.g. on `create_checkpoint`) · `RATE_LIMITED` · `BACKEND_ERROR`.

Messages are written so the agent can self-correct — read them and adjust.

---

## 9. Tips & tricks

- **Read before you write.** A quick `list_directory` + `read_file` (or `grep`)
  pass costs little and dramatically improves edit accuracy.
- **Use `dry_run` on `edit_file`** to confirm the diff before committing to a
  change, especially for multi-edit calls.
- **Prefer `edit_file` over `write_file`** for existing files — surgical edits
  avoid clobbering and produce a reviewable diff.
- **Read line ranges** with `read_file`'s `offset`/`limit` on large files
  instead of pulling the whole thing into context.
- **When something "looks broken," tail `/tmp/vite.log`** before guessing —
  it usually names the exact file and line.
- **Let it commit.** Pause a few seconds after your final edit so the auto-commit
  lands before you disconnect or publish.
- **Checkpoint known-good states.** Use `create_checkpoint` (`sandbox checkpoint`)
  to mark a restore point before or after a risky chunk of edits — it flushes
  pending changes first, so the user can always roll back to that point.
- **One agent at a time.** The feature is designed for a single external agent
  per app; don't run parallel sessions against the same app.

---

## 10. Local agents via the `base44 sandbox` CLI

If your agent runs on your machine, it can drive the same sandbox through the Base44 CLI instead of
MCP, authenticating with the Base44 CLI instead of OAuth. Same tools, same behavior, same error
codes (Section 8) — only the surface and auth differ.

**Auth.** Log in with the Base44 CLI (`base44 login`) — the same credential used for
`base44 functions deploy`. Like the projectless `base44 connectors` commands, the sandbox
subcommands resolve the app id from `--app-id`, then `BASE44_APP_ID`, then a local `.app.jsonc`;
no `config.jsonc` is required.

**Command names.** The CLI exposes each sandbox tool under a shorter name:

| MCP tool | CLI command |
|---|---|
| `list_directory` | `base44 sandbox ls` |
| `read_file` | `base44 sandbox read` |
| `write_file` | `base44 sandbox write` |
| `edit_file` | `base44 sandbox edit` |
| `run_command` | `base44 sandbox run` |
| `grep` | `base44 sandbox grep` |
| `create_checkpoint` | `base44 sandbox checkpoint` |

```bash
npx base44 sandbox read --app-id <APP_ID> src/App.jsx
```

`base44 sandbox checkpoint` takes an optional `--name` (message/title) and saves a restore point:

```bash
npx base44 sandbox checkpoint --app-id <APP_ID> --name "before refactor"
```

**Hand an agent the full reference** for a specific app (instructions, public, no
auth needed to fetch):

```
https://app.base44.com/api/sandbox/<APP_ID>/local-agent/readme.md
```

(The cloud/MCP equivalent is `.../api/sandbox/<APP_ID>/claude-web/readme.md`.)

Everything else in this skill — the edit→preview→verify loop (Section 5), persistence
(Section 6), concurrency (Section 7), and guardrails (Section 8) — applies identically; only the
surface and auth differ.

---

## 11. Connectors (OAuth integrations)

Beyond the sandbox file/shell tools, the Base44 MCP server exposes two tools for managing a
third-party OAuth connector (Google Calendar, Gmail, Slack, …) on an app. They don't touch the
sandbox filesystem — they operate on the app's connector state directly. Both take `appId`.

| Tool | Scope | Purpose |
|---|---|---|
| `list_connectors` | `apps:read` | List the app's connectors. With no `integrationTypes`, returns the full catalog (name, description, connected?, and — if connected — status and granted scopes). Pass `integrationTypes` for detail on specific ones. |
| `initiate_connector_connection` | `apps:write` | Connect (or re-scope) a connector. Inputs: `appId`, `integrationType`, `scopes`, optional `connectionConfig`. |

Two semantics to get right:

- **Declarative scopes (replace, not merge).** `initiate_connector_connection` sets the connector
  to **exactly** the `scopes` you pass. Omitted scopes are removed and the user is re-prompted to
  consent. **Always call `list_connectors` first**, then pass the complete desired set (existing
  scopes you want to keep **plus** any new ones).
- **OAuth needs a human.** The tool returns either `already_authorized: true` (nothing to do) or a
  `redirect_url` the **user** must open in a browser to sign in and consent — you can't complete it
  yourself. After they finish, call `list_connectors` again to verify and read the **granted**
  scopes (a provider may grant fewer than requested).

These need only `apps:read` / `apps:write` — **not** `sandbox:write`. Over the CLI surface
(Section 10), the equivalent is the projectless `base44 connectors` commands
(`list-available`, `initiate --integration-type <t> --scopes <s...> --app-id <id>`, `pull`), which
print the same authorization URL.
