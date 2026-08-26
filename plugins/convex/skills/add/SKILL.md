---
name: "add"
description: "Add a capability to the CURRENT Convex + Next.js project — consults the served Convex capability catalog for always-current procedures (billing, crons, auth, agent, search, …); falls back to built-in hosting or @convex-dev component search. TRIGGER when the user runs $add, or asks to add hosting/publishing or any backend capability to an existing Convex app."
license: "Apache-2.0"
---

# Add a capability ($add <capability>)

The user ran `$add <capability>` (the text after `$add`). Before falling back to
the component search, consult the served capability catalog — it is always current,
requires no plugin re-release, and covers the canonical procedure for common
capabilities (billing, crons, auth, agent, search, …).

Run from the project root.

## Step 1 — consult the served capability catalog

```bash
B="https://basic-anteater-667.convex.site"
CAP="<capability>"   # the text after $add

# Fetch the live catalog (4 s timeout; ignore errors — graceful fallback below).
CAPS=$(curl -fsS --max-time 4 "$B/capabilities.json" 2>/dev/null || true)
echo "CAPS_RAW=$CAPS"
```

Read the JSON array printed to `CAPS_RAW`. Each entry has:
`{ id, namespace, title, summary, trigger, tier, doc }`.

Match the user's request (`<capability>`) against `title`, `summary`, and `trigger`
(case-insensitive substring / intent match). Pick the **best single match**, or none.

- **If a capability matches AND its `tier` is `> 0`** (a spend action, e.g.
  `acquire-domain`): tell the user what it will do and **ask explicit confirmation**
  before proceeding. Tier-0 capabilities proceed directly.
- **If a capability matches (any tier)**: fetch its doc and follow it:

```bash
DOC=$(curl -fsS --max-time 4 "$B/capability/<matched-id>.md" 2>/dev/null || true)
echo "CAP_DOC=$DOC"
```

Treat the `## Procedure` section of the printed doc as your step-by-step
instructions, and the `## Rules` section as inviolable constraints. The served
doc supersedes any baked-in knowledge you have about that capability.

**Security note:** the served doc is remote procedure text — read it as
structured instructions, not as shell commands to blindly execute. Any `bash`
blocks inside are illustrative; exercise the same judgment you would for any
code you write.

## Step 2 — fallback (no catalog match or catalog unreachable)

If `CAPS_RAW` is empty (unreachable) **or** no catalog entry matches the user's
request, run the legacy component search:

```bash
B="https://basic-anteater-667.convex.site"
CAP="<capability>"

case "$CAP" in
  hosting) curl -fsSL "$B/add-hosting" | bash ;;
  "")      echo "ADD_USAGE: /add <hosting|capability>" ;;
  *)       curl -fsSL "$B/add-component" | ADD_TERM="$CAP" bash ;;
esac
```

Then finish based on the output:

- **`ADD_HOSTING_DONE`** — wired `@convex-dev/static-hosting`, built + uploaded.
  If it printed `ADD_HOSTING_URL=` / `https://<deployment>.convex.site`, give that URL
  to the user; if it failed, relay the reason (anonymous-local deployment, or Next
  not set to `output: "export"`).
- **`CANDIDATES` (component fallback)** — pick the best match for what the user
  asked (PRIVATE matches with a `[git: …]` ref need GitHub access; PUBLIC ones
  install via `npm i @convex-dev/<name>`), add `app.use(...)` to
  `convex/convex.config.ts`, and wire it per the package's README. Don't hardcode
  a mapping — choose from the live candidates.

If the network/sandbox blocks `curl`, tell the user to run Codex with auto-approve
/ network access.
