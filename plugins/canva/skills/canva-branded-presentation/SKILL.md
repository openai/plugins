---
name: canva-branded-presentation
description: Create on-brand Canva presentations from an outline or brief. Use when the user asks to create a branded presentation, make an on-brand deck, turn an outline into slides, or generate a presentation from a brief. Input can be text directly in the message, a Canva design ID, a reference to a Canva doc by name, or a Canva design link (e.g., https://www.canva.com/design/...).
---

# Canva Branded Presentation Creator

Create professional, on-brand presentations in Canva from user-provided outlines or briefs.

## Workflow

1. **Get the content source**
   - If the user provides text directly, use that as the outline/brief
   - If the user provides a **Canva design ID** directly (typically starts with `D`, e.g. `DABcd1234ef`), use it as `design_id` with `Canva:start-editing-transaction` to read its contents; **do not** use `Canva:search-designs` for a raw ID
   - If the user provides a Canva design link (e.g., `https://www.canva.com/design/DAG.../...`), extract the design ID from the URL and use `Canva:start-editing-transaction` to read its contents
   - If the user references a Canva doc by name, use `Canva:search-designs` to find it, then `Canva:start-editing-transaction` to read its contents

2. **List available brand kits**
   - Call `Canva:list-brand-kits` to retrieve the user's brand kits
   - If only one brand kit exists, use it automatically without asking
   - If multiple brand kits exist, present the options and ask the user to select one

3. **Generate the presentation**
   - Call `Canva:generate-design` with:
     - `design_type`: "presentation"
     - `brand_kit_id`: the selected brand kit ID
     - `query`: a detailed prompt following the presentation format below
   - Show the generated candidates to the user

4. **Finalize**
   - Ask the user which candidate they prefer
   - Call `Canva:create-design-from-candidate` to create the editable design
   - Provide the user with the link to their new presentation

## Presentation Query Format

Structure the query for `Canva:generate-design` with these sections:

**Presentation Brief**
- Title: working title for the deck
- Topic/Scope: 1-2 lines describing the subject
- Key Messages: 3-5 main takeaways
- Style Guide: tone and imagery style based on the brief

**Narrative Arc**
One paragraph describing the story flow (e.g., Hook → Problem → Solution → Proof → CTA).

**Slide Plan**
For each slide include:
- Slide N — "Exact Title"
- Goal: one sentence on the slide's purpose
- Bullets (3-6): short, parallel phrasing with specifics
- Visuals: explicit recommendation (chart type, diagram, image subject)
- Speaker Notes: 2-4 sentences of narrative detail

## Notes

- If multiple brand kits exist, confirm selection before generating; if only one, use it automatically
- If the outline is sparse, expand it into a complete slide plan with reasonable content
- For briefs (narrative descriptions), extract key points and structure them into slides
- Aim for clear, action-oriented slide titles
- Autofill requires a Canva Enterprise plan
