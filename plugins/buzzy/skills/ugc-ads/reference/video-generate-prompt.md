# UGC ADS — 成片正文

每段生成一段**新片子**。agent **按本文件模板直接写出** Prompt，禁止 run_prompt。
不要把参考视频当成片输入。媒体**只传 URL 字段**（`image_url` / `image_urls` / `video_url` / `video_urls`，以 tool 声明为准），数量 = 正文里实际出现的 `<<<image_n>>>` / `<<<video_n>>>` 个数。图进 image_*，视频进 video_*。**禁止传 `nodeIds`**。prompt 正文不要写 HTTPS / `@Image` / `@Video`。
`title` = `UGC Video {i}`；时长 = 该段 Duration。
`generate_video.model` = `<available_models>` Video 表 **Seedance 2.0 Fast** 行的 `model` 列原文。
`aspectRatio` / `resolution`：只传该行 `ratios` / `resolutions` 里的 token。`SessionRatio` / `SessionVideoResolution` 在表里就原样用；不在表里 → 该行第一个合法 token（或再问一次）。`ratios=fixed` 或 `resolutions` `-` / 空 → 对应字段整项省略。禁止写死 `720p` / `1080p`。

调度：Video 1 先发，`get_task` 阻塞轮询到成功后同轮发齐 2…N。后续段必须参照 Video 1。
**HARD**：每段 `generate_video` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（PENDING/RUNNING 就继续查；视频通常要数分钟，不要停、不要等用户下一句）。记下素材 URL。Apps widget 不能代替轮询。后续段 `generate_video` 用这些 URL（Video 1 的视频 URL 挂进 `video_url(s)`）。`merge_videos` 挂各段成片 URL，**禁止传 `nodeIds`**。

**禁止**把真实 `@Image …` / `@Video …` 或 URL 写进正文。
**禁止**只挂节点而不写 Timeline。Timeline 由本段 extract **改写**，禁止整段粘 extract。

---

## 占位与挂载

组槽从左到右、有才加入；禁止空占位、禁止同一 URL 挂两次。

| 顺序 | 何时挂 | 正文怎么写 |
|------|--------|------------|
| 该段首帧 | 有则挂 | `<<<image_n>>>` 写成 visual reference for opening look and framing。**禁止**写 first frame / opening frame / 首帧 |
| 产品主图 | 必挂 | `{{Product}}` 句式，占位用 `<<<image_n>>>` |
| 角色图 | 有则挂 | `{{Talent}}` 句式，占位用 `<<<image_n>>>` |
| 场景图 | 有则挂 | `{{Scene}}` 句式，占位用 `<<<image_n>>>` |
| Video 1 成片 | 仅 i≥2 | `<<<video_1>>>` |

缺角色 / 场景 → **整行省略**，不要写 `(none)` 或空 `<<<image_n>>>`。
无任何产品图且无其它视觉 → 不要硬成片，请用户补图。

有用户声音参考时，在语言句后插入：`The voiceover sound is based on the referenced video.` 并把该视频 URL 挂进 `video_url(s)`。无则整项省略。

---

## 固定句式（复制后填槽）

槽名仅中文标注，**禁止**抄进 Prompt；填入值必须 English（口播 / 花字跟 `SessionScriptLanguage`）。`{SessionRatio}` 用规格提问原文，禁止写死 `9:16`。

```text
Generate a {SegmentDuration}-second, {SessionRatio}, mobile-first UGC-style ad for TikTok/Instagram Reels. {SessionScriptLanguage} voiceover.{VariantClause}

Reference assets:
{AssetLines}

Overall style: authentic UGC creator selfie/handheld video, natural window light, real skin texture, slight handheld camera motion, mobile front/back camera field of view, conversational performance. Face and voice must change through each shot — shifting micro-expressions, natural pitch and stress, brief breaths. No held pose, no frozen face, no flat text-to-speech cadence.

Timeline:
{TimelineLines}

Continuity: same talent identity, same product appearance, same scene throughout. No face swap, no product drift, natural lip sync. Continuity is appearance and wardrobe, not a locked expression or a locked vocal pitch.{Video1Continuity}

Prohibited: product shape change, wrong colors, logo distortion, text gibberish, extra fingers, plastic skin, heavy HDR, studio lighting, beauty filter, held facial expression, monotone or text-to-speech delivery.{VoiceReplica}
```

| 槽 | 怎么填 |
|----|--------|
| `{SegmentDuration}` | 本段时长秒数（如 `12`）→ 写成 `12-second` |
| `{SessionRatio}` | 规格提问画幅原文 |
| `{SessionScriptLanguage}` | 口播语言（`Custom`→English） |
| `{VariantClause}` | 有 `ExecutionGoal` → ` VARIANT - {ExecutionGoal}.`；无则**整句省略**（含前面空格和句点） |
| `{AssetLines}` | 见下方资产行；只写已挂槽 |
| `{TimelineLines}` | 见下方 Timeline；只写本段各镜 |
| `{Video1Continuity}` | i≥2 → 空一行后追加 `Keep character appearance, wardrobe, and voice identity continuity with the referenced first-segment video <<<video_1>>>. Do not copy a frozen face or a flat vocal pitch.`；Video 1 **禁止**写 |
| `{VoiceReplica}` | i≥2 → 文末追加 `1:1 replica of only the voices of the characters in the video .The character must deliver all the Voiceover Narration correct, with natural intonation and stress, not monotone.`；Video 1 **禁止**写 |

---

## 资产行（有才写，`n` 按出现顺序从 1 递增）

首帧（有则写，禁止 first frame 字样）：

```text
- <<<image_n>>> : visual reference for opening look and framing. Use it for identity, wardrobe, and composition only — do not freeze the face or body in that still for the rest of the clip.
```

产品（必写）：

```text
- <<<image_n>>> : controls the [商品名称] — [商品核心外观特征、材质、颜色、Logo与不可变要素]. Do not alter shape, color, or logo.
```

角色（有则写）：

```text
- <<<image_n>>> : controls the talent — [年龄段/性别/外貌特征/发型/服装风格], natural skin, no beauty filter, authentic mobile selfie look. Use this image for the person only. Do not copy its background if a scene image is also attached.
```

场景（有则写）：

```text
- <<<image_n>>> : controls the scene — [室内/室外具体场景], [标志性背景家具或环境元素], natural balanced lighting. This image is the only environment source. Same room throughout.
```

身份 / 外观从角色图、`CharacterPromptBody` / `ProductBrief` 推断；环境只从场景图 / `ScenePromptBody` 推断。禁止发明与参考图冲突的外形。有场景图时禁止另造房间。

---

## Timeline（HARD — 由本段 extract 改写）

只写 **Video {i}** 的镜。按 extract 镜序，段内时间从 `0` 累加各镜 `Duration`。禁止发明与 extract 冲突的动作 / 口播 / 花字。

每镜一行：

```text
[开始-结束s]: [镜头景别 / 拍摄机位] [画面主体与动态动作描述]. Face/body: [该镜表情与肢体如何随时间变化]. Spoken voiceover: "[口播台词或留白]" — natural pitch, word stress, and brief breaths, not flat TTS. On-screen text: "[屏幕花字]"
```

| 段 | 来源 |
|----|------|
| `[开始-结束s]` | 段内累计，如 `0-3s` / `3-6s`。各行首尾相接，最后结束秒 = `{SegmentDuration}` |
| `[镜头景别 / 拍摄机位]` | extract 的 Shooting Style |
| `[画面主体与动态动作描述]` | extract 的 Action（可加主体词，但身份/环境仍以已挂图为准） |
| `Face/body` | extract 的 Expression。必须写成该镜内的变化（起 → 中 → 收），禁止整镜一个情绪词。若 extract 只有单点情绪，按同一情绪族补出变化，不要另造情绪 |
| `Spoken voiceover` | extract 的 Voiceover Narration；`N/A` → `""`。词数仍按分镜，但必须带自然语调，禁止匀速平念 |
| `On-screen text` | extract 的 On-Screen Text；允许烧进画面。`N/A` → `none` |

禁止再写「should not include subtitles」或「no burned-in subtitles」。

---

## 仍禁止

- 挂分镜表 / brief / Prompt 文本当生成参考
- 引用 Video 2…N 成片；i=1 引用任何 UGC 成片
- i≥2 漏 Video 1 的视频 URL 或漏 `<<<video_1>>>`
- 把参考视频传入成片
- 字面输出 `{{Product}}` / `{{Talent}}` / `{{Scene}}`（必须换成已绑定的 `<<<image_n>>>`）
- 整段粘 extract、空 Timeline、空占位
