# Routing, Overlap, and Quality

## What Problem This Solves

This reference covers the layout phases that often determine whether a diagram is merely valid or actually readable: routing, overlap removal, constraints, and QA.

## When to Use It

Use this after the main layout family is chosen and before declaring a node-link diagram done.

## Edge Routing

- Orthogonal routing is a strong default for ERDs, database schemas, state machines, block diagrams, and port-aware system diagrams because it creates clearer entry and exit directions at boxes.
- ELK Layered explicitly supports orthogonal routing with arbitrary port constraints, which makes it a strong choice for block diagrams and circuit-like schematics.
- If users manually place nodes and only need connectors recomputed, use a dedicated router rather than relaying out the nodes. ELK's Libavoid integration exists for this exact need.
- Spline routing can improve static appearance, but it is weaker when users need to trace crowded connectors precisely.

## Crossing Reduction and Planarization

- Crossing reduction is central to readable layered drawings and remains heuristic-heavy in practice because the general problem is hard.
- Purchase's user study found that reducing edge crossings is by far the most important aesthetic for human understanding, ahead of bend minimization and symmetry.
- When the graph is not planar and crossings dominate readability, planarization is still one of the strongest heuristic families for finding good practical solutions.

## Overlap Removal

- Node overlap removal is a distinct problem from node layout. Treat it as an explicit pass when the chosen layout engine starts from point nodes or weak size assumptions.
- Gansner and Hu propose a proximity-preserving approach that aims to retain layout shape while adding as little area as possible.
- Graphviz exposes multiple overlap-removal modes, including Prism and VPSC-style displacement minimization.
- Overlap removal should preserve the user's mental map as much as possible; otherwise the cure becomes worse than the disease.

## Constraint Support

- Ports matter. Fixed side, fixed order, and fixed position constraints are essential for schemas, block diagrams, and many editable node-link tools.
- Preserve model order when the source semantics imply a meaningful ordering of fields, states, or connectors.
- If the tool must support partial manual placement, use constrained or interactive modes rather than fully recomputing from scratch.

## Quality Checklist

- Crossings are low enough for the diagram's task.
- Bends are limited and do not produce unnecessary doglegs.
- Connector labels never sit under nodes or tables.
- Foreign-key and dependency connectors do not run through table bodies or text blocks.
- Directionality remains obvious after routing.
- Layout remains stable across small edits.
- On narrow screens, the fallback is scrolling, filtering, or faceting rather than illegible scaling.

## Common Mistakes

- Choosing a good layered algorithm and then letting edge routing destroy the reading path.
- Removing overlap by large uniform scaling when a proximity-preserving method is available.
- Ignoring port constraints on tables, lanes, or block diagrams.
- Evaluating layout only by visual taste instead of task performance.

## Adjacent Skills

- `../SKILL.md`
- `../../uml-and-software-architecture-visualization/SKILL.md`
- `../../testing-data-visualizations/SKILL.md`

## Source Links

- [Which aesthetic has the greatest effect on human understanding?](https://doi.org/10.1007/3-540-63938-1_67)
- [On Embedding a Graph in the Grid with the Minimum Number of Bends](https://doi.org/10.1137/0216030)
- [Advances in the Planarization Method: Effective Multiple Edge Insertions](https://doi.org/10.7155/jgaa.00264)
- [How to Draw a Planarization](https://doi.org/10.7155/jgaa.00506)
- [Efficient, Proximity-Preserving Node Overlap Removal](https://doi.org/10.7155/jgaa.00198)
- [Node Overlap Removal Algorithms: an Extended Comparative Study](https://doi.org/10.7155/jgaa.00532)
- [ELK Layered](https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-layered.html)
- [ELK port constraints](https://eclipse.dev/elk/reference/options/org-eclipse-elk-portConstraints.html)
- [ELK crossing minimization strategy](https://eclipse.dev/elk/reference/options/org-eclipse-elk-layered-crossingMinimization-strategy.html)
- [ELK Libavoid routing](https://eclipse.dev/elk/blog/posts/2022/22-11-17-libavoid.html)
- [Graphviz overlap removal](https://graphviz.org/docs/attrs/overlap/)
