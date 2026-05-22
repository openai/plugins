# Perception, Color, and Encoding

## What Problem This Solves

This reference keeps encoding decisions grounded in how people actually read visual marks.

## When to Use It

Use this when deciding scales, color systems, redundancy, label strategy, or whether the main comparison is visually strong enough.

## Key Takeaways

- Position on a common scale is usually the strongest encoding for quantitative comparison.
- Color hue is best for categories; lightness or structured sequential ramps are better for ordered magnitude.
- Color should not carry unique meaning if the visualization also needs to work for color-deficient or grayscale contexts.
- Define color roles before choosing exact colors: neutral context, primary focus, secondary comparison, ordered magnitude, positive/negative change, warning/error, selection, hover/focus, missing/uncertain, and disabled or stale state.
- Do not overload the same hue with unrelated meanings. If blue means selected, it should not also mean forecast, team A, safe, current period, and above target in the same view.
- Use contrast to direct attention. The most important data marks, selected state, insight annotation, and critical threshold should have stronger contrast than gridlines, basemaps, inactive series, and secondary context.
- For meaningful non-text marks and UI state indicators, target at least 3:1 contrast against adjacent colors. For text, target WCAG AA text contrast: at least 4.5:1 for normal text and 3:1 for large text.
- Check contrast between adjacent data marks when the boundary itself carries meaning, not just mark-to-background contrast.
- Prefer perceptually ordered sequential or diverging ramps for magnitude. Avoid rainbow ramps unless the data and audience have a domain-specific convention that justifies them.
- Direct labels usually beat legend lookup when the number of series is manageable.
- If a key is required, keep it inside the visualization or immediately adjacent to the marks it explains.
- For compact views such as in-cell charts and sparklines, use surrounding row or column context plus inline labels instead of detached legends.
- Accessibility and perceptual clarity are linked: redundant encodings, contrast, and legible labeling improve both.
- In editorial figures, neutral context plus one or two purposeful accent hues usually beats assigning a unique hue to every category.
- When a chart needs many categories, look for grouping, direct labeling, small multiples, ordering, or interaction before adding more hues.
- Every glow, pulse, halo, blur, particle, stroke thickness, ring count, shimmer, or animation must have a named data or interaction mapping. If the effect is only "looks good," remove it or demote it so it cannot be confused with data.
- Keep data encodings and interaction encodings visually distinct. If rings encode magnitude, selection should use another shape language such as chevrons, brackets, outlines, or a callout rather than adding more rings.

## Common Mistakes

- Using rainbow ramps for ordered values.
- Reusing one color for unrelated semantics such as category, selection, warning, and forecast.
- Making context as saturated or high contrast as the key evidence.
- Encoding too many variables with weak channels at once.
- Letting labels, legends, and tooltips fight for the same job.
- Parking a legend far from the chart and forcing repeated eye travel to decode the view.
- Using color variety as a substitute for hierarchy.
- Letting decorative glow, particles, or size compete with the encoded value.
- Reusing the same visual channel for both data and selection state.
- Passing text contrast while leaving meaningful marks, focus rings, selected states, or map boundaries too faint to understand.

## Adjacent Skills

- `../../skills/accessibility-and-inclusive-visualization/SKILL.md`
- `../../skills/visualization-strategy-and-critique/SKILL.md`
- `../../skills/geospatial-and-cartographic-visualization/SKILL.md`
- `./editorial-infographic-system.md`

## Source Links

- [ColorBrewer](https://colorbrewer2.org/)
- [W3C WAI: Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)
- [W3C WAI: Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast)
- [W3C WAI: Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)
- [W3C Complex Images Tutorial](https://www.w3.org/WAI/tutorials/images/complex/)
- [Information Visualization: Perception for Design](https://books.apple.com/us/book/information-visualization/id535481998)
