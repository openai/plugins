---
name: shopify-polaris-admin-extensions
description: "Add custom actions and blocks from your app at contextually relevant spots throughout the Shopify Admin. Admin UI Extensions also supports scaffolding new adminextensions using Shopify CLI commands."
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
   (Always include these flags. Use your actual model name for YOUR_MODEL_NAME; use claude-code/cursor/etc. for YOUR_CLIENT_NAME. For YOUR_ARTIFACT_ID, generate a stable random ID per code block and reuse it across validation retries. For REVISION_NUMBER, start at 1 and increment on each retry of the same artifact.) Pass `--target` with the admin extension target this code runs in (e.g. `admin.product-details.block.render`); validation will fail without it.
4. If validation fails: search for the error type, fix, re-validate (max 3 retries)
5. Return code only after validation passes

**You must run both search_docs.mjs and validate.mjs in every response. Do not return code to the user without completing step 3.**

---

You are an assistant that helps Shopify developers write UI Framework code to interact with the latest Shopify polaris-admin-extensions UI Framework version.

You should find all operations that can help the developer achieve their goal, provide valid UI Framework code along with helpful explanations.
Admin Extensions integrate into the Shopify admin at contextual locations for merchant workflows.
Admin actions are a UI extension that you can use to create transactional workflows within existing pages of the Shopify admin. Merchants can launch these UI extensions from the More actions menus on resource pages or from an index table's bulk action menu when one or more resources are selected. After the UI extensions are launched, they display as modals. After they're closed, the page updates with the changes from the action.

## Validator constraints

Do not include HTML comments (`<!-- ... -->`) in the code — the validator treats them as invalid custom components.

## IMPORTANT : ALWAYS USE THE CLI TO SCAFFOLD A NEW EXTENSION

Shopify CLI generates templates that aligns with the latest available version and is not prone to errors. ALWAYS use the CLI Command to Scaffold a new Admin UI extension

CLI Command to Scaffold a new Admin Action Extension

```bash
shopify app generate extension --template admin_action --name my-admin-action
```

Admin blocks are built with UI extensions and enable your app to embed contextual information and inputs directly on resource pages in the Shopify admin. When a merchant has added them to their pages, these UI extensions display as cards inline with the other resource information. Merchants need to manually add and pin the block to their page in the Shopify admin before they can use it.
With admin blocks, merchants can view and modify information from your app and other data on the page simultaneously. To facilitate complex interactions and transactional changes, you can launch admin actions directly from admin blocks.

CLI Command to Scaffold a new Admin Block Extension:

```bash
shopify app generate extension --template admin_block --name my-admin-block
```

Admin link extensions let you direct merchants from pages in the Shopify admin to related, complex workflows in your app. For example, the Shopify Flow app has an admin link extension that directs merchants to a page of the app where they can run an automation for any order:

```bash
shopify app generate extension --template admin_link --name admin-link-extension
```

Admin print actions are a special form of UI extension designed to let your app print documents from key pages in the Shopify admin. Unlike typical actions provided by UI extensions, admin print actions are found under the Print menu on orders and product pages. Additionally, they contain special APIs to let your app display a preview of a document and print it.
CLI Command to Scaffold a new Admin Print Action Extension:

```bash
shopify app generate extension --template admin_print --name my-admin-print-extension
```

version: 2026-01

## Target APIs

**Contextual APIs:** Customer Segment Template Extension API, Discount Function Settings API, Order Routing Rule API, Product Details Configuration API, Product Variant Details Configuration API, Purchase Options Card Configuration API, Validation Settings API
**Core APIs:** Action Extension API, Block Extension API, Print Action Extension API, Standard API
**Utility APIs:** Intents API, Picker API, Resource Picker API, Should Render API

## Polaris Web Components

**Actions:** Button, ButtonGroup, Clickable, ClickableChip, Link, Menu
**Feedback and status indicators:** Badge, Banner, Spinner
**Forms:** Checkbox, ChoiceList, ColorField, ColorPicker, DateField, DatePicker, EmailField, Form, FunctionSettings, MoneyField, NumberField, PasswordField, SearchField, Select, Switch, TextArea, TextField, URLField
**Layout and structure:** Box, Divider, Grid, OrderedList, QueryContainer, Section, Stack, Table, UnorderedList
**Media and visuals:** Avatar, Icon, Image, Thumbnail
**Settings and templates:** AdminAction, AdminBlock, AdminPrintAction
**Typography and content:** Chip, Heading, Paragraph, Text, Tooltip

## Guides

**Available guides:** Network Features

## Components available for Admin UI extensions.

These examples have all the props available for the component. Some example values for these props are provided.
Refer to the developer documentation to find all valid values for a prop. Ensure the component is available for the target you are using.

```html
<s-admin-action heading="Edit product" loading>Content</s-admin-action>
<s-admin-block heading="Custom Fields" collapsedSummary="3 fields configured">Content</s-admin-block>
<s-admin-print-action src="https://example.com/invoice.pdf"></s-admin-print-action>
<s-avatar initials="JD" src="https://example.com/avatar.jpg" size="base" alt="Jane Doe"></s-avatar>
<s-badge tone="success" color="base" icon="check-circle" size="base">Fulfilled</s-badge>
<s-banner heading="Important notice" tone="info" dismissible hidden>Message content</s-banner>
<s-box accessibilityLabel="Container" accessibilityRole="group" accessibilityVisibility="visible" background="subdued" blockSize="auto" border="base" borderColor="base" borderRadius="base" borderStyle="solid" borderWidth="base" display="auto" inlineSize="100%" maxBlockSize="500px" maxInlineSize="100%" minBlockSize="100px" minInlineSize="50px" overflow="hidden" padding="base" paddingBlock="large" paddingBlockStart="base" paddingBlockEnd="base" paddingInline="large" paddingInlineStart="base" paddingInlineEnd="base">Content</s-box>
<s-button accessibilityLabel="Save product" disabled command="--show" commandFor="my-modal" icon="save" interestFor="my-tooltip" lang="en" loading type="submit" tone="auto" variant="primary" target="_blank" href="https://example.com" download="file.csv" inlineSize="fill">Save</s-button>
<s-button-group gap="base" accessibilityLabel="Actions"><s-button slot="primary-action" variant="primary">Save</s-button><s-button slot="secondary-actions">Cancel</s-button></s-button-group>
<s-checkbox accessibilityLabel="Accept" checked defaultChecked details="Required" error="Must accept" label="Accept terms" required name="terms" disabled value="accepted" indeterminate defaultIndeterminate></s-checkbox>
<s-chip color="base" accessibilityLabel="Category">Electronics</s-chip>
<s-choice-list details="Pick shipping" disabled error="Required" label="Shipping method" labelAccessibilityVisibility="exclusive" multiple name="shipping" values={["standard"]}><s-choice value="standard" selected defaultSelected disabled accessibilityLabel="Standard shipping">Standard</s-choice><s-choice value="express">Express</s-choice></s-choice-list>
<s-clickable accessibilityLabel="View product" command="--show" commandFor="detail-modal" disabled download="file.pdf" href="/products/42" interestFor="tip" lang="en" loading target="_blank" type="button" padding="base" background="subdued" borderRadius="base">Content</s-clickable>
<s-clickable-chip color="base" accessibilityLabel="Filter" removable hidden href="/filter" disabled command="--show" commandFor="chip-menu" interestFor="chip-tip">Active</s-clickable-chip>
<s-color-field name="brandColor" value="#FF5733" defaultValue="#000000" disabled label="Brand color" labelAccessibilityVisibility="exclusive" placeholder="Pick color" readOnly required error="Invalid" details="Brand color" autocomplete="off" alpha></s-color-field>
<s-color-picker alpha value="#3498DB" defaultValue="#000000" name="accent"></s-color-picker>
<s-date-field name="startDate" value="2025-06-15" defaultValue="2025-01-01" disabled label="Start date" labelAccessibilityVisibility="exclusive" placeholder="YYYY-MM-DD" readOnly required error="Invalid date" details="Event start" autocomplete="bday" allow="2025--" allowDays="1,2,3,4,5" disallow="2025-12-25" disallowDays="0,6" view="2025-06" defaultView="2025-01"></s-date-field>
<s-date-picker type="range" value="2025-03-01" defaultValue="2025-01-01" name="dateRange" defaultView="2025-06" view="2025-03" allow="2025--" disallow="2025-12-25" allowDays="1,2,3,4,5" disallowDays="0,6"></s-date-picker>
<s-divider direction="inline" color="base"></s-divider>
<s-drop-zone accept=".jpg,.png" accessibilityLabel="Upload images" disabled error="File too large" label="Product images" labelAccessibilityVisibility="exclusive" multiple name="images" required value="file.jpg"></s-drop-zone>
<s-email-field name="email" value="test@example.com" defaultValue="user@shop.com" disabled label="Email" labelAccessibilityVisibility="exclusive" placeholder="you@example.com" readOnly required error="Invalid email" details="Contact email" autocomplete="email" maxLength="100" minLength="5"></s-email-field>
<s-form id="my-form"><s-text-field label="Name" name="name"></s-text-field><s-button type="submit">Submit</s-button></s-form>
<s-function-settings id="my-settings"><s-number-field label="Min order" name="minAmount" min={0}></s-number-field></s-function-settings>
<s-grid gridTemplateColumns="1fr 2fr" gridTemplateRows="auto" alignItems="center" justifyItems="start" placeItems="center" alignContent="start" justifyContent="space-between" placeContent="center" gap="base" rowGap="large" columnGap="base" padding="base" background="subdued"><s-grid-item gridColumn="1 / 3" gridRow="1" padding="base">Col 1</s-grid-item><s-grid-item>Col 2</s-grid-item></s-grid>
<s-heading accessibilityRole="presentation" accessibilityVisibility="visible" lineClamp="2">Page Title</s-heading>
<s-icon type="cart" tone="success" color="base" size="base" interestFor="cart-tip"></s-icon>
<s-image src="https://example.com/product.jpg" srcSet="img-1x.jpg 1x, img-2x.jpg 2x" sizes="(max-width: 600px) 100vw, 50vw" alt="Product" loading="lazy" accessibilityRole="presentation" inlineSize="100%" aspectRatio="16/9" objectFit="cover" border="base" borderColor="base" borderRadius="base" borderStyle="solid" borderWidth="base"></s-image>
<s-link accessibilityLabel="Docs" command="--show" commandFor="help-modal" interestFor="link-tip" download="report.csv" href="https://shopify.dev" lang="en" target="_blank" tone="auto">Shopify Docs</s-link>
<s-menu id="actions-menu" accessibilityLabel="Product actions"><s-button variant="tertiary" icon="edit">Edit</s-button><s-button variant="tertiary" icon="delete" tone="critical">Delete</s-button></s-menu>
<s-money-field name="price" value="29.99" defaultValue="0" disabled label="Price" labelAccessibilityVisibility="exclusive" placeholder="0.00" readOnly required error="Required" details="Product price" autocomplete="off" max={999999} min={0}></s-money-field>
<s-number-field name="qty" value="10" defaultValue="1" disabled label="Quantity" labelAccessibilityVisibility="exclusive" placeholder="0" readOnly required error="Invalid" details="Enter quantity" autocomplete="off" inputMode="numeric" max={100} min={1} prefix="#" step={1} suffix="units"></s-number-field>
<s-ordered-list><s-list-item>First</s-list-item><s-list-item>Second</s-list-item></s-ordered-list>
<s-paragraph accessibilityVisibility="visible" fontVariantNumeric="tabular-nums" tone="neutral" dir="ltr" color="subdued" lineClamp="3">Body text content</s-paragraph>
<s-password-field name="password" value="secret123" defaultValue="" disabled label="Password" labelAccessibilityVisibility="exclusive" placeholder="Enter password" readOnly required error="Too short" details="Min 8 chars" autocomplete="current-password" maxLength="128" minLength="8"></s-password-field>
<s-query-container containerName="main">Content</s-query-container>
<s-search-field name="query" value="blue shirt" defaultValue="" disabled label="Search" labelAccessibilityVisibility="exclusive" placeholder="Search products" readOnly required error="No results" details="Search catalog" autocomplete="off" maxLength="200" minLength="1"></s-search-field>
<s-section accessibilityLabel="Details" heading="Product details" padding="base">Content</s-section>
<s-select disabled name="status" value="active" details="Pick status" error="Required" label="Status" labelAccessibilityVisibility="exclusive" placeholder="Select status" required icon="product"><s-option-group disabled label="States"><s-option value="active" disabled selected defaultSelected>Active</s-option><s-option value="draft">Draft</s-option></s-option-group></s-select>
<s-spinner accessibilityLabel="Loading products" size="base"></s-spinner>
<s-stack direction="inline" justifyContent="space-between" alignItems="center" alignContent="start" gap="base" rowGap="large" columnGap="base" padding="base" background="subdued"><s-text>Item 1</s-text><s-text>Item 2</s-text></s-stack>
<s-switch accessibilityLabel="Toggle" checked defaultChecked details="Enable feature" error="Required" label="Active" required name="active" disabled value="on" labelAccessibilityVisibility="exclusive"></s-switch>
<s-table loading paginate hasPreviousPage hasNextPage variant="auto"><s-table-header-row><s-table-header listSlot="primary">Product</s-table-header><s-table-header listSlot="labeled" format="currency">Price</s-table-header></s-table-header-row><s-table-body><s-table-row clickDelegate="first-cell"><s-table-cell>Blue T-Shirt</s-table-cell><s-table-cell>$29.99</s-table-cell></s-table-row></s-table-body></s-table>
<s-text accessibilityVisibility="visible" dir="ltr" color="subdued" type="strong" tone="success" fontVariantNumeric="tabular-nums" interestFor="text-tip">Styled text</s-text>
<s-text-area name="description" value="A great product" defaultValue="" disabled label="Description" labelAccessibilityVisibility="exclusive" placeholder="Enter description" readOnly required error="Too short" details="Product description" autocomplete="off" maxLength="500" minLength="10" rows={4}></s-text-area>
<s-text-field disabled name="title" value="Blue T-Shirt" defaultValue="Untitled" details="Product name" error="Required" label="Title" labelAccessibilityVisibility="exclusive" placeholder="Enter title" readOnly required autocomplete="off" icon="product" maxLength="255" minLength="1" prefix="SKU-" suffix="™"></s-text-field>
<s-thumbnail src="https://example.com/thumb.jpg" alt="Product" size="base"></s-thumbnail>
<s-tooltip id="my-tip">Helpful tooltip text</s-tooltip>
<s-unordered-list><s-list-item>Item A</s-list-item><s-list-item>Item B</s-list-item></s-unordered-list>
<s-url-field name="website" value="https://example.com" defaultValue="https://" disabled label="Website" labelAccessibilityVisibility="exclusive" placeholder="https://example.com" readOnly required error="Invalid URL" details="Store URL" autocomplete="url" maxLength="2000" minLength="10"></s-url-field>
```

## Imports

Use the Preact entry point:

```ts
import "@shopify/ui-extensions/preact";
import { render } from "preact";
```

### Polaris web components (`s-admin-action`, `s-badge`, etc.)

Polaris web components are custom HTML elements with an `s-` prefix. These are globally registered and require **no import statement**. Use them directly as JSX tags:

```tsx
// No import needed — s-admin-action, s-badge, s-button, etc. are globally available
<s-admin-action heading="My Action">
  <s-button slot="primary-action">Submit</s-button>
  <s-button slot="secondary-actions">Cancel</s-button>
</s-admin-action>
```

When the user asks for Polaris web components (e.g. `s-admin-action`, `s-badge`, `s-button`, `s-text`), use the web component tag syntax above.

**Web component attribute rules:**

- Use **camelCase** attribute names: `alignItems`, `paddingBlock`, `borderRadius` — NOT kebab-case (`align-items`, `padding-block`)
- **Boolean attributes** (`disabled`, `loading`, `dismissible`, `hidden`, `required`, `checked`, `defaultChecked`) accept shorthand or `{expression}`:
  - ✅ `<s-button disabled loading>`, `<s-banner dismissible>`, `<s-checkbox checked={isChecked} />`
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

For example, if the user asks about admin extension target for product details blocks:
```
scripts/search_docs.mjs "admin.product-details.block.render" --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION
```

## ⚠️ MANDATORY: Validate Before Returning Code

You MUST run `scripts/validate.mjs` before returning any generated code to the user. Always include the instrumentation flags:

```
scripts/validate.mjs --code '...' --model YOUR_MODEL_NAME --client-name YOUR_CLIENT_NAME --client-version YOUR_CLIENT_VERSION --artifact-id YOUR_ARTIFACT_ID --revision REVISION_NUMBER --target <extension-target>
```

**`--target` is required for admin extensions.** Pass the extension target this code runs in (e.g. `admin.product-details.block.render`). If you don't know which target applies, run `scripts/search_docs.mjs "extension targets"` first to look one up — validation will fail without it.
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
