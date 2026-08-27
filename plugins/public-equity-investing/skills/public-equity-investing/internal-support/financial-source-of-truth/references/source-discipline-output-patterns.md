# Source Discipline Output Patterns

Use these patterns when source review needs to be useful, not just compliant.

## Core response shape

Start with a posture block:

```markdown
Evidence posture: [decision-grade / research-grade / preliminary / assumption-led / not supportable]
What is usable now: [one sentence]
What is not yet supportable: [one sentence]
Highest-priority next action: [specific source request or tie-out]
```

Then use the full table set by default:

1. `Supported facts`
2. `Assumptions / inferences`
3. `Limitations / conflicts`
4. `Next actions`

This keeps the output actionable without overstating support. Use fewer tables only when the user explicitly asks for a short answer or one disputed claim.

## Sparse-source pattern

Use this when the user provides a claim, note, model, deck, or ask but not the underlying sources.

```markdown
Evidence posture: assumption-led.

| Item | Current treatment | Why | What would upgrade it |
|---|---|---|---|
| [metric/claim] | `assumption_user_provided` / `unknown` | User provided it, but no source is attached | [filing/vendor export/transcript/model tab/date needed] |
```

Do not say the work cannot proceed. Provide a usable framework and mark unsupported items clearly.

## Conflict pattern

Use this when two sources disagree.

```markdown
Evidence posture: preliminary due to unresolved conflict.

| Claim | Source A | Source B | Preferred source | Treatment | Next action |
|---|---|---|---|---|---|
| [claim] | [S1 + exact support] | [S2 + exact support] | [S1/S2/unresolved] | [use preferred / show both / sensitize] | [specific tie-out] |
```

Do not average conflicting numbers unless the method is explicit and appropriate.

## Unsupported precision pattern

Use this when the requested output contains exact figures that are not backed by exact support.

```markdown
Evidence posture: not supportable at the stated precision.

Supported directionally: [what the evidence supports]
Unsupported precision: [exact number/range/date that lacks support]
Safer wording: [rewrite without false precision]
Required support: [source, page/tab, provider timestamp, or calculation bridge]
```

## Practical next-action language

Good next actions are specific:

- "Provide the latest 10-Q debt note and the model EV bridge tab to support net debt."
- "Provide consensus export with provider name and estimate-as-of date."
- "Tie the investor-deck adjusted EBITDA bridge to the earnings release reconciliation."
- "Confirm whether the market price is current as of the valuation date or a stale placeholder."

Avoid generic next actions:

- "Need more sources."
- "Verify data."
- "Add citations."
- "Check assumptions."

## Language calibration

| Evidence state | Use this language | Avoid |
|---|---|---|
| Supported fact | "reported", "filed", "per S1" | "appears" |
| User-provided input | "user-provided assumption" | "verified" |
| Issuer claim | "management states" | "the company has proven" |
| Weak support | "directionally supported" | exact unsupported decimals |
| Conflict | "unresolved conflict" | burying one source |
| Missing source | "not yet supportable" | false certainty |


## Unsupported Connector Or Provider Access

When a requested Bloomberg, FactSet, S&P Capital IQ, CapIQ, LSEG, Refinitiv, Daloopa, PitchBook, Morningstar, broker, email, collaboration-app, or internal data connector is not callable in the runtime, do not pretend to have pulled it. Use user-provided exports if available, request the specific export, label the missing evidence as `missing_required_source`, and keep the evidence posture preliminary or screen-grade.

## Credit Markets Handoff Pattern

If the user asks for a public-credit memo, bond/loan/CDS analysis, covenant review, recovery waterfall, restructuring view, spread/yield relative value, or debt-security selection, route to Credit Markets. If credit data is present inside a public-equity packet, retain only the equity read-through: refinancing stress, solvency warning, maturity-wall risk, CDS/spread signal, or liquidity pressure that could affect common-equity downside.
