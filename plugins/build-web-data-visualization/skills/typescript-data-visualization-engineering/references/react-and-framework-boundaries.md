# React and Framework Boundaries

## What Problem This Solves

This reference keeps React or framework-owned visualization code maintainable.

## When to Use It

Use this when the chart lives inside React or another component framework.

## Key Takeaways

- Let the framework own structure, lifecycle boundaries, and surrounding UI.
- Let D3 or the renderer own math, geometry, and narrowly scoped imperative behavior.
- Keep effects and refs small and explicit.

## Common Mistakes

- Letting D3 and React mutate the same nodes.
- Mixing view model creation with event handlers and DOM updates in one place.

## Adjacent Skills

- `../SKILL.md`
- `../../d3-data-visualization/SKILL.md`

## Source Links

- [D3 API](https://d3js.org/api)
