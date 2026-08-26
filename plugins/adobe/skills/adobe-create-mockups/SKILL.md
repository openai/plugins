---
name: adobe-create-mockups
description: >
  Use when a user wants to see their logo, design, or sketch on a product or scene mockup — mugs, t-shirts, business cards, hats, phone screens, posters, billboards, or similar. Triggers on "create mockups", "show my logo on products", or any logo upload with a request to visualize it on items.
  Access: 🔐 Signed-In required | Gen AI: ✅ Adobe Firefly via `image_generate` used for design creation, sketch polishing, and mockup scene generation
allowed-tools: adobe_mandatory_init asset_share_link boards_add_items_to_board boards_create_new_board image_generate
license: Apache-2.0
metadata:
  version: 0.1.0
  visibility: public
  surface: [codex]
---

# Create Mockups

Takes a logo sketch, clean logo image, or broader design asset and produces a suite of product mockups styled to a desired brand vibe. The design is always passed to `image_generate` as a reference image — never described in text as a substitute. Uses progressive checkpoints to validate scene direction before committing to the full set.

---

## Tool Reference

| Step | Tool | Notes |
|------|------|-------|
| 0 | `adobe_mandatory_init` | File-handling and routing rules; call first |
| 1 - 5  | `image_generate` | Generate designs from scratch, polish sketches into clean logos with `referenceImage`, and generate mockup scenes with the design as `referenceImage`. See **`image_generate` Call Rules** below. |
| 7 | `boards_create_new_board` | create a Firefly Board and return its `boardId` |
| 7 | `boards_add_items_to_board` | add final mockup images to the Firefly Board |
| 7 | `asset_share_link` | convert the returned Firefly Board `boardId` into a shareable Firefly Board URL |

### `image_generate` Call Rules

- Pass all generation settings inside `options`.
- Use `options.referenceImage: "<designAssetUrl>"` whenever generating from an uploaded or previously generated design.
- Do not combine `referenceImage` with `aspectRatio` or `size`; express the intended composition in the prompt instead.
- Use `outputFileType: "png"` unless the user explicitly requests JPEG.

---

## High-Level Pipeline

1. **Get the design** — If no design was provided, ask to upload or create one from scratch
2. **Brand profile** — Infer brand direction from the design and only ask for missing output choices
3. **Review design** *(sketches and unclear designs only)* — Ask whether to use as-is or polish first; skip for clean digital assets
4. **Pilot mockup** — Generate one mockup to validate scene direction → **get approval before continuing**
5. **Generate remaining mockups** — Complete the full set (max 5 per turn)
6. **Deliver** — Display all mockups inline with iteration options
7. **Firefly Board** — Create a Firefly Board, add the final mockup images, and return the shareable board link

---

## Workflow

### Step 0: Initialize Adobe Tools

Call `adobe_mandatory_init` first. This returns file handling rules and tool routing guidance required for the rest of the workflow.

```json
{ "skill_name": "adobe-create-mockups", "skill_version": "0.1.0" }
```

---

### Step 1: Get the Design

If the user already provided a design asset in their message, skip this step and proceed to Step 2.

If no design was provided:

```
ask_user_question({
  questions: [{
    question: "Do you already have a logo or design, or would you like to create one?",
    header: "Design",
    multiSelect: false,
    options: [
      { label: "Upload my design", description: "I have a logo or design ready to use" },
      { label: "Create a design", description: "Help me design something from scratch" }
    ]
  }]
})
```

- **Upload my design** → User uploads their design. Proceed to Step 2.
- **Create a design** → Ask what they're envisioning (brand name, style, colors, any inspiration). Generate using `image_generate`, show the result, and iterate until they're happy. Use the approved generation URL as `designAssetUrl`. Proceed to Step 2.

```
image_generate({
  options: {
    prompt: "<design generation prompt>",
    aspectRatio: "1:1",
    n: 1,
    promptReasoner: "quality"
  },
  outputFileType: "png"
})
```

---

### Step 2: Brand Profile

#### 2a. Collect inputs

Extract everything you can from the user's message and the design itself. Default to inference over interrogation. Ask only for what's genuinely missing, and prefer a single structured question page over multiple rounds of Q&A.

| Input | How to get it |
|---|---|
| **Design image** | User uploads directly to chat |
| **Brand name** | Infer from filename or message for internal reference only (e.g. labeling outputs). Only treat a name as explicitly provided — and eligible to render as text in mockups — if the user stated it directly in their message. |
| **Brand colors** | Infer from the design if it has clear colors. Otherwise improvise and fall back to neutral tones (`#FFFFFF`, `#111111`, `#E8E4DC`). |
| **Brand vibe** | Infer from the design style and any context clues (e.g. a sleek monogram → Minimal, a bold illustrated character → Playful). Do not ask a dedicated vibe question unless the direction is genuinely ambiguous. |
| **Mockup selection** | If the user already named products, use those. Otherwise ask once using a single structured product picker. If no preference is given, default to a standard set (mug, business card, t-shirt, phone screen). |
| **Aspect ratio** | If the user specified one, use it. If they specified products but not aspect ratio, default to square (`1:1`) or infer a better fit from product type. Only ask when aspect ratio is important and cannot be safely inferred. |

##### Brand vibe reference

| Vibe | Description |
|---|---|
| **Minimal** | Clean white/light backgrounds, generous whitespace, muted palette |
| **Playful** | Bright colors, casual settings, energetic product photography feel |
| **Luxury** | Dark or gold backgrounds, dramatic lighting, premium materials |
| **Bold** | High contrast, strong colors, graphic and commanding |
| **Earthy / Organic** | Natural textures (wood, linen, stone), warm tones, lifestyle feel |
| **Custom** | User describes their own |

If everything is clear from the message and design, skip directly to Step 3 without asking anything.

#### 2b. Product and aspect-ratio intake

Use `ask_user_question` only if the user has **not** already specified which mockups they want. Keep it to a single page that combines product suggestions with aspect-ratio choices.

**Product options must be tailored to the brand.** Infer the most fitting products from the design, brand name, vibe, and any context the user provided. Use the examples below as a guide — not a fixed list:

| Brand type | Good product suggestions |
|---|---|
| Streetwear / skate | Hoodie, snapback, skateboard deck, tote bag, sticker sheet |
| Food / beverage | Coffee mug, takeaway cup, tote bag, apron, business card |
| Kitchenware / home | Plate, mug, tea towel, tote bag, business card |
| Tech / SaaS | Phone screen, laptop sticker, notebook, t-shirt, business card |
| Beauty / wellness | Label/bottle, tote bag, business card, mirror card, poster |
| Creative studio | Poster, business card, notebook, tote bag, phone screen |
| Generic / unclear | Coffee mug, t-shirt, business card, phone screen *(fallback defaults)* |

Always offer 4–5 product options. Tailor the descriptions to feel relevant to the brand. The fallback defaults (mug, t-shirt, business card, phone screen) should only be used when there is genuinely no brand context to work from.

```
ask_user_question({
  questions: [
    {
      question: "Which mockups should I make first?",
      header: "Products",
      multiSelect: true,
      options: [
        // 4-5 brand-appropriate products inferred from context
      ]
    },
    {
      question: "What image shape should I use?",
      header: "Ratio",
      multiSelect: false,
      options: [
        { label: "Square", description: "Best default for most product mockups and portfolios" },
        { label: "Landscape", description: "Better for presentation slides and wider scenes" },
        { label: "Vertical", description: "Better for mobile-first or poster-style layouts" },
        { label: "Auto", description: "Pick the most natural ratio for each mockup automatically" }
      ]
    }
  ]
})
```

Rules:

- If the user already specified products, skip the product question.
- If the user already specified products but not aspect ratio, default to `1:1` unless the product strongly suggests another format.
- For referenced mockups, use the chosen ratio as prompt guidance only (for example, "square studio composition"). Do not pass `aspectRatio` or `size` to `image_generate` when `referenceImage` is present.
- Use `Auto` behavior by default when product type clearly implies a better composition:
  - phone screen / poster → vertical is often more natural
  - billboard / website hero / presentation scene → landscape is often more natural
  - mug / t-shirt / tote / business card → square is usually the safest default
- Do not ask a dedicated brand-vibe picker unless the design and prompt leave the direction genuinely unclear.
- If asking anything in Step 2, keep it to this single structured intake pass.

---

### Step 3: Review the Design

Trigger this checkpoint if **any** of the following are true:

- Visible pencil, pen, or marker strokes
- Paper, notebook, or textured background
- Rough, uneven, or hand-drawn edges
- Watercolor, paint, or brush texture
- Photo of a drawing or physical object
- Low resolution or pixelated rendering
- Incomplete or rough linework

**Skip this step** if the asset clearly shows a finished logo.

```
ask_user_question({
  questions: [{
    question: "Would you like to use this design as-is for mockups, or have me generate a polished logo render from it first?",
    header: "Design",
    multiSelect: false,
    options: [
      { label: "Use as-is", description: "Go straight to mockup generation with this exact artwork" },
      { label: "Polish it first", description: "Create a cleaned-up logo render from this sketch before making mockups" }
    ]
  }]
})
```

- **Use as-is** → Use the uploaded image directly as `designAssetUrl`. Proceed to Step 4.
- **Polish it first** → Generate a polished logo render using `image_generate`. Pass the sketch URL as `options.referenceImage`. Preserve the original concept while cleaning edges, removing paper/pencil texture, and producing a crisp, production-ready result. Omit `aspectRatio` and `size` because `referenceImage` is present. Use the generated URL as `designAssetUrl` and proceed to Step 4. Do not ask follow-up questions unless the user requests specific changes.

```
image_generate({
  options: {
    prompt: "Create a crisp, production-ready logo render from the reference sketch. Preserve the original concept, silhouette, and distinctive marks while removing paper texture, pencil or marker artifacts, rough edges, shadows, and background noise. Keep the result clean and centered on a simple plain background.",
    referenceImage: "<uploadedSketchUrl>",
    n: 1,
    promptReasoner: "quality"
  },
  outputFileType: "png"
})
```

**Skip this step only** if the asset is clearly a finished digital file with no ambiguity.

---

### Step 4: Generate Mockups

#### 4a. Build scene language from brand profile

Before writing any prompts, lock in the following shared constants from the brand profile. Every prompt must use these exact values — do not vary them across mockups:

- **Brand colors** — the hex values inferred or confirmed in Step 2. Use these consistently for backgrounds, surface tints, props, and accents across all scenes.
- **Brand name** — only include text in mockups if the user explicitly provided a name. Never invent or add a brand name, tagline, or any other text.

Use the confirmed brand profile to define visual language for the scenes. Adapt based on the specific brand — don't copy the table verbatim:

| Vibe | Scene language starting point |
|---|---|
| Minimal | Soft studio light, white or pale grey surfaces, clean negative space, no props |
| Playful | Bright saturated backgrounds matching brand colors, casual angles, fun props |
| Luxury | Dark rich-toned surfaces (marble, velvet, dark wood), dramatic directional light, gold accents |
| Bold | Punchy solid-color backgrounds in brand colors, high contrast flat-lay compositions |
| Earthy / Organic | Natural materials (wood, linen, stone, kraft paper), warm diffused light |
| Custom | Derive from the user's description |

#### 4b. Write all prompts before generating anything

For each product, write the mockup prompt before making any tool calls. This ensures visual consistency across the set. **Do not output the prompts to the user — keep them internal.**

**Prompt structure:** Describe the scene and placement — not the design itself. `image_generate` reads the design from `options.referenceImage`.

```
"[surface and background from vibe and brand colors], [product description],
[design placement on product, e.g. 'logo mark on the front face'],
[scale/placement detail, e.g. 'centered, occupying roughly 30% of the face'],
[lighting style], mockup photography, [props or details that fit brand personality].
The logo/design from the reference image must fit naturally on the [product surface] —
sized and positioned as it would appear on a real product, not floating or oversized.
Use the design from the reference image."
```

Always end with *"Use the design from the reference image."* and include the natural-on-surface constraint — this helps the model prioritize `referenceImage` and keeps the design grounded on the product.

**Do not add any text, lettering, brand name, or tagline** to the scene or product unless the user explicitly provided a name in their message. If no name was given, the design from the reference image is the only branding — no additional text of any kind.

#### 4c. Pilot mockup — validate direction before generating the full set

Generate the **first product only**. Always pass `designAssetUrl` as `options.referenceImage`. Do not pass `aspectRatio` or `size` in this call:

```
image_generate({
  options: {
    prompt: "<mockup prompt from 4b>",
    referenceImage: "<designAssetUrl>",
    n: 1,
    promptReasoner: "quality"
  },
  outputFileType: "png"
})
```

Save the output URL as the first mockup URL. Also save any Firefly generation URN or asset ID returned by the tool; use it later for the board if available.

**If the call fails:** Stop. Do not fall back to describing the design in the prompt. Tell the user:

> "Mockup generation isn't working — this may be a platform limitation or an authentication issue. Please check your plan or try re-authenticating."

**Show the pilot mockup and checkpoint:**

```
Here's a pilot [product name] mockup. Does the direction feel right?
- Scene / lighting / surfaces ✓/✗
- Design placement and scale ✓/✗
- Overall vibe ✓/✗

Say the word and I'll generate the rest, or tell me what to adjust first.
```

**Do not generate remaining mockups until the user approves the pilot.**

### 5. Generate remaining mockups

**If the user approved the pilot with no changes:** use the prompts written in Step 4b exactly as-is for all remaining products. Do not rewrite or re-derive them.

**If the user requested changes during the pilot checkpoint:** update all prompts from Step 4b to reflect those changes, then regenerate the entire set — including the pilot product. Do not carry forward the original pilot image; every mockup in the final set should be generated from the same updated prompt language.

Always pass `designAssetUrl` as `options.referenceImage` on every call, and omit `aspectRatio` and `size` on those referenced calls. **Call `image_generate` for all remaining products in parallel — do not call them sequentially.** Issue all calls at once, up to 5 at a time. If rate-limited, reduce batch size and retry the remaining ones together. Track progress in a manifest:

```
mockups = {
  [product_1]: { url: "<outputUrl>", assetId: "<generationUrn-or-assetId-if-returned>" },
  [product_2]: { url: "<outputUrl>", assetId: "<generationUrn-or-assetId-if-returned>" },
  ...
}
```

Do not display any mockups here. Wait until all products are generated, then deliver the full set together in Step 6.

---

### Step 6: Deliver

Display all mockups together in a single delivery — including the pilot. Do not split output across messages or show mockups as they are generated. Wait until the full set is complete, then display everything at once.

#### Iteration options

After delivery, always offer:

```
Want to refine anything?
- Redo a mockup → "Redo the mug with a darker background"
- Try out different vibes → "Try luxury feel instead"
- Add or swap a product → "Add a tote bag" / "Replace the hat with a hoodie"
- Adjust design placement → "Move the logo to the left chest on the shirt"
```

When the user requests a refinement, re-enter the pipeline at the appropriate step using the existing `designAssetUrl` — no need to re-review the design unless they ask.

---

### Step 7: Create Firefly Board

Create a Firefly Board, then add the final mockups to it. Never invent a `boardId`.

```
boards_create_new_board({
  doc_name: "<Brand or project name> mockups"
})
```

Save the returned `boardId`, then add the mockups. Prefer generation IDs/URNs when the generation result provides them:

```
boards_add_items_to_board({
  board_id: "<boardId>",
  items: [
    {
      type: "generationUrn",
      assetIds: [
        "<generationUrn_or_assetId_image1>",
        "<generationUrn_or_assetId_image2>"
      ]
    }
  ]
})
```

If the generation result only provides HTTPS output URLs, use `presignedUrl` instead:

```
boards_add_items_to_board({
  board_id: "<boardId>",
  items: [
    {
      type: "presignedUrl",
      urls: [
        "<outputUrl_image1>",
        "<outputUrl_image2>"
      ]
    }
  ]
})
```

Use one `boards_add_items_to_board` call when there are 1-12 mockups. If there are more than 12, split them into sequential batches and reuse the same `boardId`.

Only include successful mockups. Do not recap or re-display the mockups here. After `boards_add_items_to_board` succeeds, create the user-facing Firefly Board link by calling `asset_share_link` with the returned `boardId` as `assetId`. Do not invent or derive the URL manually.

```json
asset_share_link({
  "assetId": "<boardId>"
})
```

Omit `changeAccess` and `accessLevel` unless the user explicitly asks to change who can access the board. Present the returned `url` as a Markdown link.

```markdown
Your mockups are saved to a Firefly Board: [<board name>](<url>)
```

If `asset_share_link` fails, present the `boardId` and say the board was created but a share link could not be generated.

---

## Error Handling

| Situation | Action |
|---|---|
| No image uploaded | Ask the user to upload their design or sketch |
| `image_generate` fails on the pilot, or fails for every product in a batch | Stop. Flag the limitation clearly. Do not fall back to prompt-based design description. |
| `image_generate` fails for one or more products during the batch (not all) | Skip the failed products, note them explicitly, and deliver the rest. Never skip silently. |
| Rate limit on `image_generate` | Reduce batch size and continue — do not stop or switch tools |
| `boards_create_new_board` fails | Retry once for 503/504/500/502. Do not retry 400/401 without changing the input/auth. If it still fails, note it; inline images in Step 6 are still the deliverable. |
| `boards_add_items_to_board` returns 201 partial success | Treat as success for the added items. Re-send only the failed items after fixing the named cause. |
| `boards_add_items_to_board` fails | Retry once for 503/504. For 404, create a new board and retry once. For 400/401/415, fix the request/auth instead of retrying unchanged. Inline images in Step 6 are still the deliverable. |

---

## Important Constraints

- **Only ask whether to use as-is or polish first for sketches and unclear designs** — skip straight to generation for clean, production-ready digital files
- **Always get pilot approval** before generating the full set
- **Always pass `designAssetUrl` as `options.referenceImage`** on every referenced `image_generate` call — never describe the design in text as a substitute
- **Never pass `aspectRatio` or `size` with `referenceImage`** — include shape/composition requirements in the prompt instead
- **Never silently degrade** — if generation fails, stop and flag rather than falling back to a prompt description
- **Rate limits**: Generate at most 5 images per turn. If rate-limited, reduce batch size and retry.
- The final deliverables are the mockup images — display them inline
- Keep the brand vibe consistent across all prompts — use the same scene language throughout
- **Never output prompts to the user** — prompts are internal working documents only
- **No commentary on quality** — do not comment on logo or mockup quality. Only surface information the user needs (brand analysis, the images, the checkpoint question, the board link, and iteration options).
