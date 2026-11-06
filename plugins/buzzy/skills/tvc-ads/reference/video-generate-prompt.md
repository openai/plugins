# TVC ADS — 分段成片

每段生成一段**新片子**。不要把参考视频当成片输入。
**HARD — 成片单元是 segment，不是 shot**：`N` = `plan` 校验通过后的 `SegmentCount`。成片正文使用计划阶段留下的分段内容，按本文「紧凑镜头时间线（Compact Shot Timeline）」格式注入，严禁把包含 `| --- |` 的原始 Markdown 管道表格或冗余元数据列原样粘入 Prompt。禁止按分镜表每一行、每一张 Chat 卡片、或某一个 2s/3s shot `Duration` 调一次 `generate_video`。还没有通过 `plan-and-opening.md` §Shot ≠ Segment 的进入前校验 → 先本地重切或重跑计划，禁止直接成片。媒体**只传 URL 字段**（`image_url` / `image_urls` / `video_url` / `video_urls`，以 tool 声明为准），数量 = 正文里实际出现的 `<<<image_n>>>` 个数。图进 image_*。**禁止传 `nodeIds`**。prompt 正文不要写 HTTPS / `@Image`。opening 规则见 `slot-adaptation.md`。声音统一规则见 `voice-direction.md` 与本文「统一声音描述」。
`title` = `TVC Clip {i}`；时长 = 该段 `segment_duration` / `VideoSegmentDurations[i]`（合并后的段长），**不是**分镜某一行的 Duration。
`generate_video.model` = `<available_models>` Video 表 **seedance-2.0-fast** 行的 `model` 列原文（`name` 只用来找行）。
`aspectRatio` / `resolution`：只传该行 `ratios` / `resolutions` 里的 token。`SessionRatio` / `SessionVideoResolution` 在表里就原样用；不在表里 → 该行第一个合法 token（或再问一次）。`ratios=fixed` 或 `resolutions` `-` / 空 → 对应字段整项省略。禁止写死 `720p` / `1080p`。
本条只约束 `generate_video` 入参。禁止用模型表裁剪 info_card 候选项；规格题必须按 SKILL §info_card 字面量发出（画幅 4 档、分辨率 3 档）。再问一次时同样用全档，不要改成模型表子集。

**HARD — 提示词长度硬限制（≤ 2000 字符）与字符预算**：平台模型对 `generate_video.prompt` 有严格的 2000 字符硬限制，**总字符数必须严格 ≤ 2000**（安全目标 ≤ 1800 字符，严禁突破 2000 字符报错）。成片提示词必须按以下预算执行：
- 开场句与资产引用（`OpeningLookSentence` + `Reference assets`）：≤ 200 字符；
- 画面与动作时间线（`SegmentVideoPrompt`）：≤ 1000 字符（使用紧凑镜头时间线，去除非核心元数据）；
- 规格声明（`Follow only this segment...`）：≤ 150 字符；
- 紧凑声音块（`VoiceProfileBlock`）：≤ 450 字符（使用高密度紧凑版，严禁长篇大论）。

调度（HARD）：进入 `video` 前确认 `N = SegmentCount`（合并后的段数，不是 `ShotCount`）。先只生成 Clip 1。Clip 1 成功返回后，若平台支持独立音频参考槽则绑定其旁白音频 URL；若平台明确不支持则直接使用 fallback VoiceProfile 匹配约束，不要等待不存在的槽位。随后在**同一 action 并发**发起 Clip 2…N；后续片段仍必须逐字复用同一份 `VoiceProfile`。Clip 1 失败只重跑 Clip 1；Clip 2…N 中部分失败时只并发重跑失败段，不重跑已成功片段。N=1 时直接生成 Clip 1 并进入合成（先询问配乐）。`generate_video` 调用次数必须等于 `SegmentCount`，禁止等于分镜行数。
**HARD**：每段 `generate_video` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（PENDING/RUNNING 就继续查；视频通常要数分钟，不要停、不要等用户下一句）。记下素材 URL。Apps widget 不能代替轮询。Clip 1 终态前禁止发 2…N。全部终态后才能发配乐提问。后续 `merge_videos` 挂各段成片 URL，**禁止传 `nodeIds`**。

## 统一声音描述（HARD — 紧凑高密度注入）

每个视频片段都必须携带同一份 `Voice Profile` / `Sound Identity`，该描述由 script 阶段确定并在所有片段中逐字复用。为防止总提示词超过 2000 字符硬限制，成片 Prompt 必须使用**高密度紧凑版声音块（≤ 450 字符）**，严禁注入长篇大论的散文型声音描述。

### Compact Voice Profile（≤ 180 字符）

在生成第一个片段前，从分镜脚本中提炼一份紧凑的 English 声音身份描述（保持全片统一）：
`[Speaker identity], [age & accent], [vocal register & timbre], [pacing ~2 words/sec], [overall tone], [mic/recording character].`

示例（紧凑高密度）：
```text
Narrator early 30s, neutral international English, warm low-mid register, gentle resonance, natural breath, relaxed conversational 2 words/sec pace. Intimate, observant, quietly confident. Close natural mic, no BGM.
```

### 紧凑声音块（Compact Audio Block，≤ 450 字符）

每个片段在画面时间线后追加以下紧凑声音块：

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
{Only this segment's pause placement, emphasis, and emotional intensity (≤ 50 chars).}
```

### Clip 1 音色参考状态

- `Clip1Status` 必须先为 `done`，后续 Clip 2…N 才能开始生成。
- `Clip1AudioReference` 优先保存平台实际返回的独立旁白音频 / 声音参考 URL。若能力声明明确没有独立音频参考槽，则使用 `fallback: VoiceProfile + Clip 1 matching instruction` 继续，不要无限等待；不要把 Clip 1 视频 URL 当成音频参考。
- 如果平台没有独立音频参考槽，后续片段仍必须逐字携带同一 `VoiceProfile`，并写明匹配 Clip 1 的 voice identity、timbre、resonance、pronunciation、pacing character 和 recording character。

### 声音描述执行规则

- `VoiceProfile` 必须在所有片段中保持一致，不得由 agent 根据单段内容重新改写。Clip 1 成功后，将 Clip 1 的旁白音频 URL 作为后续片段的 voice reference；如果平台没有可绑定的音频参考槽，必须在后续片段正文中明确要求 match Clip 1，但不得声称实现了技术级音色锁定。
- 每段 `Dialogue` 仍需逐字保留；只允许根据该段动作调整局部停顿、重音和情绪强度。
- Dialogue 中真正发声的字必须放在引号内；表演说明明确标记为 `not spoken`。
- `Sound Design` 必须描述可见动作产生的真实声音，并与画面接触点同步。只生成真实环境音、动作 Foley 和必要的自然空间底噪。永远不生成 BGM 或任何音乐层。
- 如果某段没有对白，仍携带同一 `VoiceProfile` 作为全片声音身份参考，但明确写 `No spoken words in this segment.`，不要凭空添加台词。
- 如果平台提供独立 voice reference / voice ID 槽，优先绑定同一声音参考 URL；如果没有，只能把以上内容作为提示词约束，不能宣称已实现音色锁定。

## 参考槽

从左到右、有才加入；禁止空占位、禁止同一 URL 挂两次。

| 顺序 | 何时挂 | 正文怎么写 |
|------|--------|------------|
| 该段开场视觉 | 有则挂（预览图或首帧；Skip 开场视觉则省略） | `<<<image_n>>>` 写成 visual reference for opening look and framing。有开场视觉时，在正文前加一句：以该开场图为起始画面 |
| 产品主图 | 有则挂 | `<<<image_n>>>` 写成 the target product |
| 该段用到的角色图 | 有参考且 `CharacterVisualPlan=run` 或 `provided` 时，按 `character_index` | `<<<image_n>>>` 写成 the on-screen talent |
| Clip 1 旁白音频 | 仅 Clip 2…N，且平台提供独立音频参考槽时 | 挂 Clip 1 的音频 URL；不要把 Clip 1 画面当作后续片段的视觉参考 |

opening 已经是产品图时，不要再挂第二个产品槽。
无开场视觉、只有产品图时，写明以产品图为起始视觉。
**禁止**挂参考视频、分镜表、卖点正文、Prompt 文本。

## 紧凑镜头时间线（Compact Shot Timeline）

为了防止包含多镜的段落膨胀超标，将该段所包含的各镜整理为紧凑时间线（保留核心事实，去除 `|` 管道符、分隔行、Keyframe、Background Music 列等冗余信息）：

每镜 1–2 行：
```text
Shot {Shot No.} ({Start}-{End}s): {Framing & Camera Move}, {Visual action & subject motion}. Dialogue: "{Spoken Words}" (delivery: {direction}). Sound: {Foley / Ambience}.
```
（无台词则写 `Dialogue: None`；若原表有 Scene / Lighting 简短融入视觉描述即可，不要竖排堆砌字段名）。

## 正文组装与自检（HARD）

成片正文按以下结构组装：

```text
{OpeningLookSentence}

Reference assets:
{AssetLines}

Timeline:
{CompactShotTimeline}

Follow only this segment. Duration {SegmentDuration}s, aspect ratio {SessionRatio}, resolution {SessionVideoResolution}. Stay consistent with every referenced <<<image_n>>> bound for this clip. Spoken language is English. Do not burn in subtitles.

{CompactAudioBlock}
```

| 槽 | 怎么填 | 预算上限 |
|----|--------|----------|
| `{OpeningLookSentence}` | 有开场视觉 → `Start from the opening look in <<<image_1>>>`. 无开场、只有产品图 → `Start from the product look in <<<image_1>>>`. 连产品图都没有 → 不要硬成片 | ~50 chars |
| `{AssetLines}` | 只写已挂槽，`n` 按出现顺序从 1 递增 | ~150 chars |
| `{CompactShotTimeline}` | 该段各镜紧凑时间线，保留核心动作、运镜、台词与声效 | ~800-1000 chars |
| `Follow only this segment...` | 规格声明语句 | ~150 chars |
| `{CompactAudioBlock}` | 紧凑声音块（CompactVoiceProfile + Audio rules + Local performance） | ~400 chars |

### 长度自检与修剪机制（Self-Check & Prune HARD）

组装成最终提示词字符串后，在调用 `generate_video` 前必须检查字符数：
1. **目标范围**：总长度 ≤ 1800 字符最佳，绝对不可超过 2000 字符。
2. **超长修剪（若总长 > 1900 字符）**：
   - **第一级修剪**：压缩时间线中的次要环境修饰词与背景说明，仅保留「主体动态 + 运镜动作 + 引号内台词 + 核心音效」；
   - **第二级修剪**：将声音块压缩至核心 3 行（`Audio rules: Speak ONLY quoted dialogue, no notes/labels. Real action foley & room tone only, NO BGM. Clip 2+: match Clip 1 narrator.`）；
3. **硬性底线**：严禁向 `generate_video` 传入超过 2000 字符的 prompt。任何超出必须在本地修剪合格后再发起调用。

## 合成

普通模式：Clip 1 成功后按调度发齐后续段；全部分段 `get_task` 成功后，对 Host tools 发配乐闸门，等用户选 `No music` 或 `Add background music`。问句 = `Do you want background music in the final video?` 选项只进 `options`，禁止 Chat 编号列表。选 `No music` → 直接以原生音轨合成；选 `Add background music` → 合成时在原生音轨上叠加音乐。该选择只影响最终合成，不得反向改写任何片段音轨。
FastForward 到 merge → 同样先问配乐，再按选择合成。
`video_infos` 按片段序原样带上每段成片 URL。`merge_videos` 必须挂上**全部**分段成片 URL，禁止传 `nodeIds`。
N=1 仍走配乐闸门（单段配乐）。Skip(`merge`) → 以分段成片为结束。

```text
AskQuestion
title: Final audio
questions:
  - id: background_music
    prompt: Do you want background music in the final video?
    options:
      - id: no_music
        label: No music
      - id: add_bgm
        label: Add background music
```

## 仍禁止

- 把参考视频传入成片
- 只挂 URL、不内联该段视频正文
- 把作废旧开场视觉当成 provided
- Rollback 重做分段后自动合成
- 空 `<<<image_n>>>`、同一 URL 挂两次
- Clip 1 未成功就发 2…N
- 用 Apps widget 代替 `get_task`
- 把 `nodeIds` 传给 generate_image / generate_video / run_prompt / merge_videos
- 按分镜表 / Chat 卡片「一镜一段」成片（2s/3s shot 单独 `generate_video`）
- 把 shot `Duration` 填进 `generate_video.duration`
- 传入超过 2000 字符的提示词导致 `generate_video` 报错（必须过自检修剪）
