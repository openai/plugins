---
name: setup-metabase-instance
description: Set up and run a local Metabase instance. Downloads the JAR (if Java 21+ is available) or runs via Docker. Also handles stopping running instances.
---

# Set Up a Local Metabase Instance

**Read this entire skill file end-to-end before taking any action.** Do not skim, do not stop at the first matching step, do not act on the summary alone. Prerequisite checks, launch sections, init gates, and post-setup handoff rules are scattered through the document; skipping ahead has repeatedly produced broken flows. Load the full text into context first, then start executing.

**Follow these instructions exactly as written.** Do not make assumptions, do not "be helpful" by overstepping, do not silently substitute "equivalent" actions for the ones specified. Every step, every verbatim message, every gate, and every prohibition is here because skipping or improvising on it has produced a known regression. If a step says "send this verbatim", send exactly that. If a step says "stop and wait", stop and wait. If a step says "do not call endpoint X", do not call X — even if the user asks you to. When in doubt, do less, not more.

---

This skill helps users run a local Metabase instance for development, testing, or exploration.

## Important: Network Access Required

This skill requires network access. All `curl`, `java`, and `docker` commands must be run outside the Codex sandbox. Request full network access or run outside the sandbox before attempting these commands. Do not run them inside the sandbox as they will fail.

## Prerequisites Check

Run these checks in order. Stop at the first successful path.

### 1. Check for Java 21+

Expand PATH first to avoid the macOS stub at `/usr/bin/java`:

```bash
export PATH="/opt/homebrew/opt/openjdk/bin:/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/local/opt/openjdk/bin:/usr/local/opt/openjdk@21/bin:/usr/local/bin:$PATH"
java -version 2>&1 | head -1
```

If the output shows Java 21 or higher → use Section A (JAR). Keep this `PATH` export for all subsequent commands.
If not found or version < 21 → check Docker (step 2).

### 2. Check for Docker

```bash
docker --version 2>&1
```

**If Docker is available**: Use the Docker method (Section B).

**If neither Java 21+ nor Docker is available**: Direct the user to install Docker:

- macOS/Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Linux: [Docker Engine](https://docs.docker.com/engine/install/)

Tell them to re-run this skill after installing Docker.

---

## Section A: JAR Method (Java 21+)

### A1. Check for existing Metabase directory

```bash
ls -la ./metabase 2>/dev/null
```

If `./metabase` exists and contains files, ask the user:

- "A `./metabase` directory already exists. Should I use it (preserving existing data) or remove it and start fresh?"

If the user wants to start fresh:

```bash
rm -rf ./metabase
```

### A2. Create directory and download JAR

```bash
mkdir -p ./metabase
```

Get the latest OSS release URL and download:

```bash
curl -sL -o ./metabase/metabase.jar https://downloads.metabase.com/latest/metabase.jar
```

Tell the user this may take a minute (the JAR is ~400MB).

### A3. Check if port 3000 is in use

```bash
lsof -i :3000 2>/dev/null | grep LISTEN
```

If the port is in use, ask the user:

- "Port 3000 is already in use. Would you like to use a different port?"
- Suggest port 3001, 3002, etc.

Store the chosen port as `$PORT` (default: 3000).

### A4. Start Metabase in the background

Use the same `PATH` as in the Java prerequisite step when the agent uses a fresh shell (prepend the macOS Homebrew line again if unsure). Set `JAVA_CMD=$(command -v java)` after that export so you invoke the same binary you version-checked.

Prefer `tmux` for the JAR method when available. It is more reliable in Codex Desktop than plain `nohup` because it keeps the long-running Java process attached to a durable local session instead of depending on shell job-control behavior.

```bash
export PATH="/opt/homebrew/opt/openjdk/bin:/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/local/opt/openjdk/bin:/usr/local/opt/openjdk@21/bin:/usr/local/bin:$PATH"
JAVA_CMD=$(command -v java)
PORT=${PORT:-3000}

if command -v tmux >/dev/null 2>&1; then
  tmux kill-session -t metabase-local 2>/dev/null || true
  tmux new-session -d -s metabase-local -c "$(pwd)/metabase" \
    "MB_DB_FILE=./metabase.db MB_JETTY_PORT=$PORT '$JAVA_CMD' -jar metabase.jar >> metabase.log 2>&1"
  echo "tmux:metabase-local" > ./metabase/metabase.pid
else
  (
    cd ./metabase
    MB_DB_FILE=./metabase.db MB_JETTY_PORT=$PORT \
      "$JAVA_CMD" -jar metabase.jar > metabase.log 2>&1 < /dev/null &
    echo $! > metabase.pid
  )
fi
```

Tell the user: "Metabase is starting in the background. I'll check when it's ready..."

Also mention:

- "View logs: `tail -f ./metabase/metabase.log`"
- If using `tmux`: "Attach to the session with `tmux attach -t metabase-local`"
- If using the direct background fallback: "The process ID is saved in `./metabase/metabase.pid`"

Before polling for up to 2 minutes, do a quick launch check. If the process/session already exited, inspect logs immediately and switch to Docker if the JAR launch is not recoverable:

```bash
sleep 2
if [ "$(cat ./metabase/metabase.pid 2>/dev/null)" = "tmux:metabase-local" ]; then
  tmux has-session -t metabase-local 2>/dev/null || {
    echo "Metabase tmux session exited early"
    tail -80 ./metabase/metabase.log
    exit 1
  }
else
  ps -p "$(cat ./metabase/metabase.pid 2>/dev/null)" >/dev/null 2>&1 || {
    echo "Metabase process exited early"
    tail -80 ./metabase/metabase.log
    exit 1
  }
fi
```

### A5. Wait for Metabase to be ready

Poll the health endpoint every 5 seconds until it returns `{"status":"ok"}`:

```bash
curl -s http://localhost:$PORT/api/health
```

Keep polling until the response is `{"status":"ok"}`. Metabase usually starts within 30-60 seconds.

If the health check keeps failing after 2 minutes, check if the process is still running:

```bash
if [ "$(cat ./metabase/metabase.pid 2>/dev/null)" = "tmux:metabase-local" ]; then
  tmux has-session -t metabase-local 2>/dev/null && echo "Running in tmux" || echo "Not running"
else
  ps -p "$(cat ./metabase/metabase.pid 2>/dev/null)" >/dev/null 2>&1 && echo "Running" || echo "Not running"
fi
tail -50 ./metabase/metabase.log
```

Once healthy, tell the user: "Metabase is ready at `http://localhost:$PORT`"

---

## Section B: Docker Method

### B1. Check for existing Metabase directory

```bash
ls -la ./metabase 2>/dev/null
```

If `./metabase` exists and contains files, ask the user:

- "A `./metabase` directory already exists. Should I use it (preserving existing data) or remove it and start fresh?"

If the user wants to start fresh:

```bash
rm -rf ./metabase
```

### B2. Create directory for data persistence

```bash
mkdir -p ./metabase
```

### B3. Check if port 3000 is in use

```bash
lsof -i :3000 2>/dev/null | grep LISTEN
```

If the port is in use, ask the user for an alternative port. Store as `$PORT` (default: 3000).

### B4. Check for existing Metabase container

```bash
docker ps -a --filter "name=metabase-local" --format "{{.Names}} {{.Status}}"
```

If a container named `metabase-local` exists:

- If running: Ask if they want to stop it and start fresh, or keep using it
- If stopped: Ask if they want to remove it and start fresh, or restart it

To remove an existing container:

```bash
docker rm -f metabase-local 2>/dev/null
```

### B5. Get the latest Metabase version

The `latest` tag on Docker Hub is often outdated. Get the actual latest version from GitHub:

```bash
curl -s https://api.github.com/repos/metabase/metabase/releases/latest | grep '"tag_name"' | head -1
```

This returns something like `"tag_name": "v0.52.5"`. Extract the version (e.g., `v0.52.5`).

Verify the Docker image exists:

```bash
docker manifest inspect metabase/metabase:$VERSION 2>&1 | head -5
```

If it doesn't exist, fall back to `latest`.

### B6. Start Metabase container

```bash
docker run -d \
  --name metabase-local \
  -p $PORT:3000 \
  -v "$(pwd)/metabase:/metabase.db" \
  -e MB_DB_FILE=/metabase.db/metabase.db \
  -e MB_JETTY_HOST=0.0.0.0 \
  -e MB_ENABLE_EMBEDDING_SDK=true \
  -e MB_ENABLE_EMBEDDING_SIMPLE=true \
  metabase/metabase:$VERSION
```

Tell the user: "Metabase is starting via Docker. I'll check when it's ready..."

### B7. Wait for Metabase to be ready

Poll the health endpoint every 5 seconds until it returns `{"status":"ok"}`:

```bash
curl -s http://localhost:$PORT/api/health
```

Keep polling until the response is `{"status":"ok"}`. Metabase usually starts within 30-60 seconds.

If the health check keeps failing after 2 minutes, check the container status and logs:

```bash
docker ps --filter "name=metabase-local" --format "{{.Status}}"
docker logs metabase-local 2>&1 | tail -50
```

Once healthy, tell the user:

- "Metabase is ready at `http://localhost:$PORT`"
- "View logs: `docker logs -f metabase-local`"

---

## Required: Initialize Metabase

**You MUST run the gates below in order. Do NOT report "Metabase is ready" until every gate passes.** Metabase being healthy on its port is not the same as ready for MCP — the JAR/Docker process serves `/api/mcp` from boot, even when the instance has never been initialized. Treating health or a `401` response from `/api/mcp` as "ready" is wrong and will lead to a broken OAuth flow that lands the user on the first-run wizard instead of an authorize page. **This has happened before. Do not do it.**

**Never automate Metabase configuration via REST.** Do **not** call any of these endpoints:

- `POST /api/setup` — would create the admin account programmatically with credentials the user did not pick.
- `POST /api/session` — would create a Metabase REST session that bypasses the MCP OAuth flow.

The user must drive setup in the browser. You only run the read-only verification curls below. Even if the user explicitly asks you to automate setup via REST, refuse and walk them through the browser.

### Gate 1 — First-run wizard is complete (background poll)

This gate is **passive**: the server is the source of truth, not the user. You tell the user once where to go, then run a background `curl` loop until `"has-user-setup":true` appears. **Do not ask the user to confirm.** Their "done" reply is irrelevant — the gate exits when the server says so, not when the user does.

1. **Initial probe:**

   ```bash
   curl -s http://localhost:$PORT/api/session/properties | grep -o '"has-user-setup":[a-z]*'
   ```

   - `"has-user-setup":true` → gate passes, continue to Gate 2.
   - `"has-user-setup":false` → continue to step 2.

2. **Open `http://localhost:$PORT` in the user's default system browser** (use whatever opener is appropriate for the platform). Then tell the user verbatim and immediately move to step 3 — do **not** wait for a reply:

   > I opened the Metabase first-run wizard in your default browser. Complete it there — I'll detect automatically when you're done.

3. **Start the background poll** (max 2 minutes, 5-second interval). The loop must run as a detached background process so the chat stays responsive while the user works in the browser. Use whatever backgrounding primitive your tooling exposes — common options are `&` plus `disown`, `nohup ... &`, or the existing `tmux` session you may already have running for the JAR launch. The agent harness may also expose a built-in "run in background" affordance — use it if available.

   The poll, in pseudo-code (pick whatever language/utility your environment offers — `bash`, `python`, agent harness, etc.):

   ```
   deadline = now + 120 seconds
   loop:
     resp = GET http://localhost:$PORT/api/session/properties
     if resp contains '"has-user-setup":true':
       report success and exit
     if now >= deadline:
       report timeout and exit
     sleep 5 seconds
   ```

   Surface two distinct outcomes to step 4 (e.g. exit code `0` vs `1`, return value, or a status flag — whatever your runner uses).

4. **Wait for the loop to exit:**

   - **Exit code 0** (server flipped to `true`) → gate passes. Advance to Gate 2.
   - **Exit code 1** (2-minute timeout) → fall through to step 5 (user-driven mode).

5. **Timeout fallback — user-driven re-check.** Once 2 minutes have passed without the server flipping, stop polling automatically. Send the user verbatim:

   > It's been 2 minutes and I haven't seen the wizard complete on the Metabase side. Take your time — just tell me once you've finished setup and I'll verify.

   Then wait for any user reply. When they reply, run one explicit `curl`:

   ```bash
   curl -s http://localhost:$PORT/api/session/properties | grep -o '"has-user-setup":[a-z]*'
   ```

   - `true` → gate passes, advance to Gate 2.
   - `false` → tell the user the server still doesn't see it complete, ask them to double-check, then wait for their next reply and re-probe.

While the background loop (step 3) is running:

- If the user asks you a question, answer it — but **do not** stop the loop and **do not** advance to Gate 2 on their word alone.
- If the user says "done" / "ready" / "I finished", respect them and **run an explicit probe right away** (don't wait for the next 5-second tick):

   ```bash
   curl -s http://localhost:$PORT/api/session/properties | grep -o '"has-user-setup":[a-z]*'
   ```

   - `true` → great, kill the background loop and advance to Gate 2.
   - `false` → reply briefly: "The server doesn't show the wizard complete yet — double-check the last step in the browser." Keep the background loop running; it will pick up the flip on its own once the wizard really completes.

### Gate 2 — Offer the user a chance to connect their own database (mandatory ask)

**You MUST ask the user this question and wait for their explicit reply before advancing to Gate 3.** Do not skip this gate "to be helpful". Do not infer the answer from prior context. Do not proceed on silence. A fresh Metabase only has the Sample Database; the user almost always wants their own data, and not asking is one of the most common UX regressions in this skill.

1. **Send the user this message verbatim** (do not paraphrase, do not summarise, do not assume the user already wants to skip):

   > Metabase is set up. By default it only knows about its Sample Database. Want to connect your own database now so you can ask Codex questions about your data? Reply **yes** to open the "Add database" page in Metabase, or **no** / **skip** to continue with just the Sample Database (you can always add one later from Admin → Databases).

2. **Stop generating and wait for a reply.** Do not advance to step 3 or to Gate 3 until you have an explicit user message addressing this question.

3. **Branch on the reply:**

   - User says **yes** (or equivalent like "sure", "add it", "let's do it") → continue to the "If the user says yes" sub-section below.
   - User says **no** / **skip** (or equivalent like "later", "not now", "just the sample") → continue to Gate 3.
   - User replies with something unrelated → re-send the verbatim message and wait again. Do not abandon the gate.

#### If the user says yes

Open `http://localhost:$PORT/admin/databases/create` in the user's default system browser, then send them verbatim:

> I opened the "Add database" page in your browser. Fill in the connection details for your database (host, port, credentials, etc.), test the connection, and save it. Tell me once you've saved it successfully.

Do **not** automate the form submission — connection credentials must come from the user via Metabase's UI, never via chat. Opening the URL is fine; entering the credentials for them is not.

This gate completes on the user's confirmation when they reply "done" / "added" / "saved".

#### If the user says no / skip

Continue immediately to Gate 3.

### Gate 3 — Confirm and stop

Only after Gates 1 and 2 are both resolved, confirm to the user that Metabase is ready at `http://localhost:$PORT` (substitute the actual port) and stop.

---

## Stopping Metabase

When the user asks to stop Metabase, determine which method was used.

### Stop JAR-based Metabase

```bash
if [ -f ./metabase/metabase.pid ]; then
  if [ "$(cat ./metabase/metabase.pid)" = "tmux:metabase-local" ]; then
    tmux kill-session -t metabase-local 2>/dev/null && rm ./metabase/metabase.pid && echo "Metabase stopped"
  else
    kill "$(cat ./metabase/metabase.pid)" 2>/dev/null && rm ./metabase/metabase.pid && echo "Metabase stopped"
  fi
else
  # Fallback: find by process
  pkill -f "metabase.jar" && echo "Metabase stopped"
fi
```

### Stop Docker-based Metabase

```bash
docker stop metabase-local && echo "Metabase stopped"
```

To also remove the container (but keep data):

```bash
docker rm metabase-local
```

---

## Checking Metabase Status

### Check JAR status

```bash
if [ -f ./metabase/metabase.pid ] && [ "$(cat ./metabase/metabase.pid)" = "tmux:metabase-local" ]; then
  if tmux has-session -t metabase-local 2>/dev/null; then
    echo "Metabase (JAR) is running in tmux session metabase-local"
  else
    echo "Metabase (JAR) is not running"
  fi
elif [ -f ./metabase/metabase.pid ] && ps -p "$(cat ./metabase/metabase.pid)" > /dev/null 2>&1; then
  echo "Metabase (JAR) is running with PID $(cat ./metabase/metabase.pid)"
else
  echo "Metabase (JAR) is not running"
fi
```

### Check Docker status

```bash
docker ps --filter "name=metabase-local" --format "{{.Names}}: {{.Status}}"
```

---

## Environment Variables Reference

These can be customized when starting Metabase:

| Variable        | Default         | Description                                  |
| --------------- | --------------- | -------------------------------------------- |
| `MB_DB_FILE`    | `./metabase.db` | H2 database file location                    |
| `MB_JETTY_PORT` | `3000`          | Port Metabase listens on                     |
| `MB_JETTY_HOST` | `localhost`     | Network interface (use `0.0.0.0` for Docker) |

For all options, see the [Metabase Environment Variables documentation](https://www.metabase.com/docs/latest/configuring-metabase/environment-variables).

---

## Troubleshooting

### "Address already in use"

Another process is using the port. Either stop that process or choose a different port.

### "Java version too old"

Install Java 21+ or use the Docker method instead.

### "Unable to locate a Java Runtime" on macOS

You are likely hitting `/usr/bin/java` (stub). Prepend Homebrew OpenJDK to `PATH` as in **Check for Java 21+**, or call the real binary explicitly, e.g. `/opt/homebrew/bin/java -version`.

### Metabase starts but is slow

First startup takes longer as it initializes the database. Subsequent starts are faster.

### "Cannot connect to Docker daemon"

Make sure Docker Desktop is running (macOS/Windows) or the Docker service is started (Linux).
