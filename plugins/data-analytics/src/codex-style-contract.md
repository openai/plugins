# Codex Style Contract

Data Analytics follows the Codex visual system. The durable fallback token layer lives in `src/styles/codex-theme.css` and must be imported before analytics CSS. Host-provided theme variables, fonts, and display-mode context override that fallback when the app runs inside ChatGPT Desktop.

## Non-Negotiables

- Start from neutral Codex surfaces and semantic text levels.
- Use blue for accent and focus. Reserve status and chart colors for meaning.
- Keep controls compact, work-oriented, and consistent with the Codex shape system.
- Prefer borders, tonal shifts, and subtle shadows before heavy elevation.
- Preserve keyboard focus visibility, reduced-motion behavior, responsive sizing, and the inline-to-fullscreen affordance.
- Treat `src/analytics-app/tokens.css` as an additive analytics alias layer, not a competing design system.

## Analytics Extensions

Data Analytics owns domain-specific visualization palettes, KPI status roles, table density, report reading widths, dashboard layouts, and chart geometry. Those extensions should consume Codex tokens before introducing new values.

## File Ownership

- `src/styles/codex-theme.css` is the copied Codex fallback baseline.
- `src/analytics-app/tokens.css` aliases shared UI roles to the baseline and defines analytics-only roles.
- `src/DESIGN.md` is the validator-required analytics extension contract for generated packages.
- Component CSS should use those roles; add bespoke values only for chart geometry or analytics-specific layouts.

## Review Checklist

- Do new shared UI roles resolve through `--codex-*` tokens?
- Are new colors semantic or visualization-specific?
- Does the first screen remain a usable workspace?
- Do inline, fullscreen, light, dark, keyboard, and reduced-motion states work?
