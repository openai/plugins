# Hedge Finder Output Contracts

Use compact structures; include only rows that matter for the decision.

## Full Hedge Memo

```markdown
# Hedge Recommendation: [target/view]

## Executive PM Summary
- Position/view: [long/short/security/size if supplied]
- Core thesis to preserve: [desired exposure]
- Hedge objective: [risk, horizon/catalyst]
- Recommended hedge: [primary package]
- Main cost/carry: [premium/borrow/roll/upside give-up]
- Main basis risk: [failure mode]
- Confidence/readiness: [high/medium/low; ready/needs checks/screen-grade]
- Decision needed: [price/check borrow/run risk/size down/do not hedge]

## Assumptions And Data Quality
| Item | Status | Notes/as-of |
|---|---|---|
| Position size / horizon / portfolio exposures / live pricing / option chain / borrow / risk model | provided/missing/stale/unavailable |  |

## Objective And Exposure Classification
"Reduce [unwanted exposure] over [horizon/catalyst] while preserving [desired thesis exposure]."

| Exposure | Direction | Desired? | Evidence | Materiality | Treatment |
|---|---|---|---|---|---|

## Candidate Hedge Set
| Rank | Hedge | Type | Risk hedged | Thesis preservation | Cost/carry | Liquidity | Basis risk | Readiness | Senior view |
|---:|---|---|---|---|---|---|---|---|---|

Readiness labels: ready, needs live pricing, needs borrow check, needs option-chain validation, needs risk-system check, needs mandate/compliance review, idea-generation only.

For an equity short subject to an absolute loss cap, show a `Hard-Cap Package` row. The compliant direct-option structure is a share-for-share long call hedge, normally one listed call contract per 100 shares short, with maximum loss calculated from entry-to-strike loss plus premium, borrow/dividend cost, bid/ask and execution reserve, and applicable carry. If live terms cannot establish compliance, the output should say `do not initiate`, not recommend an unhedged short. A call spread is not compliant with an absolute cap because loss reopens above its written strike.

## Recommended Package
Primary: instrument, conceptual size/method, rationale, risk hedged, exposure retained, expected behavior, cost/carry, basis risk, readiness.

Alternative/event/overlay: include only if useful.

Rejected hedges:
| Hedge | Why rejected |
|---|---|

## Sizing / Cost / Scenario / Basis / Exits
- Sizing method and assumptions: [beta/factor/vol/dollar/driver/premium/loss-floor/scenario/etc.]
- Required data before implementation: [pricing/borrow/chain/risk model/mandate]
- Scenario behavior: include thesis-right, adverse, and hedge-failure cases.
- Basis risk ledger: hedge, risk, severity, mitigation, trigger.
- Exit rules: resize, roll, monetize, remove, re-underwrite, escalate.

## Bottom Line
Best answer: [primary action]. Use [alternative] if [constraint]. Do not use [rejected hedge] because [reason]. Confirm [checks] before implementation.
```

## Quick Outputs

### One-Page Summary

Recommendation, objective, why this hedge, conceptual sizing, cost/carry, basis risk, alternatives, rejected hedge, next action.

### Candidate Screen

| Hedge idea | Risk hedged | Pros | Cons | Basis risk | Next check |
|---|---|---|---|---|---|

Add: best first check, most dangerous false hedge, likely path if no data.

### Options Comparison

| Structure | Protection | Premium/carry | Upside retained | Best use | Main risk |
|---|---|---|---|---|---|
| Long put | full below strike | high | full | clean downside | decay |
| Put spread | between strikes | lower | full | event gap range | capped protection |
| Collar | below put strike | low/zero possible | capped | willing to sell upside | gives away upside |
| Index put | broad beta | varies | full for single name | portfolio selloff | basis |
| Call on short | squeeze cap | premium | n/a | crowded short | decay |

Required commentary: IV richness, expiry vs catalyst, protected risk, monetization rule, data needed.

For a capped-loss short, add coverage ratio and maximum package loss; require live strike, expiry, premium, bid/ask, liquidity and Greeks before recommending implementation.

### Pair Trade

| Pair candidate | Relative thesis | Hedge fit | Sizing basis | Borrow/liquidity | Catalyst match | Key basis risk | Verdict |
|---|---|---|---|---|---|---|---|

State that the short leg is a second investment thesis with independent risk.

### Basis-Risk Only

| Failure mode | Why it could happen | Impact | Early warning | Mitigation |
|---|---|---|---|---|

Conclude with most likely failure, most severe failure, whether hedge still deserves use, and what to monitor.

## Tone

Prefer: "QQQ is liquid and reduces mega-cap growth beta, but may over-hedge desired AI/growth exposure. If the thesis is company-specific share gain, use it only as a partial beta hedge; if the thesis is continued AI capex, a semi peer basket is cleaner."

Avoid: "The stock is correlated with QQQ, so short QQQ."

Prefer: "A put spread is better than an outright put when protection is needed for a normal earnings miss, not disaster protection; the tradeoff is capped downside protection."

Avoid: "Buy puts."
