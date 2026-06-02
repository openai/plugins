---
name: "Guardrail: Margin Protection"
description: Safety constraints for discount percentages — global discount cap, minimum margin requirements, user override protocol, and percentage sanity checks.
layer: guardrail
---
# Guardrail: Margin Protection

## When to apply

Run before EVERY discount rule creation or update. Check both the new rule's discount AND the cumulative effect with existing active rules (stacking).

---

## Constraint 1: Global discount cap

The default maximum discount percentage (`discountMargin`) is **25%**.

Any discount rule that exceeds this cap should be flagged before creation:

> "This discount ({pct}%) exceeds the default cap of 25%. Proceeding only because you explicitly requested it."

Respect the cap unless user input explicitly overrides it.

---

## Constraint 2: Minimum margin requirement

The default minimum margin percentage (`minMarginPct`) is **15%**.

Never create a discount that would push the effective margin below 15% unless the user explicitly overrides this constraint.

If cost data is available, calculate:
- `effective_margin = (price - cost - discount_amount) / price × 100`
- If `effective_margin < minMarginPct` → block and explain the margin impact.

---

## Constraint 3: Percentage sanity checks

| Discount value | Action |
|---|---|
| Discount > 50% | Warn — "This discount is {pct}% off. A $100 product would sell for ${100 - pct}. Are you sure?" |
| Discount = 100% | Block unless explicitly confirmed — "This makes the product free." |
| Discount > 100% | Block always — "A discount cannot exceed 100%." |

---

## Constraint 4: User input override protocol (ABSOLUTE PRIORITY)

User input overrides ALL constraints — margin caps, discount caps, naming conventions, percentage limits.

**How it works:**

- If the user says "50% discount" and the cap is 25%, honor 50%.
- If the user says "set margin to 5%" and the minimum is 15%, honor 5%.
- Document which constraints were overridden in reasoning so there is a clear audit trail.

**Example reasoning output:**

> "Creating a 50% discount as requested. Note: this overrides the default 25% discount cap. The effective margin on a product with 60% gross margin would drop to 10%, below the default 15% minimum margin threshold. Proceeding per explicit user instruction."

---

## Constraint 5: Stacking cumulative check

When creating a new discount, also check the cumulative effect with existing active rules:

1. Query all active discount rules that overlap in scope with the new rule.
2. Calculate the combined discount percentage (accounting for multiplicative stacking).
3. If the combined discount exceeds the global cap or violates the minimum margin, warn the merchant:

> "Combined with the existing '{existingRuleName}' ({existingPct}%), the total effective discount would be approximately {combinedPct}%. This exceeds the {cap}% cap / pushes margin below {minMarginPct}%."

---

## Summary: Decision matrix

| Scenario | Action |
|---|---|
| Discount ≤ 25% and margin ≥ 15% | Proceed |
| Discount > 25% but ≤ 50%, no user override | Warn, ask for confirmation |
| Discount > 25%, user explicitly requested | Proceed, document override |
| Discount > 50% | Warn with dollar example, ask for confirmation |
| Discount = 100% | Block unless explicitly confirmed |
| Discount > 100% | Block always |
| Combined stacking exceeds cap | Warn about cumulative effect |
| Margin drops below 15%, no user override | Block, explain margin impact |
| Margin drops below 15%, user override | Proceed, document override |
