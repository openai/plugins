# Quartr Provider Guide

> Internal provider guide. Load through `internal-support/policy.md` only after the current workflow selects a callable Quartr route for an attempted source category. This is not a selectable skill.

## Load Gate

Do not load this guide during user-context preflight, onboarding, or unrelated source setup. A configured `.app.json` entry, preferred provider, or surfaced tool name is not proof that Quartr is callable for the current user.

## Authority And Scope

Use the live Quartr action schema as the source of truth. If it differs from this guide, follow the live schema and retry with the smallest valid call. When using a generic connector runner, place action arguments inside top-level `params`. Use Quartr before web search for public-company filings, annual and quarterly reports, earnings releases, presentations, transcripts, events, management commentary, and standardized actual financials.

Before calling Quartr, read `references/connector-playbook.md`. For a workbook workflow, also read `references/workbook-mode.md` before editing the workbook.

## Default Sequence

1. Call `search_companies` with one ticker or clean company name.
2. Validate the company match before using `companyId`. Do not accept a fuzzy top result when ticker or normalized company name does not match.
3. Use `get_financials` for standardized actuals, one `financialType` at a time.
4. Use `list_documents` or `list_events` to identify bounded source material.
5. Prefer `search_documents`, `get_document_summary`, or `get_event_summary` before broad document reads. Use targeted `read_document` calls only when needed.
6. Compute derived values from sourced inputs and preserve their provenance.

Never invent company IDs, document IDs, event IDs, source URLs, filing dates, or page references.

## Call Shape And Data Rules

- `search_companies` uses `query`.
- `get_financials` uses `companyId`, ISO `startDate` and `endDate` when needed, `periodType`, and one `financialType`: `incomeStatement`, `balanceSheet`, or `cashFlowStatement`.
- `list_documents` uses `companyId`, narrow `documentTypes`, and a small `limit`, usually 5-10.
- `search_documents` uses a short `query`, `documentTypes`, and `filter: "companyId:=<id>"` when restricting results to one company.
- Use ISO dates for Quartr inputs. Label non-calendar fiscal periods from returned event and document metadata.
- Keep reported actuals, guidance, estimates, and derived calculations separate.

## Output Budget And Recovery

Prefer several small calls over broad pulls. If `get_financials` is too large, retain one `financialType` and split the date range to one year per call. If a document read is too large, use a summary or targeted search, then read fewer pages. If company search returns weak matches, retry with ticker or a shorter distinctive name rather than using an unrelated result.

## Citation Discipline

Carry returned `referenceUrl`, `reportUrl`, document URL, event URL, and page reference fields into tables, artifacts, charts, and prose. Cite computed values through their sourced inputs. Identify Quartr as the data source without implying that unrelated values came from Quartr.
