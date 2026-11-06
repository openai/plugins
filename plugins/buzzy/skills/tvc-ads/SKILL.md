---
name: tvc-ads
description: "Always use this skill to make a TVC / brand commercial from a product link, product image, or product description. Must trigger for /tvc-ads, tvc-ads, TVC ad, brand commercial, cinematic product film, brand ad, film commercial, or when the user drops a product page and asks for a TVC or brand film. Also use when a tvc-ads run is already in progress (Confirmed Product Info, selling-point confirm, specs, storyboard cards, character sheets, preview / first frames, clips, BGM merge) or the user skips a step, supplies an asset, jumps ahead, or revises an earlier step without restarting. Even a vague \"make a TVC\" or \"help me make a brand ad\" must start this skill. First-round with-questions (default) asks 1 content-direction question; no-questions starts the pipeline."
source: "buzzy"
risk: safe
scope: mcp
allowed-tools: |
  Buzzy MCP tools
  - create_project
  - parse_product_info
  - display_product_info
  - run_prompt
  - generate_image
  - generate_video
  - get_task
  - merge_videos

  Host tools — not part of this MCP server
  - AskQuestion
  - ask_question
  - AskUserQuestion
---

# TVC Ads Orchestrator

本链自包含。查阅本 skill 文件只用完整前缀 `skills/tvc-ads/reference/`。
**怎么调平台能力、填哪些参数，对照各 tool 自己的声明**；本文件只写目的、产物和硬底线。

**HARD — allowed-tools 分类**：`Buzzy MCP tools` 是本 MCP 服务注册的平台 tool，经 Buzzy MCP `tools/call`。`Host tools — not part of this MCP server` 是宿主内置提问 tool，**不是** Buzzy MCP tool，也不走 `load_workflow` / ExecuteTools。Cursor 用 `AskQuestion`，Claude 用 `AskUserQuestion` / `ask_question`，Codex 用同类。选择题必须调 Host tools 里当前可用的那个，禁止因为「不在 Buzzy MCP tools 列表里」就改成编号纯文本。
**HARD — create_project**：进入任何需要 `projectId` / `project_id` 的 Buzzy MCP tool 之前，必须先调 `create_project` 拿到真实 id。本会话只创建一次，后续全程复用。workflow tool（`parse_product_info` / `display_product_info` / run_prompt / `merge_videos`）传 `projectId`；`generate_image` / `generate_video` 传 `project_id`。禁止编造 id，禁止省略，禁止因为 generate_image / generate_video 写了「可自动建项目」就跳过。`create_project` 的入参是 `name`（可读项目名），不要把 catalog 的 `name` 或 `workflow` 抄过来。Host tools 开场问询那一拍仍禁止同拍调 `create_project`；问询完成（或 `IntentQuestions=false`）后、进 `product` 的第一拍若还没有 id，必须先 `create_project`。Jump / FastForward 到更后阶段同此：还没有 id 就先创建，再调带项目字段的 tool。

**HARD — 宿主提问**：等人选择或确认时（**卖点分析、Apps 商品控件确认除外**），必须对 Host tools 里当前可用名字真调用一次。选项只进提问 tool 的 `options`。禁止用 `1.` `2.` `3.` 编号列表、bullet、`Recommended:` 前缀段落作为用户可见选项——那样写 = 本步失败，必须立刻改成真调用。assistant 正文最多一句问句或状态句，**不要复述选项**。不要自己造第 4 个 `Other` 选项：Cursor `AskQuestion` 自带 Other 自由输入。仅当 `tools/list` 里 `AskQuestion` / `ask_question` / `AskUserQuestion` 三个名字都没有时，才允许编号列表，并写明本宿主没有选择框。Cursor 有 `AskQuestion`，禁止走这条。媒体产物就绪只用 assistant 正文状态句。伪调用或编号列表都算没发出提问。
**例外 — 商品确认**：`parse_product_info` 打开编辑控件。有产品页 URL 则传 `productLink`；没有则**不要编造链接、不要传 `productLink`**，打开空表。返回值（即使带 Title / Description / Images）只表示控件已打开，**不是**确认。然后**停住**，等用户确认。确认信号（任一即可）：消息含 `Confirmed Product Info`；或用户明确确认/继续该商品（`Confirm` / `Continue` / `looks good` / 确认 / 继续）。在此之前禁止 `display_product_info`，禁止 Host tools 问要不要继续。无 iframe 宿主才用 Host tools 收集标题/描述/图。
**例外 — 卖点分析**：不走 Host tools。run_prompt 返回后按 `selling-analysis-prompt.md` 贴三段：固定引导句 `Here are the product selling points:` + `content` 原文 markdown + 固定确认句 `Confirm to continue, or tell me what you'd like to change.`，然后停住等用户下一条自由回复。禁止只贴正文、不说明这是商品卖点。用户回复 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续 = **已确认**，必须进入 `info_card`。
**例外 — run_prompt `content`**：卖点正文必须原文贴进对话（禁止 code fence），不受「正文最多一句」限制。分镜 `content` 是 GFM 管道表；Chat **禁止**贴 `|` 管道表，必须按 `script-table-format.md` 转成分镜卡片。卡片贴完后仍发 Host tools Continue/Revise。

| 何时读 | 文件 |
|--------|------|
| 开场组题（`with-questions` 时恰好 1 题） | `intent-questions.md` |
| 下游缺输入时怎么组槽 | `slot-adaptation.md` |
| 任意状态句 / 提问引导 | 本文件 §双通道文案 |
| 填 `generate_image` / `generate_video` 参数 | 本文件 §运行时填参 |
| 商品确认后的卖点分析 | `selling-analysis-prompt.md` |
| 用户自带参考视频时 | 本文件 §`ref_video`（无单独 reference；禁止搜片） |
| 分镜 / 角色图 / 对话卡片 | `storyboard-prompts.md` + `script-table-format.md` |
| 脚本计划 / Master 提示词 / 开场视觉 / 首帧 | `plan-and-opening.md` |
| 声音身份、口播表演、混音层级与验收 | `voice-direction.md` |
| 分段成片 / BGM 合成 | `video-generate-prompt.md` |

`run_prompt` 可用的 `prompt_key`：`tvc_ads_selling_analysis` / `tvc_ads_storyboard_with_ref` / `tvc_ads_script_plan` / `tvc_ads_storyboard_no_ref` / `tvc_ads_master_video_prompt` / `tvc_ads_first_frame_prompt`。按当前阶段选择 key。下文提到调用模板 key 时，实际工具均为 `run_prompt(prompt_key=该 key, instruction=本阶段输入, projectId=项目 id)`。
Preview Prompt **由 agent 按对应 reference 直接写出**，禁止再调 run_prompt（或其它单独 tool）获取。无参考模式的首帧 Prompt **必须**调用 `tvc_ads_first_frame_prompt` 生成，禁止 agent 自由改写；角色图 Prompt **只从 script 步**（有参考分镜返回的 `character_prompts`）逐字取，禁止 agent 另写、禁止再调单独 tool 获取。禁止短路径、读其它 skill、把 YAML 当自由 prompt。禁止调用 `tvc_ads_search_keywords` / `tvc_ads_master_first_frame_prompt`。禁止搜片。

用户可见文案 **固定 English**。分镜表、卖点正文、规格提问、方向选择、口播单元格一律 English。run_prompt 的卖点 `content` **必须**作为 markdown 贴进对话（禁止只写一句 status、禁止 code fence）。分镜 `content` 是 GFM 管道表；对话必须转成分镜卡片，**禁止**把该表贴进 Chat。
参考素材**一律走 URL 字段**（`image_url` / `image_urls` / `video_url` / `video_urls`，以各 tool 声明为准），适用于 `generate_image` / `generate_video` / run_prompt / `merge_videos`。**禁止传 `nodeIds`**。卖点正文 / 分镜正文 / Prompt 文本不是生成参考；生成参考用产品主图 URL、角色图 URL、开场视觉 URL、用户 Provide 的媒体 URL。
角色图 / Preview / 首帧的 `generate_image.model` = `<available_models>` Image 表 **gpt image2** 行的 `model` 列原文（`name` 只用来找行；禁止把 `gpt image2` 别名、视频行、其它图片行写入）。
成片的 `generate_video.model` = `<available_models>` Video 表 **seedance-2.0-fast** 行的 `model` 列原文（`name` 只用来找行；禁止把 `seedance-2.0-fast` 简称、图片行、其它视频行写入）。填参细则见 §运行时填参。
产物 `title` **禁止方括号**。统一用无括号名：确认后的商品名、`Selling Point Analysis`、`Storyboard Table`、`Character {i}`、`Preview - Clip {i}`、`First Frame - Clip {i}`、`TVC Clip {i}`。

**HARD — generate_image / generate_video 阻塞轮询**：`generate_image` / `generate_video` 只返回 `task_id`，**不算完成**。同一 continuation 必须立刻反复调用 `get_task(task_id)`，直到终态：`TASK_STATE_PENDING` / `TASK_STATE_RUNNING` → 继续 `get_task`（禁止停住、禁止等用户下一句、禁止只写「生成中」就结束、禁止发下一阶段提问）；`TASK_STATE_SUCCEEDED` → 记下返回里的**素材 URL**（`url` / `image_url` / `video_url` 以返回为准），本段才算完成；失败态 → 说明失败，禁止当成功、禁止再叠一次 generate_image / generate_video。并发提交的多个 `task_id` 必须全部轮询到终态后才能 Advance。Apps widget 只展示进度，**不能**代替 `get_task`。禁止因为「控件会自己轮询」而跳过。后续 `generate_image` / `generate_video` / run_prompt / `merge_videos` 都用这些 URL，**禁止**把 `node_id` 当素材入参。

---

## 运行时填参（HARD）

本链没有 generic-agent system prompt。调平台 tool 时按下表填，**禁止发明**当前 tool schema 没有的字段。schema 有的必填项缺了就按本表补，不要空着让平台猜。

### 项目

| 调用 | 怎么填 |
|------|--------|
| `create_project` | `{ "name": "<短项目名>" }`。本链只调一次，记下返回的 id |
| `parse_product_info` / `display_product_info` / run_prompt / `merge_videos` | 必传 `projectId` = 该 id |
| `generate_image` / `generate_video` | 必传 `project_id` = 该 id。加载本 skill 后禁止省略、禁止靠自动建项目 |

还没有 id 就先 `create_project`，不要先调上表其它 tool。

### 模型

| 调用 | 怎么填 `model` |
|------|----------------|
| `generate_image`（角色 / Preview / 首帧） | Image 表 **gpt image2** 行的 `model` 列原文 |
| `generate_video`（成片） | Video 表 **seedance-2.0-fast** 行的 `model` 列原文 |

`name` 只用来找行。禁止把别名、错表、其它行写进 `model`。

### 画幅 / 分辨率（成片）

成片读 Video 表 **seedance-2.0-fast** 行：

| 字段 | 怎么填 |
|------|--------|
| `aspectRatio` | `SessionRatio` 若在该行 `ratios` 里 → 原样用。`ratios=fixed` → **整项省略**。不在表里 → 改用该行第一个合法 token；无法唯一确定则 Host tools 再问一次。禁止把非法 token 传出去 |
| `resolution` | `SessionVideoResolution` 若在该行 `resolutions` 里 → 原样用（`480` / `480p` 等照抄）。`resolutions` 为 `-` / 空 → **整项省略**。不在表里 → 改用该行第一个合法 token；无法唯一确定则 Host tools 再问一次。禁止写死 `720p` / `1080p` |
| `duration` | **本段** `segment_duration`（plan 合并后的段长），不是 info_card 的档位 token，也不是分镜某一行的 2s/3s |

规格写入 Session 后，后续 Preview / 首帧 / 成片**静默继承**仍合法的 `SessionRatio` / `SessionVideoResolution`；用户本句写了新值才改。角色图的 `aspectRatio` 仍固定 `16:9`，不受本表影响。

**两层不要混**：上表只约束 `generate_video` 入参。info_card 的画幅 / 分辨率候选项是冻结字面量（见 §info_card），**禁止**用本表、`<available_models>` 的 `ratios` / `resolutions`、`ratios=fixed` 或缺表去裁剪、省略或改写规格题。

### 媒体绑定

按 tool 分流，**禁止发明当前 schema 没有的字段**：

| 调用 | 怎么挂素材 |
|------|------------|
| `generate_image` / `generate_video` / run_prompt / `merge_videos` | **只传 URL 字段**（声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`）。图进 image_*，视频进 video_*。**禁止传 `nodeIds`** |
| `display_product_info.images` | 确认消息里的 `Main Image:` / `Images:` URL |

这些 URL 只许用已有真实地址，禁止编造、禁止为凑槽复制同一条：

- 商品图：确认消息 `Main Image:` / `Images:`，或 `display_product_info` 返回的图 URL
- 用户 Provide：用户消息 / 上传给出的图、视频 URL
- 本链生成：`get_task` 成功后的素材 URL

prompt 正文禁止写 HTTPS / `@Image` / `@Video`。

### 占位符

prompt 正文只用 `<<<image_n>>>` / `<<<video_n>>>`：小写、从 `1` 起，与 `image_url(s)` / `video_url(s)` 顺序一一对应。每个占位必须写清角色。冻结模板 Prompt（如 `character_prompts` / `first_frame_prompts`）若没有占位，调用前按当前绑定**追加**一段 Reference assets，不要改写模板正文。历史里若烂成 `<<>>`，按当前绑定重写成完整占位后再调用。禁止空占位。

### 串行

run_prompt **禁止**与 `generate_image` / `generate_video` 同拍并行。该跑的角色图、开场视觉 ×N、分段成片 1…N 仍按本文件 §并行。

### 含糊 / 纯确认

**只**适用于已发出且仍有效的 **Host tools** 提问：`nice` / 无可执行新指令 → 重发同一提问，不要 Advance。
**不适用**于卖点三段、也不适用于商品控件确认。这两处 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续 = **已确认**，必须 Advance。

---

## 为什么要灵活

用户不会只走一条固定生产线。他们可能跳过任意中间产物、自带任意素材、从任意点直奔更后的目标、中途改主意、或对任意前序不满意。本 skill 用**阶段图 + 五个算子**处理这些情况；下面的说法只是算子的实例，**不是**封闭清单。遇到未写出的说法，先归到某个算子，再往下走，不要因为「没写过这个例子」而卡住。

**HARD — 越级要产物（通用）**：停在任一用户可见等待上（分镜卡片、卖点三段、规格题、开场视觉提问、配乐闸门……），或某阶段刚完成时，用户本句要的若是**更后阶段的产物**，一律 `Jump(T)`，**不是**确认当前主选项。路上没被点名的可选可见全部 `Skip`；内部阶段（`plan`）静默跑；硬前置仍要有。禁止因为当前选项写着 `Generate first frames` / `Generate preview image` / `Continue`，就把「直接出视频」当成先出首帧再出片。当前等待作废，同轮 Advance 到 T。

实例（非封闭，按同一条规则推）：script 后 `directly generate the videos` / 「直接出视频」→ `T=video`，`Skip(opening_visual)`，静默 `plan`（只要分段，不写 Preview、不调 `tvc_ads_first_frame_prompt`、不成首帧），立刻成片；卖点后「先出分镜」→ `T=script`；开场视觉后「跳过合成只要分段」→ `Skip(merge)`。没写过的同义句同样归 Jump / Skip，不要另写例外。

有参考与无参考不再拆成两套阶段名。`ref_video` 是否 **provided** 只改变 **script / plan / opening_visual** 的适配模式。默认无参考。

---

## 阶段图

默认顺序（只执行 **enabled** 的阶段）：

```text
intent → product → selling_analysis → ref_video → info_card → script → plan → opening_visual → video → merge
```

| 阶段 | 默认 | 用户可见产物 | 说明 |
|------|------|--------------|------|
| `intent` | `with-questions` 则跑（恰好 1 题）；`no-questions` 则 skip | 无 | 指令式触发，见 §开场意图。恰好 1 题 = 广告视频内容方向，恰好 3 个按指令现写的选项 |
| `product` | 必跑 | 商品卡 / 确认后的商品展示 | 三路互斥入口，见 §阶段目的 |
| `selling_analysis` | 必跑 | 对话中的卖点 markdown（带引导 / 确认句） | 商品确认后 run_prompt，按 `selling-analysis-prompt.md` 贴三段并停住；用户确认后 `content` 全文 = 下游 `SellingPoint` |
| `ref_video` | **skip** | 用户自带参考视频 | 可选；默认 skip；**禁止搜片**；Provide 才绑定 |
| `info_card` | 规格未齐则跑 | 规格提问 | 时长 / 画幅 / 分辨率（无 language、无卖点字段） |
| `script` | 必有（生成或自供） | 分镜卡片；有参考时可选角色图 | 成片前必须有一份可用 script。角色**不是**独立阶段 |
| `plan` | script 之后、用户继续后 | 无（纯内存） | 把分镜 **shot 合并成 segment**（≤15s，短镜必须并段）。有参考 = 脚本计划 + agent 写 Preview Prompt；无参考 = Master 视频提示词 + 拆段 + 调用 `tvc_ads_first_frame_prompt` 生成首帧 Prompt。未过合并校验则本地重切 |
| `opening_visual` | run | 有参考 = 分段预览图；无参考 = 分段首帧 | 可选。张数 = `SegmentCount`，不是 shot 行数。角色图若在 script 已出，本阶段不再出角色。**不提供 Edit** |
| `video` | 必跑才能成片 | 分段成片 | 按合并后的段出片，禁止一镜一段。不要把用户参考片当成片 |
| `merge` | 有分段成片则跑 | 成片（原生人声与真实环境音，可选叠加配乐） | 合成前先问是否加配乐，按选择合成；N=1 仍可配乐 |

每阶段状态：`pending` | `run` | `skip` | `provided` | `done` | `invalidated`。
**enabled** = 不是 `skip`，且（`pending`/`run`/`invalidated` 需要执行，或 `provided` 只需绑定不再生成）。
角色图不是独立阶段，另维护 `CharacterVisualPlan = run | skip | provided`：正常有参考模式初始为 `run`；用户 Skip 角色或 Jump 越过 script 且未点名保留角色图时设为 `skip`；用户 Provide 角色图时设为 `provided`。只有 `CharacterVisualPlan=run` 才可按 `character_prompts` 生成角色图。
`video` 另维护两个声音状态：`Clip1Status` 与 `Clip1AudioReference`。`Clip1Status` 必须先到 `done`，后续 Clip 2…N 才能启动；`Clip1AudioReference` 优先保存平台实际返回的独立旁白音频 / 声音参考资产（URL）。若能力声明明确没有独立音频参考槽，则立即写入 `fallback: VoiceProfile + Clip 1 matching instruction`，不得无限等待，也不把 Clip 1 视频 URL 冒充音频参考。只有平台已声明支持且资产处于绑定处理中时，才允许等待绑定结果。
`ref_video` 开场默认 **`skip`**。用户自带视频则 Provide。禁止把默认 skip 理解成还要再问搜片卡。**继续禁止搜片。**

Jump 分类直接读上表：说明里写「可选」的是可选可见；写「无 / 纯内存 / 内部」的是内部；卖点分析等待 / 规格提问是闸门。`intent` 在 `IntentQuestions=true` 时必须先问完，不是 Jump 可跳过闸门。不要再为某条跳转另写规则。

**硬底线**（不能整链跳过）：必须有商品身份（链接 / 图 / 描述之一）；要出视频必须有 script（生成或自供）以及至少一块视觉参考（开场视觉、角色图或产品图之一）。其它阶段都可以 skip 或 provided。

`IntentQuestions`：仅从本任务**首轮**字面量读取。出现 `no-questions` → `false`（跳过问询）；出现 `with-questions` 或两者都未出现 → `true`（默认问 1 题）。首轮冻结，禁止后续轮次改写。`false` → `intent = skip`，`IntentDone=true`，同轮进 `product`。卖点分析 / 规格提问仍照常。

---

## 五个算子（HARD — 任意阶段、任意轮次）

从用户这句话里识别**一个主算子**（一条消息可同时 Provide 多件素材）。然后立刻 Advance。

### 1. Skip(S)

用户不要某阶段的产物（「不要参考视频」「别生成预览图 / 首帧」「不要出镜人物」「跳过合成直接看分段」……）。

- `Stage[S] = skip`。不生成、不展示、不等该步选项。
- 下游按 `slot-adaptation.md` **缺了就省略或回退到次近素材**，禁止为凑槽复制节点。
- 若当前正停在 S 的等待提问，马上离开。
- Skip(`opening_visual`)：成片 opening 用角色图，否则产品图。
- Skip 角色（自然语言「不要人物 / 不要角色图」）：`CharacterVisualPlan=skip`；script 仍跑；忽略分镜返回的 `character_prompts`，不生成角色图。

### 2. Provide(S, asset)

用户交出该阶段产物（上传、粘贴、产物 URL、选片消息、自带分镜 / 预览 / 首帧……）。**提供优先于 Skip。**

- 绑定到 S 的锚点，`Stage[S] = provided`，不生成 / 不搜索。
- 模特图、角色图、声音参考 **禁止**当成商品主图或产品页链接。
- 任意轮次都可 Provide；中途补交则改状态并继续。
- 选片消息 `Use this video` + 视频 URL → Provide(`ref_video`)。不要再造一份视频。用户 Provide 角色图 → `CharacterVisualPlan=provided`。

### 3. Jump(T)

用户要的是 **T 的产物**，不是把路上每一站都做完（「直接出视频」「先出首帧」「先出分镜」「不要中间结果」「不生成角色，直接出首帧」……）。

1. 从这句话认出目标 T。只说「直接做完 / 出视频 / directly generate the videos / skip to video / 不要中间结果，出片」→ `T = video`（有分段成片时含 `merge`）。点名「首帧 / 预览 / 开场图」→ `T = opening_visual`。点名分镜 → `T = script`。没列出的同义句按产物归 T，不要因为等待面上有别的主按钮就改判。
2. 对**当前点到 T 之间**（不含 T）的每个阶段 S，按下表分类，**禁止**按具体阶段名写死例外：

| S 对 T 的关系 | 怎么处理 |
|---------------|----------|
| 已 `done` / `provided` | 沿用 |
| **硬前置**：缺少 S 的产物会违反硬底线，或 T 按 `slot-adaptation.md` 没有任何次近回退可用 | 必须有产物（生成或 Provide） |
| **内部阶段**（无用户可见产物，只为硬前置或 T 服务） | 静默跑 |
| **闸门**（卖点分析 / 规格提问）：值可草稿或默认 | 写入草稿或默认，不停 |
| **可选可见**，且用户本句没点名要这份产物 | `Skip(S)`；若 S 是 `script` 内的角色图子产物，同时设 `CharacterVisualPlan=skip` |

硬底线仍是：商品身份；出片前必须有 script；至少一块视觉（开场图 / 角色图 / 产品图任一即可）。因此 script 是 `opening_visual` / `video` 的硬前置；角色图、开场视觉**不是**成片的硬前置；角色图**不是**开场视觉的硬前置（回退到产品图）。Jump 越过 script 去 `opening_visual` / `video` 时，script 仍作为硬前置静默生成，但其中未被用户点名保留的角色图属于可选可见子产物，必须设 `CharacterVisualPlan=skip`，不得被 `character_prompts` 的默认触发规则重新强制生成。

`IntentQuestions=true` 且内容方向题未发出或未答 → **禁止**把问询当闸门跳过；先问完再 FastForward。`parse_product_info` 控件未收到 §商品确认信号 → 商品身份未成立，禁止 Jump 越过去 `display_product_info` 或更后阶段。

3. 用户本句点名要保留的中间产物 → 该阶段不 Skip。只有用户点的是**当前等待主选项原文或其同义确认**（`Generate first frames` / `Generate preview image` / `Continue` / `looks good`，且**没有**点名更后产物）→ **不是** Jump，按普通继续。点名更后产物、或「直接 / skip / 不要中间」+ 目标 → **就是** Jump，即使 Host tools 提问还在。script 等待面上说 `directly generate the videos` = Jump(`video`)，禁止先出首帧 / 预览。
4. 然后 `FastForwardTo = T`：只跑仍 enabled 的阶段，不发中间等待提问；停在 T 的完成态。
5. 只说「按当前计划做完、中间别停」而**没有**点名跳过中间产物 → 仅 FastForward，不改 skip/run。
6. FastForward 穿过 `merge` → 在合成前停一次，用 Host tools 问要不要配乐（`No music` / `Add background music`），按用户选择完成合成；不擅自默认无 BGM。已点名则按其说的做。

### 4. Rollback(S)

用户不满意某前序（提问选项 `Revise …` 或自然语言点名 script / 参考 / 预览 / 首帧 / 卖点 / 规格 / 成片……）。未点名时，按语义落到**最早仍影响当前问题的阶段**。

- `Stage[S] = invalidated`；S **之后**全部 `invalidated`（旧产物 URL 可留，状态禁止再引用）。作废后的下游恢复为回退前的计划：用户独立 Provide 的素材锚点保留为 `provided`，但其内容若直接依赖被回退阶段的生成结果、旧参考模式或旧规格，则同时 `invalidated` 并要求重新 Provide；生成型下游一律 `invalidated`，待重新执行后再恢复为 `run`。不要把可选阶段改成 skip。
- 用这条建议改输入 / 规格；只说「重做」则同参重跑。
- **禁止 AutoRun**：重做完 S 后，若 S 有用户可见产物 → **停住**（卖点：贴三段等自由回复；其它：状态句 + 宿主提问）。不要顺跑 plan / opening_visual / video / merge。内部阶段（`plan`）只在用户选了等待提问上的继续之后才跑。
- `opening_visual` 回退前是 `run` 则重做链路里仍是 `run`，禁止因回溯而 skip。
- 作废旧预览 / 旧首帧不算 provided。

### 5. Reroute(S, mode)

同一阶段换做法（等用户传参考 → 改为不参考；brief 改走链接解析……）。

- 更新该阶段模式，作废只依赖旧模式的下游（通常从该阶段起 invalidated）。
- 立刻按新模式执行或等待新输入。

**冲突**：Provide > Skip > 默认 run。Jump 不取消已 Provide 的素材。Rollback 之后以最新 Stage 计划为准。本链**没有**搜片模式，禁止把 Reroute(`ref_video`) 理解成「去搜索」。

---

## 不得卡住（HARD）

每一次 assistant action 必须是下面之一（自上而下，先匹配的优先；禁止用「调用平台能力」压过前面的等待）：

1. 开场问询（仅 `IntentQuestions=true` 且内容方向题尚未真发出）：同轮对 Host tools 真调用一次。标题 = 短题名；问句 = **恰好一句**；`options` = **恰好 3 条**且**第一条为推荐默认**。无真调用、把 3 条方向写成 Chat 编号列表、或问句为空 / 把占位句当成唯一问句 = 本步失败。**这一拍只能发这一次 Host tools**，禁止同拍再调任何 Buzzy MCP tool（含 `create_project` / `parse_product_info` / `display_product_info` / run_prompt / `generate_image / generate_video`）。`IntentQuestions=false` 时本条不适用，直接进 `product`
2. `IntentQuestions=true` 且内容方向题**已经**对 Host tools 真发出，且用户还没有对本题作答 → **停住**。禁止 `parse_product_info` / `display_product_info` / 其它流水线 tool。Host tools 返回若**没有**用户选中的 option id/label / Other 文本，只表示选择框已发出，**不是**已答，禁止因此 Advance。`IntentDone` 在用户作答前必须保持 `false`。返回里已有选中方向 → 本条不适用，收下并 `IntentDone=true`
3. 停在已打开的 `parse_product_info` 商品编辑控件上，等用户确认（见 §商品确认信号）。此期间禁止 `display_product_info`，禁止 Host tools 问是否继续
4. 停在**已经发出且仍有效**的其它宿主提问上，等用户选择。**例外**：用户本句已识别为 Skip / Provide / Jump / Rollback / Reroute → 当前等待作废，先执行算子，不要停住
5. 停在已贴进对话的卖点三段正文上，等用户自由回复（卖点闸门不走 Host tools）。用户本句点名更后产物 → 按已确认卖点 + Jump，不要继续干等
6. 卖点已确认、规格未齐、且 §info_card 尚未对 Host tools 真发出（Chat 编号单值 / 只写一档 / 画幅或分辨率少选项不算）：同轮按 §info_card 字面量发出三题（时长恰好 3 档 `<15s` / `15s-30s` / `30s-1min`，画幅恰好 4 档、分辨率恰好 3 档），然后停住。禁止进 `script` / `generate_image`
7. 调用平台能力，产出下一件产物或下一轮宿主提问（仅当 1–6 都不适用）

禁止空回复且无任何能力调用、也无宿主提问、也未贴出卖点正文、也未打开商品控件——**但**开场问询 / 其它 Host tools 题已经发出、用户尚未作答时，**停住且不再调任何 tool 是正确终点**（不要为了避开「空回复」去调 `parse_product_info`）。伪调用文本已写出但没有真调用 → 重发真调用。
能力返回后的 continuation 必须 Advance，不需要用户再发一句——**例外（必须停住）**：① Host tools 开场问询 / 规格提问 / BGM 提问已发出、用户尚未作答，且本句**不是**算子；② `parse_product_info` 返回只表示控件已打开，不要 Advance 到 `display_product_info`。用户本句已识别为 Jump / Skip / Provide / Rollback / Reroute → 不要停在旧等待上。Advance 碰到用户可见产物且非 FastForward 时发等待并**停住**（Rollback 重做后同此）。卖点等待 = 引导句 + markdown + 确认句，不是 Host tools。
贴过卖点正文 **不是** 已确认：run_prompt 已返回但本会话还没按 `selling-analysis-prompt.md` 贴出三段 → 立刻贴三段并停住，禁止只写 status、禁止只贴 `content` 不说明这是卖点、禁止空结束。
分镜卡片已贴 **不是** 已确认：run_prompt（及该跑的角色图）已返回但本会话还没按 `script-table-format.md` 贴卡片 + Host tools Continue/Revise → 立刻贴卡片并发提问，禁止空结束、禁止同轮 `plan`。
缺必填输入 → 问清楚（一题宿主提问），不要空转。
阶段被 Skip / 已 Provided → **同轮或同一次 continuation** 进入下一 enabled 阶段。

---

## Advance

算子落地后，取阶段图上**下一个 enabled 且未 done/provided** 的阶段：

- 需要产出 → 按 §阶段目的选用平台能力
- 只需绑定（provided）→ 记锚点，继续下一个
- skip → 跳过
- 普通模式（含 Rollback 重做后）且该阶段有用户可见产物、且不在 FastForward 中 → 按 §双通道文案发等待提问（主路径 = 下一 enabled 阶段），**停住**
- FastForward 中 → 不发中间等待提问，继续直到 Jump 的目标 T

过渡态（`display_product_info` 刚跑完 / 卖点等待刚被确认）**禁止停驻**。`video` 的 Clip 1 成功后属于内部依赖续跑：若能力支持独立音频参考槽则绑定 `Clip1AudioReference`，若明确不支持则立即采用 fallback，然后自动启动 Clip 2…N；不得等待用户、重复生成 Clip 1 或把它误判为流程结束。只有平台已声明支持且音频资产仍处于异步绑定处理中时，才允许短暂等待该能力结果。`parse_product_info` 刚返回 **必须停驻**，不是过渡态。Host tools 开场问询刚发出、用户尚未作答 **必须停驻**，不是过渡态，禁止 Advance 到 `product`。
**商品确认后的同一 continuation（HARD）**：先 `display_product_info`（该次确认最多一次；无链接有图路径若未走控件则跳过 display_product_info）→ 立刻 `selling_analysis`（run_prompt + 贴三段）→ 停住。禁止在 display_product_info 之前跑卖点。禁止只 display_product_info 就结束。卖点「尚未跑完」= 本会话还没贴出三段。未在 Jump 越过时禁止先出规格提问。卖点分析普通模式：run_prompt 返回后**同一 continuation** 必须按 `selling-analysis-prompt.md` 贴出三段，然后**停住**（只写 status、只贴 `content` 不说明这是卖点、或调 Host tools Continue/Revise = 本步失败）。用户从该等待确认后、规格未齐 → 立刻进入 `info_card`。`ref_video` 默认 skip，**不要**在卖点后插入搜片提问。
script 普通模式：分镜 run_prompt（及该跑的角色图 `get_task` 终态）返回后**同一 continuation** 必须贴分镜卡片 + Host tools，然后**停住**（表已返回但没卡片 / 没提问 = 仍是过渡态）。
正在 Jump 越过这些闸门 / 可选阶段 → 按 §Jump 写入默认或 Skip，不要被本段拦截，也不要被「script 必须停住出首帧」拦截。问询未完成或商品控件未确认时，Jump 也不得越过这两道等待。Jump(`video`) 且 `opening_visual` 已被 Skip 时：`plan` 只做分段，禁止出预览 / 首帧。

---

## 开场意图（`intent`）

**目的**：是否问询由首轮指令字面量决定。问则发出 1 题后**停住**，等用户答完再进 `product`；不问则同轮进 `product`。细则见 `intent-questions.md`。

- **指令式触发（HARD）**：只读本任务**首轮**字面量。`no-questions` → 不问，`intent=skip`，立刻进 `product`。`with-questions` 或未写 → 问 **恰好 1 题**。冻结后禁止改写。用户后来说「直接开始」不能代替首轮 `no-questions`。
- **`IntentQuestions=true`（HARD）**：正式流水线前必须对 Host tools 发出 **恰好 1 题**（广告视频内容方向）。用户看见的是选择框，不是 Chat 里的编号列表。
- **开场提问 HARD**：标题 = 短题名；问句 = **恰好一句**（禁止把选项写进问句、禁止问句为空）；`options` = **恰好 3 条**且第一条 = 推荐默认。**禁止**用多字段规格提问来问这个问题。**禁止**把 3 条方向写进 assistant 正文。
- **发出 ≠ 答完（HARD）**：Host tools 调用成功 / 选择框已出现 **不是** `IntentDone`。`IntentDone=true` **只**在用户点选了 3 条之一、用 Other 写了方向、或下一条消息给出可执行内容方向之后。发出后必须停住等用户下一句，**禁止**同拍或紧接着的 continuation 调 `parse_product_info`。
- **与用户输入挂钩（HARD）**：问句和 3 个选项必须根据本轮用户指令现写。选项是具体可执行的内容方向（运镜要写清展现什么；剧情要写清具体情节），禁止空泛标签，禁止原样套示例，禁止抛一套与这条指令无关的通用问卷。
- 已由首轮文本 / 上传说清的事实写入字段，**不要再确认一遍**；本题只问内容方向。
- `IntentQuestions=true` 时：**禁止** 0 题进 `product`。也**禁止**「题已发出、人还没答」就进 `product`。问询中的上传先 Provide，再发出本题或在本题已答后结束问询。
- `IntentQuestions=false` 时：未问到的项用默认（可选阶段 `run`；`ref_video=skip`；画风 `cinematic polished TVC`）。卖点 / 规格仍跑。

---

## 每 turn

自上而下只取一条：

0. 伪调用无真执行 → 重发。
1. `IntentQuestions=true` 且内容方向题尚未对 Host tools 真发出 → **只发这一题**，然后**停住**。禁止同拍 `create_project` / `parse_product_info` / `display_product_info` / 其它流水线 tool。首轮带了链接 / 图也先问询，入口只记账。编号列表不算已问。
2. `IntentQuestions=true` 且内容方向题已对 Host tools 真发出，且用户还没有对本题作答 → **停住**。返回里没有选中的 option / Other 文本 = 未答。禁止 `parse_product_info`。禁止把 `IntentDone` 置 `true`。返回或用户下一句已有方向 → 收下，`IntentDone=true`，再进 `product`。
3. `parse_product_info` 已打开，且本会话还没有 §商品确认信号 → **停住**。禁止 `display_product_info`。禁止 Host tools 问要不要继续。tool 返回里的商品字段是刮取草稿，不是确认。
4. 某次能力调用已发出、**尚无结果** → 等结果，不要叠新生成调用。`generate_image` / `generate_video` 返回 `task_id` = **尚无结果**：本 continuation 必须 `get_task` 轮询到终态，`get_task` 不算叠生成。已返回终态 / 同步 tool 已返回（**不含** `parse_product_info`，**不含** Host tools 开场问询 / 规格提问 / BGM 提问）→ 必须 continuation，禁止干等用户再发一句。卖点 run_prompt 返回后按 `selling-analysis-prompt.md` 贴三段并停住是 mandatory，不算叠生成。分镜 run_prompt / 角色图终态后贴卡片 + Host tools 是 mandatory。
5. 已有 §商品确认信号，且该次确认还没跑过 `display_product_info`（该走 display_product_info 的路径）→ 本 continuation **先** `display_product_info`，**立刻** `selling_analysis`（run_prompt + 贴三段）。禁止只 display_product_info 就停。`display_product_info` 已按该次确认跑完，或无链接有图路径不走 display_product_info：卖点三段未贴 → 只跑卖点（未调用则调用；已返回则贴三段并停住）。三段已贴仍在等用户 → 停住，不要顺跑规格提问。卖点已确认但规格未出 → **只**对 Host tools 发 §info_card 字面量三题。Chat 打印默认值、少题、或画幅 / 分辨率少档 = 没出，必须立刻按字面量重发。**本条在开场题未答完时不适用。禁止在卖点后出搜片提问。**
6. 已进入 `video`：`Clip1Status` 未 `done` → **只**发 / 轮询 Clip 1，禁止先发 2…N。Clip 1 已 `done`、N≥2、2…N 尚未全部发起 → **同轮并发补齐**未发起的后续段。已发出的 `task_id` 必须全部 `get_task` 到终态。
7. 本轮能识别算子 → 执行算子。停在某次等待提问时，用户点名的是**更后阶段的产物**（含 `directly generate the videos` / 直接出视频 / 跳过首帧出片）→ 按 Jump(T)，不要当成确认当前主选项，也不要先把当前主路径（首帧 / 预览）做完。若 `IntentQuestions=true` 且内容方向题未发出或未答：**只记账**，**禁止**进 `product` / `parse_product_info`；题未发出则本轮仍只问这一题，题已发出则停住等答。`IntentQuestions=false` → 不要进本条问询分支。
8. `IntentQuestions=true` 且 `IntentDone=false` → 题未发出则只发这一题并停；题已发出未答则停住，**不要**进 `product`。必须真调用 Host tools，问句含内容方向；编号列表不算已问。用户已答 → `IntentDone=true`，再进 `product`。`IntentQuestions=false` → 进 `product`。
9. FastForward 且上一步已齐 → 只跑下一 enabled 阶段，直到目标 T。问询未完成（题未发出或未答）或商品控件未确认 → **不要**走本条。Rollback 重做刚完成 → **不要**走本条。
10. 否则按当前阶段目的推进。仅当停在 **Host tools** 提问上且用户只回 `nice` / 无可执行新指令 → 重发同一提问，不要空回复，不要 Advance。卖点三段或商品控件上的 `looks good` / `continue` / `ok` **不是**本条，按已确认处理。

---

## 阶段目的（该跑时才读对应 reference）

链隔离：`TvcAdsActive` 为真时只按本文件。启动：`/tvc-ads`、TVC / brand commercial / studio-quality branding ad、跳步 / 自供 / 回退式 TVC，或本链已有入口 / 问询 / 相位。
状态从 history 每轮重推。禁止拿 `ugc-ads` / `trending-search` 正文跑本链。**禁止搜片**，不要调用 `trending_search_videos` 或任何搜片 skill。

### `product`

**前置**：本会话还没有 `create_project` 返回的 id → 先 `create_project({ name })`，再走下面三路。问询未完成时不要进本阶段。

**商品确认信号（HARD）**：`parse_product_info` 返回 ≠ 确认。确认 = 下面任一：消息含 `Confirmed Product Info`；用户明确确认/继续该商品（`Confirm` / `Continue` / `looks good` / `ok` / 确认 / 继续）。不要只认「首行字面量」，也不要把刮取字段当成已确认。

三路互斥：

1. 有产品详情页链接 → `parse_product_info({ projectId, productLink })` 打开编辑控件。**返回值不是确认**：同一 continuation **禁止** `display_product_info`，**停住**等 §商品确认信号（禁止 Host tools 问是否继续）→ 从确认消息解析 `Title:` / `Description:` / `Main Image:` / 全部 `Images:`（没有这些前缀则用用户确认的标题/描述/图）→ `display_product_info({ projectId, title, description, images: [main, ...others] })`（每个确认事件最多一次）→ **同一 continuation** 立刻进入 `selling_analysis`
2. 无链接、有商品图 → 记下商品图 URL；有实质用户文则整理后写入 `ProductBrief` / 确认事实，缺标题则用用户描述里的商品名或 `(untitled product)` → 进入 `selling_analysis`。不要走解析。不要把 `imageUrls:` 商品图当成产品页。进入 `selling_analysis` 前同样必须已有 `projectId`
3. 无链接、无图 → `parse_product_info({ projectId })`（**不传** `productLink`）打开空编辑控件，用户填 title / description / 上传图片。**不要**再用 Host tools 收集这三项。同一 continuation **禁止** `display_product_info`。停住等 §商品确认信号，再按路径 1 同样解析并 `display_product_info`。无 iframe 宿主才用 Host tools 收集标题/描述/图。

`imageUrls:` 且 host 含 `buzzy.now`、path 含 `/file-service/`、图片后缀 → 商品图，不是产品页。
商品已确认展示 = `display_product_info` 已按该次确认跑完，或无链接有图路径已记下商品图 URL。卖点三段未贴 → 立刻 `selling_analysis`；**禁止**先出规格提问，**禁止**先出搜片提问。

### `selling_analysis`

见 `selling-analysis-prompt.md`。前置：产品信息已确认。
`run_prompt(prompt_key="tvc_ads_selling_analysis", projectId=项目 id, instruction=卖点分析输入)` **恰好 1 次**。成功字段是 `content` + `name`（`name` 必须是 `Selling Point Analysis`）。商品图 URL 有才加（确认消息 `Main Image:` / `Images:`，或 `display_product_info` 返回的图地址；否则用已记下的商品图 URL）。走 `image_url(s)`。**禁止传 `nodeIds`**。还没有 `projectId` 就先 `create_project`。
**HARD**：`恰好 1 次` 只约束 run_prompt。同一 continuation 必须按 `selling-analysis-prompt.md` 贴三段：`Here are the product selling points:` + `items[].content` 原文 markdown + `Confirm to continue, or tell me what you'd like to change.`（禁止只写 `Your selling point analysis is ready.`，禁止 code fence，禁止只贴正文不说明这是卖点）。然后**停住**等用户自由回复。**不要**调 Host tools Continue/Revise。缺这三段 = 卡住 / 本步失败。不要顺跑规格提问。用户回复 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续，或改了文案后接受 → `SellingPoint` = `content` 全文（不含引导句 / 确认句；用户改了文案则以用户稿为准）。规格提问不再收卖点。禁止去调 UGC 的 brief / selling key。

### `ref_video`

可选。默认 `skip`。仅当用户 Provide 参考视频时变为 `provided`。**禁止搜片。禁止出「要不要搜竞品片」提问。**

- 默认 skip → 无参考；卖点确认后立刻进 `info_card`
- provided（上传、粘贴、产物 URL、`Use this video` + URL）→ 绑定，不要再造一份视频
- 用户说不用参考 → 保持 skip
- 中途 Provide 参考且 script 尚未生成 → 后续 script 走 with-ref
- 中途 Provide 参考且 script 已生成 → 按 Provide 改状态；若用户要按新参考重做 script，走 Rollback(`script`) 或用户明确要求重做

### `info_card`

前置：`SellingPoint` 已写入。
**必须**对 Host tools 真调用（能一次提多题就一次提完）。标题 `Video settings`。assistant 正文最多一句：`Confirm duration, aspect ratio, and resolution.`
**HARD — 选项在 tool 里，不在 Chat**：每一题的全部候选项只进该题 `options`。禁止把三项印成单值「当前设置」。仅当三个 Host tools 名字都没有、只能用正文时，每行必须列出该字段全部档位：

```text
Confirm duration, aspect ratio, and resolution.
1. Duration: <15s / 15s-30s / 30s-1min
2. Aspect ratio: 16:9 / 4:3 / 3:4 / 9:16
3. Resolution: 480p / 720p / 1080p
```

**HARD — 每项必须列出全部可选项**：Duration / Aspect ratio / Resolution 三题都要出现，**每一项都必须把下表该行全部档位写全**。Host tools：该题 `options` = 该行全部档位，禁止只塞一档。禁止在正文、问句、选项旁写 default / 预选 / Recommended / 当前设置。Duration `values` 必须恰好为 `<15s` / `15s-30s` / `30s-1min`。废弃的旧时长（`<30s` / `>1min`）不得出现。

**HARD — 规格题字面量（禁止裁剪）**：画幅 / 分辨率题的候选项是冻结清单，不是从模型表推导出来的。发出前按下面清单**整段复制**，发出后自检个数；对不上就丢弃重发，不要「补一档」或「先用默认往下走」。

| 顺序 | 题 `id` | `prompt` | `options`（id → label，必须全有、顺序不许改） | 预选 |
|------|---------|----------|-----------------------------------------------|------|
| 1 | `duration` | Duration | `under_15`→`<15s`；`mid_15_to_30`→`15s-30s`；`mid_30_to_1min`→`30s-1min` | （不写进正文） |
| 2 | `aspect_ratio` | Aspect ratio | `ratio_16_9`→`16:9`；`ratio_4_3`→`4:3`；`ratio_3_4`→`3:4`；`ratio_9_16`→`9:16` | （不写进正文） |
| 3 | `resolution` | Resolution | `res_480p`→`480p`；`res_720p`→`720p`；`res_1080p`→`1080p` | （不写进正文） |

自检 HARD（任一失败 = 没问，立刻按字面量重发，禁止进 `script`）：

- 恰好 3 题，顺序 Duration → Aspect ratio → Resolution
- Duration `options.length === 3`；Aspect ratio `options.length === 4`；Resolution `options.length === 3`
- 每题 label 集合必须与上表完全一致（画幅四档、分辨率三档一个都不能少）
- option `id` **必须**用上表字母开头的 token（`under_15` / `mid_15_to_30` / `mid_30_to_1min` / `ratio_16_9` / `res_720p`）。禁止把 `<15s` / `16:9` / `4:3` / `480p` 当成 `id`：含冒号、`<` 或纯数字开头的 id 会被宿主丢掉，表现为「有时缺时长、有时缺画幅或分辨率」
- Cursor `AskQuestion` 用 `id` + `label`；Claude `AskUserQuestion` / `ask_question` 按该 tool schema 填，但 **label 集合仍是上表那 3+4+3 个**，禁止改成 2 档画幅或 2 档分辨率
- 一次调用塞不下 3 题或某题全档 → **拆成连续 3 次 Host tools**（先 Duration，再 Aspect ratio，再 Resolution），每次仍带该题全部档。禁止为了「塞进一次调用」而删题或删档

禁止用来裁剪 / 省略画幅题或分辨率题的理由（这些只作用于成片填参，见 §运行时填参）：

- `<available_models>` 缺表、没有 `ratios` / `resolutions`、或 `ratios=fixed` / `resolutions` 为 `-` / 空
- 模型行只列出部分画幅或分辨率（例如只有 `16:9` / `9:16`，或没有 `480p`）
- 从 UGC 规格题抄来（UGC 画幅含 `21:9` / `1:1`，分辨率没有 `480p`）
- 「默认 `16:9` / `720p` 就够了」、只打印默认值、或把三项写成 Chat 编号列表

下面任一写法 = 本步失败，必须立刻按字面量重发（不要继续 script / 成图）：

- Chat 编号 / bullet：`1. Duration: <15s` / `2. Aspect ratio: 16:9` / `3. Resolution: 720p`
- 只打印默认值、不列出其它档
- 伪调用文本、或把三项规格写进正文当「当前设置」
- 画幅不足 4 档，或分辨率不足 3 档，或缺整题

```text
AskQuestion
title: Video settings
questions:
  - id: duration
    prompt: Duration
    options:
      - id: under_15
        label: <15s
      - id: mid_15_to_30
        label: 15s-30s
      - id: mid_30_to_1min
        label: 30s-1min
  - id: aspect_ratio
    prompt: Aspect ratio
    options:
      - id: ratio_16_9
        label: 16:9
      - id: ratio_4_3
        label: 4:3
      - id: ratio_3_4
        label: 3:4
      - id: ratio_9_16
        label: 9:16
  - id: resolution
    prompt: Resolution
    options:
      - id: res_480p
        label: 480p
      - id: res_720p
        label: 720p
      - id: res_1080p
        label: 1080p
```

收回后写入 Session（label 或 id 任一匹配即可）：

| 用户选中 | 写入 |
|----------|------|
| `under_15` / `<15s` | `SessionVideoDuration=<15s`，`SessionVideoDurationRange=0-15s` |
| `mid_15_to_30` / `15s-30s` | `SessionVideoDuration=15s-30s`，`SessionVideoDurationRange=15-30s` |
| `mid_30_to_1min` / `30s-1min` | `SessionVideoDuration=30s-1min`，`SessionVideoDurationRange=30-60s` |
| `ratio_16_9` / `16:9` | `SessionRatio=16:9` |
| `ratio_4_3` / `4:3` | `SessionRatio=4:3` |
| `ratio_3_4` / `3:4` | `SessionRatio=3:4` |
| `ratio_9_16` / `9:16` | `SessionRatio=9:16` |
| `res_480p` / `480p` | `SessionVideoResolution=480p` |
| `res_720p` / `720p` | `SessionVideoResolution=720p` |
| `res_1080p` / `1080p` | `SessionVideoResolution=1080p` |

发出后**停住**等用户点选。Host tools 返回若没有各题选中项 = 未答，禁止 Advance。Chat 编号列表不算已问。
整链默认一次。用户**本句已明确写出**画幅 + 时长（+ 分辨率）且要求开跑 → 写入 Session 后可不再停。只打印默认 / 用户未逐项选定 ≠ 已给齐。成片调用时若有模型表，再按 §运行时填参收敛一次：用户选的 token 不在该行 → 改用该行第一个合法值，或 Host tools 再问一次（再问时选项仍用本节字面量全档，不要改成模型表子集）。无模型表则按用户所选原样传。

确认后冻结 `SessionVideoDuration` = 所选档位原文，并写入对应 `SessionVideoDurationRange`。时长范围写入分镜：`<15s` → `0-15s`；`15s-30s` → `15-30s`；`30s-1min` → `30-60s`。分镜总时长必须落在所选范围内。**禁止**把档位映射成 15 / 22 / 45 / 75 或任何写死秒数。废弃旧时长卡（`<30s` / `30s-1min` / `>1min`）不得生成或回退。Jump 越过本闸且用户未点名规格 → 内部写入 `<15s` / `16:9` / `720p`（`SessionVideoDurationRange=0-15s`），禁止把这三档印给用户当选项清单。参考视频只作节奏 / 镜头 / 构图参考，不是输出总时长约束。

### `script`

有用户分镜 → 整理成 GFM 表，并按 `script-table-format.md` 把每一行转成分镜卡片贴进对话。否则见 `storyboard-prompts.md`。
有参考（`ref_video=provided`）→ `tvc_ads_storyboard_with_ref`；无参考 → `tvc_ads_storyboard_no_ref`。缺卖点 / 参考写 `(none)`。分镜输出中的声音描述必须形成一份全片统一的 `VoiceProfile`：由 script 首次生成时确定并写入内存，后续 plan 与 video 逐段复用；不得让 agent 按片段重新发明声音身份。声音质量规则见 `voice-direction.md`。
`name` 必须是 `Storyboard Table`。非 GFM / 缺分隔行 → 重试。表头与正文固定 English。Chat **禁止**贴 `|` 管道表。

**角色（附在本阶段，不是独立阶段）**：

- 有参考且返回 `character_prompts` 非空、且 `CharacterVisualPlan=run` → 同轮按返回 Prompt **逐字**成图（禁止 agent 改写或另写）。`model` = Image 表 **gpt image2** 行的 `model` 列原文；画幅固定 16:9；title=`Character {i}`。风格对齐参考视频媒介（实拍就实拍，卡通就卡通）。每个 `generate_image` 必须 `get_task` **阻塞轮询到成功**，记下素材 URL。角色图未终态时等结果，不要空结束。
- **人物触发条件 HARD**：正常非 Jump 的有参考模式中，只要参考分镜 `character_prompts` 返回非空且 `CharacterVisualPlan=run`，就必须生成对应人物图。以下情况必须不生成：用户明确 Skip 角色或 Jump 越过该可选子产物（`CharacterVisualPlan=skip`）；`character_prompts` 为空数组；角色图由用户 Provide（`CharacterVisualPlan=provided`）。不得让本条覆盖 §Jump 已经写入的子状态。
- 无参考 / Skip 角色 / `character_prompts` 为空 → 不生成角色图。
- 用户 Provide 角色图 → 只绑定。

**HARD**：run_prompt 返回 ≠ 对话卡片 ≠ 等待提问。普通模式（含 Rollback 重做）在 run_prompt 已返回、且该跑的角色图已 `get_task` 终态（或不该跑）的同一 continuation，必须按 `script-table-format.md` 贴卡片 + Host tools Continue/Revise（有参考且有角色图：引导 `Review the storyboard table and optional character sheets, then continue.`；否则 `Review the storyboard table, then continue.`；第 1 条有参考 → `Generate preview image`，无参考 → `Generate first frames`；另给 `Revise`）。缺卡片或缺提问 = 卡住 / 本步失败。然后停住 = 不要同轮 `plan` / 开场视觉 / 成片。用户下一句点名更后产物（直接出视频等）→ Jump，不要当确认首帧 / 预览。FastForward / Jump：贴卡片后立刻按目标推进。

**声音（附在本阶段，不是独立阶段）**：

- script 首次生成时，根据产品定位、用户意图和分镜中的 Dialogue / Voice-over，读取分镜模板返回的顶层 `voice_profile`，确定一份全片统一的 `VoiceProfile` 并写入内存；至少包括 speaker identity、approximate age、accent / pronunciation、vocal register、timbre、resonance、breathiness、articulation、speaking pace、pause style、prosody、emotional baseline、overall commercial tone 和 recording / mix character。若旧模板没有返回该字段，再按 `voice-direction.md` 从脚本整理，不得凭空缩成几个形容词。
- `voice_profile` 只作为结构化返回供下游读取，不新增对话列、不写进 `content`；后续 `plan` 和 `video` 必须读取同一份内存值。每个视频片段都要逐字携带该描述，只允许按当前镜头改变局部情绪、停顿、重音和强弱。
- Dialogue / Voice-over 中只有引号内文字允许发声；表演提示必须明确标注 `not spoken`，防止模型把导演说明或字段名念出来。
- 没有独立 voice reference / voice ID 时，`VoiceProfile` 只能作为提示词约束，不得宣称已锁定真实音色。

### `plan`

内部。见 `plan-and-opening.md`。不把脚本计划 / Master 提示词 / Preview·首帧 Prompt 贴进 Chat。
仅当用户已确认离开 script（等待提问选继续）或 FastForward / Jump 到更后阶段时才进入。
无参考模式在调用 `tvc_ads_master_video_prompt` **之前**，必须检查已确认商品的真实图片 URL 是否至少有一张；没有就请用户补图并停在 `plan`，禁止调用 Master Prompt、`tvc_ads_first_frame_prompt` 或首帧 `generate_image`，也禁止用商品描述或分镜表正文代替图片参考。分段仍走 `tvc_ads_script_plan` / `tvc_ads_master_video_prompt`。**HARD**：分镜行 / Chat 卡片是 shot，不是成片单元。计划返回后必须按 `plan-and-opening.md` §Shot ≠ Segment 做进入前校验；「一镜一段」（例如 8 个 2s/3s 镜 → 8 段）非法，必须先本地重切，仍不过再重跑计划。`SegmentCount` 冻结前禁止出预览 / 首帧 / 成片。
**HARD — 开场视觉已 Skip 则只分段**：`opening_visual=skip`（含 Jump 到 `video` 且用户没点名首帧 / 预览）时，计划仍要跑，但**禁止**写 `PreviewPrompts`、禁止调 `tvc_ads_first_frame_prompt`、禁止 `generate_image` 首帧 / 预览；分段通过后同轮进 `video`。只有 `opening_visual` 仍 enabled 时：有参考由 agent 按段写 Preview Prompt；无参考在拆段（及必要的本地重切）后才调用 `tvc_ads_first_frame_prompt`，输入完整分镜、MasterVideoPrompt、分段后的 `SegmentVideoPrompts[]` 与商品图事实，并在该调用中挂载已确认商品的真实图片 URL（主图第一）；读取并校验 `first_frame_prompts[]`，按 `clip_index` 与合并后的 `SegmentCount` 对齐后逐字冻结。随后调用 `generate_image` 时再次挂载同一组真实商品图片 URL，主图仍排第一；分镜表只进 Prompt。禁止再调 `tvc_ads_master_first_frame_prompt`，也禁止 agent 另写或覆盖模板返回的首帧 Prompt。

### `opening_visual`

skip 或各段已 **provided**（用户本轮指定的预览 / 首帧，不是作废旧产物）→ 不生成。否则按 `plan-and-opening.md` 变槽并发 ×N，**N = 合并后的 `SegmentCount`**，禁止按 shot 行数 / Chat 卡片数出图。调用 `generate_image` 前必须重新取已确认商品的真实产品图片 URL，主图第一；不得只沿用首帧 Prompt 工作流的文字结果。无真实产品图 URL → 问补图，禁止无参考硬生成。每张图提交后必须 `get_task` **阻塞轮询到成功**，记下素材 URL；全部终态前禁止发等待提问。
成功后按 §双通道发等待提问并停住（FastForward 除外）。**有参考预览与无参考首帧都不提供 Edit**；只留继续出片和 `Revise`。Rollback 不得把本阶段改成 skip。

### `video` / `merge`

见 `video-generate-prompt.md`。每**段**生成一段新片子（不要用参考视频当成片输入）。段 = `plan` 合并后的 segment，不是分镜表一行。`generate_video` 次数 = `SegmentCount`；`duration` = 该段 `segment_duration`。禁止一镜一段。`generate_video.model` = Video 表 **seedance-2.0-fast** 行的 `model` 列原文；`aspectRatio` / `resolution` 按 §运行时填参只传该行合法 token（无模型表则用 Session 原样）。
**HARD — 提示词长度硬限制（≤ 2000 字符）**：平台视频生成工具对 `prompt` 有严格的 2000 字符硬限制。成片正文严禁把包含 `| --- |` 的原始 Markdown 表格或冗余列原样填入，必须按 `video-generate-prompt.md` 紧凑时间线（Compact Shot Timeline）和紧凑声音块（Compact Audio Block ≤ 450 字符）进行组装，并在调用前自检总字符数（预算目标 ≤ 1800 字符，总长超过 1900 字符必须触发两级自动修剪），严禁突破 2000 字符导致报错。
进入 `video` 后必须先生成第 1 段；第 1 段成功返回并可作为音频参考后，再在同一 action 并发生成第 2…N 段。后续片段必须引用第 1 段的旁白音色 / 音频参考（有独立音频 URL 才挂；否则只用 VoiceProfile + Clip 1 matching 正文），并继续逐字复用同一份 `VoiceProfile`。第 1 段失败只重跑第 1 段；第 2…N 段失败则只并发重跑失败段。
普通模式：Clip 1 成功后，若能力声明支持独立音频参考槽则先写入 `Clip1AudioReference`；若明确不支持则写入 fallback 匹配约束，不等待不存在的槽位；随后在同一 action 并发启动 Clip 2…N。全部片段成功后对 Host tools 发 **配乐闸门**并停住。问句 = `Do you want background music in the final video?` 选项固定 `No music` / `Add background music`。选 `No music` → 直接以原生音轨合成；选 `Add background music` → 合成时在原生音轨上叠加音乐。视频片段本身仍只生成原生人声、真实环境音、动作 Foley 和必要的自然空间底噪，片段内不生成任何 BGM。N=1 仍走配乐闸门。
FastForward 到 merge → 同样先问配乐，再按选择合成。Skip(`merge`) → 以分段成片为结束态。合成时 `merge_videos` 挂各段成片 URL，禁止传 `nodeIds`。
Rollback 重做 video 后同样停在对应等待提问，不要自动 merge。

---

## 双通道文案（HARD — 全流程）

任意阶段的首次生成、重生成、Provide、等待下一步，都用**同一套拆句**。选哪个能力对照 tool 声明；这里只约束两句分别写什么。

| 槽 | 取值 |
|----|------|
| `{ReadyNoun}` | 本拍刚落地或刚更新的用户可见产物短名 |
| `{NextAct}` | 下一 **enabled** 阶段的主路径动作 |

**同轮同时发状态句 + 宿主提问时**：

1. 状态句 = **一句状态**，只说什么好了。首次：`Your {ReadyNoun} is ready.` 更新：`Your updated {ReadyNoun} is ready.` 禁止出现 review / then / continue / generate / merge。写在 assistant 正文。
2. 提问引导 = **一句行动**。有可审产物：`Review {the ReadyNoun}, then {NextAct}.` 禁止再写 is ready / updated。
3. 两句禁止相同、禁止互为子串、禁止粘成一句再复制到两个表面。

**只发其中一个时**：自动续跑只发状态句；结束态只发 `Your {ReadyNoun} is ready.`（可保留 Revise 选项，不要再写引导）；上一拍已用状态句说过则本拍只发提问。

选项只进 Host tools 的 `options`。禁止伪 call、编号列表、`Recommended:` 段落进 Chat。
开场问询**不适用**本表的 Review / NextAct 拆句：对 Host tools 真调用；问句只有内容方向那一句；3 条方向只进 `options`。

**通用提问规则**：第 1 条选项 = 下一 enabled 主路径；另给 Skip 或 Rollback 出口；只 Revise 实际存在的产物；FastForward 不发中间等待提问；Rollback 重做后必须发等待提问。**禁止**给开场视觉加 `Edit`。

填空示例（按当前槽改写，非封闭）：

| 情境 | 状态句 | 提问引导 |
|------|--------|----------|
| 开场问询 | （可省略状态句） | Host tools：标题=短题名；问句=`{问句}`；恰好 3 个方向进 `options`，禁止 Chat 编号列表。发出后停住，未答前禁止 `parse_product_info` |
| 卖点分析 | `Here are the product selling points:` + `content` 原文 markdown + `Confirm to continue, or tell me what you'd like to change.`（禁止只写 status、禁止只贴正文） | **不要** Host tools；停住等自由回复 |
| parse_product_info 控件已打开 | （可省略状态句；不要复述商品字段；不要预告 display_product_info） | **不要** Host tools；**不要** `display_product_info`；停住等 §商品确认信号 |
| 卖点已确认、规格未齐 | （正文最多一句 `Confirm duration, aspect ratio, and resolution.`；禁止把三项印成单值「当前设置」） | Host tools 真调用：按 §info_card 字面量三题（时长 3 档 `<15s` / `15s-30s` / `30s-1min`；画幅恰好 4 档、分辨率恰好 3 档；id 用 `under_15` / `ratio_*` / `res_*`）。编号单值 / 只写一档 / 少档 = 没问，必须重发 |
| 首次 / 重生成 script | `Here is the storyboard table:` + 每镜一张卡片（按实际表头；禁止贴 `|` 表）；可附 `Your storyboard table is ready.` / `Your updated storyboard table is ready.` | 有参考且有角色图：`Review the storyboard table and optional character sheets, then continue.` 否则：`Review the storyboard table, then continue.` 第 1 条：有参考 → `Generate preview image`；无参考 → `Generate first frames` |
| 开场视觉（有参考=预览） | `Your preview images are ready.` | `Review them, then generate the first video clip as the voice reference.` |
| 开场视觉（无参考=首帧） | `Your first frames are ready.` | `Review the first frames, then generate the first video clip as the voice reference.` **不要** Edit |
| 待合成 | `Your TVC video segments are ready.` | Host tools：问句=`Do you want background music in the final video?`；options=`No music` / `Add background music` |
| 单段 / 合成结束 | `Your TVC video is ready.` / `Your full TVC ad video is ready.` | （禁止提问引导） |

产物 `title`（无产物不编造，**无方括号**）：商品名 / `Selling Point Analysis` / `Storyboard Table` / `Character {i}` / `Preview - Clip {i}` / `First Frame - Clip {i}` / `TVC Clip {i}`

等待提问主选项（按模式改写，非封闭）：卖点分析 → 自由回复后进规格提问；有参考 script → `Generate preview image`；无参考 script → `Generate first frames`；开场视觉后 → `Generate first video clip as voice reference`；Clip 1 成功后按调度自动生成剩余片段；合成 → `No music` / `Add background music`。

---

## 并行

问询一题一轮：发出后本轮结束，未答前 continuation 也不得进 `product`。该跑的角色图同轮并发，每张 `get_task` 到终态。该跑的开场视觉 ×N 同轮并发（N = 合并后的 `SegmentCount`，不是 shot 行数），每张 `get_task` 到终态。分段成片改为两阶段：先生成 Clip 1，成功返回并绑定为旁白音色参考后，再将 Clip 2…N 同轮并发，每段 `get_task` 到终态。run_prompt 不与 `generate_image / generate_video` 同拍并行。FastForward / Skip 后的下一阶段在 continuation 立刻开始（问询未答完除外）。Rollback 重做的可见阶段在 continuation 只发等待（卖点：贴三段等自由回复；其它：宿主提问），不顺跑。
