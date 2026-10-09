# Test set — diverse scenes for template stability regression

Canonical test corpus for verifying templates don't regress when we add
features. Pick cases that stress different parts of the pipeline — blend
mode, matte quality, baked-in graphics, luminance extremes, motion.

## The test set

All in `~/Downloads/heygen_relevant_videos/` (720×1290, ~8s, 9:16). Add
landscape + 1:1 as we grow.

| Case            | Scene                                                                      | Stress test                                                                          |
| --------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `Sunset_Stroll` | Outdoor selfie at sunset, palm trees, boardwalk                            | **Bright backdrop** → default `screen` blend fails; needs dark text + `normal` blend |
| `Nature_Vibe`   | Forest golden-hour + **baked timestamp** bottom-left + watermark top-right | Baked graphics avoidance; warm-mid luminance                                         |
| `Gym_Grind`     | Dark gym + dark tank top + phone-mirror selfie                             | **Low luminance** → matte difficulty; screen blend natural fit                       |
| `AI_Insights`   | Podcast studio + neon "THE DIALOG" sign + window view                      | **Competing graphics in BG** (sign, city skyline); mid-tone                          |
| `Kitchen_Buzz`  | Warm kitchen, apron, smiling                                               | Baseline friendly case                                                               |
| `Tech_Trends`   | Clean white studio + mic                                                   | **Max bright backdrop** — needs dark text or opaque BG                               |
| `Street_Talk`   | Walking city street, handheld                                              | Handheld motion + bright outdoor                                                     |
| `Outdoor_Hype`  | Forest + **Instagram watermark** top + sun flare                           | Baked graphic + bright + motion                                                      |

## Usage

```bash
for case in Sunset_Stroll Nature_Vibe Gym_Grind AI_Insights; do
  bash scripts/render-and-composite.sh /tmp/ts-${case}
done
```

## Regression checklist

For every new template or significant change, re-run the test set and
verify:

- [ ] Sunset_Stroll: captions legible on bright sunset (Cinematic cream/screen washes out → use **Standard mode**, opaque rail)
- [ ] Nature_Vibe: captions don't collide with baked timestamp (bottom-left) or watermark
- [ ] Gym_Grind: captions visible on dark gym despite dark subject
- [ ] AI_Insights: captions don't fight with "THE DIALOG" neon sign
- [ ] Tech_Trends: dark text + `normal` blend on pure white studio
- [ ] Each case: 0.5s+ per caption, no wrap-into-subject-head-zone
- [ ] Each case: FG layer for 9:16 portraits where subject fills frame

## Bugs we've fixed via this test set

- **2026-04-23**: Hardcoded `text-shadow: warm-glow + dark-drop` in all
  templates ignored `cap_color` — dark text got overwhelmed by bright
  halo on bright backgrounds. Fix: `TEXT_SHADOW` placeholder with
  luminance-adaptive default.
- **2026-04-23**: Hardcoded `filter: brightness(1.12)` lightened dark
  text, shifting it toward neutral. Fix: `TEXT_FILTER` placeholder that
  drops brightness boost for dark colors.
- **2026-04-23**: `BLEND_MODE` and `CAP_COLOR` hardcoded in new
  templates — plan.json overrides ignored. Fix: placeholders added to
  all 4 templates.

## Expansion plan

Still need to add:

- 1 × 16:9 landscape (from any heygen_relevant via letterboxing, or new source)
- 1 × 1:1 square (if available)
- 1 × multi-speaker (speaker diarization test)
- 1 × foreign language (CJK rendering test)
- 1 × shot-cut (PySceneDetect-required case)
- 1 × product/B-roll (no talking head — refuse gate)
