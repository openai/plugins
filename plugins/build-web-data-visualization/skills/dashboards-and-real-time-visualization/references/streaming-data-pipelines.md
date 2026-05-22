# Streaming Data Pipelines

## What Problem This Solves

This reference covers the data-side assumptions that shape real-time visuals.

## When to Use It

Use this when a chart is fed by append-only streams, polling, or bursty event traffic.

## Key Takeaways

- Know whether the data arrives as stream, snapshot, or hybrid.
- Handle late, missing, and out-of-order events intentionally.
- Aggregate and decimate before sending every raw event to the renderer.
- On mobile and spotty networks, preserve the last known good view, show stale/live/offline/partial state, and reconnect with backoff instead of blanking the chart.
- Treat browser network signals as hints. The server/feed protocol still needs explicit cursors, retry, snapshot repair, and stale state semantics when accuracy matters.

## Common Mistakes

- Assuming event arrival order equals event time.
- Treating raw throughput as proof of better fidelity.
- Hiding connection failure behind a spinner that erases the operational context users were monitoring.

## Adjacent Skills

- `../SKILL.md`
- `../../canvas2d-data-visualization/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [MDN: Navigator.onLine](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine)
- [MDN: NetworkInformation](https://developer.mozilla.org/en-US/docs/Web/API/NetworkInformation)
