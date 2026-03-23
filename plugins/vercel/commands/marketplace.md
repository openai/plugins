---
description: Discover and install Vercel Marketplace integrations. Use to find databases, CMS, auth providers, and other services available on the Vercel Marketplace.
---

# Vercel Marketplace

Discover, install, and apply Vercel Marketplace integrations with guided setup and local verification.

## Preflight

1. **Project linked?** — Check for `.vercel/project.json` in the current directory or nearest parent.
   - If not found: run `vercel link` interactively, then re-run `/marketplace`.
   - Do not attempt provisioning until the project is linked.
2. **CLI available?** — Confirm `vercel` is on PATH.
   - If missing: `npm i -g vercel` (or `pnpm add -g vercel` / `bun add -g vercel`).
3. **Repo state** — Note uncommitted changes so the user can diff integration-related code changes later.
4. **Scope** — Detect monorepo (`turbo.json` or `pnpm-workspace.yaml`). If detected, confirm which package is targeted.

## Plan

The marketplace command follows an **apply-guide loop**:

1. **Discover** — Search the Marketplace catalog via `vercel integration discover`.
2. **Select** — User picks an integration (or specifies one in "$ARGUMENTS").
3. **Guide** — Fetch the agent-friendly setup guide via `vercel integration guide <name> --framework <fw>`.
4. **Install** — Run `vercel integration add <name>` for the automated happy path.
5. **Confirm env vars provisioned** — Explicitly verify required environment variables are set after provisioning.
6. **Apply code changes** — Install SDK packages and scaffold configuration code.
7. **Verify drain** — For observability integrations, confirm drain was auto-created and data is flowing.
8. **Run local health check** — Verify the integration works locally before deploying.

If "$ARGUMENTS" specifies an integration name, skip directly to the **Guide** step.

For observability integrations (Datadog, Sentry, Axiom, etc.), the flow extends with drain verification — see Step 7.

No destructive operations unless the user explicitly confirms. Package installs and code scaffolding are additive.

## Commands

### 1. Discover — Search the Marketplace Catalog

```bash
# Search all available integrations
vercel integration discover

# Filter by category
vercel integration discover --category databases
vercel integration discover --category monitoring
vercel integration discover --category auth

# List integrations already installed on this project
vercel integration list
```

Present integrations organized by category:

| Category   | Examples                          |
| ---------- | --------------------------------- |
| Database   | Neon, PlanetScale, Supabase       |
| Cache      | Upstash Redis, Upstash KV         |
| Auth       | Clerk, Auth0                      |
| CMS        | Sanity, Contentful, Prismic       |
| Payments   | Stripe, LemonSqueezy              |
| Monitoring | Datadog, Sentry, Axiom, Honeycomb |

Common replacements for sunset packages:

- **Neon** — Serverless Postgres (replaces `@vercel/postgres`)
- **Upstash** — Serverless Redis (replaces `@vercel/kv`)

### 2. Select — User Picks an Integration

If the user hasn't specified one in "$ARGUMENTS", ask which integration to set up. Accept the integration name or slug.

### 3. Guide — Fetch Setup Steps

```bash
# Get agent-friendly setup guide
vercel integration guide <name> --framework <fw>
```

Use framework-specific guides by default when framework is known. If unknown, infer from the repo and confirm with the user.

The guide returns structured setup steps: required env vars, SDK packages, code snippets, and framework-specific notes. Present these to the user.

### 4. Install — Add the Integration

```bash
vercel integration add <name>
```

`vercel integration add` is the primary scripted/AI flow. It installs against the linked project, auto-connects the integration, and auto-runs local env sync unless disabled.

If the CLI bounces to the dashboard for provider-specific completion, treat it as fallback and open the integration page directly:

```bash
vercel integration open <name>
```

Complete the web step, then continue with env verification.

After installation, the integration auto-provisions environment variables. For observability vendors (Datadog, Sentry, Axiom), this also auto-creates **log and trace drains**.

### 5. Confirm Env Vars Provisioned

Before applying code changes, verify the integration's required environment variables exist:

```bash
vercel env ls
```

Check that each variable name listed in the guide appears in the output. **Never echo variable values — check names only.**

- If local env sync was disabled or `.env.local` is stale, run:

```bash
vercel env pull .env.local --yes
```

- **All present** → Proceed to code changes.
- **Missing vars** → Tell the user which variables are missing. The integration install via `vercel integration add <name>` typically provisions these automatically. Guide the user to provision them before continuing.

### 6. Apply Code Changes

Install the SDK package:

```bash
npm install <sdk-package>   # or pnpm add / bun add
```

Then apply the code scaffolding from the guide:

- Create or update configuration files (e.g., `db.ts`, `redis.ts`, `auth.ts`)
- Add initialization code following the guide's patterns
- Respect the project's existing conventions (TypeScript vs JavaScript, import style, directory structure)

Ask the user for confirmation before writing files.

### 7. Verify Drain (Observability Integrations)

<!-- Sourced from marketplace skill: Observability Integration Path -->
Marketplace observability integrations (Datadog, Sentry, Axiom, Honeycomb, etc.) connect to Vercel's **Drains** system to receive telemetry. Understanding the data-type split is critical for correct setup.

### Data-Type Split

| Data Type          | Delivery Mechanism                                    | Integration Setup                                                                                                      |
| ------------------ | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Logs**           | Native drain (auto-configured by Marketplace install) | `vercel integration add <vendor>` auto-creates drain                                                                   |
| **Traces**         | Native drain (OpenTelemetry-compatible)               | Same — auto-configured on install                                                                                      |
| **Speed Insights** | Custom drain endpoint only                            | Requires manual drain creation via REST API or Dashboard (`https://vercel.com/dashboard/{team}/~/settings/log-drains`) |
| **Web Analytics**  | Custom drain endpoint only                            | Requires manual drain creation via REST API or Dashboard (`https://vercel.com/dashboard/{team}/~/settings/log-drains`) |

> **Key distinction:** When you install an observability vendor via the Marketplace, it auto-configures drains for **logs and traces** only. Speed Insights and Web Analytics data require a separate, manually configured drain pointing to a custom endpoint. See `⤳ skill: observability` for drain setup details.

### Agentic Flow: Observability Vendor Setup

Follow this sequence when setting up an observability integration:

#### 1. Pick Vendor

```bash
# Discover observability integrations
vercel integration discover --category monitoring

# Get setup guide for chosen vendor
vercel integration guide datadog
```

#### 2. Install Integration

```bash
# Install — auto-provisions env vars and creates log/trace drains
vercel integration add datadog
```

#### 3. Verify Drain Created

```bash
# Confirm drain was auto-configured
curl -s -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v1/drains?teamId=$TEAM_ID" | jq '.[] | {id, url, type, sources}'
```

Check the response for a drain pointing to the vendor's ingestion endpoint. If no drain appears, the integration may need manual drain setup — see `⤳ skill: observability` for REST API drain creation.

#### 4. Validate Endpoint

```bash
# Send a test payload to the drain
curl -X POST -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v1/drains/<drain-id>/test?teamId=$TEAM_ID"
```

Confirm the vendor dashboard shows the test event arriving.

#### 5. Smoke Log Check

```bash
# Trigger a deployment and check logs flow through
vercel logs <deployment-url> --follow --since 5m

# Check integration balance to confirm data is flowing
vercel integration balance datadog
```

Verify that logs appear both in Vercel's runtime logs and in the vendor's dashboard.

> **For drain payload formats and signature verification**, see `⤳ skill: observability` — the Drains section covers JSON/NDJSON schemas and `x-vercel-signature` HMAC-SHA1 verification.

### Speed Insights + Web Analytics Drains

For observability vendors that also want Speed Insights or Web Analytics data, configure a separate drain manually:

```bash
# Create a drain for Speed Insights + Web Analytics
curl -X POST -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.vercel.com/v1/drains?teamId=$TEAM_ID" \
  -d '{
    "url": "https://your-vendor-endpoint.example.com/vercel-analytics",
    "type": "json",
    "sources": ["lambda"],
    "environments": ["production"]
  }'
```

> **Payload schema reference:** See `⤳ skill: observability` for Web Analytics drain payload formats (JSON array of `{type, url, referrer, timestamp, geo, device}` events).

- **Drain present** → Proceed to health check.
- **No drain found** → Integration may not auto-configure drains. Create one manually via REST API (see `⤳ skill: observability`).
- **Drain errored** → Check the drain status in the Vercel Dashboard. Common fixes: endpoint URL typo, auth header missing, endpoint not accepting POST.

### 8. Run Local Health Check

Verify the integration works locally:

```bash
vercel dev
```

Or run the project's dev server and test the integration endpoint/connection:

- **Database** → Confirm connection by running a simple query (e.g., `SELECT 1`)
- **Auth** → Confirm the auth provider redirects correctly
- **Cache** → Confirm a set/get round-trip succeeds
- **CMS** → Confirm content fetch returns data
- **Observability** → Run `vercel logs <deployment-url> --follow --since 5m` and confirm logs appear in the vendor dashboard

If the health check fails, review the error output and guide the user through fixes (common: missing env vars in `.env.local`, wrong SDK version, network issues).

## Verification

After completing the apply-guide loop, confirm:

- [ ] Integration guide was retrieved via `vercel integration guide <name> --framework <fw>`
- [ ] Project was linked before provisioning started
- [ ] All required environment variables are provisioned on Vercel
- [ ] Local env sync is up to date (auto-sync succeeded or `vercel env pull .env.local --yes` ran)
- [ ] SDK package installed without errors
- [ ] Code changes applied and match the guide's patterns
- [ ] For observability integrations: drain verified and test payload received
- [ ] Local health check passed (dev server starts, integration responds)

If any step fails, report the specific error and suggest remediation before continuing.

## Summary

Present a structured result block:

```
## Marketplace Result
- **Integration**: <name>
- **Status**: installed | partially configured | failed
- **Package**: <sdk-package>@<version>
- **Env Vars**: <count> provisioned / <count> required
- **Drain**: configured | not applicable | manual setup needed
- **Health Check**: passed | failed | skipped
- **Files Changed**: <list of created/modified files>
```

## Next Steps

Based on the outcome:

- **Installed successfully** → "Run `/deploy` to deploy with the new integration. Your environment variables are already configured on Vercel."
- **Env vars missing** → "Provision the missing variables via the Vercel dashboard or `vercel integration add <name>`, then re-run `/marketplace <name>` to continue setup."
- **CLI handed off to dashboard** → "Run `vercel integration open <name>` to complete the provider web step, then resume from env verification."
- **Drain not auto-created** → "Create a drain manually via the REST API. See `⤳ skill: observability` for the `/v1/drains` endpoint and payload format."
- **Need Speed Insights / Web Analytics export** → "These data types require manual drain setup — they are not auto-configured by vendor installs. See `⤳ skill: observability`."
- **Health check failed** → "Review the error above. Common fixes: copy env vars to `.env.local` with `vercel env pull`, check SDK version compatibility, verify network access."
- **Want another integration?** → "Run `/marketplace` again to browse available integrations."
- **Review changes** → "Run `git diff` to review all integration-related code changes before committing."
