# Sample prompts

Use these as adaptable recipes, not as permission to invent requirements. Preserve the user's constraints and include only the fields that help.

## Generate a photorealistic scene

```text
Asset type: editorial website image
Primary request: candid photo of an elderly sailor adjusting a net on a small fishing boat
Scene/backdrop: coastal water with soft haze
Style/medium: photorealistic candid photography
Composition/framing: medium close-up, eye-level
Lighting/mood: soft coastal daylight
Materials/textures: weathered skin, worn fabric, salt-worn wood
Constraints: natural color; no studio polish, logo, text, or watermark
```

## Generate a product image

```text
Asset type: ecommerce product hero
Primary request: premium product photo of a matte black shampoo bottle with a minimal label
Scene/backdrop: clean light-gray studio gradient
Composition/framing: centered three-quarter angle with generous padding
Lighting/mood: softbox lighting with controlled shadows
Text (verbatim): "FIELD DAY"
Constraints: render the label exactly once; no other text, logo, or watermark
```

## Generate a UI mockup

```text
Asset type: mobile app screen
Primary request: home screen for a local farmers market with vendors and daily specials
Style/medium: realistic product UI, not concept art
Composition/framing: vertical mobile layout with clear hierarchy
Constraints: practical controls, readable typography, no unrelated logos or watermark
```

## Generate an educational diagram

```text
Asset type: high-school biology handout
Primary request: a diagram titled "Cellular Respiration at a Glance"
Subject: glucose becoming energy through glycolysis, the Krebs cycle, and the electron transport chain
Style/medium: flat scientific diagram with consistent arrows and labels
Composition/framing: landscape layout with generous whitespace
Text (verbatim): "Cellular Respiration at a Glance", "Glucose", "Pyruvate", "ATP", "NADH", "FADH2", "CO2", "O2", "H2O"
Constraints: scientifically plausible; no tiny or extra text; no watermark
```

## Generate a transparent cutout source

```text
Asset type: transparent product cutout
Primary request: a single ceramic mug, fully visible and centered
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background
Composition/framing: crisp silhouette with generous padding
Constraints: uniform background; no green in the subject; no shadow, gradient, texture, floor plane, reflection, text, or watermark
```

After generation, use the parent skill's `scripts/remove_chroma_key.py`. Do not use this recipe for hair, fur, glass, smoke, liquid, translucent materials, reflections, or soft shadows.

## Edit one object

```text
Primary request: replace only the blue mug with a red ceramic mug
Input images: Image 1: edit target
Constraints: change only the mug color and material; preserve framing, hands, table, background, lighting, and every other object
```

## Replace a background

```text
Primary request: replace only the background with a warm sunset sky
Input images: Image 1: edit target
Constraints: preserve the subject, pose, identity, edges, framing, and foreground lighting; add no objects or text
```

## Preserve identity

```text
Primary request: place the same person in a quiet library
Input images: Image 1: identity and pose reference
Constraints: preserve facial features, body proportions, hair, expression, pose, and clothing; change only the environment; no text or watermark
```

## Composite two images

```text
Primary request: place the subject from Image 2 into Image 1
Input images: Image 1: base scene; Image 2: subject to insert
Constraints: match lighting, perspective, scale, focus, and grain; preserve the base framing; add no other elements
```
