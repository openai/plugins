# Cinematic — 2-Second Hook Framework

写词时前 2 秒必须有感官冲击。这是本链和普通「先建立镜头」写法的分界。

## Why 2 Seconds

- 无意识注意在 0.5–2 秒触发
- 短视频算法偏好撑过 2 秒的片子
- 电影开场也是冲击：*Blade Runner 2049* 霓虹、*Dunkirk* 立刻混乱、*1917* 长跟张力

## Hook Table

| Hook Technique | Cinematic Effect | Prompt Phrasing Template |
|---|---|---|
| **Extreme Close-Up Snap to Wide Reveal** | Disorientation → context clarity | "Open with extreme macro close-up of [detail: water droplet, dust mote, fabric weave]. At 0.5s, whip cut to extreme wide shot of [landscape/space]. Contrast ratio 100:1." |
| **Black Screen to Dramatic Light Burst** | Silence then explosion | "Begin in pure black. At 0.8s, explosive light burst from [direction: top-left corner]. Golden/amber light floods frame in 0.3s. Lens flare blooming across center." |
| **Reverse Motion That Catches the Eye** | Unnatural = immediately interesting | "Action moves backwards in first 2 seconds: [object] slides in reverse across frame with momentum. Water droplets float upward. Smoke swirls counterclockwise. Hypnotic, impossible motion." |
| **Unexpected Scale — Macro Detail of Familiar Object** | Cognitive dissonance | "Extreme macro photography of mundane object: fabric texture, concrete pores, leaf veins, raindrop surface. Treat as vast landscape. Shallow depth of field, cinematic bokeh. Viewer doesn't recognize scale for 2 seconds." |
| **Silent Beat Then Explosive Sound** | Audio contrast | "First 1.2 seconds: complete silence. No dialogue, minimal ambient. At 1.3s, sudden violent sound: gunshot, explosion, door slam. Synchronized video cut/freeze/blur at audio moment. no background music" |
| **Extreme Color Shift** | Palette punch | "Frame opens in cool desaturated blue-grey. At 0.6s, sudden color correction to warm amber-gold or saturated neon. 50% color shift in 0.4s. Creates 'time jump' or 'reality shift' feel." |
| **Fast Movement Entering Frame** | Peripheral motion | "Subject enters frame with high-speed movement: speeding car, sprinting figure, falling object, camera push-in at high velocity. Enter from edge (not center), create leading lines." |
| **Extreme Depth of Field Rack Focus** | Attention via focus | "Two planes of focus: foreground and background both sharp initially. At 1s, focus racking to dramatic foreground (completely blurring background), or vice versa. Shallow depth (f/1.4 cinema equivalent)." |
| **Stark Geometric Contrast** | Visual tension | "Frame composition: extreme geometric contrast in first 2s. Sharp horizontal lines vs vertical elements. High-contrast lighting emphasizes geometry. Asymmetrical frame." |
| **Protagonist's Eyes Open/Look** | Primal attention | "Close shot of eyes in low-light. At 0.8s, eyes snap open or lock on-camera. Dilating pupil effect optional. Followed by subtle head tilt or eye direction shift." |
| **Disorienting Camera Rotation** | Sensory engagement | "Camera tilts, rolls, or rotates rapidly in frame 0–1.5s. 45°–180° rotation. Tilted horizon line. Stabilizes to level frame at 2s marker." |
| **Scale Impossibility** | Awe or claustrophobia | "Tiny human figure in impossibly vast landscape [desert, ocean, space]. OR giant object in confined space. Emphasize scale via distance, leading lines, proportion." |

## Hook Stacking

一层 2–3 个钩子叠在前 2 秒：

- Black screen (silence) + color burst + extreme close-up revealing landscape
- Reverse motion + eyes opening + geometric contrast

从问询 `HookPlan` 取主钩子；用户没选就按 `MoodGenre` 挑一个，不要每片都用 black-to-burst。
