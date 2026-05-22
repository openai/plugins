# D3, Canvas, and Grammar Tools in React

## What Problem This Solves

This reference helps choose and integrate the actual visualization layer inside a React component tree.

## When to Use It

Use this when embedding D3, Canvas, Observable Plot, Vega-Lite, or other renderers into React.

## Key Takeaways

- React should usually own the container and surrounding controls.
- D3 should own math and narrowly scoped DOM behavior, not the whole subtree.
- Canvas and WebGL integrations should isolate imperative drawing behind a stable component boundary.
- Grammar-based embeds are often the simplest option for many product charts.

## Common Mistakes

- Letting React and D3 mutate the same nodes.
- Rebuilding heavy chart runtimes unnecessarily on every render.
- Choosing bespoke rendering when a declarative embed would satisfy the product need.

## Adjacent Skills

- `../SKILL.md`
- `../../d3-data-visualization/SKILL.md`
- `../../grammar-of-graphics-and-declarative-visualization/SKILL.md`

## Source Links

- [D3 API](https://d3js.org/api)
- [Observable Plot](https://observablehq.com/plot/what-is-plot)
- [Vega-Lite](https://vega.github.io/vega-lite/)
