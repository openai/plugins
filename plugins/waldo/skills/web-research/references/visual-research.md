# Visual Research

Use the screenshot pipeline when the task involves analyzing what a webpage looks like -- layout, UI elements, color palette, typography, icons, UX patterns, brand identity, or creative quality.

`fetch_page` returns text content. It cannot tell you about colors, layout, typography, or visual hierarchy.

## The Screenshot Pipeline (3 steps)

1. **Get the URL.** Use `search_web` if you do not already have it.
2. **Capture.** Run `screenshot` on the URL. Returns an image link.
3. **Analyze.** Run `fetch_and_analyze_image` on the screenshot link. This is where you actually see the page.

Each page costs 2-3 tool calls. Budget accordingly.

## Visual Analysis Tips

- Be specific about colors (not "blue" but "navy blue" or "muted teal"), typography (serif vs. sans-serif, weight, hierarchy), and spatial relationships.
- Screenshots capture the visible viewport (above the fold). Mention when relevant content might be below the fold.
- Never describe a page's visual design based on `fetch_page` output or URL alone.
- Always embed screenshot image links in your output: `![Page Name](screenshot_url)`

## Other Visual Tools

- Use `fetch_and_analyze_image` directly (without screenshot) for standalone media: ad creatives, product photos, logos.
- Use `image_search` to find visual references, then `fetch_and_analyze_image` to analyze them.
- Use `screenshot` as a fallback when `fetch_page` fails to return content.
