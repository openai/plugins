# Feed Query Guide

## Signal Feeds

Call `feed_get_items` for each signal feed with:
- **select**: `data.content.text`, `data.content.title`, `data.platform.url`
- **filter.status**: `"published"` (unless user says otherwise)
- **filter**: Add keyword filters when the user provides search terms (e.g., `data.content.text` contains keyword)
- **limit**: 15 (default), up to 20 if needed

Signal feed types: Brand Mentions, Owned Media, Paid Ads, Category News, About Management, Audience Convos, Trending Topics, From Management.

## Insight Feeds

Call `feed_get_items` for each insight feed with:
- **select**: `data.title`, `data.content`, `data.actionableIdeas`
- **filter**: Add keyword filters on `data.content.text` when searching
- **limit**: 15 (default)
- **NEVER** use `startDate` in filter unless explicitly instructed by the user

Insight feed types: Brand Insights, Ideas, Trends Insights.

## Token Budget Management

### Mandatory Constraints

**Always use `select`.** Never return raw feed item objects. Every `feed_get_items` call must include a `select` parameter scoped only to the fields you need.

**Cap results per feed call.** Default to 15 items per feed. May increase to 20. Never exceed 20 without explicit instruction.

**Parallel calls multiply token cost.** Searching 8 signal feeds at 15 items = 120 items. Before launching parallel calls, estimate whether the combined payload fits. If in doubt, reduce per-feed `limit` to 10.

**Keyword searches narrow before you retrieve.** Always apply keywords via `filter` parameter before fetching — do not fetch broadly and filter afterward.

**Progressive retrieval over broad sweeps.** Start with the most relevant 5-7 feeds. Only fan out if initial results are insufficient.

### Escalation Pattern

If a query requires a broad sweep and risks exceeding budget:
1. Reduce `limit` to 10 per feed
2. Tighten `select` to only 3-5 fields
3. Run the most targeted feeds first, stop when sufficient signal is found
4. Inform the user if results were limited due to budget constraints

## Citation Instructions

- Always cite signal/insight source URLs from the `data.content.title` and `data.platform.url` fields
- Format: `[[Source Name]](URL)`
- ALWAYS verify valid source name and URL. Retry `feed_get_items` if needed.
- NEVER fabricate source names or URLs.
- If search results contain no relevant information, say so plainly with no citations.
