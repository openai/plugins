---
name: marketplace
description: Vercel Marketplace expert guidance — discovering, installing, and building integrations, auto-provisioned environment variables, unified billing, and the vercel integration CLI. Use when consuming third-party services, building custom integrations, or managing marketplace resources on Vercel.
metadata:
  priority: 3
  docs:
    - "https://vercel.com/docs/integrations"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - "integration.json"
  bashPatterns:
    - '\bvercel\s+integration\b'
    - '\bvercel\s+integration\s+add\b'
    - '\bvercel\s+integration\s+discover\b'
retrieval:
  aliases:
    - vercel integrations
    - marketplace
    - third party services
    - add ons
  intents:
    - install integration
    - build integration
    - manage marketplace
    - add third party service
  entities:
    - Vercel Marketplace
    - integration
    - vercel integration
    - unified billing
chainTo:
  -
    pattern: 'NEON_|POSTGRES_|DATABASE_URL|@neondatabase|@vercel/postgres'
    targetSkill: vercel-storage
    message: 'Database integration detected — loading Storage guidance for Neon Postgres setup, connection pooling, and serverless patterns.'
  -
    pattern: 'CLERK_|@clerk/|clerkMiddleware'
    targetSkill: auth
    message: 'Clerk integration detected — loading Auth guidance for middleware setup, route protection, and organization flows.'
  -
    pattern: 'SANITY_|CONTENTFUL_|STORYBLOK_|DATOCMS_|sanity|contentful|storyblok'
    targetSkill: cms
    message: 'CMS integration detected — loading CMS guidance for content modeling, preview mode, and revalidation webhooks.'

---

# Vercel Marketplace

You are an expert in the Vercel Marketplace — the integration platform that connects third-party services to Vercel projects with unified billing, auto-provisioned environment variables, and one-click setup.

## Consuming Integrations

### Linked Project Preflight

Integration provisioning is project-scoped. Verify the repository is linked before running `integration add`.

```bash
# Check whether this directory is linked to a Vercel project
test -f .vercel/project.json && echo "Linked" || echo "Not linked"

# Link if needed
vercel link
```

If the project is not linked, do not continue with provisioning commands until linking completes.

### Discovering Integrations

```bash
# Search the Marketplace catalog from CLI
vercel integration discover

# Filter by category
vercel integration discover --category databases
vercel integration discover --category monitoring

# List integrations already installed on this project
vercel integration list
```

For browsing the full catalog interactively, use the [Vercel Marketplace](https://vercel.com/marketplace) dashboard.

### Getting Setup Guidance

```bash
# Get agent-friendly setup guide for a specific integration
vercel integration guide <name>

# Include framework-specific steps when available
vercel integration guide <name> --framework <fw>

# Examples
vercel integration guide neon
vercel integration guide datadog --framework nextjs
```

Use `--framework <fw>` as the default discovery flow when framework-specific setup matters. The guide returns structured setup steps including required environment variables, SDK packages, and code snippets — ideal for agentic workflows.

### Installing an Integration

```bash
# Install from CLI
vercel integration add <integration-name>

# Examples
vercel integration add neon          # Postgres database
vercel integration add upstash       # Redis / Kafka
vercel integration add clerk         # Authentication
vercel integration add sentry        # Error monitoring
vercel integration add sanity        # CMS
vercel integration add datadog       # Observability (auto-configures drain)
```

`vercel integration add` is the primary scripted/AI path. It installs to the currently linked project, auto-connects the integration, and auto-runs environment sync locally unless disabled.

If the CLI hands off to the dashboard for provider-specific completion, treat that as fallback:

```bash
vercel integration open <integration-name>
```

Complete the web step, then return to CLI verification (`vercel env ls` and local env sync check).

### Auto-Provisioned Environment Variables

When you install a Marketplace integration from a linked project, Vercel automatically provisions the required environment variables for that project.

**IMPORTANT: Provisioning delay after install.** After installing a database integration (especially Neon), the resource may take **1–3 minutes** to fully provision. During this window, connection attempts return HTTP 500 errors. Do NOT debug the connection string or code — just wait and retry. If local env sync was disabled or skipped, run `vercel env pull .env.local --yes` after a brief wait to get the finalized credentials.

```bash
# View environment variables added by integrations
vercel env ls

# Example: after installing Neon, these are auto-provisioned:
# POSTGRES_URL          — connection string
# POSTGRES_URL_NON_POOLING — direct connection
# POSTGRES_USER         — database user
# POSTGRES_PASSWORD     — database password
# POSTGRES_DATABASE     — database name
# POSTGRES_HOST         — database host
```

No manual `.env` file management is needed — the variables are injected into all environments (Development, Preview, Production) automatically.

### Using Provisioned Resources

```ts
// app/api/users/route.ts — using Neon auto-provisioned env vars
import { neon } from "@neondatabase/serverless";

// POSTGRES_URL is auto-injected by the Neon integration
const sql = neon(process.env.POSTGRES_URL!);

export async function GET() {
  const users = await sql`SELECT * FROM users LIMIT 10`;
  return Response.json(users);
}
```

```ts
// app/api/cache/route.ts — using Upstash auto-provisioned env vars
import { Redis } from "@upstash/redis";

// KV_REST_API_URL and KV_REST_API_TOKEN are auto-injected
const redis = Redis.fromEnv();

export async function GET() {
  const cached = await redis.get("featured-products");
  return Response.json(cached);
}
```

### Managing Integrations

```bash
# List installed integrations
vercel integration ls

# Check usage and billing for an integration
vercel integration balance <name>

# Remove an integration
vercel integration remove <integration-name>
```

## Unified Billing

Marketplace integrations use Vercel's unified billing system:

- **Single invoice**: All integration charges appear on your Vercel bill
- **Usage-based**: Pay for what you use, scaled per integration's pricing model
- **Team-level billing**: Charges roll up to the Vercel team account
- **No separate accounts**: No need to manage billing with each provider individually

```bash
# Check current usage balance for an integration
vercel integration balance datadog
vercel integration balance neon
```

## Building Integrations

### Integration Architecture

Vercel integrations consist of:

1. **Integration manifest** — declares capabilities, required scopes, and UI surfaces
2. **Webhook handlers** — respond to Vercel lifecycle events
3. **UI components** — optional dashboard panels rendered within Vercel
4. **Resource provisioning** — create and manage resources for users

### Scaffold an Integration

```bash
# Create a new integration project
npx create-vercel-integration my-integration

# Or start from the template
npx create-next-app my-integration --example vercel-integration
```

### Integration Manifest

```json
// vercel-integration.json
{
  "name": "my-integration",
  "slug": "my-integration",
  "description": "Provides X for Vercel projects",
  "logo": "public/logo.svg",
  "website": "https://my-service.com",
  "categories": ["databases"],
  "scopes": {
    "project": ["env-vars:read-write"],
    "team": ["integrations:read-write"]
  },
  "installationType": "marketplace",
  "resourceTypes": [
    {
      "name": "database",
      "displayName": "Database",
      "description": "A managed database instance"
    }
  ]
}
```

### Handling Lifecycle Webhooks

```ts
// app/api/webhook/route.ts
import { verifyVercelSignature } from "@vercel/integration-utils";

export async function POST(req: Request) {
  const body = await req.json();

  // Verify the webhook is from Vercel
  const isValid = await verifyVercelSignature(req, body);
  if (!isValid) {
    return Response.json({ error: "Invalid signature" }, { status: 401 });
  }

  switch (body.type) {
    case "integration.installed":
      // Provision resources for the new installation
      await provisionDatabase(body.payload);
      break;

    case "integration.uninstalled":
      // Clean up resources
      await deprovisionDatabase(body.payload);
      break;

    case "integration.configuration-updated":
      // Handle config changes
      await updateConfiguration(body.payload);
      break;
  }

  return Response.json({ received: true });
}
```

### Provisioning Environment Variables

```ts
// lib/provision.ts
async function provisionEnvVars(
  installationId: string,
  projectId: string,
  credentials: { url: string; token: string },
) {
  const response = await fetch(
    `https://api.vercel.com/v1/integrations/installations/${installationId}/env`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.VERCEL_INTEGRATION_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        projectId,
        envVars: [
          {
            key: "MY_SERVICE_URL",
            value: credentials.url,
            target: ["production", "preview", "development"],
            type: "encrypted",
          },
          {
            key: "MY_SERVICE_TOKEN",
            value: credentials.token,
            target: ["production", "preview", "development"],
            type: "secret",
          },
        ],
      }),
    },
  );

  return response.json();
}
```

### Integration CLI Commands

The `vercel integration` CLI supports these subcommands:

```bash
# Discover integrations in the Marketplace catalog
vercel integration discover
vercel integration discover --category <category>

# Get agent-friendly setup guide
vercel integration guide <name>
vercel integration guide <name> --framework <framework>

# Add (install) an integration
vercel integration add <name>

# List installed integrations
vercel integration list    # alias: vercel integration ls

# Check usage / billing balance
vercel integration balance <name>

# Open integration dashboard in browser (fallback when add redirects)
vercel integration open <name>

# Remove an integration
vercel integration remove <name>
```

> **Building integrations?** Use `npx create-vercel-integration` to scaffold, then deploy your
> integration app to Vercel normally with `vercel --prod`. Publish to the Marketplace via the
> [Vercel Partner Dashboard](https://vercel.com/docs/integrations).

## Common Integration Categories

| Category              | Popular Integrations                          | Auto-Provisioned Env Vars               |
| --------------------- | --------------------------------------------- | --------------------------------------- |
| Databases             | Neon, Supabase, PlanetScale, MongoDB, Turso   | `POSTGRES_URL`, `DATABASE_URL`          |
| Cache/KV              | Upstash Redis                                 | `KV_REST_API_URL`, `KV_REST_API_TOKEN`  |
| Auth                  | Clerk, Auth0, Descope                         | `CLERK_SECRET_KEY`, `AUTH0_SECRET`      |
| CMS                   | Sanity, Contentful, Storyblok, DatoCMS        | `SANITY_PROJECT_ID`, `CONTENTFUL_TOKEN` |
| Monitoring            | Datadog, Sentry, Checkly, New Relic           | `SENTRY_DSN`, `DD_API_KEY`             |
| Payments              | Stripe                                        | `STRIPE_SECRET_KEY`                     |
| Feature Flags         | LaunchDarkly, Statsig, Hypertune              | `LAUNCHDARKLY_SDK_KEY`                  |
| AI Agents & Services  | CodeRabbit, Braintrust, Sourcery, Chatbase    | varies by integration                   |
| Video                 | Mux                                           | `MUX_TOKEN_ID`, `MUX_TOKEN_SECRET`     |
| Messaging             | Resend, Knock, Novu                           | `RESEND_API_KEY`                        |
| Searching             | Algolia, Meilisearch                          | `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY`    |
| Commerce              | Shopify, Swell, BigCommerce                   | `SHOPIFY_ACCESS_TOKEN`                  |

## Observability Integration Path

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

## Decision Matrix

| Need                                      | Use                                                | Why                                            |
| ----------------------------------------- | -------------------------------------------------- | ---------------------------------------------- |
| Add a database to your project            | `vercel integration add neon`                      | Auto-provisioned, unified billing              |
| Browse available services                 | `vercel integration discover`                      | CLI-native catalog search                      |
| Get setup steps for an integration        | `vercel integration guide <name> --framework <fw>` | Framework-specific, agent-friendly setup guide |
| CLI redirects to dashboard during install | `vercel integration open <name>`                   | Fallback to complete provider web flow         |
| Check integration usage/cost              | `vercel integration balance <name>`                | Billing visibility per integration             |
| Build a SaaS integration                  | Integration SDK + manifest                         | Full lifecycle management                      |
| Centralize billing                        | Marketplace integrations                           | Single Vercel invoice                          |
| Auto-inject credentials                   | Marketplace auto-provisioning                      | No manual env var management                   |
| Add observability vendor                  | `vercel integration add <vendor>`                  | Auto-creates log/trace drains                  |
| Export Speed Insights / Web Analytics     | Manual drain via REST API                          | Not auto-configured by vendor install          |
| Manage integrations programmatically      | Vercel REST API                                    | `/v1/integrations` endpoints                   |
| Test integration locally                  | `vercel dev`                                       | Local development server with Vercel features  |

## Cross-References

- **Drain configuration, payload formats, signature verification** → `⤳ skill: observability`
- **Drains REST API endpoints** → `⤳ skill: vercel-api`
- **CLI log streaming (`--follow`, `--since`, `--level`)** → `⤳ skill: vercel-cli`
- **Safe project setup sequencing (link, env pull, then run db/dev)** → `⤳ skill:bootstrap`
- **Headless CMS integrations (Sanity, Contentful)** → `⤳ skill:cms`

## Official Documentation

- [Vercel Marketplace](https://vercel.com/marketplace)
- [Building Integrations](https://vercel.com/docs/integrations)
- [Integration CLI](https://vercel.com/docs/cli/integration)
- [Integration Webhooks](https://vercel.com/docs/integrations#webhooks)
- [Environment Variables](https://vercel.com/docs/environment-variables)
- [Drains Overview](https://vercel.com/docs/drains)
- [Drains Security](https://vercel.com/docs/drains/security)
