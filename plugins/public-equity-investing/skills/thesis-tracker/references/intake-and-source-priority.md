# Intake And Source Priority

Use when context is missing, partial, conflicting, stale, or source-sensitive.

## Context Rules

- **No context:** do not invent a company thesis. Produce blank institutional tracker tables and ask for minimum inputs.
- **Ticker-only:** use connected/public sources for objective facts only; label thesis, mandate, cost basis, target, risk tolerance, and house view as preliminary/missing.
- **Partial context:** extract what exists and expose gaps. Memo = thesis/pillars/catalysts/risks; model = drivers/assumptions; tracker = preserve structure and flag stale/missing fields; release/transcript = evidence only unless prior thesis is supplied; position list = triage review priority.
- **Full context:** append a new update, preserve original underwriting and prior entries, update statuses, and add changelog.

Minimum intake: issuer/ticker/security, direction, role/mandate, horizon, thesis, position/rating, source materials, output format.

## Source Hierarchy

1. User prompt and explicit instructions.
2. User-provided files, tracker, model, memo, notes as house source of record unless stale/contradicted.
3. Callable connected routes or user-provided firm-system exports.
4. Official company/regulatory sources.
5. Market data and consensus vendors.
6. Earnings calls, conferences, investor days.
7. Broker/third-party research, expert calls, alt-data with licensing/bias labels.
8. News/web for current public facts and source discovery.
9. Assumptions/inferences, clearly labeled.

Reliability labels: high (primary/user/source file), medium (reputable transcript/vendor/news/research), low (anecdote/rumor/vague/stale), unknown (uncited/not inspectable).

## Freshness

Track source date, reporting period, model version, consensus timestamp, market data timestamp, prior tracker as-of, and whether post-date events are included. If a key point may have changed and no current source is available, mark stale/unavailable.

## Clarification Policy

Do not block on broad questions when a useful labeled output is possible. Ask only targeted blockers such as direction, append-vs-rewrite, model source of truth, or desired output format.

## Preservation

Append rows/sections, create version labels, keep changelog, and mark stale/superseded/duplicate/contradicted items rather than deleting. Show proposed deletions/merges before cleanup unless direct deletion is explicitly authorized.

## Labels

Use `Fact`, `Assumption`, `Judgment`, `Open question`, and `Sensitive` labels where source boundaries matter.
