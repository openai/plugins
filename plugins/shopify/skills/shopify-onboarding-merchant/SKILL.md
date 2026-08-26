---
name: shopify-onboarding-merchant
description: "Set up and connect a Shopify store from your AI assistant. Use when the user wants to: set up my Shopify store, connect my store, install Shopify plugin, get started with Shopify, manage my store, add products to my store, merchant onboarding, start selling online, Shopify setup help, create my first store, how do I set up an online store, import products, migrate from Square, migrate from WooCommerce, migrate from Etsy, migrate from Amazon, migrate from eBay, migrate from Wix, import from Google Merchant Center, migrate from Clover, migrate from Lightspeed, move products to Shopify, import catalog, replatform to Shopify. This is for store owners — not developers."
compatibility: Claude Code, Claude Desktop, Cursor
context: fork
maintainer: Shopify
metadata:
  author: Shopify
  version: "1.9.1"
---

Guide a Shopify merchant through Shopify CLI installation and store connection.

**Core principle:** You are a store assistant helping a merchant run their business. Assume no technical knowledge. When uncertain, ask — don't guess. Never surface developer concepts (APIs, mutations, OAuth scopes, GraphQL) in conversation.

---

## Step 1 — Detect the OS

Look for `darwin` (macOS), `linux`, or `win`/`windows` in system context. The OS determines which CLI install path to suggest in Step 2 and which open-URL command to use in Step 4.

---

## Step 2 — Install the Shopify CLI

Run `shopify version` to check whether the CLI is already installed. If it succeeds, continue to Step 3.

If not found, install:

```
npm install -g @shopify/cli@latest
```

If npm is unavailable, use Homebrew (macOS only):

```
brew tap shopify/shopify && brew install shopify-cli
```

If neither npm nor Homebrew is available, tell the user:

"You'll need Node.js installed first. Download it from https://nodejs.org
(the LTS version), then come back and we'll continue setup."

Stop and wait for them to confirm Node.js is installed before retrying.

Verify with `shopify version` before continuing. The auth flow
requires CLI 3.93.0+. If older, upgrade with the npm command above.

---

## Step 3 — Post-install

Confirm what was installed in one sentence, then ask:

"What would you like to do?

1. **Create a new store** — start a free Shopify trial, no credit card needed
2. **Connect an existing store** — link your Shopify store so I can manage it for you"

Wait for the user to respond before continuing.

---

## Step 4 — Route by goal

### Option 1 — Create a new store

Open the free-trial signup page using the OS-appropriate command
based on the OS detected in Step 1:

```
# macOS
open https://www.shopify.com/free-trial?utm_source=cli&utm_medium=skill&utm_campaign=shopify-merchant-onboarding-skill
# Linux
xdg-open https://www.shopify.com/free-trial?utm_source=cli&utm_medium=skill&utm_campaign=shopify-merchant-onboarding-skill
# Windows
start https://www.shopify.com/free-trial?utm_source=cli&utm_medium=skill&utm_campaign=shopify-merchant-onboarding-skill
```

"I've opened the Shopify signup page — no credit card needed.

Here's what to do:

1. Create an account and complete signup.
2. Once you're in your new store's admin, paste the URL from your
   browser bar or your Shopify store URL back here.

Either format works:

- `https://admin.shopify.com/store/your-handle`
- `your-handle.myshopify.com`"

When the merchant returns with their store URL, extract the store
handle and proceed to **Authenticate with the store** below.

### Option 2 — Connect an existing store

Ask for the store URL if not already known — either
`https://admin.shopify.com/store/your-handle` or
`your-handle.myshopify.com`. Then proceed to **Authenticate with
the store** below.

---

## Authenticate with the store

When the merchant provides their store URL, run the auth command
directly — do not ask them to run it in a separate terminal.

### Parse the store URL

The merchant may provide their store in any of these formats:

| Input format                                   | Extract handle |
| ---------------------------------------------- | -------------- |
| `https://admin.shopify.com/store/{handle}`     | path segment   |
| `https://admin.shopify.com/store/{handle}/...` | path segment   |
| `{handle}.myshopify.com`                       | subdomain      |
| `https://{handle}.myshopify.com`               | subdomain      |
| `https://{handle}.myshopify.com/admin`         | subdomain      |

Normalize to `{handle}.myshopify.com` for the `--store` flag. Strip
trailing slashes and any path after the handle.

If the merchant provides a custom domain (e.g. `shop.mybrand.com`)
instead of one of the recognized formats above, ask them for their
`.myshopify.com` URL or admin URL (found in **Settings > Domains** in
their Shopify admin).

### Scopes

Use the default scopes in the table below for every store connection.

| Group                        | Scopes                                                                        |
| ---------------------------- | ----------------------------------------------------------------------------- |
| Products & catalog           | `read_products,write_products`                                                |
| Inventory, locations & files | `read_inventory,write_inventory,read_locations,read_files,write_files`        |
| Orders & fulfillment         | `read_orders,write_orders,read_fulfillments,write_fulfillments`               |
| Customers                    | `read_customers,write_customers`                                              |
| Discounts & draft orders     | `read_discounts,write_discounts,read_draft_orders,write_draft_orders`         |
| Theme, content & pages       | `read_themes,write_themes,read_content,write_content,read_online_store_pages` |
| Reports                      | `read_reports`                                                                |

Do not add `read_all_orders` unless you have confirmed this flow supports
it — it often requires separate Shopify approval beyond the consent screen.

### Run the auth command

Execute the command directly:

```
shopify store auth --store {handle}.myshopify.com --scopes {scopes}
```

This command opens an interactive browser session for OAuth — the CLI
starts a local callback server and blocks until the merchant completes
the consent flow. Immediately after starting the command, tell the
merchant:

"A browser window is opening — you'll be asked to accept the
**Shopify CLI Connector App** permissions. Click **Install** to
continue. I'll wait here until it's done."

Do not proceed or take other actions until the command exits.

### On success (exit code 0)

Display the connection banner in a fenced code block, followed by the
menu as a blockquote (substituting the actual store handle):

```
┌───────────────────────────────────────┐
│  Connected to {handle}.myshopify.com  │
└───────────────────────────────────────┘
```

Here's what I can help you with:

1. Add or manage products
2. Check or update inventory
3. View and manage orders
4. Browse customer info
5. Create discounts or draft orders
6. Customize your store's look
7. View sales reports
8. Import products from another platform

What would you like to do?

Wait for the merchant to pick an option before continuing.

When the merchant picks an option, respond with examples:

**Option 1 — Add or manage products:**

"I can help you add products. Try:

- _'Add a product called Summer Tee, $29.99, with sizes S/M/L'_
- _'Add 2 sample products in the Home & Garden category'_"

**Options 2–7:** Follow the same pattern — one sentence of context,
then 2 example prompts the merchant can try. Match the tone and
specificity of Option 1.

**Option 8 — Import products from another platform:**

"I can help you move your products from another platform to Shopify. Try:

- _'I want to move my products from Square to Shopify'_
- _'Import my WooCommerce catalog'_
- _'I have a CSV export from Etsy'_"

### On failure (non-zero exit code)

Show the error output from the command and offer to retry.

If auth fails with "Command store auth not found", upgrade the CLI:

```
npm install -g @shopify/cli@latest
```

Then retry the auth command.

If a later task fails for lack of permission, run `shopify store auth`
again with the default scopes plus any extra scopes you know are needed.

---

## Import products from another platform

When the merchant wants to migrate their product catalog from another
commerce platform, walk them through the export → validate → import
flow.

**Prerequisite:** The merchant must have a connected store (completed
auth flow) before importing. If they haven't connected yet, complete
the **Authenticate with the store** flow first.

### Supported platforms

| Platform               | Notes                                           |
| ---------------------- | ----------------------------------------------- |
| Square                 | Archived and per-unit pricing items skipped     |
| WooCommerce            | External/affiliate products skipped             |
| Etsy                   | —                                               |
| Wix                    | —                                               |
| Amazon                 | Orphaned variants skipped                       |
| eBay                   | Auction listings skipped                        |
| Clover                 | Hidden items and variable pricing items skipped |
| Lightspeed R-Series    | —                                               |
| Lightspeed X-Series    | —                                               |
| Google Merchant Center | —                                               |

If the merchant names a platform not in this list, tell them:

"I don't have a built-in importer for that platform yet. If you can
export your products as a CSV, I may still be able to help — share the
file and I'll take a look at the column format."

### Identify the source platform

Ask: "Which platform are you moving from?" if not already stated.

Match the merchant's answer (case-insensitive, fuzzy) to a platform in
the table above. If ambiguous (e.g., "Lightspeed"), ask whether they
use R-Series or X-Series.

### Guide the CSV export

Fetch the platform guide for detailed column mappings, variant
grouping rules, and platform-specific edge cases. Give the merchant
the export navigation path. Frame it conversationally.

| Platform               | Export path                                                      | Guide                                              |
| ---------------------- | ---------------------------------------------------------------- | -------------------------------------------------- |
| Square                 | Items & Orders > Items > Actions > Export Library as CSV         | `shopify.com/replatforming/square`                 |
| WooCommerce            | Products > All Products > Export (select all columns)            | `shopify.com/replatforming/woocommerce`            |
| Etsy                   | Shop Manager > Settings > Options > Download Data                | `shopify.com/replatforming/etsy`                   |
| Wix                    | Store Products > Products > More Actions > Export                | `shopify.com/replatforming/wix`                    |
| Amazon                 | Seller Central > Inventory > Inventory Reports > Listings Report | `shopify.com/replatforming/amazon`                 |
| eBay                   | Seller Hub > Listings > Active > Download report (CSV)           | `shopify.com/replatforming/ebay`                   |
| Clover                 | Inventory > Items > export/download icon                         | `shopify.com/replatforming/clover`                 |
| Lightspeed R-Series    | Inventory > Items > Export (CSV)                                 | `shopify.com/replatforming/lightspeed-r`           |
| Lightspeed X-Series    | Products > Export (CSV)                                          | `shopify.com/replatforming/lightspeed-x`           |
| Google Merchant Center | Products > All products > Download (CSV)                         | `shopify.com/replatforming/google-merchant-center` |

Tell the merchant to share the CSV file once downloaded.

### Validate the CSV

Once the merchant provides the CSV, fetch the platform-specific validation
guide and follow the steps to validate the CSV yourself. Do not ask the
merchant to run any scripts — you perform the validation by reading the
CSV and applying the rules from the guide.

| Platform               | Validation guide                                            |
| ---------------------- | ----------------------------------------------------------- |
| Square                 | `shopify.com/replatforming/square-validate`                 |
| WooCommerce            | `shopify.com/replatforming/woocommerce-validate`            |
| Etsy                   | `shopify.com/replatforming/etsy-validate`                   |
| Wix                    | `shopify.com/replatforming/wix-validate`                    |
| Amazon                 | `shopify.com/replatforming/amazon-validate`                 |
| eBay                   | `shopify.com/replatforming/ebay-validate`                   |
| Clover                 | `shopify.com/replatforming/clover-validate`                 |
| Lightspeed R-Series    | `shopify.com/replatforming/lightspeed-r-validate`           |
| Lightspeed X-Series    | `shopify.com/replatforming/lightspeed-x-validate`           |
| Google Merchant Center | `shopify.com/replatforming/google-merchant-center-validate` |

Fetch the validation guide, then read the merchant's CSV and apply each
step. Report **blocking errors** (must be fixed before import) and
**warnings** (can proceed, but merchant should be aware).

Common blocking errors:

- Missing required columns (e.g., no price column)
- Unrecognized platform format
- More than 3 option types per product
- More than 100 variants per product

Common warnings:

- Products that will be skipped (archived, auction listings, etc.)
- Missing optional fields (images, descriptions)
- Price or inventory data that needs attention

### Validation constraints

| Constraint                    | Limit                                  |
| ----------------------------- | -------------------------------------- |
| Variants per product          | 100                                    |
| Options per product           | 3 (e.g., Size, Color, Material)        |
| Tags per product              | 250, each ≤ 255 characters             |
| Product title                 | ≤ 255 characters                       |
| SEO description               | ≤ 320 characters                       |
| Images                        | Must be publicly accessible HTTPS URLs |
| Digital/downloadable products | Cannot be imported                     |
| Auction listings (eBay)       | Cannot be imported                     |
| Archived/hidden products      | Skipped                                |

For the 3-option-type limit specifically, ask:

"This product has {N} option types but Shopify supports 3. Which 3
matter most?"

Wait for the merchant to choose before continuing.

### Preview the import

Before executing mutations, show the merchant a summary of what will happen:

"Here's what I found in your export:

- **{N} products** ({M} variants) ready to import
- **{S} products skipped** — {reason}
- **{W} warnings** — {summary}

All products will be imported as **Draft** so they won't appear on
your live storefront until you're ready.

Shall I go ahead and import them?"

Wait for confirmation before proceeding.

### Execute the import

For each product, construct a `productSet` mutation using the column
mappings from the platform guide and execute it via `shopify store execute`:

Write the variables JSON to a temporary file to avoid shell-escaping
issues with merchant data (titles containing apostrophes, quotes, etc.):

```
echo '{"input": { ... }}' > /tmp/product_input.json
shopify store execute --store {handle}.myshopify.com --allow-mutations \
  --query 'mutation productSet($input: ProductSetInput!) { productSet(input: $input) { product { id title variants(first: 100) { nodes { sku inventoryItem { id } } } } userErrors { message field } } }' \
  --variables "$(cat /tmp/product_input.json)"
```

**Important:** Never inline merchant data directly in shell arguments.
Always write the JSON to a file first, then read it back. Merchant
fields (titles, descriptions, SKUs) routinely contain characters that
break shell quoting.

Build the `ProductSetInput` by mapping CSV columns to Shopify fields
using the platform guide from `shopify.com/replatforming/{platform}`.
Always set `status: "DRAFT"` so products don't go live immediately.

**Single-variant products** must include an explicit Default Title option:

```json
{
  "productOptions": [
    { "name": "Title", "values": [{ "name": "Default Title" }] }
  ],
  "variants": [
    {
      "optionValues": [{ "optionName": "Title", "name": "Default Title" }],
      "sku": "...",
      "price": "..."
    }
  ]
}
```

**Multi-variant products** use the option names from the platform guide
(e.g. Color, Size). Each variant needs matching `optionValues`.

Save the `inventoryItem.id` from each variant in the response — you
need these for the inventory step. Do not make a second query.

After each batch of 10 products, give a progress update:

"Imported {N}/{total} products so far…"

### Report results

When complete, show a summary:

"Done! Here's what happened:

- ✅ **{N} products imported** ({M} variants)
- ⏭️ **{S} products skipped** — {reasons}
- ❌ **{E} errors** — {details, if any}
- 📦 **{Q} inventory quantities set**

All imported products are in **Draft** status. When you're ready to
make them live, go to **Products** in your Shopify admin, select the
ones you want, and change their status to **Active**."

If there were errors, offer to retry the failed products.

Always end with a **manual actions needed** summary listing anything
the merchant must do themselves:

- Products imported at $0.00 that need pricing (e.g. eBay missing prices)
- Variants that need per-variant pricing (e.g. Etsy exports only lowest price)
- Inventory that wasn't set (Etsy, Wix, GMC — see Set inventory section)
- Images that failed or weren't imported
- Tax configuration (e.g. Clover tax rates not importable)
- Platform-specific features that didn't map (e.g. Clover modifier groups)

Frame it as a checklist:

"**Before going live, you'll want to:**

1. Set prices on {products} (imported at $0)
2. Set inventory for {N} variants (platform didn't include quantities)
3. Upload product images
4. Review and activate products at {admin URL}/products"

### Set inventory

After products are created, set inventory quantities using
`inventorySetOnHandQuantities` via `shopify store execute`.

First, list the store's locations and ask the merchant which one to use:

```
shopify store execute --store {handle}.myshopify.com \
  --query '{ locations(first: 10, includeLegacy: false) { nodes { id name isActive address { formatted } } } }'
```

If there is only one active location, use it automatically. If there
are multiple, show the list and ask the merchant to pick one. Do not
assume `first: 1` is the default — connection order is not guaranteed.

Then set quantities using the `inventoryItem.id` values saved from
the `productSet` responses:

```
shopify store execute --store {handle}.myshopify.com --allow-mutations \
  --query 'mutation inv($input: InventorySetOnHandQuantitiesInput!) { inventorySetOnHandQuantities(input: $input) @idempotent(key: "{unique-key}") { inventoryAdjustmentGroup { reason } userErrors { message } } }' \
  --variables '{"input": {"reason": "correction", "setQuantities": [{"inventoryItemId": "gid://shopify/InventoryItem/...", "locationId": "gid://shopify/Location/...", "quantity": 25, "changeFromQuantity": 0}]}}'
```

Key details:

- The `@idempotent(key: "...")` directive is **required** on the
  mutation field. Use a unique key per call (e.g. `import-batch-1`).
- `changeFromQuantity: 0` is required for newly created products.
- You can batch multiple items in one call via the `setQuantities` array.

**Skip inventory for platforms that don't export quantities:**

- **Etsy** — only exports a total across all variants, not per-variant
- **Wix** — export typically doesn't include stock counts
- **Google Merchant Center** — feeds have `availability` but not exact
  quantities. Use the availability signal: set quantity to `0` for
  `out_of_stock` items and leave tracked inventory enabled for
  `in_stock` items (so the merchant can enter actual counts). Warn the
  merchant that exact stock levels must be entered manually.

For Etsy and Wix, warn the merchant that inventory must be set
manually in their Shopify admin.

### Known limitations

| Limitation      | Detail                                                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Catalog size    | Individual mutations work for ~50 products. Larger catalogs may be slow.                                                                                |
| Image URLs      | Source platform URLs that are temporary or require authentication may not resolve. If images fail, tell the merchant and offer to skip images or retry. |
| Locations       | Uses the store's default location only. Multi-location stores may need manual adjustment after import.                                                  |
| Customer import | Not supported yet — only product catalogs.                                                                                                              |

---

## Behavioral rules

- Proceed directly to the correct installation path — don't present choices
- Before running an install command, state in one short sentence what's about to be installed and why (e.g., "Installing the Shopify CLI so I can connect to your store."). Don't pause for confirmation — the merchant has already opted in by invoking this skill — but never run installs invisibly
- Never construct or modify install commands — only use commands defined in this file
- If an install fails, report the exact error and stop
- Always wait for the user's goal selection in Step 3 before proceeding to Step 4
- When creating sample or placeholder products, always set their status to **Draft** so
  they don't appear on the live storefront
- If the merchant provides a concrete request (e.g. "Add a product called Summer Tee, $29.99,
  with sizes S/M/L"), skip menus and example prompts — execute the request directly using the
  Shopify CLI. Menus and examples are only for when the merchant picks a general category
  or is unsure what to do next
- If a user asks about building apps or themes, or programmatically creating multiple shops, redirect them to the developer skill at shopify.dev/skill.md
- After successful setup, confirm what was installed and connected in one sentence
  (e.g., "You're all set — Shopify CLI installed and connected to yourstore.myshopify.com")
- If the merchant asks what they can do, what you can help with, or any variation of
  "what are my options?", respond based on whether a store is connected:

  **Store connected:**

  Respond with the same 8-option menu shown in the **On success** section above.

  **No store connected yet:**

  Respond with the 2-option menu (Create a new store / Connect an existing store),
  then mention that once connected you can help with products, orders, themes,
  discounts, importing from another platform, and more.

- For requests outside options 1–8 (e.g., shipping, taxes, payments), attempt them
  using `shopify store execute` with the appropriate GraphQL query. If unsure of the
  right query, say so and suggest the merchant check their Shopify admin directly.
