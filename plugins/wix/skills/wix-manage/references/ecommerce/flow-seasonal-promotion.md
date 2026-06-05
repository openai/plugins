---
name: "Flow: Seasonal Promotion"
description: Creates event-driven promotional campaigns tied to holidays or seasonal events. Uses country and date context to identify upcoming events, calculates optimal campaign windows, and targets relevant categories.
layer: flow
references:
  - name: "Guardrail: Discount Conflicts"
    path: ecommerce/guardrail-discount-conflicts.md
    load: true
  - name: "Setup: Discount Rules"
    path: ecommerce/setup-discount-rules.md
    load: true
---
# Flow: Seasonal Promotion

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Guardrail: Discount Conflicts](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/guardrail-discount-conflicts)
> - [Setup: Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/setup-discount-rules)

Creates event-driven promotional discounts tied to holidays, shopping events, or seasonal milestones. The flow identifies upcoming events based on the site's country and current date, calculates optimal campaign start/end windows, and targets event-relevant product categories with appropriately sized discounts.

## Prerequisites

- Wix Stores installed on the site
- Products exist in the catalog
- Access to `getCatalogAnalytics`, `getProductCatalogData`, and `getSiteData` tools
- `current_date` available for event scheduling
- Site `country` known for region-specific event mapping

## Required APIs

- [Create Discount Rule](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/create-discount-rule)
- [Query Discount Rules](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/query-discount-rules)

---

## Step 1: Identify upcoming event

Use `current_date` and the site's `country` (from `getSiteData`) to identify major holidays or shopping events within the next 30 days.

### Common event calendar

| Event | Typical Date | Regions | Event-relevant categories |
|---|---|---|---|
| Valentine's Day | February 14 | Global | Gifts, Jewelry, Flowers, Fashion |
| Mother's Day | 2nd Sunday in May (US), March (UK) | Varies by country | Gifts, Home & Garden, Jewelry |
| Father's Day | 3rd Sunday in June (US) | Varies by country | Electronics, Tools, Fashion |
| Back to School | August-September | US, Global | School supplies, Kids, Fashion |
| Black Friday | 4th Friday in November | US, spreading globally | Electronics, Fashion, All categories |
| Cyber Monday | Monday after Black Friday | US, spreading globally | Electronics, Tech, All categories |
| Christmas | December 25 | Global (Christian-majority) | Gifts, Toys, Fashion, Home |
| Boxing Day | December 26 | UK, Canada, Australia | All categories (clearance) |
| New Year Sale | January 1-7 | Global | All categories (clearance) |
| Singles' Day | November 11 | China, spreading globally | Fashion, Electronics, Beauty |

If no event is within 30 days, inform the merchant and suggest either a general seasonal promotion or waiting for the next event.

---

## Step 2: Calculate campaign window

Determine the optimal start and end dates for the campaign based on the event date.

### Window calculation rules

- **Start date**: 3-5 days before the event date.
- **End date**: 1-3 days after the event (or through the following Tuesday for weekend events).
- **IMPORTANT**: If the calculated start date is before `current_date`, set start to `current_date`. Never schedule a campaign to start in the past.

### Examples

| Event | Event Date | Start | End | Notes |
|---|---|---|---|---|
| Valentine's Day | Feb 14 (Saturday) | Feb 10 (Tuesday) | Feb 16 (Monday) | Through the weekend after |
| Black Friday | Nov 27 (Friday) | Nov 23 (Monday) | Dec 1 (Tuesday) | Start Monday, end following Tuesday (covers Cyber Monday) |
| Cyber Monday | Nov 30 (Monday) | Nov 28 (Saturday) | Dec 1 (Tuesday) | Often combined with Black Friday window |
| Christmas | Dec 25 (Thursday) | Dec 20 (Saturday) | Dec 27 (Saturday) | Start ~5 days before, include Boxing Day |
| Mother's Day | May 10 (Sunday) | May 6 (Wednesday) | May 11 (Monday) | Through the day after |

### Combined events

For Black Friday + Cyber Monday, use a single extended window: start the preceding Monday/Tuesday, end the following Tuesday. Do not create two separate discount rules.

---

## Step 3: Gather catalog data

Call `getCatalogAnalytics` and `getProductCatalogData` concurrently.

**getCatalogAnalytics** call:
```
aggregates: sum(ordersCount), quantiles([0.5, 0.9], price), avg(profitMargin)
```

**getProductCatalogData** call:
```
ordered: ordersCount DESC
```

This sort order surfaces the best-selling products first — seasonal campaigns should lead with proven sellers to maximize revenue.

Save the following values:
- `total_orders` — overall sales volume
- `price_p50`, `price_p90` — price distribution for discount sizing
- `avg_profit_margin` — sets discount ceiling
- Top products by sales volume

---

## Step 4: Focus on event-relevant categories

Map the identified event to relevant product categories:

| Event | Priority Categories | Fallback |
|---|---|---|
| Valentine's Day | Gifts, Jewelry, Flowers, Fashion | Site-wide |
| Black Friday / Cyber Monday | Electronics, Fashion, Home | Site-wide (broad event) |
| Christmas | Gifts, Toys, Home Decor, Fashion | Site-wide |
| Back to School | School Supplies, Kids, Fashion | Site-wide |
| Mother's Day / Father's Day | Gifts, relevant verticals | Site-wide |

If the merchant's catalog matches an event-relevant category, target that category specifically. If no clear match exists, use site-wide scope.

---

## Step 5: Create campaign name

Build a compelling campaign name using the event/period name:

| Event | Example Campaign Names |
|---|---|
| Black Friday | "Black Friday Flash Deal", "Black Friday Blowout" |
| Cyber Monday | "Cyber Monday Special", "Cyber Monday Deals" |
| Christmas | "Holiday Season Sale", "Christmas Gift Sale" |
| Valentine's Day | "Valentine's Day Special", "Love Day Sale" |
| New Year | "New Year Clearance", "Fresh Start Sale" |
| Generic seasonal | "Spring Sale", "Summer Savings", "Fall Collection Sale" |

Keep names concise and recognizable. The name is internal (not shown to customers in checkout) but helps merchants manage their promotions.

---

## Step 6: Determine discount scope

- **CATEGORY** (preferred for event-relevant promotions): Target the event-relevant category with the highest margin and product count.
- **SITE** (for broad events): Use for events like Black Friday where the expectation is store-wide deals.

Avoid ITEMS scope for seasonal campaigns — seasonal promotions are typically broad rather than targeting individual products.

---

## Step 7: Convert category names to GUIDs (if CATEGORY scope)

If scope is CATEGORY, call `getCategoryIds` to convert category names to GUIDs.

- Never use category names as scope IDs — always use the GUID.
- Exclude the "All Products" system category.
- Max 3 categoryIds per discount rule.

---

## Step 8: Run guardrail checks

**Run the Guardrail: Discount Conflicts checks before creating the rule.**

1. Query existing active discount rules:

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules/query`

**Request**:
```json
{
  "query": {
    "filter": {
      "active": true
    },
    "paging": {
      "limit": 100
    }
  }
}
```

2. Check for time overlap — seasonal promotions have defined windows, so check that no existing rule covers the same period on the same scope.
3. Check for scope overlap — a seasonal category discount stacking with an existing catalog-wide discount could create unexpectedly deep combined discounts.
4. Check for coupon stacking — seasonal events often have high coupon usage.
5. If conflicts found, present to merchant and get confirmation.

---

## Step 9: Create the discount rule with campaign window

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/discount-rules`

**Request** — Black Friday 20% off electronics category, Monday-Tuesday window:
```json
{
  "discountRule": {
    "name": "Black Friday Flash Deal",
    "active": true,
    "activeTimeInfo": {
      "start": "2026-11-23T00:00:00.000Z",
      "end": "2026-12-01T23:59:59.000Z"
    },
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "electronics-category-guid",
          "type": "COLLECTION"
        }
      }
    ]
  }
}
```

**Response**:
```json
{
  "discountRule": {
    "id": "f6a7b8c9-d0e1-2345-f012-456789012345",
    "revision": "1",
    "name": "Black Friday Flash Deal",
    "active": true,
    "activeTimeInfo": {
      "start": "2026-11-23T00:00:00.000Z",
      "end": "2026-12-01T23:59:59.000Z"
    },
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 20
        },
        "scope": {
          "id": "electronics-category-guid",
          "type": "COLLECTION"
        }
      }
    ]
  }
}
```

**Request** — Valentine's Day site-wide 15% off:
```json
{
  "discountRule": {
    "name": "Valentine's Day Special",
    "active": true,
    "activeTimeInfo": {
      "start": "2026-02-10T00:00:00.000Z",
      "end": "2026-02-16T23:59:59.000Z"
    },
    "discounts": [
      {
        "discount": {
          "discountType": "PERCENTAGE",
          "percentage": 15
        },
        "scope": {
          "id": "catalog",
          "type": "CATALOG"
        }
      }
    ]
  }
}
```

Save the returned `id` and `revision` for later management.

---

## Step 10: Verify and remind about deactivation

1. Query discount rules to confirm the new rule exists and is `active: true`
2. Verify the `activeTimeInfo` window is correctly set
3. Report to the merchant:
   > "{Campaign name} is live: {discount}% off {scope description} from {start_date} to {end_date}. The discount will apply automatically at checkout during this window."

4. **IMPORTANT — Deactivation reminder**: There is no native auto-deactivation in Wix discount rules. Even though `activeTimeInfo.end` is set, the rule remains in the system after expiration. Remind the merchant:
   > "Note: After {end_date}, the discount will no longer apply at checkout, but the rule will remain active in your dashboard. You may want to deactivate or delete it after the promotion ends to keep your discount rules tidy."

---

## Branching logic

| Merchant intent | Event | Scope | Window |
|---|---|---|---|
| "Run a Black Friday sale" | Black Friday | Electronics/Fashion CATEGORY or SITE | Mon before through following Tue |
| "Valentine's promotion on gifts" | Valentine's Day | Gifts CATEGORY | 3-5 days before through day after |
| "Christmas sale on everything" | Christmas | CATALOG (site-wide) | ~5 days before through Dec 26 |
| "Seasonal promotion" (generic) | Next upcoming event for site's country | Determined by analytics | Standard 3-5 day lead, 1-3 day tail |
| "30% off for Cyber Monday" (explicit) | Cyber Monday | As specified | User-defined or standard window |
| No event within 30 days | None | N/A | Inform merchant; suggest general promotion instead |

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `DISCOUNT_RULE_NOT_FOUND` | Rule ID doesn't exist | Re-query discount rules for current IDs |
| `REVISION_MISMATCH` | Revision doesn't match | Re-fetch rule for latest revision, then retry |
| No upcoming event | No major holiday within 30 days of current_date | Inform merchant; suggest a general promotion or ask for a specific event |
| Start date in the past | Calculated start < current_date | Set start to current_date |
| Country not available | Site country unknown from getSiteData | Use global events (Black Friday, Christmas) as fallback |
| Category GUID not found | Event-relevant category doesn't exist in merchant's catalog | Fall back to SITE scope |
| Time conflict with existing rule | Another seasonal promotion overlaps the same window | Present conflict; suggest adjusting window or deactivating the existing rule |

## References

- [Discount Rules API](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/introduction)
