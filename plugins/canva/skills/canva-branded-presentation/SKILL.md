---
name: canva-branded-presentation
description: Create on-brand Canva presentations from a brief, outline, existing Canva doc, or design link. Use when the user wants a branded slide deck, wants to turn notes into a presentation, or needs a presentation generated in Canva with the right brand kit and a clear slide plan.
---

# Canva Branded Presentation

## Overview

Use this skill to turn a brief, outline, or existing Canva content into a branded presentation. Gather the source content first, choose the right brand kit, and generate presentation candidates before creating the editable deck.

## Preferred Deliverables

- A clear presentation brief with title, scope, key messages, and a narrative arc.
- A slide plan with concrete titles, goals, bullets, and visual guidance.
- A new editable Canva presentation created from the user's preferred candidate.

## Workflow

1. Identify the content source before generating. Accept direct text, a Canva design link, or a Canva document/design name that can be found through search.
2. Read the source content when it lives in Canva. Use the available Canva search and editing tools to locate the design, open it, and extract the material that should drive the deck.
3. List the available brand kits. If there is only one, use it automatically. If there are multiple, ask the user to choose before generating.
4. Build a strong generation prompt. Include a working title, topic, key messages, visual style, story arc, and a slide-by-slide plan.
5. Generate presentation candidates in Canva and show the options to the user before creating the final design.
6. Create the editable presentation from the selected candidate and return the Canva link.

## Write Safety

- Keep the original source design untouched unless the user explicitly asks to modify it.
- If multiple matching source designs or brand kits appear, identify the exact one before generating.
- Preserve specific names, dates, metrics, and claims from the source content unless the user asks to change them.
- If the brief is sparse, expand it thoughtfully, but call out major assumptions that shape the narrative.

## Output Conventions

- When helpful, summarize the deck direction before generation: title, audience, key message, and slide count.
- For larger decks, present a concise slide plan before or alongside candidate generation.
- When showing results, distinguish clearly between generated candidates and the final editable deck.
- Return the final Canva design link once the chosen candidate has been created.

## Example Requests

- "Create a branded presentation from this launch outline."
- "Turn this Canva doc into a polished deck using our brand kit."
- "Make an on-brand sales presentation from this brief."
- "Generate a presentation from this Canva design link."

## Light Fallback

If the source design or brand kit cannot be found, say that Canva access may be unavailable or pointed at the wrong account and ask the user to reconnect or identify the right design or brand kit.
