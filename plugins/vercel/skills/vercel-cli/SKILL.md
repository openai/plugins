---
name: vercel-cli
description: Vercel CLI expert guidance. Use when deploying, managing environment variables, linking projects, viewing logs, managing domains, or interacting with the Vercel platform from the command line.
metadata:
  priority: 4
  docs:
    - "https://vercel.com/docs/cli"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'vercel.json'
    - 'vercel.ts'
    - '.vercel/**'
    - '.vercelignore'
    - 'now.json'
  bashPatterns:
    - '^\s*vercel(?:\s|$)'
    - '^\s*vc(?:\s|$)'
    - '\bnpx\s+vercel\b'
    - '\bpnpm\s+dlx\s+vercel\b'
    - '\bbunx\s+vercel\b'
    - '\byarn\s+dlx\s+vercel\b'
    - '\bnpx\s+@vercel/config\b'
  promptSignals:
    phrases:
      - "check deployment"
      - "check deploy"
      - "deployment status"
      - "deploy status"
      - "vercel logs"
      - "deployment logs"
      - "deploy logs"
      - "vercel inspect"
      - "is it deployed"
      - "deploy failing"
      - "deploy failed"
      - "deployment error"
      - "check vercel"
      - "vercel status"
    allOf:
      - [check, deployment]
      - [check, deploy]
      - [vercel, status]
      - [vercel, logs]
      - [deploy, error]
      - [deploy, failed]
      - [deploy, stuck]
    anyOf:
      - "deployment"
      - "deploy"
      - "vercel"
      - "production"
    noneOf:
      - "terraform"
      - "aws deploy"
      - "heroku"
    minScore: 6
retrieval:
  aliases:
    - vercel command line
    - vc cli
    - deploy command
    - vercel terminal
  intents:
    - deploy from cli
    - link project
    - manage domains
    - view logs from terminal
  entities:
    - vercel CLI
    - vercel deploy
    - vercel env
    - vercel link
    - vercel logs
chainTo:
  -
    pattern: '"crons"\s*:'
    targetSkill: cron-jobs
    message: 'Cron configuration detected in vercel.json — loading Cron Jobs guidance for schedule syntax, CRON_SECRET verification, and function handler patterns.'
  -
    pattern: '"functions"\s*:\s*\{|"maxDuration"\s*:|"memory"\s*:'
    targetSkill: vercel-functions
    message: 'Functions configuration detected in vercel.json — loading Vercel Functions guidance for runtime options, streaming, and Fluid Compute.'
    skipIfFileContains: '"crons"\s*:'
  -
    pattern: '"redirects"\s*:\s*\[|"rewrites"\s*:\s*\[|"headers"\s*:\s*\['
    targetSkill: routing-middleware
    message: 'Routing rules in vercel.json — loading Routing Middleware guidance for platform-level request interception patterns.'

---

# Vercel CLI

You are an expert in the Vercel CLI v50.28.0 (`vercel` or `vc`). The CLI is the primary way to manage Vercel projects from the terminal.

## Installation

```bash
npm i -g vercel
```

## Login

The CLI uses an **OAuth 2.0 Device Flow** for authentication.

```bash
vercel login
```

> **Deprecation notice**: Email-based login (`vercel login your@email.com`) and the flags `--github`, `--gitlab`, `--bitbucket`, `--oob` were removed February 26, 2026. The `team` method (SAML-based login) remains supported until June 1, 2026, then will also be removed.

## Core Commands

### Deployment

```bash
# Preview deployment (from project root)
vercel

# Production deployment
vercel --prod

# Build locally, deploy build output only
vercel build
vercel deploy --prebuilt

# Build for production (uses production env vars)
vercel build --prod
vercel deploy --prebuilt --prod

# Force a new deployment (skip cache)
vercel --force

# Promote a preview deployment to production
vercel promote <deployment-url>

# Rollback to previous production deployment
vercel rollback
```

### Development

```bash
# Start local dev server with Vercel features
vercel dev

# Link current directory to a Vercel project
vercel link

# Deterministic non-interactive link (recommended for bootstrap/automation)
vercel link --yes --project <name-or-id> --scope <team>

# Pull environment variables and project settings
vercel pull

# Pull specific environment
vercel pull --environment=production

# Open linked project in the Vercel Dashboard
vercel open
```

### Deterministic Project Linking (Recommended)

Prefer explicit non-interactive linking for bootstrap and automation:

```bash
vercel link --yes --project <name-or-id> --scope <team>
```

This is more reliable than interactive prompt-driven linking, which can pick the wrong project or team in multi-account setups. If there is any ambiguity, run `vercel open` to confirm the dashboard project, then relink with explicit `--project` and `--scope`.

### Environment Variables

```bash
# List all environment variables
vercel env ls

# Add an environment variable
vercel env add MY_VAR

# Add for specific environments
vercel env add MY_VAR production
vercel env add MY_VAR preview development

# Add branch-scoped variable
vercel env add MY_VAR preview --branch=feature-x

# Add sensitive (write-only) variable
vercel env add MY_SECRET --sensitive

# Remove an environment variable
vercel env rm MY_VAR

# Pull all env vars to .env.local
vercel env pull
vercel env pull .env.production.local --environment=production
```

### Logs & Inspection

The `vercel logs` command (rebuilt February 2026) supports **historical log querying** and uses **git context by default** — it automatically scopes logs to your current repository when run from a project directory.

```bash
# View runtime/function logs (real-time)
vercel logs <deployment-url>

# Follow logs in real-time (streaming mode)
vercel logs <deployment-url> --follow

# Query historical logs (no longer limited to live-only)
vercel logs --since 24h
vercel logs --since 7d

# Filter by time range
vercel logs <deployment-url> --since 1h
vercel logs <deployment-url> --since 30m

# Filter by log level
vercel logs <deployment-url> --level error
vercel logs <deployment-url> --level warning

# Filter by deployment ID, request ID, or arbitrary string
vercel logs --deployment-id dpl_xxxxx
vercel logs --request-id req_xxxxx
vercel logs --query "TypeError"

# Output as JSON (for piping to jq or other tools)
vercel logs <deployment-url> --json

# Combine filters: stream errors from the last hour as JSON
vercel logs <deployment-url> --follow --since 1h --level error --json

# Inspect a deployment (build details, metadata, function list)
vercel inspect <deployment-url>

# List recent deployments
vercel ls
```

> **Note:** `vercel logs` shows runtime request logs only. For build output, use
> `vercel inspect <deployment-url>` or view build logs at `https://vercel.com/{team}/{project}/deployments` → select deployment → **Build Logs**.
>
> **Drains and advanced observability:** Log drains, trace export, and analytics data forwarding are
> configured via the Vercel Dashboard at `https://vercel.com/dashboard/{team}/~/settings/log-drains` or REST API (`/v1/drains`), not the CLI. See `⤳ skill: observability`
> for drain setup, payload schemas, and signature verification.

### Domains

```bash
# List domains
vercel domains ls

# Add a domain to a project
vercel domains add example.com

# Remove a domain
vercel domains rm example.com
```

### DNS

```bash
# List DNS records
vercel dns ls example.com

# Add a DNS record
vercel dns add example.com @ A 1.2.3.4
```

### Teams

```bash
# List teams
vercel teams ls

# Switch to a team
vercel teams switch my-team
```

### Cache Management

```bash
# Purge all cache (CDN + Data cache) for current project
vercel cache purge

# Purge only CDN cache
vercel cache purge --type cdn

# Purge only Data cache
vercel cache purge --type data

# Purge without confirmation prompt
vercel cache purge --yes

# Invalidate by tag (stale-while-revalidate)
vercel cache invalidate --tag blog-posts

# Invalidate multiple tags
vercel cache invalidate --tag blog-posts,user-profiles,homepage

# Hard delete by tag (blocks until revalidated — use with caution)
vercel cache dangerously-delete --tag blog-posts

# Hard delete with revalidation deadline (deletes only if not accessed within N seconds)
vercel cache dangerously-delete --tag blog-posts --revalidation-deadline-seconds 3600

# Invalidate cached image transformations by source path
vercel cache invalidate --srcimg /api/avatar/1

# Hard delete cached image transformations
vercel cache dangerously-delete --srcimg /api/avatar/1
```

**Key distinction:** `invalidate` serves STALE and revalidates in the background. `dangerously-delete` serves MISS and blocks while revalidating. Prefer `invalidate` unless you need immediate freshness.

**Note:** `--tag` and `--srcimg` cannot be used together.

### MCP Server Integration

```bash
# Initialize global MCP client configuration for your Vercel account
vercel mcp

# Set up project-specific MCP access for the linked project
vercel mcp --project
```

The `vercel mcp` command links your local MCP client configuration to a Vercel Project. It generates connection details so AI agents and tools can call your MCP endpoints deployed on Vercel securely.

### Programmatic Configuration (`@vercel/config`)

```bash
# Compile vercel.ts to JSON (stdout)
npx @vercel/config compile

# Validate configuration and show summary
npx @vercel/config validate

# Generate vercel.json locally for development
npx @vercel/config generate
```

Use `vercel.ts` (or `.js`, `.mjs`, `.cjs`, `.mts`) instead of `vercel.json` for type-safe, dynamic project configuration. Only one config file per project — `vercel.json` or `vercel.ts`, not both.

> **Note:** Legacy `now.json` support will be removed on March 31, 2026. Rename to `vercel.json` (no content changes needed).

### Marketplace Integrations

Auto-provisioning is the default for `vercel integration add` — the CLI automatically creates resources and sets environment variables without extra prompts.

```bash
# List installed integrations
vercel integration list

# Add an integration (auto-provisions env vars by default)
vercel integration add neon

# Open an integration's dashboard
vercel integration open neon

# Remove an integration
vercel integration remove neon
```

#### Agent-Optimized: `discover` and `guide`

AI agents can autonomously discover, install, and retrieve setup instructions for Marketplace integrations (added March 2026):

```bash
# Search the integration catalog (returns JSON for automation)
vercel integration discover --format=json

# Search with a keyword filter
vercel integration discover database --format=json

# Get agent-friendly setup guide with code snippets
vercel integration guide neon

# Full workflow: discover → add → guide
vercel integration discover storage --format=json
vercel integration add neon
vercel integration guide neon
```

- `discover` — Searches the Vercel Marketplace catalog. Use `--format=json` for non-interactive output suitable for scripting and agent pipelines.
- `guide <name>` — Returns getting-started documentation in agent-friendly markdown: environment variables, SDK setup, and code snippets.
- Human-in-the-loop safety: the CLI prompts for developer confirmation when accepting Terms of Service.

> Full subcommands: `discover`, `guide`, `add`, `list` (alias `ls`), `balance`, `open`, `remove`.

### Project-Level Routing (No Redeploy)

Create and update routing rules — headers, rewrites, redirects — without building a new deployment. Rules take effect instantly.

Available via dashboard (CDN tab), API, CLI, and Vercel SDK. Project-level routes run after bulk redirects and before deployment config routes.

### Feature Flags

```bash
# Create a feature flag
vercel flags add redesigned-checkout --kind boolean --description "New checkout flow"

# List SDK keys
vercel flags sdk-keys ls

# Enable/disable, archive, and manage flags from CLI
vercel flags --help
```

See `⤳ skill: vercel-flags` for full flag configuration and adapter patterns.

### Direct API Access

The `vercel api` command (added January 2026) gives direct access to the full Vercel REST API from the terminal. Designed for AI agents — call Vercel APIs with no additional configuration.

```bash
# Call any Vercel REST API endpoint
vercel api GET /v9/projects
vercel api GET /v13/deployments
vercel api POST /v9/projects/:id/env --body '{"key":"MY_VAR","value":"val","target":["production"]}'

# Pipe JSON output to jq
vercel api GET /v9/projects | jq '.[].name'
```

### Metrics

```bash
# Query project metrics (rich text output with sparklines)
vercel metrics

# Raw values for scripting
vercel metrics --raw-values
```

## CI/CD Integration

Required environment variables for CI:
```bash
VERCEL_TOKEN=<your-token>
VERCEL_ORG_ID=<org-id>
VERCEL_PROJECT_ID=<project-id>
```

### GitHub Actions Example

```yaml
- name: Deploy to Vercel
  run: |
    vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
    vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
    vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Global Options

| Flag | Purpose |
|------|---------|
| `--token` | Authentication token (for CI) |
| `--cwd <dir>` | Working directory |
| `--debug` / `-d` | Verbose output |
| `--yes` / `-y` | Skip confirmation prompts |
| `--scope <team>` | Execute as a team |

## Common Workflows

### First-Time Setup
```bash
vercel link          # Connect to Vercel project
vercel env pull      # Get environment variables
vercel dev           # Start local dev
```

### Deploy from CI
```bash
vercel pull --yes --environment=production --token=$TOKEN
vercel build --prod --token=$TOKEN
vercel deploy --prebuilt --prod --token=$TOKEN
```

### Quick Preview
```bash
vercel               # Creates preview deployment, returns URL
```

## Official Documentation

- [Vercel CLI](https://vercel.com/docs/cli)
- [Cache Management](https://vercel.com/docs/cli/cache)
- [MCP Integration](https://vercel.com/docs/cli/mcp)
- [Deployments](https://vercel.com/docs/deployments)
- [REST API](https://vercel.com/docs/rest-api/reference)
- [GitHub: Vercel CLI](https://github.com/vercel/vercel)
