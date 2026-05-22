# Layered, Tree, Force, and Radial Layouts

## What Problem This Solves

This reference explains the major layout families that matter most in practice for line-connected diagrams.

## When to Use It

Use this when choosing among layered, tree, force-directed, stress, radial, circular, or multilevel layouts.

## Layered Layouts

- The Sugiyama framework remains the default for directional diagrams because it separates cycle breaking, layer assignment, crossing minimization, node placement, and edge routing.
- Gansner, Koutsofios, North, and Vo operationalized this into a practical four-pass directed-graph pipeline using network simplex for rank assignment, heuristic rank ordering to reduce crossings, coordinate assignment, and spline routing.
- Layered layout is the best default for state machines, dependency maps, workflows, class hierarchies, ERDs, and most UML-like directed diagrams.
- Crossing reduction inside layered layouts is hard in the general case, so practical systems rely on heuristics such as barycenter, median, layer sweeps, greedy switches, and local transpositions.
- For constrained two-level crossing reduction, simple heuristics based on barycenter remain important because the problem is NP-hard and practical implementations need speed.

## Tree Layouts

- Reingold and Tilford introduced tidy tree drawing that preserves level alignment, child order, parental centering, and mirror symmetry.
- Their subtree-composition approach is the right default for decision trees and rooted trees because it preserves the tree metaphor instead of approximating it through physics.
- Buchheim, Junger, and Leipert corrected Walker-style assumptions and gave a linear-time refinement that preserves the same family of tidy layouts for trees of unbounded degree.

## Force and Stress Layouts

- Kamada-Kawai formulates layout as an energy minimization based on graph-theoretic distances and is useful for small undirected graphs.
- Fruchterman-Reingold is a classic force-directed heuristic that aims for uniform edge lengths with intuitive attractive and repulsive forces.
- Stress majorization is generally more stable than steepest-descent Kamada-Kawai for stress-based layouts and is the basis of Graphviz `neato`.
- Multilevel force methods scale better for large undirected graphs and are the basis of Graphviz `sfdp`.
- These layouts are strongest when cluster structure, relative proximity, or neighborhood exploration matter more than a single global direction.

## Radial and Circular Layouts

- Radial layout is appropriate when the key story is distance from a chosen root or center.
- Circular layout is appropriate when cycles, ring structure, or repeated ordering around a hub matter more than hierarchy.
- Do not use radial or circular layouts just to make a dense graph look novel; they should earn their geometry semantically.

## Common Mistakes

- Using force layout for flowcharts, schemas, or state machines.
- Using a layered layout for undirected social or similarity networks where artificial direction would mislead.
- Using radial layout when labels are long and the angle of reading becomes the main problem.
- Treating multilevel force layout as a cure for density instead of adding filtering and alternate views.

## Adjacent Skills

- `../SKILL.md`
- `../../uml-and-software-architecture-visualization/SKILL.md`

## Source Links

- [Methods for Visual Understanding of Hierarchical System Structures](https://doi.org/10.1109/TSMC.1981.4308636)
- [A Technique for Drawing Directed Graphs](https://doi.org/10.1109/32.221135)
- [Simple and Efficient Bilayer Cross Counting](https://doi.org/10.7155/jgaa.00088)
- [A Fast and Simple Heuristic for Constrained Two-Level Crossing Reduction](https://michael.forster.pro/publication/constrained-crossing-reduction/)
- [Tidier Drawings of Trees](https://reingold.co/tidier-drawings.pdf)
- [Improving Walker's Algorithm to Run in Linear Time](https://doi.org/10.1007/3-540-36151-0_32)
- [An algorithm for drawing general undirected graphs](https://doi.org/10.1016/0020-0190(89)90102-6)
- [Graph drawing by force-directed placement](https://doi.org/10.1002/spe.4380211102)
- [Graph Drawing by Stress Majorization](https://graphviz.org/documentation/GKN04.pdf)
- [Graphviz `dot`](https://graphviz.org/docs/layouts/dot/)
- [Graphviz `neato`](https://graphviz.org/docs/layouts/neato/)
- [Graphviz `fdp`](https://graphviz.org/docs/layouts/fdp/)
- [Graphviz `sfdp`](https://graphviz.org/docs/layouts/sfdp/)
- [Graphviz `twopi`](https://graphviz.org/docs/layouts/twopi/)
