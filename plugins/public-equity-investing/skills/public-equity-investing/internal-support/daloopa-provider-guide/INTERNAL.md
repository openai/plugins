# Daloopa Provider Guide

> Internal provider guide. Load through `internal-support/policy.md` only after the current workflow selects a callable Daloopa route for an attempted source category. This is not a selectable skill.

## Load Gate

Do not load this guide during user-context preflight, onboarding, or unrelated source setup. A configured `.app.json` entry, preferred provider, or surfaced tool name is not proof that Daloopa is callable for the current user.

## Authority And Scope

Use the live Daloopa action schema as the source of truth. If it differs from this guide, follow the live schema and retry with the smallest valid call. Use Daloopa for source-backed public-company financials, KPIs, and targeted document snippets. Keep live prices, consensus, news, and non-Daloopa sources separately labeled when another route owns them.

Before calling Daloopa, read `references/connector-playbook.md`. For a workbook workflow, also read `references/workbook-mode.md` before editing the workbook.

## Default Sequence

1. Call `discover_companies` with one ticker or clean company name and capture the returned `company_id` plus latest available period fields.
2. Call `discover_company_series` with that `company_id`, one explicit anchor period, and one narrow metric family.
3. Inspect returned labels, select the needed series IDs, and call `get_company_fundamentals` with explicit periods and roughly 15 series IDs or fewer per batch.
4. Use `search_documents` only for targeted qualitative context such as guidance, strategy, risks, or performance explanations.
5. Compute derived values from sourced inputs and preserve their provenance.

Never invent company IDs, series IDs, periods, fundamental IDs, or source URLs.

## Call Shape And Data Rules

- `discover_companies` uses `keywords: list[str]`.
- `discover_company_series` uses `company_id`, `keywords`, and `periods`.
- `get_company_fundamentals` uses `company_id`, `periods`, and `series_ids`.
- `search_documents` uses `keywords`, `company_ids`, and `periods`; its keywords use AND logic, so retry sparse searches with fewer terms.
- Use explicit `YYYYQ#` or `YYYYFY` periods. Prefer the connector-returned latest period over an assumption based on the current date.
- For quarterly analysis, use `value_quarter` when available. Label any conversion from year-to-date values.
- Keep reported actuals, guidance, estimates, and derived calculations separate.

## Output Budget And Recovery

Prefer several small calls over broad pulls. If a call is too large, narrow the metric family, periods, peer set, or series-ID batch before retrying. If a call fails, check live parameter names and types, retry minimally, and state the specific remaining gap if the route is still blocked.

## Citation Discipline

Capture each returned fundamental `id` at pull time and carry it through tables, artifacts, charts, and prose. Cite every Daloopa-sourced figure using its source URL. Cite computed values through their sourced inputs. Identify Daloopa as the data source without implying that unrelated values came from Daloopa.
