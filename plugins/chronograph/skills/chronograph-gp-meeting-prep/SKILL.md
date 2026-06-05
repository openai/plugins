---
name: chronograph-gp-meeting-prep
description: >
  Prepare an LP to meet with their fund manager (GP): review the fund's latest
  reporting, surface what changed since last period, and draft the questions
  worth raising. Use when someone is getting ready for a manager call, quarterly
  check-in, annual meeting, LPAC meeting, or a re-up decision — for example "I
  have my quarterly call with this manager next week, help me prep," "what
  changed in this fund this quarter," "what should I ask them about these marks,"
  or "what are the red flags in this reporting package." Draws on Chronograph
  fund and portfolio data when connected — captured reporting such as fund
  performance, schedules of investments, and portfolio company KPI profiles —
  and asks the LP to provide anything else it needs, such as a capital account
  statement, investor letter, or AGM or board deck.
---

# Chronograph GP Meeting Prep

**Requirements:** A connected Chronograph MCP server. These workflows are designed for permissioned Chronograph users to connect to their private investment data.

## Overview

Prepare an LP for a meeting with a GP by reviewing fund reporting, surfacing what changed, identifying diligence questions, and producing a concise meeting brief. The brief exists to sharpen a forward decision — a re-up, a secondary sale, or an LPAC vote — so prioritize what bears on those. Use Chronograph as the source of truth where connected and permissioned; otherwise work from user-provided reporting materials.

Default to a chat brief. Create a document, workbook, or deck only when the user asks for an artifact.

## Workflow

1. Clarify scope only when needed: GP, fund, reporting period, meeting type, as-of date, currency, units, output format, and whether the user wants a quick brief or a formal prep document.
2. Resolve the relevant fund, manager, commitment, reporting period, and LP perspective from Chronograph where available. If Chronograph is unavailable, ask for the GP reporting package or a pasted/uploaded summary.
3. Gather the fund baseline, anchoring first on the figures the GP reported this period and citing the source document where available: gross performance, cost, realized and unrealized value, current valuation, portfolio holdings, prior-period values, and fund attributes. Carry net performance — NAV, calls, distributions, TVPI/DPI/RVPI, and net IRR — as the LP's headline return, clearly labeled gross versus net and dated.
4. Review document-backed reporting content. When Chronograph document semantic search is available, use it as a primary step to find the story behind the numbers: what drove calls and distributions, how the GP describes its marks, and the commentary on portfolio company KPIs.
5. If a document the meeting needs isn't in the connected context, ask the LP to provide it. Do not infer narrative, management explanations, or meeting context from structured data alone.
6. Compare current period to prior period: performance movement, cashflow activity, NAV and unfunded movement, valuation changes, portfolio company adds/exits, concentration changes, and KPI movements.
7. Separate facts from interpretation. Use reporting data for facts, cite document support when available, and label inferred questions as analyst prompts rather than confirmed issues.
8. Produce a prioritized meeting brief with key changes, watch items, suggested GP questions, and follow-up requests.

## Chronograph Data Use

When the Chronograph MCP is available, use it to retrieve the relevant portfolio, fund, commitment, performance, exposure, and report-derived document context where permissioned. Keep public-facing explanations at the workflow level; do not expose internal schemas, private tool names, field mappings, or retrieval recipes.

Source discipline:

- Cite Chronograph, document, page, period, or user-provided source for quantitative claims whenever available.
- State currency, units, as-of date, and whether values are GP-reported, Chronograph-derived, user-provided, or estimated.
- Do not fabricate NAVs, KPIs, performance metrics, holdings, explanations, or manager commentary.
- If sources disagree, present the discrepancy and ask the GP-facing question that follows from it.

## Review Priorities

Use `references/report-review-checklist.md` for a fuller checklist when reviewing a package. Anchor the review on the figures the GP reported this period, citing the source document where available, and present net performance as the LP's headline return clearly labeled gross versus net. Prioritize:

- Performance: lead with the GP-reported figures — gross IRR and MOIC, cost, and realized and unrealized value — and their movement versus prior period, citing sources where available. Carry net performance (TVPI, DPI, RVPI, net IRR) as the LP's bottom-line return, labeled gross versus net, and watch the trend from unrealized value toward realized distributions.
- Cashflows: calls, distributions, recallable amounts, unfunded exposure, and unusual activity. Distinguish realized-cash distributions from those financed by NAV or subscription-line facilities.
- Valuation: write-ups, write-downs, stale marks, methodology changes (including any shift toward a cost basis), the GP's written valuation policy, and valuation concentration.
- Portfolio: new investments, exits, major company KPI changes, top holdings, sector/geography exposure, and single-name concentration.
- Reporting quality: missing explanations, inconsistent values, stale dates, changed definitions, or unexplained metric movement.
- Meeting readiness: three to eight prioritized questions, required follow-up materials, and open items to track.

## Output

For a quick answer, use this shape:

- Executive snapshot
- What changed this period
- Items to ask the GP
- Follow-up requests
- Source notes and assumptions

For a formal memo or document, use `references/meeting-brief-template.md`.

Use `references/question-bank.md` when the user wants more complete question coverage by topic or when the review surfaces a broad set of issues.

## Fallback Behavior

If Chronograph is unavailable, or the meeting needs a document outside the connected context:

- Ask the LP for the relevant GP reporting package or materials — for example the quarterly report, schedule of investments, capital account statement, or prior meeting notes.
- If only partial data is available, produce a partial brief and list the missing inputs needed for a complete meeting prep.
- If the user provides PDFs, workbooks, or pasted text, extract only what is supported by the material and cite the source artifact.

## Guardrails

- Treat the output as draft analyst work product for LP meeting preparation.
- Do not provide investment, legal, tax, audit, or valuation advice.
- Do not imply that a missing GP explanation is misconduct; frame gaps as questions or follow-up requests.
- Do not infer manager intent or portfolio company facts from metric movement alone.
- Avoid overprecision. Round appropriately and disclose incomplete source coverage.
