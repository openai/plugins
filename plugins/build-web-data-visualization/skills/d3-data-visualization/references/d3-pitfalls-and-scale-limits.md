# D3 Pitfalls and Scale Limits

## What Problem This Solves

This reference helps recognize when D3 is no longer the right default.

## When to Use It

Use this when the chart is becoming slow, the DOM is exploding, or the code is carrying more rendering responsibility than necessary.

## Key Takeaways

- D3 is excellent for bespoke charts but not ideal for every density or redraw problem.
- When DOM count and frame budget become limiting, move the marks to Canvas or WebGL and keep D3 for math where appropriate.
- Some chart problems are better solved declaratively or with product-oriented libraries.

## Common Mistakes

- Treating D3 flexibility as proof that it is still the right abstraction.
- Ignoring the cost of large DOM trees and repeated layout work.

## Adjacent Skills

- `../SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`

## Source Links

- [D3 API](https://d3js.org/api)
