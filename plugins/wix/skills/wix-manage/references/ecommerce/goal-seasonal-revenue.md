---
name: "Goal: Seasonal Revenue"
description: Maps the SEASONAL business goal to event-driven revenue KPIs and promotional flows.
layer: goal
references:
  - name: "Flow: Seasonal Promotion"
    path: ecommerce/flow-seasonal-promotion.md
    load: true
---
# Goal: Capitalize on Seasonal Events

> **Before executing this skill**, read these referenced skills with `ReadFullDocsArticle`:
> - [Flow: Seasonal Promotion](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/skills/flow-seasonal-promotion)

Capitalize on holidays, cultural events, and seasonal moments to drive revenue spikes through time-limited promotional campaigns.

---

## Business Goal

**Goal ID:** `SEASONAL`

The merchant wants to take advantage of a specific event or season to boost sales. This is achieved through time-bound discount campaigns that create urgency and align with customer purchasing behavior during peak shopping periods.

---

## KPIs

| KPI | Definition | How to measure |
|---|---|---|
| Campaign period revenue | Total revenue during the promotional window | Compare order revenue within campaign dates |
| Conversion lift | Conversion rate during event vs baseline | Site metrics: orders / visitors during campaign vs prior period |
| Event vs baseline comparison | Revenue during event vs same period in prior month/year | `getSiteData` revenue comparison |
| Discount redemption rate | Orders qualifying for campaign discount / total orders in window | Track discount-attributed orders |
| Traffic-to-sale ratio | Orders / site visitors during campaign | Site metrics during campaign window |

---

## Triggers

Activate this goal when the merchant expresses any of the following intents:

- "Black Friday"
- "Christmas sale"
- "seasonal"
- "holiday discount"
- "New Year sale"
- "Valentine's Day"
- "summer sale"
- "back to school"
- "end of season"
- Any date-related promotion request
- Any mention of a specific holiday or cultural event tied to a discount

### Proactive Detection

If `current_date` is within 30 days of a major shopping holiday, auto-suggest a seasonal campaign:

| Holiday / Event | Approximate Date | Suggest Window |
|---|---|---|
| Valentine's Day | Feb 14 | Jan 15 - Feb 14 |
| Easter | Variable (March/April) | 30 days before |
| Mother's Day | 2nd Sunday in May | April 15 - May date |
| Father's Day | 3rd Sunday in June | May 20 - June date |
| Back to School | August | July 15 - Aug 31 |
| Black Friday | 4th Friday in November | Nov 1 - Nov 30 |
| Cyber Monday | Monday after Black Friday | Nov 1 - Nov 30 |
| Christmas | Dec 25 | Nov 25 - Dec 25 |
| Boxing Day / End of Year | Dec 26-31 | Dec 20 - Dec 31 |
| New Year | Jan 1 | Dec 26 - Jan 7 |

When proactively suggesting, frame it as an opportunity rather than a requirement:
> "Black Friday is {N} days away. Would you like to set up a promotional campaign to capitalize on the increased shopping traffic?"

---

## Recommended Actions

### Primary: Flow: Seasonal Promotion

For planned, scheduled events where the merchant has lead time. Creates a discount with defined start and end dates aligned to the event window.

**When to use:**
- The event is more than 48 hours away
- The merchant wants a structured campaign with specific dates
- The promotion should run for multiple days (e.g., a week-long sale)

**Key mechanics:**
- Time-bounded discount with explicit start/end dates
- Scope can be CATEGORY (seasonal products), ITEMS (featured products), or SITE (store-wide event)
- Discount percentage calibrated to margin and event significance

### Secondary: Flow: Run Flash Sale

For quick, high-urgency promotions with short windows (24-72 hours). Creates immediate impact with deeper discounts and tighter time constraints.

**When to use:**
- The event is imminent (within 48 hours)
- The merchant wants a short burst of urgency-driven sales
- Flash sale format (limited time, deeper discount) suits the event
- Last-minute seasonal opportunity

**Key mechanics:**
- Short duration (typically 24-48 hours)
- Can use deeper discounts than standard campaigns due to limited exposure
- Urgency messaging: "24-hour flash sale" or "ends midnight"

---

## Measurement Plan

### Before campaign launch

1. Record baseline revenue for the same period (prior week or prior year if available)
2. Record baseline conversion rate and traffic
3. Note the campaign window (start date, end date)

### During campaign

1. Monitor revenue daily against the campaign target
2. Track conversion rate vs baseline
3. Check inventory levels for promoted products — adjust if selling out too fast
4. Monitor discount stacking risks if other active promotions exist

### After campaign (within 7 days of end)

1. Calculate campaign revenue lift: `(campaign_revenue - baseline_revenue) / baseline_revenue * 100`
2. Compare conversion rate during campaign vs baseline
3. Assess whether the event-specific timing maximized impact
4. Calculate ROI: incremental revenue vs margin cost of discounts
5. Document learnings for next seasonal event:
   - Was the discount depth appropriate?
   - Was the campaign window too long or too short?
   - Which product scope performed best?

---

## Decision Matrix

| Scenario | Recommended Flow | Rationale |
|---|---|---|
| Major holiday, 7+ days lead time | Seasonal Promotion | Structured multi-day campaign with planned dates |
| Event is tomorrow or today | Flash Sale | Immediate activation, short window |
| End-of-season clearance | Seasonal Promotion + stock mover overlap | Combine seasonal framing with inventory goals |
| Merchant says "quick weekend sale" | Flash Sale | Short duration matches flash format |
| Merchant specifies exact dates and discount | Honor input, choose matching flow | User overrides take priority; select flow that fits the duration |
