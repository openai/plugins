# Competitive Analysis Patterns

## Side-by-Side Comparison

Run all brand searches **in parallel**. Compare:
- **Volume**: Number of active ads
- **Platforms**: Where each brand invests
- **Creative formats**: Video vs. static, carousel vs. single image
- **Messaging themes**: Value propositions, CTAs, offers
- **Recency**: Creative refresh frequency
- **Regional presence**: Market targeting differences

## Category Mapping

1. Use `search_web` to identify key players in the category
2. Suggest 3-5 brands and confirm with user
3. Run ad library searches for each **in parallel**
4. Synthesize into comparative view

## Parallel Tool Calling Rules

Batch all independent ad library searches into a single response:
- Searching the same advertiser across Meta, Google, and LinkedIn → 3 parallel calls
- Comparing 3 brands on Meta → 3 parallel calls
- Running advertiser discovery + initial search on different platforms → parallel
- Fetching ad details or creative analysis for multiple ads → all parallel
- Sequential only when one call's output is needed as input (e.g., meta_advertiser_search to get a page ID, then search_meta_ads with that ID)
