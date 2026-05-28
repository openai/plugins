# Performance and Degradation

## What Problem This Solves

This reference defines how live systems stay usable as rate, volume, and interaction pressure increase.

## When to Use It

Use this when designing or triaging performance-sensitive dashboards.

## Key Takeaways

- Set frame, memory, and network budgets up front.
- Degrade gracefully through aggregation, lower-frequency updates, culling, or narrower time windows.
- Make degraded state visible rather than silently dropping fidelity.
- For mobile, budget battery, thermal pressure, device pixel ratio, GPU memory, bundle weight, and bandwidth.
- Pause or lower quality for offscreen, backgrounded, reduced-motion, low-power, or low-bandwidth states.

## Common Mistakes

- Pretending the user still sees all signal after aggressive decimation without disclosure.
- Measuring only idle cases and not burst behavior.
- Profiling only desktop hardware and missing mobile browser chrome, keyboard, orientation, and thermal behavior.

## Adjacent Skills

- `../SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [deck.gl docs](https://deck.gl/docs)
