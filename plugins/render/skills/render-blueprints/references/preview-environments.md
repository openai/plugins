# Preview Environments

Pull request (PR) previews spin up temporary stacks from your Blueprint so each PR can be tested in isolation. This document summarizes Blueprint knobs and behavioral constraints.

## Top-level `previews`

```yaml
previews:
  generation: off          # default
  expireAfterDays: 3
```

### `previews.generation`

| Value | Behavior |
|-------|----------|
| `off` | No automatic preview creation from PRs (default). |
| `manual` | Previews are created on demand (Dashboard/workflow action—exact UX may vary by integration). |
| `automatic` | Previews are created for eligible PRs per Render’s Git integration rules. |

### `previews.expireAfterDays`

- Positive integer: automatically **delete** preview environments after **N** days to control cost and clutter.
- Omit or set per product/docs for “no expiry” behavior.

---

## Service-level override

Individual services may override preview generation:

```yaml
services:
  - type: web
    name: api
    runtime: node
    # ...
    previews:
      generation: off
```

Use this when a heavy or sensitive service should not run in every preview (e.g. workers that touch billing).

---

## `previewPlan` constraints

- **`previewPlan`** selects the instance type for preview **service** instances.
- **Cannot mix** flexible and non-flexible instance types between **`plan`** and **`previewPlan`** in ways Render rejects (same family constraints as production).
- If previews fail validation, align `previewPlan` with the primary `plan` category or choose a supported preview size.

---

## Database previews: `previewDiskSizeGB`

- Databases created for previews may use **`previewDiskSizeGB`** (and related preview fields per schema) so preview DB storage is smaller/cheaper than production.
- Keep disk large enough for migrations and seed data used in CI.

---

## `sync: false` env vars in previews

- Environment variables with **`sync: false`** are **excluded** from automatic preview configuration.
- **Users must set these manually** on preview services (Dashboard or automation) or the app may fail at runtime (missing secrets).

**Mitigation:** For previews, prefer secrets that can be generated per-preview, or use non-secret placeholders, or inject via your CI pipeline into preview env as allowed by your security model.

---

## Autoscaling in previews

- **Autoscaling is disabled** in preview environments.
- Instance counts follow **minimum instance** behavior (effectively pinned to the floor—commonly `scaling.minInstances` when autoscaling exists, or a single instance).
- Do not rely on preview traffic to test autoscale rules; test scaling in staging/production-like environments.

---

## PR workflow — how previews map to Git

1. A **pull request** is opened against the tracked branch (e.g. `main`).
2. Render uses the **PR head commit** (and Blueprint at that revision) to propose or create a preview stack, depending on `previews.generation` and service overrides.
3. **Build filters** and **branch** settings on services still matter: misconfigured `branch` can break the expectation that previews track the PR (see `common-mistakes.md`).
4. When the PR closes or merges, previews are typically torn down per product rules; **`expireAfterDays`** enforces a maximum lifetime regardless.

---

## Checklist

- [ ] `previews.generation` matches team workflow (`off` / `manual` / `automatic`).
- [ ] `expireAfterDays` set if org needs automatic cleanup.
- [ ] `previewPlan` compatible with primary `plan`.
- [ ] `previewDiskSizeGB` (if used) sufficient for migrations.
- [ ] No reliance on `sync: false` secrets without a preview secret strategy.
- [ ] Service-level `previews` overrides reviewed for workers/cron/private services.

Validate with `render blueprints validate` and `https://render.com/schema/render.yaml.json`.
