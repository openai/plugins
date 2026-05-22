# Choropleths, Symbols, and Flows

## What Problem This Solves

This reference helps choose the right family of map encodings once a map is justified.

## When to Use It

Use this when the data is geospatial and the next step is to choose the map form.

## Key Takeaways

- Use choropleths for normalized area-based magnitude.
- Use symbol maps when precise location or point-specific magnitude matters.
- Use clustered symbol maps when point density is high enough that individual symbols stop being legible at the current scale.
- Use flow maps only when movement or directional transfer is the real story.
- Consider hex or tile summaries when small-area shapes are too noisy.
- Choose point overlap behavior intentionally: clustered summaries for dense previews, displacement or spiderfying for small low-count overlaps, and exact-location anchor dots when large point symbols need to keep their true centers visible.

## Common Mistakes

- Using choropleths for raw counts.
- Placing too many proportional symbols without overlap strategy.
- Using large proportional or halo-style point symbols without a visible center mark.
- Applying displacement to large dense point sets that should be summarized instead.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`

## Source Links

- [ColorBrewer](https://colorbrewer2.org/)
