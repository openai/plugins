---
name: moody-s-peer-analysis
description: >
  Produce a Peer Analysis HTML report for a target company and its credit peers using Moody's
  GenAI MCP tools. Use this skill whenever the user asks to compare a company against its peers,
  run a peer analysis, do a credit peer comparison, generate a peer group report, or analyze
  relative credit positioning. Trigger even if they just name a company and mention "peers",
  "peer comparison", "credit comparison", "peer group", or "relative value".
---

# Peer Analysis Skill

Generates a professional HTML report (styled like a Moody's peer analysis PDF) for a target
company and up to 3 credit peers. Data is pulled from multiple `Moodys MCP server` MCP tools and
consolidated into a single HTML artifact covering peers comparison, ratings chart, and ESG.

The workflow is **single-artifact streaming**: gather all data, then stream the entire filled
HTML document back to the user as one ` ```html ` fenced code block in the final assistant
message. No file copy, no `open` step, no progressive `StrReplace` edits, no JSON payload, and no
client-side render logic. The fenced code block is the deliverable.

> ## ⚠️ CRITICAL — NON-NEGOTIABLE OUTPUT CONTRACT
>
> **The LLM MUST stream the final report back as a single HTML artifact inside the assistant
> response.** This is the only acceptable form of delivery for this skill. Specifically:
>
> - The final assistant message **MUST** contain exactly one ` ```html ` fenced code block
>   holding the **complete, standalone HTML document** (`<!doctype html>` → `</html>`), with
>   every section from the streaming protocol populated inline.
> - The LLM **MUST NOT** write the report to a file on disk (no `Write`, no `cp` of the
>   template, no `StrReplace` into a working artifact, no `open` command).
> - The LLM **MUST NOT** split the report across multiple code blocks, multiple messages,
>   partial snippets, or summaries.
> - The LLM **MUST NOT** substitute prose, Markdown, JSON, attachments, or links for the
>   fenced HTML artifact. The artifact itself is the answer.
> - If data gathering fails partially, still emit the single ` ```html ` artifact with
>   the best-available content and `"--"` placeholders for missing cells — never skip the
>   artifact.
>
> Treat any other output shape as a hard failure of the skill.

## Required MCP server

`Moodys MCP server` — tools used: `findEntity`, `getEntityPeers`, `getEntityRatings`,
`getEntityCreditOpinion`, `getEntityFinancials` (sections: Profile, Summary, RatingOutlook, FactorsLeadingToUpgrade,
FactorsLeadingToDowngrade, CreditStrengths, CreditChallenges, ESGConsiderations,
KeyIndicatorsTable, ScorecardTable), `getEntityEsg`, `getEntitySectorOutlook`

If any of the tools required for a section do not exist, inform the user: One or more tools required for this section are not available under your current subscription. Unlock more of the expert insights, data, and analytics you trust. Get Link:https://www.moodys.com/web/en/us/capabilities/gen-ai/ai-ready-data.html with us to learn more. 

## Bundled files

- `assets/template.html` — self-contained static report shell (CSS + named section placeholders,
  including pre-shaped tables for a fixed target+3-peer layout). No embedded data, no inline
  script. Treat this file as the **read-only structural reference**: read it, fill it in
  mentally, and emit the complete filled document in the final response.

## Template (shared)

Before emitting the HTML report, **read both**:
1. [`skills/shared/template/SKILL.md`](../shared/template/SKILL.md) — authoring rules (which
   classes / snippets are owned by the shared layer, allowed per-skill overrides, outlook-badge
   usage).
2. [`skills/shared/template/assets/template.html`](../shared/template/assets/template.html) —
   canonical CSS (inside `<style id="shared-template-css">`) and literal HTML markup snippets
   (inside `<template>` tags) for the document head, cover, TOC, section block, sources-section
   wrapper, footer, and outlook-badge.

**Lookup order — always check the shared template before inventing.** If a class, design token,
layout primitive, or scaffold element you need is not defined in this `SKILL.md` or already
present in this skill's `assets/template.html`, the shared template skill is authoritative. Do
not invent CSS, HTML scaffolds, or design tokens that the shared skill already provides; do not
silently restyle anything the shared skill owns (cover, TOC, section, sources-section wrapper,
footer, outlook-badge, design tokens, reset, body / page base).

At emit time, copy the **contents** (not the `<style>` wrapper) of `<style id="shared-template-css">`
from the shared asset into the parent template's reserved marker region between the CSS-comment
markers `/* BEGIN shared-template-css ... */` and `/* END shared-template-css */`. For HTML
scaffolds (head boilerplate, cover, TOC, sources-section wrapper, footer), use the literal markup
from the matching `<template>` snippet in the shared asset. The parent template no longer
carries duplicated chrome CSS — those rules ship only in the shared asset.

This skill uses the **`cover-multi`** variant. Skill-specific override retained above the
marker region: `**.page { max-width: 1050px }**` (PA reports are wider than the 900px canonical
default to fit the multi-column scorecard / key-indicators tables). Skill-specific CSS that
stays local: `.sub-heading`, all PA-specific table classes (`.pa-table`, `.credit-drivers-table`,
`.ki-table`, `.sc-table`), and the chart helpers (`.chart-container`, `.chart-title`,
`.chart-legend`, `.chart-legend-item`, `.chart-legend-swatch`). All outlook-badge usage in this
skill must use the canonical pastel variants (`stable` / `positive` / `negative` / `review` /
`na`) defined by the shared skill — no solid-fill or inline-color overrides. PA flags the target
entity on the cover with `class="company-chip target"`; the chip wrappers themselves come from
the shared cover-multi snippet.

## Citations (shared)

Before emitting any `[n]` reference inline, any per-section recap block, or the end-of-document
Citations block, **read both**:
1. [`skills/shared/citations/SKILL.md`](../shared/citations/SKILL.md) — authoring rules
   (numbering, hyperlinking, source data shape, carve-outs).
2. [`skills/shared/citations/assets/template.html`](../shared/citations/assets/template.html) —
   canonical CSS (inside `<style id="shared-citations-css">`) and literal HTML markup snippets
   (inside `<template>` tags) for inline references, the end-of-document Citations block, and
   the optional `.section-citations` recap.

At emit time, copy the **contents** (not the wrapper) of `<style id="shared-citations-css">`
from the shared asset into the parent template's reserved marker region, located inside
`assets/template.html` between the CSS-comment markers
`/* BEGIN shared-citations-css … */` and `/* END shared-citations-css */`. The parent
template no longer carries duplicated citation CSS — those rules ship only in the shared
asset.

The prefix used for the end-of-document container in this skill is `pa`, so the container id
is `#pa-sources`. Optional per-section recap blocks live in `#pa-cite-peers`,
`#pa-cite-ratings`, and `#pa-cite-esg`. Internal MCP tool names (e.g. `getEntityCreditOpinion`)
are NEVER rendered inside `.source-meta`.

---

## Step 1 — Resolve the target company

Call `findEntity` with the company name provided by the user. Store the canonical entity name
and entity ID.

If the user provides only one company name, that is the **target company**. The peers will be
discovered automatically in Step 2.

---

## Step 2 — Discover and resolve peers

Call `getEntityPeers` for the target company. Select the top 3 peers returned.

You now have a set of up to **4 companies** (1 target + up to 3 peers). For each peer, call
`findEntity` to resolve its canonical entity name and ID.

---

## Step 3 — Read the template

Read `assets/template.html` (relative to this skill directory) once. Keep its exact structure —
CSS, `<head>`, section order, table skeletons (including all pre-shaped 4-company columns/rows),
row labels, and element IDs — as the scaffold for the final artifact. Do **not** copy it to the
workspace and do **not** open it.

---

## Step 4 — Gather all data in parallel

For every company in the set (target + up to 3 peers), fire **all of the following in a single
parallel batch** (one message, many tool calls):

### Credit Opinion data (per company)

Call `getEntityCreditOpinion`,`getEntityFinancials` requesting these sections, about the key Indicators table this should be populated with most recent fiscal year available (e.g. 2025 FY) on `getEntityFinancials`. Not LTM allowed:

| Section parameter | Purpose |
|---|---|
| `Profile` | Company description for the Peers Table |
| `FactorsLeadingToUpgrade` | Upgrade factors for Credit Drivers |
| `FactorsLeadingToDowngrade` | Downgrade factors for Credit Drivers |
| `CreditStrengths` | Credit strengths for Credit Drivers |
| `CreditChallenges` | Credit challenges for Credit Drivers |
| `KeyIndicatorsTable` | Financial metrics for Key Indicators table |
| `ScorecardTable` | Scorecard data |

### Ratings (per company)

Call `getEntityRatings` — retrieve the current long-term rating, rating class, rating date,
outlook, and historical ratings (need at least the last 5 rating actions for the Ratings Chart).

### ESG (per company)

Call `getEntityEsg` — overall CIS classification plus E, S, G sub-scores.

### Sector outlook (once per sector)

Call `getEntitySectorOutlook` for the target company's sector. Reuse for peers in the same
sector.

Hold all results in context for Step 5 synthesis.

---

## Step 5 — Synthesize + emit the complete artifact

After data is gathered, produce **one** final assistant message. The message contains:

1. A one-line summary sentence (e.g. `Peer Analysis for {Target Company}:`).
2. A single fenced ` ```html ` code block containing the **entire filled `template.html`
   document** — with every element from the streaming protocol populated in place. No partial
   documents, no separate code blocks per section.

The code block **must**:

- Start at column 0 with ` ```html ` and end with a closing ` ``` ` on its own line.
- Contain a complete, standalone HTML document (doctype → `</html>`) that renders without
  external dependencies.
- Preserve the template's `<head>` (CSS, fonts), section order, table skeletons, row labels, and
  element IDs exactly. Only the empty targets defined below are populated.

Write in professional financial/credit analysis language. Always reference specific companies by
name. The target company is **always the first column / first row** in every table. Render order
of content inside the code block follows the page top-to-bottom so the artifact is human-readable
as well as browser-renderable: cover/header fields first, then Peers Comparison sub-sections
(1–6), Ratings Chart, ESG, and citations/sources last.

Attribute substantive claims with numbered citation references. The exact inline markup, the
URL-less fallback, and the rule that `n` matches the row position of the source inside
`#pa-sources` are defined in [skills/shared/citations/SKILL.md](../shared/citations/SKILL.md).

### Cover / header fields (write first)

- `#pa-report-date` — e.g. `April 20, 2026` (plain text)
- `#pa-footer-date` — same value (plain text)
- `#pa-target-company` — canonical name of the target (plain text)
- `#pa-peer-count` — integer count of peers resolved in Step 2 (plain text)
- `#pa-company-chips` — `<span class="company-chip target">Target</span>` followed by one
  `<span class="company-chip">Peer</span>` per peer (space-separated; target first)
- `#pa-cover-img-right`, `#pa-cover-img-bottom` — optional. If you have image URLs or data URIs
  to use, set the `src` attributes **and** add the `has-cover-image` class to the corresponding
  container (`<div class="cover-top has-cover-image">` and/or `<div class="cover-bottom has-cover-image">`).
  If you do not have images, leave the template as-is — the empty image strips will collapse
  automatically and the cover will render as a clean navy block with the accent bar.

### Section 1 — Peers Comparison Table & Analysis

**1) Peers Table** → `<tbody id="pa-peers-table">`

Write one `<tr>` per company. Two columns: company name + a substantive description paragraph
sourced from the Credit Opinion `Profile` section (headquarters, business overview, key
brands/segments, approximate TTM revenue). Description paragraphs may carry inline citations.

**2) Peers Rating** → `<tbody id="pa-peers-rating">`

Write one `<tr>` per company. Three columns: company name, rating (formatted as
`{rating} ({rating class} / {date})`), and `<span class="outlook-badge …">Outlook</span>`.
Use class rules below.

**3) Credit Drivers** — 5 rows × 4 company columns, pre-shaped `<table>` with per-cell IDs

Write the 4 company header cells first:
- `#pa-cd-col-1` — target name (plain text)
- `#pa-cd-col-2`, `#pa-cd-col-3`, `#pa-cd-col-4` — peer names in order (leave empty if fewer
  than 3 peers were resolved)

Then write the 20 body cells (`#pa-cd-r{1..5}-c{1..4}`). Each cell is a substantive paragraph
with specific quantitative thresholds where available. Cells may carry inline citations:

- Row 1 (`Upgrade factors`) — from `FactorsLeadingToUpgrade`
- Row 2 (`Downgrade factors`) — from `FactorsLeadingToDowngrade`
- Row 3 (`Credit strengths (qualitative)`) — from `CreditStrengths`
- Row 4 (`Credit challenges (qualitative)`) — from `CreditChallenges`
- Row 5 (`Quantitative support (most recent financials in context)`) — from
  `KeyIndicatorsTable`; cite the most recent period's key metrics (debt/EBITDA, EBITA margin,
  EBITA/interest, RCF/net debt, revenue)

If a Credit Opinion section is missing for a company, write `Not available` in the corresponding
cell rather than leaving it blank.

**4) Key Indicators** — 4 rows × 11 columns, pre-shaped `<table>`

For each company row `r ∈ {1..4}` (target = row 1), write the 11 cells:
- `#pa-ki-r{r}-company` — company name
- `#pa-ki-r{r}-v1` — Period (e.g. `2025 FY`)
- `#pa-ki-r{r}-v2` — Revenue (USD)
- `#pa-ki-r{r}-v3` — Total Debt (USD)
- `#pa-ki-r{r}-v4` — EBITA (USD)
- `#pa-ki-r{r}-v5` — EBITA Margin
- `#pa-ki-r{r}-v6` — EBITDA (USD)
- `#pa-ki-r{r}-v7` — Debt/EBITDA
- `#pa-ki-r{r}-v8` — EBITA/Interest
- `#pa-ki-r{r}-v9` — Net LT Debt (USD)
- `#pa-ki-r{r}-v10` — RCF/Net Debt

Source all values from `getEntityFinancials`. If fewer than 3 peers are
resolved, leave the unused row's cells empty.

**5) Scorecards** — 7 rows × 8 sub-columns (4 companies × Current/Forward), pre-shaped `<table>`

Write the 4 top-level company headers first:
- `#pa-sc-col-1` — target name
- `#pa-sc-col-2`, `#pa-sc-col-3`, `#pa-sc-col-4` — peer names

Write the 8 sub-header labels:
- `#pa-sc-col-{1..4}-curr` — current-period label (e.g. `Current 2025 FY`)
- `#pa-sc-col-{1..4}-fwd` — forward-period label (e.g. `Forward`)

Then write the 56 body cells (`#pa-sc-r{1..7}-c{1..4}-curr` and `-fwd`) for the 7 rows:
- Row 1 — Scale: Revenue/Sales (USD bn)
- Row 2 — Profitability: EBIT(A) margin
- Row 3 — Leverage: Debt/EBITDA
- Row 4 — Cash flow: RCF/Net debt
- Row 5 — Coverage: EBIT(A)/Interest
- Row 6 — Scorecard-indicated outcome
- Row 7 — Actual rating

Source from `ScorecardTable` in the Credit Opinion and `getEntityFinancials`

**6) Conclusion** → `#pa-conclusion`

Three `<p>` paragraphs focused on **differentiation** of the target among its peers. Paragraphs
may carry inline citations:

- Paragraph 1: How the target differentiates positively vs. weaker peers on quantitative metrics
  (leverage, coverage, cash flow). Cite specific ratios.
- Paragraph 2: Business risk profile comparison — where the target is more concentrated or less
  diversified vs. stable peers. Reference upgrade/downgrade triggers.
- Paragraph 3: Practical positioning — frame the target's "path to stand out" by linking back
  to the upgrade/downgrade framework and key risk factors.

### Section 2 — Ratings Chart

**Chart** → `#pa-ratings-chart`

Emit a single inline `<svg>` block authored by the agent (see SVG template below). The chart
plots the last 5 rating actions for each company as a line chart. X-axis uses sequential labels
(`Rating 1` … `Rating 5`, most recent first); Y-axis maps Moody's rating symbols to a numeric
scale.

**Analysis** → `#pa-ratings-analysis`

One `<p>` paragraph on rating trajectories — which companies show improvement, deterioration,
or stability, and what that implies for relative credit positioning. May carry inline citations.

### Section 3 — ESG Table & Analysis

**ESG Table** → `<tbody id="pa-esg-table">`

Write one `<tr>` per company. Five columns: company name, Overall (CIS-*), Environmental (E-*),
Social (S-*), Governance (G-*).

**Analysis** → `#pa-esg-analysis`

Two `<p>` paragraphs. Paragraphs may carry inline citations:

- Paragraph 1: Compare ESG profiles across the peer set. Identify which companies share similar
  profiles and what drives the overall classification.
- Paragraph 2: Highlight the key differentiator (typically Governance) and explain which company
  stands out as weaker/stronger and why.

### Citations & sources (write last)

- `#pa-cite-peers` — optional `<div class="section-citations">…</div>` recap for the
  peers-comparison section. Use the markup defined in
  [skills/shared/citations/SKILL.md](../shared/citations/SKILL.md). Omit if empty.
- `#pa-cite-ratings` — optional recap for the ratings-chart section. Same markup.
- `#pa-cite-esg` — optional recap for the ESG section. Same markup.
- `#pa-sources` — end-of-document Citations rows. One `<div class="source-item">` per source,
  in `[1], [2], …` order, using the canonical row markup from the shared citations skill.
  Internal MCP tool names are NEVER rendered in `.source-meta`.

---

## Streaming protocol (element → content mapping)

| Element ID                                           | Content type                                                           |
|------------------------------------------------------|------------------------------------------------------------------------|
| `#pa-report-date`                                    | Plain text date                                                        |
| `#pa-footer-date`                                    | Plain text date (same value)                                           |
| `#pa-target-company`                                 | Plain text (canonical target name)                                     |
| `#pa-peer-count`                                     | Plain text integer                                                     |
| `#pa-company-chips`                                  | `<span class="company-chip target">` + `<span class="company-chip">`s  |
| `#pa-cover-img-right`, `#pa-cover-img-bottom`        | `<img>` element — set `src` attribute                                  |
| `<tbody id="pa-peers-table">`                        | `<tr>` rows (company name + description) with inline citations         |
| `<tbody id="pa-peers-rating">`                       | `<tr>` rows with `<span class="outlook-badge …">`                      |
| `#pa-cd-col-1` … `#pa-cd-col-4`                      | Plain text (company names)                                             |
| `#pa-cd-r{1..5}-c{1..4}`                             | Prose cell content (short `<p>` or plain text) with inline citations   |
| `#pa-ki-r{1..4}-company`                             | Plain text (company name)                                              |
| `#pa-ki-r{1..4}-v{1..10}`                            | Plain text (period / metric value)                                     |
| `#pa-sc-col-1` … `#pa-sc-col-4`                      | Plain text (company names, span 2 sub-columns)                         |
| `#pa-sc-col-{1..4}-curr`, `#pa-sc-col-{1..4}-fwd`    | Plain text sub-header labels (Current / Forward period)                |
| `#pa-sc-r{1..7}-c{1..4}-curr`, `…-fwd`               | Plain text scorecard cell values                                       |
| `#pa-conclusion`                                     | Three `<p>` paragraphs with inline citations                           |
| `#pa-ratings-chart`                                  | Single `<div class="chart-container">…<svg>…</svg>…</div>` block       |
| `#pa-ratings-analysis`                               | One `<p>` paragraph with inline citations                              |
| `<tbody id="pa-esg-table">`                          | `<tr>` rows (company + overall + E + S + G)                            |
| `#pa-esg-analysis`                                   | Two `<p>` paragraphs with inline citations                             |
| `#pa-cite-peers`, `#pa-cite-ratings`, `#pa-cite-esg` | `<div class="section-citations">…</div>` (optional, see shared citations skill) |
| `#pa-sources`                                        | `<div class="source-item">` rows (see shared citations skill)          |

If fewer than 3 peers are returned, leave unused column/row IDs empty. Do not collapse or remove
cells — the pre-shaped table simply keeps those cells blank.

### Reference HTML snippets

**Peers table row** (`<tbody id="pa-peers-table">`):

```html
<tr>
  <td class="company-name">Target Co</td>
  <td>Headquartered in Dearborn, Michigan, Target Co is a global automaker with TTM revenue of approximately $180B <a href="https://example.com/credit-opinion-target" target="_blank" class="cite-ref">[1]</a>, anchored by its F-Series, SUV, and Pro commercial businesses <a href="https://example.com/profile-target" target="_blank" class="cite-ref">[2]</a>.</td>
</tr>
```

**Peers rating row** (`<tbody id="pa-peers-rating">`):

```html
<tr>
  <td class="company-name">Target Co</td>
  <td>Baa3 (Senior Unsecured - Dom Curr / 2024-05-09)</td>
  <td><span class="outlook-badge stable">Stable</span></td>
</tr>
```

**Company chips** (`#pa-company-chips`):

```html
<span class="company-chip target">Target Co</span>
<span class="company-chip">Peer One</span>
<span class="company-chip">Peer Two</span>
<span class="company-chip">Peer Three</span>
```

**ESG table row** (`<tbody id="pa-esg-table">`):

```html
<tr>
  <td class="company-name">Target Co</td>
  <td>CIS-3</td>
  <td>E-4</td>
  <td>S-3</td>
  <td>G-2</td>
</tr>
```

**Credit Drivers — per-cell write** (repeat for each of the 20 body cells):

```html
Leverage sustained below 2.5x Debt/EBITDA, EBITA margin above 7%, and sustained positive free cash flow after dividends <a href="https://example.com/credit-opinion-target" target="_blank" class="cite-ref">[1]</a>.
```

**Conclusion paragraph** (inside `#pa-conclusion`, same inline-citation pattern applies to
`#pa-ratings-analysis` and `#pa-esg-analysis`):

```html
<p>On pure quantitative credit metrics, Target Co stands out decisively: Debt/EBITDA of 0.7x and EBITA/Interest of 27x are in line with the strongest-scoring peers, while its scale advantage (LTM revenue of $294B vs. $61B and $23B for the peer set) and FCF/Debt of 41% add a differentiation layer the others cannot match <a href="https://example.com/credit-opinion-target" target="_blank" class="cite-ref">[1]</a><a href="https://example.com/peer-ratings" target="_blank" class="cite-ref">[2]</a>.</p>
```

**Key Indicators — single row** (emit the full `<tr>` for each company inside the
`#pa-key-indicators` table, keeping the per-cell `id` attributes intact):

```html
<tr>
  <td id="pa-ki-r1-company">Target Co</td>
  <td id="pa-ki-r1-v1">LTM (30 Sep 2025)</td>
  <td id="pa-ki-r1-v2">180.2B</td>
  <td id="pa-ki-r1-v3">155.6B</td>
  <td id="pa-ki-r1-v4">7.8B</td>
  <td id="pa-ki-r1-v5">4.33%</td>
  <td id="pa-ki-r1-v6">13.1B</td>
  <td id="pa-ki-r1-v7">11.88x</td>
  <td id="pa-ki-r1-v8">3.62x</td>
  <td id="pa-ki-r1-v9">136.0B</td>
  <td id="pa-ki-r1-v10">18.5%</td>
</tr>
```

**Scorecard — per-cell write** (Current or Forward):

```html
2.7x
```

**Section citations recap** (`#pa-cite-peers`, `#pa-cite-ratings`, `#pa-cite-esg`) and
**sources rows** (`#pa-sources`): see
[skills/shared/citations/SKILL.md](../shared/citations/SKILL.md) for the canonical markup.
Reuse the same `[n]` numbering across inline references, optional recap blocks, and the
end-of-document Citations block. Never include MCP tool names in `.source-meta`.

---

## Ratings Chart SVG template

Emit the entire chart as a single HTML string into `#pa-ratings-chart`. The agent authors the
SVG directly — there is no runtime script.

### Hardcoded constants

- Dimensions: `W = 700`, `H = 350`
- Padding: `PAD_L = 70`, `PAD_R = 30`, `PAD_T = 30`, `PAD_B = 50`
- Plot area: width `= W - PAD_L - PAD_R = 600`, height `= H - PAD_T - PAD_B = 270`
- Number of x-axis points: `maxPts` = the largest number of ratings any company has, capped at 5
- Palette (first = target): `#0066cc`, `#e6550d`, `#1a7a4a`, `#8b5cf6`, `#d63384`

### Moody's rating → numeric value map

| Rating | Value | Rating | Value |
|--------|-------|--------|-------|
| Aaa | 21 | Ba1 | 11 |
| Aa1 | 20 | Ba2 | 10 |
| Aa2 | 19 | Ba3 | 9 |
| Aa3 | 18 | B1 | 8 |
| A1 | 17 | B2 | 7 |
| A2 | 16 | B3 | 6 |
| A3 | 15 | Caa1 | 5 |
| Baa1 | 14 | Caa2 | 4 |
| Baa2 | 13 | Caa3 | 3 |
| Baa3 | 12 | Ca | 2 |
|     |    | C | 1 |

`RATING_LABELS` (index 0..20 → symbol): `["C", "Ca", "Caa3", "Caa2", "Caa1", "B3", "B2", "B1", "Ba3", "Ba2", "Ba1", "Baa3", "Baa2", "Baa1", "A3", "A2", "A1", "Aa3", "Aa2", "Aa1", "Aaa"]`.

### Coordinate formulae

Compute once per chart:

- Collect every rating value across all companies' last-5 series → `values[]`.
- `minV = clamp(min(values) - 1, 1, 21)`
- `maxV = clamp(max(values) + 1, 1, 21)` (ensure `maxV > minV`; if equal, set `maxV = minV + 1`)

Per point `(i, v)` where `i` is the x-index (0-based) and `v` is the rating value:

- `xPos(i) = PAD_L + (i / (maxPts - 1)) * 600` = `70 + (i / (maxPts - 1)) * 600`
- `yPos(v) = PAD_T + 270 - ((v - minV) / (maxV - minV)) * 270` = `30 + 270 - ((v - minV) / (maxV - minV)) * 270`

### Reference SVG block

```html
<div class="chart-container">
  <div class="chart-title">Last 5 Ratings for Target and Peers</div>
  <svg viewBox="0 0 700 350" width="100%" preserveAspectRatio="xMidYMid meet">
    <!-- Horizontal gridlines + y-axis rating labels (one line + label per rating tick from minV to maxV) -->
    <line x1="70" y1="30"  x2="670" y2="30"  stroke="#e5e7eb" stroke-width="1"/>
    <text x="64" y="34" text-anchor="end" font-size="10" fill="#475569">Baa1</text>
    <line x1="70" y1="84"  x2="670" y2="84"  stroke="#e5e7eb" stroke-width="1"/>
    <text x="64" y="88" text-anchor="end" font-size="10" fill="#475569">Baa2</text>
    <line x1="70" y1="138" x2="670" y2="138" stroke="#e5e7eb" stroke-width="1"/>
    <text x="64" y="142" text-anchor="end" font-size="10" fill="#475569">Baa3</text>
    <line x1="70" y1="192" x2="670" y2="192" stroke="#e5e7eb" stroke-width="1"/>
    <text x="64" y="196" text-anchor="end" font-size="10" fill="#475569">Ba1</text>
    <line x1="70" y1="246" x2="670" y2="246" stroke="#e5e7eb" stroke-width="1"/>
    <text x="64" y="250" text-anchor="end" font-size="10" fill="#475569">Ba2</text>
    <line x1="70" y1="300" x2="670" y2="300" stroke="#e5e7eb" stroke-width="1"/>
    <text x="64" y="304" text-anchor="end" font-size="10" fill="#475569">Ba3</text>

    <!-- X-axis baseline + tick labels -->
    <line x1="70" y1="300" x2="670" y2="300" stroke="#334155" stroke-width="1.5"/>
    <text x="70"  y="320" text-anchor="middle" font-size="10" fill="#475569">Rating 1</text>
    <text x="220" y="320" text-anchor="middle" font-size="10" fill="#475569">Rating 2</text>
    <text x="370" y="320" text-anchor="middle" font-size="10" fill="#475569">Rating 3</text>
    <text x="520" y="320" text-anchor="middle" font-size="10" fill="#475569">Rating 4</text>
    <text x="670" y="320" text-anchor="middle" font-size="10" fill="#475569">Rating 5</text>

    <!-- Target company line (palette[0] = #0066cc) -->
    <path d="M70,138 L220,138 L370,192 L520,192 L670,192"
          fill="none" stroke="#0066cc" stroke-width="2.5"/>
    <circle cx="70"  cy="138" r="4" fill="#0066cc"/>
    <circle cx="220" cy="138" r="4" fill="#0066cc"/>
    <circle cx="370" cy="192" r="4" fill="#0066cc"/>
    <circle cx="520" cy="192" r="4" fill="#0066cc"/>
    <circle cx="670" cy="192" r="4" fill="#0066cc"/>

    <!-- Repeat <path>+<circle>s for peers 2, 3, 4 using palette[1..3] -->
  </svg>
  <div class="chart-legend">
    <div class="chart-legend-item"><span class="chart-legend-swatch" style="background:#0066cc"></span>Target Co</div>
    <div class="chart-legend-item"><span class="chart-legend-swatch" style="background:#e6550d"></span>Peer One</div>
    <div class="chart-legend-item"><span class="chart-legend-swatch" style="background:#1a7a4a"></span>Peer Two</div>
    <div class="chart-legend-item"><span class="chart-legend-swatch" style="background:#8b5cf6"></span>Peer Three</div>
  </div>
</div>
```

### Class-selection rules

**`.outlook-badge`** modifier (inside peers-rating rows):

- `stable` — outlook is "Stable"
- `positive` — outlook is "Positive"
- `negative` — outlook is "Negative"
- `review` — outlook contains "Review" (e.g., "Rating Under Review")
- `na` — outlook is missing or unknown

**`.company-chip.target`** applies only to the target (first) chip. Remaining chips use plain
`.company-chip`.

### Conventions

- Use `<p>` for paragraphs, `<ul><li>` for bullets, `<strong class="subsection-title">…</strong>`
  for bold subheaders inside prose containers.
- Emit inline citations per [skills/shared/citations/SKILL.md](../shared/citations/SKILL.md).
  Inline citations are the primary attribution mechanism — the optional per-section blocks
  (`#pa-cite-peers`, `#pa-cite-ratings`, `#pa-cite-esg`) remain available as supplementary
  summary boxes.
- Do NOT include overall section titles — the template already has those.
- `rating` values: use Moody's rating symbol (e.g. `Aaa`, `Aa1`, `Baa2`, `Ba1`). If not found,
  use `N/A`.
- `outlook` values: `Stable`, `Positive`, `Negative`, `Rating Under Review`, or `N/A`.

---

## Step 6 — Tell the user

After the ` ```html ` code block, add a single short sentence confirming the artifact is
complete (e.g. `Artifact rendered above — the report is fully self-contained HTML.`). Do not
write the artifact to disk and do not suggest shell commands. The code block itself is the
deliverable.

---

## Tips

- Run ALL data-gathering tool calls in a single parallel batch (one message, many tool calls).
- Emit the final HTML as one `html` fenced code block — do not stream partial sections, do not
  split across multiple messages, do not write to disk.
- The target company always appears as the first column / first row in every table and
  comparison.
- The conclusion must orient around the target company — how it differentiates from its peers.
- If fewer than 3 peers are returned, leave the unused column/row IDs empty. The pre-shaped
  tables keep those cells blank — do not attempt to collapse or restructure the table.
- If `getEntityCreditOpinion` does not return a particular section, write `Not available` in the
  corresponding cell rather than leaving it blank.
- `getEntitySectorOutlook` typically applies to all companies in the same sector — call once
  and reuse.
- Emit the ratings-chart SVG directly into `#pa-ratings-chart` — the template no longer builds
  the chart at render time. Pick the `.outlook-badge` class yourself using the rules above.
- For companies with fewer than 5 historical ratings, either repeat the oldest available rating
  value to fill the trailing points, or reduce `maxPts` in the chart formula to the largest
  available count (and drop the corresponding `Rating k` x-axis labels).
- Inline citations follow the shared citations skill — read
  [skills/shared/citations/SKILL.md](../shared/citations/SKILL.md) before authoring any `[n]`
  reference or the Citations block.

---

## Step 7 — Save and deliver the report as a downloadable file

After assembling the complete HTML string (same content that would have been emitted as the
fenced code block), **write it to disk as a standalone `.html` file** and make it available for
the user to download. Do **not** print the raw HTML in the chat.

### File naming

Use the pattern: `{target_company_slug}_peer_analysis.html`

Where `{target_company_slug}` is the target company's canonical name lowercased, spaces and
special characters replaced with underscores (e.g. `apple_inc_peer_analysis.html`).


### Delivery

After writing the file, use whatever file-presentation capability is available in the current
environment to surface the file to the user so they can open or download it. Do not describe
the tool being used — just invoke it. Then add one short confirmation sentence, for example:
`The peer analysis report for [Target Company] is ready to download above.`

Do **not** print the HTML source in the chat. Do **not** emit a fenced ` ```html ` code block.
The saved file is the sole deliverable.

---

## Amendment: Always use the most recent fiscal year for Key Indicators and Scorecards

When populating the Key Indicators table (`#pa-ki-r{1..4}-*`) and the Scorecard table
(`#pa-sc-r{1..7}-c{1..4}-curr`), always use the **most recent fiscal year-end (FY) data
available** from `getEntityFinancials` — never default to an earlier year simply because
the credit opinion's Key Indicators table cites it, or because one peer's most recent year
differs from another's.

### Procedure

1. After calling `getEntityFinancials` with `excludeInterimData: true`, inspect the
   returned columns for each entity and identify the **latest year with a non-null Revenue
   value** — that is the most recent fiscal year end for that entity.
2. Use that year's figures for the Key Indicators table and the "Current" column of the
   Scorecard, regardless of what year the credit opinion's exhibit uses.
3. If different entities have different most-recent years (e.g. one entity has 2025 data
   while another only has 2024), use each entity's own most recent year independently and
   label the `#pa-ki-r{n}-v1` cell accordingly (e.g. `2025 FY` vs `2024 FY`).

### Handling distorted EBITDA years

If the most recent fiscal year contains a non-cash charge (e.g. goodwill impairment) that
makes reported EBITDA or Debt/EBITDA not meaningful on a reported basis:
- Still use that year as the period reference.
- Populate EBITDA and ratio cells with the reported figure plus a `†` marker (e.g.
  `-$1.6B†`, `N/M†`).
- Add a footnote below the Key Indicators table explaining the distortion and citing the
  Moody's-adjusted figure where available from the credit opinion.
- Use the Moody's-adjusted ratio (from the credit opinion's Key Indicators table) for the
  Scorecard leverage cell rather than the distorted reported figure.

---

## Amendment: Visual Enhancements

Three additional visual components are added to the report. Emit them inline as part of the
single HTML artifact (same non-negotiable output contract applies). All new elements use only
the CSS classes already defined in `assets/template.html` — no external scripts or libraries.

---

### Visual 1 — Rating Summary Cards (`#pa-rating-cards`)

Placed **immediately after** the Peers Rating table (sub-heading 2), before sub-heading 3
(Credit Drivers). Emit one `.rating-card` per company (target first, then peers in order).
The target card carries the extra class `target-card`.

**What to populate:**
- `.rc-company` — abbreviated company name (≤ 25 chars; truncate with "…" if longer)
- `.rc-rating` — Moody's rating symbol (e.g. `Baa2`)
- `.rc-class` — rating class + date (e.g. `Senior Unsecured / 2024-05-09`)
- `.outlook-badge` — outlook badge using the canonical pastel classes (`stable`, `positive`,
  `negative`, `review`, `na`)

**Reference snippet** (emit one block like this per company inside `#pa-rating-cards`):

```html
<div class="rating-card target-card">
  <div class="rc-company">Target Co</div>
  <div class="rc-rating">Baa2</div>
  <div class="rc-class">Senior Unsecured / 2024-05-09</div>
  <span class="outlook-badge stable">Stable</span>
</div>
```

---

### Visual 2 — Financial Comparison Bar Charts (`#pa-fi-charts`)

Placed **immediately after** the Key Indicators table (sub-heading 4), before sub-heading 5
(Scorecards). Emit a two-column grid (`div.fi-chart-grid`) containing exactly **two**
`div.fi-chart-box` blocks:

1. **Revenue** — horizontal bar chart comparing Revenue (USD) for all companies
2. **Debt/EBITDA** — horizontal bar chart comparing Debt/EBITDA ratio for all companies

For each chart, the widths are proportional: the company with the largest value gets a
`fi-bar-fill` width of `100%`; all others are scaled relative to that maximum.

**Colour palette** (same as the ratings chart): target = `#0066cc`, peer 1 = `#e6550d`,
peer 2 = `#1a7a4a`, peer 3 = `#8b5cf6`. Assign colours in the same company order as all
other tables (target first).

**Values:** source from `getEntityFinancials` (same figures used in Key Indicators).
Format Revenue as `$XB` or `$XM`; Debt/EBITDA as `X.Xx`.

If a value is missing or `N/A`, set `fi-bar-fill` width to `0%` and display `N/A` in
`.fi-bar-value`.

**Reference snippet** for one chart box (repeat once for Revenue, once for Debt/EBITDA):

```html
<div class="fi-chart-box">
  <div class="fi-chart-title">Revenue (USD)</div>
  <div class="fi-bar-row">
    <span class="fi-bar-label">Target Co</span>
    <div class="fi-bar-track"><div class="fi-bar-fill" style="width:100%;background:#0066cc;"></div></div>
    <span class="fi-bar-value">$180B</span>
  </div>
  <div class="fi-bar-row">
    <span class="fi-bar-label">Peer One</span>
    <div class="fi-bar-track"><div class="fi-bar-fill" style="width:34%;background:#e6550d;"></div></div>
    <span class="fi-bar-value">$61B</span>
  </div>
  <div class="fi-bar-row">
    <span class="fi-bar-label">Peer Two</span>
    <div class="fi-bar-track"><div class="fi-bar-fill" style="width:13%;background:#1a7a4a;"></div></div>
    <span class="fi-bar-value">$23B</span>
  </div>
  <div class="fi-bar-row">
    <span class="fi-bar-label">Peer Three</span>
    <div class="fi-bar-track"><div class="fi-bar-fill" style="width:20%;background:#8b5cf6;"></div></div>
    <span class="fi-bar-value">$36B</span>
  </div>
</div>
```

Omit bar rows for companies that were not resolved (fewer than 3 peers).

---

### Visual 3 — ESG Score Heatmap (`#pa-esg-heatmap`)

Placed **immediately after** the ESG table, before `#pa-esg-analysis`. Emit a colour-coded
HTML table (inside `div.esg-heatmap`) that makes the CIS and sub-scores scannable at a glance.

**Colour mapping** — apply a CSS class to each score `<td>` based on numeric severity
(lower CIS/sub-score = better):

| Score | Class | Meaning |
|-------|-------|---------|
| 1 | `esg-s1` | Green — minimal risk |
| 2 | `esg-s2` | Light green — limited risk |
| 3 | `esg-s3` | Amber — moderate risk |
| 4 | `esg-s4` | Orange — high risk |
| 5 | `esg-s5` | Red — very high risk |

Parse the numeric suffix from the Moody's score string (e.g. `CIS-3` → 3, `E-4` → 4).
If the score is `N/A` or missing, omit the colour class (plain white cell).

**Reference snippet:**

```html
<table>
  <thead>
    <tr>
      <th>Company</th>
      <th>CIS (Overall)</th>
      <th>E Score</th>
      <th>S Score</th>
      <th>G Score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Target Co</td>
      <td class="esg-s3">CIS-3</td>
      <td class="esg-s4">E-4</td>
      <td class="esg-s3">S-3</td>
      <td class="esg-s2">G-2</td>
    </tr>
    <!-- one <tr> per company, same order as all other tables -->
  </tbody>
</table>
```

---

### Updated element ID mapping (addendum)

| Element ID / selector          | Content                                                                 |
|-------------------------------|-------------------------------------------------------------------------|
| `#pa-rating-cards`            | `.rating-card` divs — one per company (target first)                   |
| `#pa-fi-charts`               | Two `.fi-chart-box` divs inside `.fi-chart-grid` (Revenue, Debt/EBITDA)|
| `#pa-esg-heatmap`             | `.esg-heatmap` table with colour-coded CIS / E / S / G scores          |

---

## Amendment: Section Layout, Ratings Chart, and ESG Display Overrides

### Section 1 — Revised sub-section order

Emit sub-sections in this exact order:

1. **Peers Table** (`<tbody id="pa-peers-table">`) — unchanged, as defined above.
2. **Rating Cards only** (`#pa-rating-cards`) — emit the `.rating-card` blocks as defined in
   Visual 1. **Do NOT emit the `<tbody id="pa-peers-rating">` table at all.** The cards are the
   sole representation of peer ratings in Section 1.
3. **Credit Drivers table** — unchanged, as defined above.
4. **Key Indicators table** + **Financial Comparison Bar Charts** (`#pa-fi-charts`) — unchanged,
   both emitted as defined above (table first, then the two bar-chart boxes).
5. **Scorecard table** — unchanged, as defined above.
6. **Conclusion** (`#pa-conclusion`) — unchanged.

The `<table>` element whose `<tbody>` carries `id="pa-peers-rating"` must be **omitted entirely**
from the emitted HTML. Do not render it, do not hide it with CSS, do not leave an empty wrapper.

---

### Section 2 — Enhanced Ratings Chart

Replace the plain SVG line chart described earlier with the enhanced version below. The output
must still be emitted inline inside `#pa-ratings-chart`.

**Design goals:** visually polished, readable at a glance, clearly differentiates companies with
colour and shape, highlights the most-recent rating prominently.

**Layout — SVG viewBox `"0 0 780 400"`:**

- Left padding (y-axis labels): 80 px
- Right padding: 30 px
- Top padding: 40 px
- Bottom padding (x-axis labels + legend): 60 px
- Plot area: 670 × 300 px (x: 80→750, y: 40→340)

**Y-axis:** draw one horizontal gridline + label per rating tier present in the data set (use the
`minV`→`maxV` range from the coordinate formulae above, but now label with the Moody's symbol,
not a number). Gridlines are `stroke="#e5e7eb"`. Labels are `font-size="11"`, `fill="#64748b"`,
`text-anchor="end"` at `x="74"`.

**X-axis:** draw the baseline (`stroke="#334155"`, `stroke-width="1.5"`). Label each point with
the **actual rating date** (formatted `MMM YYYY`, e.g. `Jan 2023`) instead of `Rating N`.
Labels `font-size="10"`, `fill="#64748b"`, `text-anchor="middle"`, `y="358"`.

**Lines:** `stroke-width="2.5"`, rounded joins (`stroke-linejoin="round"`, `stroke-linecap="round"`).

**Data points:** each rating action is a `<circle r="5">` filled with the company colour. The
**most-recent point** (rightmost) for each company is instead a `<circle r="7">` with a white
inner ring — achieved by stacking a white `<circle r="4" fill="white"/>` on top of the coloured
outer circle. Add a `<title>` element inside each point group for tooltip text:
`{company} · {rating symbol} · {date}`.

**Value labels:** above each data point, emit a `<text>` showing the Moody's rating symbol
(`font-size="9"`, `fill` = company colour, `text-anchor="middle"`, `dy="-10"`). Suppress the
label if it would overlap a neighbour (points within 40 px horizontally from the same series can
share a label only at the leftmost occurrence; skip the rest in that cluster).

**Colour palette:** same as all other charts — target `#0066cc`, peer 1 `#e6550d`,
peer 2 `#1a7a4a`, peer 3 `#8b5cf6`.

**Legend:** emit below the SVG as a `<div class="chart-legend">` row (same pattern as before),
but add the actual current rating symbol in parentheses after each company name, e.g.
`Target Co (Baa2)`.

**Reference snippet** (abbreviated — fill in real coordinates from the formulae):

```html
<div class="chart-container">
  <div class="chart-title">Rating History — Last 5 Actions</div>
  <svg viewBox="0 0 780 400" width="100%" preserveAspectRatio="xMidYMid meet">

    <!-- Gridlines + Y-axis labels -->
    <line x1="80" y1="40"  x2="750" y2="40"  stroke="#e5e7eb" stroke-width="1"/>
    <text x="74" y="44"  text-anchor="end" font-size="11" fill="#64748b">Baa1</text>
    <!-- … one per tier … -->

    <!-- X-axis baseline -->
    <line x1="80" y1="340" x2="750" y2="340" stroke="#334155" stroke-width="1.5"/>
    <!-- X-axis date labels -->
    <text x="80"  y="358" text-anchor="middle" font-size="10" fill="#64748b">Jan 2021</text>
    <!-- … -->

    <!-- Target company — line -->
    <path d="M80,192 L247,192 L415,138 L582,138 L750,138"
          fill="none" stroke="#0066cc" stroke-width="2.5"
          stroke-linejoin="round" stroke-linecap="round"/>
    <!-- Rating labels above points -->
    <text x="80"  y="182" text-anchor="middle" font-size="9" fill="#0066cc">Baa2</text>
    <!-- Regular points -->
    <circle cx="80"  cy="192" r="5" fill="#0066cc"/>
    <circle cx="247" cy="192" r="5" fill="#0066cc"/>
    <circle cx="415" cy="138" r="5" fill="#0066cc"/>
    <circle cx="582" cy="138" r="5" fill="#0066cc"/>
    <!-- Most-recent point (highlighted) -->
    <circle cx="750" cy="138" r="7" fill="#0066cc"/>
    <circle cx="750" cy="138" r="4" fill="white"/>
    <title>Target Co · Baa1 · Mar 2025</title>

    <!-- Repeat for each peer with palette[1..3] -->
  </svg>
  <div class="chart-legend">
    <div class="chart-legend-item">
      <span class="chart-legend-swatch" style="background:#0066cc"></span>Target Co (Baa1)
    </div>
    <div class="chart-legend-item">
      <span class="chart-legend-swatch" style="background:#e6550d"></span>Peer One (Ba1)
    </div>
    <!-- … -->
  </div>
</div>
```

---

### Section 3 — ESG: Heatmap Only

**Do NOT emit the plain `<table>` whose `<tbody>` carries `id="pa-esg-table"`**. Remove it
entirely from the output HTML — do not render it, do not hide it.

Instead, emit **only** the colour-coded heatmap table (`#pa-esg-heatmap`, as defined in
Visual 3 above) as the sole ESG data table. Follow it immediately with `#pa-esg-analysis`.

The heatmap already contains all the same data (company, CIS, E, S, G scores) in a more
readable, colour-coded format; the plain table is redundant and must be omitted.

**Revised Section 3 emit order:**

1. `#pa-esg-heatmap` (colour-coded heatmap table — the only ESG table)
2. `#pa-esg-analysis` (two analysis paragraphs, unchanged)
3. Optional `#pa-cite-esg` recap block (if citations are present)

---

### Summary of omissions (do NOT emit these elements)

| Element | Reason |
|---|---|
| `<table>` wrapping `<tbody id="pa-peers-rating">` | Replaced by rating cards |
| `<table>` wrapping `<tbody id="pa-esg-table">` | Replaced by ESG heatmap |
