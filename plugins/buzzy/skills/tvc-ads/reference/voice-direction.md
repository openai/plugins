# TVC ADS — 统一声音导演规范

本规范解决两个问题：让口播像真实的人在表达，而不是把一串字读出来；让每个片段的声音有近距离的材质、空间和情绪层次。视频片段只生成原生人声、真实环境音、动作 Foley 和必要的自然空间底噪；片段内绝不生成 BGM 或音乐层（最终合成是否叠加配乐由 merge 配乐闸门决定）。它服务于 `script`、`plan` 和 `video`，不新增阶段，也不新增表格列。

## 1. 先锁定一个全片 VoiceProfile

在第一次生成 script 后，从产品定位、用户选定的内容方向和全部 Dialogue 单元格中确定一份全片唯一的 `VoiceProfile`。将它写入内存，并在 plan 与每个 video prompt 中逐字复用。进入 video 阶段时先生成 Clip 1；Clip 1 成功后把它的旁白音频作为后续片段的 voice reference，再生成其余片段。不要按片段重新设计声音。

VoiceProfile 至少包含：

- speaker identity：narrator 或角色身份；
- apparent age range、accent / pronunciation；
- vocal register、timbre、resonance、breathiness；
- articulation 与 speaking pace；
- prosody：句群长短、音高曲线、重音与停顿习惯；
- emotional baseline 与全片情绪弧线；
- recording / mix character：close-mic or natural distance、dry or lightly reverberant、voice priority in mix。

推荐采用一段可直接复制的 English profile，而不是每段拼几个形容词：

```text
A consistent human narrator in their early 30s, neutral international English with clear natural pronunciation, a soft low-mid register, warm rounded timbre, gentle chest resonance, light natural breath, relaxed conversational articulation, and an unhurried 1.9–2.3 words-per-second pace. Shape phrases in breath groups with small pitch movement and asymmetric pauses; let key words receive quiet emphasis without sounding performed. The emotional baseline is intimate, observant, and quietly assured, opening with curiosity and resolving with calm confidence. Record as a close, natural voice with restrained room tone; keep the spoken voice clearly in front of real environmental sound and foley. Do not generate music, melody, harmony, rhythm, music bed, or background score.
```

上面的内容是结构示例，不是固定人设。根据商品、受众和用户方向改写事实部分，但保持句式和信息完整。没有独立 voice reference / voice ID 时，只能把它当作生成约束，不能宣称已锁定真实音色或跨片段完全一致。

**成片提示词预算注入（HARD — Compact VoiceProfile ≤ 180 字符）**：
为遵守 `generate_video.prompt` ≤ 2000 字符的硬上限，注入视频成片提示词时，必须将上述完整 profile 提炼为高密度的 Compact VoiceProfile（严格 ≤ 180 字符），禁止在成片提示词中堆砌散文长篇大论：
```text
Narrator early 30s, neutral international English, warm low-mid register, gentle resonance, natural breath, relaxed conversational 2 words/sec pace. Intimate, observant, quietly confident. Close natural mic, no BGM.
```

## 2. Dialogue 的写法：先写人话，再写表演

Dialogue 单元格中把“要说的字”和“怎么说”分开，避免模型把表演说明读出来：

```text
Voice-over (spoken words only): "A quiet ritual, made for the moment you return to yourself."
Delivery direction (not spoken): intimate and reflective; one natural breath after “ritual”; slight lift on “return”, then let the final words settle.
```

规则：

- `spoken words only` 后只放真正要发声的文字；`Delivery direction (not spoken)` 后只放表演说明。
- 台词要按呼吸句群组织，不要每句都用相同长度、相同句尾和相同重音。必要时用逗号、句号制造自然落点，不要写成口号列表。
- 情绪变化写成可执行的局部动作：`slight pitch lift`、`brief inhale`、`soften the middle phrase`、`land the final brand word`，不要只写 `emotional` 或 `natural`。
- 口播控制在约 1.9–2.3 English words/second；复杂动作、特写或需要听见 Foley 时降到 1.4–1.8 words/second。宁可少说，不要塞满镜头。
- 速度必须按镜头功能分档，禁止全片统一慢速：钩子、转场、反应插镜和简单信息镜头应紧凑，主变化在首秒内出现；人物交互、手部使用动作、功能演示和叙事推进保持自然 1.0x 实时速度，通常以 1.5–3 秒完成一个明确动作；仅包装、质地、微距材质或最终英雄镜头在可读细节确需停留时才允许 2–4 秒的克制放慢。
- 每个镜头首秒内必须出现新的动作、细节、角度、证明点或叙事信息；一个动作完成后不要用空白慢动作拖时长。除最终品牌收束外，禁止连续两个以上 3–4 秒长停留镜头。
- 每句都要有不同的“进入—展开—落点”形状；不要让相邻句子都以同一音高或同一力度收尾。
- 不要求每镜都有口播。产品揭示、质地特写、关键触摸和最终品牌句前可以留白。
- 片段无对白时写 `No spoken words in this segment.`，禁止凭空补台词。

## 3. Sound Design：建立前景、中景、背景

每个镜头只选择真正可听见且有物理来源的声音，并写清相对层级：

```text
Voice: spoken line with the local delivery direction, clearly foreground.
Foley: close, dry lid click and fingertip contact exactly on the visible movement, below the voice.
Ambience: very low, stable room tone matching the space, with no musical pitch or rhythmic bed.
Music: None. Do not generate BGM, score, melody, harmony, rhythm, tonal pad, or music-like sustained sound.
```

- 只生成真实环境音与动作 Foley：房间底噪、空间反射、空气流动、脚步、衣料、容器、盖子、手指、液体、粉末、乳霜等声音必须有明确的物理来源，并与画面接触同步。
- 永远不生成 BGM、配乐、音乐床、旋律、和声、节拍、音调持续层、低频音乐性轰鸣或电子情绪音效。
- 让声音有对比：重要口播前后降低环境声；关键 Foley 可以短暂靠前；品牌句结束后留 0.4–0.8 秒干净自然空间尾部。
- 不要在每镜堆满 Voice、Foley、Ambience；没有必要的层直接省略或写 `None`。

## 4. 片段生成时必须携带的声音块（紧凑高密度注入，≤ 450 字符）

Clip 1 是全片的声音锚点：先生成 Clip 1 并确认其旁白音频返回成功，再生成后续片段。若平台支持独立音频参考槽，将 Clip 1 的旁白音频 URL 绑定到 Clip 2…N；若平台明确不支持，则直接使用冻结的 VoiceProfile 和 Clip 1 音色匹配文字继续，不要为了等待不存在的音频槽而停住。不能把 Clip 1 画面作为声音参考，也不能宣称技术级锁音。

**成片提示词硬上限约束**：为防止 `generate_video` 超过 2000 字符硬限制，放入每段视频成片正文的声音块必须采用以下紧凑高密度结构（总体控制在 ≤ 450 字符），`{CompactVoiceProfile}` 保持全片统一；局部情绪只写在该段的 `Local performance`（≤ 50 字符），不能重写全局身份：

```text
Global Voice Profile:
{CompactVoiceProfile}

Audio rules:
- Speak ONLY words inside quoted Dialogue lines. Never read directions, labels, or notes aloud. Voice clearly foregrounded; duck foley/ambience when spoken.
- Natural human delivery, conversational breath pauses, no monotone TTS.
- For Clip 1: establish identity and mic distance. Clip 2+: match Clip 1 voice identity, timbre, and pacing.
- Sound: Real action foley & room tone only. NO BGM, music bed, melody, or emotional score.
- Preserve silence where no spoken words are indicated.

Local performance:
{segment-specific pauses, emphasis, and emotional intensity only}
```

如果平台支持独立 voice reference / voice ID，优先在同一声音槽绑定 URL；若当前能力没有该槽，不要伪造音频，也不要在结果中声称已完成音色锁定。

## 5. 验收

生成后检查：

1. 台词是否在可用时长内，并且留出了呼吸与物理声音空间；
2. 相邻镜头是否有句长、停顿、重音和情绪强度变化；
3. 是否能看出清晰的音频层级：Voice > 关键真实 Foley > 环境底噪；
4. 是否误把元数据或表演说明当成口播；
5. 是否存在无物理来源的音效、音乐性持续音、低频轰鸣、每句同调收尾或播音腔；
6. 所有片段是否逐字复用同一 VoiceProfile，并只改变局部表演。
