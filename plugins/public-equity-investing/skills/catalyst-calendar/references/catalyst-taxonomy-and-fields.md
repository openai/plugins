# Catalyst Taxonomy And Fields

Use stable field names for workbook rows and refresh comparisons. The workbook helper accepts common aliases such as `company`, `event_type`, `event_window_start`, `event_window_end`, `source`, `confidence`, `importance`, `prep_action`, and `next_decision`, then writes canonical fields.

## Canonical Row Fields

| Group | Fields | Notes |
|---|---|---|
| Identity | `event_id`, `ticker`, `issuer`, `security_type`, `sector`, `region`, `portfolio_group`, `position_context` | `event_id` must be stable enough for refresh/change-log tracking. |
| Event | `event_category`, `event_subcategory`, `event_name`, `event_description`, `reported_period`, `status` | Use concrete labels; avoid generic “update” when the underlying event is earnings, regulatory, trial, financing, legal, etc. |
| Timing | `date_type`, `event_date`, `window_start`, `window_end`, `time_of_day`, `time_zone` | Exact dates require confirmation. Use windows for guided, estimated, inferred, or statutory timing. |
| Source | `source_label`, `source_id`, `source_notes` | Keep company/regulator/exchange sources distinct from provider, street-estimated, assumption, PM judgment, rumor, and restricted/internal sources. |
| Priority | `impact_score`, `confidence_score`, `urgency`, `thesis_relevance`, `kpi_or_model_line`, `market_setup` | Scores are 1-5; missing or weak evidence should downgrade confidence. |
| PM Action | `expected_outcome`, `variant_watch`, `prep_required`, `owner`, `prep_due_date`, `follow_up_date`, `decision_implication`, `post_event_action`, `notes` | Every high-impact event should create a work item, model/thesis checkpoint, or explicit monitoring rationale. |

## Event Categories

- **Earnings and guidance:** reports, preannouncements, guidance, KPI disclosures, call Q&A, restatements, capital return updates.
- **Investor events:** investor days, conferences, firesides, roadshows, product demos, teach-ins. Track only when there is disclosure or narrative risk.
- **Product/customer/GTM:** launches, pricing, user conferences, customer go-lives, channel checks, adoption/ramp milestones.
- **Regulatory/policy/legal:** agency decisions, comment deadlines, tariffs, rate cases, permits, antitrust, hearings, rulings, appeals.
- **Clinical/healthcare:** enrollment, topline/full data, PDUFA, advisory committees, label/reimbursement decisions.
- **Macro/rates/FX/commodities:** CPI, payrolls, central banks, PMIs, auctions, OPEC, inventories, fiscal deadlines. Track exposure relevance, not just the release date.
- **Technical/capital markets:** lockups, offerings, converts, buybacks, index changes, blackout windows, maturities, covenant tests.
- **M&A/activism/special situations:** votes, tenders, regulatory approvals, walk dates, go-shops, spins, separations, proxy deadlines.

## Scoring Labels

- **Impact 5:** Thesis, valuation, position size, financing path, or regulatory viability can change.
- **Impact 4:** Estimates, multiple, sentiment, or risk can move materially.
- **Impact 3:** Relevant update with model/narrative implications.
- **Impact 2:** Monitoring item.
- **Impact 1:** Calendar hygiene.

Confidence labels:
- **Confirmed:** Primary source confirms exact date.
- **Guided:** Company/regulator gives a window or expected timing.
- **Expected:** Reliable aggregator/consensus, no primary confirmation.
- **Inferred:** Cadence, statutory timeline, or historical pattern.
- **Rumored:** Press/market chatter only.
- **Unknown:** Insufficient evidence.

## Public Equity PM Catalyst Fields

Add fields: `benchmark_index`, `index_event_type`, `estimated_passive_flow`, `flow_vs_adv`, `etf_holder_base`, `rebalance_date`, `float_change`, `active_weight_relevance`, `decision_pressure`.

Add technical/capital-markets subcategories: `index_rebalance`, `offering`, `lockup`, `buyback_blackout`, `float_change`, `convert_or_warrant`, `passive_flow`.

Confirmed dates must stay separate from inferred windows. Do not export inferred windows as exact ICS events.
