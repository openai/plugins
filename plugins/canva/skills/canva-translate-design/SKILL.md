---
name: canva-translate-design
description: Translate the text in a Canva design into another language while preserving the original layout as much as possible. Use when the user wants a localized or translated version of an existing Canva design and expects the original file to remain unchanged.
---

# Canva Translate Design

## Overview

Use this skill to create a translated copy of an existing Canva design. Find the source design, duplicate it safely, translate text elements into the target language, and save the localized version only after the user approves.

## Preferred Deliverables

- A translated copy of the original Canva design in the requested language.
- A concise note about any text-length or layout risks introduced by translation.
- A final Canva link to the saved translated design.

## Workflow

1. Locate the design from a Canva URL or by searching for its title. If multiple matches appear, identify the right design before continuing.
2. Create a copy of the design so the original stays untouched.
3. Start an editing transaction on the copied design and gather the text elements that need translation.
4. Translate each text element into the requested language while preserving meaning, line breaks, and important formatting cues.
5. Apply the translated text in a single batched edit when possible, and update the design title to reflect the target language.
6. Show the translated preview or summarize the pending result, ask for approval to save, then commit the transaction and return the new design link.

## Write Safety

- Always work on a copy rather than the original design.
- Preserve proper nouns, product names, and brand language unless the user asks for deeper localization.
- Warn the user when translation is likely to expand text enough to require layout cleanup in Canva.
- Treat the final save as an explicit action that follows user approval.

## Output Conventions

- State the source design and target language up front.
- Call out any translation assumptions, especially around brand names or ambiguous phrases.
- Mention likely layout risks before the final save when text expansion is significant.
- Return the saved translated design link after commit.

## Example Requests

- "Translate my Canva poster into Spanish."
- "Make a French version of this design."
- "Localize this Canva design for German."
- "Create a Portuguese copy of this brochure."

## Light Fallback

If the source design cannot be found or opened for editing, say that Canva access may be unavailable or pointed at the wrong account and ask the user to reconnect or identify the exact design to translate.
