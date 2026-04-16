# Blueprint Example: Heroku Migration with Project/Environment Pattern

This example shows a complete `render.yaml` for migrating a typical Heroku app with a web dyno, worker dyno, Heroku Scheduler (clock), Postgres, and Redis. It uses the `projects`/`environments` pattern to group all resources in a single Render project.

References: [Blueprint docs](https://render.com/docs/blueprint-spec#projects-and-environments) | [Blueprint YAML JSON schema](https://render.com/schema/render.yaml.json)

## Full Example

Assumes a Node.js app named `acme-app` migrating from Heroku US region.

```yaml
previews:
  generation: off
projects:
  - name: acme-app
    environments:
      - name: production
        services:
          # Web service (from Heroku web dyno)
          - type: web
            name: acme-app-web
            runtime: node
            plan: starter
            region: oregon
            buildCommand: npm ci && npm run build
            startCommand: npm start
            healthCheckPath: /health
            envVars:
              - key: NODE_ENV
                value: production
              - key: DATABASE_URL
                fromDatabase:
                  name: acme-app-db
                  property: connectionString
              - key: REDIS_URL
                fromService:
                  type: keyvalue
                  name: acme-app-cache
                  property: connectionString
              - key: APP_NAME
                value: acme-app
              - key: LOG_LEVEL
                value: info
              - key: STRIPE_API_KEY
                sync: false
              - key: JWT_SECRET
                sync: false

          # Background worker (from Heroku worker dyno)
          - type: worker
            name: acme-app-worker
            runtime: node
            plan: starter
            region: oregon
            buildCommand: npm ci
            startCommand: node worker.js
            envVars:
              - key: DATABASE_URL
                fromDatabase:
                  name: acme-app-db
                  property: connectionString
              - key: REDIS_URL
                fromService:
                  type: keyvalue
                  name: acme-app-cache
                  property: connectionString
              - key: APP_NAME
                value: acme-app
              - key: LOG_LEVEL
                value: info
              - key: STRIPE_API_KEY
                sync: false

          # Cron job (from Heroku Scheduler or clock dyno)
          - type: cron
            name: acme-app-cron
            runtime: node
            plan: starter
            region: oregon
            schedule: "0 * * * *"
            buildCommand: npm ci
            startCommand: node scripts/scheduled-task.js
            envVars:
              - key: DATABASE_URL
                fromDatabase:
                  name: acme-app-db
                  property: connectionString
              - key: APP_NAME
                value: acme-app
              - key: STRIPE_API_KEY
                sync: false

          # Key Value (from Heroku Data for Redis)
          - type: keyvalue
            name: acme-app-cache
            plan: starter
            ipAllowList:
              - source: 0.0.0.0/0
                description: everywhere

        databases:
          # Postgres (from Heroku Postgres)
          - name: acme-app-db
            plan: basic-1gb
            diskSizeGB: 10  # carried over from Heroku plan allocation

```

## Key Patterns

### Service references

Use `fromDatabase` and `fromService` instead of hardcoding connection strings:

```yaml
# Postgres connection string
- key: DATABASE_URL
  fromDatabase:
    name: acme-app-db
    property: connectionString

# Key Value (Redis) connection string
- key: REDIS_URL
  fromService:
    type: keyvalue
    name: acme-app-cache
    property: connectionString
```

### Environment variables

Define env vars directly on each service. Do not use `envVarGroups` — they can cause misapplication issues during Blueprint sync.

### Secrets

Mark secrets with `sync: false` so the user is prompted in the Dashboard:

```yaml
- key: STRIPE_API_KEY
  sync: false
```

Render prompts for these values only during the initial Blueprint apply. For updates after initial creation, set secrets manually in the Dashboard or via MCP `update_environment_variables`.

## Blueprint Rules

Follow these rules when generating a `render.yaml` for migration:

- **Always use the `projects:`/`environments:` pattern** — the YAML must start with a `projects:` key. Never use flat top-level `services:` or `databases:` keys.
- **Set every `plan:` field** using the [service mapping](service-mapping.md) — look up the Heroku dyno size or add-on plan and use the mapped Render plan. Never hardcode `starter` without checking the mapping first.
- **Set `diskSizeGB` on databases** — carry over the Heroku disk allocation from the [service mapping](service-mapping.md). Round up to 1 or the nearest multiple of 5. Render storage is expandable and can be resized later.
- Always include `previews: { generation: off }` at the root level to disable preview environments by default.
- Use `fromDatabase` for `DATABASE_URL` — never hardcode connection strings.
- Use `fromService` with `type: keyvalue` and `property: connectionString` for `REDIS_URL`.
- Define env vars directly on each service (do not use `envVarGroups`).
- Mark secrets with `sync: false` (user fills these in the Dashboard during Blueprint apply).
- Map region from Heroku using the [service mapping](service-mapping.md).
- Only include service/database blocks that the Heroku app actually uses.

## Plan Selection

Set every `plan:` field by looking up the Heroku dyno size or add-on plan in the [service mapping](service-mapping.md). The example above uses `starter` and `basic-1gb` as representative values. In a real migration, replace these with the mapped plan for the actual Heroku configuration.

**Fallback defaults** (when the Heroku plan is unknown):

| Service type | Fallback plan |
|---|---|
| Web / worker / cron / static / pserv | `starter` |
| Key Value | `starter` |
| Postgres | `basic-1gb` |

## Adapting This Example

- **Python app:** Change `runtime: node` to `runtime: python`, update build/start commands (e.g., `pip install -r requirements.txt`, `gunicorn app:app`)
- **Ruby app:** Change to `runtime: ruby`, update commands (e.g., `bundle install`, `bundle exec puma`)
- **No worker:** Remove the `type: worker` service block
- **No cron:** Remove the `type: cron` service block
- **No Redis:** Remove the `type: keyvalue` service block and any `REDIS_URL` env var references
- **No Postgres:** Remove the `databases` section and any `DATABASE_URL` env var references
- **Static site:** Replace `type: web` with `runtime: static` and add `staticPublishPath`
- **EU region:** Change `region: oregon` to `region: frankfurt` (maps from Heroku `eu` region)
