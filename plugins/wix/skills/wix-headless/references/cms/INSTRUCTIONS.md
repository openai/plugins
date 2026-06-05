---
name: cms-implementer
description: "Implements structured content pages (About, FAQ, portfolios, team directories, resource libraries) via Wix CMS and @wix/data. Scopes: seed, pages. Extends references/shared/IMPLEMENTER.md."
---

# CMS Implementer

Extends `references/shared/IMPLEMENTER.md`. Read that file first for phase routing, REST auth + doc lookups, prompt-inlined inputs (no site.json reads), return contract, style conventions, and common failure modes.

## Scope routing

| Scope | Phase | Reference |
|-------|-------|-----------|
| `seed` | Seed (create collections + seed items via REST) | `./CMS_FOUNDATIONS.md` (seeding, business half) + use-case ref under `../astro/cms/` (collection schema + seed-with-images) |
| `pages` | Pages (About + FAQ pages read CMS via @wix/data inline) | `../astro/cms/CMS_FOUNDATIONS.md` (code patterns) + use-case ref under `../astro/cms/` |

No `components` scope — CMS pages SSR content inline via `@wix/data`; no React islands.

## Use-case references

Pick based on the business type (the orchestrator names one in your prompt):

- `../astro/cms/FAQ_KNOWLEDGE_BASE.md` — Q&A accordions, category sections, search
- `../astro/cms/PORTFOLIO.md` — project grid, category filter tabs, project detail
- `../astro/cms/TEAM_DIRECTORY.md` — department-grouped directory, staff cards
- `../astro/cms/RESOURCE_LIBRARY.md` — file listings, download buttons, file type badges

## Files this vertical creates / contributes

See `<SKILL_ROOT>/references/verticals/cms.md` frontmatter.

## Page width (FAQ, About, long-form CMS)

Read `references/shared/STYLING.md` § "Prose / reading width". **Do not** wrap FAQ/About body copy in `max-w-3xl` unless `--container-3xl` exists in `src/styles/global.css` `@theme`. Prefer `container-reading`, `max-w-6xl` (when `--container-6xl` is defined), or `max-w-[48rem]`. A bare `max-w-3xl` with only a spacing scale ships a ~80px column.

## CMS-specific failure modes

| Wrong | Right |
|---|---|
| `items.queryDataItems(...)` / `items.query({ dataCollectionId })` | `items.query("CollectionId").find()` — queryDataItems doesn't exist |
| React islands for static content pages | SSR inline with `@wix/data`; no islands needed |
| `max-w-3xl` on FAQ/About wrappers without `--container-3xl` in `@theme` | `container-reading` or `max-w-[48rem]` / `max-w-6xl` per STYLING.md |
| Return `status: "complete"` without re-querying the collection | Always run the verify-after-insert query (see CMS_FOUNDATIONS.md § "Verify inserts with a live query"); fail fast if any field is missing |
| Report `fields: [...]` guessed from the insert body | Report `storedFields: [...]` matching the actual keys in the query response's `data` object — pages agents compare against these |
| Assume text fields survive downstream image PATCHes | Seeder's job is to verify content is present; images agent must preserve via read-merge-PUT (images INSTRUCTIONS.md § "CMS Items") |