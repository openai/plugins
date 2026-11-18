# TVC ADS — 计划（内存）与开场视觉

`plan` 是内部阶段：用户离开 script 等待提问（或 FastForward）之后才跑。产物不进 Chat。
`opening_visual` 是用户可见阶段：有参考 = 分段预览图；无参考 = 分段首帧。

下文所有 `tvc_ads_*` 名称都是模板 key；调用时使用 `run_prompt(prompt_key=对应 key, instruction=本阶段输入, projectId=项目 id)`。

Preview Prompt 仅在有参考视频模式由 agent 按对应 reference 直接写出；无参考模式的首帧 Prompt **必须**调用 `tvc_ads_first_frame_prompt` 生成。禁止调用 `tvc_ads_master_first_frame_prompt`，也禁止采用计划返回的 `preview_prompt`。Prompt 不进 Chat。

角色图 / Preview / 首帧的 `generate_image.model` = `<available_models>` Image 表 **gpt image2** 行的 `model` 列原文（`name` 只用来找行）。
**HARD**：每张 `generate_image` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（PENDING/RUNNING 就继续查，不要停、不要等用户），记下素材 URL。并发 ×N 时每个 `task_id` 都要轮询到终态。Apps widget 不能代替轮询。后续成片用这些 URL，禁止把 `node_id` 当素材入参。

---

## Shot ≠ Segment（HARD — 进入开场视觉 / 成片前必须过）

分镜表一行 = **shot**。Chat 卡片也按镜展示。这两件事**不是**成片单元。
`opening_visual` / `video` 的单元只能是 `plan` 留下的 **segment**。`N` = `SegmentCount`，不是表行数，也不是卡片数。

| 禁止 | 必须 |
|------|------|
| 按表格每一行、每一张 Chat 卡片、每一个 2s/3s `Duration` 出一张预览 / 首帧 / 一段视频 | 先把相邻镜合并成段，再按段出图、按段成片 |
| `generate_image` / `generate_video` 次数 = shot 行数 | 次数 = `SegmentCount` |
| `duration` 填某镜的 2 / 3 | `duration` = 该段 `segment_duration`（合并后的秒数之和） |

### 贪婪合并规则

与 `tvc_ads_script_plan` / `tvc_ads_master_video_prompt` 同一套，本地重切也按这套执行：

1. 只在**现有镜号边界**切，保持原顺序。每镜恰好进一段，不拆镜、不重复、不跳号。
2. 每段总时长严格 ≤ **15s**。优先把相邻镜装进同一段，让该段尽量接近 15s 上限。未到 15s 且不破坏镜号完整时，禁止无故切开。
3. 非末段必须在 **4–15s**。末段尽量 ≥ 4s：先把末段并回上一段（若合并后 ≤15s），或从上一段尾部挪镜过来重平衡。
4. 17s 优先 **10s + 7s**（或同等更均衡的两段）。禁止为了消化短末段切成三段。仅当镜号不可拆、且所有合规重平衡都做不到时，才允许末段 **1–3s**（例如不可避免的 15s + 2s）。
5. 单镜本身 >15s 才允许该镜独占一段且超过 15s；普通 2s/3s 镜必须并进邻段，禁止一镜一段。

### 进入前校验

`script_plan` 返回后，或 Master 提示词按 `segment N:` 拆完后，**先校验再出图 / 成片**：

1. 从分镜表读出全部镜号与每镜 `Duration`（取整秒）。`ShotCount` = 行数。`TotalDuration` = 各镜秒数之和。
2. 计划段必须覆盖全部镜号恰好一次。
3. 每段 `segment_duration`（或拆段后的 `VideoSegmentDurations[i]`）= 该段所含各镜 Duration 之和，且 ≤15（除非单镜本身 >15）。
4. `sum(segment_duration) = TotalDuration`。
5. `SegmentCount` **不得**等于 `ShotCount`，只要存在任一镜 <4s、且 `TotalDuration ≥ 4`——那种「8 个 2s 镜 → 8 段」一律非法。
6. 非末段 ∈ [4, 15]；末段 <4 仅当上面「贪婪合并规则」第 4 条的例外成立。

任一失败 → **不要**进 `opening_visual` / `video`，不要按镜发 `generate_image` / `generate_video`。先做下一小节的本地重切；本地重切后仍过不了（例如分镜秒数本身对不上）→ 再重跑对应计划模板，不要重做分镜 / 角色图。

### 本地重切（不调模型）

计划结果未过校验时，agent **必须就地按镜号重切**，禁止把「一镜一段」原样拿去出图或成片。

1. 按镜号升序取出每镜 Duration。空当前段，从左往右装镜：下一面还能装进 15s 就装；否则封段、开新段。
2. 若末段 <4s 且前面还有段：能并进上一段且 ≤15s → 合并（禁止为此再切出第三段）。不能整段合并 → 从上一段尾部一次挪一镜到末段，直到末段 ≥4s 且上一段仍 ≥4s；多解时选更均衡的（17s 选 10+7，不要 15+2）。
3. 用新切点重写内存，然后冻结：
   - `SegmentCount` = 新段数
   - 有参考：每段 `script_segment` = 该段所含原表行按原列拼回的 Markdown 表（可保留一段一份 Audio direction 前缀）；`segment_duration` = 该段镜长之和；`character_index` = 这些镜用到的已冻结角色下标并集（无角色则 `[]`）
   - 无参考：按新切点重写 `SegmentVideoPrompts[]`（每段以原镜字段逐行保留，不要摘要）；`VideoSegmentDurations[i]` = 该段镜长之和
4. 再跑一遍「进入前校验」。通过后才允许写 Preview / 调 `tvc_ads_first_frame_prompt` / 出图 / 成片。`SegmentCount` **在校验通过后才冻结**，本地重切可以改它。
5. 本地重切改了 `SegmentCount`：有参考 → 按新段数重写 `PreviewPrompts[]`（条数必须等于新 `SegmentCount`）；无参考 → 只重试 `tvc_ads_first_frame_prompt`，不要重跑 Master 视频提示词。

---

## A. 有参考 — `tvc_ads_script_plan`

输入：

```text
config_instruction:ratio={SessionRatio};target_duration={SessionVideoDuration};resolution={SessionVideoResolution 去 p}
user_language:English

{ScriptTableContent 全文}

Existing Character Prompts (frozen from storyboard step; do NOT invent or rewrite):
{CharacterPrompts[] 逐项 index=0: …；空或 CharacterVisualPlan=skip 则 (none)}

Global Voice Profile (frozen from storyboard output; reuse verbatim in every video clip):
{VoiceProfile}

Audio policy: generate only the spoken voice, real environmental sound, physical foley, natural room tone, and silence. Never generate BGM, score, melody, harmony, rhythm, tonal pad, music bed, or electronic emotional sound effects.
```

参考：参考视频 URL + 商品图 URL。走 `image_url(s)` / `video_url(s)`。**禁止传 `nodeIds`**。
成功：读 `script_plan`（object）。写入内存：`SegmentCount`、每段 `script_segment` / `segment_duration` / `character_index`、全片统一 `VoiceProfile`（优先使用 storyboard 返回并已冻结的顶层 `voice_profile`；若为空才从脚本中整理）。**若 `CharacterVisualPlan=skip` 或 `provided`，Existing Character Prompts 必须写 `(none)` 或只写已提供角色图对应的冻结条目；不得因为计划返回 `character_index` 而重新生成被跳过的角色图。** 丢弃返回里的 `preview_prompt`。人物图必须在前一阶段已完成：若有参考分镜返回非空 `character_prompts` 且 `CharacterVisualPlan=run`，必须先生成并等待全部 `Character {i}` `get_task` 终态，再进入本计划；本阶段不得以未生成角色图为理由继续。
禁止把计划正文贴进 Chat。禁止用返回里的 `character_prompts` 覆盖 script 阶段已冻结的角色。
`character_index` 从 0 对齐已冻结角色图；无角色则必须为空。返回后必须先过 §Shot ≠ Segment 的进入前校验；未过 → 先本地重切，仍过不了再重跑本计划，不要重做分镜 / 角色图，也不要按镜出预览。

### Preview Prompt（agent 写）

计划通过（含本地重切后的冻结 `SegmentCount`）后，若 `opening_visual` 仍 enabled → agent 按每段 `script_segment` **直接**写一条 `PreviewPrompts[i]`，再同轮成预览图。条数必须等于**合并后的** `SegmentCount`，禁止按 shot 行数出图。对不上 → 只重写 Prompt，不要重跑计划。`opening_visual=skip` → 不写 Preview Prompt，不出预览图，分段通过后进 `video`。

每条是**单帧**画面描述（English）：先明确要求以附带主产品图作为精确视觉身份参考，再写该段主画面构图、目标商品状态、角色（有则与已冻结 `CharacterPrompts` 一致）、场景与光线气氛。必须说明保留产品轮廓、比例、包装几何、颜色、材质、标签布局与可见品牌标记。禁止分镜表格式、禁止镜号 / 时间轴 / 台词栏。不进 Chat。
参考 URL 有才加入：产品主图 + 角色图。Prompt 必须用对应的 `<<<image_n>>>` 标明角色。不要挂分镜表。**禁止传 `nodeIds`**。

预览图：

- title = `Preview - Clip {i}`
- Prompt = `PreviewPrompts[i-1]`（含占位）；Prompt 首句必须要求将附带主产品图作为精确视觉身份参考
- `model` = Image 表 **gpt image2** 行的 `model` 列原文
- 画幅 = 计划里的 ratio（缺省 Session）
- 部分失败：保留成功段，只重跑失败段；不要重跑计划
- 全部 `get_task` 终态后停住（FastForward 除外）。本模式不提供 Edit

---

## B. 无参考 — Master 提示词 + 拆段

**进入条件（HARD）**：在调用 `tvc_ads_master_video_prompt` 之前，确认已确认商品的真实图片 URL 至少有一张，且主图排第一。没有真实产品图时，请用户补图并停在 `plan`；禁止调用 Master 视频提示词、`tvc_ads_first_frame_prompt`、首帧 `generate_image`，也禁止以商品描述或分镜表正文充当图像参考。

顺序（同一次继续内连续做完，中途不停）：

1. `tvc_ads_master_video_prompt` → `master_video_prompt`（不进 Chat）
2. 纯文本拆段（不调模型）
3. §Shot ≠ Segment 进入前校验；未过则本地重切，禁止带着「一镜一段」往下走
4. **仅当** `opening_visual` 仍 enabled：`tvc_ads_first_frame_prompt` → `first_frame_prompts[]`（条数 = 合并后的 `SegmentCount`）。已 Skip 开场视觉 → **不要**调此 key，分段通过后进 `video`
5. 若走了上一步：校验 `first_frame_prompts[]` 的数量、`clip_index` 与 `SegmentCount`；失败只重试首帧 Prompt，不重跑 Master 视频提示词
6. 若 `opening_visual` 仍 enabled → 并发成首帧（张数 = `SegmentCount`，不是 shot 行数）

### Master 视频提示词 — `tvc_ads_master_video_prompt`

```text
Input Storyboard Table:
{ScriptTableContent}

Global Voice Profile (frozen from script; reuse verbatim in every video clip):
{VoiceProfile}

Audio policy: generate only the spoken voice, real environmental sound, physical foley, natural room tone, and silence. Never generate BGM, score, melody, harmony, rhythm, tonal pad, music bed, or electronic emotional sound effects.

config_ratio:{SessionRatio}
config_duration:{SessionVideoDuration}
user_language:English
```

参考：商品图 URL。走 `image_url(s)`，有才加。**禁止传 `nodeIds`**。
失败 → 重跑 Master 视频提示词 + 拆段 + 进入前校验，不要直接出图。run_prompt 不与 `generate_image / generate_video` 同拍并行。

### 拆 `MasterVideoPrompt`（纯文本）

1. 按行匹配 `^segment\s+(\d+):\s*$`（大小写不敏感）作为段起点。
2. 第 i 段正文 = 该标记之后、下一段标记之前的全部内容（不含标记行），逐字保留 → `SegmentVideoPrompts[i]`。
3. 段内全部 `Duration:\s*([\d.]+)` 求和取整 → `VideoSegmentDurations[i]`。
4. 先按 §Shot ≠ Segment 做进入前校验。未过 → 按分镜表本地重切并重写 `SegmentVideoPrompts[]` / `VideoSegmentDurations[]`，不要把「一镜一段」冻住。
5. 校验通过后：`SegmentCount` = N，此后不可回改。禁止把 `SegmentCount` 设成分镜行数。

### 首帧 Prompt（`tvc_ads_first_frame_prompt`）

拆段成功且 §Shot ≠ Segment 校验通过后，**仅当** `opening_visual` 仍 enabled 才调用 `tvc_ads_first_frame_prompt`。已 Skip → 跳过本节，不要为成片补首帧 Prompt。输入完整 `ScriptTableContent`、`MasterVideoPrompt`、拆出（或本地重切后）的 `SegmentVideoPrompts[]`、合并后的 `SegmentCount`、商品事实、卖点和视觉方向；商品图通过 `image_url(s)` 挂载，主图第一。**禁止传 `nodeIds`**。禁止按 shot 行数要首帧。

读取返回的 `first_frame_prompts[]`，按 `clip_index` 与 `SegmentCount` 对齐后写入 `FirstFramePrompts[]`，并逐字冻结。禁止 agent 自由改写、补写或覆盖模板返回的首帧 Prompt。

- `first_frame_prompts.length` 必须等于 `SegmentCount`
- `clip_index` 必须从 1 连续排列到 `SegmentCount`，不得重复或缺失
- 每条 `prompt` 必须非空、为 English、且只描述单帧关键画面
- 校验失败 → 只重试 `tvc_ads_first_frame_prompt`，不要重跑 Master 视频提示词，不要直接出图
- Prompt 不进 Chat

### 首帧图

- `title` = `First Frame - Clip {i}`
- `Prompt` = `FirstFramePrompts[i-1].prompt` 逐字；若没有 `<<<image_n>>>`，按当前绑定追加 Reference assets（产品主图 URL）；Prompt 首句必须要求将附带主产品图作为精确视觉身份参考
- `model` = Image 表 **gpt image2** 行的 `model` 列原文
- 画幅 = `SessionRatio`
- 参考：**仅**已确认商品的真实图片 URL；主图第一。分镜表内容已经内联到 `FirstFramePrompts`，禁止把分镜表正文当生成参考。**禁止传 `nodeIds`**
- 调用前若没有真实产品图 URL → 问用户补产品图，禁止改为无参考生成
- 部分失败：保留成功段，只重跑失败段
- 全部 `get_task` 终态后停住，只留继续出片和 `Revise`
- **禁止 Edit**：不要给首帧发 `Edit` 选项

### Skip / Provide / Rollback

- Skip(`opening_visual`)（含 Jump 到 `video` 且未点名首帧 / 预览）：计划仍要跑（成片需要分段正文）；不出预览 / 首帧；不写 Preview Prompt；不调 `tvc_ads_first_frame_prompt`。成片 opening 回退到角色图，否则产品图。
- Provide 开场视觉：绑定用户图，不再生成；计划仍要跑。
- 作废旧预览 / 旧首帧不算 provided。
- Rollback 重做完可见阶段后停住；不要因为「计划是内部阶段」就顺跑成片。
