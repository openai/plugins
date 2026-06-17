---
name: chronograph-portfolio-company-one-pager
description: >
  GP platform one-pager and investor report generator for private equity portfolio companies.
  Use this skill whenever a user asks to generate a company tearsheet, one-pager, investor
  report, portfolio overview, or company deep-dive — especially when they name a company or
  ask to "build a report", "create a one-pager", or "show me a tearsheet". Also trigger when
  the user asks to include commentary, quarterly updates, investment narratives, or any
  Investment Overview in the report output. This skill handles live data fetching via a
  connected MCP data source OR from an uploaded Excel model, metric formatting, AI-generated
  or model-sourced commentary, and rendering a fully styled HTML one-pager. Also trigger for
  LP quarterly updates, valuation summaries, and portco performance pages — any output that
  combines financials, valuation, and return data for a single portfolio company.
---

# GP Report Builder

Generates a fully styled, self-contained HTML investor report for a named portfolio company.
Supports two data source modes, two report types, and automatic brand detection from uploaded
templates. **Read this skill fully before writing a single line of HTML.**

**Requirements:** A connected Chronograph MCP server. These workflows are designed for permissioned Chronograph users to connect to their private investment data, or an uploaded Excel model for Model mode.

---

## Step 0 — Resolve Branding

Brand tokens are resolved automatically — the user never fills in a config file manually.
Execute the following decision tree before any other step.

### 0A — Check for an Uploaded Brand Template

Look for any of the following in the current conversation:

| File type | What to extract |
|---|---|
| **HTML / CSS file** | Parse all `color`, `background`, `font-family`, and `border` declarations. Identify the dominant background, primary accent, heading font, and body font. Extract any `--variable` tokens if a design system is present. |
| **PDF report or one-pager** | Visually analyse the document. Identify background color(s), the dominant accent/highlight color, heading and body typefaces, logo presence, and footer text. |
| **Image (PNG / JPG / SVG)** | Extract the 3–5 most visually prominent colors using the image content. Identify any visible text to infer font style (serif vs sans-serif, bold vs light). Note logo or wordmark if present. |
| **PowerPoint / PPTX** | Read slide backgrounds, title font, body font, accent colors from shapes and highlights. |
| **CSS / design token file** | Map token names to the brand token schema below directly. |

Once extracted, map findings to the Brand Token Schema in **0C**.

If the user has dropped **multiple** files, treat the most recent one as authoritative for
branding, unless the user specifies otherwise.

### 0B — No Template Provided → Apply Chronograph Defaults

If no brand template is present in the conversation, apply the following defaults silently —
do not ask the user to provide branding.

```
firm_name:             Chronograph
website:               www.chronograph.pe
confidentiality_label: CONFIDENTIAL

colors:
  bg_primary:       #101C1D   ← Near Black 1 (page background)
  bg_secondary:     #1A2627   ← Near Black 2 (card / panel background)
  bg_header:        #1B4147   ← Deep Teal (header strip)
  accent_primary:   #57E5EE   ← Bright Teal (headlines, KPI values, eyebrows)
  accent_secondary: #11A8B2   ← Regular Teal (bars, borders, left-rule accents)
  accent_negative:  #F95532   ← Accent Red (EBITDA bars, negative deltas)
  accent_positive:  #4ecb8a   ← Green (positive deltas)
  text_primary:     #FFFFFF   ← White (body text)
  text_muted:       #D9E8E8   ← Light teal tint (footnotes, commentary)
  table_header_bg:  #1B4147   ← Deep Teal (table header row)

fonts:
  heading:         Ubuntu
  heading_weight:  700
  body:            Open Sans
  body_weight:     300
  google_fonts_url: https://fonts.googleapis.com/css2?family=Ubuntu:wght@700&family=Open+Sans:wght@300;300i&display=swap

logo:
  url:      (none — render firm name as text)
  position: top-left

theme: dark
```

### 0C — Brand Token Schema

Whether tokens are extracted from a template (0A) or defaults are applied (0B), resolve all
of the following before proceeding. Every downstream panel references these names.

| Token | Role | Fallback if undetectable |
|---|---|---|
| `firm_name` | Firm name in header and footer | Infer from logo text or filename; else `"Your Firm"` |
| `website` | Footer URL | `""` (omit from footer) |
| `confidentiality_label` | Footer suffix | `"CONFIDENTIAL"` |
| `bg_primary` | Page / root background | Chronograph default |
| `bg_secondary` | Card / panel background | Darken `bg_primary` by 5% |
| `bg_header` | Header strip background | Darken `bg_primary` by 15% |
| `accent_primary` | Headlines, KPI values, eyebrow labels | Dominant bright color from template |
| `accent_secondary` | Bars, borders, left-rule accents | Mute `accent_primary` by 30% |
| `accent_negative` | Negative values, downward deltas | `#F95532` |
| `accent_positive` | Positive deltas | `#4ecb8a` |
| `text_primary` | Main body text | `#FFFFFF` on dark; `#1A1A1A` on light |
| `text_muted` | Footnotes, commentary | Tint `text_primary` toward `bg_primary` by 20% |
| `table_header_bg` | Table header row | `bg_header` |
| `font_heading` | Heading / KPI / eyebrow font | Detected from template; else `Ubuntu` |
| `font_heading_weight` | Heading weight | `700` |
| `font_body` | Body / table / footnote font | Detected from template; else `Open Sans` |
| `font_body_weight` | Body weight | `300` |
| `google_fonts_url` | Font load URL | Build from detected font names |
| `logo_url` | Logo image src | `""` — fall back to firm name as text |
| `logo_position` | Header logo placement | `top-left` |
| `theme` | `dark` or `light` | `dark` if `bg_primary` luminance < 0.2; else `light` |

### 0D — Theme Handling

**Dark theme** (luminance of `bg_primary` < 0.2):
Use the token values as resolved. Default contrast pairings apply (white text on dark
backgrounds). Minimum contrast ratio: 4.5:1 for body text, 3:1 for large text (≥ 18px bold).

**Light theme** (luminance of `bg_primary` ≥ 0.2):
- Swap `text_primary` to a near-black (e.g. `#1A1A1A`) if not already dark
- Ensure `accent_primary` provides ≥ 3:1 contrast against `bg_primary`
- Table header: use the firm's dark brand color (e.g. deep navy / dark green) rather than
  a light value

### 0E — Confirm with the User (optional, brief)

After resolving tokens, output a **single short line** — not a table, not a list — before
generating the report:

> *"Using [firm_name] branding — [accent_primary] accent on [bg_primary] background,
> [font_heading] / [font_body] fonts."*

If brand detection produced low-confidence results (e.g. only a logo image was provided with
no color context), ask one focused question:

> *"I've picked up [X] and [Y] from your file — is that the right color scheme,
> or would you like to adjust anything?"*

Do not ask if defaults were applied — just proceed.

---

## Step 1 — Determine Report Mode

**Data source mode:**

| Signal | Mode |
|---|---|
| User uploads an Excel model (.xlsx) or references an uploaded file | **Model mode** — read data from the file |
| No file uploaded; company exists in the connected data platform | **MCP mode** — fetch live from the platform |
| Both available | Prefer the model for financials and commentary; use MCP to supplement metadata and returns |

**Report type:**

| User asks for… | Report type |
|---|---|
| One-pager, tearsheet, company report, GP report | **GP One-Pager** |
| LP update, quarterly update, LP quarterly report | **LP Quarterly Update** |

If unclear, default to **GP One-Pager**.

---

## Step 2 — Resolve the Company & Fetch Data

### MCP Mode

All data is fetched from the user's connected **Chronograph MCP server**. The agent must have the Chronograph MCP connected before running the skill in MCP mode; if it isn't connected, prompt the user to connect it, or fall back to Model mode if a file is available.

Inspect the connected Chronograph MCP's tool list at runtime and pick the appropriate tool for each step below based on the tool descriptions the server provides. Do not hard-code tool names — read the live descriptions to stay current.

### Fetch sequence

Work through these steps in order. At each step, identify the right Chronograph tool from its description, call it to fetch what the report needs, and hold the result for the rendering steps that follow. The skill does not need a fixed schema — only the values listed below in plain language.

**1. Resolve the company.** Find the tool that searches for companies, funds, and other portfolio entities by name. Use it to turn the user's input into a canonical company. If multiple candidates come back, prefer the closest name match; ask the user only if genuinely ambiguous.

**2. Get the company's basic facts.** Use the tool that retrieves core portfolio entity records. Fetch what the **Header Strip** (Step 4) needs: company name, sector, industry, geography, HQ, and the company's reporting currency. Request only what the header renders — the tool's description will list what's available.

**3. Get the company's investments.** Using the same core-entity retrieval tool, fetch the list of investments associated with the company. The **Investment Returns Table** (Step 4) needs one row per investment: investment name, the fund it belongs to, entry date, exit date if applicable, and whether it has exited.

**4. Get the company's financial line items.** Find the tool for company-level financial metrics. Make a discovery / help call first, passing the company ID, to see what's available.

**Metric selection rule.** Always query by the platform's metric type when one is available for the line item — even if the company's display label differs. Use a company-specific mapped metric definition only when no metric type covers the line item or the request is inherently tenant-specific (bespoke KPIs, commentary fields, operating metrics, custom valuation inputs).

Priority:

1. Platform metric type
2. Company-specific mapped metric definition (only if no metric type exists)
3. Name-based metric search (only if neither of the above resolves)

Do not pick a company-specific metric because its label is a closer word match than an available metric type. Metric types drive querying; display labels drive presentation.

What the report needs (query via the metric type whenever available):

- **Financial Performance Table:** Revenue, Gross Profit, EBITDA, the company's adjusted EBITDA series, and Net Debt. Pull the last 4–5 trailing-twelve-month periods plus the most recent quarter.
- **Valuation Summary Table:** Enterprise Value, valuation multiple, Total Debt, Cash, Net Debt, Equity Value — current quarter and prior quarter.
- **KPI Strip:** the latest values for LTM Revenue, LTM Adj. EBITDA, Enterprise Value, and Net Debt.

Use LTM for income-statement items, As-of for balance items. The discovery response will tell you which period types are supported per metric.

**5. Get per-investment returns.** Find the tool for investment-level performance. It uses gross performance figures (not net — net lives elsewhere on the platform and is the wrong tool for the GP one-pager). The **Investment Returns Table** needs, per investment: invested capital, realized proceeds, unrealized value, MOIC, and IRR. Sum across investments to populate the MOIC card in the **KPI Strip**.

**6. Resolve any non-standard metrics by name.** If the user asks the report to include a tenant-specific KPI that isn't part of the platform's standard metric set — e.g. a custom operating metric — use the metric-name search tool to resolve it to an ID before querying the company-metrics tool.

### Currency

Use the company's reporting currency as returned in step 2. **Do not default to USD.** If the user explicitly asks for a different currency, pass that through to each tool call.

### If something is missing

- Company not found → ask the user to confirm spelling; try the legal name.
- A metric returns no value → display `—`. Never fabricate.
- A tool returns a schema or help error → comply with the introspection call it asks for and retry.
- Chronograph MCP not connected → prompt the user to connect it, or fall back to Model mode.

### Model Mode

Read the uploaded Excel file using pandas (`data_only=True`). Extract from:

| Tab | Data to extract |
|---|---|
| `Overview` | Company name, HQ, fiscal year end, fund name(s), investment names, entry dates, ownership % |
| `Performance` | Revenue, Gross Profit, EBITDA, Adj. EBITDA (Reported and Valuation basis), Net Debt — last 4–5 LTM periods |
| `Valuation` | EV, valuation multiple, equity value, net debt — current and prior quarter; commentary text (Business Update, Rationale for Conclusion, Rationale for Discount); per-investment cost, realized, unrealized, MOIC |

**Currency and scale:** Check the `Figures In` field on the Overview tab. If `1000`
(thousands), divide all financial values by 1,000 before displaying in millions. Note the
`Local Currency` field and include it in the report header.

**If commentary is present in the model**, use it verbatim (lightly edited for grammar only).

---

## Step 3 — Layout Structure

Both report types share the same structural template. The Financial Performance table must
always be **directly above** the Valuation Summary table in the same column.

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER — Logo · Company · Fund · Sector · HQ · Report date    │
│           Tag pills: sector, geography, fund, status           │
├─────────────────────────────────────────────────────────────────┤
│  KPI STRIP (5 cards, full width)                               │
│  LTM Revenue | LTM EBITDA | Enterprise Value | Net Debt | MOIC │
├───────────────────────────┬─────────────────────────────────────┤
│  LEFT COLUMN              │  RIGHT COLUMN                       │
│                           │                                     │
│  Financial Performance    │  Revenue & EBITDA Bar Chart         │
│  Table                    │  (last 4 LTM periods, SVG inline)  │
│                           │                                     │
│  Valuation Summary        │  Investment Returns Table           │
│  Table  ← must stay here  │                                     │
│                           │                                     │
├───────────────────────────┴─────────────────────────────────────┤
│  COMMENTARY (full width, up to 3 columns)                      │
│  Business Update | Valuation Rationale | Discount Rationale    │
├─────────────────────────────────────────────────────────────────┤
│  FOOTER — © {firm_name} | {website} | {confidentiality_label} │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 4 — Panel Specifications

### Header Strip

- Background: `bg_header` → `bg_primary` gradient, 135°
- **Logo:** if `logo_url` is set, render `<img src="{logo_url}">` at `logo_position`;
  maintain clearspace equal to the cap-height of the firm name on all sides
- **Logo fallback:** if `logo_url` is blank, render firm name in `font_heading`,
  `font_heading_weight`, 24px, `text_primary`
- Company name: `font_heading`, 28px, `accent_primary`
- Subtitle (fund · sector · HQ · date): `font_body`, 12px, `text_muted`
- Tag pills: `bg_secondary` fill, `accent_secondary` border, `font_body` 10px

### KPI Strip (5 cards)

| Card | Value |
|---|---|
| LTM Revenue | Current period revenue |
| LTM Adj. EBITDA | Valuation basis if available, else Reported |
| Enterprise Value | Current quarter EV |
| Net Debt | Current quarter net debt |
| Gross MOIC | Blended or primary investment MOIC |

- Card: `bg_secondary` background, 6px border-radius, `box-shadow: 0 2px 8px rgba(0,0,0,0.4)`
- Value: `font_heading`, 28px, `accent_primary`
- Label: `font_body`, 9px, uppercase, letter-spacing 0.05em, `text_primary`
- Delta: `▲ +X%` in `accent_positive` · `▼ -X%` in `accent_negative`

### Financial Performance Table (LEFT column, top)

Rows (LTM, 3 prior periods + current quarter, vs. PY column):

| Row | Notes |
|---|---|
| Revenue | |
| Gross Profit | |
| Gross Margin % | |
| EBITDA | |
| EBITDA Margin % | |
| **Adj. EBITDA (Valuation)** | Highlight row — `font_heading`, `accent_primary` value |
| **Adj. EBITDA Margin %** | Highlight row |
| Net Debt | |

- Header row: `table_header_bg`, `font_body` 9px uppercase, `text_primary`
- Alternating rows: `bg_secondary` / `bg_primary`
- Highlight rows: `rgba({accent_primary}, 0.06)` background
- Numeric columns right-aligned; label column left-aligned

### Valuation Summary Table (LEFT column, directly below Financial Performance)

| Row | Notes |
|---|---|
| Valuation Multiple | `X.Xx` |
| Adj. EBITDA (LTM) | currency |
| **Enterprise Value** | Highlight row |
| Total Debt | |
| Cash | |
| Net Debt | |
| **Total Equity Value** | Highlight row |

Prior Quarter vs Current Quarter, plus a delta column (`accent_positive` / `accent_negative`).

### Revenue & EBITDA Bar Chart (RIGHT column, top)

- **Inline SVG only** — no external JS or D3
- Side-by-side bars: Revenue in `accent_secondary`, Adj. EBITDA in `accent_negative`
- Current quarter Revenue bar: `accent_primary`
- 4 LTM periods on x-axis; `$Xm` labels above each bar
- Current quarter label: `font_heading`, `accent_primary`; prior: `font_body`, `text_muted`
- Y-axis gridlines: dashed, `rgba({accent_primary}, 0.08)`
- Legend: colour swatches + labels, `font_body` 9px
- Auto-scale: y-axis max = largest revenue × 1.2; bar heights proportional

### Investment Returns Table (RIGHT column, bottom)

| Column | Format |
|---|---|
| Investment name | Left-aligned |
| Entry date | `Mon YYYY` |
| Ownership % | `X.X%` |
| Cost (Gross) | `$Xm` |
| Realized | `$Xm` |
| Unrealized | `$Xm` |
| MOIC (Gross) | `X.XXx` — `font_heading`, `accent_primary` |

- Sort: largest cost first
- **Total / Blended** row at bottom in `font_heading`
- Add IRR column if available; omit column if all values null
- Unavailable values: `—`
- One-sentence QoQ note below table: `font_body` 9.5px, `text_muted`

### Commentary Section (full width, up to 3 columns)

1. **Business Update** — verbatim from model if present; AI-generated in MCP mode
2. **Rationale for Valuation Conclusion** — verbatim from model if present
3. **Rationale for Discount to Comps** — verbatim from model if present

- Eyebrow label: `accent_primary`, 9px, uppercase, letter-spacing 0.08em,
  1px bottom border in `accent_primary`
- Body: `font_body`, 11px, `text_muted`, line-height 1.6
- Collapse empty columns — never show a blank block

---

## Step 5 — LP Quarterly Update Additions

When report type is **LP Quarterly Update**:

1. Header eyebrow → `LP QUARTERLY UPDATE · Q[N] YYYY`
2. Commentary must come from model verbatim — never AI-generate for LP reports
3. Add an optional **valuation bridge note** below the Valuation Summary table:
   *"EV increase driven by multiple expansion from X.Xx to Y.Yx; EBITDA contribution +$Zm"*

---

## Step 6 — CSS Variables & Font Loading

Populate these from the resolved brand tokens (Step 0). Set once in `<style>`; all panels
inherit automatically.

```html
<!-- In <head> -->
<link href="{google_fonts_url}" rel="stylesheet">

<style>
:root {
  --bg-primary:        {bg_primary};
  --bg-secondary:      {bg_secondary};
  --bg-header:         {bg_header};
  --accent-primary:    {accent_primary};
  --accent-secondary:  {accent_secondary};
  --accent-negative:   {accent_negative};
  --accent-positive:   {accent_positive};
  --text-primary:      {text_primary};
  --text-muted:        {text_muted};
  --table-header-bg:   {table_header_bg};
}

body {
  font-family: '{font_body}', sans-serif;
  font-weight: {font_body_weight};
  background: var(--bg-primary);
  color: var(--text-primary);
  margin: 0;
}

h1, h2, h3, h4, .eyebrow, .kpi-value, .moic-value {
  font-family: '{font_heading}', sans-serif;
  font-weight: {font_heading_weight};
}
</style>
```

---

## Step 7 — Formatting Rules

| Type | Format |
|---|---|
| Currency (millions) | `$43.5m` |
| Negative / net cash | `($3.4m)` in `var(--accent-negative)` |
| Multiples | `1.41x` |
| Percentages | `15.7%` |
| Basis point changes | `+70bps` |
| Dates | `Q4 2024` or `31 Dec 2024` |
| MOIC | `4.97x` — heading font, `var(--accent-primary)` |
| Positive delta | `▲ +X%` — `var(--accent-positive)` |
| Negative delta | `▼ -X%` — `var(--accent-negative)` |
| Unavailable | `—` (em dash) — never fabricate |

---

## Step 8 — Output

- **File name:** `[company_name_lowercase_underscored]_[report_type]_[quarter].html`
  - Examples: `ashworth_health_gp_report.html` · `ashworth_health_lp_update_q4_2024.html`
- **Single self-contained HTML file** — all CSS in `<style>`, all data inline
- **No external JS** — bar chart is inline SVG
- **Footer:** `© {firm_name} | {website} | {confidentiality_label}` (omit blank fields)
- Save to the outputs directory and present the file to the user

---

## Error Handling

| Situation | Action |
|---|---|
| No brand template and no defaults configured | Apply Chronograph defaults silently |
| Brand template provided but colors are ambiguous | Apply best-guess tokens; surface the one-line confirmation (Step 0E) |
| Logo URL returns 404 or is empty | Fall back to firm name as heading-font text |
| Company not found via MCP | Ask user to confirm spelling; try alternate names |
| Metric unavailable | Display `—`; never fabricate |
| Commentary empty in model | AI-generate; label `(AI-generated)` in small `text_muted` |
| IRR null for all investments | Omit IRR column |
| Cost split unavailable for a tranche | Show combined row; note gap in footnote |
| Model and MCP figures conflict | Flag in footnote; prefer model figures |
| `Figures In` = 1000 | Divide all values by 1,000 before displaying in millions |
| Light-theme brand detected | Swap text tokens to dark; verify contrast ≥ 4.5:1 before rendering |
| Chronograph MCP not connected (MCP mode) | Prompt user to connect; fall back to Model mode if a file is available |

---

## Data & Brand Checklist (verify before rendering)

**Brand**
- [ ] Brand tokens resolved — from uploaded template or Chronograph defaults
- [ ] One-line brand confirmation output to user (or low-confidence question asked)
- [ ] CSS variables set; Google Fonts `<link>` in `<head>`
- [ ] Logo rendered or firm-name fallback applied
- [ ] Theme (dark/light) confirmed; contrast ratios verified

**Data**
- [ ] Data source mode determined (Model or MCP)
- [ ] Report type determined (GP One-Pager or LP Quarterly Update)
- [ ] Currency and scale confirmed (`Figures In` handling applied if needed)
- [ ] Financial Performance table: 4 periods + vs. PY column
- [ ] Valuation Summary: PQ vs CQ + delta — in same column as Financial Performance
- [ ] Bar chart: 4 periods, bars labelled, y-axis auto-scaled
- [ ] Investment Returns: per-investment rows + total row
- [ ] Commentary: model text verbatim if available; empty blocks collapsed
- [ ] Footer: firm name, website, confidentiality label (omit blanks)
- [ ] Single self-contained HTML file, no external JS
