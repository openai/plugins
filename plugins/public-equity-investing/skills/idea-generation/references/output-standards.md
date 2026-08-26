# Output Standards and Templates

Use this reference when producing a PM pack, idea cards, exportable idea log, or examples of senior-investor language. For a substantial screen, market map, watchlist review, or source-heavy candidate set, default to a flexible standalone HTML idea-triage report following `../../../shared/html-artifact-standard.md`; use the standardized dashboard pack only when that dashboard path is explicitly selected.

## HTML idea-triage report

Use a candidate funnel or exposure-versus-expectations matrix as the primary visual object rather than a generic dashboard summary. Lead with the research-priority conclusion, then classify names as `Advance to deeper work`, `Valuation / expectations gated`, `Exposure not yet proven`, or `Deprioritized or reject`.

For thematic screens, show beneficiary pathways before or alongside rank, such as electrical/power distribution, construction, networking, cooling, grid/generation, and colocation/real estate. A name advances only when evidence connects the demand driver to orders, backlog, revenue, margins, or estimate revisions; otherwise mark it `needs exposure attribution`.

Recommended HTML sequence:

- Research-priority conclusion and three to five distinct summary tiles.
- Candidate funnel or exposure-versus-expectations matrix.
- Ranked candidate board with beneficiary pathway, exposure proof, expectations risk, first rejection, and next workflow.
- Short idea cards for highest-priority names only.
- Deprioritized or false-positive list, missing evidence, and source ledger.

Use `crowded` only for supported positioning, ownership, flow, short-interest, or comparably direct evidence. With indirect evidence only, write `expectations-heavy`, `valuation-gated`, or `crowding-risk candidate`.

## Default report structure

Use this structure unless the user requests a shorter or different format:

# Public Equity Investing Idea Generation

## Scope and assumptions
- Universe, region, sector, market cap, liquidity, instruments.
- Mandate, direction, horizon, and constraints.
- Sources used and freshness caveats.
- Assumptions inferred from missing context.

## Executive summary
- Top 3-5 conclusions.
- Most actionable ideas.
- Best long, short, pair, event, and watchlist candidates if relevant.
- Biggest false positives or data issues.
- Recommended next work.

## Methodology
- Archetypes used.
- Factor dimensions.
- Sector-specific adjustments.
- Ranking logic.
- Data-quality limitations.

## Ranked idea table
Include columns appropriate to available data:

| Rank | Ticker | Company | Direction | Pathway | Priority | Exposure proof | Expectations risk | Variant wedge | Why now / catalyst | First rejection test | Next workflow |
|---:|---|---|---|---|---|---|---|---|---|---|---|

## Top idea cards
Use the idea-card template below.

## Rejected / deprioritized names
Explain why names that screened well were killed or deprioritized.

## Cross-idea themes and risk observations
Discuss sector, macro, factor, liquidity, crowding, benchmark, and portfolio implications.

## Recommended next workflows
Map candidates to downstream skills or human workstreams.

## Data gaps and caveats
State missing data, stale data, assumptions, and required follow-up.

## Idea-card template

### [Ticker] - [Company] - [Direction] - [Setup type] - [Priority]

**Security snapshot**
- Region/sector/industry:
- Market cap/liquidity:
- Benchmark/portfolio/watchlist status if known:
- Source date and data caveats:

**Why it surfaced**
- Name the factor triggers, not just the rank.
- Mention valuation, growth, revisions, quality, momentum, catalysts, risk, liquidity, crowding, and portfolio fit only where relevant.

**Exposure proof**
- State the source-backed link between the theme or driver and orders, backlog, revenue, margins, or estimate revisions.
- If that link is unavailable or unquantified, label the candidate `needs exposure attribution`.

**Potential thesis wedge / variant perception**
- What the market appears to believe.
- What the investor might believe differently.
- Whether the possible edge is analytical, mosaic, time-horizon, behavioral, structural, or variant interpretation.

**Why now**
- Catalyst, revision inflection, price dislocation, narrative shift, flow/technical event, or watchlist trigger.

**What must be true**
- Fundamental conditions required for the idea to work.

**What would invalidate it**
- Disconfirming evidence or kill criteria.

**Main false-positive risk**
- The first smart reason a senior PM might reject the idea.
- State whether crowding is verified by direct evidence or only an inferred expectations risk.

**Next highest-value work**
- Model, filings, transcript review, consensus bridge, peer work, catalyst timeline, borrow check, channel work, valuation scenarios, credit review, hedge analysis, or memo.

**Recommended routing**
- Downstream skill or human owner/workstream.

## Structured idea log schema

When the user wants an exportable database or recurring tracker, use fields like:

- idea_id
- date_generated
- ticker
- company
- security_type
- region
- sector
- industry
- market_cap
- liquidity
- direction
- setup_type
- rank
- priority
- why_surfaced
- valuation_summary
- growth_summary
- revision_summary
- quality_summary
- momentum_summary
- catalyst_summary
- risk_summary
- variant_perception
- why_now
- what_must_be_true
- what_would_invalidate
- main_false_positive_risk
- next_research_step
- recommended_downstream_skill
- data_sources
- data_gaps
- status

If creating a spreadsheet, preserve source tabs and write output to a new tab or new file.

## PM-grade language examples

Weak:
"ABC is cheap and has strong growth. It may be a good long idea."

Strong:
"ABC screens as a possible revision-inflection long, not simply a cheap stock. The stock remains near trough valuation while the first positive FY2 EBITDA revisions in four quarters suggest consensus may be moving from estimate reset to recovery. The potential wedge is that the market still treats the margin improvement as temporary, while segment disclosure may support a more durable mix/cost bridge. The idea is not underwritten yet: rebuild the FY2 margin bridge, compare consensus to guidance, and test downside if revenue weakness offsets cost saves. First rejection risk: this is a value trap if the denominator is still too high."

Weak:
"XYZ has poor momentum and high valuation, so it is a short."

Strong:
"XYZ is a possible over-earning short. The setup depends on consensus margin assumptions proving too high, not just valuation mean reversion. Margins appear above normalized levels while revenue momentum is decelerating and the stock still trades at a premium multiple. Before advancing, check borrow cost, short interest, customer concentration, and buyback support. First rejection risk: a low bar next print could trigger a squeeze before the fundamental short thesis plays out."

Weak:
"DEF is a good company but expensive."

Strong:
"DEF belongs on watchlist, not active research, unless price or revisions create a better entry point. Business quality appears high, but the current setup lacks variant perception: the market already prices durable growth and clean execution. Move to active research if a drawdown creates a valuation dislocation without degradation in retention, margins, or bookings."

## Tone and concision

- Be direct, skeptical, and decision-oriented.
- Use plain investment language.
- Avoid cheerleading.
- Say when an idea is merely interesting rather than actionable.
- Distinguish verified positioning from valuation-gated or expectations-heavy exposure.
- Prefer a sharp top five over a long list of generic names.
- Use "candidate," "screen flag," "watchlist," and "requires diligence" unless the user has requested a final pitch or memo.

## PM Output Standard

Every top idea should include actionability, variant wedge, why now, what is priced in, first smart rejection reason, what would make it investable, what would kill it, and next workflow owner.
