---
name: canva-translate-design
description: Translate all text in a Canva design to another language, creating a translated copy. Faster than manually copying and editing each text box in Canva's editor. Use when users say "translate my design to [language]", "make a Spanish/French/etc version", or "localize my Canva design".
---

# Canva Translate

Translate all text elements in a Canva design to a target language, creating a new copy with translated content.

## Workflow

### 1. Locate the Design

If user provides a **design ID** directly (typically starts with `D`, e.g. `DABcd1234ef`), use that as the design identifier; **do not** pass it to `Canva:search-designs` (search is for titles, not IDs).

If user provides a **URL**: Extract the design ID from the URL (format: `https://www.canva.com/design/{design_id}/...`).

If user provides a **name**: Use `Canva:search-designs` to find the design by title. If multiple matches, ask user to clarify.

### 2. Create a Translated Copy

Use `Canva:resize-design` with the same dimensions to create a copy. This preserves the original design untouched.

### 3. Start Editing Transaction

Use `Canva:start-editing-transaction` on the new copy to get:
- `transaction_id` for making edits
- All text elements with their `element_id` and current text content

### 4. Translate Text

For each text element returned:
1. Translate the text to the target language (use Claude's translation capability)
2. Preserve formatting cues (line breaks, emphasis patterns)
3. Keep proper nouns, brand names, and technical terms as appropriate

### 5. Apply Translations

Use `Canva:perform-editing-operations` with `replace_text` operations for all translated elements. Batch all replacements in a single call.

Also update the design title to indicate the language (e.g., append " (Spanish)" or use translated title).

### 6. Commit Changes

After showing the user the translated preview thumbnail:
1. Ask for explicit approval to save
2. Use `Canva:commit-editing-transaction` to finalize
3. Provide the link to the new translated design

## Example Interaction

**User**: Translate my "Summer Sale Poster" to French

**Steps**:
1. Search: `Canva:search-designs` with query "Summer Sale Poster"
2. Copy: `Canva:resize-design` to create duplicate
3. Edit: `Canva:start-editing-transaction` on copy
4. Translate all text elements to French
5. Apply: `Canva:perform-editing-operations` with all `replace_text` operations
6. Show preview, get approval, commit

## Important Notes

- Always create a copy—never modify the original design
- Batch all text replacements in one `perform-editing-operations` call for efficiency
- If translation significantly changes text length, warn user that layout adjustments may be needed in Canva
- For designs with many pages, translate all pages in the same transaction
