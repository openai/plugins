---
name: ugc-ads
description: "Always use this skill to make a UGC product ad from a product link, product image, or product description. Must trigger for /ugc-ads, ugc-ads, UGC ad, UGC ads, product ad, TikTok ad, Reels ad, shoppable short, creator review, unboxing ad, product seeding video, sales video, Amazon/Shopify/product URL, or when the user drops a product page and says make a video or shoot a clip. Also use when a ugc-ads run is already in progress (Confirmed Product Info, selling-point confirm, specs, storyboard cards, first frames, clips, merge) or the user skips a step, supplies an asset, jumps ahead, or revises an earlier step without restarting. Even a vague \"make a UGC\" or \"help me make a UGC\" must start this skill. First-round with-questions (default) asks 1 content-direction question; no-questions starts the pipeline."
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

# UGC Ads Orchestrator

本链自包含。查阅本 skill 文件只用完整前缀 `skills/ugc-ads/reference/`。
**怎么调平台能力、填哪些参数，对照各 tool 自己的声明**；本文件只写目的、产物和硬底线。

**HARD — allowed-tools 分类**：`Buzzy MCP tools` 是本 MCP 服务注册的平台 tool，经 Buzzy MCP `tools/call`。`Host tools — not part of this MCP server` 是宿主内置提问 tool，**不是** Buzzy MCP tool，也不走 `load_workflow` / ExecuteTools。Cursor 用 `AskQuestion`，Claude 用 `AskUserQuestion` / `ask_question`，Codex 用同类。选择题必须调 Host tools 里当前可用的那个，禁止因为「不在 Buzzy MCP tools 列表里」就改成编号纯文本。
**HARD — create_project**：进入任何需要 `projectId` / `project_id` 的 Buzzy MCP tool 之前，必须先调 `create_project` 拿到真实 id。本会话只创建一次，后续全程复用。workflow tool（`parse_product_info` / `display_product_info` / run_prompt / `merge_videos`）传 `projectId`；`generate_image` / `generate_video` 传 `project_id`。禁止编造 id，禁止省略，禁止因为 generate_image / generate_video 写了「可自动建项目」就跳过。`create_project` 的入参是 `name`（可读项目名），不要把 catalog 的 `name` 或 `workflow` 抄过来。Host tools 开场问询那一拍仍禁止同拍调 `create_project`；问询完成（或 `IntentQuestions=false`）后、进 `product` 的第一拍若还没有 id，必须先 `create_project`。Jump / FastForward 到更后阶段同此：还没有 id 就先创建，再调带项目字段的 tool。

**HARD — 宿主提问**：等人选择或确认时（**卖点分析、Apps 商品控件确认除外**），必须对 Host tools 里当前可用名字真调用一次。选项只进提问 tool 的 `options`，且**该题全部可选项必须传齐**（禁止只塞一档）。禁止用 `1.` `2.` `3.` 编号列表、bullet、`Recommended:` 前缀段落作为用户可见选项——那样写 = 本步失败，必须立刻改成真调用。assistant 正文最多一句问句或状态句，**不要复述选项**。不要自己造第 4 个 `Other` 选项：Cursor `AskQuestion` 自带 Other 自由输入。仅当 `tools/list` 里 `AskQuestion` / `ask_question` / `AskUserQuestion` 三个名字都没有时，才允许编号列表，并写明本宿主没有选择框；**规格题的编号列表必须每行列出该字段全部档位**（`Language: English / Spanish / Arabic / Custom`），禁止写成单值（`Language: English`）。Cursor 有 `AskQuestion`，禁止走这条。媒体产物就绪只用 assistant 正文状态句。伪调用、编号单值、或缺档都算没发出提问。
**例外 — 商品确认**：`parse_product_info` 打开编辑控件。有产品页 URL 则传 `productLink`；没有则**不要编造链接、不要传 `productLink`**，打开空表。返回值（即使带 Title / Description / Images）只表示控件已打开，**不是**确认。然后**停住**，等用户确认。确认信号（任一即可）：消息含 `Confirmed Product Info`；或用户明确确认/继续该商品（`Confirm` / `Continue` / `looks good` / 确认 / 继续）。在此之前禁止 `display_product_info`，禁止 Host tools 问要不要继续。无 iframe 宿主才用 Host tools 收集标题/描述/图。
**例外 — 卖点分析**：不走 Host tools。run_prompt 返回后按 `selling-analysis-prompt.md` 贴三段：固定引导句 `Here are the product selling points:` + `content` 原文 markdown + 固定确认句 `Confirm to continue, or tell me what you'd like to change.`，然后停住等用户下一条自由回复。禁止只贴正文、不说明这是商品卖点。用户回复 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续 = **已确认**，必须进入 `info_card`。
**例外 — run_prompt `content`**：卖点正文必须原文贴进对话（禁止 code fence），不受「正文最多一句」限制。分镜 `content` 是 9 列管道表；Chat **禁止**贴 `|` 管道表，必须按 `script-table-format.md` 转成分镜卡片。卡片贴完后仍发 Host tools Continue/Revise。

| 何时读 | 文件 |
|--------|------|
| 开场组题（`with-questions` 时恰好 1 题） | `intent-questions.md` |
| 下游缺输入时怎么组槽 | `slot-adaptation.md` |
| 任意状态句 / 提问引导 | 本文件 §双通道文案 |
| 填 `generate_image` / `generate_video` 参数 | 本文件 §运行时填参 |
| 商品确认后的卖点分析 | `selling-analysis-prompt.md` |
| 用户自带参考视频时 | 本文件 §`ref_video`（无单独 reference） |
| 跑到该步且未跳过时 | `product-brief-prompt.md` / `character-scene-image-prompt.md` / `storyboard-script-prompt.md` / `script-table-format.md` / `storyboard-extract-prompt.md` / `storyboard-extract-format.md` / `first-frame-prompt.md` / `video-generate-prompt.md` |

`run_prompt` 可用的 `prompt_key`：`ugc_ads_product_brief` / `ugc_ads_selling_analysis` / `ugc_ads_storyboard_with_ref` / `ugc_ads_storyboard_no_ref`。按当前阶段选择 key。
角色 Prompt、场景 Prompt、首帧 Prompt **由 agent 按对应 reference 直接写出**，禁止再调 run_prompt（或其它单独 tool）获取。禁止短路径、读其它 skill、把 YAML 当自由 prompt。

用户可见文案 **固定 English**。`SessionScriptLanguage` 只约束口播 / 分镜单元格。run_prompt 的卖点 `content` **必须**作为 markdown 贴进对话（禁止只写一句 status、禁止 code fence）。分镜 `content` 是 9 列管道表；对话必须转成分镜卡片，**禁止**把该表贴进 Chat。
参考素材**一律走 URL 字段**（`image_url` / `image_urls` / `video_url` / `video_urls`，以各 tool 声明为准），适用于 `generate_image` / `generate_video` / run_prompt / `merge_videos`。**禁止传 `nodeIds`**。`ProductBrief` / 卖点正文 / 角色场景 Prompt 文本不是生成参考；生成参考用产品主图 URL。
角色图 / 场景图 / 首帧的 `generate_image.model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文（`name` 只用来找行；禁止把 `Nano Banana 2` 别名、视频行、其它图片行写入）。
成片的 `generate_video.model` = `<available_models>` Video 表 **Seedance 2.0 Fast** 行的 `model` 列原文（`name` 只用来找行；禁止把 `Seedance 2.0 Fast` 别名、图片行、其它视频行写入）。填参细则见 §运行时填参。

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
| `generate_image`（角色 / 场景 / 首帧） | Image 表 **Nano Banana 2** 行的 `model` 列原文 |
| `generate_video`（成片） | Video 表 **Seedance 2.0 Fast** 行的 `model` 列原文 |

`name` 只用来找行。禁止把别名、错表、其它行写进 `model`。

### 画幅 / 分辨率（成片）

成片读 Video 表 **Seedance 2.0 Fast** 行：

| 字段 | 怎么填 |
|------|--------|
| `aspectRatio` | `SessionRatio` 若在该行 `ratios` 里 → 原样用。`ratios=fixed` → **整项省略**。不在表里 → 改用该行第一个合法 token；无法唯一确定则 Host tools 再问一次。禁止把非法 token 传出去 |
| `resolution` | `SessionVideoResolution` 若在该行 `resolutions` 里 → 原样用（`480` / `480p` 等照抄）。`resolutions` 为 `-` / 空 → **整项省略**。不在表里 → 改用该行第一个合法 token；无法唯一确定则 Host tools 再问一次。禁止写死 `720p` / `1080p` |
| `duration` | **本段** Duration 秒数（extract 拆出来的段长），不是 info_card 的 12 / 25 / 45 |

规格写入 Session 后，后续首帧 / 成片**静默继承**仍合法的 `SessionRatio` / `SessionVideoResolution`；用户本句写了新值才改。角色图 / 场景图的 `aspectRatio` 仍固定 `9:16`，不受本表影响。

info_card 规格题**必须**走 Host tools，**每题全部可选项都要进 `options`**（语言四档 `English` / `Spanish` / `Arabic` / `Custom`；画幅六档 `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16`；时长三档 `<15s` / `15s-30s` / `30s-1min`；分辨率两档 `720p` / `1080p`）。禁止从 `<available_models>` 抄 `ratios`，禁止因缺表 / `ratios=fixed` 省略画幅题，禁止 Chat 只打印一档（`Language: English` / `Aspect ratio: 9:16` / `Duration: 30s-1min` / `Resolution: 720p`）。禁止在正文里写 default / 预选。

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

prompt 正文只用 `<<<image_n>>>` / `<<<video_n>>>`：小写、从 `1` 起，与 `image_url(s)` / `video_url(s)` 顺序一一对应。每个占位必须写清角色。历史里若烂成 `<<>>`，按当前绑定重写成完整占位后再调用。禁止空占位。

### 串行

run_prompt **禁止**与 `generate_image` / `generate_video` 同拍并行。角色+场景成图、首帧 ×N、Video 2…N 仍按本文件 §并行。

### 含糊 / 纯确认

**只**适用于已发出且仍有效的 **Host tools** 提问：`nice` / 无可执行新指令 → 重发同一提问，不要 Advance。
**不适用**于卖点三段、也不适用于商品控件确认。这两处 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续 = **已确认**，必须 Advance。

---

## 为什么要灵活

用户不会只走一条固定生产线。他们可能跳过任意中间产物、自带任意素材、从任意点直奔更后的目标、中途改主意、或对任意前序不满意。本 skill 用**阶段图 + 五个算子**处理这些情况；下面的「不要场景 / 自带角色图 / script 后出视频」只是算子的实例，**不是**封闭清单。遇到未写出的说法，先归到某个算子，再往下走，不要因为「没写过这个例子」而卡住。

---

## 阶段图

默认顺序（只执行 **enabled** 的阶段）：

```text
intent → product → selling_analysis → info_card → character → scene → ref_video → script → extract → first_frame → video → merge
```

| 阶段 | 默认 | 用户可见产物 | 说明 |
|------|------|--------------|------|
| `intent` | `with-questions` 则跑（恰好 1 题）；`no-questions` 则 skip | 无 | 指令式触发，见 §开场意图。恰好 1 题 = 广告视频内容方向，恰好 3 个按指令现写的选项 |
| `product` | 必跑 | 商品卡 / brief | 三路互斥入口，见 §阶段目的 |
| `selling_analysis` | 必跑 | 对话中的卖点 markdown（带引导 / 确认句） | 商品确认后 run_prompt，按 `selling-analysis-prompt.md` 贴三段并停住；用户确认后 `content` 全文 = 下游 `SellingPoint` |
| `info_card` | 规格未齐则跑 | 规格提问 | 语言 / 画幅 / 时长 / 分辨率（无卖点字段） |
| `character` | run | 角色 Prompt + 成图 | 可选 |
| `scene` | run | 场景 Prompt + 成图 | 可选 |
| `ref_video` | skip | 用户自带参考视频 | 可选；默认 skip；Provide 才绑定 |
| `script` | 必有（生成或自供） | 分镜表 | 成片前必须有一份可用 script |
| `extract` | script 之后自动 | 无（纯内存） | 内部阶段，不调 LLM |
| `first_frame` | run | 各段首帧 | 可选 |
| `video` | 必跑才能成片 | 分段成片 | |
| `merge` | 仅 N≥2 | 成片 | N=1 则 skip |

每阶段状态：`pending` | `run` | `skip` | `provided` | `done` | `invalidated`。
**enabled** = 不是 `skip`，且（`pending`/`run`/`invalidated` 需要执行，或 `provided` 只需绑定不再生成）。
`ref_video` 开场默认 **`skip`**。用户自带视频则 Provide。

Jump 分类直接读上表：说明里写「可选」的是可选可见；写「无 / 纯内存 / 内部」的是内部；卖点分析等待 / 规格提问是闸门。`intent` 在 `IntentQuestions=true` 时必须先问完，不是 Jump 可跳过闸门。不要再为某条跳转另写规则。

**硬底线**（不能整链跳过）：必须有商品身份（链接 / 图 / 描述之一）；要出视频必须有 script（生成或自供）以及至少一块视觉参考（首帧、角色图或产品图之一）。其它阶段都可以 skip 或 provided。

`IntentQuestions`：仅从本任务**首轮**字面量读取。出现 `no-questions` → `false`（跳过问询）；出现 `with-questions` 或两者都未出现 → `true`（默认问 1 题）。首轮冻结，禁止后续轮次改写。`false` → `intent = skip`，`IntentDone=true`，同轮进 `product`。卖点分析 / 规格提问仍照常。

---

## 五个算子（HARD — 任意阶段、任意轮次）

从用户这句话里识别**一个主算子**（一条消息可同时 Provide 多件素材）。然后立刻 Advance。

### 1. Skip(S)

用户不要某阶段的产物（「不要场景」「别生成首帧」「不用参考视频」「不要出镜人物」「跳过合成直接看分段」……）。

- `Stage[S] = skip`。不生成、不展示、不等该步选项。
- 下游按 `slot-adaptation.md` **缺了就省略或回退到次近素材**，禁止为凑槽复制节点。
- 若当前正停在 S 的等待提问，马上离开。

### 2. Provide(S, asset)

用户交出该阶段产物（上传、粘贴、产物 id……）。**提供优先于 Skip。**

- 绑定到 S 的锚点，`Stage[S] = provided`，不生成。
- 模特图、场景图、声音参考 **禁止**当成商品主图或产品页链接。
- 任意轮次都可 Provide；中途补交则改状态并继续。

### 3. Jump(T)

用户要的是 **T 的产物**，不是把路上每一站都做完（「直接出视频」「先出首帧」「先出分镜」「不要中间结果」「不生成角色，直接出首帧」……）。

1. 从这句话认出目标 T。只说「直接做完 / 出视频」→ `T = video`（N≥2 时含 `merge`）。点名首帧 → `T = first_frame`。点名分镜 → `T = script`。
2. 对**当前点到 T 之间**（不含 T）的每个阶段 S，按下表分类，**禁止**按具体阶段名写死例外：

| S 对 T 的关系 | 怎么处理 |
|---------------|----------|
| 已 `done` / `provided` | 沿用 |
| **硬前置**：缺少 S 的产物会违反硬底线，或 T 按 `slot-adaptation.md` 没有任何次近回退可用 | 必须有产物（生成或 Provide） |
| **内部阶段**（无用户可见产物，只为硬前置或 T 服务） | 静默跑 |
| **闸门**（卖点分析 / 规格提问）：值可草稿或默认 | 写入草稿或默认，不停 |
| **可选可见**，且用户本句没点名要这份产物 | `Skip(S)` |

硬底线仍是：商品身份；出片前必须有 script；至少一块视觉（首帧 / 角色图 / 产品图任一即可）。因此 script 是 `first_frame` / `video` 的硬前置；角色、场景、首帧**不是**成片的硬前置；角色、场景**不是**首帧的硬前置（回退到产品图）。

`IntentQuestions=true` 且内容方向题未发出或未答 → **禁止**把问询当闸门跳过；先问完再 FastForward。`parse_product_info` 控件未收到 §商品确认信号 → 商品身份未成立，禁止 Jump 越过去 `display_product_info` 或更后阶段。

3. 用户本句点名要保留的中间产物 → 该阶段不 Skip。点当前等待提问的主选项 → **不是** Jump，按普通继续做当前阶段。
4. 然后 `FastForwardTo = T`：只跑仍 enabled 的阶段，不发中间等待提问；停在 T 的完成态。
5. 只说「按当前计划做完、中间别停」而**没有**点名跳过中间产物 → 仅 FastForward，不改 skip/run。

### 4. Rollback(S)

用户不满意某前序（提问选项 `Revise …` 或自然语言点名 script / 角色 / 场景 / 参考 / 首帧 / 卖点 / 规格 / 成片……）。未点名时，按语义落到**最早仍影响当前问题的阶段**。

- `Stage[S] = invalidated`；S **之后**全部 `invalidated`（旧产物 id 可留，状态禁止再引用）。作废后的下游**恢复为回退前的计划**（`run` / `skip` / `provided` 以回退前为准），不要把可选阶段改成 skip。
- 用这条建议改输入 / 规格；只说「重做」则同参重跑。
- **禁止 AutoRun**：重做完 S 后，若 S 有用户可见产物 → **停住**（卖点：贴三段等自由回复；其它：状态句 + 宿主提问）。不要顺跑 extract / first_frame / video / merge。内部阶段（如 extract）只在用户选了等待提问上的继续之后才跑。
- `first_frame` 回退前是 `run` 则重做链路里仍是 `run`，禁止因回溯而 skip。

### 5. Reroute(S, mode)

同一阶段换做法（等用户传参考 → 改为不参考；brief 改走链接解析……）。

- 更新该阶段模式，作废只依赖旧模式的下游（通常从该阶段起 invalidated）。
- 立刻按新模式执行或等待新输入。

**冲突**：Provide > Skip > 默认 run。Jump 不取消已 Provide 的素材。Rollback 之后以最新 Stage 计划为准。

---

## 不得卡住（HARD）

每一次 assistant action 必须是下面之一（自上而下，先匹配的优先；禁止用「调用平台能力」压过前面的等待）：

1. 开场问询（仅 `IntentQuestions=true` 且内容方向题尚未真发出）：同轮对 Host tools 真调用一次。标题 = 短题名；问句 = **恰好一句**；`options` = **恰好 3 条**且**第一条为推荐默认**。无真调用、把 3 条方向写成 Chat 编号列表、或问句为空 / 把占位句当成唯一问句 = 本步失败。**这一拍只能发这一次 Host tools**，禁止同拍再调任何 Buzzy MCP tool（含 `create_project` / `parse_product_info` / `display_product_info` / run_prompt / `generate_image / generate_video`）。`IntentQuestions=false` 时本条不适用，直接进 `product`
2. `IntentQuestions=true` 且内容方向题**已经**对 Host tools 真发出，且用户还没有对本题作答 → **停住**。禁止 `parse_product_info` / `display_product_info` / 其它流水线 tool。Host tools 返回若**没有**用户选中的 option id/label / Other 文本，只表示选择框已发出，**不是**已答，禁止因此 Advance。`IntentDone` 在用户作答前必须保持 `false`。返回里已有选中方向 → 本条不适用，收下并 `IntentDone=true`
3. 停在已打开的 `parse_product_info` 商品编辑控件上，等用户确认（见 §商品确认信号）。此期间禁止 `display_product_info`，禁止 Host tools 问是否继续
4. 停在**已经发出且仍有效**的其它宿主提问上，等用户选择
5. 停在已贴进对话的卖点三段正文上，等用户自由回复（卖点闸门不走 Host tools）
6. 卖点已确认、规格未齐、且 §info_card 尚未对 Host tools 真发出（Chat 编号单值 / 只写一档不算）：同轮真调用一次，四题每题全部档位进 `options`，然后停住。禁止进 `character` / `generate_image`
7. 调用平台能力，产出下一件产物或下一轮宿主提问（仅当 1–6 都不适用）

禁止空回复且无任何能力调用、也无宿主提问、也未贴出卖点正文、也未打开商品控件——**但**开场问询 / 其它 Host tools 题已经发出、用户尚未作答时，**停住且不再调任何 tool 是正确终点**（不要为了避开「空回复」去调 `parse_product_info`）。伪调用文本已写出但没有真调用 → 重发真调用。
能力返回后的 continuation 必须 Advance，不需要用户再发一句——**例外（必须停住）**：① Host tools 开场问询 / 规格提问已发出、用户尚未作答；② `parse_product_info` 返回只表示控件已打开，不要 Advance 到 `display_product_info`。Advance 碰到用户可见产物且非 FastForward 时发等待并**停住**（Rollback 重做后同此）。卖点等待 = 引导句 + markdown + 确认句，不是 Host tools。
贴过卖点正文 **不是** 已确认：run_prompt 已返回但本会话还没按 `selling-analysis-prompt.md` 贴出三段 → 立刻贴三段并停住，禁止只写 status、禁止只贴 `content` 不说明这是卖点、禁止空结束。
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

过渡态（`display_product_info` 刚跑完 / brief 刚齐 / 卖点等待刚被确认 / 仅第一段成片）**禁止停驻**。`parse_product_info` 刚返回 **必须停驻**，不是过渡态。Host tools 开场问询刚发出、用户尚未作答 **必须停驻**，不是过渡态，禁止 Advance 到 `product`。
**商品确认后的同一 continuation（HARD）**：先 `display_product_info`（该次确认最多一次）→ 立刻 `selling_analysis`（run_prompt + 贴三段）→ 停住。禁止在 display_product_info 之前跑卖点。禁止只 display_product_info 就结束。卖点「尚未跑完」= 本会话还没贴出三段。未在 Jump 越过时禁止先出规格提问。卖点分析普通模式：run_prompt 返回后**同一 continuation** 必须按 `selling-analysis-prompt.md` 贴出三段，然后**停住**（只写 status、只贴 `content` 不说明这是卖点、或调 Host tools Continue/Revise = 本步失败）。用户从该等待确认后、规格未齐 → 立刻进入 `info_card`。角色/场景刚齐 → 立刻发 script 等待提问。
正在 Jump 越过这些闸门 / 可选阶段 → 按 §Jump 写入默认或 Skip，不要被本段拦截。问询未完成或商品控件未确认时，Jump 也不得越过这两道等待。

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
- `IntentQuestions=false` 时：未问到的项用默认（可选阶段 `run`；`ref_video=skip`；画风 `authentic handheld UGC`）。卖点 / 规格仍跑。

---

## 每 turn

自上而下只取一条：

0. 伪调用无真执行 → 重发。
1. `IntentQuestions=true` 且内容方向题尚未对 Host tools 真发出 → **只发这一题**，然后**停住**。禁止同拍 `create_project` / `parse_product_info` / `display_product_info` / 其它流水线 tool。首轮带了链接 / 图也先问询，入口只记账。编号列表不算已问。
2. `IntentQuestions=true` 且内容方向题已对 Host tools 真发出，且用户还没有对本题作答 → **停住**。返回里没有选中的 option / Other 文本 = 未答。禁止 `parse_product_info`。禁止把 `IntentDone` 置 `true`。返回或用户下一句已有方向 → 收下，`IntentDone=true`，再进 `product`。
3. `parse_product_info` 已打开，且本会话还没有 §商品确认信号 → **停住**。禁止 `display_product_info`。禁止 Host tools 问要不要继续。tool 返回里的商品字段是刮取草稿，不是确认。
4. 某次能力调用已发出、**尚无结果** → 等结果，不要叠新生成调用。`generate_image` / `generate_video` 返回 `task_id` = **尚无结果**：本 continuation 必须 `get_task` 轮询到终态，`get_task` 不算叠生成。已返回终态 / 同步 tool 已返回（**不含** `parse_product_info`，**不含** Host tools 开场问询 / 规格提问）→ 必须 continuation，禁止干等用户再发一句。卖点 run_prompt 返回后按 `selling-analysis-prompt.md` 贴三段并停住是 mandatory，不算叠生成。
5. 已有 §商品确认信号，且该次确认还没跑过 `display_product_info` → 本 continuation **先** `display_product_info`，**立刻** `selling_analysis`（run_prompt + 贴三段）。禁止只 display_product_info 就停。`display_product_info` 已按该次确认跑完：卖点三段未贴 → 只跑卖点（未调用则调用；已返回则贴三段并停住）。三段已贴仍在等用户 → 停住，不要顺跑规格提问。卖点已确认但规格未出 → **只**对 Host tools 发 §info_card 四题（每题全部档位进 `options`）。Chat 打印 `1. Language: English` 这种单值不算已出，必须立刻改成四项 × 全部档位。无链有图且 `ProductBrief` 已齐、卖点三段未贴 → 只跑卖点。**本条在开场题未答完时不适用。**
6. 第一段成片已成、N≥2、其余段尚未全部发起且非等待中 → 发齐剩余段。
7. 本轮能识别算子 → 执行算子。停在某次等待提问时，用户点名的是**更后阶段的产物** → 按 Jump(T)，不要当成确认当前主选项。若 `IntentQuestions=true` 且内容方向题未发出或未答：**只记账**，**禁止**进 `product` / `parse_product_info`；题未发出则本轮仍只问这一题，题已发出则停住等答。`IntentQuestions=false` → 不要进本条问询分支。
8. `IntentQuestions=true` 且 `IntentDone=false` → 题未发出则只发这一题并停；题已发出未答则停住，**不要**进 `product`。必须真调用 Host tools，问句含内容方向；编号列表不算已问。用户已答 → `IntentDone=true`，再进 `product`。`IntentQuestions=false` → 进 `product`。
9. FastForward 且上一步已齐 → 只跑下一 enabled 阶段，直到目标 T。问询未完成（题未发出或未答）或商品控件未确认 → **不要**走本条。Rollback 重做刚完成 → **不要**走本条。
10. 否则按当前阶段目的推进。仅当停在 **Host tools** 提问上且用户只回 `nice` / 无可执行新指令 → 重发同一提问，不要空回复，不要 Advance。卖点三段或商品控件上的 `looks good` / `continue` / `ok` **不是**本条，按已确认处理。

---

## 阶段目的（该跑时才读对应 reference）

链隔离：`UgcAdsActive` 为真时只按本文件。启动：`/ugc-ads`、UGC ad、跳步 / 自供 / 回退式 UGC，或本链已有入口 / 问询 / 相位。
状态从 history 每轮重推。禁止拿 `tvc-ads` / `trending-search` 正文跑本链。

### `product`

**前置**：本会话还没有 `create_project` 返回的 id → 先 `create_project({ name })`，再走下面三路。问询未完成时不要进本阶段。

**商品确认信号（HARD）**：`parse_product_info` 返回 ≠ 确认。确认 = 下面任一：消息含 `Confirmed Product Info`；用户明确确认/继续该商品（`Confirm` / `Continue` / `looks good` / `ok` / 确认 / 继续）。不要只认「首行字面量」，也不要把刮取字段当成已确认。

三路互斥：

1. 有产品详情页链接 → `parse_product_info({ projectId, productLink })` 打开编辑控件。**返回值不是确认**：同一 continuation **禁止** `display_product_info`，**停住**等 §商品确认信号（禁止 Host tools 问是否继续）→ 从确认消息解析 `Title:` / `Description:` / `Main Image:` / 全部 `Images:`（没有这些前缀则用用户确认的标题/描述/图）→ `display_product_info({ projectId, title, description, images: [main, ...others] })`（每个确认事件最多一次）→ **同一 continuation** 立刻进入 `selling_analysis`
2. 无链接、有商品图 → 记下商品图 id；缺用户文则用 `ugc_ads_product_brief` 写 `ProductBrief`，有实质用户文则整理后写入 `ProductBrief` → 进入 `selling_analysis`。不要走解析。进入 `selling_analysis` 前同样必须已有 `projectId`
3. 无链接、无图 → `parse_product_info({ projectId })`（**不传** `productLink`）打开空编辑控件，用户填 title / description / 上传图片。**不要**再用 Host tools 收集这三项。同一 continuation **禁止** `display_product_info`。停住等 §商品确认信号，再按路径 1 同样解析并 `display_product_info`。无 iframe 宿主才用 Host tools 收集标题/描述/图。

`imageUrls:` 且 host 含 `buzzy.now`、path 含 `/file-service/`、图片后缀 → 商品图，不是产品页。
商品已确认展示 = `display_product_info` 已按该次确认跑完，不是 `parse_product_info` 刚返回。卖点三段未贴 → 立刻 `selling_analysis`；**禁止**先出规格提问。

parse / 控件确认后的 `ProductBrief`：

```text
Product Name: {ConfirmedProductTitle}

Product Description:
{ConfirmedProductDescription}
```

### `selling_analysis`

见 `selling-analysis-prompt.md`。前置：产品信息已确认。
`run_prompt(prompt_key="ugc_ads_selling_analysis", projectId=项目 id, instruction=卖点分析输入)` **恰好 1 次**（已有 brief 只当输入，**不要**再用 `prompt_key="ugc_ads_product_brief"` 调 `run_prompt`）。成功字段是 `content` + `name`（`name` 必须是 `Selling Point Analysis`）。商品图 URL 有才加（确认消息 `Main Image:` / `Images:`，或 `display_product_info` 返回的图地址）。还没有 `projectId` 就先 `create_project`。
**HARD**：`恰好 1 次` 只约束 run_prompt。同一 continuation 必须按 `selling-analysis-prompt.md` 贴三段：`Here are the product selling points:` + `items[].content` 原文 markdown + `Confirm to continue, or tell me what you'd like to change.`（禁止只写 `Your selling point analysis is ready.`，禁止 code fence，禁止只贴正文不说明这是卖点）。然后**停住**等用户自由回复。**不要**调 Host tools Continue/Revise。缺这三段 = 卡住 / 本步失败。不要顺跑规格提问。用户回复 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续，或改了文案后接受 → `SellingPoint` = `content` 全文（不含引导句 / 确认句；用户改了文案则以用户稿为准）。规格提问不再收卖点。

### `info_card`

前置：`SellingPoint` 已写入。
**必须**对 Host tools 真调用一次（能一次提多题就一次提完）。标题 `Set up your UGC Video`。assistant 正文最多一句：`Choose the language and set the video specs.`
**HARD — 每项必须列出全部可选项**：Language / Aspect ratio / Duration / Resolution 四项都要出现，**每一项都必须把下表该行全部档位写全**。Host tools：该题 `options` = 该行全部档位，禁止只塞一档。禁止在正文、问句、选项旁写 default / 预选 / Recommended / 当前设置。
仅当三个 Host tools 名字都没有、只能用正文时：用编号列表，但**每行必须是 `标签: 档1 / 档2 / …`**，形状如下（禁止改成单值）：

```text
Choose the language and set the video specs.
1. Language: English / Spanish / Arabic / Custom
2. Aspect ratio: 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16
3. Duration: <15s / 15s-30s / 30s-1min
4. Resolution: 720p / 1080p
```

下面任一写法 = 本步失败，必须立刻改成「四项 × 全部档位」（不要继续 character / 成图）：

- 只写一档：`1. Language: English` / `2. Aspect ratio: 9:16` / `3. Duration: 30s-1min` / `4. Resolution: 720p`
- 把四项印成「当前设置」而不给其它档
- 伪调用文本、或缺任一题、或缺任一题的任一档

```text
AskQuestion
title: Set up your UGC Video
questions:
  - id: language
    prompt: Language
    options:
      - id: english
        label: English
      - id: spanish
        label: Spanish
      - id: arabic
        label: Arabic
      - id: custom
        label: Custom
  - id: aspect_ratio
    prompt: Aspect ratio
    options:
      - id: "21:9"
        label: 21:9
      - id: "16:9"
        label: 16:9
      - id: "4:3"
        label: 4:3
      - id: "1:1"
        label: 1:1
      - id: "3:4"
        label: 3:4
      - id: "9:16"
        label: 9:16
  - id: duration
    prompt: Duration
    options:
      - id: under_15
        label: <15s
      - id: 15_to_30
        label: 15s-30s
      - id: 30_to_1min
        label: 30s-1min
  - id: resolution
    prompt: Resolution
    options:
      - id: 720p
        label: 720p
      - id: 1080p
        label: 1080p
```

**固定顺序 HARD**（四题都要出现，每题 options 必须传齐，禁止省略档位）：

| 顺序 | 标签 | `name` | 全部可选项（必须全部列出） |
|------|------|--------|---------------------------|
| 1 | Language | `language` | `English` / `Spanish` / `Arabic` / `Custom` |
| 2 | Aspect Ratio | `aspectRatio` | `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| 3 | Duration | `duration` | `<15s` / `15s-30s` / `30s-1min` |
| 4 | Resolution | `resolution` | `720p` / `1080p` |

发出后**停住**等用户点选。Host tools 返回若没有各题选中项 = 未答，禁止 Advance。只写一档的编号列表不算已问。
整链一次。用户**本句已明确写出**语言 + 画幅 + 时长（+ 分辨率）且要求开跑 → 写入 Session 后可不再停。只打印一档 / 用户未逐项选定 ≠ 已给齐。`Custom` → 口播按 English。时长写入分镜：`<15s` → 12s；`15s-30s` → 25s；`30s-1min` → 45s。Jump 越过本闸且用户未点名规格 → 内部写入 `English` / `9:16` / `30s-1min` / `720p`，禁止把这四档印给用户当选项清单。成片调用时若有模型表，再按 §运行时填参收敛一次：用户选的 token 不在该行 → 改用该行第一个合法值，或 Host tools 再问一次。无模型表则按用户所选原样传。

### `character` / `scene`

见 `character-scene-image-prompt.md`。该跑且无自供图：同轮先写齐 `ScenePromptBody` / `CharacterPromptBody`（角色背景槽必须对齐场景 Prompt 正文；正文不上 Chat），再**并发**成图。角色成图 **禁止**挂场景图当参考。`generate_image.model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文。角色图 / 场景图 `generate_image.aspectRatio` **固定 `9:16`**，禁止跟 `SessionRatio` / 规格提问。有则追加 `Character Role` / `Visual Tone`。skip → 对应 Description 用 `(none)`。provided → 只绑定。每个 `generate_image` 必须 `get_task` **阻塞轮询到成功** 才算完成。成功只在正文写状态句。
成功后下一 enabled 阶段通常是 `script`。发 script 等待提问。

### `ref_video`

可选。默认 `skip`。仅当用户 Provide 参考视频时变为 `provided`。

- 默认 skip → 无参考；角色/场景齐后立刻发 script 等待提问
- provided（上传、粘贴、产物 id、`Use this video` + URL）→ 绑定，不要再造一份视频，再发 script 等待提问
- 用户说不用参考 → 保持 skip

### `script`

有用户分镜 → 整理成 9 列管道表，并按 `script-table-format.md` 把每一行转成分镜卡片贴进对话。否则见 `storyboard-script-prompt.md`。缺角色/场景/参考写 `(none)`。
**HARD**：run_prompt **恰好 1 次**；成功字段是 `content` + `name`（`name` 必须是 `[Script] UGC Storyboard`）。必挂商品图 URL，角色图 / 场景图 / 参考视频 URL 有则加。同一 continuation 必须按「对话分镜卡片」贴进对话（禁止把 `|` 管道表贴进 Chat；禁止 code fence）。
非 9 列 / 缺 GFM 分隔行 / 缺 `content` → 才允许同 key 重试。行数目标是 `round(时长秒 / 30 × 8)`（12s→3、25s→7、45s→12），少于目标也照收，**不要**因行数重试。普通模式（含 Rollback 重做 script）→ 卡片在对话里可见后发 Host tools Continue/Revise（引导 `Review the storyboard, then continue.`），**禁止**同轮 `extract` / 首帧 / 成片。FastForward：贴卡片后立刻 `extract`。

### `extract`

内部。按 `script-table-format.md` 拆段（每段 ≤15s 且 ≤3 镜）。超限 → 请改 script，不要硬出片。通过后写入 `ExtractVideoContents[]`。不调 LLM。仅当用户已确认离开 script（等待提问选继续）或 FastForward 时才进入本阶段。完成后：`first_frame` 仍 enabled → 进 `first_frame`；否则进 `video`。禁止把已 `invalidated` 的旧首帧当成「用户已提供首帧」。

### `first_frame`

skip 或各段已 **provided**（用户本轮指定的首帧，不是已 `invalidated` 的旧图）→ 不生成。否则 agent 按 `first-frame-prompt.md` 变槽**直接写出**各段首帧 Prompt（禁止 run_prompt），再并发 ×N 成图。`generate_image.model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文。每张图提交后必须 `get_task` **阻塞轮询到成功**，记下素材 URL；全部终态前禁止发等待提问。无任何可用图 → 问补图。成功后按 §双通道发等待提问并停住（FastForward 除外）。Rollback 不得把本阶段改成 skip。

### `video` / `merge`

见 `video-generate-prompt.md`。每段生成一段新片子（不要用参考视频当成片输入）。`generate_video.model` = Video 表 **Seedance 2.0 Fast** 行的 `model` 列原文；`aspectRatio` / `resolution` 按 §运行时填参只传该行合法 token（无模型表则用 Session 原样）。Video 1 先发，`get_task` **阻塞轮询到成功** 后再发 2…N（后续段必须参照 Video 1）。N≥2 同轮发齐后，每一段都必须 `get_task` 轮询到终态。成片正文按 extract **改写 Timeline**，禁止整段粘 extract。普通模式 N≥2 等用户合成；FastForward 则自动合成（不配 BGM）。合成时 `merge_videos` 挂各段成片 URL，禁止传 `nodeIds`。N=1 禁止合成。Rollback 重做 video 后同样停在对应等待提问，不要自动 merge。

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

**通用提问规则**：第 1 条选项 = 下一 enabled 主路径；另给 Skip 或 Rollback 出口；只 Revise 实际存在的产物；FastForward 不发中间等待提问；Rollback 重做后必须发等待提问。

填空示例（按当前槽改写，非封闭）：

| 情境 | 状态句 | 提问引导 |
|------|--------|----------|
| 开场问询 | （可省略状态句） | Host tools：标题=短题名；问句=`{问句}`；恰好 3 个方向进 `options`，禁止 Chat 编号列表。发出后停住，未答前禁止 `parse_product_info` |
| 首次 / 重生成 script | `Here is the storyboard script:` + 每镜一张卡片（9 列表头字段；禁止贴 `|` 表）；可附 `Your storyboard script is ready.` / `Your updated storyboard script is ready.` | `Review the storyboard, then continue.` |
| 角色场景刚齐 | `Your character and scene references are ready.` | `Review the references, then generate the storyboard script.` |
| 首帧 | `Your first frames are ready.` | `Review alignment, then generate all videos.` |
| 待合成 | `Your UGC video segments are ready.` | `Review the segments, then merge them.` |
| 卖点分析 | `Here are the product selling points:` + `content` 原文 markdown + `Confirm to continue, or tell me what you'd like to change.`（禁止只写 status、禁止只贴正文） | **不要** Host tools；停住等自由回复 |
| parse_product_info 控件已打开 | （可省略状态句；不要复述商品字段；不要预告 display_product_info） | **不要** Host tools；**不要** `display_product_info`；停住等 §商品确认信号 |
| 卖点已确认、规格未齐 | （正文最多一句 `Choose the language and set the video specs.`；禁止把四项印成单值「当前设置」） | Host tools 真调用：四题，每题全部可选项进 `options`（见 §info_card）。编号单值 / 只写一档 = 没问，必须重发；无 Host tools 时正文必须列出每项全部档位 |
| Video 1 续跑 | `The first UGC video segment is ready. Generating the remaining segments now.` | （禁止提问） |
| 单段 / 合成结束 | `Your UGC video is ready.` / `Your full UGC ad video is ready.` | （禁止提问引导） |

产物 `title`（无产物不编造）：`[Product] Image` / `[Avatar] Model` / `[Scene] Upload {n}` / `[Product] Brief` / `Selling Point Analysis` / `Character Prompt` / `Scene Prompt` / `[Character] Creator` / `[Scene] {短名}` / `[Script] UGC Storyboard` / `[First Frame] Video {i}` / `UGC Video {i}`

---

## 并行

问询一题一轮：发出后本轮结束，未答前 continuation 也不得进 `product`。该跑的 character+scene Prompt 同轮先写齐再并发成图（角色不挂场景图）。该跑的首帧 ×N 同轮并发。Video 2…N 同轮发齐。run_prompt 不与 `generate_image / generate_video` 同拍并行。FastForward / Skip 后的下一阶段在 continuation 立刻开始（问询未答完除外）。Rollback 重做的可见阶段在 continuation 只发等待（卖点：贴三段等自由回复；其它：宿主提问），不顺跑。
