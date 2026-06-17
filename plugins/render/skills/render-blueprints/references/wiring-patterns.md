# Cross-Service Wiring Patterns

Complete examples for wiring services together in `render.yaml` via `envVars`.

---

## fromDatabase

Reference a Managed Postgres database property:

```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: my-postgres
      property: connectionString
```

Available properties:

| Property | Value |
|----------|-------|
| `connectionString` | Full `postgres://` URL (most common) |
| `host` | Database hostname |
| `port` | Database port |
| `user` | Database user |
| `password` | Database password |
| `database` | Database name |

The `name` must match a database defined in the `databases` section of the same Blueprint, or an existing database in the workspace.

---

## fromService (Key Value)

Reference a Key Value (Redis-compatible) instance:

```yaml
envVars:
  - key: REDIS_URL
    fromService:
      name: my-redis
      type: keyvalue
      property: connectionString
```

Available properties:

| Property | Value |
|----------|-------|
| `connectionString` | Full `redis://` URL |
| `host` | Internal hostname |
| `port` | Port number |
| `hostport` | `host:port` combined |

---

## fromService (Private Service or Web Service)

Reference another service's internal address or environment variable:

```yaml
envVars:
  # Get internal hostname
  - key: AUTH_SERVICE_HOST
    fromService:
      name: auth-service
      type: pserv
      property: host

  # Get host:port
  - key: AUTH_SERVICE_URL
    fromService:
      name: auth-service
      type: pserv
      property: hostport

  # Copy an env var from another service
  - key: SHARED_SECRET
    fromService:
      name: auth-service
      type: pserv
      envVarKey: API_SECRET
```

Available properties for `pserv` and `web`:

| Property | Value |
|----------|-------|
| `host` | Internal hostname |
| `hostport` | `host:port` combined |

Use `envVarKey` to copy a specific environment variable value from the other service.

---

## fromGroup

Link an entire environment group:

```yaml
envVars:
  - fromGroup: shared-secrets
```

This adds all variables from the named group to the service. The group must exist in the workspace or be defined in `envVarGroups`.

---

## generateValue

Generate a random base64-encoded 256-bit secret:

```yaml
envVars:
  - key: APP_SECRET
    generateValue: true
```

The value is generated once on initial Blueprint creation and persists across syncs.

---

## sync: false

Prompt the user to provide a value in the Dashboard:

```yaml
envVars:
  - key: STRIPE_API_KEY
    sync: false
```

Use for secrets that should never appear in the Blueprint file.

---

## Combined Example

A web service wired to Postgres, Key Value, and a private service:

```yaml
services:
  - type: web
    name: api
    runtime: node
    plan: starter
    buildCommand: npm ci
    startCommand: npm start
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: cache
          type: keyvalue
          property: connectionString
      - key: AUTH_HOST
        fromService:
          name: auth
          type: pserv
          property: hostport
      - key: JWT_SECRET
        generateValue: true
      - key: STRIPE_KEY
        sync: false
      - fromGroup: shared-config

  - type: pserv
    name: auth
    runtime: node
    plan: starter
    buildCommand: npm ci
    startCommand: npm start

  - type: keyvalue
    name: cache
    plan: starter
    maxmemoryPolicy: allkeys-lru
    ipAllowList:
      - source: 0.0.0.0/0
        description: everywhere

databases:
  - name: db
    plan: starter

envVarGroups:
  - name: shared-config
    envVars:
      - key: LOG_LEVEL
        value: info
```

---

## Edge Cases

- **sync: false only prompts on initial Blueprint setup.** On subsequent syncs, existing `sync: false` values are preserved. Adding a new `sync: false` var to an existing Blueprint does not prompt.
- **sync: false is excluded from preview environments.** Users must set these values manually for each preview.
- **sync: false is invalid in envVarGroups.** It is silently ignored if used in a group definition.
- **fromService/fromDatabase can reference services outside the Blueprint** but the referenced service must already exist in the workspace.
- **generateValue** generates once on initial create. It does not regenerate on subsequent Blueprint syncs.
