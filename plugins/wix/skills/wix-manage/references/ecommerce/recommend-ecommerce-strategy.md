---
name: "Recommend: eCommerce Strategy"
description: Unified eCommerce recommendation skill — analyzes site data across ALL domains (discounts, shipping, and future domains) and generates up to 5 actionable recommendations. Single entry point for any "help my business" request. Tracking is built-in.
layer: R
references:
  - name: "API: Recommendation Tracking"
    path: ecommerce/api-recommendation-tracking.md
    load: false
  - name: "Goal: Increase AOV"
    path: ecommerce/goal-increase-aov.md
    load: false
  - name: "Goal: Clear Inventory"
    path: ecommerce/goal-clear-inventory.md
    load: false
  - name: "Goal: Seasonal Revenue"
    path: ecommerce/goal-seasonal-revenue.md
    load: false
  - name: "Goal: Drive Cross-Sells"
    path: ecommerce/goal-drive-cross-sells.md
    load: false
  - name: "Goal: Reduce Cart Abandonment"
    path: ecommerce/goal-reduce-cart-abandonment.md
    load: false
  - name: "Setup: Coupons"
    path: ecommerce/setup-coupons.md
    load: false
---
# Recommend: eCommerce Strategy

>
> **After classifying domains in Step 4b**, load the matching goal skill with `ReadFullDocsArticle`:
> - **SEASONAL** → [Goal: Seasonal Revenue](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-seasonal-revenue)
> - **UPSELL_BOOST** / **SHIPPING** → [Goal: Increase AOV](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-increase-aov) (includes both discount and shipping flows)
> - **STOCK_MOVER** → [Goal: Clear Inventory](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-clear-inventory)
> - **BUNDLE_AND_SAVE** → [Goal: Drive Cross-Sells](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-drive-cross-sells)
> - **ABANDONED_CART** → [Goal: Reduce Cart Abandonment](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-reduce-cart-abandonment)
>
> **If COUPON mechanism in Step 4c**, load:
> - [Setup: Coupons](https://dev.wix.com/docs/api-reference/business-solutions/coupons)

## EXECUTION RULES — READ BEFORE ANYTHING ELSE

**You are an operator, not a consultant.** When this recipe is activated:

1. **Do NOT ask clarifying questions — start executing immediately from Step 1.** The merchant's request contains enough information. The analysis steps will determine which domains and strategies apply.
2. **Do NOT produce recommendations before calling the mandatory APIs.** If you skip the API calls and generate advice from assumptions, your output is wrong — even if it sounds reasonable.
3. **Execute every step in order.** Do not skip steps. Do not merge steps. Do not answer "in the meantime."
4. **Use ONLY data returned by API calls.** Never substitute reasoning, general knowledge, or doc summaries for live data. Every number you cite in `reasoning` MUST come directly from an API response — do NOT assume, infer, or fabricate data.
5. **If a call fails or is blocked, report the exact blocker.** Do not work around it with assumptions.
6. **All API calls use `CallWixSiteAPI`.** The internal tool names (getSiteData, getCatalogAnalytics, etc.) are NOT directly callable.
7. **Generate recommendations across ALL relevant domains** — not just discounts. Consider shipping, discounts, and any other domain that the data supports.

---

## Step 1: Resolve the target site

**MANDATORY — do this first.**

If you don't already have a `siteId`, call `ListWixSites` to find it.

If the merchant mentioned a site name, match it. If only one site exists, auto-select it. Store the `siteId` — every subsequent API call requires it.

**Do not proceed without a siteId.**

---

## Step 2: Load recommendation history (Tracking)

**MANDATORY — do NOT skip unless the user said `SKIP_TRACKING` or "don't track".**

Query the tracking database for existing recommendations on this site:

```
CallWixSiteAPI(
  url: "https://manage.wix.com/_api/agentic-recommendations/v1/agentic-recommendations/query",
  method: "POST",

  body: { "query": { "filter": {}, "cursorPaging": { "limit": 50 } } }
)
```

**Use the returned history to inform your analysis:**

| State | How to use it |
|---|---|
| `PROPOSED` | Don't re-propose — ask about the pending one |
| `DONE` | Don't re-propose — consider complementary recommendations |
| `REJECTED` | Do NOT re-propose. If `rejectionPermanent` is true, never suggest this action type again |
| `FAILED` | Offer to retry or suggest alternative |
| `EXPIRED` | Can re-propose if still relevant with fresh data |

If the query returns empty results or fails, continue — this is a fresh session.

---

## Step 3: Gather site data

**MANDATORY API CALL — do not skip.**

```
CallWixSiteAPI(
  url: "https://www.wix.com/wix-profile-client/v4/profile/metasite",
  method: "POST",

  body: {
    "fields": [
      "language",
      "merchant_business_country",
      "suggested_main_industry",
      "suggested_sub_industry",
      "last_30_days_distinct_visitors",
      "last_30_days_orders_count",
      "online_gpv_last_30_days",
      "payment_currency"
    ]
  }
)
```

**Available fields:**

| Field ID | Type | Description | Used for |
|---|---|---|---|
| `language` | STRING | Wix site language code | Locale-aware recommendations |
| `merchant_business_country` | STRING | Merchant's business country (ISO alpha-2) | Holiday detection, region analysis, shipping |
| `suggested_main_industry` | STRING | Dominant industry in last 30 days (user growth model) | Domain classification, goal selection |
| `suggested_sub_industry` | STRING | Dominant sub-industry in last 30 days | Domain classification |
| `last_30_days_distinct_visitors` | LONG | Distinct visitors in last 30 days (incl. app sessions) | Traffic-based thresholds |
| `last_30_days_orders_count` | LONG | Order count in last 30 days | AOV calculation, goal selection |
| `online_gpv_last_30_days` | LONG | Online Gross Payment Volume in last 30 days (site currency units) | Revenue analysis, AOV calculation |
| `payment_currency` | STRING | Store payment currency code (ISO-4217) | Discount/shipping amount formatting |

**Response shape** — each field is a nested object; missing fields = no data for this site:

```json
{
  "metaSiteId": "<msid>",
  "fields": {
    "language":                    { "aSingleValue": { "aString": "en-US" } },
    "merchant_business_country":   { "aSingleValue": { "aString": "US" } },
    "payment_currency":            { "aSingleValue": { "aString": "USD" } },
    "last_30_days_orders_count":   { "aSingleValue": { "aLong": "2141" } },
    "online_gpv_last_30_days":     { "aSingleValue": { "aLong": "526550" } }
  }
}
```

Extracting values:
- String: `fields.<name>.aSingleValue.aString`
- Number: `fields.<name>.aSingleValue.aLong` — **returned as a JSON string, parse to int before arithmetic**

**Derived value:** `aov = parseInt(online_gpv_last_30_days) / parseInt(last_30_days_orders_count)` — in `payment_currency` units

**Currency rule:** All monetary values (`online_gpv_last_30_days`, `aov`, discount thresholds, shipping amounts) are in the site's `payment_currency`. Never assume USD. Always display and compute amounts using `payment_currency`.

**STOP if `merchant_business_country`, `suggested_main_industry`, or `online_gpv_last_30_days` are missing or null.** Report: "Cannot generate recommendations — missing required site data: {fields}."

---

## Step 3b: Validate the request

Check if the merchant's request includes anything unsupported. **Reject** these:

| Unsupported request | Response |
|---|---|
| Buy one get one (BOGO) | Explain: not supported by Discount Rules API |
| Fixed-price bundles ("3 for $100") | Explain: requires custom pricing logic |
| Unrelated to eCommerce | Decline politely |

If valid, continue.

---

## Step 4: Identify applicable domains

Based on the merchant's request AND the site data, determine which domains to analyze. **Multiple domains can be active simultaneously.**

| Domain | When to activate | Data signals |
|---|---|---|
| **DISCOUNTS** | Merchant mentions sales, promotions, revenue, AOV, clearance, holidays, coupons. **Also activate if no specific domain is mentioned** (default). | Always — site data contains discount metrics |
| **SHIPPING** | Merchant mentions shipping, delivery, checkout conversion, cart abandonment. **Also activate proactively** if site data suggests shipping issues. | High visitors + low orders may indicate shipping friction |
| **ABANDONED_CART** | Activate proactively if site data shows abandoned carts with no active recovery automation. No merchant trigger needed — detect from data. | `currentDiscounts` empty or no cart recovery automation visible |

**Priority rule**: If the merchant mentions a specific holiday/event/date, the DISCOUNTS domain MUST use the **SEASONAL** strategy — even if other signals like "boost sales" or "increase revenue" could match other goals. Holidays are time-sensitive and take priority over general intent.

**If the request is generic** (e.g., "boost my sales", "help my business"), **activate ALL domains**. The best recommendations will come from analyzing every angle.

**If the request targets a specific domain** (e.g., "give me a coupon", "fix my shipping rates", "set up a gift card"), **activate ONLY that domain**. Do not generate cross-domain recommendations — focus all 5 recommendation slots on the requested domain. The merchant asked for something specific; respect that focus.

---

## Step 4b: Load domain-specific goal skills

**MANDATORY — load the matching goal skill(s) now using `ReadFullDocsArticle`.** These contain detailed strategy logic, KPIs, margin tiers, campaign window calculations, and guardrails that you MUST follow.

**For DISCOUNTS domain — classify the discount goal and load it:**

| Discount goal | Trigger | Load this skill |
|---|---|---|
| SEASONAL | Holiday/event/date mentioned | [Goal: Seasonal Revenue](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-seasonal-revenue) |
| UPSELL_BOOST | "increase AOV", "spend more", "upsell" | [Goal: Increase AOV](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-increase-aov) |
| STOCK_MOVER | "clear inventory", "overstock", "clearance" | [Goal: Clear Inventory](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-clear-inventory) |
| BUNDLE_AND_SAVE | "bundle", "cross-sell", "buy together" | [Goal: Drive Cross-Sells](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-drive-cross-sells) |
| Generic (no clear goal) | "boost sales", ambiguous | Default to SEASONAL if holiday nearby, else UPSELL_BOOST |

**For SHIPPING domain — load the same goal as discounts.** Shipping flows (free shipping threshold, rate optimization) serve the same business goals as discount flows. Load the matching discount goal above — it now includes shipping flow references.

**For ABANDONED_CART domain — load the cart abandonment goal:**

[Goal: Reduce Cart Abandonment](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/goal-reduce-cart-abandonment)

**The goal skill will instruct you to load flow and guardrail skills** — follow those instructions. This chain provides the detailed execution logic you need for high-quality recommendations.

**Do NOT skip this step.** The goal/flow/guardrail skills contain critical constraints (margin tiers, campaign windows, conflict checks) that prevent bad recommendations.

---

## Step 4c: Determine mechanism — Automatic Discount or Coupon

**Only for DISCOUNTS domain. Skip if DISCOUNTS is not active.**

| Merchant says | Mechanism |
|---|---|
| "sale", "promotion", "discount for everyone" | **AUTOMATIC** |
| "coupon", "code", "promo code", "voucher" | **COUPON** |
| "discount for subscribers", "influencer code" | **COUPON** |
| Unclear | **Ask the merchant** |

**If unclear, ask:** "Would you like this to apply automatically to everyone, or as a coupon code?"

**If COUPON is selected**, load the coupon setup reference with `ReadFullDocsArticle`:
[Setup: Coupons](https://dev.wix.com/docs/api-reference/business-solutions/coupons)

---

## Step 5: Analyze catalog

**Permission**: `ecom:discounts_recommendations:v1:recommendation:build_recommendation`

Call both APIs concurrently:

### Call 1: GetCatalogAnalytics

```
CallWixSiteAPI(
  url: "https://manage.wix.com/recommendations/v1/recommendations/get-catalog-analytics-tool",
  method: "POST",
  body: {
    "aggregates": <see table below>,
    "minMarginPct": 0.15
  }
)
```

Valid `aggregates` values: `op` ∈ `count|sum|avg|min|max|stddev|quantiles` · `field` ∈ `quantity|price|cost|profit|profitMargin|ordersCount` · `q` required only for `quantiles` (array of 0.0–1.0, max 20)

**Aggregates by goal:**

| Goal | `aggregates` array |
|---|---|
| UPSELL_BOOST | `[{"op":"count","field":"price"}, {"op":"quantiles","field":"price","q":[0.5,0.75,0.9]}, {"op":"avg","field":"profitMargin"}]` |
| BUNDLE_AND_SAVE | `[{"op":"min","field":"price"}, {"op":"max","field":"price"}, {"op":"avg","field":"profitMargin"}, {"op":"count","field":"price"}]` |
| STOCK_MOVER | `[{"op":"sum","field":"quantity"}, {"op":"sum","field":"ordersCount"}, {"op":"avg","field":"profitMargin"}]` |
| SEASONAL | `[{"op":"sum","field":"ordersCount"}, {"op":"quantiles","field":"price","q":[0.5,0.9]}, {"op":"avg","field":"profitMargin"}]` |
| SHIPPING | `[{"op":"count","field":"price"}, {"op":"quantiles","field":"price","q":[0.5,0.75]}, {"op":"avg","field":"profitMargin"}]` |

**Response shape:**
```json
{
  "categoryGroups": [
    {
      "categoryName": "Electronics",
      "fields": {
        "count()": 45,
        "quantiles([0.5,0.75,0.9],price)": [
          { "quantile": 0.5, "value": 89.99 },
          { "quantile": 0.75, "value": 149.99 }
        ],
        "avg(profitMargin)": 0.42
      }
    },
    { "categoryName": "All Products", "fields": { "count()": 120, "avg(profitMargin)": 0.35 } }
  ]
}
```
**Important**: Use "All Products" only for overall catalog stats. Exclude it from category-level analysis.

### Call 2: GetProductCatalogData

```
CallWixSiteAPI(
  url: "https://manage.wix.com/recommendations/v1/recommendations/get-product-catalog-data-tool",
  method: "POST",
  body: {
    "businessGoal": "<goal from Step 4>",
    "minMarginPct": 0.15,
    "catalogLimit": 30,
    "query": "<keywords from merchant request, or empty string>",
    "categoryNames": <category names if mentioned, or empty array>
  }
)
```

**Sort order applied server-side by `businessGoal`:**

| Goal | Sort order |
|---|---|
| UPSELL_BOOST | price DESC, ordersCount DESC |
| BUNDLE_AND_SAVE | price DESC, ordersCount DESC |
| STOCK_MOVER | quantity DESC, ordersCount ASC |
| SEASONAL / SHIPPING | ordersCount DESC |

**Response shape:**
```json
{
  "items": [
    {
      "id": "product-uuid",
      "name": "Premium Headphones",
      "quantity": 85,
      "price": 149.99,
      "profit": 67.50,
      "profitMargin": 0.45,
      "ordersCount": 23
    }
  ]
}
```
`price` and `profit` are in `payment_currency` units. `id` is the product UUID — use for `productIds` in rules.

### Step 5b: Convert category names to GUIDs (if using CATEGORY scope)

**MANDATORY before outputting any categoryIds.** Never output category names as IDs.

**Send only categories you plan to target — max 10 per call.**

```
CallWixSiteAPI(
  url: "https://manage.wix.com/recommendations/v1/recommendations/get-category-ids-tool",
  method: "POST",
  body: { "categoryNames": ["<top category 1>", "<top category 2>"] }
)
```

**Response:** `{ "categoryIds": ["a1b2c3d4-...", "b2c3d4e5-..."] }`

If `categoryIds` is empty: category doesn't exist — fall back to SITE scope and tell the merchant: "Could not resolve category '{name}', using site-wide scope instead."

### Failure handling

- Both calls fail: Fall back to SITE scope using only site profile data.
- One fails: Use whichever succeeded.

---

## Step 6: Generate recommendations across ALL active domains

**Only now — after data gathering — generate recommendations.**

Maximum **5 recommendations total** across all domains. Each recommendation includes its `domain` field.

### Discount recommendations (if DISCOUNTS domain active)

Use site data + catalog data to generate discount recommendations. Each should use a **different strategy**:

| Strategy | When to use | Key parameters |
|---|---|---|
| SEASONAL | Holiday/event within 30 days | Time-bounded, site-wide or category scope |
| UPSELL_BOOST | AOV data available | minSubTotal above current AOV |
| STOCK_MOVER | Products with high stock + low orders | Deeper discounts on slow movers |
| BUNDLE_AND_SAVE | Many low-priced items | minItemQuantity conditions |

**Scope selection** (in order of preference):

1. **CATEGORY** (preferred): High-opportunity category from analytics. Must have GUID from GetCategoryIds.
2. **ITEMS** (specific): Individual products from catalog data. Max 5 product IDs.
3. **SITE** (fallback): When no clear category/product opportunity.

**Performance signals:**

| What you observe in the data | What to recommend |
|---|---|
| High visitors, low ordersCount | Site-wide discount to convert traffic |
| High AOV, few items per order | BUNDLE_AND_SAVE |
| Products with high stock + low orders | STOCK_MOVER |
| Holiday within 30 days | SEASONAL |

**Discount constraints:**
- Discount must not exceed `discountMargin` from site data (unless merchant overrides)
- Round percentages to 5/10/15/20/25% unless merchant specified exact value
- All categoryIds must be GUIDs from GetCategoryIds
- All productIds must be from GetProductCatalogData
- Mechanism must be AUTOMATIC or COUPON per Step 4c

### Shipping recommendations (if SHIPPING domain active)

Analyze the site's shipping configuration using the rules below. All shipping recommendations use `domain: "shipping"`.

**Externally managed regions:** Regions where `deliveryCarriers[].appId` matches an external carrier (e.g., Shippo) — exclude from ALL analysis. Do not recommend changes to these.

**Shipping analysis rules — evaluate each and recommend where data supports:**

| Rule | Finding | Recommendation |
|---|---|---|
| **Coverage** | Active region with zero shipping options | CRITICAL — `create_shipping_option` for that region |
| **Coverage** | Domestic country not covered by any region | CRITICAL — `activate_region` or create domestic region |
| **Coverage** | Inactive regions with shipping options | `activate_region` or clean up orphaned options |
| **Free Shipping** | No free shipping option anywhere | `create_shipping_option` with AOV-calibrated threshold (1.2-1.5x AOV) |
| **Free Shipping** | Free shipping threshold > 2x AOV | Lower threshold — too high for most customers |
| **Rates** | Flat rate > 15% of AOV | Reduce rate or add conditional tiering — sticker shock risk |
| **Rates** | All flat rates, no conditional pricing | Add threshold-based tiers for better conversion |
| **Rates** | Per-item pricing enabled | Review — usually causes unexpectedly high totals |
| **Carrier** | No backup rate on carrier regions | `enable_backup_rate` as fallback |
| **Options** | Too many options per region (> 5) | Consolidate — choice paralysis reduces conversion |
| **Options** | Only 1 option per region | Add at least one alternative (e.g., express tier) |

**Shipping action types:** `create_shipping_option`, `update_shipping_option`, `enable_backup_rate`, `activate_region`.

**Priority order:** CRITICAL blockers (no options, no coverage) → Conversion-linked (no free shipping, high rates) → Revenue opportunities (international, tiered pricing) → Configuration improvements (consolidate, add estimates).

### Abandoned cart recommendations (if ABANDONED_CART domain active)

Detect if the merchant has significant cart abandonment without active recovery. All abandoned cart recommendations use `domain: "abandoned_cart_recovery"`.

**Eligibility gate (BOTH conditions required):**
1. Cart abandonment recovery automation is **NOT active** on the site
2. Estimated missing sales >= $200 over the last 30 days

**If either condition fails, do NOT generate abandoned cart recommendations.**

**Urgency thresholds based on missing sales (USD, last 30 days):**

| Missing sales | Urgency |
|---|---|
| >= $1,000 | HIGH |
| $200 — $999 | MEDIUM |
| < $200 | Do not recommend |

**Action type:** `activate_abandoned_cart_recovery`

**Params must include:** `automation_key` ("wix_e_commerce-cart_abandonment"), `missing_sales_usd` (integer, rounded), `abandoned_cart_count` (integer), `window_days` (always 30).

**Title pattern:** "Recover $[missing_sales_usd] in abandoned carts"

**Reasoning MUST cite:** automation is inactive, exact cart count, exact missing sales USD, 30-day window, and why the urgency level was chosen.

### Cross-domain balance

- If request is generic, aim for recommendations from **multiple domains** (e.g., 2-3 discount + 1-2 shipping + abandoned cart if eligible)
- If request targets a specific domain, focus all slots on that domain
- Rank by business impact: CRITICAL blockers first, then conversion-linked, then revenue opportunities

---

## Step 7: Validate before returning

1. **Conflict check**: Do existing active discounts/coupons overlap with your recommendation scope? Warn about stacking.
2. **Margin check**: Discounts within `discountMargin` cap.
3. **No duplicates**: Each recommendation targets a different scope/action combination.
4. **No contradictions**: Don't recommend opposite actions in the same domain.
5. **Strategy diversity**: Discount recommendations use different strategies where possible.
6. **Mechanism match**: Discount mechanism matches Step 4c determination.
7. **ID validity**: All categoryIds are GUIDs from GetCategoryIds. All productIds are from GetProductCatalogData.
8. **Rounding**: Discount percentages round to 5/10/15/20/25% unless merchant specified exact value.
9. **Data-backed**: Every recommendation must reference specific data from API responses.
10. **Domain labeled**: Every recommendation has the correct `domain` field.

---

## Step 8: Persist recommendations to database (Tracking)

**MANDATORY — do NOT skip unless the user said `SKIP_TRACKING`.**

Call `BatchCreate` to persist ALL recommendations as PROPOSED:

```
CallWixSiteAPI(
  url: "https://manage.wix.com/_api/agentic-recommendations/v1/agentic-recommendations/batch-create",
  method: "POST",

  body: {
    "agenticRecommendations": [
      {
        "title": "<recommendation title>",
        "reasoning": "<recommendation reasoning>",
        "domain": "<discounts|shipping|abandoned_cart_recovery>",
        "urgency": "<CRITICAL|HIGH|MEDIUM|LOW>",
        "advice": {
          "action": "<action type>",
          "params": <params object>,
          "successCriteria": "<how to verify success>"
        }
      }
    ],
    "conversationId": "<conversationId>"
  }
)
```

**Save the `id` and `revision` from each result.** Include them in the output.

If BatchCreate fails, report the error and include recommendations without tracking IDs.

---

## Output format

```json
{
  "recommendations": [
    {
      "id": "<tracking-id from BatchCreate, or omit if tracking failed>",
      "revision": "<revision from BatchCreate>",
      "title": "Memorial Weekend Flash Sale — 15% Off Orders Over $250",
      "reasoning": "AOV is $242 (online_gpv_last_30_days / last_30_days_orders_count). merchant_business_country is US, Memorial Day is within 7 days. Setting $250 threshold nudges carts above AOV while staying within 25% discount cap.",
      "domain": "discounts",
      "urgency": "HIGH",
      "advice": {
        "action": "apply_discount",
        "params": {
          "mechanism": "AUTOMATIC",
          "scope": "SITE",
          "categoryIds": [],
          "productIds": [],
          "name": "Memorial Weekend Sale",
          "why": "Your AOV is $242. A 15% discount on orders over $250 encourages adding one more item.",
          "discountType": "PERCENTAGE",
          "discount": 15,
          "code": "",
          "usageLimit": 0,
          "limitPerCustomer": 0,
          "conditions": {
            "minItemQuantity": 0,
            "minSubTotal": 250,
            "startDate": "2026-05-23",
            "endDate": "2026-05-26"
          }
        },
        "success_criteria": "15% discount applied site-wide for orders above $250 during Memorial Weekend"
      }
    }
  ]
}
```

### Field rules

| Field | Rule |
|---|---|
| `id` | GUID from tracking BatchCreate response (omit if tracking skipped/failed) |
| `title` | Short, actionable. Max 200 chars. Always English. |
| `reasoning` | **Must reference which API call returned the data.** Always English. |
| `domain` | `"discounts"`, `"shipping"`, or `"abandoned_cart_recovery"` (future: `"gift_cards"`, `"taxes"`) |
| `urgency` | `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` |
| `mechanism` | `AUTOMATIC` or `COUPON`. From Step 4c. Only for discounts domain. |
| `name` | Marketing headline, 2-5 words. Translate to site `language` if not English. |
| `why` | 1-2 sentences with specific data points from API responses. Translate to site `language`. |
| `code` | Only for COUPON mechanism. Memorable code, max 20 chars (e.g., "SAVE15"). |
| `scope` + IDs | For discounts: SITE = both empty, CATEGORY = categoryIds only (max 3), ITEMS = productIds only (max 5). |
| `success_criteria` | How to verify the recommendation was applied correctly |

### Valid action types by domain

| Domain | Action types |
|---|---|
| discounts | `apply_discount` |
| shipping | `create_shipping_option`, `update_shipping_option`, `enable_backup_rate`, `activate_region` |
| abandoned_cart_recovery | `activate_abandoned_cart_recovery` |

---

## Constraints

- Maximum 5 recommendations total across all domains
- Each discount recommendation must use a different strategy
- All data must come from API responses — no assumptions
- Respect discountMargin cap unless merchant overrides
- All IDs must be GUIDs from API responses
- Catalog queries limited to 30 items
- Every recommendation MUST be persisted via tracking before presenting (unless SKIP_TRACKING)
- Recommendations should span multiple domains when the request is generic
- Never recommend changes to externally managed (Shippo) shipping regions
