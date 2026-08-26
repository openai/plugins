# P0 Integrations

## Ownership boundaries

This skill owns public trading comps judgment, peer-set framing, valuation multiple read-throughs, and implied valuation ranges.

Adjacent P0 ownership:

| Area | This skill owns | Adjacent skill owns |
|---|---|---|
| Source hierarchy | Use labels and caveats | `financial-source-of-truth` owns source priority, stale-data rules, conflicts, and citation format |
| Messy exports | Identify unusable data and route | `excel-data-cleaner` owns table cleanup and normalization |
| Full workbook | Select workbook mode and provide requirements | `comps-valuation` in `workbook` mode owns Excel/Sheets comps models |
| Workbook audit | Flag issues in memo | `model-audit-tieout` owns formula, link, and model QA |
| Final materials | Provide comps support | `deck-report-qc` owns deck/report circulation checks |
| DCF cross-check | Provide market multiple range | `dcf-model-builder` owns DCF mechanics |
| Credit Markets | Provide leverage, liquidity, or valuation-cushion context only when needed for a public-equity comps view | Credit Markets owns credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis |
| Model update | Provide peer multiple support | `equity-model-update` owns public-company model refresh from new actuals, guidance, consensus, and KPI disclosures |
| Investment synthesis | Provide valuation support | `memo-builder` owns full memo narrative and recommendation |

## Downstream handoff contract

When comps support another P0 skill, expose these fields clearly.

### Peer-set handoff

- target / subject;
- selected peer set;
- peer role labels;
- excluded close peers;
- business-model rationale;
- geography / size / growth / margin / leverage caveats.

### Valuation handoff

- as-of date;
- selected multiples;
- statistic used: median, p25, p75, trimmed mean, or selected range;
- denominator used for target;
- implied EV;
- net debt and other claims;
- implied equity value;
- implied value per share, if applicable;
- source limitations.

### QA handoff

- missing fields;
- stale fields;
- source conflicts;
- adjustment basis;
- currency / FX issues;
- outlier treatment;
- confidence level;
- output posture label.

## Handoff uses

Use the handoff for:

- `dcf-model-builder` as a market cross-check;
- Credit Markets as leverage, liquidity, recovery, and refinancing context only when the final view is public equity;
- `equity-model-update` as public-company model refresh support;
- `memo-builder` as valuation support;
- `deck-report-qc` as the tie-out source for final materials.

## Workbook routing

If the user asks for Excel, Google Sheets, refreshable data, formula-driven EV bridge, source tabs, peer-universe management, sensitivity tables, or a file deliverable, use `comps-valuation` in `workbook` mode.

Do not emit ad hoc exported workbook artifacts from `report` mode. If the user needs a downloadable table, CSV/XLSX, workbook shell, or audit-ready file package, preserve the normalized requirements and caveats while switching to `workbook` mode. For a substantial reusable comps report, produce a standalone HTML comps report following the shared HTML artifact standard; hand a normalized payload to `dashboard-builder` only when the user explicitly selects a standardized dashboard or structured payload-driven render.
