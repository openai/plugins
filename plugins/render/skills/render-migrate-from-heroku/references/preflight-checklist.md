# Pre-Flight Checklist

Before creating any resources, validate the migration plan and present it to the user. Check each item below.

## Validation Checks

1. **Runtime supported?** If buildpack maps to `docker`, warn user they need a Dockerfile
2. **Worker dynos?** Flag these — can be defined in a Blueprint (`type: worker`, minimum plan `starter`), but cannot be created via MCP tools directly
3. **Release phase?** If Procfile has `release:`, suggest appending to build command
4. **Static site?** Check for static buildpack, `static.json`, or SPA framework deps — use `create_static_site` instead of `create_web_service`. See detection rules in the [buildpack mapping](buildpack-mapping.md).
5. **Third-party add-ons?** List any add-ons without direct Render equivalents (e.g., Papertrail, SendGrid) — user needs to find alternatives and update env vars
6. **Multiple process types?** If Procfile has >1 entry, each becomes a separate Render service (except `release:`)
7. **Repo URL available?** Verify a Git remote exists:

   ```bash
   git remote -v
   ```

   If no remote exists, stop and guide the user to create a GitHub/GitLab/Bitbucket repo, add it as `origin`, and push before continuing.

   If the URL is SSH format, convert it to HTTPS for service creation and deeplinks:

   | SSH Format | HTTPS Format |
   |---|---|
   | `git@github.com:user/repo.git` | `https://github.com/user/repo` |
   | `git@gitlab.com:user/repo.git` | `https://gitlab.com/user/repo` |
   | `git@bitbucket.org:user/repo.git` | `https://bitbucket.org/user/repo` |

   **Conversion pattern:** Replace `git@<host>:` with `https://<host>/` and remove the `.git` suffix.

8. **Database size?** If Postgres is Premium/large tier, recommend contacting Render support for assisted migration

## Migration Plan Table

Look up each Heroku dyno size and add-on plan in the [service mapping](service-mapping.md) to determine the correct Render plan. Then present the full plan as a table:

```
MIGRATION PLAN — [app-name]
─────────────────────────────────
CREATE (include only items that apply):
  ✅ Web service ([runtime], [mapped-plan]) — startCommand: [cmd]
     Heroku: [dyno-size] ($X/mo) → Render: [mapped-plan] ($Y/mo)
  ✅ Background worker ([runtime], [mapped-plan]) — startCommand: [cmd]
     Heroku: [dyno-size] ($X/mo) → Render: [mapped-plan] ($Y/mo)
  ✅ Cron job ([mapped-plan]) — schedule: [cron expr] — command: [cmd]
  ✅ Postgres ([mapped-plan], diskSizeGB: [size])
     Heroku: [plan-slug] ($X/mo) → Render: [mapped-plan] ($Y/mo + storage)
  ✅ Key Value ([mapped-plan])
     Heroku: [plan-slug] ($X/mo) → Render: [mapped-plan] ($Y/mo)

ESTIMATED MONTHLY COST:
  Heroku: $[total]/mo → Render: $[total]/mo
  (Render storage billed separately at $0.30/GB/mo in 5 GB increments; cannot be scaled down once provisioned)

METHOD: [Blueprint | MCP Direct Creation]

MANUAL STEPS REQUIRED:
  ⚠️ Custom domain: [domain] — configure after deploy
  ⚠️ Replace add-on: [name] → find alternative

ENV VARS: [N] to migrate, [M] filtered out
DATABASE: [size] — pg_dump/render psql required
─────────────────────────────────
Proceed? (y/n)
```

Use the pricing columns in the [service mapping](service-mapping.md) to calculate costs. Sum up the Render $/mo for each service, database, and Key Value store. For Postgres, note that storage is billed separately.

Wait for user confirmation before creating any resources.
