---
name: "Troubleshoot: Checkout Delivery Drop-off"
description: Diagnostic tree for when delivery step conversion is below benchmark. Correlates shipping issues with checkout abandonment and calculates revenue impact.
layer: troubleshoot
---
# Troubleshoot: Checkout Delivery Drop-off

## When to use

Use this diagnostic tree when analyzing checkout funnel performance and the delivery step shows elevated abandonment. The delivery step is where customers choose their shipping method — drop-off here directly indicates shipping-related friction.

---

## Step 1: Check delivery step conversion rate

Compare `delivery_step_cvr` against the benchmark of **65%**.

### Interpretation

| CVR range | Interpretation | Action |
|---|---|---|
| cvr < benchmark (65%) AND shipping issues detected | Correlate specific issues to conversion drop | Proceed to full diagnostic |
| cvr ≥ benchmark (65%) | Do NOT cite CVR gap as justification | Focus on best practices, not recovery |
| cvr ≥ 90% | Excellent — note strong performance | Focus on maintaining, not fixing |

**Important**: If the CVR is at or above benchmark, do not frame recommendations as fixing a conversion problem. Only cite CVR gap when the data supports it.

---

## Step 2: Calculate revenue impact

Use this formula to quantify the business impact of the delivery step drop-off:

```
revenue_impact = (benchmark_delivery_cvr - delivery_step_cvr) / 100 × total_checkouts × aov
```

**Example**: If benchmark is 65%, current CVR is 55%, with 2,000 checkouts/month and $80 AOV:
- `(65 - 55) / 100 × 2000 × 80 = $16,000/month` in potential lost revenue.

### High traffic amplifier

If `visitors > 30,000` (approximately 1,000+ per day) AND a HIGH-severity shipping issue is detected, include a daily revenue impact estimate to emphasize urgency:

```
daily_impact = revenue_impact / 30
```

> "At your traffic volume, this shipping issue may be costing approximately ${daily_impact} per day."

---

## Step 3: Assign priority

Based on the gap between current CVR and benchmark:

| Gap | Priority | Urgency |
|---|---|---|
| Gap > 10 percentage points | **HIGH** | Address immediately — significant revenue loss |
| Gap 5-10 percentage points | **MEDIUM** | Address soon — meaningful improvement opportunity |
| Gap < 5 percentage points | **LOW** | Optimize when convenient — incremental gains |

---

## Step 4: Identify common causes

Check for these known shipping issues that correlate with delivery step drop-off:

1. **No free shipping option**: Stores without any free shipping option see higher delivery-step abandonment. Customers expect at least a conditional free shipping tier.

2. **Missing delivery estimates**: Shipping options without estimated delivery times create uncertainty. Customers abandon when they don't know when their order will arrive.

3. **Per-item pricing (`multiplyByQuantity`)**: Customers adding multiple items see shipping costs spike unexpectedly at checkout.

4. **Coverage gaps**: Customer's delivery address falls outside configured shipping regions. The checkout shows no available shipping methods.

5. **Inactive backup rates**: When the primary carrier can't fulfill and no backup rate is configured, the customer sees no shipping options.

6. **Options on inactive regions**: Shipping options configured for regions that are set to `active: false` are not available at checkout.

---

## Step 5: Run diagnostic sequence

Follow this sequence to systematically identify the root cause:

### 5.1 Check configuration completeness
- Are delivery profiles configured?
- Are regions active?
- Are shipping options assigned to active regions?

### 5.2 Check coverage gaps
- Do the configured regions cover the store's primary customer geographies?
- Are there common destination countries/states missing from region definitions?

### 5.3 Check free shipping presence
- Is there at least one free shipping option (unconditional or threshold-based)?
- If threshold-based, is the threshold achievable relative to AOV?

### 5.4 Check rate pricing sanity
- Are any rates exceeding 15% of AOV?
- Is `multiplyByQuantity` enabled on any rate?
- See the **Guardrail: Rate Pricing Sanity** skill for detailed checks.

### 5.5 Check backup rates
- Are backup rates configured on carriers?
- Are backup rate amounts reasonable (5-10% of AOV)?

### 5.6 Correlate findings with CVR impact
- For each issue found, estimate its contribution to the CVR gap.
- Prioritize fixes by expected conversion recovery.
- Present findings in order of impact, with revenue estimates where possible.

---

## Summary: Diagnostic checklist

| Step | Check | What to look for |
|---|---|---|
| 1 | CVR vs benchmark | Is there actually a gap to address? |
| 2 | Revenue impact | Quantify the business cost |
| 3 | Priority | HIGH (>10pt gap), MEDIUM (5-10pt), LOW (<5pt) |
| 4 | Common causes | Free shipping, estimates, per-item, coverage, backups |
| 5 | Diagnostic sequence | Config → coverage → free shipping → rates → backups → correlate |
