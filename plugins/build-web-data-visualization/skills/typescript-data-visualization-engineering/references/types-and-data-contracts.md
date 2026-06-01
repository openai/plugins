# Types and Data Contracts

## What Problem This Solves

This reference helps TypeScript charts stay reliable at the boundary between external data and rendering code.

## When to Use It

Use this when modeling datasets, tooltip payloads, selections, filters, or reusable chart APIs.

## Key Takeaways

- Validate external data at the edge.
- Use explicit interfaces for input rows, derived marks, scales, and interaction state.
- Keep tooltip and selection payloads intentional rather than loosely typed.

## Common Mistakes

- Passing raw unvalidated API data directly into render logic.
- Treating chart state as an untyped bag of options.

## Adjacent Skills

- `../SKILL.md`

## Source Links

- [Vega-Lite](https://vega.github.io/vega-lite/)
