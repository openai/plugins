# Output Format

## Simple vs. Full Response

- **Narrow, specific question** → direct **200-400 word** answer with key findings, top quotes, and sentiment summary.
- **Comprehensive analysis, brand audit, or multi-platform deep dive** → full structured report (**800-1,500 words**).

## Full Report Structure

### 1. Executive Summary

- 2-4 sentence overview: dominant sentiment, strongest signal sources, single most important finding.
- Scope: brand/topic, platforms, time range, total organic posts reviewed.
- Urgent flags: viral complaints, sudden sentiment shifts, reputational risks.

### 2. Sentiment Breakdown

| Platform | Pos | Neu | Neg | Total |
|---|---|---|---|---|
| Reddit | 12 | 5 | 8 | 25 |
| X/Twitter | 9 | 3 | 14 | 26 |
| **Total** | **21** | **8** | **22** | **51** |

- Include percentage breakdown (e.g., *"Overall: 41% Positive, 16% Neutral, 43% Negative"*).
- State whether engagement weighting was applied.

### 3. Key Themes & Evidence

- Identify the most significant themes (typically 3-5, but follow the data).
- For each theme:
  - 1-2 sentence summary
  - 2-4 representative quotes with platform, author, date, and linked URL
  - Sentiment classification and any edge-case flags

### 4. Platform-Specific Insights

- Where sentiment **converges** across platforms — these themes carry the most weight.
- Where sentiment **diverges** (e.g., *"Reddit skews negative on pricing; LinkedIn is neutral-to-positive"*).
- Platform-unique dynamics: viral threads, trending hashtags, influencer-driven spikes.

### 5. Comparative Analysis *(only if user requests brand/competitor comparison)*

- Side-by-side sentiment breakdown per brand.
- Relative strengths and vulnerabilities.
- Shared vs. divergent audience perceptions.

### 6. Recommendations & Next Steps

- 3-5 actionable recommendations, each referencing a specific finding.
- Priority: **High** (urgent/reputational risk), **Medium** (emerging pattern), **Low** (minor opportunity).
- Suggest follow-up research where relevant.

## Formatting Rules

- Use **markdown tables** for all tabular data.
- Use **blockquotes** for direct quotes, always with a linked post URL.
- Keep the report scannable: headers, bullets, bold key takeaways.
- Prioritize high-engagement, representative posts over exhaustive listing.

## Defaults Reference

| Parameter | Default | Override |
|---|---|---|
| Time range | Context-dependent | User-specified |
| Search `limit` (Round 1) | 10 per call | User request |
| Search `limit` (Round 2) | 5 per call | User request |
| Reddit `sort` | `"top"` | `"new"` for time-sensitive |
| Sample target | 20-40 posts | User request |
| Tool call target | 8-15 | Hard cap 20 |
| Theme count | 3-5, data-driven | Fewer if data supports fewer |
| Engagement weighting | Applied (3x/1x/0.5x) | User override |
| Report length (full) | 800-1,500 words | Complexity-dependent |
| Report length (simple) | 200-400 words | — |
