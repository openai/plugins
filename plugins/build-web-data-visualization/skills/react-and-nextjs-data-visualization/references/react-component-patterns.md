# React Component Patterns

## What Problem This Solves

This reference defines the core ownership model for charts inside React applications.

## When to Use It

Use this when the user is deciding how a chart component should be structured or where chart state should live.

## Key Takeaways

- Let React own layout, controls, and application state.
- Keep the chart render layer narrow: props in, marks out.
- Use refs for imperative integration points and keep effects scoped to chart lifecycle work.
- Separate data fetching, data shaping, configuration, and rendering concerns.

## Common Mistakes

- Letting chart code own surrounding UI or product state.
- Mixing data fetching, resize logic, imperative drawing, and tooltip state in one component.

## Adjacent Skills

- `../SKILL.md`
- `../../typescript-data-visualization-engineering/SKILL.md`

## Source Links

- [React useRef](https://react.dev/reference/react/useRef)
- [React synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
