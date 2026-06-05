---
name: "Guardrail: Discount Conflicts"
description: Validation rules for detecting and preventing discount stacking conflicts, coupon overlap, and unintended deep discounts before applying new promotions. Covers automatic discount rules, coupon interactions, and safe discount limits.
layer: guardrail
references:
  - name: "Troubleshoot: Discount Not Applying"
    path: ecommerce/troubleshoot-discount-not-applying.md
    load: false
---
# Guardrail: Discount Conflicts

> **Related skills** (read with `ReadFullDocsArticle` if needed):
> - [Troubleshoot: Discount Not Applying](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/troubleshoot-discount-not-applying)

## When to use this guardrail

Run these checks **before** creating or updating any discount — whether automatic discount rule or coupon. Discount conflicts are one of the most common merchant mistakes — overlapping discounts silently stack and give customers a much deeper discount than intended. This is especially dangerous when **automatic discounts and coupons interact**, since merchants often forget that both mechanisms apply simultaneously.

---

## Check 1: Existing active discount rules on the same scope

**Why:** Wix eCommerce stacks automatic discount rules. If a 20% catalog-wide discount and a 15% collection discount both apply to the same product, the customer may get both applied.

**How to check:**

1. Query all active discount rules:

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

2. For each existing active rule, compare its scope against the new rule:
   - If both target `CATALOG` scope: **conflict** — both apply to all products
   - If new rule targets `CATALOG` and existing targets `COLLECTION`: **conflict** — catalog-wide includes that collection
   - If both target the same `COLLECTION` ID: **conflict** — same products affected
   - If both target the same `SPECIFIC_PRODUCTS` ID: **conflict** — same product

3. If a conflict is found, warn the merchant:
   > "There's already an active discount '{existingRuleName}' ({existingDiscount}%) that applies to the same products. Adding this new {newDiscount}% discount may stack, giving customers a combined discount. Would you like to deactivate the existing rule first, or proceed with both?"

---

## Check 2: Discount percentage sanity

**Why:** A discount above 50% is unusual and may indicate a typo (the merchant meant 15% not 50%). A discount of 100% makes the product free.

**Rules:**
- Discount > 50%: Warn — "This discount is {percentage}% off. Are you sure? This means a $100 product would sell for ${100 - percentage}."
- Discount = 100%: Block unless explicitly confirmed — "This would make the product free. Please confirm this is intentional."
- Discount > 100%: Block — "A discount cannot exceed 100%."

---

## Check 3: Time overlap with existing promotions

**Why:** Two promotions running simultaneously on overlapping products cause stacking during the overlap period.

**How to check:**

1. For the new rule's `activeTimeInfo` (start/end), check if any existing active rule has an overlapping time window on the same scope.
2. Overlap exists when: `existingStart < newEnd AND existingEnd > newStart`
3. If overlap found on the same scope: warn the merchant about the overlap period.

---

## Check 4: Cross-mechanism stacking (Automatic + Coupon)

**Why:** Automatic discounts and coupons stack with each other at checkout. A customer with a 20% coupon buying during a 20% automatic sale gets both applied — the effective discount is much deeper than either one alone. This is the most commonly overlooked stacking issue.

**How to check:**

1. If you are creating an **automatic discount**: Query active coupons that target overlapping products/collections.
2. If you are creating a **coupon**: Query active automatic discount rules that target overlapping products/collections.
3. If overlap found, warn the merchant with the combined impact:
   > "You have an active {automatic discount / coupon} '{name}' ({X}% off) that applies to the same products. If you create this {coupon / automatic discount}, customers will get BOTH discounts — a combined effective discount of approximately {combined}%. Is this intentional?"

**Key rule:** Only one coupon can be used per checkout, but automatic discounts have no such limit. The worst case is: multiple automatic discounts + one coupon all stacking on the same product.

---

## Check 5: Minimum profit margin

**Why:** Deep discounts on low-margin products can result in selling at a loss.

**Rules:**
- If the merchant has provided cost/margin information, verify that the discount doesn't reduce the price below cost
- If no cost information is available, warn for discounts > 40% as a general safety threshold

---

## Summary: Decision matrix

| Scenario | Action |
|---|---|
| No conflicts found | Proceed with creating the discount |
| Scope overlap with existing active automatic discount | Warn merchant, ask to deactivate existing or confirm stacking |
| Cross-mechanism stacking (automatic + coupon on same scope) | Warn merchant with combined effective discount percentage |
| Discount > 50% | Warn merchant, ask for confirmation |
| Discount = 100% | Block unless explicitly confirmed |
| Time overlap on same scope | Warn about overlap period |

## References

- [Discount Rules API (Automatic Discounts)](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/extensions/discounts/discount-rules/introduction)
- [Coupons API](https://dev.wix.com/docs/api-reference/business-solutions/coupons/coupons/introduction)
