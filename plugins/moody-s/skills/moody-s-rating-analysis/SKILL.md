---
name: moody-s-rating-analysis
description: >
  Produce a Rating Pitch Report for a company using Moody's GenAI MCP tools, delivered as a
  self-contained HTML file saved to disk. Use this skill whenever the user asks to create
  a rating pitch, rating pitch deck, credit pitch, rating presentation, rating pitch
  report, or rating HTML report. Also trigger when they ask for a comprehensive credit
  overview combining sector analysis, company financials, SWOT, peer comparison, and ESG
  into a single report or presentation. Trigger even if they just name a company and say
  "pitch deck", "rating deck", "credit deck", or "rating report".
---

# Rating Pitch Skill

Generates a Moody's Rating Pitch Report as a self-contained HTML file from a single MCP
data pass. The Python builder (`scripts/build_html.py`) takes the resolved payload JSON and
produces a single `.html` file containing all sections with inline Chart.js charts, styled
tables, and bullet lists using the Moody's brand palette — no external dependencies beyond
a browser to open it.

> ## ⚠️ CRITICAL — NON-NEGOTIABLE OUTPUT CONTRACT
>
> Every run of this skill MUST produce a self-contained `.html` report. Specifically:
>
> - The skill **MUST** save the resolved `payload.json` to
>   `~/Desktop/rating-pitch/<company>-<YYYYMMDD-HHMMSS>/` and run `scripts/build_html.py`
>   against it to produce the `rating_pitch.html` alongside it.
> - The LLM **MUST NOT** stream the report content as inline Markdown, JSON dumps, or
>   any other in-chat artifact in lieu of building the `.html` file. The `.html` file itself
>   is the deliverable.
> - The final assistant message **MUST** point the user at the full path to the generated
>   `rating_pitch.html` so they can open it in their browser.
> - If data gathering fails partially, still build the `.html` from the partial payload
>   using `"--"` placeholders for missing values — never skip the build.
>
> Treat any other output shape as a hard failure of the skill.

## Required MCP server

`Moodys MCP server` — tools used: `findEntity`, `getEntityPeers`, `getEntityRatings`,
`getEntityCreditOpinion` (sections: Profile, Summary, RatingOutlook,
FactorsLeadingToUpgrade, FactorsLeadingToDowngrade, CreditStrengths, CreditChallenges,
ESGConsiderations, KeyIndicatorsTable, ScorecardTable), `getEntityFinancials`,
`getEntityEsg`, `getEntitySectorOutlook`, `searchEntityEarningsCall`,
`searchEntityDocuments`, `searchNews`

Web research is also required via searchNews or general web search tools.

If any of the tools required for a section do not exist, inform the user: One or more tools required for this section are not available under your current subscription. Unlock more of the expert insights, data, and analytics you trust. Get Link:https://www.moodys.com/web/en/us/capabilities/gen-ai/ai-ready-data.html with us to learn more.


## Bundled files

- `scripts/build_html.py` — the report builder. Takes a JSON payload and emits a `.html`.
  Uses only the Python standard library; no pip installs required.
- `scripts/requirements.txt` — no additional Python dependencies needed.
- `assets/sample_payload.json` — reference payload showing every field populated. Read this
  if you're ever unsure what a field should look like.

## Parameters the user should provide

- **Company Name** (required)
- **Sector** (required — e.g., "Aerospace/Defense", "Consumer Products"). Infer it from
  the company if the user doesn't say.
- **Number of peers** (optional, default 6)
- **Currency** (optional, default USD)

---

## Step 1 — Resolve the target company

Call `findEntity` with the company name. Store the canonical entity name and ID.

## Step 2 — Gather ALL data in parallel

Fire the following in a **single parallel batch**. Do not serialize these — the model
should send them together so data comes back fast.

### Target company data

| Tool | Purpose |
|------|---------|
| `getEntityCreditOpinion` (sections: Profile, Summary, RatingOutlook, FactorsLeadingToUpgrade, FactorsLeadingToDowngrade, CreditStrengths, CreditChallenges, ESGConsiderations, KeyIndicatorsTable, ScorecardTable) | Credit opinion sections for financial analysis, SWOT, scorecard |
| `getEntityRatings` | Current rating + last 5 rating actions for history chart |
| `getEntityEsg` | ESG scores |
| `getEntitySectorOutlook` | Sector overview and outlook |
| `getEntityPeers` (N peers) | Peer set |
| `searchEntityEarningsCall` (keywords: outlook, guidance, forecast, strategy) | Strategic updates / forward-looking |
| `searchEntityDocuments` (annual/quarterly reports) | Revenue segments, geography |
| `searchNews` | M&A, leadership, external trends |

### Peer data (for each peer)

| Tool | Purpose |
|------|---------|
| `findEntity` | Resolve canonical name |
| `getEntityRatings` | Peer rating + outlook |
| `getEntityCreditOpinion` (sections: Profile, KeyIndicatorsTable, ScorecardTable) | Financials + scorecard |
| `getEntityFinancials` (prompt: `"annual revenue, EBITDA, EBIT margin, debt/EBITDA, RCF/net debt, most recent year-end only"`, filterCriteria: `{excludeInterimData: true}`) | Most recent full-year financials for peer charts |
| `getEntityEsg` | Peer ESG scores |

**Period-selection rule (applies to target company and every peer):**
When `getEntityFinancials` returns multiple annual periods, always use the
**most recent year-end period available** — i.e. the column with the highest
calendar or fiscal year. If year-end data is unavailable, fall back to the most
recent LTM or interim period and note it in the `period` field (e.g. `"LTM Mar 2025"`).
Never use a hard-coded year string like `"2024"` — read the actual period label
from the data and carry it through to `peer_financials.rows[].period` and
`peer_profitability_charts` / `peer_debt_charts` entries.

---

## Step 3 — Synthesize the sections

Build a single in-memory **resolved payload** that matches the JSON shape in the **Payload
schema** section below (a reference copy lives at `assets/sample_payload.json`). This
payload drives the .html build (Step 4) — fill it completely before moving on.

Content rules for each section:

> **`commentary` type rule — applies to every section without exception:**
> All `commentary` fields in the payload MUST be a **JSON array of strings** — never a
> bare string. A bare string passed to the .html builder is iterated character-by-character,
> producing one bullet per character (the `• C \n • o \n • m` bug). Always write:
> `"commentary": ["Sentence one.", "Sentence two."]` — even for a single sentence.

### Part 1 — Sector Analysis

- **sector_overview** — three 3-bullet lists (overview / watchlist / takeaways). Keep
  bullets punchy, ≤25 words each.
- **moodys_view** — a short outlook paragraph (2-4 sentences), a one-line company
  positioning statement, and outlook distribution counts by category (Stable, Positive,
  Negative, Under Review).
- **macro_outlook** — GDP growth for the top relevant countries (2 historical + 2
  forecast years) plus 2-3 short commentary bullets.
- **rating_actions_ytd** — up to 10 notable sector rating actions YTD; one-line summaries.

### Part 2 — Company Credit Overview

- **financial_analysis** — 5-6 commentary bullets (revenue, margin, leverage, cash flow,
  liquidity, rating rationale). Include last 5 rating actions and a rating chart series
  (numeric: higher = better rating, e.g., Aaa=21, Baa3=10, Caa1=4).
  **`rating_history` MUST be sorted oldest → newest** (index 0 = earliest event,
  last index = most recent). `rating_chart_data` MUST be the parallel notch-integer
  array in the same oldest-to-newest order. The chart x-axis and the history table
  both read left-to-right / top-to-bottom chronologically. `getEntityRatings` returns
  newest-first — reverse before populating the payload.
- **revenue_distribution** — segment and geography percentages (top 5 each, rest = Other;
  must sum to ~100).
- **swot** — 3 items per quadrant, 15-25 words each.
- **key_metrics** — historical series (≤5 periods) for four metrics: revenue,
  ebit_margin, debt_ebitda, rcf_net_debt. Arrays must match the `periods` array length.
  Use `null` (not omission) for missing points.
- **strategic_updates** — `recent` (3-5) and `forward` (3-5, strictly future-looking).
- **news_mna** / **external_trends** — structured list form:
  `[{"category": "...", "items": ["...", "..."]}]`. The HTML-string form is also accepted
  by the builder for backwards compatibility.

### Part 3 — Company Positioning vs. Peers

- **peer_summary** — row per company (target first), plus 2-3 commentary bullets.
- **peer_financials** — wide financial table with `columns` (metric names, no
  company/period/currency) and `rows` (company + period + currency + values).
  Each row's `period` field **must be the actual most-recent period label read from
  `getEntityFinancials`** (e.g. `"FY2025"`, `"FY2024"`, `"LTM Mar 2025"`). Never
  default all rows to the same hard-coded year. Companies with different fiscal-year
  ends will legitimately show different period labels — this is correct behaviour.
- **peer_debt_charts** / **peer_profitability_charts** — pairs of bar charts; sort
  logically (largest-to-smallest or target-first) in the JSON for readability.
  Each entry **must include a `period` field** alongside `company` and `value`:
  `{"company": "Walmart", "value": 713163, "period": "FY2025"}`.
  The `period` is used as a sub-label on the bar. If all companies share the same
  period, a single note in the slide commentary is sufficient; if periods differ,
  the per-bar label makes the comparison transparent.
- **peer_scatter** — two scatter series (`margin_vs_leverage`, `fcf_vs_rcf`), each a list
  of `{company, x, y}` points. Drop extreme outliers that would distort the axes.
  > **Scatter chart rendering notes:**
  > - Each company is rendered as a **separate series** so it gets its own distinct brand colour
  >   (Blue → company 0, Pink → 1, Teal → 2, Gold → 3, Mid Blue → 4, Purple → 5).
  > - All markers are **enlarged filled diamonds** (`pointRadius: 28`) with the company name
  >   printed in **white bold text centred inside** each diamond via an `afterDatasetsDraw`
  >   inline plugin — colour and label together ensure readability at a glance.
  > - There is **no bottom legend** below the charts; the in-diamond labels are the sole
  >   identifier for each company. Do not add a separate legend.
- **scorecard** — `factors` (row labels, including group headers), `is_header` boolean
  flags per row, `companies` (column headers), and `values` as a 3D array: outer = rows,
  middle = columns, inner = `[measure, score]` or `[]` for header rows.
  > **SCORECARD CONTRACT — READ CAREFULLY:**
  > - `companies` must list **the target company first, followed by peer entities** (e.g.
  >   `["Boeing", "Airbus", "RTX", "Lockheed Martin"]`). Never put two time-horizons of the
  >   same company here — that produces a scorecard with no peers. The first entry is the
  >   target; its LTM scorecard data goes at `values[row][1]`.
  > - `values[row]` is **1-indexed against `companies`**: index `0` in every row is always `[]`
  >   (a silent placeholder the builder skips). `companies[0]` maps to `values[row][1]`,
  >   `companies[1]` maps to `values[row][2]`, and so on. Omitting the `[]` at index 0 will
  >   shift every peer column one position and silently misalign the data.
  > - Header rows (`is_header=true`) use `values[row] = [[], [], [], ...]` — one `[]` per company
  >   plus one for the placeholder. Length must equal `len(companies) + 1`.
  > - **Quick checklist before writing the scorecard payload:**
  >   1. `len(companies)` = number of peer entities (not counting the target).
  >   2. Every non-header `values[row]` has length `len(companies) + 1`.
  >   3. `values[row][0]` is always `[]`.
  >   4. `values[row][i+1]` contains `["metric_value", "ScoreLabel"]` for `companies[i]`.
- **esg_analysis** — table of CIS/E/S/G scores plus 3-5 commentary bullets.

Target first in every peer table.

---

## Step 4 — Build the HTML report

**Default output location: always save runs to the user's Desktop** so they're easy to
find. Use `~/Desktop/rating-pitch/<company>-<YYYYMMDD-HHMMSS>/` as the `<output-dir>`.
Only use a different path if the user explicitly asks for one.

1. Save your resolved payload to `<output-dir>/payload.json`.
2. No additional Python packages are required — `build_html.py` uses only the standard
   library. Verify Python 3 is available:
   ```bash
   python3 --version
   ```
3. Run the builder:
   ```bash
   python3 <skill-dir>/scripts/build_html.py <output-dir>/payload.json <output-dir>/rating_pitch.html
   ```
4. Open the report: `open <output-dir>/rating_pitch.html`
5. The final assistant message gives the full `<output-dir>/rating_pitch.html` path so the
   user can open the report in their browser.

If any section data is missing, still include the section in the payload (empty arrays
are fine) — the builder handles empties gracefully and the deck will stay well-formed.

---

## Payload schema

> ⚠️ **`rating_chart_data` constraint:** This array MUST have the same length as
> `rating_history`. Index `i` must match: `rating_history[i] ↔ rating_chart_data[i]`.
> Both arrays must be sorted **oldest → newest**.

```json
{
  "report_date": "April 15, 2026",
  "target_company": "Boeing Company (The)",
  "sector": "Aerospace/Defense",
  "currency": "USD",
  "companies": ["Boeing", "RTX", "Northrop Grumman", "..."],
  "sources": [
    {"id": 1, "title": "", "source": "", "date": "", "url": ""}  // id optional; rendered as [n] citation
  ],
  "sections": {
    "sector_overview": {
      "overview_bullets": ["...", "...", "..."],
      "watchlist_bullets": ["...", "...", "..."],
      "takeaway_bullets": ["...", "...", "..."]
    },
    "moodys_view": {
      "outlook_summary": "Two to four sentences (plain text or <p>...</p>).",
      "company_positioning": "One-line positioning statement.",
      "outlook_distribution": [
        {"category": "Stable",   "count": 11, "color": "#BDBFC3"},
        {"category": "Positive", "count": 5,  "color": "#5EB6BB"},
        {"category": "Negative", "count": 3,  "color": "#F09613"},
        {"category": "Under Review", "count": 1, "color": "#ED1B2E"}
      ]
    },
    "macro_outlook": {
      "gdp_table": {
        "year_columns": ["2023", "2024", "2025F", "2026F"],
        "rows": [{"country": "United States", "values": ["2.9", "2.8", "2.0", "1.8"]}]
      },
      "gdp_commentary": ["...", "...", "..."]
    },
    "rating_actions_ytd": [
      {"date": "Nov 20, 2025", "company": "...", "summary": "..."}
    ],
    "financial_analysis": {
      "commentary": ["...", "..."],
      "rating_history": [
        {"date": "Sep 2025", "rating": "Baa3", "outlook": "Negative",
         "direction": "Affirmation", "reason": "..."}
      ],
      "rating_chart_data": [8, 8, 7, 7, 7]
    },
    "revenue_distribution": {
      "by_segment":   [{"name": "Commercial Airplanes", "percentage": 45.2}],
      "by_geography": [{"name": "United States", "percentage": 55.0}],
      "commentary": ["...", "..."]
    },
    "swot": {
      "strengths":     ["...", "...", "..."],
      "weaknesses":    ["...", "...", "..."],
      "opportunities": ["...", "...", "..."],
      "threats":       ["...", "...", "..."]
    },
    "key_metrics": {
      "periods":      ["2021", "2022", "2023", "2024", "LTM Sep25"],
      "revenue":      [62286, 66608, 77794, 66517, 80757],
      "ebit_margin":  [-2.5, 4.1, -1.0, -16.1, -8.2],
      "debt_ebitda":  [-15.9, 8.5, 10.2, -6.8, -15.9],
      "rcf_net_debt": [-5.0, 10.1, 5.5, -8.3, -1.3]
    },
    "strategic_updates": {
      "recent":  ["...", "..."],
      "forward": ["...", "..."]
    },
    "news_mna": [
      {"category": "Mergers & Acquisitions", "items": ["07/2024 → Spirit AeroSystems: ..."]}
    ],
    "external_trends": [
      {"category": "Macro & Sector Trends", "items": ["..."]}
    ],
    "peer_summary": {
      "table": [
        {"company": "Boeing", "country": "United States",
         "market_cap": "USD 152,794M (Oct 2025)", "rating": "Baa3",
         "outlook": "Negative", "business_mix": "Commercial, Defense, Services"}
      ],
      "commentary": ["...", "..."]
    },
    "peer_financials": {
      "columns": ["Revenue", "EBITDA", "EBITDA Mg%", "CAPEX", "R&D/Rev",
                  "Debt/EBITDA", "FFO/Debt%", "FCF/Debt%", "RCF/Debt%"],
      "rows": [
        {"company": "Boeing", "period": "FY2024", "currency": "USD",
         "values": ["66,517", "(7,913)", "--", "(2,230)", "0.06",
                    "(6.81)", "(6.15)", "(26.57)", "(6.15)"]}
      ]
    },
    "peer_debt_charts": {
      "rcf_net_debt": [
        {"company": "Gen Dynamics", "value": 36.93, "period": "FY2024"},
        {"company": "Airbus",       "value": 32.0,  "period": "FY2024"},
        {"company": "Boeing",       "value": -6.15, "period": "FY2024"}
      ],
      "debt_ebitda": [
        {"company": "Airbus",       "value": 1.55,  "period": "FY2024"},
        {"company": "Gen Dynamics", "value": 1.62,  "period": "FY2024"},
        {"company": "Boeing",       "value": -6.81, "period": "FY2024"}
      ],
      "commentary": ["Two-sentence commentary."]
    },
    "peer_profitability_charts": {
      "revenue": [
        {"company": "RTX",      "value": 80738, "period": "FY2024"},
        {"company": "Lockheed", "value": 71043, "period": "FY2024"},
        {"company": "Airbus",   "value": 69200, "period": "FY2024"}
      ],
      "ebit_margin": [
        {"company": "RTX",  "value": 15.0, "period": "FY2024"},
        {"company": "BAE",  "value": 11.9, "period": "FY2024"},
        {"company": "Airbus","value": 10.7, "period": "FY2024"}
      ],
      "commentary": ["Two-sentence commentary."]
    },
    "peer_scatter": {
      "margin_vs_leverage": [{"company": "Boeing", "x": -6.81, "y": -16.1}],
      "fcf_vs_rcf":         [{"company": "Boeing", "x": -6.15, "y": -26.57}],
      "commentary": ["Two-sentence commentary."]
    },
    "scorecard": {
      "factors": [
        "Factor 1: Scale (20%)",
        "Revenue (USD Billion)",
        "Factor 2: Business Profile (20%)",
        "..."
      ],
      "is_header": [true, false, true, false],
      "companies": ["<TARGET>", "<PEER_1>", "<PEER_2>"],
      "values": [
        [[], [], [], []],
        [[], ["<target_rev>", "<target_score>"], ["<peer1_rev>", "<peer1_score>"], ["<peer2_rev>", "<peer2_score>"]]
      ]
    },
    "esg_analysis": {
      "table": [
        {"company": "Boeing", "cis": "CIS-4", "environmental": "E-3",
         "social": "S-4", "governance": "G-4"}
      ],
      "commentary": ["...", "..."]
    }
  }
}
```

---

## Report structure

The Python builder emits these 26 sections as HTML, in this order:

1. Cover
2. Agenda
3. Part 1 divider
4. Sector Overview (3-column chips)
5. Moody's View (outlook text + positioning + outlook pie)
6. Global Macro Outlook (GDP table + takeaways)
7. Rating Actions YTD (table)
8. Part 2 divider
9. Financial Analysis (bullets + rating history line chart + rating rationale)
10. Revenue Distribution (two pie charts + commentary)
11. SWOT (2×2)
12. Key Financial Metrics (four bar charts in 2×2 grid)
13. Strategic Updates (2 columns)
14. News, M&A & Leadership
15. External Trends, Pressures & Risks
16. Part 3 divider
17. Peer Comparison Summary (table + commentary)
18. Detailed Peer Comparison (wide financial table)
19. Peer Comparison — Debt (two horizontal bar charts)
20. Peer Comparison — Profitability (two horizontal bar charts)
21. Peer Scatter Plots (two scatter charts)
22. Scorecard Comparison (multi-column factor table)
23. ESG Analysis (table + commentary)
24. Citations (appendix — canonical numbered [n] references with hyperlinked titles)
25. Thank You
26. Disclaimer

The builder's data-visualization palette (Moody's official, priority order):
`#1 BRIGHT_BLUE=#005eff`, `#2 TEAL=#5eb6bc`, `#3 GOLD=#c7ab21`, `#4 MID_BLUE=#5c068c`,
`#5 PINK=#ba0168`, `#6 PURPLE=#c64809`, `#7 PALE=#bed6ff`, `NAVY=#040826`,
`LIGHT_GRAY=#e1e2e1`.

Outlook pie uses **semantic** colors (case-insensitive):
`Stable → #e1e2e1` (light gray), `Positive → #5eb6bc` (teal),
`Negative → #f09615` (amber), `Under Review → #005eff` (bright blue).

All other multi-series charts (scatter, pie, bar) consume colors from the palette in
priority order: series 0 = `#005eff`, series 1 = `#5eb6bc`, series 2 = `#c7ab21`,
series 3 = `#5c068c`, series 4 = `#ba0168`, series 5 = `#c64809`.

Charts are rendered client-side via Chart.js (loaded from cdnjs.cloudflare.com CDN).
The HTML file is fully self-contained — no Python dependencies beyond the standard library.

---

## Tips

- Run ALL data-gathering tool calls in a single parallel batch.
- Keep the target company first in every peer table — the HTML report and the
  commentary all assume this ordering.
- `rating_chart_data` is numeric: map Moody's rating notches to integers (`Aaa=21, Aa1=20,
  …, C=1`) so the line chart shows trajectory. Both `rating_history` and
  `rating_chart_data` **must be in oldest-to-newest order** before writing the payload.
  `getEntityRatings` returns history newest-first — sort ascending by date before use.
- Pie percentages must sum to 100 — bucket small categories into "Other".
- `key_metrics` arrays must match `periods` length. Use `null` for missing points.
- Scorecard header rows use `is_header=true` and `values[row] = [[], [], ...]` (empty
  per-company entries). The builder turns these into highlighted header rows in the HTML table.
- **Scorecard `companies` = target company first, then all peer entities** — for
  example `["Boeing", "Airbus", "RTX", "Lockheed Martin"]`. Never put two time-horizons
  of the same company here. `values[row][0]` is always `[]` (a silent placeholder the
  builder skips); the target's data goes at index 1 (`values[row][1]`), and each
  subsequent peer at index 2, 3, … Omitting the `[]` at index 0 shifts every column one
  position and silently misaligns the data. Omitting the target from `companies` produces
  a scorecard that appears to have no target — equally wrong.
- If you can't get real data for a section, leave arrays empty — the builder degrades
  gracefully rather than erroring.
- Dates in the report are just strings; format however reads best (e.g., "Nov 20, 2025").
- The `<output-dir>` name should be lower-cased and hyphen-joined (e.g.
  `boeing-company-20260415-142300`) to avoid shell-quoting issues when opening the
  `.html` file.
- Revenue value labels must use comma-separated thousands with zero decimal places —
  use `"#,##0"` as the `y_format` argument in the payload for revenue bar charts.
- **Never copy `period` values from `sample_payload.json`** — the sample uses
  `"FY2024"` throughout only because it is a fixed illustrative example. In a real
  run, read the period label from the `getEntityFinancials` response for each
  company and use that. A company reporting in 2025 must show `"FY2025"`, not
  `"FY2024"`. Anchoring on the sample year is a silent data-accuracy bug.
