---
name: fund-comparison
description: Compares exactly 2 funds or ETFs using a structural-first Morningstar analysis. Starts with a Markdown structural snapshot, supports targeted follow-up analysis, and can generate a self-contained HTML report after the user confirms. Use when the user says “compare SPY and QQQ,” “compare two ETFs,” “create a fund comparison report,” or requests a side-by-side Morningstar comparison of two fund tickers.
---

# Fund Comparison

Compare 2 funds using Morningstar MCP tools. Establish what each fund *is* before reporting what it *did*.

## Guardrails

- Compare exactly 2 funds. If more or fewer are provided, ask the user to specify exactly 2.
- Supported types: ETF (FE), open-end fund (FO), closed-end fund (FC). Exclude ST; notify the user.
- Data source: Morningstar MCP tools only. Never infer, estimate, or backfill values.
- Missing field → `N/A`. Tool failure → `N/A` and identify it as a tool failure.
- No investment advice, suitability statements, or performance predictions.
- Do not generate HTML until the user explicitly confirms after seeing the structural snapshot. An initial request for a full report or HTML does not bypass the snapshot.

## Workflow

Read `references/full-workflow.md` once before starting. It is the complete execution contract.

1. Resolve both identifiers.
2. Retrieve the structural snapshot: a narrow shared data-tool call plus `asset_allocation` for each fund, emitted together after IDs resolve.
3. Show the required Markdown snapshot and structural read. State the factual difference most likely to drive performance and risk differences, unless the funds are structurally similar; in that case use a similarity-first read and name the practical distinctions. Then offer targeted analysis or the full HTML report before asking how the user wants to proceed.
4. For a focused question, retrieve only the relevant diagnostic data, answer in Markdown, and offer the full HTML report again.
5. Generate the full report only after explicit post-snapshot confirmation. Reuse the identifiers, snapshot data, allocations, and any relevant follow-up data from this comparison session; retrieve only the remaining report data and required detail. Keep the confirmed-report path direct: retrieve, validate, render, and deliver. Use intermediate planning, status output, or extra steps only when needed to resolve missing data, ambiguity, or an error.

The comparison order is: asset class → Morningstar Category → exposure/universe → implementation → portfolio choices → outcomes. Lead with the first material difference, never performance.

## Examples

- “Compare SPY and VOO.” → Retrieve and show the structural snapshot, then ask how to proceed.
- “Create a fund comparison report for FBND and VOO.” → Show the snapshot first, note the cross-mandate difference, then ask whether to generate HTML.
- “How do SPY and VOO differ by region?” → Show the structural snapshot, then retrieve regional exposure when requested; do not create HTML unless confirmed.
- “Compare SPY, QQQ, and VTI.” → Ask the user to choose exactly 2 funds before calling tools.

## HTML Deliverable

After the user confirms, create one self-contained HTML file: `comparison-[TICKERA]-vs-[TICKERB].html`. Keep the intermediate `D` JSON at a unique path `/tmp/fund-comparison-data-[TICKERA]-[TICKERB]-[RUN-ID].json`; provide it only when the user explicitly asks. Do not create a companion chart or PDF.

When offering it, describe its sections in one compact sentence: fund identity, structure, management, and cost; structural composition and eligible holdings breakdowns; returns and category ranks; risk; ratings; and analyst research with a concise synthesis.

## Post-report Response

Respond with the output HTML path, important data limitations, and one short invitation for questions about the comparison data. Do not mention the intermediate JSON unless asked. Successful validation is an internal delivery gate; report validation only when it fails and prevents delivery.
