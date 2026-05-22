---
name: grammar-of-graphics-and-declarative-visualization
description: Build data visualizations with declarative grammars. Use when the user needs Vega-Lite, Vega, Observable Plot, or grammar-of-graphics reasoning, especially for tabular charts that do not require bespoke rendering.
---

# Grammar of Graphics and Declarative Visualization

## Overview

Use this skill as the default implementation path for many tabular charts. Declarative grammars are often the fastest, clearest, and most maintainable route when the chart can be expressed as data plus marks plus encodings plus transforms.

This skill covers Vega-Lite, Vega, and Observable Plot. Default to the highest-level tool that cleanly expresses the needed chart and interaction.

## Selection Rules

1. Use Observable Plot for fast exploratory and explanatory charts in JavaScript when concise code is valuable.
2. Use Vega-Lite for portable, declarative specs, multi-view composition, transforms, and embed-friendly chart definitions.
3. Use Vega when the user needs lower-level control that still benefits from a declarative runtime.
4. Leave this skill and route to D3, Canvas, or the Three.js/WebGL skill only when the chart requires bespoke layout, extreme density, GPU-scale rendering, particles, true 3D, or rendering control that the grammar no longer expresses cleanly.

## Working Pattern

1. Normalize the table shape.
2. Name the mark, encodings, transforms, faceting, and interaction model explicitly.
3. Choose the highest-level grammar that supports the chart without contortions.
4. Keep specs readable and portable.
5. Check whether the declarative approach still fits the expected number of simultaneous chart instances on the page.
6. Check mobile portrait and optional landscape behavior: responsive spec, label/tick reduction, hover replacement, touch target policy, and whether the grammar can keep the main visualization visible around controls.
7. Use declarative composition before custom code.

## Output Expectations

- Explain why the chosen grammar fits better than bespoke rendering.
- Keep the spec readable enough to be reused, embedded, or translated across stacks.
- Call out when the declarative path is reaching its limits and a lower-level skill should take over.
- Call out whether the grammar can support the mobile concept contract or whether D3, Canvas, WebGL, or framework-owned layout should take over.
- For new work, include a technical design section covering instance-count assumptions, performance implications, and the maintenance upside of staying declarative.

## References

- Shared theory:
  - `../../references/foundations/task-abstraction-and-chart-selection.md`
  - `../../references/foundations/perception-color-and-encoding.md`
  - `../../references/foundations/mobile-first-responsive-visualization.md`
  - `../../references/foundations/implementation-design-and-tradeoffs.md`
- Skill references:
  - `./references/vega-lite-and-vega.md`
  - `./references/observable-plot.md`
  - `./references/when-to-stay-declarative.md`

## Representative Prompts

- "Write a Vega-Lite spec for this dataset."
- "Should I use Plot, Vega-Lite, or D3 for this chart?"
- "Build a layered declarative chart with faceting and tooltips."
- "Tell me when this declarative approach stops being a good fit."
