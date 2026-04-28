---
name: motion-vocabulary
description: Motion verbs, the 5-layer visual system, scene types, and anti-patterns for Video Agent prompts
---

# Motion Vocabulary & Visual Layer System

Video Agent is an HTML interpreter. It renders layouts, typography, and structured content natively. The key to great B-roll: describe elements with **action verbs** ("slams in," "types on," "counts up") not layout specs ("upper-left, 48pt").

Based on patterns from 40+ produced videos.

> **Language note:** Motion verbs MUST remain in English regardless of the video's content language. Video Agent's rendering engine responds to these specific English verbs. Do not translate "SLAMS", "CASCADE", "COUNTS UP", etc. They are API-level commands, not viewer-facing text.

## Motion Verbs

Use these exact verbs in prompts. Video Agent responds to them. Without them, you get static frames.

### High Energy
| Verb | Example |
|------|---------|
| **SLAMS** | `"$95M" SLAMS in from left at -5 degrees` |
| **CRASHES** | `Title CRASHES in from right, screen-shake on impact` |
| **PUNCHES** | `Quote card PUNCHES up from bottom` |
| **STAMPS** | `Data blocks STAMP in staggered 0.4s` |
| **SHATTERS** | `Text SHATTERS after 1.5s, revealing number underneath` |

### Medium Energy
| Verb | Example |
|------|---------|
| **CASCADE** | `Three cards CASCADE from top, staggered 0.3s` |
| **SLIDES** | `Ticker SLIDES in from right — continuous scroll` |
| **DROPS** | `"TIER 1" DROPS in with white flash` |
| **FILLS** | `Progress bar FILLS 0 to 90% in orange` |
| **DRAWS** | `Chart line DRAWS itself left to right` |

### Low Energy
| Verb | Example |
|------|---------|
| **types on** | `Quote types on word by word in italic white` |
| **fades in** | `Logo fades in at center, held for 3 seconds` |
| **FLOATS** | `Bokeh orbs FLOAT across frame at different speeds` |
| **morphs** | `Number morphs from 17 to 18.9` |
| **COUNTS UP** | `"1.85M" COUNTS UP from 0 in amber 96pt` |

## Transition Types

| Transition | Energy | Best With Styles |
|------------|--------|-----------------|
| Smash cut | Aggressive | Deconstructed, Maximalist, Carnival Surge |
| White flash frame | Punchy | Deconstructed, Maximalist |
| Grid wipe | Systematic | Swiss Pulse, Digital Grid |
| Hard cut | Clean | Swiss Pulse, Shadow Cut |
| Liquid dissolve | Elegant | Data Drift, Dream State |
| Slow cross-dissolve | Refined | Velvet Standard |
| Pop cut / bounce | Fun | Play Mode, Carnival Surge |
| Snap cut | Urgent | Red Wire, Contact Sheet |
| Soft dissolve | Warm | Soft Signal, Warm Grain, Quiet Drama |
| Iris wipe | Nostalgic | Heritage Reel |

## The 5-Layer Visual System

Break B-roll scenes into 5 stacked layers. This is the most powerful technique for motion graphics.

| Layer | Purpose | Examples |
|-------|---------|---------|
| **L1** | Background | Textured surface, grid, gradient, color field |
| **L2** | Hero content | Main headline/number that dominates the frame |
| **L3** | Supporting data | Cards, stats, bullet points, secondary information |
| **L4** | Information bar | Tickers, labels, source attributions, quotes |
| **L5** | Effects | Particles, glitches, grid animations, ambient motion |

**Rules:**
- Every B-roll scene: 4+ layers minimum
- Every overlay content side: 3+ layers minimum
- **Every element must MOVE.** No static frames.

### Example: B-Roll Scene with Layers

```
SCENE 2 — FULL SCREEN B-ROLL (12s)
[NO AVATAR — motion graphic only]
VOICEOVER: "One-point-eight-five million signups. Twenty-eight percent month over month."
LAYER 1: Dark #1a1a1a background with thin grid lines pulsing at 8% opacity.
LAYER 2: "1.85M" SLAMS in from left, white Bold 140pt. "+28% MoM" appears in amber.
LAYER 3: Three stat cards CASCADE from top-right, staggered 0.3s.
         Each number COUNTS UP from 0.
LAYER 4: Bottom ticker scrolls: "Non-brand search +36% • Brand impressions 9.2M"
LAYER 5: Grid lines RIPPLE outward on "1.85M" slam.
Hard cut.
```

## Scene Types

| Type | Format | When to Use |
|------|--------|-------------|
| **A-ROLL** | Avatar speaking to camera | Intros, key insights, CTAs, emotional beats |
| **FULL SCREEN B-ROLL** | No avatar, motion graphics only | Data visualization, information-dense content |
| **A-ROLL + OVERLAY** | Split frame: avatar + content | Presenting data while maintaining human connection |

**Rotation is mandatory.** Never 3+ of the same type in a row. Every video needs at least 2 pure B-roll scenes.

**Voiceover on EVERY scene.** Every B-roll scene MUST include a `VOICEOVER:` line. Silent B-roll = broken video.

## Timing Guidelines

| Content Type | Duration |
|---|---|
| Hook/Intro (A-roll) | 6-10 seconds |
| Data-heavy B-roll | 10-15 seconds (NEVER ≤5s — causes black frames) |
| A-roll + Overlay | 8-12 seconds |
| CTA / Close (A-roll) | 6-8 seconds |

**Common video lengths:**
- Social clip: 30-45s (5-7 scenes)
- Briefing: 60-75s (7-9 scenes)
- Deep dive: 90-120s (10-13 scenes)

## Avatar Description Guide

**The avatar is NOT a fixed headshot.** Design it for each video like a movie character.

### Thematic Wardrobe Rule

The avatar's outfit and environment MUST match the content's emotional/cultural context:

| Content Type | Avatar Design | NOT This |
|---|---|---|
| Breaking tech news | Field reporter, windswept hair, earpiece, city skyline | "Anchor at a desk" |
| Data analysis | Black merino turtleneck, minimalist desk, dual monitors with charts | "Business casual" |
| Product launch | Branded tee, open-plan startup space, product prototype on desk | "Generic office" |
| Tutorial | Casual hoodie, messy developer desk, sticky notes, coffee mug | "Presenter in a studio" |

### What to Specify

| Element | Weak | Strong |
|---|---|---|
| Clothing | "Business casual" | "Black ribbed merino turtleneck, high collar framing jaw" |
| Environment | "An office" | "Glass-walled conference room. Whiteboard with hand-drawn tier pyramid" |
| Monitor content | "Computer screens" | "Monitor shows scrolling green terminal text and red security alerts" |
| Lighting | "Well lit" | "Cool blue monitor glow from left, warm amber desk lamp from right" |

### Template (60-100 words)
```
AVATAR: [Clothing — fabric, color, fit, accessories, posture].
[Setting — specific props, brand logos, what's on the walls].
[Monitors/desk — content visible on screens, items on desk].
[Lighting — direction, color temperature]. [Mood of the space].
```

**Remember:** When `avatar_id` is set as an API parameter, do NOT describe appearance. Only delivery style and environment notes. Say "The selected presenter" instead.

## Critical On-Screen Text

List every piece of text that MUST appear literally on screen:

```
CRITICAL ON-SCREEN TEXT (display literally):
- "$141M ARR — All-Time High"
- "1.85M Signups — +28% MoM"
- Quote: "Use technology to serve the message, not distract from it." — Shalev Hani
- "@eve_builds" — exact social handle
```

Without this block, Video Agent will summarize, round numbers, or rephrase quotes.

**Voiceover number rule:** Spell out numbers in speech ("one-point-eight-five million"), use figures on screen ("1.85M").

## What Doesn't Work

Patterns that consistently produce poor results (from 40+ videos):

**Layout language** — Screen coordinates cause empty/black B-roll:
```
❌ "UPPER-LEFT: headline in 48pt Helvetica"
❌ "CENTER-SCREEN: display at coordinates (400, 300)"
✅ "135K" SLAMS in from left, white Impact 120pt, fills 40% of frame.
```

**Named artists without specs** — "Ikko Tanaka style" means nothing to Video Agent. Translate to concrete rules:
```
❌ "Use an Ikko Tanaka style"
✅ "Flat color blocks, maximum 3 colors per frame, 60% negative space, typography as primary element"
```

**Style examples injected into prompts** — Full example scenes from a style library confuse the agent. Use the style's **rules**, not example scenes.

**Forced short B-roll (≤5 seconds)** — Too short for rendering. Every tested video with 5s B-roll had empty/black screens. Minimum 10s.

**Content as a list, not a story** — "Here are 5 tweets" produces flat videos. Always synthesize a thesis: *"X is happening because Y — here's the proof."*

**Static frames** — Every element must have a motion verb. "Title appears" → dead frame. "Title SLAMS in from left" → alive.
