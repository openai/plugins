# Algorithm Selection

## What Problem This Solves

This reference maps common node-link and diagram families to layout algorithms that fit their reading tasks.

## When to Use It

Use this before choosing a library or renderer whenever a prompt is about auto-arranging connected nodes.

## Key Takeaways

- Trees are not just small DAGs. Use tidy tree algorithms for rooted ordered trees and decision trees.
- Most UML-like flow, schema, state, and dependency diagrams are better served by layered layout than by generic force layout.
- Force-directed and stress-based methods are best for undirected exploration when cluster shape or approximate distance matters.
- Port-constrained block diagrams and ERDs need layout engines that understand boxes, ports, and routing constraints, not just node centers.
- Crossing minimization, overlap removal, and edge routing are separate phases. No single algorithm solves all three equally well.

## Recommended Defaults

- Rooted ordered tree or decision tree:
  - Reingold-Tilford or Buchheim-style tidy tree layout.
- DAG, workflow, state machine, dependency graph, class hierarchy, schema dependency:
  - Sugiyama or layered layout.
- Port-aware block diagram, ERD, database schema, circuit-like or actor-like graph:
  - Layered layout plus orthogonal routing and fixed-side or fixed-order ports.
- General undirected network:
  - Stress majorization, Kamada-Kawai, or Fruchterman-Reingold family.
- Large undirected network:
  - Multilevel force layout.
- Root-distance view:
  - Radial or concentric layout.
- Cycle-heavy view where circular order is the point:
  - Circular layout.
- Non-planar graph where minimizing crossings dominates:
  - Planarization-based workflow.

## Selection Heuristics

- If users read top-to-bottom or left-to-right, start with layered layout.
- If users read parent-child depth, start with tree layout.
- If users read neighborhood or cluster proximity, start with force or stress layout.
- If users trace connectors entering specific sides of boxes, require port-aware routing.
- If users compare revisions or edit interactively, prefer stable constrained layout over fresh randomized layout.
- If labels are large and tables are wide, treat node size as input to the algorithm, not a post-layout afterthought.

## Common Mistakes

- Calling a decision tree a network and sending it to force layout.
- Using a layered algorithm but ignoring port order on schemas or block diagrams.
- Packing disconnected components tightly enough to destroy scanability.
- Choosing splines for dense tabular diagrams where orthogonal routing would be easier to trace.

## Adjacent Skills

- `../SKILL.md`
- `../../uml-and-software-architecture-visualization/SKILL.md`

## Source Links

- [Methods for Visual Understanding of Hierarchical System Structures](https://doi.org/10.1109/TSMC.1981.4308636)
- [A Technique for Drawing Directed Graphs](https://doi.org/10.1109/32.221135)
- [Tidier Drawings of Trees](https://reingold.co/tidier-drawings.pdf)
- [Graph drawing by force-directed placement](https://doi.org/10.1002/spe.4380211102)
- [An algorithm for drawing general undirected graphs](https://doi.org/10.1016/0020-0190(89)90102-6)
- [Graph Drawing by Stress Majorization](https://graphviz.org/documentation/GKN04.pdf)
- [ELK Layered](https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-layered.html)
- [Graphviz layout engines](https://graphviz.org/docs/layouts/)
