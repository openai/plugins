---
name: caption-template-motion
description: The named flow + climax entrance/exit recipes (GSAP, seek-safe) that the per-template files reference, plus the motion numerics (ease palette, exit=75% entry, climax dwell, restraint, mood→motion). Every template picks a FLOW_IN/OUT and a CLIMAX_IN/OUT from here — look up only the 2-3 recipes a template names (grep the `### name`), this is a catalog, not a read-through.
metadata:
  tags: gsap, easing, entrance, exit, timing, restraint, mood-matching, captions
---

# Caption Template — Motion Language

`_anatomy.md` wires four hooks onto one paused timeline: `FLOW_IN`, `FLOW_OUT`, `CLIMAX_IN`, `CLIMAX_OUT`. This file is the catalog each template picks from. Each recipe is a GSAP tween on the climax `span` (or a flow `.w`); placed at an absolute time it is fully **seek-safe**. Multi-stage looks use GSAP `keyframes:{}` (still seek-safe) — never CSS keyframes.

## Numerics (shared)

**Ease palette** (sanctioned — reads clean on video, stays distinct):

| Curve           | GSAP                                    | Use                                                 |
| --------------- | --------------------------------------- | --------------------------------------------------- |
| overshoot entry | `back.out(1.4–1.7)`                     | confident arrivals (premium/epic/creator)           |
| heavy/refined   | `power3.out`                            | hero/secondary entrances, slides                    |
| general         | `power2.out`                            | fades, scales                                       |
| exit accel      | `power2.in`                             | the _exit_ side of any move (departure accelerates) |
| snappy          | `expo.out`                              | warp/fly/sonic confident snaps                      |
| breathing       | `sine.inOut`                            | gentle wellness drift                               |
| impact thud     | `back.out(1.5–2)` or a quick `expo.out` | slam/stomp/stamp landings                           |
| linear driver   | `none`                                  | the asr active-word envelope driver only            |
| digital stutter | `steps(n)`                              | glitch/vhs/blink/possess/cut                        |

**Forbidden:** `bounce.out`, `elastic.out` everywhere **except** the Playful cluster (explicit playfulness — KIDS drop-bounce, CANDY jelly). Elsewhere real objects decelerate; they don't bounce. Use low `back.out` for sanctioned overshoot.

**Durations** — flow word enter 0.30–0.50 s · climax entrance 0.6–1.6 s · **exit ≈ 75 % of entry** (arrival deliberate, departure swift) · stagger 50–150 ms / word.

**Restraint (the rule that makes it premium):** the FLOW stays clean — a tasteful reveal + the active-word accent, no effects. The big mood move + any scene effect (flash, shockwave, shake) happens **only at the CLIMAX**, then clears. Never sprinkle effects across the flow.

**Climax dwell ≥ 1 s** after the entrance finishes — the climax is the headline beat.

**Mood → motion** (pick an entrance whose physics match the theme):

| Mood                            | Entrances                                            |
| ------------------------------- | ---------------------------------------------------- |
| premium                         | deblur · rise · expose · breathe · flip              |
| epic                            | slam · monument · fly · grandrise                    |
| cyber                           | glitch · type · scan · boot                          |
| horror                          | loom · possess · glimpse · seep (never bouncy/clean) |
| luxury                          | tracking-expand · hairrise                           |
| retro                           | vhs · stamp · blink · type                           |
| neon                            | ignite · buzz                                        |
| hype                            | stomp · punch · slap                                 |
| playful                         | jelly · dropb · scrawl · popr                        |
| creator                         | boxpop · slideup · flip · shimmer                    |
| ultra (flash in the type)       | volt · hyper · liquid · prism · shatter · extrude    |
| atelier (design)                | editwipe · rise · block · vert · ink · weight        |
| impact (scene effect at climax) | nuke · meteor · sonic · seismic · judge              |

---

## FLOW entrances / exits (per word `.w`)

The flow caption reveals word-by-word from the transcript. The active word gets `.act` (→ `--cacc`). Exit hard-hides the group.

- **fade-up** (premium/atelier default) — `fromTo(w,{opacity:0,y:14},{opacity:1,y:0,duration:.42,ease:'power3.out'})`
- **pop** (epic/hype) — `fromTo(w,{opacity:0,scale:.5},{opacity:1,scale:1,duration:.34,ease:'back.out(1.6)'})`
- **whip** (kinetic) — `fromTo(w,{opacity:0,x:-30,filter:'blur(10px)'},{opacity:1,x:0,filter:'blur(0)',duration:.32,ease:'expo.out'})`
- **glitch** (cyber) — `fromTo(w,{opacity:0,clipPath:'inset(45% 0 45% 0)'},{opacity:1,clipPath:'inset(0)',duration:.4,ease:'steps(6)'})`
- **type** (terminal/retro) — `fromTo(w,{opacity:0},{opacity:1,duration:.2,ease:'steps(3)'})` staggered as the cadence
- **blur-in** (horror) — `fromTo(w,{opacity:0,filter:'blur(10px)',y:'.1em'},{opacity:1,filter:'blur(0)',y:0,duration:.6,ease:'power2.out'})`
- **karaoke** (creator) — words start visible-dim; on `w.start` `set(w,{className:'w act'})` (active → `--cacc`), prior word back to spoken. The signature verbatim mechanic.
- **flow exits** — fade-up-out `to{opacity:0,y:-10}` · horror smear `to{opacity:0,x:6,skewX:10,filter:'blur(5px)'}` · all ≈0.4–0.55 s.

---

## CLIMAX entrances

Each is a `gsap.fromTo(span, {from}, {to, duration, ease})`. Where a `keyframes:{}` is shown, pass it as the 2nd arg's `keyframes`.

### premium

- **deblur** — `{opacity:0,scale:.96,filter:'blur(8px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:.8,ease:'power3.out'}`
- **rise** — `{opacity:0,yPercent:48}→{opacity:1,yPercent:0,duration:.9,ease:'power3.out'}`
- **expose** — `{opacity:0,filter:'brightness(3.2) blur(5px)',scale:1.05}→{opacity:1,filter:'brightness(1) blur(0)',scale:1,duration:1,ease:'power2.out'}`
- **breathe** — `{opacity:0,scale:1.09,filter:'blur(8px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:1.2,ease:'sine.out'}`
- **flip** — `{opacity:0,rotationX:93,transformPerspective:720}→{opacity:1,rotationX:0,duration:.9,ease:'power3.out'}`

### epic

- **slam** — `{opacity:0,scale:1.6,filter:'blur(12px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:.7,ease:'back.out(1.6)'}` (lands with a thud; overshoot ~1.03 mid)
- **monument** — `{opacity:0,scale:1.42,letterSpacing:'.12em'}→{opacity:1,scale:1,letterSpacing:'0',duration:1.3,ease:'power3.out'}`
- **fly** — `{opacity:0,scale:.3,filter:'blur(14px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:.8,ease:'expo.out'}`
- **grandrise** — `{opacity:0,yPercent:66,scale:1.05}→{opacity:1,yPercent:0,scale:1,duration:1.15,ease:'power3.out'}`

### cyber

- **glitch** — `{opacity:0}→{opacity:1,duration:.6,ease:'steps(8)',keyframes:{clipPath:['inset(40% 0 40% 0)','inset(0)','inset(60% 0 10% 0)','inset(0)'],x:[-8,5,-2,0],textShadow:['4px 0 #ff003c,-4px 0 #00ffd1','none']}}`
- **type** — `{opacity:1,clipPath:'inset(0 100% 0 0)'}→{clipPath:'inset(0 0 0 0)',duration:.85,ease:'steps(13)'}` (typewriter L→R)
- **scan** — `{opacity:0,scaleY:.02,filter:'brightness(2.4)'}→{opacity:1,scaleY:1,filter:'brightness(1)',duration:.75,ease:'power3.out'}`
- **boot** — `{opacity:0,scaleY:.1}→{opacity:1,scaleY:1,duration:1,ease:'steps(1)',keyframes:{opacity:[0,.6,.1,.85,.2,1]}}` (hologram power-up flicker)

### horror (never bouncy, never clean)

- **loom** — `{opacity:0,scale:.6,filter:'blur(17px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:1.6,ease:'power2.in',keyframes:{scale:[.6,.93,1.07,1]}}` (slowly approaches out of the dark, then a lurch closer)
- **possess** — `{opacity:0}→{opacity:1,duration:1.15,ease:'steps(1)',keyframes:{x:[0,-5,6,-4,5,-2,0],skewX:[0,9,-10,7,-5,3,0],textShadow:['none','4px 0 #c00,-4px 0 #0aa','-6px 0 #c00,6px 0 #0aa','none']}}` (materialise then violent demonic shudder)
- **glimpse** — `{opacity:0}→{opacity:1,duration:1.35,ease:'steps(1)',keyframes:{opacity:[0,1,0,0,1,0,0,1,.05,1,.15,1],x:[0,0,0,3,0,-2,0]}}` (subliminal failing-light flicker)
- **seep** — `{opacity:0,clipPath:'inset(-15% -8% 100% -8%)',filter:'blur(4px)'}→{opacity:1,clipPath:'inset(-15% -8% -15% -8%)',filter:'blur(0)',duration:1.35,ease:'power1.inOut'}` (blood seeps down into the word; negative insets so script tops aren't clipped)

### luxury

- **tracking** — `{opacity:0,letterSpacing:'-.05em'}→{opacity:1,letterSpacing:'.28em',duration:1.4,ease:'power3.out'}` (the most "expensive" move)
- **hairrise** — `{opacity:0,yPercent:32,letterSpacing:'.07em'}→{opacity:1,yPercent:0,letterSpacing:'0',duration:1.1,ease:'power3.out'}`

### retro

- **vhs** — `{opacity:0}→{opacity:1,duration:.8,ease:'steps(1)',keyframes:{x:[0,-7,6,-3,2,0],textShadow:['none','3px 0 #ff3b5c,-3px 0 #3aa0ff','none']}}` (tracking-lock jitter + chroma)
- **stamp** — `{opacity:0,scale:1.7,rotation:-5}→{opacity:1,scale:1,rotation:0,duration:.7,ease:'back.out(2)'}` (printing-stamp thud)
- **blink** — `{opacity:0}→{opacity:1,duration:.75,ease:'steps(1)',keyframes:{opacity:[0,0,1,0,1,0,1,1]}}` (8-bit blink-in)

### neon

- **ignite** — `{opacity:0}→{opacity:1,duration:1.3,ease:'steps(1)',keyframes:{opacity:[.2,1,.2,1,.3,1,1]}}` (tube strikes + buzzes alight; glow is a style `text-shadow`)
- **buzz** — `{opacity:0}→{opacity:1,duration:1.2,ease:'steps(1)',keyframes:{opacity:[0,.7,.1,.85,.2,1,.5,1]}}` (slower warm-up rhythm)

### hype

- **stomp** — `{opacity:0,scale:1.5,filter:'blur(8px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:.9,ease:'back.out(1.6)'}`
- **punch** — `{opacity:0,xPercent:-55,scale:1.1,filter:'blur(9px)'}→{opacity:1,xPercent:0,scale:1,filter:'blur(0)',duration:.6,ease:'expo.out'}` (whip from the side)
- **slap** — `{opacity:0,rotation:12,scale:1.5,filter:'blur(7px)'}→{opacity:1,rotation:0,scale:1,filter:'blur(0)',duration:.7,ease:'back.out(2)'}` (sticker/tag slap)

### playful (bounce allowed here)

- **jelly** — `{opacity:0,scale:.5}→{opacity:1,scale:1,duration:.8,ease:'back.out(2.2)',keyframes:{scale:[.5,1.12,.92,1.04,1],skewX:[0,0,6,-4,0]}}`
- **dropb** — `{opacity:0,yPercent:-85}→{opacity:1,yPercent:0,duration:.95,ease:'power2.out',keyframes:{yPercent:[-85,0,-22,0,-8,0]}}` (drop + multi-bounce). **❗opacity must reach 1 and stay** — declare it at the end of the keyframes.
- **scrawl** — `{opacity:0,clipPath:'inset(-12% 100% -12% 0)',rotation:-3}→{opacity:1,clipPath:'inset(-12% 0 -12% 0)',rotation:0,duration:.8,ease:'power2.out'}` (handwritten write-on, for script faces)
- **popr** — `{opacity:0,scale:.4,rotation:8}→{opacity:1,scale:1,rotation:0,duration:.6,ease:'back.out(2)'}`

### creator

- **boxpop** — `{opacity:0,scale:.5}→{opacity:1,scale:1,duration:.5,ease:'back.out(1.8)'}` (the active flow word's highlight box is a style)
- **slideup** — `{opacity:0,yPercent:44}→{opacity:1,yPercent:0,duration:.55,ease:'power3.out'}`
- **flip** — see premium
- **shimmer** — `{opacity:0,scale:.7,filter:'brightness(2.2)'}→{opacity:1,scale:1,filter:'brightness(1)',duration:.75,ease:'power2.out'}`

### ultra (the flash lives in the type)

- **volt** — `{opacity:0}→{opacity:1,duration:1.1,ease:'steps(1)',keyframes:{opacity:[0,1,.12,1,.35,1],x:[0,0,0,2,-2,0]}}` then settle to glow `text-shadow:0 0 8px #fff,0 0 22px #43f4ff,0 0 48px #1e90ff` (electric strike)
- **hyper** — `{opacity:0,scale:.05,filter:'blur(3px) brightness(3)'}→{opacity:1,scale:1,filter:'blur(0) brightness(1)',duration:.9,ease:'expo.out'}` (warp from depth)
- **liquid** — `{opacity:0,scale:.9,yPercent:6,filter:'blur(10px)'}→{opacity:1,scale:1,yPercent:0,filter:'blur(0)',duration:1,ease:'power2.out'}` + the `.climax` _container_ carries SVG `filter:url(#liquid)`; in HF drive `feDisplacementMap@scale` from the timeline (don't use SMIL — not seek-safe)
- **prism** — `{opacity:0,textShadow:'-38px 0 #ff003c,38px 0 #00ffd1',filter:'blur(5px)',scale:1.08}→{opacity:1,textShadow:'-3px 0 #ff003c,3px 0 #00ffd1',filter:'blur(0)',scale:1,duration:1,ease:'power3.out'}` (chromatic dispersion converge)
- **shatter** — `{opacity:0,scale:1.9,rotation:-3,filter:'blur(14px)'}→{opacity:1,scale:1,rotation:0,filter:'blur(0)',duration:1,ease:'back.out(1.4)',keyframes:{scale:[1.9,.9,1.06,.98,1]}}` (+ a 1-frame white `text-shadow` flash on landing)
- **extrude** — `{opacity:0,rotationY:42,scale:.9,transformPerspective:700}→{opacity:1,rotationY:-9,scale:1,duration:.9,ease:'power3.out'}` (3D turn; depth via stacked `text-shadow` in the style)

### atelier (design-forward)

- **editwipe** — `{opacity:1,clipPath:'inset(-15% 100% -15% 0)'}→{clipPath:'inset(-15% -4% -15% 0)',duration:.7,ease:'power4.inOut'}` (Swiss precise wipe; negative top/bottom so glyph tops aren't clipped)
- **rise** — see premium (slower, `duration:.9`)
- **block** — `{opacity:0,scaleY:0,transformOrigin:'bottom center'}→{opacity:1,scaleY:1,duration:.7,ease:'power3.out'}` (constructed/Bauhaus)
- **vert** — `{opacity:0,clipPath:'inset(0 0 100% 0)'}→{opacity:1,clipPath:'inset(0 0 0 0)',duration:.9,ease:'power2.out'}` (vertical ink-drop; `writing-mode:vertical-rl` is a style, climax sits at `left:81%`)
- **ink** — `{opacity:0,clipPath:'inset(-28% 100% -28% -4%)',filter:'blur(3px)'}→{opacity:1,clipPath:'inset(-28% -8% -28% -4%)',filter:'blur(0)',duration:.9,ease:'power2.out'}` (brush write-on; generous negative insets for the script face)
- **weight** — `{opacity:0,fontVariationSettings:"'wght' 100",letterSpacing:'.18em'}→{opacity:1,fontVariationSettings:"'wght' 900",letterSpacing:'0',duration:1,ease:'power2.out'}` (variable-font morph; needs a variable face, e.g. Inter `wght@100..900`)

### impact (the ONE sanctioned scene effect, at the climax only)

Each pairs the type move with a scene element (`<div class="flash">` / `<div class="ring">`) and/or a stage shake. Keep it to the climax beat.

- **nuke** — type: `{opacity:0,scale:.3,filter:'brightness(8) blur(10px)'}→{opacity:1,scale:1,filter:'brightness(1) blur(0)',duration:1,ease:'expo.out'}` + white `.flash` `to{opacity:0}` over 0.3 s + brief stage `x` shake
- **meteor** — `{opacity:0,yPercent:-45,scale:1.12,filter:'blur(12px) brightness(2.2)'}→{opacity:1,yPercent:0,scale:1,filter:'blur(0)',duration:1,ease:'power4.in'}` (accelerate DOWN) + on-land stage shake
- **sonic** — `{opacity:0,scale:1.4,filter:'blur(8px)'}→{opacity:1,scale:1,filter:'blur(0)',duration:.9,ease:'expo.out'}` + a `.ring` scaling `0→3` opacity `1→0`
- **seismic** — `{opacity:0,scale:1.1}→{opacity:1,scale:1,duration:.9,ease:'power3.out'}` + stage `x`/`y` quake `keyframes:[3,-3,2,-2,0]` decaying
- **judge** — `{opacity:0,yPercent:-45,scale:1.12,filter:'blur(12px) brightness(2.2)'}→{opacity:1,yPercent:0,scale:1,filter:'blur(0)',duration:1,ease:'power3.out'}` (descends from above) + light-shaft `.flash`

---

## CLIMAX exits

Default is **fade** unless a template names another. **Every exit ends at `opacity:0`** (or fully-clipped) so nothing lingers — declare opacity:0 at the end even on transform/clip exits.

- **fade** — `to{opacity:0,scale:1.03,duration:.6,ease:'power2.in'}` (premium/epic/most defaults)
- **rise-off** — `to{opacity:0,yPercent:-42,duration:.6}` · **sink** — `to{opacity:0,yPercent:16,scale:.97}` · **lift** — `to{opacity:0,yPercent:-26,letterSpacing:'.1em'}`
- **expose-off** — `to{opacity:0,filter:'brightness(3.6) blur(4px)'}` · **breathe-off** — `to{opacity:0,scale:1.08,filter:'blur(7px)'}`
- **flip-off** — `to{opacity:0,rotationX:-90}` · **fly-off** — `to{opacity:0,scale:2.5,filter:'blur(13px)'}`
- **untype** — `to{clipPath:'inset(-15% 100% -15% 0)',opacity:0,ease:'steps(11)'}` (backspace) · **scan-collapse** — `to{opacity:0,scaleY:.02}` · **power-off** — `keyframes:{opacity:[1,.3,1,.1,.5,0]}` + scaleY collapse
- **drag** (horror) — `to{opacity:0,xPercent:-40,skewX:-20,filter:'blur(11px)',duration:.55,ease:'power2.in'}` (dragged away)
- **snap** (horror) — `keyframes:{x:[0,7,-6,0],skewX:[0,-13,0],scale:[1,1.1,1.16,1.32],opacity:[1,1,1,0],textShadow:['none','8px 0 #c00,-8px 0 #0aa','none','none']}` (violent jerk then gone)
- **cut** (horror) — `keyframes:{opacity:[1,0,1,0,.8,0]},ease:'steps(1)'` (frame-drop) · **bleed** — `to{opacity:0,yPercent:50,scale:.97,filter:'blur(6px)'}` (drips down)
- **knock** — `to{opacity:0,xPercent:55,filter:'blur(9px)'}` · **peel** — `to{opacity:0,rotation:14,xPercent:42,scale:.9}` · **spin-out** — `to{opacity:0,rotation:180,scale:.3}`
- **hop** — `keyframes:{yPercent:[0,-26,120],opacity:[1,1,0]},scaleY:.7` · **popout** — `to{opacity:0,scale:.3,rotation:-10}` · **slidedown** — `to{opacity:0,yPercent:42}` · **scrawl-off** — `to{opacity:0,yPercent:-14,rotation:2}`
- **vhs-out** — `keyframes:{x:[0,-9,8,0],opacity:[1,1,0]},scaleY:.2` (tracking-lost roll) · **blink-out** — `keyframes:{opacity:[1,0,1,0,1,0,0]},ease:'steps(1)'` · **power-down** — `keyframes:{opacity:[1,.2,.7,.1,0]},ease:'steps(2)'` · **lift2** — `to{opacity:0,scale:1.12,filter:'blur(3px)'}` (stamp lift) · **shim-out** — `to{opacity:0,scale:.8,filter:'brightness(1.9)'}`
- **iris-close** — `to{opacity:0,clipPath:'circle(0% at 50% 46%)'}` (Bond) · **un-shine** — `to{opacity:0,clipPath:'inset(0 0 0 100%)',filter:'brightness(1.7)'}` · **sweep-off** — `to{opacity:1,clipPath:'inset(0 100% 0 0)'}`
- ultra family exits: **glitch-out**, **neon-out**, **hyper-out** `to{opacity:0,scale:2.6,filter:'blur(13px)'}`, **liquid-out** `to{opacity:0,yPercent:40,scale:.96,filter:'blur(9px)'}`, **prism-out** (channels split apart), **shatter-out** `to{opacity:0,scale:1.45,filter:'blur(9px)',textShadow:'7px 0 #ff003c,-7px 0 #00ffd1'}`

## Pairs with HF skills

- `hyperframes-gsap` — single paused timeline, transform aliases, ease list, the animated-property allowlist.
- `_anatomy.md` — where these four hooks attach.
- `hyperframes-animation/rules/asr-keyword-glow.md` — the verbatim active-word envelope for the flow.
