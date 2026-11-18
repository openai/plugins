# Cinematic — Example Prompts

形状参考，禁止原文照抄到无关 brief。样例里的配乐句**不要**写进 `generate_video.prompt`；改成画内声 + 视觉强度。每份词末尾 `no background music`。分辨率不要写死，继承 Session。

参考图用 `<<<image_1>>>` 点名。没有参考就删 REFERENCE 段。

---

## EXAMPLE 1: Film Noir Detective

```
CINEMATIC VIDEO PROMPT - NOIR DETECTIVE MOMENT

[OPENING HOOK — 0 to 2 seconds]
Black screen complete silence. At 0.8s, explosion of cool blue light
from frame-left corner. Single harsh 5000K light. Hard-edged shadow
across center. Disorientation as light invades blackness.

[ESTABLISHING CONTEXT — 2 to 4 seconds]
1940s noir warehouse, cool grey concrete, metal beams. Camera 40 feet
back, low angle 15 degrees looking up. 35mm equivalent. Chiaroscuro:
hard 3000K key upper-left 60 degrees, fill 15%. 35mm grain.

[PRIMARY ACTION — 4 to 8 seconds]
Slow dolly forward 1.5 ft/s, low angle. Detective silhouette materializes
in center shadow-pool. At 5.5s face catches overhead light, eye glint.
At 6s pulls cigarette from pocket (silhouette).

[DEPTH & COMPOSITION]
Foreground: concrete striations. Mid: detective silhouette. Background:
beams in deep shadow. Asymmetrical: figure right-of-center, 70% shadow.

[CLIMAX — 8 to 10 seconds]
At 8s lights cigarette. Weathered face. At 8.3s desk lamp flicks on
frame-right, two-source conflicting shadows. Turns camera-left.
At 9.5s fade to black, silhouette profile.

[CAMERA]
f/2.0 shallow. Focus locked on face. 1.5 ft/s constant. Duration:
VIDEO_DURATION. Aspect: VIDEO_RATIO.

[COLOR]
Bleach bypass noir: lifted crushed blacks, 0% saturation, grain 150%.
Only light sources and skin keep slight 2500K warm. Cold blue shadows.

[AUDIO]
0–1s silence. 4–7s Foley: footsteps on concrete, clothing rustle.
8–8.3s match-scratch lighter. no background music

[REFERENCE]
<<<image_1>>> if a warehouse or character still is bound: match wardrobe
and concrete texture, not a new identity.
```

---

## EXAMPLE 2: Epic Landscape Aerial

```
CINEMATIC VIDEO PROMPT - EPIC AERIAL LANDSCAPE

[OPENING HOOK — 0 to 2 seconds]
Extreme reverse macro: inches from a water droplet refracting the
landscape upside-down. At 0.5s whip-pull backward. At 1.2s extreme
wide desert valley, layered mountains. Scale shock at 2s.

[ESTABLISHING — 2 to 4 seconds]
High-altitude valley. Golden hour 3200K. Aerial 200 feet up. 28mm
ultra-wide. Warm directional light frame-right. Volumetric god-rays.
Three depth layers: rocky foreground, valley mid, receding mountains.

[PRIMARY ACTION — 4 to 10 seconds]
Crane descend 3 ft/s from 200 feet. Tilt adjusts to keep foreground.
At 6s valley-floor boulders and vegetation. At 8s decelerate to 1 ft/s.
At 10s hover 20 feet, 90-degree pan left.

[CLIMAX — 10 to 15 seconds]
Hover + pan reveals hidden canyon. Sun kisses mountain-top frame-right,
edge-light terrain. Slow pull-back; tiny human figure sells scale.

[CAMERA]
28mm, f/5.6 deep focus, locked on valley floor. Duration VIDEO_DURATION.
Aspect VIDEO_RATIO.

[COLOR]
Golden hour 3200K. Saturation +20% on gold. Shadows warm 2000K.
Sky peachy-orange, not blue.

[AUDIO]
Wind at altitude, rushing air during descent, quieter near ground.
no background music

[REFERENCE]
<<<image_1>>> location still: match ridge lines, haze, and scale.
```

---

## EXAMPLE 3: Dramatic Dialogue Close-Up

```
CINEMATIC VIDEO PROMPT - DRAMATIC DIALOGUE MOMENT

[OPENING HOOK — 0 to 2 seconds]
Silent black 0–1.2s. At 1.2s cut to extreme close-up of an eye opening.
Iris dilates 0.3s. At 1.8s micro-zoom, tear glistening. On-camera eye
contact.

[ESTABLISHING — 2 to 4 seconds]
Intimate interior. Medium close-up, 2 feet from face. 50mm portrait.
Soft three-point: 3000K key 45° left 60%, fill 40% right (2:1), rim 45%.
Warm lamplight.

[PRIMARY ACTION — 4 to 8 seconds]
Head turns 45° to full front over 2s. At 5s mouth opens — dialogue
begins: "[exact line]". Delivery: whispered, intense. f/1.4, face
sharp, circular lamp bokeh. Focus locked on eye.

[CLIMAX — 8 to 10 seconds]
Key line at 8s. Camera push-in 6 inches over 3s (1 in/s). Natural
blinks. At 9.5s jaw clench. At 10s pull-back 6 inches.

[CAMERA]
50mm, f/1.4, eye lock. Duration VIDEO_DURATION. Aspect VIDEO_RATIO.

[COLOR]
3200K interior. Skin saturation 110%. Warm lifted shadows. +0.3 stop.
Slight highlight diffusion 5%.

[AUDIO]
0–2s silence. 2–7.5s minimal room tone. Dialogue at 7.5s, 0.3s reverb
tail. no background music
```

---

## EXAMPLE 4: High-Speed Chase

```
CINEMATIC VIDEO PROMPT - ADRENALINE CHASE

[OPENING HOOK — 0 to 2 seconds]
Black silence 0–0.8s. At 0.8s: whip-cut to high-speed movement.
Subject enters from frame edge at extreme velocity. Motion blur 20%
trails. Synchronized impact SFX (not music).

[ESTABLISHING — 2 to 4 seconds]
Urban street, concrete. Low 25° tracking from behind-left. 35mm.
Harsh midday 5500K, hard geometric shadows, temporal parallax.

[PRIMARY ACTION — 4 to 9 seconds]
Subject ~35 mph. Camera 4-foot gimbal follow, subject frame-right.
4–5s obstacle. 5–6s alley compression. 6–7s faster blur. 8–9s
near-collision / sharp turn.

[CLIMAX — 9 to 12 seconds]
Maximum danger at 9s. Camera 5+ ft/s. At 9.5s impact + optional
0.3s slow-mo. 10–11s aftermath, reduced speed.

[CAMERA]
35mm, f/4–f/5.6, focus locked on subject. Gimbal-smooth. Duration
VIDEO_DURATION. Aspect VIDEO_RATIO.

[COLOR]
Saturation 120%. Slightly crushed shadows. Teal-orange split.
Background slightly desaturated so subject pops.

[AUDIO]
0–0.8s silence then impact SFX. Foley footsteps escalate with speed.
Breathing, rushing wind, Doppler whoosh past obstacles.
no background music
```

---

## EXAMPLE 5: Tender Farewell

```
CINEMATIC VIDEO PROMPT - TENDER EMOTIONAL FAREWELL

[OPENING HOOK — 0 to 2 seconds]
Extreme close-up two hands almost-touching over wood. 1 inch gap.
Fingertips sharp, hands fall to black bokeh. At 1.2s one hand
approaches. At 1.8s fingertips barely touch.

[ESTABLISHING — 2 to 4 seconds]
Small intimate interior, practical lamps. Eye-level, 3 feet from
hands. 50mm. Soft three-point 2700K key 45° left 50%, fill 40%,
rim 30%.

[PRIMARY ACTION — 4 to 10 seconds]
Two figures seated. Camera at table height, favor primary.
4–5s primary hand extends 4 in/s. 5.5s contact, fingers interlace.
6–8s slight tremor. Secondary looks from hands to face. 8–9s
primary leans in.

[CLIMAX — 10 to 12 seconds]
Eye contact locks. Push-in 12 inches over 1.5s. Optional tear.
Gentle smile. Hands stay connected.

[CAMERA]
50mm, f/1.2, hands and faces. Duration VIDEO_DURATION. Aspect VIDEO_RATIO.

[COLOR]
2700K. +200K on faces. Soft lifted shadows. +0.5 stop. Saturation 90%.
Highlight diffusion 3%. Optional vignette.

[AUDIO]
Quiet room tone. Soft table-touch Foley at contact. Natural breath.
no background music. No dialogue.
```
