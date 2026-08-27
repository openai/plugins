# Public Equity Investing Memo Modes

Choose the full memo mode that fits the decision by default. Use a compressed mode only when the user explicitly asks for a short, quick, one-page, brief, TL;DR, or review-only output.

| Mode | Use when | Posture |
|---|---|---|
| `ic-note` | explicitly requested compact committee discussion or one-page ask | decision-forward, tight, source-aware |
| `investment-memo` | formal public equity, event-driven equity, PM update, client research, or sector memo | complete narrative, valuation, scenarios, risks, catalysts |
| `event-driven-committee-note` | M&A arb, spin, litigation, regulatory, restructuring, index, tender, special situation | probability, timing, spread, break price, milestones |
| `pm-update` | post-print, news, price move, thesis drift, model update, catalyst change | what changed, implication, action options, monitoring |
| `client-research-note` | polished external or semi-external communication | clear narrative, source caveats, less trade-instruction-heavy |
| `screen-grade-scratch-memo` | ticker/theme/sparse prompt with no complete source packet | build-from-scratch scaffold with provisional house view, source gaps, and upgrade path |
| `qa-review` | review an existing memo | findings first, severity ordered |

Escalation rules:

- If the prompt asks for short/brief/one-page/first-pass, use `ic-note` unless a fuller mode is necessary.
- If the user provides thin context and no source pack, produce a full screen-grade memo structure with visible assumptions and evidence requests.
- If the user provides only a ticker, theme, headline, or partial thesis, use `screen-grade-scratch-memo`: provide the intake checklist, source packet requirements, first-pass house view, variant wedge, what is priced in, estimate path, valuation/skew, downside mechanism, catalysts, disconfirmers, action rules, and evidence needed to upgrade the memo.
- Compress background first; do not cut recommendation, scenarios, downside, catalysts, monitoring, or open items.

## Public Equity Memo Modes

Add `buy-side-investment-memo`, `pm-update`, `sell-side-research-note`, `client-research-note`, `etf-index-diligence-note`, and `public-equity-diligence-memo`. Each full memo must include decision hinge, what must be true, what is priced in, downside mechanism, measurable disconfirmers, source posture, and action discipline.
