---
description: Bootstrap a repository with Vercel-linked resources by running preflight checks, provisioning integrations, verifying env keys, and then executing db/dev startup commands safely.
---

# Vercel Project Bootstrap

Run a deterministic bootstrap flow for new or partially configured repositories.

## Preflight

<!-- Sourced from bootstrap skill: Preflight -->
1. Confirm Vercel CLI is installed and authenticated.

```bash
vercel --version
vercel whoami
```

2. Confirm repo linkage by checking `.vercel/project.json`.
3. If not linked, inspect available teams/projects before asking the user to choose:

```bash
vercel teams ls
vercel projects ls --scope <team>
vercel link --yes --scope <team> --project <project>
```

4. Find the env template in priority order: `.env.example`, `.env.sample`, `.env.template`.
5. Create local env file if missing:

```bash
cp .env.example .env.local
```

6. Detect package manager and available scripts (`db:push`, `db:seed`, `db:migrate`, `db:generate`, `dev`) from `package.json`.
7. Inspect auth/database signals (`prisma/schema.prisma`, `drizzle.config.*`, `auth.*`, `src/**/auth.*`) to scope bootstrap details.

Stop with clear guidance if CLI auth or linkage fails.

## Plan

Execute in this order:

1. Preflight validation and project linking.
2. Resource provisioning (prefer Vercel-managed Neon integration).
3. Secret/bootstrap env setup (`AUTH_SECRET`, env pull, key verification).
4. Application bootstrap (`db:*` then `dev`) only after env checks pass.

<!-- Sourced from bootstrap skill: Rules -->
- Do not run `db:push`, `db:migrate`, `db:seed`, or `dev` until Vercel linking is complete and env keys are verified.
- Prefer Vercel-managed provisioning (`vercel integration ...`) for shared resources.
- Use provider CLIs only as fallback when Vercel integration flow is unavailable.
- Never echo secret values in terminal output, logs, or summaries.

## Commands

### 1. Link + local env template

Copy the first matching template file only if `.env.local` does not exist:

```bash
cp .env.example .env.local
```

If `.env.example` is absent, use `.env.sample` or `.env.template`.

### 2. Provision Postgres

<!-- Sourced from bootstrap skill: Resource Setup: Postgres -->
### Preferred path (Vercel-managed Neon)

1. Read integration setup guidance:

```bash
vercel integration guide neon
```

2. Add Neon integration to the Vercel scope:

```bash
vercel integration add neon --scope <team>
```

3. Verify expected environment variable names exist in Vercel and pull locally:

```bash
vercel env ls
vercel env pull .env.local --yes
```

### Fallback path 1 (Dashboard)

1. Provision Neon through the Vercel dashboard integration UI.
2. Re-run `vercel env pull .env.local --yes`.

### Fallback path 2 (Neon CLI)

Use Neon CLI only when Vercel-managed provisioning is unavailable. After creating resources, add required env vars in Vercel and pull again.

### 3. Generate and store `AUTH_SECRET`

<!-- Sourced from bootstrap skill: AUTH_SECRET Generation -->
Generate a high-entropy secret without printing it, then store it in Vercel and refresh local env:

```bash
AUTH_SECRET="$(node -e "console.log(require('node:crypto').randomBytes(32).toString('base64url'))")"
printf "%s" "$AUTH_SECRET" | vercel env add AUTH_SECRET development preview production
unset AUTH_SECRET
vercel env pull .env.local --yes
```

### 4. Verify required env keys

<!-- Sourced from bootstrap skill: Env Verification -->
Compare required keys from template file against `.env.local` keys (names only, never values):

```bash
template_file=""
for candidate in .env.example .env.sample .env.template; do
  if [ -f "$candidate" ]; then
    template_file="$candidate"
    break
  fi
done

comm -23 \
  <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$template_file" | cut -d '=' -f 1 | sort -u) \
  <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env.local | cut -d '=' -f 1 | sort -u)
```

Proceed only when missing key list is empty.

Do not continue if any required keys are missing.

### 5. Run app bootstrap commands (after verification)

<!-- Sourced from bootstrap skill: App Setup -->
After linkage + env verification:

```bash
npm run db:push
npm run db:seed
npm run dev
```

Use the repository package manager (`npm`, `pnpm`, `bun`, or `yarn`) and run only scripts that exist in `package.json`.

## Verification

<!-- Sourced from bootstrap skill: Bootstrap Verification -->
Confirm each checkpoint:

- `vercel whoami` succeeds.
- `.vercel/project.json` exists and matches chosen project.
- Postgres integration path completed (Vercel integration, dashboard, or provider CLI fallback).
- `vercel env pull .env.local --yes` succeeds.
- Required env key diff is empty.
- Database command status is recorded (`db:push`, `db:seed`, `db:migrate`, `db:generate` as applicable).
- `dev` command starts without immediate config/auth/env failure.

If verification fails, stop and report exact failing step plus remediation.

## Summary

<!-- Sourced from bootstrap skill: Summary Format -->
Return a final bootstrap summary in this format:

```md
## Bootstrap Result
- **Linked Project**: <team>/<project>
- **Resource Path**: vercel-integration-neon | dashboard-neon | neon-cli
- **Env Keys**: <count> required, <count> present, <count> missing
- **Secrets**: AUTH_SECRET set in Vercel (value never shown)
- **Migration Status**: not-run | success | failed (<step>)
- **Dev Result**: not-run | started | failed
```

## Next Steps

<!-- Sourced from bootstrap skill: Bootstrap Next Steps -->
- If env keys are still missing, add the missing keys in Vercel and re-run `vercel env pull .env.local --yes`.
- If DB commands fail, fix connectivity/schema issues and re-run only the failed db step.
- If `dev` fails, resolve runtime errors, then restart with your package manager's `run dev`.
