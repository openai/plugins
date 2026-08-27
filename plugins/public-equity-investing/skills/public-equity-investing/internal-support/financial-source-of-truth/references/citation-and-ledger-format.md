# Citation and Evidence Ledger Format

Use this reference to make source support auditable across markdown, spreadsheets, documents, and slide outputs.

## Native citations first

If the active environment provides native citations from web, files, callable connectors, or internal search, use those citations exactly as required by that environment. Do not imply connector access when it is not callable, and do not replace native citations with generic source IDs in the final user-facing answer.

Use source IDs such as S1, S2, and S3 as an internal and appendix-friendly shorthand, especially when building a source inventory or evidence ledger.

## What requires citation

Cite or label the following:

- Every hard number that affects analysis: revenue, EBITDA, FCF, growth, margin, leverage, valuation, market price, consensus, ownership, ETF/index weight, borrow, short interest, option data, CDS/spread signals, ARR, churn, net debt, share count, EPS, NAV.
- Every direct quote or paraphrased management statement.
- Every issuer, management, broker, or company-presentation claim extracted from an investor deck, earnings call, conference deck, sell-side note, or other non-filed source.
- Every consensus, market data, rating, forecast, or third-party estimate.
- Credit terms only when they support a common-equity risk view: maturity, coupon, covenant headline, lien/priority signal, guarantee, amortization, or call protection. Route credit-security analysis to Credit Markets.
- Every macro release or policy fact that drives the view.
- Every evidence finding that supports a red flag, kill criterion, recommendation, or investment action.

## What does not always require citation

Do not overload short outputs with citations for generic reasoning. The following can usually be uncited unless the specific claim is disputed or decision-critical:

- Basic finance formulas.
- Your own clearly labeled inference.
- A scenario assumption explicitly chosen by the user.
- Formatting comments or writing-quality feedback.
- An evidence request derived from a missing source.

## Citation placement

Place the citation immediately after the supported claim.

Good:

```markdown
Revenue grew 12 percent year over year in Q2, while gross margin declined 180 bps. [S1]
```

Bad:

```markdown
Revenue grew 12 percent year over year and margins declined, showing cost pressure and weak execution. [S1]
```

The bad example over-cites the interpretation. Rewrite as:

```markdown
Revenue grew 12 percent year over year and gross margin declined 180 bps. [S1] The margin decline suggests cost pressure, but the cause needs support from management commentary or cost detail.
```

## Source inventory template

```markdown
| ID | Source | Source owner | Type | Date / as-of | Period | Tier | Used for | Freshness | Limits |
|---|---|---|---|---|---|---|---|---|---|
| S1 | [title or file name] | [company / vendor / user / court / regulator / broker] | [filing / model / transcript / vendor / agreement / presentation] | [date] | [period] | [tier] | [metric/claim] | [label] | [caveat] |
```

## Evidence ledger template

```markdown
| Claim / metric | Label | Source ID(s) | Exact support | Caveat or conflict | Decision impact |
|---|---|---|---|---|---|
| [claim] | [`fact_source_reported` / `issuer_management_claim` / `assumption_inferred` / `estimate_consensus`] | [S1] | [what the source actually supports] | [limits] | [why it matters] |
```

## Assumption register template

```markdown
| Assumption | Type | Basis | Evidence support | Sensitivity | Owner | Status |
|---|---|---|---|---|---|---|
| [assumption] | [operating / valuation / credit / macro / timing / legal] | [why chosen] | [direct / indirect / none / missing_required_source] | [what changes if wrong] | [user / analyst / management] | [accepted / needs evidence] |
```

## Evidence requests template

```markdown
| Priority | Request | Why it matters | Current evidence | Required support | Owner |
|---:|---|---|---|---|---|
| 1 | [specific request] | [decision impact] | [current source/claim] | [document/data needed] | [company / management / vendor / user] |
```

## Spreadsheet and model source notes

When producing or reviewing a workbook:

1. Add a first visible `Cover` or dashboard tab that summarizes source posture, stale/missing evidence, unsupported assumptions, and where source support lives.
2. Add a `Sources` or `Evidence Ledger` tab when the model is decision-grade.
3. Add source comments or notes to key input cells when feasible.
4. Do not cite formulas as sources. Cite the inputs behind the formulas.
5. Mark assumptions in a different section from historical sourced values.
6. Include as-of dates for market data, consensus, rates, spreads, and prices.
7. Include a checks section that flags missing source notes, stale inputs, and hardcoded formulas that should be linked.

Suggested source note format for a model input:

```text
Source: S3, FY2025 10-K, Note 12, filed 2026-02-20. As-of: FY2025. Used for debt maturity schedule.
```

## Slides and decks

When producing or reviewing slides:

1. Keep source footnotes short but specific.
2. Make repeated metrics tie to the same source and definition across the deck.
3. If a slide uses a derived number, cite the source for inputs and name the calculation.
4. Flag any slide where title claim is stronger than the evidence.
5. Put detailed source inventory in appendix when footnotes would overwhelm the slide.

## Output labels

Use labels inline when useful:

- **Verified fact:** directly supported by appropriate evidence.
- **Issuer / management claim:** from investor deck, earnings call, conference deck, broker note, or company presentation.
- **Assumption:** chosen input; not proven by evidence.
- **Inference:** analyst conclusion from evidence.
- **Estimate:** calculated or approximated.
- **Stale:** may be superseded.
- **Conflict:** sources disagree.

## Compact evidence note

Use this for fast answers:

```markdown
Evidence note: [verified / preliminary / assumption-led]. Primary support: [sources]. Key caveat: [stale/conflicting/missing item].
```

## Practical evidence posture block

Use this when the user needs a source-of-truth answer, not only a ledger:

```markdown
Evidence posture: [decision-grade / research-grade / preliminary / assumption-led / not supportable]
Supported facts: [what the evidence actually supports]
Assumptions / inferences: [what is assumed, inferred, estimated, or user-provided]
Limitations / conflicts: [what is stale, missing, contradictory, or too precise]
Next actions: [specific source request or tie-out that upgrades the work]
```

This block is the default fallback when source context is partial. It should be concrete enough to guide the next analyst step and conservative enough to avoid invented precision.
