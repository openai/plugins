# /review-design-parity

Review implemented UI against a Figma design and call out visual/behavioral mismatches.

## Arguments

- `figma_url`: Figma frame/component URL (required)
- `target`: local page/component to review (required)

## Workflow

1. Fetch `get_design_context` + `get_screenshot` for the Figma target.
2. Inspect current implementation and run the relevant local preview/test path.
3. Compare layout, typography, tokens, assets, and interactions.
4. Report findings first, then suggested fixes.

## Output requirements

- Findings ordered by severity
- What evidence was checked (screenshot, local preview, tests)
- Any missing evidence that blocks a full parity judgment
