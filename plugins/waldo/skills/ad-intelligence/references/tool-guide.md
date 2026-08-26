# Ad Library Tool Reference

## Meta — `search_meta_ads`

Required params: `query`, `country`, `category`, `activity_status`.
- **query**: Brand name or product keyword. Keep it short (1-3 words).
- **country**: ISO 2-letter code. Use "ALL" only if user explicitly says global.
- **activity_status**: Use "ACTIVE" for current, "INACTIVE" for ended, "ALL" for both.
- **Optional filters**: `platform`, `media_type`, `start_date`/`end_date`, `language`.

**Advertiser Discovery:**
1. `meta_advertiser_search` or `get_meta_ad_search_auto_fill` to find the page ID
2. `search_meta_ads` with that page ID as `advertiser`
3. `get_meta_ad_details` or `get_meta_ad_summary_details` to drill into specifics

## Google — `search_google_ads`

Requires either `advertiser_id` or `domain`.
- **domain**: Brand's website domain (e.g. "nike.com").
- **time_period**: "today", "last_7_days", "last_30_days", or "YYYY-MM-DD..YYYY-MM-DD".
- **Optional filters**: `ad_format`, `platform`, `region`.

## LinkedIn — `search_linkedin_ads`

Provide at least one of `q` or `advertiser`.
- **country**: ISO 2-letter codes, comma-separated for multiple markets.
- **time_period**: "last_year", "this_year", "this_month", "last_30_days", or "YYYY-MM-DD..YYYY-MM-DD".

## Tool Budget

- 1 call per tool per brand is the default
- Only make a 2nd call if the 1st returns insufficient results — adjust parameters (e.g. broader date range, different filters) on retry
- For multi-brand searches: apply the same 1-default / 2-max rule per tool per brand
- Default settings:
  - search_meta_ads: no constraints (30 max results per call)
  - search_google_ads: num=30
  - search_linkedin_ads: time_period=last_30_days (unless user wants older)
- If more ads are available beyond what was retrieved, tell the user and offer to fetch more

## Creative Analysis

Use `fetch_and_analyze_image` and `fetch_and_analyze_video` when the user asks about visual elements, creative themes, or design patterns.

1. Run the ad search tool first to get results with media URLs
2. Pass media URLs to analysis tools with a descriptive prompt — **batch all analysis calls in parallel**
3. Write prompts specific to the user's question
4. **Budget**: Max 10 ads per batch. Stop, provide the answer, and offer additional batches if needed.

## Citation Formatting

Every specific ad you mention MUST have a citation.

- **Links:** `[[Source Name]](https://adUrl)` — placed after the period at the end of the sentence
- **Images:** `![Source Name](image_url)`
- Only cite URLs from your current search results. Never cite from memory.
- No results? Say so plainly. Do not fabricate citations.
