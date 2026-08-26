# Biotech And Pharma Modeling Rules

Deferred reference for `Biotech Pharma Sector Analysis`. Load only when the task needs sector modeling detail.

## Core Frame

Underwrite biotech/pharma as an option tree across science, evidence, regulation, label, access, manufacturing, IP, financing, and security claims. Do not start with EBITDA, simple revenue growth, or management words like de-risked, best-in-class, platform, or blockbuster.

Start with the disease and mechanism, then ask whether the data prove a clinically meaningful benefit in the likely label population, whether regulators can accept it, whether patients can reach and stay on therapy, whether manufacturing can scale, how long exclusivity lasts, and whether cash runway reaches the next value-inflecting event.

Treat a beat as low quality when driven by milestones, upfront-license revenue, stocking, channel fill, one-time government orders, PRV or asset-sale gains, tax noise, or deferred trial spend rather than cleaner product demand or improved pipeline probability.

## Analysis Sequence

### 1) Disease, mechanism, and unit of value
- Define disease state, standard of care, line of therapy, unmet need, and real commercial denominator: diagnosed, biomarker-positive, eligible, referred, treated, or persistent patients.
- Identify modality and delivery burden: small molecule, biologic, ADC, cell/gene therapy, RNA, radiopharma, vaccine, combo, hospital, office, specialty pharmacy, or site-of-care dependent.
- Map mechanism to disease biology; target novelty is not evidence of clinical relevance.
- Build value from patient starts, treated patients, persistence, infusions, doses, scripts, vials, royalties, or partner sales, not TAM adjectives.
- For diversified pharma, separate mature franchises, launch assets, and pipeline options before combining them.

### 2) Evidence quality and endpoint discipline
- Read study design before valuation: randomization, blinding, control, inclusion/exclusion, line of therapy, geography, stratification, powering, endpoint hierarchy, and follow-up maturity.
- Separate biological plausibility, statistical evidence, clinical relevance, regulatory acceptability, and commercial attractiveness.
- Haircut uncontrolled, small, post-hoc, immature, crossover-heavy, investigator-assessed, or subgroup-sliced datasets unless the design supports the claim.
- Safety matters economically: grade 3+ AEs, SAEs, discontinuations, dose reductions, treatment deaths, boxed warnings, monitoring burden, and real-world tolerability.
- Hazard ratios need medians, tails, absolute benefit, confidence intervals, and follow-up context; statistical significance can still be commercially weak.

### 3) Regulatory path and label economics
- Map NDA/BLA/supplemental, accelerated or traditional approval, orphan/RMAT/Breakthrough/Priority status, filing acceptance, AdCom, inspection, PDUFA, and post-marketing commitments.
- Treat designations as process aids, not proof of approval.
- Underwrite label scenarios: indication wording, line of therapy, biomarker restriction, dose, combination language, REMS, monitoring, confirmatory-study burden, and geography.
- Pressure-test CMC and facility-inspection risk, especially for biologics, sterile products, and advanced modalities.
- Approval is an input; label breadth, restrictions, reimbursement, and confirmatory obligations determine value.

### 4) Launch, access, and commercial quality
- Model patient flow: prevalence, diagnosis, testing, referral, eligibility, site readiness, initiation, persistence, retreatment, geography, and share.
- Use realized net price. Bridge WAC/list price to gross sales, rebates, chargebacks, copay assistance, returns, distribution fees, and net product revenue.
- Identify payer channel and friction: commercial, Part B/D, Medicaid, buy-and-bill, specialty pharmacy, tender, prior auth, step edits, and out-of-pocket burden.
- Early launch can be inflated by pent-up demand, easiest-to-find patients, stocking, or inventory; persistence and patient starts are cleaner than list-price-driven growth.
- For rare disease and advanced therapy, test patient finding, newborn screening, advocacy reach, treatment-center capacity, cold chain, and release timing.

### 5) Manufacturing, supply chain, and CMC
- Classify manufacturing complexity: conventional, biologic, sterile, personalized, short shelf-life, cold-chain, outsourced, single-source, or quality-system dependent.
- For cell/gene therapy, track vein-to-vein time, batch failures, release testing, comparability, vector/raw-material supply, throughput, and center logistics.
- For biologics and radiopharma, test scale-up, yield, fill-finish, distribution, decay, capacity, and process consistency.
- Commercial supply issues, warning letters, recalls, shortages, and inventory swings can drive both revenue quality and regulatory downside.

### 6) IP, exclusivity, lifecycle, and LOE
- Map composition, formulation, method-of-use, manufacturing, device, salt/polymorph patents, plus Orange Book/Purple Book and regulatory exclusivity.
- Build LOE by product, market, and competition type: generic, biosimilar, branded follow-on, or therapeutic substitution.
- Separate legal moat, regulatory exclusivity, manufacturing barrier, brand/physician habit, and lifecycle innovation.
- Lifecycle extensions soften LOE only when they change clinical or access value; secondary patents alone deserve caution.
- For royalty streams, map royalty step-downs, expiry mechanics, tail periods, and revenue exposure to competition.

### 7) Financial quality and runway
- Split product, collaboration, milestone, royalty, manufacturing, and one-time revenue.
- For commercial assets, model gross-to-net, gross margin, launch SG&A, R&D, and operating profit by product or franchise.
- For development-stage biotech, reconcile cash to normalized burn, trial footprint, working-capital noise, upfront receipts, capex, financing, and runway in quarters.
- Lower R&D can be optical if caused by cancelled programs or delayed trials; deal revenue can mask weak recurring demand.

### 8) Capital structure and security-specific risk
- Map cash, restricted cash, debt, converts, warrants, royalty financings, synthetic royalties, term loans, minimum-cash covenants, liens, and pledged assets.
- Test whether runway reaches the next catalyst under realistic spend and whether a miss forces dilution, covenant pressure, royalty monetization, licensing, or asset sale.
- For debt or royalty claims, route claim-seniority, collateral-quality, and recovery underwriting to Credit Markets; retain downside cash generation, expiry, competition, and label-change effects only as equity dilution/runway risk.
- For large pharma, include patent cliffs, M&A appetite, shareholder returns, litigation, FX/tax noise, and maturity profile.

## Deferred Modeling Layers

Load deeper files only when needed:
- `valuation-rules.md`: valuation hierarchy, rNPV/SOTP, and public-equity security context; route Credit Markets handoff rules to Credit Markets.
- `model-architecture.md`: model structure, driver decomposition, and sensitivities.
