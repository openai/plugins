# Analytical SQL Semantics

Use these rules only for the applicable analytical pattern. A matching domain
specialization remains authoritative for business metrics, entity keys, exclusions,
and denominators. Use PostgreSQL-compatible forms unless a required alternative is
verified through the CognitiveDB SQL capabilities guidance.

## Contents

- [Reported Row Identity](#reported-row-identity)
- [Counts and Grain](#counts-and-grain)
- [Existing SQL and Nested Data](#existing-sql-and-nested-data)
- [Ranking and Requested Output](#ranking-and-requested-output)
- [Evidence and Result Interpretation](#evidence-and-result-interpretation)
- [Time Comparisons and Boundaries](#time-comparisons-and-boundaries)
- [Averages Across Groups](#averages-across-groups)
- [Trailing and Rolling Windows](#trailing-and-rolling-windows)
- [Ratios, Percentages, and Growth](#ratios-percentages-and-growth)
- [Distributions](#distributions)

## Reported Row Identity

Use identifiers from structured result rows verbatim rather than reconstructing
them in prose. When the user requests a label transformation, apply it while
preserving the correspondence to the source identifier.

## Counts and Grain

- Determine what one source row represents before choosing an aggregate.
- Use `COUNT(*)` for qualifying rows or events, `COUNT(column)` for non-null values,
  `COUNT(DISTINCT key)` for unique entities, and `SUM(quantity)` for additive units.
- Treat distinct-rate metadata as evidence of repetition, not as the metric
  definition. Account for nulls, composite entity keys, duplicate records, and join
  fanout. Investigate an unexpectedly high count before adding `DISTINCT`.

## Existing SQL and Nested Data

- Treat joins, filters, exclusions, entity grain, and denominator logic inherited
  from an existing query as business semantics. Change only what the request or
  verified metadata requires; do not silently simplify them.
- Verify each nested column's type before access or expansion. Dot notation is not
  interchangeable across structures, arrays, and maps; use only syntax verified for
  the exact CognitiveDB type and preserve the parent row grain unless expansion is
  intentional.

## Ranking and Requested Output

- For global Top-K, prefer an ordered aggregate with a bounded limit. Use a window
  rank when ranking within groups, returning rank, or applying explicit tie semantics.
- Use `ROW_NUMBER` for unique positions, `RANK` for shared ranks with gaps, and
  `DENSE_RANK` for shared ranks without gaps. Add a deterministic tie-breaker when
  unique ordering is required.
- Interpret rank from the metric definition, sort direction, and returned values together. Preserve numerical ordering when values are negative, and ensure labels such as highest, lowest, greatest loss, or smallest loss agree with the ordered result.
- Return the requested winner, Top-K rows, comparison, or rank rather than extra
  alternatives, while retaining the metric and scope needed to substantiate it.

## Evidence and Result Interpretation

- Keep observed query results, supported interpretations, and unverified hypotheses distinct. Prose, tables, and visualizations must agree on metric direction, scope, units, signs, ordering, and qualifiers.
- Do not infer a data-quality defect or systemic anomaly from an aggregate, extreme
  value, sign, apparent boundary, or unusual distribution alone. Require a verified
  constraint, complete population test, lineage evidence, or relevant baseline.
- Do not infer a cause or business condition from an observed association alone;
  require evidence appropriate to that claim.
- When evidence supports the requested result but not an explanation, report the
  result and the unverified limitation without promoting the hypothesis to a finding.

## Time Comparisons and Boundaries

- Separate the calculation input range from the displayed range. Include every
  required baseline period; year-over-year outputs beginning in one period require
  the preceding comparable period as input.
- Compare like-for-like complete or explicitly partial periods. Treat a missing period
  as zero only when the metric definition and complete eligible time population
  establish zero activity. State when a zero or negative baseline makes growth
  undefined or requires a domain-specific interpretation.
- Resolve timezone, date versus timestamp grain, boundary inclusion, and whether the
  current partial period belongs in the result. Prefer half-open timestamp intervals
  when they express the requested boundary without end-of-period precision issues.

## Averages Across Groups

- For "average metric per X per Y," first calculate the metric at `(X, Y)` grain,
  then average across the intended X population for each Y.
- Distinguish observed X members from all eligible X members. When zero-activity
  members belong in the denominator, construct the complete eligible population and
  retain their zero-valued groups before averaging.

## Trailing and Rolling Windows

- Aggregate to one row per requested time grain before applying a time window when
  the source contains multiple rows at that grain.
- A `ROWS` frame counts ordered observations, not elapsed time. Use it for a trailing
  number of observations. For a calendar duration, represent missing periods or use
  a verified interval-based frame so gaps do not lengthen the effective window.

## Ratios, Percentages, and Growth

- Define the numerator, denominator, treatment of nulls and zero denominators, and
  whether the result unit is a fraction or percentage before calculation.
- Prefer domain definitions and metadata over names such as `pct` or `rate`; inspect
  representative values only as supporting evidence. Do not rescale an existing
  percentage without verified unit semantics.
- Guard zero denominators and preserve intermediate precision in SQL or in a
  deterministic calculation meeting SKILL.md result-reuse conditions. Apply percentage
  scaling once and round only for final output.

## Distributions

- Identify the metric and its grain before describing its distribution. When the
  metric is itself an aggregate, compute one value per observation group first.
- For numerical metrics, choose summary statistics, quantiles, or bins according to
  the question; include population and null coverage needed to interpret them. For
  categorical metrics, report frequencies and, when useful, shares while bounding
  high-cardinality output.
- Do not substitute a list of individual values for a requested distribution, or
  force summary statistics when the user requested a histogram, bins, or raw values.
  Use only statistical functions whose CognitiveDB signatures are verified.
