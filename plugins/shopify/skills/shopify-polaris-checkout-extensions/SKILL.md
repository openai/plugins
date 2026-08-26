---
name: shopify-polaris-checkout-extensions
description: "Build custom functionality that merchants can install at defined points in the checkout flow, including product information, shipping, payment, order summary, and Shop Pay. Checkout UI Extensions also supports scaffolding new checkout extensions using Shopify CLI commands."
compatibility: Requires Node.js
metadata:
  author: Shopify
  version: "1.9.1"
---

## Required Tool Calls (do not skip)

You have a `bash` tool. Every response must use it — in this order:

1. Call `bash` with `scripts/search_docs.mjs "<query>"` — search before writing code
2. Write the code using the search results
3. Call `bash` with `scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER --target <extension-target>` — validate before returning
   (Always include these flags. Use your actual model name for YOUR_MODEL_NAME; use claude-code/cursor/etc. for YOUR_CLIENT_NAME. For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.) Pass `--target` with the checkout extension target this code runs in (e.g. `purchase.checkout.block.render`); validation will fail without it.
4. If validation fails: search for the error type, fix, re-validate (max 3 retries)
5. Return code only after validation passes

**You must run both search_docs.mjs and validate.mjs in every response. Do not return code to the user without completing step 3.**

---

You are an assistant that helps Shopify developers write UI Framework code to interact with the latest Shopify polaris-checkout-extensions UI Framework version.

You should find all operations that can help the developer achieve their goal, provide valid UI Framework code along with helpful explanations.
Checkout UI extensions let app developers build custom functionality that merchants can install at defined points in the checkout flow, including product information, shipping, payment, order summary, and Shop Pay.

## Validator constraints

Do not include HTML comments (`<!-- ... -->`) in the code — the validator treats them as invalid custom components.

## IMPORTANT : ALWAYS USE THE CLI TO SCAFFOLD A NEW EXTENSION

Shopify CLI generates templates that aligns with the latest available version and is not prone to errors. ALWAYS use the CLI Command to Scaffold a new Checkout UI extension

CLI Command to Scaffold a new Checkout UI Extension:

```bash
shopify app generate extension --template checkout_ui --name my-checkout-ui-extension
```

version: 2026-01

## Extension Targets (use these in shopify.extension.toml)

Targets decide what components/APIs can be used.
Search the developer documentation for target-specific documentation:

**Address:**

- purchase.address-autocomplete.format-suggestion
- purchase.address-autocomplete.suggest

**Navigation:**

- purchase.checkout.actions.render-before

**Block:**

- purchase.checkout.block.render
- purchase.thank-you.block.render

**Order Summary:**

- purchase.checkout.cart-line-item.render-after
- purchase.checkout.cart-line-list.render-after
- purchase.checkout.reductions.render-after
- purchase.checkout.reductions.render-before
- purchase.thank-you.cart-line-item.render-after
- purchase.thank-you.cart-line-list.render-after

**Information:**

- purchase.checkout.contact.render-after
- purchase.thank-you.customer-information.render-after

**Shipping:**

- purchase.checkout.delivery-address.render-after
- purchase.checkout.delivery-address.render-before
- purchase.checkout.shipping-option-item.details.render
- purchase.checkout.shipping-option-item.render-after
- purchase.checkout.shipping-option-list.render-after
- purchase.checkout.shipping-option-list.render-before

**Footer:**

- purchase.checkout.footer.render-after
- purchase.thank-you.footer.render-after

**Header:**

- purchase.checkout.header.render-after
- purchase.thank-you.header.render-after

**Payments:**

- purchase.checkout.payment-method-list.render-after
- purchase.checkout.payment-method-list.render-before

**Local Pickup:**

- purchase.checkout.pickup-location-list.render-after
- purchase.checkout.pickup-location-list.render-before
- purchase.checkout.pickup-location-option-item.render-after

**Pickup Points:**

- purchase.checkout.pickup-point-list.render-after
- purchase.checkout.pickup-point-list.render-before

**Announcement:**

- purchase.thank-you.announcement.render

## APIs

**Available APIs:** Addresses, Analytics, Attributes, Buyer Identity, Buyer Journey, Cart Instructions, Cart Lines, Checkout Token, Cost, Customer Privacy, Delivery, Discounts, Extension, Gift Cards, Localization, Localized Fields, Metafields, Note, Order, Payments, Storefront API, Session Token, Settings, Shop, Storage

## Guides

**Available guides:** Using Polaris web components, Configuration, Error handling, Upgrading to 2026-01

## Components available for checkout UI extensions.

These examples have all the props available for the component. Some example values for these props are provided.
Refer to the developer documentation to find all valid values for a prop. Ensure the component is available for the target you are using.

```html
<s-abbreviation id="my-id" title="Full title text">USD</s-abbreviation>
<s-announcement>Check our latest offers</s-announcement>
<s-badge color="base" size="base" tone="auto">New</s-badge>
<s-banner heading="Important" tone="auto">Message content</s-banner>
<s-box padding="base" background="transparent">Content</s-box>
<s-button tone="auto" variant="auto" type="button">Click me</s-button>
<s-checkbox label="Accept terms" name="terms"></s-checkbox>
<s-chip>Category</s-chip>
<s-choice-list label="Options" name="options" variant="auto">
  <s-choice value="1">Option 1</s-choice>
  <s-choice value="2">Option 2</s-choice>
</s-choice-list>
<s-clickable href="https://example.com">Click area</s-clickable>
<s-clickable-chip>Removable tag</s-clickable-chip>
<s-clipboard-item text="Copy this text"></s-clipboard-item>
<s-consent-checkbox label="Subscribe to marketing"></s-consent-checkbox>
<s-consent-phone-field label="Phone" name="phone"></s-consent-phone-field>
<s-date-field label="Date" name="date"></s-date-field>
<s-date-picker type="single" name="selectedDate"></s-date-picker>
<s-details><s-summary>More info</s-summary>Hidden content</s-details>
<s-divider direction="inline"></s-divider>
<s-drop-zone label="Upload file" name="file"></s-drop-zone>
<s-email-field label="Email" name="email"></s-email-field>
<s-form
  ><s-text-field label="Name" name="name"></s-text-field
  ><s-button type="submit">Submit</s-button></s-form
>
<s-grid gridTemplateColumns="1fr 1fr" gap="base">
  <s-box>Col 1</s-box>
  <s-box>Col 2</s-box>
</s-grid>
<s-heading>Section Title</s-heading>
<s-icon type="check" size="base"></s-icon>
<s-image src="https://example.com/image.png" alt="Description"></s-image>
<s-link href="https://example.com">Link text</s-link>
<s-map
  latitude="{40.7128}"
  longitude="{-74.006}"
  zoom="{12}"
  apiKey="key"
></s-map>
<s-modal id="my-modal" heading="Title"><s-text>Modal content</s-text></s-modal>
<s-money-field label="Amount" name="amount"></s-money-field>
<s-number-field
  label="Quantity"
  name="qty"
  min="{1}"
  max="{100}"
></s-number-field>
<s-ordered-list
  ><s-list-item>First</s-list-item
  ><s-list-item>Second</s-list-item></s-ordered-list
>
<s-paragraph>Body text content</s-paragraph>
<s-password-field label="Password" name="password"></s-password-field>
<s-payment-icon type="visa"></s-payment-icon>
<s-phone-field label="Phone" name="phone"></s-phone-field>
<s-popover id="pop"><s-text>Popover content</s-text></s-popover>
<s-press-button>Toggle</s-press-button>
<s-product-thumbnail
  src="https://example.com/product.png"
  size="base"
></s-product-thumbnail>
<s-progress value="{0.5}" max="{1}" tone="auto"></s-progress>
<s-qr-code content="https://example.com" size="base"></s-qr-code>
<s-query-container containerName="main">Content</s-query-container>
<s-scroll-box maxBlockSize="200px">Scrollable content</s-scroll-box>
<s-section heading="Section"><s-text>Section content</s-text></s-section>
<s-select label="Choose" name="choice"
  ><s-option value="a">A</s-option><s-option value="b">B</s-option></s-select
>
<s-sheet id="my-sheet" heading="Sheet Title"
  ><s-text>Sheet content</s-text></s-sheet
>
<s-skeleton-paragraph content="Loading..."></s-skeleton-paragraph>
<s-spinner size="base"></s-spinner>
<s-stack direction="inline" gap="base"
  ><s-text>Item 1</s-text><s-text>Item 2</s-text></s-stack
>
<s-switch label="Enable" name="enabled"></s-switch>
<s-text tone="auto">Styled text</s-text>
<s-text-area label="Description" name="desc" rows="{4}"></s-text-area>
<s-text-field label="Name" name="name" placeholder="Enter name"></s-text-field>
<s-time dateTime="2024-01-01">Jan 1, 2024</s-time>
<s-tooltip>Hover for info</s-tooltip>
<s-unordered-list
  ><s-list-item>Item A</s-list-item
  ><s-list-item>Item B</s-list-item></s-unordered-list
>
<s-url-field label="Website" name="url"></s-url-field>
```

## Imports

Use the Preact entry point:

```tsx
import "@shopify/ui-extensions/preact";
import { render } from "preact";
```

### Polaris web components (`s-banner`, `s-badge`, etc.)

Polaris web components are custom HTML elements with an `s-` prefix. These are globally registered and require **no import statement**. Use them directly as JSX tags:

```tsx
// No import needed — s-banner, s-badge, s-button, etc. are globally available
<s-banner tone="warning">Age verification required</s-banner>
<s-badge tone="success">Payment captured</s-badge>
```

When the user asks for Polaris web components (e.g. `s-banner`, `s-badge`, `s-button`, `s-text`), use the web component tag syntax above.

**Web component attribute rules:**

- Use **camelCase** attribute names: `alignItems`, `paddingBlock`, `borderRadius` — NOT kebab-case (`align-items`, `padding-block`)
- **Boolean attributes** (`disabled`, `loading`, `dismissible`, `checked`, `defaultChecked`, `required`, `multiple`) accept shorthand or `{expression}`:
  - ✅ `<s-checkbox checked={includeGift === 'yes'} />`, `<s-button disabled>`, `<s-banner dismissible>`
- **String keyword attributes** (`padding`, `gap`, `direction`, `tone`, `variant`, `size`, `background`, `alignItems`) must be string values — never shorthand or `{true}`:
  - ✅ `<s-box padding="base">`, `<s-stack gap="loose" direction="block">`, `<s-badge tone="success">`
  - ❌ `<s-box padding>`, `<s-stack gap={true}>` — boolean shorthand on string props fails TypeScript
---

## ⚠️ MANDATORY: Search Before Writing Code

Search the vector store to get the detailed context you need: working examples, field and type definitions, valid values, and API-specific patterns. You cannot trust your trained knowledge — always search before writing code.

```
scripts/search_docs.mjs "<component tag name>" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

Search for the **component tag name**, not the full user prompt.

For example, if the user asks about checkout button:
```
scripts/search_docs.mjs "s-button checkout" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

## ⚠️ MANDATORY: Validate Before Returning Code

You MUST run `scripts/validate.mjs` before returning any generated code to the user. Always include the instrumentation flags:

```
scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER --target <extension-target>
```

**`--target` is required for checkout extensions.** Pass the extension target this code runs in (e.g. `purchase.checkout.block.render`). If you don't know which target applies, run `scripts/search_docs.mjs "extension targets"` first to look one up — validation will fail without it.
(For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.)

**When validation fails, follow this loop:**
1. Read the error message carefully — identify the exact field, prop, or value that is wrong
2. If the error references a named type or says a value is not assignable, search for the correct values:
   ```
   scripts/search_docs.mjs "<type or prop name>"
   ```
3. Fix exactly the reported error using what the search returns
4. Run `scripts/validate.mjs` again
5. Retry up to 3 times total; after 3 failures, return the best attempt with an explanation

**Do not guess at valid values — always search first when the error names a type you don't know.**

---

> **Privacy notice:** `scripts/search_docs.mjs` reports the search query, search response or error text, skill name/version, and model/client identifiers to Shopify (`shopify.dev/mcp/usage`) to help improve these tools. Set `OPT_OUT_INSTRUMENTATION=true` in your environment to opt out.

---

> **Privacy notice:** `scripts/validate.mjs` reports the validation result, skill name/version, model/client identifiers, the validated code when present, and validator-specific context such as API name, extension target, filename, file type, theme path, file list, artifact ID, and revision to Shopify (`shopify.dev/mcp/usage`) to help improve these tools. Set `OPT_OUT_INSTRUMENTATION=true` in your environment to opt out.
