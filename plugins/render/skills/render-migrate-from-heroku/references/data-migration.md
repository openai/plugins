# Data Migration Guide

Detailed steps for migrating Postgres and Redis data from Heroku to Render. The Render CLI's [`render psql`](https://render.com/docs/cli) handles the Postgres restore without requiring the Render database connection string.

## 5a. Pre-migration checks

Before generating any migration commands, verify readiness:

1. **Render Postgres is provisioned** — call `list_postgres_instances()` to find the Postgres ID and confirm the database exists. Note the ID for `render psql` in Step 5c.
2. **Render Key Value is provisioned** (if Redis data needs migrating) — call `list_key_value()` to find the Key Value ID and confirm the instance exists. Note the ID for the Dashboard deeplink in Step 5d.
3. **Check source database size** — use Heroku MCP `pg_info` (look for `Data Size`), or ask the user to run `heroku pg:info -a <app>` and paste the output.
4. **Compare disk sizes** — warn if Heroku `Data Size` exceeds the `diskSizeGB` configured on the Render side. If it does, the user needs to increase `diskSizeGB` before restoring.
5. **Render CLI** — confirm the Render CLI is installed and authenticated (required for `render psql` restore):

   ```bash
   render --version
   render whoami
   ```

   If not installed, offer to install it:
   - macOS: `brew install render`
   - Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh`

   If not authenticated, run `render login` to authorize via the Dashboard.

6. **`pg_dump` and `pg_restore`** — check that the user has PostgreSQL client tools installed locally:

   ```bash
   pg_dump --version
   pg_restore --version
   ```

   Both are needed: `pg_dump` for all approaches, `pg_restore` for the traditional approach (databases over 2 GB). If not installed, suggest installing PostgreSQL client tools (e.g., `brew install libpq` on macOS, `apt install postgresql-client` on Linux).

7. **Redis tools** (if migrating Redis data) — check for `redis-cli`:

   ```bash
   redis-cli --version
   ```

## 5b. Gather connection strings

Collect the connection strings needed for the migration. The **Render Postgres** connection string is **not needed** — the Render CLI's `render psql` command connects directly using the Postgres ID from Step 5a. Only the Heroku source URLs and the Render Key Value URL (if applicable) are needed.

**Heroku Postgres:**

If Heroku MCP is available:

```
pg_credentials(app: "<app>")
→ extract the connection URL from the response
→ store as HEROKU_DB_URL
```

If Heroku MCP is not available, ask the user to run `heroku pg:credentials:url DATABASE -a <app>` and paste the connection URL.

**Render Key Value** (if migrating Redis data):

The Render MCP does not return Key Value connection strings. Use the Key Value ID from Step 5a to construct a Dashboard deeplink and ask the user to copy the external connection URL:

```
Dashboard link: https://dashboard.render.com/d/<key-value-id>
→ ask user to open link, go to the Connections tab, copy the External Access URL
→ store as RENDER_REDIS_URL
```

**Heroku Redis** (if migrating Redis data):

If Heroku MCP is available:

```
get_app_info(app: "<app>")
→ read REDIS_URL from the config vars in the response
→ store as HEROKU_REDIS_URL
```

If Heroku MCP is not available, ask the user to run `heroku config:get REDIS_URL -a <app>` and paste the value.

**Important:** Substitute all retrieved values into the commands in the following steps. Never present commands with placeholder URLs — always use the real connection strings.

## 5c. Postgres migration

Generate commands with the Heroku connection string from Step 5b and the Render Postgres ID from Step 5a substituted in. Present the full sequence to the user.

**1. Put Heroku in maintenance mode** to stop writes during the migration:

Use `maintenance_on` via Heroku MCP if available, or tell the user to run:

```bash
heroku maintenance:on -a <app>
```

**2. Dump and restore** — choose the approach based on database size (use `Data Size` from `pg_info` in Step 5a):

**Render CLI approach** (databases under 2 GB — simplest, no Render connection string needed):

Uses plain-text SQL dump and the [Render CLI's `render psql`](https://render.com/docs/cli) in non-interactive mode, which connects directly using the Postgres ID.

```bash
# Dump from Heroku (plain-text SQL format)
pg_dump --clean --no-acl --no-owner -d <HEROKU_DB_URL> > heroku_dump.sql
# Restore to Render via CLI
render psql <postgres-id> --confirm -o text -- -f heroku_dump.sql
```

Replace `<postgres-id>` with the Render Postgres ID from Step 5a (e.g., `dpg-abc123`).

**Traditional approach** (databases 2-50 GB — faster, compressed, supports parallel restore):

Uses custom-format dump with `pg_restore`. Requires the Render **external connection string** — ask the user to copy it from the Render Dashboard:

```
Dashboard link: https://dashboard.render.com/d/<postgres-id>
→ ask user to open link, go to the Connection tab, copy the External Connection String
→ store as RENDER_DB_URL
```

Then generate:

```bash
# Dump from Heroku (compressed custom format)
pg_dump -Fc --no-acl --no-owner -d <HEROKU_DB_URL> > heroku_dump.dump
# Restore to Render (parallel with 4 jobs)
pg_restore --clean --no-acl --no-owner -j 4 -d <RENDER_DB_URL> heroku_dump.dump
```

For pipe approach (avoids local disk usage):

```bash
pg_dump -Fc --no-acl --no-owner -d <HEROKU_DB_URL> | pg_restore --clean --no-acl --no-owner -d <RENDER_DB_URL>
```

Note: the pipe approach cannot use `-j` for parallel restore.

**Very large databases** (over 50 GB): recommend the user [contact Render support](https://render.com/contact) for assisted migration. Do not generate commands — the process requires coordination.

Replace `<HEROKU_DB_URL>` with the actual Heroku connection string from Step 5b, and `<RENDER_DB_URL>` with the external connection string from the Dashboard. The user should see ready-to-run commands with real values.

Remind the user to schedule a maintenance window. The app will be unavailable on Heroku from maintenance mode until DNS cutover to Render.

## 5d. Key Value / Redis migration

Most Heroku Redis instances are used as ephemeral caches and do not need data migration. Ask the user before proceeding:

- **Ephemeral cache** (most common) — skip migration. The app will repopulate the cache after deployment on Render. No action needed.
- **Persistent data** — if the user confirms Redis holds persistent data (e.g., session store, queues, application state), generate migration commands using the connection strings from Step 5b:

  ```bash
  # Dump from Heroku Redis
  redis-cli -u <HEROKU_REDIS_URL> --rdb heroku_dump.rdb
  # Restore to Render Key Value (requires redis-cli 5.0+)
  redis-cli -u <RENDER_REDIS_URL> --pipe < heroku_dump.rdb
  ```

  Replace `<HEROKU_REDIS_URL>` with the Heroku Redis URL and `<RENDER_REDIS_URL>` with the Render Key Value External Access URL, both from Step 5b. Present ready-to-run commands with the real values.

  Note: RDB dump/restore may not be supported on all Heroku Redis plans. If it fails, the alternative is per-key `DUMP`/`RESTORE` or having the application re-seed the data.

## 5e. Data validation

After the user confirms the restore completed, validate data before moving to Step 6:

**1. Check schema exists on Render:**

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
)
```

**2. Compare row counts on key tables:**

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT 'users' AS tbl, count(*) FROM users UNION ALL SELECT 'orders', count(*) FROM orders"
)
```

Adjust the table names to match the app. Pick 2-3 key tables that represent the core data.

**3. Compare against Heroku source** (if Heroku MCP is available):

```
pg_psql(app: "<app>", command: "SELECT 'users' AS tbl, count(*) FROM users UNION ALL SELECT 'orders', count(*) FROM orders")
```

**4. Present a side-by-side summary:**

```
DATA VALIDATION
─────────────────────────────
Table     | Heroku  | Render
users     | 12,450  | 12,450  ✅
orders    | 84,321  | 84,321  ✅
products  | 1,203   | 1,203   ✅
─────────────────────────────
```

If counts don't match, warn the user and suggest re-running the restore. Do not proceed to Step 6 until validation passes.
