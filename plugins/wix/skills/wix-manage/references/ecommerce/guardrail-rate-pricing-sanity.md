---
name: "Guardrail: Rate Pricing Sanity"
description: Validates shipping rate pricing against AOV and catalog data. Flags excessive rates, per-item penalties, unreachable free shipping thresholds, and backup rate sticker shock.
layer: guardrail
---
# Guardrail: Rate Pricing Sanity

## When to use

Run these checks when evaluating existing shipping rates or before creating/updating shipping rate configurations. All thresholds are relative to the store's Average Order Value (AOV).

---

## Check 1: Excessive shipping cost

**Threshold**: Any rate `amount` > AOV x 0.15 (15%)

**Why**: Shipping costs above 15% of order value are a top reason for cart abandonment. Customers who see disproportionately high shipping fees frequently abandon their carts.

**Detection**:
- For each shipping rate, compare `amount` against `AOV × 0.15`
- If exceeded → flag:

> "Shipping rate '{title}' charges ${amount}, which is {pct}% of your average order value (${AOV}). Shipping costs above 15% of order value are a top reason for cart abandonment."

---

## Check 2: Per-item penalty (multiplyByQuantity)

**Trigger**: `multiplyByQuantity: true` on any shipping rate

**Why**: Per-item shipping charges penalize larger orders and discourage customers from adding more items to cart.

**Detection**:
- Find all rates with `multiplyByQuantity: true`
- Calculate the impact for a typical multi-item order:

> "Your '{title}' rate charges per item (${amount} x quantity). A 5-item order costs ${amount x 5}. Switch to a flat rate or tiered pricing to encourage larger orders."

---

## Check 3: Free shipping threshold too high

**Threshold**: Free shipping threshold > AOV x 2

**Why**: If the free shipping minimum is more than double the average order, very few customers will ever qualify. The threshold should be achievable — close enough to the AOV to encourage customers to add one more item.

**Detection**:
- Compare free shipping `threshold` against `AOV × 2`
- If exceeded → flag:

> "Your free shipping threshold (${threshold}) is {X}x your average order (${AOV}). Most customers won't reach it. Lower to ${AOV x 1.2} to make it achievable and drive larger orders."

---

## Check 4: Free shipping threshold too low

**Threshold**: Free shipping threshold < AOV x 0.8

**Why**: If the threshold is below the average order value, most customers already qualify for free shipping without adding anything to their cart. This provides no upsell incentive and may erode margins unnecessarily.

**Detection**:
- Compare free shipping `threshold` against `AOV × 0.8`
- If below → flag:

> "Your free shipping threshold (${threshold}) is below your average order value (${AOV}). Most customers already qualify, so this threshold isn't driving larger orders. Consider raising it to ${AOV x 1.2} to encourage add-on purchases."

---

## Check 5: Backup rate sticker shock

**Threshold**: `backupRate.amount` > effective AOV x 0.15

**Why**: Backup rates apply when the primary carrier can't fulfill (e.g., remote address, service outage). If the backup rate is dramatically higher than normal shipping, customers experience sticker shock at checkout.

**Detection**:
- For each carrier's `backupRate`, compare `amount` against `effective_aov × 0.15`
- If exceeded → flag:

> "Backup rate of ${amount} is {pct}% of your average order value. When triggered, this will surprise customers with unexpectedly high shipping. Set the backup rate to 5-10% of average order value (${effective_aov x 0.05} - ${effective_aov x 0.10})."

---

## Check 6: Hidden surcharges

**Threshold**: Total `additionalCharges` across all carriers > AOV x 0.10

**Why**: Carrier surcharges (fuel, residential delivery, handling fees) add up. If the total surcharge burden exceeds 10% of the order value, it may negate the perceived value of the base shipping rate.

**Detection**:
- Sum all `additionalCharges` across active carriers
- Compare total against `AOV × 0.10`
- If exceeded → flag:

> "Carrier surcharges add ${total} to shipping costs. Combined with base rates, total shipping cost may deter customers. Review each surcharge to determine if it's necessary."

---

## Summary: Pricing sanity thresholds

| Check | Threshold | Action |
|---|---|---|
| Excessive rate | Rate > 15% of AOV | Flag — cart abandonment risk |
| Per-item penalty | `multiplyByQuantity: true` | Flag — discourages larger orders |
| Free threshold too high | Threshold > 2x AOV | Flag — unreachable for most customers |
| Free threshold too low | Threshold < 0.8x AOV | Flag — no upsell incentive, margin erosion |
| Backup rate shock | Backup > 15% of AOV | Flag — recommend 5-10% of AOV |
| Hidden surcharges | Total surcharges > 10% of AOV | Flag — review necessity |
