---
name: canva-brand-check
description: Check a Canva design against a brand kit and report where it diverges — off-palette colors, non-brand fonts, logo misuse, and off-tone copy. Read-only; makes no changes. Use when the user asks "is this on brand", "check this against our brand kit", "do a brand review", "does this match our brand guidelines", or "brand-check my design".
---

# Brand Checker

Compare a design against the user's brand kit and report, point by point, where it follows the brand and where it drifts. This is a specialised, brand-aware version of `canva-design-feedback`: same read-only "read the design, then critique" core, but the rubric is the brand kit. It **never edits** the design.

## The brand-kit data gap — read this first

`Canva:list-brand-kits` is documented to return brand kit **IDs, names, and thumbnails**. It may NOT return the machine-readable palette (hex values) and font families. Your approach depends on what you actually get back:

- **If the kit exposes colors/fonts** → use those exact hex codes and font names as the rubric (precise check).
- **If it only exposes a thumbnail/name** → you cannot do an exact hex/font match. Fall back to a **visual** comparison against the kit thumbnail, and ASK the user to paste their brand colors (hex) and fonts so you can check precisely. Be explicit that, without those, the color/font findings are approximate.

Never invent brand colors or fonts. If you don't have the real values, say so.

## Reading the design's actual colors and fonts

`Canva:get-design-content` returns text only — not colors or fonts.

- A **read-only** editing transaction (`Canva:start-editing-transaction` → inspect → `Canva:cancel-editing-transaction`, always cancel) reliably gives element **text, positions, and sizes**.
- **Colors and fonts are NOT reliably exposed** by the transaction — tested: it often returns only text + position + dimension, with no color/font attributes. So the **thumbnail is your primary evidence** for color and typography. Use any style data the payload happens to include, but never assert a design's hex or font as fact unless it was actually in the payload.

Because both the brand kit (see the gap above) AND the design itself frequently lack machine-readable colors/fonts, brand-check is often a **visual** comparison (design thumbnail vs. brand-kit thumbnail) plus the user-supplied palette/fonts. Use `Canva:get-design-thumbnail` for logo placement and overall visual tone.

## Workflow

### Step 1: Resolve the design
Short link → `Canva:resolve-shortlink`; full URL → extract ID; raw `D...` ID → use directly; otherwise ask.

### Step 2: Get the brand kit
- `Canva:list-brand-kits`. If several, ask which one (or infer from team/context).
- Capture whatever the kit exposes (name, thumbnail, and colors/fonts if present).
- Apply the data-gap handling above. If scopes are missing (e.g. "Missing scopes: [brandkit:read]"), tell the user to disconnect and reconnect the Canva connector to refresh the token.

### Step 3: Read the design
- `Canva:get-design-thumbnail` for visual/logo/tone.
- Read-only transaction (start → inspect → cancel) for the actual colors and fonts in use.

### Step 4: Compare against the brand
Check each dimension and mark **On brand / Off brand / Can't verify**:

- **Color** — are fills/text/accents within the brand palette? Flag off-palette hexes (and the nearest brand color).
- **Typography** — do fonts match brand fonts? Flag non-brand families and inconsistent sizing/weight usage.
- **Logo** — present where expected, correct version, not stretched/recolored/crowded (visual check from thumbnail).
- **Tone & copy** — does the wording match the brand voice the user describes?
- **Consistency** — is brand application consistent across all pages?

Use **Can't verify** honestly whenever the kit didn't expose the data and the user hasn't supplied it.

### Step 5: Report
```
## Brand check — "<design title>" vs "<brand kit name>"

Overall: ⚠️ Mostly on brand, 3 issues

### Off brand
- [Color] Page 2 heading is #1A73E8 — not in palette. Nearest brand color: #0B5CD7.
- [Font] Page 4 body uses Arial; brand body font is Inter.

### Can't verify (need input)
- Brand kit didn't expose hex values. Paste your palette + fonts for an exact check,
  or confirm the colors above against your guidelines.

### On brand
- Logo placement and cover treatment match the kit.
```

### Step 6: Offer to fix
Offer to correct the API-fixable issues via **`canva-edit-design`** — note that the API can change **text color** and font **size/weight/style**, but CANNOT change font **family** or background colors (those are manual in Canva; see `canva-edit-design`).

## Rules
- Read-only: always `cancel-editing-transaction` after inspecting. Never commit.
- Never fabricate brand values — use the kit's real data or what the user provides, otherwise mark **Can't verify**.
- Always name the specific page/element and the offending value vs. the brand value.
- Distinguish hard violations (wrong logo, off-palette color) from soft ones (slightly inconsistent spacing).
