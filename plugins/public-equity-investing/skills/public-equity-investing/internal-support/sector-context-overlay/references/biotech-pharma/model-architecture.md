# Model Architecture

Deferred reference for `sector-context-overlay` biotech-pharma sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for biotech and pharma

## Required model structure
- Asset-level schedule listing modality, indication, stage, key catalyst dates, filing path, probability of success, launch timing, geography, exclusivity window, and patent-cliff timing.
- Commercial forecast by patient flow: eligible patients, diagnosis, testing, treatment rate, share, persistence, units or doses, list price, gross-to-net, and net revenue.
- Separate schedules for product revenue, collaboration revenue, milestone revenue, royalty revenue, and one-time items.
- R&D schedule by program and development stage where possible, with explicit registrational-trial and post-marketing spend.
- SG&A build tied to launch stage, field-force needs, DTC or KOL spend where relevant, and geography.
- Manufacturing and gross-margin assumptions tied to modality and scale.
- Cash-flow and financing schedule including ATM usage, convert dilution, debt service, and royalty obligations.
- For mature pharma, explicit LOE schedule and replacement pipeline bridge.

## Mandatory decomposition
- Separate science risk from regulatory risk, and regulatory risk from commercial risk.
- Separate base business from pipeline optionality.
- Separate gross sales from net sales.
- Separate real product demand from inventory and channel movement.
- Separate recurring royalties from milestones and upfronts.
- Separate current-label value from label-expansion value.
- Separate patent and exclusivity duration from terminal value.

## Mandatory sensitivities
- probability of success by asset and stage
- readout, filing, and launch timing
- label breadth and line-of-therapy assumptions
- patient identification, treatment rate, and persistence
- gross-to-net and realized net price
- manufacturing yield, capacity, and COGS for complex modalities
- timing of generic or biosimilar entry and erosion rate
- burn rate, financing timing, and dilution
- valuation multiple or discount rate appropriate to maturity and risk
