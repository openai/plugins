---
name: setup-metabase-mcp
description: Read these instructions before using Metabase MCP tools. Setup is needed to connect to Metabase instances through the Metabase app-backed connector.
---

**Read this entire skill file end-to-end before taking any action.** Do not skim, do not stop at the first matching step, and do not act on the summary alone. The gates, failure modes, prohibitions, and post-setup rules are scattered through the document.

**Follow these instructions exactly as written.** Do not make assumptions, do not silently substitute "equivalent" actions, and do not bypass the app-backed connector flow. If a step says stop, stop.

---

Configure the Metabase Codex plugin so the user can connect to a ready Metabase instance through the Metabase app-backed connector. This skill assumes the instance itself is already set up and has the MCP feature enabled - that is the job of the `setup-metabase-instance` skill, not this one.

The plugin is app-backed. `../../.app.json` is a static app mapping, not a per-user runtime config file. Do not rewrite `.app.json` with the user's Metabase URL, and do not create or restore `.mcp.json` as a workaround.

## Valid Instance URL Formats

- Local development: `http://localhost:3000`
- Metabase Cloud: `https://yourcompany.metabaseapp.com`
- Self-hosted: `https://metabase.yourcompany.com`

## Required Actions

1. Read `../../.app.json` (relative to this `SKILL.md` - two directories up, the plugin root). It must contain a Metabase app entry with a non-empty app or connector ID.

   Expected shape:

   ```json
   {
     "apps": {
       "metabase": {
         "id": "template_app_6a044bbd332881919b553bdfc2240952"
       }
     }
   }
   ```

   If `apps` is empty or there is no `metabase` entry, stop and tell the user:

   > This Metabase plugin is missing its Codex app mapping. Ask the plugin maintainer to add the Metabase app or connector ID to `.app.json`, reinstall the plugin, and start a new chat.

   Do not continue, do not edit `.app.json`, and do not run `codex mcp login`.

2. Stop all other exploration. Ask the user: "Do you have a Metabase instance URL, or would you like to set up a local instance?"

   - **If they provide a URL**: continue with step 3.
   - **If they don't have one and want to set up a local instance**: invoke the `setup-metabase-instance` skill. That skill spins up Metabase, walks the user through first-run setup, and returns with a ready URL (typically `http://localhost:3000`). Continue here with that URL.

3. Sanity-check that the URL points at a **ready-to-use** Metabase instance. Run all three probes:

   ```bash
   curl -s <INSTANCE_URL>/api/session/properties | grep -o '"tag":"[^"]*"'
   curl -s <INSTANCE_URL>/api/session/properties | grep -o '"has-user-setup":[a-z]*'
   curl -s -o /dev/null -w "%{http_code}\n" <INSTANCE_URL>/api/mcp
   ```

   All three must pass:

   - Version tag's major version is **>= 60**.
   - `"has-user-setup":true` - instance has an admin account and is past the first-run wizard.
   - `/api/mcp` response code is **`401`** - endpoint live, OAuth required.

   If any fails, **stop**. Do not run OAuth and do not modify plugin files. Failure modes:

   - **`has-user-setup:false`** - the instance is running but has never been initialized. If this is the local instance launched through this workflow, forward to the `setup-metabase-instance` skill so its Gate 1 walks the user through the first-run wizard. If this is a user-supplied Cloud or self-hosted URL, tell the user to open `<INSTANCE_URL>` in their browser, complete the first-run wizard there, and then come back so you can re-run step 3 here.
   - **Version < 60** - tell the user to upgrade Metabase, then stop.
   - **`/api/mcp` returns `404`** - MCP is on by default in 60+ and has no toggle, so this usually means the version is older than reported or the URL is wrong. Ask the user to confirm.
   - **Other HTTP codes** - surface the code to the user and stop.

   **Never call `POST /api/setup`, `POST /api/session`, or any other authenticated Metabase REST endpoint.** Those bypass the OAuth flow this skill depends on. If the user asks you to, refuse.

4. Hand the user to the app-backed connection flow. Tell them:

   > Your Metabase instance is ready. Connect the Metabase app in Codex using this URL: `<INSTANCE_URL>`. Complete the OAuth approval in Metabase, then start a new chat so the app tools are available.

   Do not run `codex mcp login`. This plugin no longer registers a local `.mcp.json` MCP server; authentication belongs to the Codex app connector.

5. Tell the user to start a new chat so the app config and token take effect:

   - **Codex CLI**: `/new`
   - **Codex Desktop**: click **New chat** in the sidebar

   Confirm setup is complete and **stop**. The Metabase tools become available in the new thread.

## After setup: do NOT bypass MCP

Once the app connector is configured, the **only** way to read data from Metabase is through the Metabase app/MCP tools. Do not, under any circumstances:

- Read, copy, snapshot, or query Metabase's H2 application database file directly (`metabase.db`, `metabase.db.mv.db`, `metabase.db.h2.db`, etc.). Even read-only inspection or working from a copy is forbidden.
- Use `sqlite`, `duckdb`, `h2`, JDBC, JDBC tools, Python `sqlalchemy`/`h2`/`jaydebeapi`, or any other client to talk to Metabase's storage.
- Call Metabase REST endpoints (`/api/card`, `/api/dashboard`, `/api/database`, `/api/session`, etc.) to answer the user's question while the new chat is pending.
- Run any other side-channel that bypasses the configured app/MCP server.

If the running chat does not yet expose Metabase tools, the correct response is only to remind the user to start a new chat and stop. Do not offer to inspect internals.
