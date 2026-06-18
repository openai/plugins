---
name: render-cli
description: >-
  Installs and uses the Render CLI for deploys, logs, SSH, psql, Blueprint
  validation, and automation. Use when the user needs to run Render CLI
  commands, script deploys in CI/CD, authenticate with an API key, query
  services non-interactively, or troubleshoot CLI auth issues.
  Trigger terms: render CLI, render login, render deploys, render logs,
  render ssh, render psql, render blueprints validate, render skills,
  RENDER_API_KEY, non-interactive, CI/CD deploy.
license: MIT
compatibility: Render CLI v2.7.0+ (Homebrew, Linux/macOS, direct download)
metadata:
  author: Render
  version: "1.0.0"
  category: operations
---

# Render CLI

The Render CLI manages services, databases, and deployments from the terminal. Supports interactive use, non-interactive scripting, and CI/CD automation.

## When to Use

- **Deploying** a service from the terminal or CI/CD
- **Tailing logs** in real time
- **Opening psql** to a Render Postgres database
- **SSHing** into a running service or launching an ephemeral shell
- **Validating** a `render.yaml` Blueprint
- **Scripting** Render operations in CI/CD pipelines
- **Installing** agent skills for AI coding tools

## Installation

| Method | Command |
|--------|---------|
| **Homebrew** | `brew update && brew install render` |
| **Linux/macOS** | `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/refs/heads/main/bin/install.sh \| sh` |
| **Direct download** | [GitHub releases](https://github.com/render-oss/cli/releases/) |
| **Build from source** | `git clone git@github.com:render-oss/cli.git && cd cli && go build -o render` |

After install, run `render` with no arguments to confirm.

## Authentication

### Interactive (local dev)

```bash
render login
```

Opens the browser to generate a CLI token. Token is saved to `~/.render/cli.yaml`. Tokens expire periodically—re-run `render login` when prompted.

### Non-interactive (CI/CD)

```bash
export RENDER_API_KEY=rnd_...
```

API keys do not expire. Generate one from **Account Settings > API Keys** in the Dashboard. The API key takes precedence over CLI tokens when set.

Set the active workspace:

```bash
render workspace set
```

## Command Reference

### Core commands

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `render login` | Authenticate via browser | — |
| `render workspace set` | Set active workspace | — |
| `render services` | List all services and datastores | `-o json` for scripting |
| `render deploys create [SVC]` | Trigger a deploy | `--wait`, `--commit SHA`, `--image URL` |
| `render deploys list [SVC]` | List deploys for a service | `-o json` |
| `render logs -r [SVC]` | View logs | `--tail` for streaming |
| `render psql [DB]` | Open psql session | `-c "SQL"`, `-o json`, `-- --csv` |
| `render ssh [SVC]` | SSH into running instance | `--ephemeral` / `-e` for isolated shell |
| `render blueprints validate` | Validate `render.yaml` | Defaults to `./render.yaml` |
| `render skills [install\|update\|list]` | Manage agent skills | — |
| `render workspaces` | List workspaces | `-o json` |

### Non-interactive mode

For CI/CD and scripts, always set:

| Flag | Purpose |
|------|---------|
| `-o json` (or `yaml`, `text`) | Machine-readable output |
| `--confirm` | Skip confirmation prompts |

Output format precedence: `--output` flag > `RENDER_OUTPUT` env var > auto-detect (TTY → interactive, pipe → text).

```bash
export RENDER_OUTPUT=json
render services --confirm
```

### Deploy patterns

```bash
# Deploy and wait for completion (exits non-zero on failure)
render deploys create srv-xxx --wait --confirm -o json

# Deploy a specific commit
render deploys create srv-xxx --commit abc123 --wait --confirm

# Deploy a specific Docker image
render deploys create srv-xxx --image ghcr.io/org/app:v1.2.3 --wait --confirm
```

### Database queries

```bash
# Single query, JSON output
render psql db-xxx -c "SELECT NOW();" -o json

# CSV output via psql passthrough
render psql db-xxx -c "SELECT id, email FROM users;" -o text -- --csv
```

## CI/CD Example (GitHub Actions)

```yaml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Install Render CLI
        run: |
          curl -L https://github.com/render-oss/cli/releases/download/v1.1.0/cli_1.1.0_linux_amd64.zip -o render.zip
          unzip render.zip
          sudo mv cli_v1.1.0 /usr/local/bin/render
      - name: Deploy
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: render deploys create ${{ secrets.RENDER_SERVICE_ID }} --wait --confirm -o json
```

Pin to a specific CLI version in CI to avoid breaking changes.

## Local Config

Config file: `~/.render/cli.yaml`

Override with `RENDER_CLI_CONFIG_PATH` env var.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Token expired | Re-run `render login` |
| Wrong workspace | Run `render workspace set` to switch |
| Missing `--confirm` in CI | Add `--confirm` to skip interactive prompts |
| Using `--output interactive` in CI | Use `-o json` or `-o text` in non-TTY environments |
| Deploying without `--wait` in CI | Add `--wait` so the job fails on deploy failure |

## References

| Document | Contents |
|----------|----------|
| `references/command-cheatsheet.md` | Full command list with flags, output examples, and scripting patterns |

## Related Skills

- **render-deploy** — End-to-end deploy flows, MCP operations, Dashboard deeplinks
- **render-blueprints** — `render.yaml` authoring and validation
- **render-postgres** — Database connections, `render psql` usage
- **render-debug** — Using `render logs` and `render ssh` for troubleshooting
