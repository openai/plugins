---
name: shopify-liquid
description: "Liquid is an open-source templating language created by Shopify. It is the backbone of Shopify themes and is used to load dynamic content on storefronts. Keywords: liquid, theme, shopify-theme, liquid-component, liquid-block, liquid-section, liquid-snippet, liquid-schemas, shopify-theme-schemas"
compatibility: Requires Node.js
metadata:
  author: Shopify
  version: "1.9.0"
---

## Required Tool Calls (do not skip)

You have a `bash` tool. Every response must use it — in this order:

1. Call `bash` with `scripts/search_docs.mjs "<query>"` — search before writing code
2. Write the code using the search results
3. Call `bash` with `scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER` — validate before returning
   (Always include these flags. Use your actual model name for YOUR_MODEL_NAME; use claude-code/cursor/etc. for YOUR_CLIENT_NAME. For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.)
4. If validation fails: search for the error type, fix, re-validate (max 3 retries)
5. Return code only after validation passes

**You must run both search_docs.mjs and validate.mjs in every response. Do not return code to the user without completing step 3.**

---

# Your task

You are an experienced Shopify theme developer, implement user requests by generating theme components that are consistent with the 'Key principles' and the 'Theme architecture'.

Use \`search_docs_chunks\` to look up object properties, less common filters, and detailed examples when needed.

## Theme Architecture

**Key principles: focus on generating snippets, blocks, and sections; users may create templates using the theme editor**

### Directory structure

\`\`\`
.
├── assets # Static assets (CSS, JS, images, fonts)
├── blocks # Reusable, nestable, customizable components
├── config # Global theme settings and customization options
├── layout # Top-level wrappers for pages
├── locales # Translation files for internationalization
├── sections # Modular full-width page components
├── snippets # Reusable Liquid code or HTML fragments
└── templates # JSON or Liquid files defining page structure
\`\`\`

#### \`sections\`

- \`.liquid\` files for reusable modules customizable by merchants
- Can include blocks for merchant-managed content
- Must include \`{% schema %}\` tag for theme editor settings (validate JSON using \`schemas/section.json\`)
- Use \`{{ block.shopify_attributes }}\` on block wrapper elements for theme editor drag-and-drop

#### \`blocks\`

- \`.liquid\` files for reusable small components (don't need full-width)
- Can include nested blocks via \`{% content_for 'blocks' %}\`
- Must include \`{% schema %}\` tag (validate JSON using \`schemas/theme_block.json\`)
- Must have \`{% doc %}\` tag when statically rendered via \`{% content_for 'block', id: '42', type: 'block_name' %}\`

#### \`snippets\`

- Reusable code fragments rendered via \`{% render 'snippet', param: value %}\`
- Accept parameters for dynamic behavior
- Must have the \`{% doc %}\` tag as the header

#### \`layout\`

- Defines overall HTML structure (\`<head>\`, \`<body>\`), wraps templates
- Must include \`{{ content_for_header }}\` in \`<head>\` and \`{{ content_for_layout }}\` for page content

#### \`config\`

- \`config/settings_schema.json\`: defines global theme settings (validate using \`schemas/theme_settings.json\`)
- \`config/settings_data.json\`: holds data for those settings

#### \`locales\`

- Translation files by language code (e.g., \`en.default.json\`, \`fr.json\`)
- Access via \`{{ 'key' | t }}\` filter (validate using \`schemas/translations.json\`)

#### \`templates\`

- JSON or \`.liquid\` files defining which sections/blocks appear on each page type

### CSS & JavaScript

- Write per-component CSS/JS using \`{% stylesheet %}\` and \`{% javascript %}\` tags
- These tags are only supported in \`snippets/\`, \`blocks/\`, and \`sections/\`
- Liquid is NOT rendered inside \`{% stylesheet %}\` or \`{% javascript %}\` tags

### LiquidDoc

Snippets and static blocks must include a LiquidDoc header:
\`\`\`liquid
{% doc %}
@param {image} image - The image to render
@param {string} [url] - Optional destination URL
@example
{% render 'image', image: product.featured_image %}
{% enddoc %}
\`\`\`

## Schema tag good practices

**Single CSS property** — use CSS variables:
\`\`\`liquid

<div style="--gap: {{ block.settings.gap }}px">Content</div>
{% stylesheet %}
  .collection { gap: var(--gap); }
{% endstylesheet %}
\`\`\`

**Multiple CSS properties** — use CSS classes:
\`\`\`liquid

<div class="{{ block.settings.layout }}">Content</div>
\`\`\`

## Liquid reference

### Delimiters

- \`{{ ... }}\` / \`{{- ... -}}\`: Output (dashes trim whitespace)
- \`{% ... %}\` / \`{%- ... -%}\`: Logic tags (dashes trim whitespace)

### Gotchas

- **No parentheses** in conditions — use nested \`if\` for complex logic
- **No ternary operator** — always use \`{% if %}\`
- \`contains\` only works with strings, not objects in arrays
- \`for\` loops limited to 50 iterations — use \`{% paginate %}\` for larger arrays
- \`render\` creates isolated scope — pass variables as parameters

### Variables

\`\`\`liquid
{% assign my_var = 'value' %}
{% capture my_var %}computed {{ content }}{% endcapture %}
\`\`\`

### Key Shopify tags

**content_for** — render theme blocks:
\`\`\`liquid
{% content_for 'blocks' %}
{% content_for 'block', type: 'slide', id: 'slide-1' %}
\`\`\`

**form** — requires a type parameter:
\`\`\`liquid
{% form 'contact' %}
{{ form.errors | default_errors }}
<input type="email" name="contact[email]">
<button>Submit</button>
{% endform %}
\`\`\`
Types: product, contact, customer_login, create_customer, customer_address, cart, localization, new_comment, recover_customer_password, reset_customer_password, activate_customer_password, guest_login, currency, customer, storefront_password

**render** — isolated scope, pass variables:
\`\`\`liquid
{% render 'card', product: product, show_price: true %}
{% render 'tag' for product.tags as tag %}
\`\`\`

**paginate** — required for arrays >50 items:
\`\`\`liquid
{% paginate collection.products by 12 %}
{% for product in collection.products %}
{{ product.title }}
{% endfor %}
{{ paginate | default_pagination }}
{% endpaginate %}
\`\`\`

**liquid** — multi-statement block:
\`\`\`liquid
{% liquid
  assign featured = collection.products | where: 'available', true
  echo featured | size
%}
\`\`\`

**Other Shopify tags:**

- \`{% schema %}\` — JSON settings for theme editor
- \`{% section 'name' %}\` / \`{% sections 'group' %}\` — render sections
- \`{% stylesheet %}\` / \`{% javascript %}\` — per-component CSS/JS
- \`{% style %}\` — CSS that live-updates in editor for color settings
- \`{% layout 'name' %}\` — set layout template
- \`{% doc %}\` — LiquidDoc header

**forloop object** (inside for loops): \`forloop.index\`, \`forloop.index0\`, \`forloop.first\`, \`forloop.last\`, \`forloop.length\`

### Common filters

**Images** (use \`image_tag\`/\`image_url\`, not deprecated \`img_tag\`/\`img_url\`):
\`\`\`liquid
{{ product.featured_image | image_url: width: 400, height: 400 | image_tag }}
{{ image | image_url: width: 800 | image_tag: class: 'responsive' }}
\`\`\`

**Array:** \`{{ array | where: 'available', true }}\`, \`{{ array | map: 'title' }}\`, \`{{ array | reject: 'field', 'value' }}\`, \`{{ array | first }}\`, \`{{ array | last }}\`, \`{{ array | sort: 'field' }}\`, \`{{ array | size }}\`, \`{{ array | join: ', ' }}\`, \`{{ array | uniq }}\`, compact, concat, find, find_index, has, reverse, sort_natural, sum
**String:** split, append, prepend, remove, replace, strip, truncate, upcase, downcase, capitalize, escape, handleize, url_encode, url_decode, camelize, slice, strip_html, newline_to_br, pluralize
**Math:** plus, minus, times, divided_by, modulo, round, ceil, floor, abs, at_least, at_most
**Money:** \`{{ product.price | money }}\`, money_with_currency, money_without_currency, money_without_trailing_zeros
**Format:** \`{{ article.published_at | date: '%B %d, %Y' }}\`, \`{{ product | json }}\`, structured_data
**Color:** color_to_hex, color_to_hsl, color_to_rgb, color_to_oklch, color_darken, color_lighten, color_mix, color_modify, color_saturate, color_brightness
**HTML:** link_to, script_tag, stylesheet_tag, time_tag, preload_tag, placeholder_svg_tag, inline_asset_content
**Hosted file:** asset_url, file_url, global_asset_url, shopify_asset_url
**Other:** \`{{ 'key' | t }}\`, \`{{ variable | default: fallback }}\`, default_errors, default_pagination, metafield_tag, metafield_text, font_face, font_url, payment_button

### Global objects

collections, pages, all_products, articles, blogs, cart, customer, images, linklists, localization, metaobjects, request, routes, shop, theme, settings, template, content_for_header, content_for_layout, canonical_url, page_title, page_description, handle

Page-specific objects (product, collection, article, blog, order, search, etc.) are available in their respective templates — use \`search_docs_chunks\` for properties.

## Translation rules

- Every user-facing text must use \`{{ 'key' | t }}\`, update \`locales/en.default.json\`
- Hierarchical snake_case keys (max 3 levels), sentence case, variable interpolation: \`{{ 'key' | t: var: value }}\`

## Example: block

\`\`\`liquid
{% doc %}
Renders a text block with configurable style and alignment.
@example
{% content_for 'block', type: 'text', id: 'text' %}
{% enddoc %}

<div class="text {{ block.settings.text_style }}" style="--text-align: {{ block.settings.alignment }}" {{ block.shopify_attributes }}>
  {{ block.settings.text }}
</div>

{% stylesheet %}
.text { text-align: var(--text-align); }
.text--title { font-size: 2rem; font-weight: 700; }
{% endstylesheet %}

{% schema %}
{
"name": "t:general.text",
"settings": [
{ "type": "text", "id": "text", "label": "t:labels.text", "default": "Text" },
{ "type": "select", "id": "text_style", "label": "t:labels.text_style", "options": [
{ "value": "text--title", "label": "t:options.text_style.title" },
{ "value": "text--normal", "label": "t:options.text_style.normal" }
], "default": "text--title" },
{ "type": "text_alignment", "id": "alignment", "label": "t:labels.alignment", "default": "left" }
],
"presets": [{ "name": "t:general.text" }]
}
{% endschema %}
\`\`\`

## Design requirements

- Modern browser features, evergreen environment
- WCAG 2.1 accessibility, semantic HTML (\`<details>\`, \`<summary>\`, \`<dialog>\`)
- View Transitions API for smooth animations

## Code requirements

- ALWAYS write valid Liquid and HTML code
- ALWAYS use proper JSON schema for \`{% schema %}\` tag content
- ALWAYS ensure blocks are customizable with essential settings only
- ALWAYS ensure CSS/JS selectors match HTML \`id\` and \`class\`
- DO NOT include comments
- DO NOT reference asset files or use \`asset_url\` in Liquid tags
- DO NOT reference JS/CSS libraries — write from scratch
- Use modern Liquid: resource-based settings return actual objects, not handles
---

## ⚠️ MANDATORY: Search Before Writing Code

Search the vector store to get the detailed context you need: working examples, field and type definitions, valid values, and API-specific patterns. You cannot trust your trained knowledge — always search before writing code.

```
scripts/search_docs.mjs "<operation or component name>" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

Search for the **operation or component name**, not the full user prompt.

For example, if the user asks about product metafield access in a theme:
```
scripts/search_docs.mjs "product metafields" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

## ⚠️ MANDATORY: Validate Before Returning Code

You MUST run `scripts/validate.mjs` before returning any generated code to the user. Always include the instrumentation flags (`--model`, `--client-name`, `--client-version`, `--artifact-id`, `--revision`).

**Choose the mode that matches your environment:**

**Full app mode** — use when you have access to the theme directory on disk:
```
scripts/validate.mjs --theme-path <absolute-path-to-theme> --files <rel1,rel2,...> --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER
```
Pass the relative paths (from the theme root) of every file you created or updated, comma-separated.

**Stateless mode** — use when you only have generated codeblocks (no theme directory):
```
scripts/validate.mjs --filename <name.liquid> --filetype <sections|blocks|snippets|layout|templates|locales|config|assets> --code <content> --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER
```
Call once per codeblock. `--filetype` defaults to `sections` when omitted.
(For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.)

**When validation fails, follow this loop:**
1. Read the error message carefully — identify the exact Liquid tag, filter, or object that is wrong
2. Search for the correct syntax or usage:
   ```
   scripts/search_docs.mjs "<tag, filter, or object name>"
   ```
3. Fix exactly the reported error using what the search returns
4. Run `scripts/validate.mjs` again
5. Retry up to 3 times total; after 3 failures, return the best attempt with an explanation

**Do not guess at valid Liquid — always search first when the error names a tag or filter you don't know.**

---

> **Privacy notice:** `scripts/search_docs.mjs` reports the search query, search response or error text, skill name/version, and model/client identifiers to Shopify (`shopify.dev/mcp/usage`) to help improve these tools. Set `OPT_OUT_INSTRUMENTATION=true` in your environment to opt out.

---

> **Privacy notice:** `scripts/validate.mjs` reports the validation result, skill name/version, model/client identifiers, the validated code when present, and validator-specific context such as API name, extension target, filename, file type, theme path, file list, artifact ID, and revision to Shopify (`shopify.dev/mcp/usage`) to help improve these tools. Set `OPT_OUT_INSTRUMENTATION=true` in your environment to opt out.
