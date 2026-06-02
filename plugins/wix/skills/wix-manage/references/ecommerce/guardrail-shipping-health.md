---
name: "Guardrail: Shipping Health"
description: Shipping health score calculation (CRITICAL/POOR/FAIR/GOOD/EXCELLENT) with exact scoring criteria. Includes the mandatory business context filter for international shipping recommendations.
layer: guardrail
references:
  - name: "Troubleshoot: Checkout Delivery Drop-off"
    path: ecommerce/troubleshoot-checkout-delivery-dropoff.md
    load: false
---
# Guardrail: Shipping Health

> **Related skills**:
> - [Troubleshoot: Checkout Delivery Drop-off](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/troubleshoot-checkout-delivery-dropoff)

## When to use

Calculate the shipping health score whenever evaluating a store's shipping configuration. Use this score to prioritize recommendations and determine urgency of shipping issues.

---

## Health score levels

### CRITICAL

Any of the following conditions:

- `delivery_profiles` is empty AND `shipping_options` is empty
- All regions across all profiles have `active: false`

**Implication**: The store cannot ship any orders. Immediate action required.

### POOR

Any of the following conditions:

- Only 1 delivery profile with empty regions
- Only 1 shipping option total
- `delivery_step_cvr` < 50% with shipping issues detected
- All carriers have `backupRate.active: false`

**Implication**: Shipping is minimally functional but has significant gaps that are likely causing lost sales.

### FAIR

All of the following conditions:

- 1-2 delivery profiles with 1-2 active regions
- 2-4 shipping options
- No free shipping option available
- OR: `delivery_step_cvr` between 50-65%

**Implication**: Basic shipping is working but missing key elements that drive conversion.

### GOOD

All of the following conditions:

- 1+ delivery profiles with both domestic and international regions
- 3-5 shipping options including at least one free shipping option
- 1+ active carriers
- `delivery_step_cvr` between 65-75%

**Implication**: Solid shipping setup. Optimization opportunities exist but fundamentals are covered.

### EXCELLENT

All of the following conditions:

- Multiple active regions
- Tiered shipping rates
- Free shipping option available
- Multiple carriers with backup rates enabled
- Pickup and/or local delivery options configured
- `delivery_step_cvr` ≥ 75%
- No `multiplyByQuantity` pricing on any rate

**Implication**: Best-in-class shipping configuration. Focus on maintaining and fine-tuning.

---

## Business context filter (MANDATORY)

**This filter MUST be applied before recommending any international shipping action.**

### Check business type

Inspect the store's `industry` and `businessType` fields (case-insensitive match) for any of the following keywords:

- food
- restaurant
- grocery
- bakery
- catering
- perishable
- fresh
- meat
- produce
- dairy
- drink
- beverage

### If matched

**DO NOT recommend any international shipping action.** Perishable/food businesses face regulatory, spoilage, and logistics barriers that make international shipping impractical as a default recommendation.

### Identifying international regions

A region is considered "international" if any of the following are true:

- Region `name` contains "international" or "internacional" (case-insensitive)
- Region `destinations[]` is empty (wildcard / all countries)
- Region `destinations` include countries outside the store's home country

---

## Summary: Score decision table

| Score | Key indicator | Action |
|---|---|---|
| CRITICAL | No profiles/options or all regions inactive | Immediate setup required |
| POOR | Minimal config, low CVR, or no backup rates | Address fundamental gaps |
| FAIR | Basic setup, no free shipping, moderate CVR | Add free shipping, expand regions |
| GOOD | Domestic + international, free shipping, good CVR | Optimize rates and carriers |
| EXCELLENT | Full coverage, tiered rates, high CVR | Maintain and fine-tune |
