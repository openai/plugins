# Fidelity Verification

Capture source and destination metadata, resolved variables, and isolated screenshots before slow analysis.

## Structure

- Normalize node IDs and the pasted root's page position.
- Compare root name, type, dimensions, direct children, metadata-tree type counts, visible names and geometry, instance count/status, variables, and library access.
- Do not expand remote instance interiors into a second count tree.

## Visuals

- Render source and destination in isolation at identical dimensions.
- Compare decoded pixels, not PNG file hashes.
- Also compare white-composited renders to separate alpha-container differences from visible differences.
- Use `scripts/compare_pngs.py` for deterministic metrics.
- If raw render sizes differ, inspect its `transparent_bounds_normalized` metrics. Use them only when the structural dimensions match and the removed rows or columns are fully transparent; report both raw bounds and normalized scores.

Classify:

- `exact`: decoded pixels and normalized structure match exactly.
- `native-equivalent`: white-composited similarity is at least 0.999, visible structure/counts/variables match, and differences are limited to hidden metadata or negligible float normalization.
- `failed`: any visible, layout, instance, variable, or library mismatch, or similarity below 0.999.

Report every normalization even for `native-equivalent` so behavior can be tracked.

If teardown is requested, save the evidence, restore and verify the destination immediately, then run offline pixel analysis. This protects cleanup from later timeouts.
