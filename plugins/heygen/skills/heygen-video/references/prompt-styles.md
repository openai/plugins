---
name: prompt-styles
description: 20 named visual styles for Video Agent prompts — mood-first selection, copy-paste STYLE blocks
---

# Prompt Style Library

Named visual styles you inject directly into the prompt text. Each is inspired by a real graphic designer and tested across 40+ videos.

**These are different from HeyGen API styles (`style_id`).** API styles are curated templates on HeyGen's backend. Prompt styles give you full control over colors, typography, motion, and transitions directly in the prompt.

**How to use:** Pick a style. Copy the STYLE block. Paste it into the prompt after your script content.

**How to pick:** Match mood first, content second. Ask: *"What should the viewer FEEL?"*

> **Language note:** Style blocks stay in English regardless of the video's content language. They are technical directives to Video Agent's rendering engine, not viewer-facing text. The video's script and narration should be in the video language, but the STYLE block at the end is always English.

## Mood-to-Style Guide

| Content feels... | Use... |
|---|---|
| Personal, intimate | Soft Signal, Quiet Drama |
| Natural, earthy | Warm Grain, Earth Pulse |
| Nostalgic, historical | Heritage Reel |
| Data-driven, analytical | Swiss Pulse, Digital Grid |
| Elegant, premium | Velvet Standard, Geometric Bold |
| Cultural, global | Silk Route, Folk Frequency |
| Investigative, serious | Contact Sheet, Shadow Cut |
| Fun, lighthearted | Play Mode, Carnival Surge |
| Philosophical, abstract | Dream State |
| Punk, grassroots, raw | Deconstructed |
| Hype, loud, high-energy | Maximalist Type |
| Tech-forward, futuristic | Data Drift |
| Breaking, urgent | Red Wire |

## Quick Reference

| # | Style | Artist | Mood | Best For |
|---|---|---|---|---|
| 1 | Soft Signal | Sagmeister | Intimate, warm | Personal stories, wellness |
| 2 | Warm Grain | Eksell | Organic, friendly | Environmental, sustainability |
| 3 | Quiet Drama | Ray | Humanist, contemplative | Profiles, biographical |
| 4 | Heritage Reel | Cassandre | Nostalgic, vintage | History, retrospectives |
| 5 | Silk Route | Abedini | Flowing, mysterious | Global affairs, cross-cultural |
| 6 | Swiss Pulse | Müller-Brockmann | Clinical, precise | Data-heavy, analytical |
| 7 | Geometric Bold | Tanaka | Minimal, elegant | Lifestyle, visual essays |
| 8 | Velvet Standard | Vignelli | Premium, timeless | Luxury, investor updates |
| 9 | Digital Grid | Crouwel | Systematic, technical | Infrastructure, engineering |
| 10 | Contact Sheet | Brodovitch | Editorial, investigative | Journalism, deep dives |
| 11 | Folk Frequency | Terrazas | Cultural, vivid | Festivals, food, heritage |
| 12 | Earth Pulse | Ghariokwu | Grounded, communal | Community, grassroots |
| 13 | Dream State | Tomaszewski | Surreal, poetic | Op-eds, philosophy |
| 14 | Play Mode | Ahn Sang-soo | Playful, irreverent | Entertainment, pop culture |
| 15 | Carnival Surge | Lins | Euphoric, celebratory | Milestones, hype |
| 16 | Shadow Cut | Hillmann | Dark, cinematic | Exposés, investigations |
| 17 | Deconstructed | Brody | Industrial, raw | Tech news, punk energy |
| 18 | Maximalist Type | Scher | Loud, kinetic | Big announcements, launches |
| 19 | Data Drift | Anadol | Futuristic, immersive | AI/tech, innovation |
| 20 | Red Wire | Tartakover | Urgent, immediate | Breaking news, crisis |

## Production Performance (from 40+ videos)

| Rank | Style | Strength |
|------|-------|----------|
| 1 | Deconstructed (Brody) | Most reliable across all topics |
| 2 | Swiss Pulse (Müller-Brockmann) | Best for data-heavy content |
| 3 | Digital Grid (Crouwel) | Strong for tech topics |
| 4 | Geometric Bold (Tanaka) | Elegant and versatile |
| 5 | Maximalist Type (Scher) | High energy, use sparingly |

---

## Style Blocks (Copy-Paste Ready)

### 1. Soft Signal — Sagmeister
**Mood:** Intimate, warm | **Best for:** Personal stories, wellness
```
STYLE — SOFT SIGNAL (Sagmeister): Warm amber/cream, dusty rose, sage green.
Handwritten-style text. Close-up framing. Slow drifts and floats.
Soft dissolves with warm light leaks.
```

### 2. Warm Grain — Eksell
**Mood:** Organic, friendly | **Best for:** Environmental, sustainability
```
STYLE — WARM GRAIN (Eksell): Earth tones — ochre, forest green, terracotta, cream.
Organic rounded compositions. 16mm film grain. Rounded sans-serif.
Gentle wipes and soft cuts.
```

### 3. Quiet Drama — Ray
**Mood:** Humanist, contemplative | **Best for:** Profiles, biographical
```
STYLE — QUIET DRAMA (Ray): Muted warm — sepia, deep brown, soft gold.
Portrait framing. Clean serif. Strong single-source contrast.
Slow fades to black.
```

### 4. Heritage Reel — Cassandre
**Mood:** Nostalgic, vintage | **Best for:** History, retrospectives
```
STYLE — HERITAGE REEL (Cassandre): Faded gold, burgundy, navy, sepia wash.
Elegant centered serif. Vignetting and aged film grain.
Iris wipe transitions.
```

### 5. Silk Route — Abedini
**Mood:** Flowing, mysterious | **Best for:** Global affairs, cross-cultural
```
STYLE — SILK ROUTE (Abedini): Jewel tones — deep teal, burgundy, gold, lapis blue.
Layered compositions, all depths active. Elegant spaced type.
Flowing dissolves and smooth morphs.
```

### 6. Swiss Pulse — Müller-Brockmann
**Mood:** Clinical, precise | **Best for:** Data-heavy, analytical, financial
```
STYLE — SWISS PULSE (Müller-Brockmann): Black/white + electric blue #0066FF.
Grid-locked. Helvetica Bold. Animated counters. Diagonal accents.
Grid wipe transitions.
```

### 7. Geometric Bold — Tanaka
**Mood:** Minimal, elegant | **Best for:** Lifestyle, visual essays
```
STYLE — GEOMETRIC BOLD (Tanaka): Max 3 flat colors per frame.
60% negative space. Bold type as primary element.
Single focal point. Clean cuts on beat.
```

### 8. Velvet Standard — Vignelli
**Mood:** Premium, timeless | **Best for:** Luxury, investor updates, keynotes
```
STYLE — VELVET STANDARD (Vignelli): Black, white, one accent: gold #c9a84c.
Thin ALL CAPS, wide spacing. Generous negative space.
Slow elegant cross-dissolves.
```

### 9. Digital Grid — Crouwel
**Mood:** Systematic, technical | **Best for:** Infrastructure, engineering, code
```
STYLE — DIGITAL GRID (Crouwel): Monospaced type. Dark #0a0a0a with cyan #00E5FF, amber #FFB300.
Pixel grid overlays. Terminal aesthetic. Clean wipe transitions.
```

### 10. Contact Sheet — Brodovitch
**Mood:** Editorial, investigative | **Best for:** Journalism, deep dives
```
STYLE — CONTACT SHEET (Brodovitch): High contrast B&W, desaturated accents.
Photo-editorial framing. Bold sans-serif annotations. Raw grain.
Hard cuts on beat. Snap-zooms.
```

### 11. Folk Frequency — Terrazas
**Mood:** Cultural, vivid | **Best for:** Festivals, food, heritage
```
STYLE — FOLK FREQUENCY (Terrazas): Vivid folk — hot pink, cobalt blue, sun yellow, emerald.
Bold rounded type. Folk art rhythms. Rich handmade textures.
Colorful wipes on festive rhythm.
```

### 12. Earth Pulse — Ghariokwu
**Mood:** Grounded, communal | **Best for:** Community, music/culture
```
STYLE — EARTH PULSE (Ghariokwu): Warm saturated — burnt orange, deep green, rich yellow.
Bold expressive type. Wide community framing.
Rhythmic cuts on beat. Freeze-frames.
```

### 13. Dream State — Tomaszewski
**Mood:** Surreal, poetic | **Best for:** Op-eds, philosophy
```
STYLE — DREAM STATE (Tomaszewski): Muted palette + one surreal accent.
Thin elegant floating type. Soft edges, atmospheric haze.
Slow morph dissolves — NEVER hard cuts.
```

### 14. Play Mode — Ahn Sang-soo
**Mood:** Playful, irreverent | **Best for:** Entertainment, pop culture
```
STYLE — PLAY MODE (Ahn Sang-soo): Electric blue, hot pink, lime green.
Bouncy spring physics. Oversized tilted text. Score cards, XP bars.
Pop cuts, bounce effects.
```

### 15. Carnival Surge — Lins
**Mood:** Euphoric, celebratory | **Best for:** Milestones, hype
```
STYLE — CARNIVAL SURGE (Lins): Max color — hot pink #FF1493, yellow #FFE000, teal #00CED1.
Collage layering. Text MASSIVE at ANGLES. Confetti bursts.
Smash cuts, flash frames.
```

### 16. Shadow Cut — Hillmann
**Mood:** Dark, cinematic | **Best for:** Exposés, investigations
```
STYLE — SHADOW CUT (Hillmann): Deep blacks, cold greys + blood red accent.
Sharp angular text. Heavy shadow. Slow creeping push-ins.
Hard cuts to black. Film noir tension.
```

### 17. Deconstructed — Brody
**Mood:** Industrial, raw | **Best for:** Tech news, punk energy
```
STYLE — DECONSTRUCTED (Brody): Dark grey #1a1a1a, rust orange #D4501E.
Type at angles, overlapping. Gritty textures, scan-line glitch.
Smash cuts with flash frames.
```

### 18. Maximalist Type — Scher
**Mood:** Loud, kinetic | **Best for:** Big announcements, launches
```
STYLE — MAXIMALIST TYPE (Scher): Red, yellow, black, white — max contrast.
Text IS the visual. Overlapping at different scales, 50-80% of frame.
Kinetic everything. Smash cuts, flash frames.
```

### 19. Data Drift — Anadol
**Mood:** Futuristic, immersive | **Best for:** AI/tech, innovation
```
STYLE — DATA DRIFT (Anadol): Iridescent — purple #7c3aed, cyan #06b6d4, deep black.
Fluid morphing compositions. Thin futuristic type.
Liquid dissolves. Particles coalesce into numbers.
```

### 20. Red Wire — Tartakover
**Mood:** Urgent, immediate | **Best for:** Breaking news, crisis
```
STYLE — RED WIRE (Tartakover): Red, black, white, emergency yellow.
Bold condensed all-caps. Split screens, tickers, timestamps.
Snap cuts, flash frames. Zero breathing room.
```

---

## Custom Styles

These 20 are starting points. Create your own by combining:
1. **Named style + designer reference** (grounds the aesthetic)
2. **Color palette with hex codes** (specific > vague)
3. **Typography rules** (font style, weight, case, spacing)
4. **Motion rules** (how elements enter/exit, timing)
5. **Transition type** (cuts, dissolves, wipes)

Example custom style:
```
STYLE — NEON TERMINAL (custom): Black #0a0a0a background, neon green #00FF41 text,
cyan #00E5FF highlights. Monospaced type throughout. Terminal cursor blinks.
Text types on character by character. Scan-line overlay at 5% opacity.
Hard cuts only. Matrix-style code rain in transitions.
```
