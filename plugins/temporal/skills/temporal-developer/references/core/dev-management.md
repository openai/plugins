# Development Server and Worker Management

## Server Management

Workers and workflows need a running Temporal Server. You can develop against a local dev server, a self-hosted cluster, or Temporal Cloud — the choice depends on your setup. If you need a local server, start one with the Temporal CLI:

```bash
temporal server start-dev # Start this in the background.
```

The dev server can be shared across projects and left running as you develop.

The dev server is in-memory by default -- all workflows, schedules, and history are lost on restart. Use `--db-filename temporal.db` to persist across restarts.

The dev server is for local development only, not production.

### `temporal server start-dev` flags

| Flag | Default | Purpose |
|---|---|---|
| `--db-filename`, `-f` | in-memory | Persistent SQLite file. Without it, state is in-memory and lost on exit. |
| `--namespace`, `-n` | `default` only | Namespaces to create at launch. Repeatable. The `default` namespace is always created. |
| `--search-attribute` | — | Register search attributes as `KEY=TYPE` pairs. TYPE is one of: `Text`, `Keyword`, `Int`, `Double`, `Bool`, `Datetime`, `KeywordList`. Repeatable. |
| `--port`, `-p` | `7233` | Front-end gRPC port. |
| `--ui-port` | `--port` + 1000 | Web UI port. |
| `--ip` | `127.0.0.1` | IP address bound to the front-end service. Use `0.0.0.0` for Docker/LAN access. |
| `--dynamic-config-value` | — | Dynamic config in `KEY=JSON_VALUE` form. Repeatable. |
| `--log-level` | `warn` | (Global flag) Log level. Accepted values: `debug`, `info`, `warn`, `error`, `never`. Default is `warn` for `start-dev`. |
| `--log-format` | `text` | (Global flag) Log format. Accepted values: `text`, `json`. |
| `--headless` | — | Disable the Web UI. |
| `--http-port` | random free port | HTTP API port. |
| `--metrics-port` | random free port | Prometheus `/metrics` port. |

Example with persistence, extra namespaces, and a search attribute:

```bash
temporal server start-dev \
    --db-filename /tmp/temporal.db \
    --namespace dev \
    --search-attribute OrderId=Keyword
```

## Worker Management Details

### Starting Workers

How you start a worker is project-dependent, but generally Temporal code should have a program entrypoint which starts a worker. If your project doesn't, you should define it.

When you need a new worker, you should start it in the background (and preferrably have it log somewhere you can check), and then remember its PID so you can kill / clean it up later.

**Best practice**: As far as local development goes, run only ONE worker instance with the latest code. Don't keep stale workers (running old code) around.

### Cleanup

**Always kill workers when done.** Don't leave workers running.

## Dev to Prod

Steps to promote a workflow from a local dev server to a production backend. For the most part, the workflow and worker code do not change between environments; only the connection descriptor does. If the connection code is in the application code, then just those spots in the code need to be updated.

### 1. Start a local dev server with persistence

```bash
temporal server start-dev --db-filename dev.db
```

### 2. Run the workflow against dev

Start your worker, then execute the workflow:

```bash
temporal workflow execute \
    --type MyWorkflow \
    --task-queue my-queue \
    --input '{"key": "value"}'
```

`workflow execute` blocks until the run terminates; a non-zero exit means the run failed, was cancelled, terminated, or timed out.

### 3. Create a prod profile configuration

```bash
temporal config --profile prod set --prop address --value "your-ns.your-acct.tmprl.cloud:7233"
temporal config --profile prod set --prop namespace --value "your-ns.your-acct"
temporal config --profile prod set --prop api-key --value "your-key"
```

The profile-selecting flag is `--profile <name>`.

### 4. Smoke-test prod

```bash
temporal workflow list --profile prod --limit 1 --output json
```

If this returns (even an empty list), the connection descriptor is correct.

### 5. Run in prod

```bash
temporal workflow start \
    --profile prod \
    --type MyWorkflow \
    --task-queue my-queue \
    --input '{"key": "value"}'
```

`workflow start` is asynchronous (returns a Workflow/Run ID); use `workflow execute` instead if you want the CLI to block.