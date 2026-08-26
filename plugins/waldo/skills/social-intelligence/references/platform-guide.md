# Platform Reference

## Reddit

- `reddit_search_posts`, `reddit_search_comments`, `reddit_search_communities`, `reddit_search_media`, `reddit_get_post`, `scan_reddit_post_page`
- Start with `reddit_search_communities` to discover relevant subreddits, then search within them.
- `reddit_search_comments` searches comment text directly — prefer this over fetching full threads.
- **No `limit` parameter.** Use `sort: "top"` by default (or `sort: "new"` for time-sensitive). Use only first 10 (Round 1) or 5 (Round 2) results.

## Instagram

- `instagram_search_posts`, `instagram_search_users`, `instagram_get_post`, `instagram_get_post_comments`, `instagram_get_posts`, `instagram_get_profile`
- Search works well with hashtags (e.g., `#skinnypop`).

## TikTok

- `tiktok_search_posts`, `tiktok_search_users`, `tiktok_get_post`, `tiktok_get_post_comments`, `tiktok_get_posts`, `tiktok_get_profile`
- Content is almost entirely video — captions are often minimal.
- Sponsored content often includes `#ad`, `#sponsored`.

## X/Twitter

- `twitter_search_posts`, `twitter_search_users`, `twitter_get_post`, `twitter_get_tweet_replies`, `twitter_get_posts`, `twitter_get_profile`
- Best for breaking opinions and real-time reaction.

## Facebook

- `facebook_search_posts`, `facebook_search_users`, `facebook_get_post`, `facebook_get_post_comments`, `facebook_get_posts`, `facebook_get_profile`
- Use `publicPosts: "true"` for publicly visible content.

## LinkedIn

- `linkedin_search_posts`, `linkedin_search_users`, `linkedin_search_companies`, `linkedin_get_post`, `linkedin_get_company`, `linkedin_get_company_posts`, `linkedin_get_profile`
- Best for employer brand, B2B, thought leadership.

## YouTube

- `youtube_search_videos`, `youtube_search_channels`, `youtube_get_post`, `youtube_get_video_details`, `youtube_get_video_comments`, `youtube_get_video_transcript`, `youtube_get_channel_content`
- Transcripts are valuable when titles are vague. Use `youtube_search_video_comments` with `searchTerm` for targeted sentiment.

## Unsupported Platforms

Use `fetch_page` or web search as a fallback and note the reduced data reliability.

## Common Pitfalls

- **X/Twitter**: Usernames must omit the `@` prefix.
- **Facebook**: Date filtering uses `startDate`/`endDate` in `YYYY-MM-DD` format, not `last_n_days`.
- **LinkedIn**: Use `datePosted` for time filtering, not `last_n_days`.
- **Instagram/TikTok**: Hashtag searches work with or without `#` — try both.
- **YouTube**: `youtube_search_video_comments` requires `videoId`, not a URL.
- **All platforms**: `last_n_days` expects an integer, not a string.
- **All platforms (except Reddit)**: Always pass `limit` on search calls.

## Time Filtering Defaults

| Context | Default Range |
|---|---|
| Crisis / breaking event | Last 7 days |
| Campaign / product launch | Last 14 days |
| General brand health | Last 30 days |
| Brand audit / trend analysis | Last 90 days |

## Query Construction

- Keep queries to **5-6 words**, neutral, with synonym variation.
- For hashtag-driven platforms, search with and without the `#` prefix.
- If initial searches return <5 relevant posts per platform, run 1-2 supplemental searches with varied phrasing.

## Content Filtering: Organic Only

Exclude brand-owned, paid/sponsored, and influencer partnership content:
- Check author username/name against the brand.
- Look for disclosure signals: `#ad`, `#sponsored`, `partnership`, `gifted`.
- On Reddit, subreddits matching the brand name are typically brand-owned.
- If uncertain, classify but flag as *"potentially non-organic."*
