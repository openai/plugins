---
name: shopify-polaris-customer-account-extensions
description: "Build custom functionality that merchants can install at defined points on the Order index, Order status, and Profile pages in customer accounts. Customer Account UI Extensions also supports scaffolding new customer account extensions using Shopify CLI commands."
compatibility: Requires Node.js
metadata:
  author: Shopify
  version: "1.9.0"
---

## Required Tool Calls (do not skip)

You have a `bash` tool. Every response must use it — in this order:

1. Call `bash` with `scripts/search_docs.mjs "<query>"` — search before writing code
2. Write the code using the search results
3. Call `bash` with `scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER --target <extension-target>` — validate before returning
   (Always include these flags. Use your actual model name for YOUR_MODEL_NAME; use claude-code/cursor/etc. for YOUR_CLIENT_NAME. For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.) Pass `--target` with the customer-account extension target this code runs in (e.g. `customer-account.order-status.block.render`); validation will fail without it.
4. If validation fails: search for the error type, fix, re-validate (max 3 retries)
5. Return code only after validation passes

**You must run both search_docs.mjs and validate.mjs in every response. Do not return code to the user without completing step 3.**

---

You are an assistant that helps Shopify developers write UI Framework code to interact with the latest Shopify polaris-customer-account-extensions UI Framework version.

You should find all operations that can help the developer achieve their goal, provide valid UI Framework code along with helpful explanations.
Customer account UI extensions let app developers build custom functionality that merchants can install at defined points on the Order index, Order status, and Profile pages in customer accounts.

## Validator constraints

Do not include HTML comments (`<!-- ... -->`) in the code — the validator treats them as invalid custom components.

CLI Command to Scaffold a new Customer Account UI Extension:

```bash
shopify app generate extension --template=customer_account_ui --name=my_customer_account_ui_extension
```

version: 2026-01

## Extension Targets (use these in shopify.extension.toml)

Targets decide what components/APIs can be used.
Search the developer documentation for target-specific documentation:

**Footer:**

- customer-account.footer.render-after

**Order index:**

- customer-account.order-index.announcement.render
- customer-account.order-index.block.render

**Order status:**

- customer-account.order-status.announcement.render
- customer-account.order-status.block.render
- customer-account.order-status.cart-line-item.render-after
- customer-account.order-status.cart-line-list.render-after
- customer-account.order-status.customer-information.render-after
- customer-account.order-status.fulfillment-details.render-after
- customer-account.order-status.payment-details.render-after
- customer-account.order-status.return-details.render-after
- customer-account.order-status.unfulfilled-items.render-after

**Order action menu:**

- customer-account.order.action.menu-item.render
- customer-account.order.action.render

**Full page:**

- customer-account.order.page.render
- customer-account.page.render

**Profile (Default):**

- customer-account.profile.addresses.render-after
- customer-account.profile.announcement.render
- customer-account.profile.block.render

**Profile (B2B):**

- customer-account.profile.company-details.render-after
- customer-account.profile.company-location-addresses.render-after
- customer-account.profile.company-location-payment.render-after
- customer-account.profile.company-location-staff.render-after

## APIs

**Available APIs:** Analytics, Authenticated Account, Customer Account API, Customer Privacy, Extension, Intents, Localization, Navigation, Storefront API, Session Token, Settings, Storage, Toast, Version
**Order Status API:** Addresses, Attributes, Authentication State, Buyer Identity, Cart Lines, Checkout Settings, Cost, Discounts, Gift Cards, Localization (Order Status API), Metafields, Note, Order, Require Login, Shop

## Guides

**Available guides:** Using Polaris web components, Configuration, Error handling, Upgrading to 2026-01

Components available for customer account UI extensions.
These examples have all the props available for the component. Some example values for these props are provided.
Refer to the developer documentation to find all valid values for a prop. Ensure the component is available for the target you are using.

```html
<s-abbreviation title="HTML">HTML</s-abbreviation>
<s-announcement>Important update content</s-announcement>
<s-avatar
  initials="JD"
  src="https://example.com/avatar.jpg"
  size="base"
  alt="Jane Doe"
></s-avatar>
<s-badge tone="critical" color="base" icon="alert-circle" size="base"
  >Overdue</s-badge
>
<s-banner heading="Notice" tone="info" dismissible collapsible
  >Message content</s-banner
>
<s-box padding="base" background="subdued" border="base" borderRadius="base"
  >Content</s-box
>
<s-button variant="primary" tone="auto" type="submit">Save</s-button>
<s-button-group
  ><s-button variant="primary">Save</s-button
  ><s-button variant="secondary">Cancel</s-button></s-button-group
>
<s-checkbox label="Accept terms" name="terms" value="accepted"></s-checkbox>
<s-chip accessibilityLabel="Tag">Category</s-chip>
<s-choice-list label="Options" name="options"
  ><s-choice value="1">Option 1</s-choice
  ><s-choice value="2">Option 2</s-choice></s-choice-list
>
<s-clickable href="/orders/42" padding="base" background="subdued"
  >Click area</s-clickable
>
<s-clickable-chip removable accessibilityLabel="Filter"
  >Active</s-clickable-chip
>
<s-clipboard-item text="ABC123" />
<s-consent-checkbox
  label="Sign up for SMS"
  name="consent"
  policy="sms-marketing"
></s-consent-checkbox>
<s-consent-phone-field
  label="Phone"
  name="phone"
  policy="sms-marketing"
></s-consent-phone-field>
<s-customer-account-action heading="Return items"
  ><s-text>Action content</s-text></s-customer-account-action
>
<s-date-field
  label="Start date"
  name="startDate"
  value="2025-06-15"
  required
></s-date-field>
<s-date-picker
  type="single"
  name="selectedDate"
  value="2025-03-01"
></s-date-picker>
<s-details
  ><s-summary>More info</s-summary
  ><s-text>Expandable content</s-text></s-details
>
<s-divider direction="inline"></s-divider>
<s-drop-zone
  label="Upload file"
  name="file"
  accept=".jpg,.png"
  multiple
></s-drop-zone>
<s-email-field
  label="Email"
  name="email"
  autocomplete="email"
  required
></s-email-field>
<s-form
  ><s-text-field label="Name" name="name"></s-text-field
  ><s-button type="submit">Submit</s-button></s-form
>
<s-grid gridTemplateColumns="1fr 1fr" gap="base"
  ><s-grid-item><s-text>Col 1</s-text></s-grid-item
  ><s-grid-item><s-text>Col 2</s-text></s-grid-item></s-grid
>
<s-heading>Section Title</s-heading>
<s-icon type="cart" tone="auto" size="base"></s-icon>
<s-image
  src="https://example.com/image.png"
  alt="Description"
  aspectRatio="16/9"
  objectFit="cover"
  loading="lazy"
></s-image>
<s-image-group totalItems="6"
  ><s-image src="https://example.com/1.jpg" alt="Image 1"></s-image
  ><s-image src="https://example.com/2.jpg" alt="Image 2"></s-image
></s-image-group>
<s-link href="https://example.com" tone="auto">Link text</s-link>
<s-map
  apiKey="KEY"
  latitude="{43.65}"
  longitude="{-79.38}"
  zoom="{12}"
  accessibilityLabel="Store location"
  ><s-map-marker
    latitude="{43.65}"
    longitude="{-79.38}"
    accessibilityLabel="Store"
  ></s-map-marker
></s-map>
<s-button commandFor="actions-menu"></s-button>
<s-menu id="actions-menu" accessibilityLabel="Actions"
  ><s-button variant="secondary">Edit</s-button></s-menu
>
<s-modal id="my-modal" heading="Title" size="base"
  ><s-text>Modal content</s-text></s-modal
>
<s-money-field
  label="Amount"
  name="amount"
  min="{0}"
  max="{999999}"
></s-money-field>
<s-number-field
  label="Quantity"
  name="qty"
  min="{1}"
  max="{100}"
  step="{1}"
  inputMode="numeric"
></s-number-field>
<s-ordered-list
  ><s-list-item>First</s-list-item
  ><s-list-item>Second</s-list-item></s-ordered-list
>
<s-page heading="Orders" subheading="Manage orders"
  ><s-section heading="All orders"><s-text>Content</s-text></s-section></s-page
>
<s-paragraph tone="neutral" color="subdued">Body text content</s-paragraph>
<s-password-field
  label="Password"
  name="password"
  autocomplete="current-password"
  minLength="8"
  required
></s-password-field>
<s-payment-icon type="visa" accessibilityLabel="Visa"></s-payment-icon>
<s-phone-field label="Phone" name="phone" autocomplete="tel"></s-phone-field>
<s-popover id="pop" inlineSize="300px"
  ><s-box padding="base"><s-text>Popover content</s-text></s-box></s-popover
>
<s-press-button accessibilityLabel="Favorite" pressed>★</s-press-button>
<s-product-thumbnail
  src="https://example.com/product.jpg"
  alt="Blue T-Shirt"
  size="base"
></s-product-thumbnail>
<s-progress
  value="{75}"
  max="{100}"
  tone="auto"
  accessibilityLabel="75% complete"
></s-progress>
<s-qr-code
  content="https://example.com"
  size="base"
  border="base"
  accessibilityLabel="Scan to visit"
></s-qr-code>
<s-query-container containerName="main">Content</s-query-container>
<s-scroll-box blockSize="200px" overflow="auto" padding="base"
  >Scrollable content</s-scroll-box
>
<s-section heading="Details"><s-text>Section content</s-text></s-section>
<s-select label="Choose" name="choice"
  ><s-option value="a">A</s-option><s-option value="b">B</s-option></s-select
>
<s-sheet id="my-sheet" heading="Details"
  ><s-text>Sheet content</s-text></s-sheet
>
<s-skeleton-paragraph content="Loading text..."></s-skeleton-paragraph>
<s-spinner size="base" accessibilityLabel="Loading"></s-spinner>
<s-stack direction="inline" gap="base" alignItems="center"
  ><s-text>Item 1</s-text><s-text>Item 2</s-text></s-stack
>
<s-switch label="Enable" name="enabled" checked></s-switch>
<s-text type="strong" tone="success" color="base">Styled text</s-text>
<s-text-area
  label="Description"
  name="desc"
  rows="{4}"
  maxLength="{500}"
></s-text-area>
<s-text-field label="Name" name="name" icon="profile" required></s-text-field>
<s-time dateTime="2025-03-15T10:30:00Z">March 15, 2025</s-time>
<s-icon type="info" interestFor="my-tip"></s-icon
><s-tooltip id="my-tip">Hover for info</s-tooltip>
<s-unordered-list
  ><s-list-item>Item A</s-list-item
  ><s-list-item>Item B</s-list-item></s-unordered-list
>
<s-url-field label="Website" name="url" autocomplete="url"></s-url-field>
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
<s-banner tone="info">Welcome back</s-banner>
<s-badge tone="success">Order placed</s-badge>
```

When the user asks for Polaris web components (e.g. `s-banner`, `s-badge`, `s-button`, `s-text`), use the web component tag syntax above.

**Web component attribute rules:**

- Use **camelCase** attribute names: `alignItems`, `paddingBlock`, `borderRadius` — NOT kebab-case (`align-items`, `padding-block`)
- **Boolean attributes** (`disabled`, `loading`, `dismissible`, `checked`, `defaultChecked`, `required`) accept shorthand or `{expression}`:
  - ✅ `<s-checkbox checked={isSelected} />`, `<s-button disabled>`, `<s-banner dismissible>`
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

For example, if the user asks about customer account card:
```
scripts/search_docs.mjs "s-card customer-account" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

## ⚠️ MANDATORY: Validate Before Returning Code

You MUST run `scripts/validate.mjs` before returning any generated code to the user. Always include the instrumentation flags:

```
scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER --target <extension-target>
```

**`--target` is required for customer-account extensions.** Pass the extension target this code runs in (e.g. `customer-account.order-status.block.render`). If you don't know which target applies, run `scripts/search_docs.mjs "extension targets"` first to look one up — validation will fail without it.
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
