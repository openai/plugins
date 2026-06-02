# Color, Contrast, and Redundant Encoding

## What Problem This Solves

This reference keeps charts readable when color alone is unreliable.

## When to Use It

Use this when choosing palettes, highlights, state colors, or comparison encodings.

## Key Takeaways

- Use structured sequential and diverging schemes rather than arbitrary rainbows.
- Add labels, shapes, line styles, or ordering cues when color is carrying important information.
- Check contrast for marks, text, and annotations, not just backgrounds.
- Treat WCAG text contrast and non-text contrast as different checks: normal text should meet at least 4.5:1, large text at least 3:1, and meaningful graphical objects or UI state indicators at least 3:1 against adjacent colors.
- Check adjacent mark contrast when the boundary between marks carries the information, such as stacked bars, choropleth regions, line crossings, network edges, map overlays, or selected outlines.
- Use a color-role ledger so a hue does not mean multiple unrelated things in the same view.
- Pair color with direct labels, symbols, line dash, stroke weight, ordering, position, or small multiples for any state or category that affects interpretation.
- Use high contrast to guide attention to the most important data, selected state, threshold, or annotation; lower the contrast of gridlines, basemaps, inactive series, and background structure.

## Common Mistakes

- Encoding everything in one palette.
- Using subtle contrast differences that disappear in export or projection contexts.
- Making every category saturated and leaving no contrast budget for the key comparison.
- Using red/green, blue/purple, or other hue-only pairs without labels, shape, ordering, or lightness difference.
- Letting selected, warning, forecast, and category colors reuse the same visual role.

## Adjacent Skills

- `../SKILL.md`
- `../../geospatial-and-cartographic-visualization/SKILL.md`

## Source Links

- [ColorBrewer](https://colorbrewer2.org/)
- [W3C WAI: Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)
- [W3C WAI: Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast)
- [W3C WAI: Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)
- [W3C Complex Images Tutorial](https://www.w3.org/WAI/tutorials/images/complex/)
