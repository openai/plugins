# TVC ADS — 分镜与角色图 Prompt

分镜工具与返回形态已注册。按是否有参考视频选择下方工具，传纯文本输入和真实媒体 URL。不要把 YAML 当自由 prompt。
角色图 Prompt **只从有参考分镜返回的 `character_prompts` 逐字取**，禁止 agent 另写。禁止搜片，禁止调 `tvc_ads_search_keywords`。

| 用途 | 怎么拿 | 成功后读 |
|------|--------|----------|
| 分镜（有参考） | `tvc_ads_storyboard_with_ref` | `name` + `items[].content` + `voice_profile` + 可选 `character_prompts` |
| 分镜（无参考） | `tvc_ads_storyboard_no_ref` | `name` + `items[].content` + `voice_profile` |

`name` 必须是 `Storyboard Table`。`content` = English GFM 表（表头 + 分隔行 + 每镜一行）。缺分隔行 → 非法重试。
**HARD — 对话渲染**：同一 continuation 必须按 `script-table-format.md` 把每一表行转成分镜卡片贴进对话。**禁止**把 `|` 管道表贴进 Chat。禁止 code fence。卡片贴完后发 Host tools Continue/Revise。

---

## 1. 分镜（有参考）— `tvc_ads_storyboard_with_ref`

参考：参考视频 URL + 商品图 URL（主图在前）。走 `image_url(s)` / `video_url(s)`。**禁止传 `nodeIds`**。

输入：

```text
product_title:{ProductTitle}
product_description:{ProductDescription}
product_brand:{ProductBrand}
selling_point:{SellingPoint 或 (none)}
config_ratio:{SessionRatio}
config_duration:{SessionVideoDuration}
config_duration_range:{SessionVideoDurationRange}
user_language:English
Character Role: {CharacterRoleOrNone}
Visual Tone: {VisualToneOrNone}
Execution Goal: {ExecutionGoalOrNone}
```

成功：读 `items[].content`。读取顶层 `voice_profile` 并冻结为全片 `VoiceProfile`。`character_prompts` 非空且 `CharacterVisualPlan=run` → 同轮成角色图（Prompt **逐字**，禁止改写）。

**人物图生成 HARD**：正常非 Jump 的有参考模式中，只要 `character_prompts` 返回非空且 `CharacterVisualPlan=run`，就必须在本阶段同轮生成对应人物图。以下情况必须不生成：用户明确 Skip 角色或 Jump 越过该可选子产物（`CharacterVisualPlan=skip`）；`character_prompts` 为空数组；用户已 Provide 角色图（`CharacterVisualPlan=provided`）。不得让本条覆盖 Jump 已写入的子状态。
有参考却返回无法访问 → 非法；重试并在输入顶部说明参考已挂上。
run_prompt 返回 **不等于** 对话卡片，更 **不等于** 等待提问。本步未完成，必须进入 §4。

---

## 2. 分镜（无参考）— `tvc_ads_storyboard_no_ref`

参考：商品图 URL（主图在前）。走 `image_url(s)`，有才加。**禁止传 `nodeIds`**。

输入：同上（无参考视频）。`selling_point` / 意图字段同样写入。
成功：读 `items[].content`。读取顶层 `voice_profile` 并冻结为全片 `VoiceProfile`。忽略返回里的 `character_prompts`，不生成角色图。
run_prompt 返回 **不等于** 等待提问。本步未完成，必须进入 §4。

---

## 3. 成角色图（Prompt 来自 script）

仅：有参考、`character_prompts` 非空、`CharacterVisualPlan=run`。`CharacterPrompts[]` = 分镜返回数组，**逐字冻结**。禁止 agent 改写、补写、发明新角色。

- Prompt 不进 Chat。同轮 `generate_image`：`prompt` 逐字；若正文没有 `<<<image_n>>>`，按当前 URL 绑定追加 Reference assets；`model` = Image 表 **gpt image2** 行的 `model` 列原文；`aspectRatio="16:9"`；`title=Character {i}`；只挂产品主图 URL（及专用角色参考图 URL，有才加）。**禁止传 `nodeIds`**。**不要**挂分镜表。
- 风格对齐参考视频媒介（实拍就实拍，卡通就卡通）。
- 后续计划 Existing Character Prompts 用这份冻结列表，不得改写。
- **HARD**：`generate_image` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（PENDING/RUNNING 就继续查，不要停、不要等用户），记下素材 URL。并发多张时每个 `task_id` 都要轮询到终态。Apps widget 不能代替轮询。
- 角色图已发出、尚未终态 → 等结果，不要空结束。全部终态后进入 §4，与分镜卡片一并展示 + 推提问。

---

## 4. script 等待提问（HARD — 生成已返回后的同一 continuation 必做）

普通模式（含 Rollback 重做）在分镜 run_prompt **已经返回**、且该跑的角色图也 **已经 `get_task` 终态**（或不该跑角色图）的那一次 continuation，必须连续做完下面两步，**缺任一 = 本步失败 / 用户卡住**：

1. 按 `script-table-format.md` 贴对话分镜卡片。引导句 `Here is the storyboard table:`（重做则 `Here is the updated storyboard table:`）。可附状态句 `Your storyboard table is ready.` / `Your updated storyboard table is ready.`
2. Host tools Continue/Revise：
   - 有参考且有角色图：问句 = `Review the storyboard table and optional character sheets, then continue.`
   - 否则：问句 = `Review the storyboard table, then continue.`
   - 第 1 条 = 下一 enabled 主路径（有参考 → `Generate preview image`；无参考 → `Generate first frames`）；另给 `Revise` 出口。

然后**停住** = 不要同 continuation 进 `plan` / 开场视觉 / 成片。**停住不是「不要发提问」**。
只有本会话对这一稿成功过 Host tools 才算「script 等待提问仍有效」。
`不要叠新调用` 只适用于 run_prompt / 角色图 **尚未终态**；返回后贴卡片 + 提问是 mandatory continuation，不是叠生成。

**HARD — 等待上的越级**：用户下一句若点名更后产物（`directly generate the videos` / 直接出视频 / 跳过首帧 / 不要预览直接成片……）→ `Jump(T)`，当前 Continue/Revise **作废**。不要当成点了 `Generate first frames` / `Generate preview image`。Jump(`video`) 时 `Skip(opening_visual)`，静默 `plan` 只分段，立刻成片。

FastForward / Jump：贴卡片后立刻按目标推进，不发本等待提问；已发出的等待被越级句作废。

---

## 5. 声音描述质量规则

声音身份、台词格式、局部表演与混音层级的完整规范见 `voice-direction.md`。本阶段的核心是让分镜产出可直接执行的口播，而不是几个抽象形容词。

### Dialogue / Voice-over

- 每句对白或旁白都必须适配该镜头时长。普通旁白控制在约 1.9–2.3 English words per second；画面动作复杂、特写或需要突出 Foley 时降到约 1.4–1.8 words per second。
- Dialogue 单元格中使用明确的双层格式：`Voice-over (spoken words only): "..."; Delivery direction (not spoken): ...`。只有引号内文字允许发声，表演提示、时间说明和字段名不得被念出。
- 在表演提示中加入 1–2 个可执行动作，例如 `brief inhale`、`asymmetric pause`、`slight pitch lift`、`soften the middle phrase` 或 `calm landing on the final brand word`，不要只写 `natural`、`emotional` 或 `premium`。
- 相邻镜头避免等长句、等间隔停顿、相同句尾和相同重音；通过呼吸句群、长短句、逗号、句号和自然留白形成节奏变化。
- 口播和画面速度服从镜头功能，且必须使用功能分档而不是全片统一慢速：钩子、转场、反应插镜和简单信息镜头应紧凑，主变化在首秒内出现；人物交互、手部动作、功能演示和连续表演保持自然实时速度与 TVC 剪辑能量，通常以 1.5–3 秒完成一个明确动作；只有商品包装、质地、微距材质或最终英雄镜头在可读细节确需停留时才允许 2–4 秒的克制放慢。
- 不要强行每镜都有旁白。画面静止、质感特写或关键动作需要留白时使用 `None`。
- 同一叙述者 / 同一角色在所有相关镜头中保持稳定的身份、语气和情绪基调。完整 VoiceProfile 与跨片段复用规则见 `voice-direction.md`。

### Sound Design

- 明确写出声音的物理来源，并与可见动作同步，例如 `soft lid click`、`fingertip contact on cream`、`quiet powder fall`、`fabric movement`、`container handling` 或 `subtle room tone`。
- 对重要声音说明相对强弱或混音关系，例如 `foreground tactile foley, kept below the voice-over`。
- 只生成真实环境音、动作 Foley 和自然空间底噪；所有声音必须有可见或强逻辑关联的物理来源，并与动作同步。永远不生成 BGM、配乐、音乐床、旋律、和声、节拍、音调持续层或电子情绪音效。
- 适当使用静音或近似静音，为产品揭示、质地特写和最终品牌句制造对比。
- 避免没有物理来源的 whoosh、低频音乐性轰鸣、持续音床、装饰性闪光音和魔法音效；口播出现时让环境音与 Foley 退到人声之后。
