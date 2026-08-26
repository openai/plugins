# Output and Review Memo Templates

Use these templates when delivering written summaries, workbook notes, or pressure-test outputs.

## Build or update summary

### Executive conclusion

- Target:
- Valuation date:
- Selected valuation method:
- Selected multiple range:
- Implied EV / equity value / per-share range:
- Confidence level:
- Bottom-line judgment:

### Peer universe

- Core peers:
- Secondary peers:
- Adjacent/context peers:
- Excluded obvious peers and rationale:
- Main comparability caveats:

### Key assumptions and data sources

- Source hierarchy used:
- Market data date:
- Financial/consensus data date:
- Currency and units:
- LTM/NTM definitions:
- Major normalizations:
- Source gaps:

### Valuation outputs

- Peer median and percentile range:
- Selected range rationale:
- Implied valuation range:
- Sensitivities:
- Premium/discount rationale:

### Risks and diligence gaps

- Data risks:
- Peer risks:
- Business-model risks:
- Accounting/normalization risks:
- Market/regime risks:

### QA status

- Checks completed:
- Issues fixed:
- Unresolved warnings:
- Recommended next steps:
- Deterministic artifact status, if scripts were used:
- Run log:
- Output manifest:

## Pressure-test summary

### Bottom line

State whether the analysis is: ready for senior review, directionally usable with fixes, or not defensible.

### Critical issues

Rank issues by impact on valuation and credibility.

### Peer-set critique

Challenge weak peers, missing peers, and unjustified exclusions.

### Data/model critique

Discuss stale data, inconsistent definitions, hardcodes, formula issues, and missing source support.

### Judgment critique

Assess whether the selected multiple range is supported by fundamentals, not just peer averages.

### Fix plan

List concrete changes by priority:

1. Must fix before use.
2. Should fix for better quality.
3. Nice to have.

## Language examples

Use precise senior-review language:

- "The model is directionally useful, but not yet IC-ready because the Core peer set includes two companies with materially different revenue models and the selected EV/revenue range does not adjust for the target's lower FCF conversion."
- "The target merits a discount to the Core median despite similar growth because retention, gross margin, and capital intensity are weaker than the peer group."
- "The valuation range is too wide to be decision-useful; tighten it around Core peer percentiles and support any premium with specific fundamentals."
- "EV/EBITDA is not the right primary multiple here because EBITDA is negative and the market is valuing the group on growth-adjusted revenue and FCF conversion."
