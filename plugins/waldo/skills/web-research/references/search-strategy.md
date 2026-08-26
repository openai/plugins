# Search Strategy

## Complexity Assessment

Classify every task before starting. This sets your minimum effort.

### Simple Search (2-5 tool calls)

Factual queries answerable with one or two authoritative sources.

Signals:
- Real-time data or frequently changing info (prices, rates, weather)
- A single definitive answer from one primary source
- Specific facts, figures, or binary yes/no questions
- Unknown terms you need to look up

### Research (5-20 tool calls)

Multi-source queries requiring comparison, validation, or synthesis.

Signals:
- Words like "deep dive," "comprehensive," "analyze," "evaluate," "compare"
- Multiple perspectives or data points needed
- Strategy, competitive analysis, or multi-faceted evaluation

Scale within the range by difficulty.

### Minimum cycles before stopping

| Category | Min cycles | Min tool calls |
|---|---|---|
| Simple Search | 1-2 | 2-5 |
| Research | 3-6 | 5-20 |

These are floors, not ceilings. At ~15 tool calls, begin wrapping up. If you genuinely cannot find good results, you must have attempted at least 10 meaningfully different searches across 3+ angles before concluding.

## Query Construction

- Keep queries concise: 1-6 words. Start broad, then narrow.
- Every query must be meaningfully different from prior queries. Never repeat.
- If initial results are thin, reformulate from a new angle -- do not just append words.
- Do not use `-`, `site:`, or quotation marks unless the user explicitly requested them.
- Use search parameters for freshness, not query text. Do not use the 'date range' param, only day, week, month allowed.
- For "today" queries, use the word "today" rather than the calendar date.

## Angle Diversity (when results are thin)

When EVALUATE reveals gaps, vary your approach:
- **Synonyms and alternative terminology** -- different words for the same concept.
- **Opposite direction** -- if searching benefits fails, search criticisms.
- **Named experts** -- specific people, authors, or organizations in the space.
- **Industry vs. general terms** -- technical jargon vs. plain language.
- **Adjacent topics** -- upstream or related topics that would contain the answer indirectly.
- **Specific data sources** -- SEC filings, census data, industry reports, company blogs.

## Source Evaluation

Prioritize sources in this order:

1. **Original sources** -- company blogs, official press releases, government sites, SEC filings, peer-reviewed papers, published reports.
2. **Quality journalism** -- established publications with original reporting.
3. **Aggregators and secondary sources** -- only when originals are not available.
4. **Forums and social posts** -- only when specifically relevant (sentiment, niche product feedback).

For evolving topics, favor sources from the last 1-3 months. Lead with the most recent information.

When sources conflict, note the conflict and present both sides. Many high-quality original sources are PDFs -- use `fetch_and_analyze_pdf` for these. Do not skip a strong source because it is a PDF.
