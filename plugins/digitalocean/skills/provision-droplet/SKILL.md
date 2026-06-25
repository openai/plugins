---
name: provision-droplet
description: >
  Use when the user wants to spin up / create / launch / provision a
  DigitalOcean droplet (or "a remote dev box on DO") and connect to it from
  Codex as a remote SSH workspace.
---

# Provision a DigitalOcean droplet as a Codex remote workspace

Follow these steps in order. Do not skip or reorder them.
**Only the installed Codex DigitalOcean app tools and the bundled Python scripts
may be used. doctl, ad hoc integration configs, and any other DigitalOcean CLI
tools are prohibited.**

## Before you start

- **Prerequisites:** a funded DigitalOcean account, the installed and
  authenticated Codex **DigitalOcean** app, a local `ssh`/`ssh-keygen`
  (OpenSSH), Python 3, and the Codex desktop app.
- **Cost:** the droplet bills **hourly from creation until you delete it**.
  Sizes in step 5 show approximate monthly rates. Remind the user to delete it
  when done (see *Cleanup* below).
- **Time:** end-to-end takes ~10–15 minutes — roughly 7 minutes waiting for the
  droplet to boot (steps 7-8) plus up to 7 minutes for cloud-init (step 9). This
  is normal; do not abort.
- **Locate the bundled scripts first (do this before Step 2).** The helper
  scripts live in the `scripts/` folder **next to this `SKILL.md`** (i.e.
  `provision-droplet/scripts/`). Your current working directory is **not** the
  skill directory, so bare relative paths like `scripts/keygen.py` will fail.
  Resolve the absolute directory that contains this `SKILL.md` and call it
  `<skill_dir>`. If you don't already know it, find it — the installed plugin may
  nest it under a version folder (e.g. `.../<version>/provision-droplet/`), so
  locate the directory that actually contains `scripts/keygen.py`. Use
  `<skill_dir>/scripts/<name>.py` (an absolute path) in **every** command below.

## Step 1 — Verify DigitalOcean app access

This plugin depends on the single Codex **DigitalOcean** app. Use it for all
DigitalOcean operations; do not register or log in to separate plugin-owned app
integrations.

The **DigitalOcean** app provides both:
- SSH key tools: `key-create`, `key-list`, `key-delete`.
- Droplet tools: `droplet-create`, `droplet-get`, `droplet-delete`.

Confirm that these tools are available before continuing. If the app's tools are
missing or unauthenticated, stop and tell the user to install or authenticate
the DigitalOcean app in Codex. Do not fall back to doctl, API tokens, or a local
integration config.

## Step 2 — Generate SSH key pair

```bash
python3 <skill_dir>/scripts/keygen.py
```

Parse the JSON output and keep these values for the steps below:
`prefix`, `name`, `key_name`, `key_path`, `pub_key`.

How these relate (all derived from one random `prefix` like `bright-hawk-a3f2`):
- `name` = `codex-<prefix>` — the **droplet name** and the **local SSH alias**
  (they are identical).
- `key_name` = `codex-key-<prefix>` — the label for the key on DigitalOcean's
  side only.
- `key_path` — the local private key file.

## Step 3 — Upload SSH public key

Call the **DigitalOcean** app tool **`key-create`**:

| Parameter | Value |
|-----------|-------|
| `Name` | `key_name` from step 2 |
| `PublicKey` | `pub_key` from step 2 |

Extract `ssh_key.id` from the response — this is `<key_id>`.

If the call fails because a key with that name or fingerprint **already exists**
(e.g. a previous run), do not create a duplicate: call the **DigitalOcean** app
tool **`key-list`**, find the entry whose `name` matches `key_name` (or whose
fingerprint matches the uploaded key), and use its `id` as `<key_id>`.

## Step 4 — Choose a region

Ask the user, in chat:

> Use the defaults — region **`nyc3`** (New York, US) and size
> **`s-2vcpu-4gb`** (2 vCPU / 4 GB, ~$24/mo) — or customize them?

If they choose the defaults, use `nyc3` as `<region>` and `s-2vcpu-4gb` as
`<size>`, then skip step 5 and continue to step 6.

If they want to customize the defaults, present this region list first and ask
them to reply with a slug:

| Slug | Location |
|------|----------|
| `nyc3` *(default)* | New York, US |
| `sfo3` | San Francisco, US |
| `tor1` | Toronto, CA |
| `lon1` | London, UK |
| `fra1` | Frankfurt, DE |
| `ams3` | Amsterdam, NL |
| `sgp1` | Singapore, SG |
| `blr1` | Bangalore, IN |
| `syd1` | Sydney, AU |

Validate their reply against this table. If it is not one of these slugs, ask
again — do not pass an unlisted value through. The chosen slug is `<region>`.

## Step 5 — Choose a droplet size

Skip this step if `<size>` was already set to the default in step 4.

Otherwise, present this size list and ask the user to reply with a slug. Every
size below is above the **1 vCPU / 2 GB** floor required by the Codex Universal
image. Prices are approximate — confirm in the DigitalOcean dashboard.

| Slug | vCPU | RAM | Tier | ~$/mo |
|------|------|-----|------|-------|
| `s-2vcpu-4gb` *(default)* | 2 | 4 GB | Shared basic | $24 |
| `s-4vcpu-8gb` | 4 | 8 GB | Shared basic | $48 |
| `s-8vcpu-16gb` | 8 | 16 GB | Shared basic | $96 |
| `c-2` | 2 | 4 GB | Premium CPU-optimized | $42 |
| `g-2vcpu-8gb` | 2 | 8 GB | Premium general-purpose | $63 |

Validate their reply against this table. If it is not one of these slugs, ask
again — do not pass an unlisted value through. The chosen slug is `<size>`.

## Step 6 — Create droplet

Call the **DigitalOcean** app tool **`droplet-create`**:

| Parameter | Value | Notes |
|-----------|-------|-------|
| `Name` | `name` from step 2 | |
| `Region` | `<region>` from step 4 | |
| `Size` | `<size>` from step 5 | |
| `ImageID` | `234061005` | DigitalOcean **Codex Universal** image |
| `SSHKeys` | `["<key_id>"]` | |

Extract `droplet.id` from the response — this is `<droplet_id>`.

If `droplet-create` fails, show the user the error and handle it by cause — do
not blindly retry the same values:
- **Size not available in this region** (premium tiers like `c-2` and
  `g-2vcpu-8gb` are not in every region): go back to step 4 or 5 and pick a
  different region/size combination.
- **Payment / quota / limit** errors: stop and tell the user to resolve it in
  the DigitalOcean dashboard, then re-run.
- **Invalid image or any other error:** stop and report it.

The uploaded SSH key from step 3 is harmless to leave, but if you abort here see
*Cleanup* below.

## Step 7 — Schedule delayed deployment check-in

After `droplet-create` succeeds, inspect the response before polling. If the
droplet is not already `active` with a public IPv4 address in the create
response, assume provisioning is still in progress.

Create a Codex **heartbeat** to resume this same thread in **5 minutes** for
the first status check. Use the Codex automation tool, not a shell sleep or
local timer:

| Field | Value |
|-------|-------|
| `mode` | `create` |
| `kind` | `heartbeat` |
| `destination` | `thread` |
| `name` | `Check DigitalOcean droplet <name>` |
| `rrule` | `FREQ=MINUTELY;INTERVAL=5` |
| `status` | `ACTIVE` |
| `prompt` | `Resume provisioning DigitalOcean droplet <name> (<droplet_id>). Start at Step 8: check whether it is active and has a public IPv4 address, then continue the workflow. The droplet bills hourly until deleted.` |

After creating the heartbeat, tell the user the droplet was created and Codex
will check back in about 5 minutes. **Stop the active turn here.** Do not start
20-second polling until the heartbeat wakes the thread back up. This avoids
busy-waiting during the normal 5-7 minute deployment window.

Keep the created heartbeat's automation id as `<heartbeat_id>` if the tool
returns one. When the heartbeat resumes the thread, use step 8 to decide
whether to keep checking or to delete/pause the heartbeat and continue.

If the create response already includes `status == "active"` and a public IPv4
address, skip the heartbeat and continue immediately to step 8.

## Step 8 — Check whether the droplet is active

Call the **DigitalOcean** app tool **`droplet-get`** once with
`ID: <droplet_id>`.

If the response has `status == "active"` **and** `networks.v4` contains an
entry with `type == "public"`, extract `ip_address` from that entry — this is
`<ip>`. Delete or pause `<heartbeat_id>` if it still exists, then continue to
step 9.

If the droplet is still not active or does not yet have a public IPv4 address,
schedule Codex to check this same thread again in **1 minute**, then **stop the
active turn here**. Keep checking back every minute until the droplet is ready;
do not give up merely because the DigitalOcean deployment is slow. Prefer
updating the existing `<heartbeat_id>` to a 1-minute interval; if that is not
possible, create a replacement heartbeat and delete/pause the old one so there
is only one active check-in.

Use these values for the 1-minute follow-up heartbeat:

| Field | Value |
|-------|-------|
| `mode` | `create` or `update`, depending on the available automation tool |
| `kind` | `heartbeat` |
| `destination` | `thread` |
| `name` | `Check DigitalOcean droplet <name>` |
| `rrule` | `FREQ=MINUTELY;INTERVAL=1` |
| `status` | `ACTIVE` |
| `prompt` | `Resume provisioning DigitalOcean droplet <name> (<droplet_id>). Start at Step 8: check whether it is active and has a public IPv4 address, then continue the workflow. If it is still not ready, schedule another 1-minute heartbeat. The droplet bills hourly until deleted.` |

Keep all status checks with the DigitalOcean app — do not use doctl or any other
tool to check droplet status.

## Step 9 — Configure local SSH

```bash
python3 <skill_dir>/scripts/configure_ssh.py \
  --alias codex-<prefix> \
  --ip <ip> \
  --user root \
  --key-path <key_path>
```

**⚠️ Do not interrupt this step.** It waits for cloud-init to finish (up to 7
minutes) and prints a `⏳` status line every 5 seconds — that output means it is
working normally. **Do not run any other commands. Wait for the line
`DROPLET READY`.** If the script exits with an error instead, report it and
offer to delete the droplet (see *Cleanup*).

## Final step: adding it to Codex

Ask Codex to open the add-SSH-host flow by responding with a clickable Markdown
link. Replace `<ssh-alias>` with `name` from step 2:

`[Add <ssh-alias> to Codex SSH](codex://settings/connections/ssh/add?name=<ssh-alias>)`

The SSH alias is the local host alias created by step 9. In this workflow, it is
the same value as the droplet name: `codex-<prefix>`.

If the link does not open the flow, or if the user wants to check it manually,
tell them to open: **Codex App → Settings → Connections → Add SSH Host → pick
the alias → choose the remote folder.**

## Cleanup (on failure or when done)

The droplet bills hourly until deleted. To tear down:

1. **Delete the droplet** — **DigitalOcean** app tool **`droplet-delete`** with
   `ID: <droplet_id>`.
2. **Delete the SSH key** (optional) — **DigitalOcean** app tool **`key-delete`**
   with the `<key_id>` from step 3.

Always confirm with the user before deleting. Do not use doctl for cleanup.
