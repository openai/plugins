# Image Building Strategy

Use this rule for first-pass Creative Production imagery. It applies before asset-specific polish, deterministic final layout, or review rendering.

## Default Path

First-pass imagery should come from generated routes: prompt packs, templates, subject references, image references, the API-backed image runner, or native Codex ImageGen in the coordinator or bounded Desktop subagents. A first-pass review should show generated or reference-grounded raster imagery that helps the user judge the visual direction.

Do not use SVG, Pillow, HTML, or canvas screenshot-style fake ad fallbacks as first-pass finished visuals. Do not simulate ads, product screens, UI screenshots, product scenes, logos, or photographic routes with hand-composited placeholder art when the user asked to explore image directions.

## Allowed Deterministic Layers

Deterministic rendering is still appropriate when it owns exactness:

- final text, claims, labels, charts, logos, safe zones, dimensions, filenames, and metadata;
- contact sheets, review boards, widgets, and local HTML inspection surfaces;
- selected publish-bound composition after generated or supplied imagery has been chosen;
- explicitly requested wireframes, diagrams, SVG/vector drafting, or exact template exports.

When deterministic layers and generated imagery both matter, generate or preserve the visual base first, then recomposite exact text, chart, logo, and layout layers deterministically.

## UI And Digital Product Imagery

For app, SaaS, dashboard, or UI-first briefs, the product interface should be treated as the proof object. Preserve supplied screenshots, product facts, workflow states, and privacy constraints. If no exact screenshot exists, use prompt-pack routes that make the UI structure and workflow role visible without inventing real customer data, partner marks, private records, or unsupported metrics.

Avoid pretending a hand-built browser mockup or placeholder dashboard is the actual product image. Use deterministic UI composition only when the user explicitly asks for wireframes, exact layout drafting, or publish-bound recomposition after a route is chosen.

## Relationship To Generation Runtime

Before running image generation, follow `openai-api-image-generation.md`. This strategy decides the creative route; the generation contract decides API routing, native worker orchestration, credentials posture, batch format, and artifact handling.
