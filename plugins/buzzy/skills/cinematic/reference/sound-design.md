# Cinematic — Sound Design（成片词里的声音）

成片词只写**画内声**。配乐不写进 `generate_video.prompt`，只走 `merge` 闸门。

禁止：`BGM` / `background music` / `scored music` / `orchestral score` / `music bed` / `music crescendo`。
必须：词末 `no background music`。

## Ambient（环境底）

"Ambient bed: continuous subtle environmental sound suggesting [location]. Heard under dialogue, never competing. Begins at 0s, continues throughout."

例：room tone、wind、distant traffic、ocean、forest。

## Foley（物性）

"Foley synchronized to visual action: footsteps match walking cadence, object falls at frame-4.2s with thud impact, clothing rustle during movement."

## Dialogue

"Dialogue enters at 3.2s: [character] speaks [quote]. Delivery: [emotional tone]. Dialogue sits above ambient and foley. Subtle reverb suggesting [location acoustic]."

只有引号内文字发声。表演提示标 `not spoken`。

## Sound Effects（冲击点）

"Sound effect impact: at 7.5s visual cut, synchronize explosive sound (gunshot/collision). 0.3s attack, 0.5s decay. Peaks louder than ambient/dialogue."

## Silence

"1.5–2.5s complete silence—no dialogue, minimal ambient. At 2.5s, sudden audio re-entry (dialogue explosion, sound effect). Contrast maximizes impact."

## Spatial

"Dialogue processed with 1.2-second reverb tail suggesting cathedral. Foley reverb 0.4 seconds suggesting intimate room. Ambient dry."

## 用户若上传了音频

当前 `generate_video` 声明里**有** `audio_url` / `audio_urls` → 把真实 URL 传进去，词里用 `<<<` 对应占位（若 schema 要求）并写清这是对白 / 音效，不是配乐。
声明里**没有** → 不要发明字段；把对白 / 音效写成文字时间戳。用户要的配乐仍然只走 merge。
