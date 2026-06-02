---
name: "Domain Search and Purchase"
description: Help users buy a domain through Wix. Check availability, suggest alternatives if taken, collect registration details (cycle, privacy, contact info), create a pre-configured cart, and provide a checkout link where the user just pays.
---
# Domain Search and Purchase

Use this recipe when a user wants to:
- Buy / purchase a domain
- Register a domain through Wix
- Get a custom domain for their Wix site
- Check if a domain is available and then buy it
- Says something like "buy me a domain", "I want to purchase a domain", "get me mybusiness.com"

## How Purchase Works

You help the user find an available domain, then collect registration details (cycle, privacy protection, contact info) directly in the chat. Once collected, you save the contact info, create a cart with the domain + addons, and provide a checkout link where the user only needs to complete payment.

**UX guidelines**: Keep the conversation natural. Do NOT expose internal implementation details to the user (e.g. don't say "I'm canceling the old cart", "saving to intent API", "adding line items"). Just tell them what matters: "Setting up your order..." then show the summary and checkout link.

## Site Context (Optional)

Domain purchase does NOT require a site. Do NOT call `ListWixSites` unless the user specifically mentions a site or asks to connect the domain to one.

However, after finding an available domain (Step 1), you should ask the user if they want to connect it to a Wix site. This unlocks two benefits:
- If the user has a **premium site**, the domain can be connected to it after purchase
- If the user has **no premium site**, they can get the domain **free for the first year** by upgrading to a premium plan (bundle deal)

See **Step 1b** for the site check flow.

## Required APIs

- **Check Domain Availability**: `GET https://www.wixapis.com/domain-search/v2/check-domain-availability`
- **Suggest Domains**: `GET https://www.wixapis.com/domain-search/v2/suggest-domains`

These are **public APIs that require no special authentication or scopes**. Just make a plain GET request to the URL with query parameters. No extra headers, no account-level auth, no site-level auth. No tokens needed.

**Important**: Do NOT use `GetSuggestedDomains` tool for domain suggestions in this recipe. Use the `SuggestDomains` v2 endpoint above instead -- it accepts free-text queries and does not need a site ID.

---

## Step 1: Find an Available Domain

### If the user has a specific domain in mind

Check if it's available using:

`GET https://www.wixapis.com/domain-search/v2/check-domain-availability?domain={domain}`

The `domain` parameter **must** include the TLD (e.g., `mybusiness.com`, not just `mybusiness`). If the user gives a name without a TLD, default to `.com` first.

**Response when available**:
```json
{
  "availability": {
    "domain": "mybusiness.com",
    "available": true,
    "premium": false
  }
}
```

**Response when taken**:
```json
{
  "availability": {
    "domain": "mybusiness.com",
    "available": false
  }
}
```

- **available: true** -> Proceed to Step 2
- **available: false** -> Do NOT just say "it's taken" and stop. Immediately suggest alternatives (see below).
- **DOMAINS_UNSUPPORTED_TLD error** -> Tell the user that TLD isn't supported by Wix, then suggest alternatives with supported TLDs (see below).

### If the domain is taken, unsupported, or the user wants ideas

Use the **Suggest Domains v2** API to find available alternatives:

`GET https://www.wixapis.com/domain-search/v2/suggest-domains`

**IMPORTANT**: Do NOT use the `GetSuggestedDomains` tool for this. Always use the v2 endpoint above.

This API accepts **free-text queries** -- it works with business descriptions, keywords, and brand concepts, not just domain names. For example: "pancakes business", "modern yoga studio", "photography portfolio".

**Query Parameters**:
| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Keywords, business idea, or brand concept | `pancakes business` |
| `paging.limit` | Number of suggestions (default: 10) | `10` |
| `tlds` | Filter by specific TLDs (repeatable, no dots) | `com`, `net` |

**Example -- alternatives for a taken domain**:
```
GET https://www.wixapis.com/domain-search/v2/suggest-domains?query=mybusiness&paging.limit=10
```

**Example -- brainstorming from a business idea**:
```
GET https://www.wixapis.com/domain-search/v2/suggest-domains?query=pancakes+business&paging.limit=10
```

**Example -- filtered by TLDs**:
```
GET https://www.wixapis.com/domain-search/v2/suggest-domains?query=mybusiness&paging.limit=5&tlds=com&tlds=net
```

**Example Response**:
```json
{
  "suggestions": [
    { "domain": "mybusiness.com", "premium": false },
    { "domain": "mybusiness.net", "premium": false },
    { "domain": "mybusiness.org", "premium": false },
    { "domain": "mybusiness.co", "premium": false },
    { "domain": "mybusiness.online", "premium": false }
  ],
  "pagingMetadata": {
    "count": 5,
    "cursors": { "next": "..." },
    "hasNext": true
  }
}
```

When presenting suggestions:
- List the domain names clearly
- All returned suggestions are already available for purchase -- no need to re-check availability
- Do NOT show a "Premium" column or flag premium domains -- it confuses users
- If the user has a TLD preference, highlight relevant ones (`.com` for general business, `.shop`/`.store` for e-commerce, `.me` for personal branding)
- If no suggestions come back, ask the user to try different keywords or broader terms
- If `pagingMetadata.hasNext` is true, more suggestions exist -- offer to show more

Once the user picks a domain (or the original was available), proceed to Step 1b.

---

## Step 1b: Check for Wix Sites (Optional but Recommended)

After the user has chosen a domain, ask: "Would you like to connect this domain to one of your Wix sites?"

If the user says yes (or if they mentioned a site earlier), call `ListWixSites` to get their sites.

The response includes each site's `id` and `name`. If the user has multiple sites, list them and ask which one they want to use.

Once a site is selected, remember the `siteId` (also called `msid`) -- you'll use it in the checkout link (Step 4d).

**Based on the site's plan status**, you can offer different guidance:
- **Site has a premium plan**: "Great, after purchasing the domain you can connect it to your site."
- **Site has no premium plan**: "I notice your site doesn't have a premium plan yet. If you upgrade to a premium plan, you can get this domain free for the first year! Want me to generate a link for the bundle deal instead?" If yes, generate: `[Get domain free with a site plan](https://manage.wix.com/premium-domains/split-page?domainName={DOMAIN_NAME})` -- this page shows the bundle option.
- **No sites at all**: "No problem, we'll proceed with a standalone domain purchase."

If the user says no or wants to skip, proceed without a site context.

---

## Step 2: Collect Registration Details

Once the user picks a domain, collect the details needed for purchase.

### 2a: Show pricing and ask for registration period

Get available cycles and pricing for the chosen TLD:

**Request** (via `ManageWixSite`):
```
POST https://manage.wix.com/_api/premium-purchase-platform-serverless/v1/offering/72af0602-1321-4897-8299-f507480b2bb8
```
Body:
```json
{
  "purchaseContext": {
    "params": { "tld": ".com" }
  }
}
```

Replace `.com` with the actual TLD (include the leading dot).

**Response** contains `products[0]` with:
- `productId` -- save this, you'll need it for the cart
- `pricingDetails[]` -- array of pricing per cycle

Present the pricing to the user as a table, for example:

| Period | Price |
|--------|-------|
| 1 year | $14.95 |
| 2 years | $27.90 |
| 3 years | $40.85 |

Ask the user which period they prefer. Default to 1 year if they don't have a preference.

If the API returns no products for this TLD, tell the user: "Wix doesn't support purchasing this TLD. Try a different extension like .com, .net, or .org."

### 2b: Ask about privacy protection

Present the user with three options:

1. **Privacy + DNSSEC** (recommended, most protecting) -- Hides your personal contact info from public WHOIS lookups AND adds DNSSEC protection against DNS spoofing/hijacking attacks. Product ID: `f8211619-d9f6-4312-9d03-f2958bbd08aa`
2. **Privacy only** -- Hides your personal contact info from public WHOIS lookups. Product ID: `22a84545-4ac0-4490-a434-45a1ebc479fb`
3. **No protection** -- Your contact info will be publicly visible in WHOIS. Product ID: `b9d89ff0-f29b-4bfd-a3f0-6e34ae65120d`

All three options use the addon product type ID `b3d86a1d-9db3-4f69-bd54-c132808856b1`.

### 2c: Collect or confirm contact info

First, check if the user already has contact info on file:

**Request** (via `ManageWixSite`):
```
GET https://manage.wix.com/v1/domain-registration-intents/preview/{domain}
```

Replace `{domain}` with the chosen domain (e.g. `mybakery.com`).

**Response** contains `domainRegistrationIntent` with existing contacts:
```json
{
  "domainRegistrationIntent": {
    "registrantContact": { "firstName": "...", "lastName": "...", "email": "...", "phone": "...", "address": { ... } },
    "adminContact": { ... },
    "techContact": { ... }
  }
}
```

- **If contacts exist**: Show the info and explicitly ask "Should I use these details, or would you like to register with different info?" Wait for the user to confirm before proceeding to Step 3. Do NOT skip this confirmation.
- **If contacts are empty**: Ask the user for: first name, last name, email, phone number, street address, city, country, and postal code. The user can provide country as a full name (e.g. "Israel", "United States") -- convert it to the 2-letter ISO country code (e.g. "IL", "US") before sending to the API. Wait for them to provide all fields before proceeding.

---

## Step 3: Save Contact Info

Generate a random UUID to use as a session ID (`wsess`). This links the contact info to the cart.

**Request** (via `ManageWixSite`):
```
POST https://manage.wix.com/v1/domain-registration-intents/upsert
```
Body:
```json
{
  "domainRegistrationIntent": {
    "domain": "mybakery.com",
    "sessionId": "<random-uuid>",
    "registrantContact": {
      "firstName": "John",
      "lastName": "Smith",
      "email": "john@email.com",
      "phone": "+1.5551234567",
      "address": {
        "streetAddress": "123 Main St",
        "city": "New York",
        "country": "US",
        "postalCode": "10001"
      }
    },
    "adminContact": { ... same as registrant ... },
    "techContact": { ... same as registrant ... }
  }
}
```

Use the same contact info for registrant, admin, and tech contacts (standard practice for individual registrations).

Phone format: `+{countryCode}.{number}` (e.g. `+1.5551234567`, `+972.544738293`).

If the API returns a validation error:
- Show the user exactly which fields have issues (missing, invalid format, etc.)
- Ask them to provide corrected values for those specific fields
- Retry the upsert with the corrected data
- Some TLDs require extra fields (e.g. .com.br needs an identification number, .it needs entity type). If the error mentions TLD-specific requirements, explain what's needed and ask the user to provide it.

---

## Step 4: Create Cart and Checkout Link

**Important**: If the user selected a site in Step 1b, use `CallWixSiteAPI` (with the site's `siteId`) for ALL cart operations below. This creates the cart in the site's context so the checkout link with `?msid=` works correctly. If no site was selected, use `ManageWixSite` (account-level).

### 4a: Cancel any existing cart

```
POST https://manage.wix.com/_api/premium-cart/v1/carts/active/cancel
```
Body: `{}`

This clears any leftover cart. If there's no active cart, this returns successfully anyway.

### 4b: Get a fresh cart

```
GET https://manage.wix.com/_api/premium-cart/v1/carts/active
```

This creates a new cart if none exists and returns it.

### 4c: Add domain and addon to cart

```
PATCH https://manage.wix.com/_api/premium-cart/v1/carts/active/add-items
```
Body:
```json
{
  "lineItems": [
    {
      "productInfo": {
        "productId": "<productId from Step 2a>",
        "productTypeId": "72af0602-1321-4897-8299-f507480b2bb8"
      },
      "cycle": {
        "cycleDuration": { "count": 1, "unit": "YEAR" },
        "cycleType": "RECURRING"
      },
      "metadata": {
        "domainName": "mybakery.com",
        "wsess": "<same random-uuid from Step 3>",
        "core": "true"
      }
    }
  ]
}
```

Set `cycle.cycleDuration.count` to the number of years the user chose.

Add a second line item for the addon (based on the user's choice from Step 2b):

```json
{
  "productInfo": {
    "productId": "<addon product ID from Step 2b>",
    "productTypeId": "b3d86a1d-9db3-4f69-bd54-c132808856b1"
  },
  "cycle": {
    "cycleDuration": { "count": 1, "unit": "YEAR" },
    "cycleType": "RECURRING"
  },
  "metadata": {
    "domainName": "mybakery.com",
    "wsess": "<same random-uuid from Step 3>"
  }
}
```

Use the same cycle duration for the addon as for the domain.

### 4d: Provide checkout link

Once the cart is populated, give the user a checkout link:

- **If a site was selected** (Step 1b): `[Click here to complete your purchase](https://manage.wix.com/cart/checkout?msid={siteId})`
- **No site / standalone purchase**: `[Click here to complete your purchase](https://manage.wix.com/cart/checkout)`

This opens the checkout page with the pre-filled cart. The user only needs to complete payment.

---

## Error Handling

| Error Code | Description | Action |
|------------|-------------|--------|
| `DOMAINS_UNSUPPORTED_TLD` | TLD not supported by Wix | Suggest alternatives using Suggest Domains API |
| `access_denied` or `403` on domain search APIs | Auth issue | These are public APIs -- do not add extra auth headers |
| Offering API returns no products | TLD not supported by Wix | Tell user to try a different TLD (.com, .net, .org) |
| Intent API validation error | Missing/invalid contact fields | Show the error, ask user to correct, retry |
| Cart add-items fails | Product ID or format issue | Verify product ID came from offering API response |

---

## Example Flows

### Flow 1: Full purchase (happy path)

1. User: "Buy me mybakery.com"
2. Check availability -> available: true
3. Get pricing for .com -> show cycles table
4. User picks 1 year
5. Ask about privacy -> user says yes
6. Preview contact info -> shows existing info -> user confirms
7. Save contact via intent API (generate wsess UUID)
8. Cancel old cart -> get fresh cart -> add domain + privacy addon
9. Share checkout link: [Complete your purchase](https://manage.wix.com/cart/checkout)

### Flow 2: Domain taken, suggest alternatives, then full purchase

1. User: "I want to buy coolstartup.com"
2. Check availability -> available: false
3. Suggest alternatives with query "coolstartup" -> show 10 options
4. User picks "coolstartup.online"
5. Get pricing for .online -> show cycles table
6. User picks 2 years
7. Ask about privacy -> user says no
8. Preview contact info -> empty -> ask user for details
9. User provides: name, email, phone, address
10. Save contact via intent API
11. Create cart with domain only (no addon), 2-year cycle
12. Share checkout link

### Flow 3: Brainstorming from scratch

1. User: "I need a domain for my pancakes restaurant"
2. Suggest domains with query "pancakes restaurant" -> show 10 options
3. User picks "stackedpancakes.com"
4. Get pricing for .com -> show cycles
5. User picks 1 year, wants privacy
6. Confirm contact info -> user confirms existing info
7. Save contact, create cart, share checkout link

### Flow 4: Purchase with site connection

1. User: "Buy mybakery.com and connect it to my site"
2. Check availability -> available: true
3. Ask which site -> call ListWixSites -> user picks "My Bakery Site" (msid: abc-123)
4. Site has premium plan -> "Great, we'll connect it after purchase"
5. Get pricing, user picks 1 year, wants privacy, confirms contact info
6. Save contact, create cart, share checkout link with msid: `https://manage.wix.com/cart/checkout?msid=abc-123`

### Flow 5: No premium site, suggest bundle

1. User: "I want mybakery.com for my website"
2. Check availability -> available: true
3. Call ListWixSites -> user picks "My Bakery Site" -> site has no premium plan
4. "Your site doesn't have a premium plan. You can get this domain free for the first year by upgrading! Want the bundle deal?"
5. User says yes -> share: [Get domain free with a site plan](https://manage.wix.com/premium-domains/split-page?domainName=mybakery.com)

### Flow 6: Unsupported TLD

1. User: "Buy mysite.io"
2. Check availability -> DOMAINS_UNSUPPORTED_TLD
3. Tell user .io is not supported, suggest alternatives with query "mysite"
4. User picks "mysite.online"
5. Continue with full purchase flow (pricing, privacy, contact, cart, checkout)
