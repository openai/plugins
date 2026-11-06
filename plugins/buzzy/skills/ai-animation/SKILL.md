---
name: ai-animation
description: "Always use this skill to make a flexible long-form animation / animated micro-film / multi-chapter storyboard-to-video. Must trigger for /ai-animation, ai-animation, long animation, animated feature, animated micro-film, or when an ai-animation run is already in progress (intent answers, style, specs, script, character sheets, preview images, video prompts, clips, BGM merge) or the user skips a step, supplies an asset, jumps ahead, or revises an earlier step without restarting. Even a vague \"make a long animation\" or \"help me make an animated feature\" must start this skill. After the first instruction, ask 2 professional direction questions grounded in that brief before the formal pipeline. Preset durations 15s / 15-30s / 30-1min (default 15s) or a typed total such as 180s / 300s."
source: "buzzy"
risk: safe
scope: mcp
allowed-tools: |
  Buzzy MCP tools
  - create_project
  - run_prompt
  - generate_image
  - generate_video
  - get_task
  - merge_videos
  - choose_skill_asset

  Host tools — not part of this MCP server
  - AskQuestion
  - ask_question
  - AskUserQuestion
---

# AI Animation Orchestrator

本链自包含。查阅本 skill 文件只用完整前缀 `skills/ai-animation/reference/`。
**怎么调平台能力、填哪些参数，对照各 tool 自己的声明**；本文件只写目的、产物和硬底线。
本文件是编排器，不是 run_prompt 的填空稿，不要改写成 `user_lang`，不要压成短 brief。

**HARD — allowed-tools 分类**：`Buzzy MCP tools` 是本 MCP 服务注册的平台 tool，经 Buzzy MCP `tools/call`。`Host tools — not part of this MCP server` 是宿主内置提问 tool，**不是** Buzzy MCP tool，也不走 `load_workflow` / ExecuteTools。Cursor 用 `AskQuestion`，Claude 用 `AskUserQuestion` / `ask_question`，Codex 用同类。选择题必须调 Host tools 里当前可用的那个，禁止因为「不在 Buzzy MCP tools 列表里」就改成编号纯文本。
**HARD — create_project**：进入任何需要 `projectId` / `project_id` 的 Buzzy MCP tool 之前，必须先调 `create_project` 拿到真实 id。本会话只创建一次，后续全程复用。workflow tool（run_prompt / `merge_videos`）传 `projectId`；`generate_image` / `generate_video` 传 `project_id`。禁止编造 id，禁止省略，禁止因为 generate_image / generate_video 写了「可自动建项目」就跳过。`create_project` 的入参是 `name`（可读项目名），不要把 catalog 的 `name` 或 `workflow` 抄过来。`choose_skill_asset` **不需要** `projectId` / `project_id`。Host tools 开场问询 / 规格提问那一拍、以及风格卡那一拍，仍禁止同拍调 `create_project`。风格卡只调 `choose_skill_asset`。问询完成且即将调**需要项目 id** 的 Buzzy tool 时若还没有 id，必须先 `create_project`。Jump / FastForward 到更后阶段同此：还没有 id 就先创建，再调带项目字段的 tool。

**HARD — 宿主提问**：等人选择或确认时，必须对 Host tools 里当前可用名字真调用一次。选项只进提问 tool 的 `options`，且**该题全部可选项必须传齐**（禁止只塞一档）。禁止用 `1.` `2.` `3.` 编号列表、bullet、`Recommended:` 前缀段落作为用户可见选项——那样写 = 本步失败，必须立刻改成真调用。assistant 正文最多一句问句或状态句，**不要复述选项**。不要自己造第 4 个 `Other` 选项：Cursor `AskQuestion` 自带 Other 自由输入。仅当 `tools/list` 里 `AskQuestion` / `ask_question` / `AskUserQuestion` 三个名字都没有时，才允许编号列表，并写明本宿主没有选择框；**规格题的编号列表必须每行列出该字段全部档位**。Cursor 有 `AskQuestion`，禁止走这条。媒体产物就绪只用 assistant 正文状态句。伪调用、编号单值、或缺档都算没发出提问。
**例外 — 风格库**：`choose_skill_asset` 打开风格单选控件。必传 `style_template: "animation"` + `title: "Styles"`。返回值（`items`）只表示控件已打开，**不是**确认。有控件 → **停住**等 `Confirmed Styles info`；禁止同拍 Host tools。无控件宿主才把 `items[].name` 塞进 Host tools。确认前禁止进 `settings`。
**例外 — run_prompt `content`**：剧本 Markdown 与各段 Video Prompt **必须原文贴进对话**（禁止 code fence），不受「正文最多一句」限制。禁止说 on the canvas。贴完后仍发对应 Host tools 等待提问（FastForward / AutoRun 除外）。

| 何时读 | 文件 |
|--------|------|
| 开场组题（默认 2 题） | `intent-questions.md` |
| 风格卡 / choose_skill_asset | `style-prompt.md` |
| 下游缺输入时怎么组槽 | `slot-adaptation.md` |
| 任意状态句 / 提问引导 | 本文件 §双通道文案 |
| 填 `generate_image` / `generate_video` 参数 | 本文件 §运行时填参 |
| 跑到该步且未跳过时 | `script-prompt.md` / `assets-prompt.md` / `frames-prompt.md` / `video-prompts.md` / `clips-merge.md` |

本链使用 `run_prompt`，按阶段选择以下 `prompt_key`：
`long_video_step1_script` / `long_video_step3_video_prompts`。
`long_video_step2_frames` 主路径不用。禁止用 STEP2 写成片词，禁止为出预览图去补 STEP2。
`long_video_step3_video_prompts` 对外仍是一次调用。Agent **必须**传 `instruction.script_markdown` + 规格（`duration_sec` / `ratio` / `model`）。**禁止**传 `frames[]`。Host 内部跑 STEP2，细镜全文零删减进 `records[]`，与这份剧本并行喂给 Gemini。写词规则是**细镜主参考、剧本辅参考**：画面先写细镜；剧本补缺口；同一事实两边否定才选边（台词→剧本，站位/运镜→细镜）。条数对不齐不失败。Gemini **只**写 `groups[]`。Host 校验该章剧本镜头行引号对白后按组拆 `items[]`。禁止挂预览图。Agent **必须**把每段 `content` 全文打印进 Chat（一段一块 `### Video Prompt {i}`）。还没打印齐 1…N = 本步未完成，禁止出片。
预览图是展示件，只从剧本文各章第一条镜头行出图，**不**用 `frames[].prompt`。可 Skip。进入 `frames` 时先只发预览图 `generate_image`×N（与资产图同一套：本拍禁止夹 STEP3），全部 `get_task` 终态后一次状态句，**下一拍**再调一次 STEP3。禁止 `defer_step2_thinking`。本批预览图未全部终态 → 禁止状态句、禁止芯片式提问、禁止 STEP3。

禁止短路径、读其它 skill、把 YAML 当自由 prompt。禁止把 `*_SPEC` / YAML 正文贴进 `instruction`。

用户可见文案 **固定 English**。禁止出现 `on the canvas`。`SessionScriptLanguage` / `user_lang` 只约束剧本可读正文、对白、分镜描述。
参考素材**一律走 URL 字段**（`image_url` / `image_urls` / `video_url` / `video_urls`，以各 tool 声明为准），适用于 `generate_image` / `generate_video` / run_prompt / `merge_videos`。**禁止传 `nodeIds`**。STEP1 必须把用户上传的参考图 / 视频放进 `image_urls` / `video_urls`（有才加）；**禁止**把风格图 URL 放进这两个字段。已绑定风格图时，`assets` 的 `generate_image` 可用 `image_urls` 只传这一张风格图。预览图不是成片参考。

角色 / 道具 / 场景 / 风格板 / 预览图的 `generate_image.model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文（`name` 只用来找行；禁止把 `Nano Banana 2` 别名、视频行、其它图片行写入）。

**HARD — generate_image / generate_video 阻塞轮询**：`generate_image` / `generate_video` 只返回 `task_id`，**不算完成**。同一 continuation 必须立刻反复调用 `get_task(task_id)`，直到终态：`TASK_STATE_PENDING` / `TASK_STATE_RUNNING` → 继续 `get_task`（禁止停住、禁止等用户下一句、禁止只写「生成中」就结束、禁止发下一阶段提问）；`TASK_STATE_SUCCEEDED` → 记下返回里的**素材 URL**（`url` / `image_url` / `video_url` 以返回为准），本段才算完成；失败态 → 说明失败，禁止当成功、禁止再叠一次 generate_image / generate_video。并发提交的多个 `task_id` 必须全部轮询到终态后才能 Advance。Apps widget 只展示进度，**不能**代替 `get_task`。禁止因为「控件会自己轮询」而跳过。后续 `generate_image` / `generate_video` / run_prompt / `merge_videos` 都用这些 URL，**禁止**把 `node_id` 当素材入参。

**HARD — 本链无画布操作**：禁止 `PushStyleList` / `PushConfiguration` / `PushDirectionTool` / `PushSuggestions` / `PushMediaUpload` / `PushGeneratedNodes` / `create_canvas_node`。风格库走 MCP `choose_skill_asset`，不是画布卡。除风格卡外，等待面一律 Host tools。文本产物（剧本、Video Prompt）由 agent 打印，不落文本节点。成片词不靠宿主读画布节点：`generate_video.prompt` = 已打印的该段 `content`。

`StyleTemplate` 整链冻结为 **`animation`**。禁止写进 Chat、开场题、规格题。禁止问 Film vs Anime。禁止 `ai_film`。`choose_skill_asset.style_template` 必须传 `"animation"`，禁止省略（省略会落到 `ai_film`）。

---

## 运行时填参（HARD）

本链没有 generic-agent system prompt。调平台 tool 时按下表填，**禁止发明**当前 tool schema 没有的字段。schema 有的必填项缺了就按本表补，不要空着让平台猜。

### 项目

| 调用 | 怎么填 |
|------|--------|
| `create_project` | `{ "name": "<短项目名>" }`。本链只调一次，记下返回的 id |
| `choose_skill_asset` | `{ "style_template": "animation", "title": "Styles" }`。**不传** `projectId`。返回不是选择 |
| run_prompt / `merge_videos` | 必传 `projectId` = 该 id |
| `generate_image` / `generate_video` | 必传 `project_id` = 该 id。加载本 skill 后禁止省略、禁止靠自动建项目 |

还没有 id、且下一拍要调上表**需要项目 id** 的 tool 时，先 `create_project`。`choose_skill_asset` 不要等 id。

### 模型

| 调用 | 怎么填 `model` |
|------|----------------|
| `generate_image`（风格板 / 角色 / 道具 / 场景 / 预览图） | Image 表 **Nano Banana 2** 行的 `model` 列原文 |
| `generate_video`（成片） | `VIDEO_MODEL`（API id，见 §`settings` 映射表） |

`name` 只用来找行。禁止把别名、错表、其它行、卡上显示名写进 `model`。

### 画幅 / 分辨率（成片）

成片读 `<available_models>` 该 `VIDEO_MODEL` 的 Video 行：

| 字段 | 怎么填 |
|------|--------|
| `aspectRatio` | `VIDEO_RATIO` 若在该行 `ratios` 里 → 原样用。`ratios=fixed` → **整项省略**。不在表里 → 改用该行第一个合法 token；无法唯一确定则 Host tools 再问一次。禁止把非法 token 传出去 |
| `resolution` | `VIDEO_RESOLUTION` 若在该行 `resolutions` 里 → 原样用。H3 默认 `768p`（合法档 `768p` / `2k`）；其余默认 `720p`（2.0 / 2.0 Fast / 2.5 常见 `480p` / `720p`，以该行原文为准）。`resolutions` 为 `-` / 空 → **整项省略**。不在该行 → **禁止** `generate_video`，引导 `This resolution is not compatible with the selected model. Change the resolution or the model.` 禁止默默改档 |
| `duration` | **本段** `duration_sec`（STEP3 该项），不是规格总时长 |

规格写入 Session 后，后续预览图 / 成片**静默继承**仍合法的 `VIDEO_RATIO` / `VIDEO_RESOLUTION`；用户本句写了新值且该值在该行才改。角色 / 道具 / 场景 / 风格板的 `aspectRatio` 仍固定 `16:9`，不受成片画幅影响。生图 `resolution` 见下方 §生图分辨率，禁止写死 `1k`。

### 生图分辨率（HARD）

`<available_models>` Image 行的 `resolutions` 是目录展示，大小写经常是 `1k` / `2k` / `4k`。`generate_image.resolution` **必须**用该 tool 自己声明里可接受的 token 原文（Nano Banana 2 当前是 `1K` / `2K` / `4K` 这一类）。语义相等时（`1k`=`1K`，`2k`=`2K`，`4k`=`4K`）选 **tool 声明那一条**，禁止把目录小写 `1k` 原样传入。目录行没有、或 `resolutions` 为 `-` / 空 → 整项省略，不要发明。

档位怎么选（先定档，再取 tool 声明原文）：

| 生图 | 档 |
|------|----|
| 风格板 / 角色 / 道具 / 场景 | **1K 档** |
| 预览图 | `VIDEO_RESOLUTION` 为 `480p` / `720p` / `768p` → **1K 档**；`2k` / `1080p` → **2K 档**；`4K` / `4k` → **4K 档** |

禁止把 Video 行的 `768p` / `720p` 写进 `generate_image.resolution`。预览图画幅仍是 `VIDEO_RATIO`。

规格题**必须**走 Host tools，**每题全部可选项都要进 `options`**（画幅六档；时长三档；模型三档）。禁止 Chat 只打印一档。禁止在正文里写 default / 预选。手填总时长走 Other / 自由输入，不进 `values[]`。

### 媒体绑定

| 调用 | 怎么挂素材 |
|------|------------|
| `generate_image` / `generate_video` / run_prompt / `merge_videos` | **只传 URL 字段**（声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`）。图进 image_*，视频进 video_*。**禁止传 `nodeIds`** |

这些 URL 只许用已有真实地址，禁止编造、禁止为凑槽复制同一条：

- 用户 Provide：用户消息 / 上传给出的图、视频 URL
- 本链生成：`get_task` 成功后的素材 URL

prompt 正文禁止写 HTTPS / `@Image` / `@Video`。

### 占位符

`generate_image` / `generate_video` 的 prompt 正文只用 `<<<image_n>>>` / `<<<video_n>>>`：小写、从 `1` 起，与 `image_url(s)` / `video_url(s)` 顺序一一对应。每个占位必须写清角色。历史里若烂成 `<<>>`，按当前绑定重写成完整占位后再调用。禁止空占位。
STEP3 返回的成片词若本身没有占位，成片时在词前加一行按序点名已挂图的 `<<<image_n>>>`（角色 / 道具 / 场景），再接原文 `content`，末尾 `no background music`。

### 串行

run_prompt **禁止**与 `generate_image` / `generate_video` 同拍并行。角色+场景成图、预览图 ×N、同一批最多 4 段成片仍按本文件 §并行。预览图与 STEP3 禁止同一 `tool_calls`。

### 含糊 / 纯确认

**只**适用于已发出且仍有效的 **Host tools** 提问，或已打开且未确认的 `choose_skill_asset`：`nice` / 无可执行新指令 → 重发同一提问 / 同一风格卡，不要 Advance。
剧本后 / 资产后 / BGM 闸门上的 `continue` / `preview images` / `Merge with BGM` = 已选，必须 Advance。`Confirmed Styles info` = 风格已选，必须 Advance。

---

## 为什么要灵活

用户不会只走一条固定生产线。他们可能跳过任意中间产物、自带剧本 / 角色图 / 场景图 / 视频提示词、从任意点直奔更后的目标、中途改主意、或对任意前序不满意。本 skill 用**阶段图 + 五个算子**处理这些情况；下面的「不要角色资产 / 自带剧本 / 剧本后出视频」只是算子的实例，**不是**封闭清单。遇到未写出的说法，先归到某个算子，再往下走，不要因为「没写过这个例子」而卡住。

每条新用户请求开一条新 run：清空上轮状态、确认、风格、资产、提示词、成片。算子改的是**本 run 的 Stage 计划**，不是另开一条刚性流水线。

---

## 阶段图

默认顺序（只执行 **enabled** 的阶段）：

```text
intent → style → settings → script → assets → frames → video_prompts → clips → merge
```

| 阶段 | 默认 | 用户可见产物 | 说明 |
|------|------|--------------|------|
| `intent` | **必跑**（默认 2 题） | 无 | 开场问询；不是规格题 |
| `style` | **pending**（可跳过） | 一张风格参考图 | `choose_skill_asset(style_template: "animation")`：点选库图。不是角色图、不是场景底板 |
| `settings` | 规格未齐则跑 | 规格提问 | 画幅 / 时长 / model；分辨率按模型写入，不上题 |
| `script` | 必有（生成或自供） | **只** Markdown 剧本（Chat 全文） | `long_video_step1_script`。同一次带回的 `character_prompts` / `background_prompts` **只进内存**，本步不上图 |
| `assets` | run | 角色设定图 + 场景底板 | 普通模式先出剧本后提问，用户选继续才成图 |
| `frames` | run | 各段预览图 | 展示件；记录内部，图可选 |
| `video_prompts` | 必有（生成或自供） | 一段一段打印 `Video Prompt {i}` | `long_video_step3_video_prompts`。拼成一份总稿只打一次 = 非法 |
| `clips` | 必跑才能成片 | 分段成片 | |
| `merge` | 有分段成片则跑 | 成片（可选 BGM） | 普通模式先停 BGM 闸门；N=1 仍可走闸门 |

每阶段状态：`pending` | `run` | `skip` | `provided` | `done` | `invalidated`。
**enabled** = 不是 `skip`，且（`pending`/`run`/`invalidated` 需要执行，或 `provided` 只需绑定不再生成）。

**硬底线**（不能整链跳过）：必须有故事身份（用户 brief / 自供剧本之一）；要出视频必须有 script（生成或自供）、`video_prompts`（生成或自供，且已打印齐）、以及至少一块视觉参考（角色图、场景图或用户参考图之一）。`style` **不是**成片硬底线；跳过则后面不传风格图。其它阶段都可以 skip 或 provided。
`style` 开场默认 **`pending`**。未决时 **enabled**，排在 `settings` 之前。普通模式必须先让用户在风格库点选（或 Skip / Provide），才能进 `settings`。
`assets` 开场默认 **`run`**。普通模式剧本打印后必须先出剧本后提问，禁止同轮直接成图。FastForward / AutoRun 才跳过这组提问。
`frames` 阶段：被 Skip 的只是**预览图成图**。预览图不依赖内部 `frames[]`。内部细镜由 Host 在合写里跑 STEP2。合写 instruction 必须带剧本文 + 规格，禁止传 `frames[]`。禁止挂预览图给 STEP3。

---

## 五个算子（HARD — 任意阶段、任意轮次）

从用户这句话里识别**一个主算子**（一条消息可同时 Provide 多件素材）。然后立刻 Advance。

### 1. Skip(S)

用户不要某阶段的产物（「不要风格参考」「不要角色图」「别生成预览图」「跳过合成直接看分段」「不要场景底板」……）。

- `Stage[S] = skip`。不生成、不展示、不等该步提问。
- 下游按 `slot-adaptation.md` **缺了就省略或回退到次近素材**，禁止为凑槽复制同一 URL。
- 若当前正停在 S 的等待提问，马上离开。
- `script` / `video_prompts` / `clips` **不能**整段 Skip 后还声称能出视频；缺硬底线就问清楚。

### 2. Provide(S, asset)

用户交出该阶段产物（上传 URL、粘贴剧本文、完整视频提示词……）。**提供优先于 Skip。**

- 绑定到 S 的锚点，`Stage[S] = provided`，不生成。
- 角色图 / 场景图 / 参考视频 **禁止**当成剧本正文；剧本文 **禁止**当成角色主图。风格参考图 **禁止**当成角色设定或场景底板。
- 任意轮次都可 Provide；中途补交则改状态并继续。

### 3. Jump(T)

用户要尽快到达更后的阶段（「剧本之后直接出视频」「一直做到成片」「先出分镜就行」「不要中间结果」……）。

- `FastForwardTo = T`（默认若只说「直接做完 / 出视频」则 `T = clips`，N≥2 时含 `merge`）。
- 从当前点起，对每个 enabled 阶段：**执行但不推中间等待提问**；文本产物仍须打印。
- 到达 T 的产物后，按 T 的完成态展示。T 之前被 Skip 的阶段仍然不做。
- Jump **不是**跳过硬底线：仍须跑完 enabled 的 `script` 与 `video_prompts` 才能进 `clips`。
- Jump(`settings` 或更后) 才可跳过 `style` 提问：已有风格图就绑定，没有则 `style = skip`，**禁止**静默生成风格板。
- Jump(`script`) 普通模式仍出剧本后提问。FastForward / AutoRun / Jump(`assets` 或更后) 才同轮成图。

### 4. Rollback(S)

用户不满意某前序（提问选项 `Revise …` 或自然语言点名风格 / 剧本 / 角色 / 场景 / 预览图 / 提示词 / 规格 / 成片……）。未点名时，按语义落到**最早仍影响当前问题的阶段**。

- `Stage[S] = invalidated`；S **之后**全部 `invalidated`（旧 URL 可留，状态禁止再引用）。
- 用这条建议改输入 / 规格；只说「重做」则同参重跑。
- `AutoRunDownstream = true`：重做 S 后，按**当前** Stage 计划自动顺跑后续 enabled 阶段，直到 `clips`（N≥2 到 `merge`）。中途不推「下一步」除非缺必填输入。

### 5. Reroute(S, mode)

同一阶段换做法（生成角色图 → 改用上传；选风格 → 重发卡；等用户传剧本 → 改为生成；规格改走默认值……）。

- 更新该阶段模式，作废只依赖旧模式的下游（通常从该阶段起 invalidated）。
- 立刻按新模式执行或等待新输入。

**冲突**：Provide > Skip > 默认 run。Jump 不取消已 Provide 的素材。Rollback 之后以最新 Stage 计划为准。

---

## 不得卡住（HARD）

每一次 assistant action 必须是下面之一（自上而下，先匹配的优先；禁止用「调用平台能力」压过前面的等待）：

1. 开场问询：`IntentAskedCount < 2` 且下一题尚未对 Host tools 真发出 → 同轮真调用一次。标题 = 短题名；问句 = **恰好一句**点名 brief；`options` = **恰好 3 条**且第一条为推荐默认。无真调用、把 3 条写成 Chat 编号列表、或问句为空 = 本步失败。未满 2 题时**禁止**进 `style` / `settings`，禁止同拍 `create_project` / `choose_skill_asset` / run_prompt / `generate_image / generate_video`
2. 开场题已发出、用户尚未作答 → **停住**。Host tools 返回若没有选中的 option / Other 文本，只表示选择框已发出，不是已答
3. 停在已打开的 `choose_skill_asset` 上，等 §风格确认信号（见 `style-prompt.md`）。此期间禁止 `settings`，有控件时禁止 Host tools 再问风格
4. 停在**已经发出且仍有效**的其它宿主提问上（规格 / 剧本后 / 资产后 / BGM / 无控件风格 fallback），等用户选择
5. 调用平台能力，产出下一件产物或下一轮宿主提问（仅当 1–4 都不适用）

禁止空回复且无任何能力调用、也无宿主提问、也未贴出必打的剧本文 / Video Prompt、也未打开风格控件——**但**开场问询 / 其它 Host tools 题已经发出、或 `choose_skill_asset` 已打开且用户尚未确认时，**停住且不再调任何 tool 是正确终点**。伪调用文本已写出但没有真调用 → 重发真调用。
能力返回后的 continuation 必须 Advance，不需要用户再发一句——**例外**：① Host tools 已发出、用户尚未作答；② `choose_skill_asset` 返回只表示控件已打开，不要 Advance 到 `settings`。`generate_image / generate_video` 返回 `task_id` 必须先 `get_task` 到终态再 Advance。
缺必填输入 → 问清楚（一题宿主提问），不要空转。
阶段被 Skip / 已 Provided → **同轮或同一次 continuation** 进入下一 enabled 阶段。

---

## Advance

算子落地后，取阶段图上**下一个 enabled 且未 done/provided** 的阶段：

- 需要产出 → 按 §阶段目的选用平台能力
- 只需绑定（provided）→ 记锚点，继续下一个
- skip → 跳过
- 普通模式且该阶段有用户可见产物、且不在 FastForward / AutoRun 中 → 按 §双通道文案发等待提问（主路径 = 下一 enabled 阶段），**停住**
- FastForward / AutoRun 中 → 不发中间等待提问，继续直到目标

过渡态（规格刚写入 / 仅内部 `frames[]` 齐 / 资产决策已拍板但图未发）**禁止停驻**。
`IntentDone=true` 且 `style` 仍 `pending`、风格卡未出 → **必须停**。同轮只调 `choose_skill_asset(style_template: "animation", title: "Styles")`。**禁止**同轮出规格提问。
`choose_skill_asset` 刚返回 **必须停驻**，不是过渡态。无控件宿主才同拍把 `items[].name` 塞进 Host tools。
`script` 刚打印、普通模式、`ScriptAssetsGateDone=false` → **必须停**。同轮只贴剧本文 + 推剧本后提问。禁止 `generate_image`。
`ScriptAssetsGateDone=true` 且 `assets` 仍是 `run`、图未发 → 立刻成图。正文 `Generating character and background images.` 禁止再推这组提问。本批全部 `get_task` 终态后一次状态句 + 资产后三选项。
`assets` 成图刚齐、用户还没点资产后提问（普通模式）→ **必须停**。**禁止**读 `frames-prompt.md` / `video-prompts.md`，**禁止**预览图 `generate_image`，**禁止** `long_video_step3_video_prompts`。
进入 `frames`（仅用户点了 `preview images` / `Continue to preview images`，或 FastForward）→ **先出图，再合写**：成图未发则本拍只发预览图 `generate_image`×N + 各 `get_task`。正文 `Generating preview images.` **禁止**夹 STEP3。本批未齐 → 禁止 STEP3。齐了一次状态句，下一拍只调一次 STEP3（正文 `Generating video prompts.`）。Skip 成图或图已齐、还没有打印齐 `Video Prompt {i}` → 本拍只调 STEP3。已打印任一 `Video Prompt {i}` → **禁止**再调 STEP3。失败章等这批 `get_task` 后再补，禁止为补图重开合写。还没打印这些词 → 禁止成片。
`video_prompts` 已齐 → **先**把全部 `Video Prompt {i}` 正文打印进 Chat。FastForward 到 `clips` 也一样：本拍只打印，**下一拍**再成片。禁止同拍出片，禁止只把词留在内存不打印。

---

## 开场意图（`intent`）

**目的**：用户给出指令后、进入 `style` / `settings` 之前，必须先基于这条指令挖掘并问出专业问题。细则见 `intent-questions.md`。

- **HARD**：正式流水线前默认只问 **2 题**。每题一次 Host tools。禁止为凑问卷问第 3 题。
- **引导 HARD**：标题 = 从 brief 压的短名；问句 = **恰好一句**（点名 brief）；`options` = **恰好 3 条**且第一条 = 推荐默认。**禁止**把问句写成 Chat 编号列表。**禁止**用规格提问问这些问题。
- 题必须**改写自当前用户指令**。已由首轮文本 / 上传说清的事实写入字段，**不要再确认一遍**；但仍须另挖至少 2 道能提升专业度的题。
- **禁止**因「看起来没有缺口 / 指令已够用 / 用户说直接开始」而 0 题进 `style` / `settings`。
- 仅当 `IntentAskedCount ≥ 2` 之后，用户再说开始 / 默认 / 跳过剩余 → `IntentDone=true`。问询中的上传先 Provide 再继续问。问询中明确交风格图 → 只绑 `style`，不要当成角色 / 场景。

---

## 每 turn

自上而下只取一条：

0. 伪调用无真执行 → 重发。
1. 某次能力调用已发出、**尚无结果** → 等这批结果，不要再叠下一批。`generate_image` / `generate_video` 返回 `task_id` = **尚无结果**：本 continuation 必须 `get_task` 轮询到终态，`get_task` 不算叠生成。进入 `frames` 时预览图 `generate_image`×N 是一批；STEP3 是终态后的下一批。禁止两批混在同一 `tool_calls`。
2. `IntentDone=false` → 只问下一题或收回答。问下一题必须真调用 Host tools，且问句含 brief 词。首轮带了剧本 / 参考图也先问询，记下入口。题已发出未答 → 停住。
3. 本轮能识别算子 → 执行算子。若 `IntentAskedCount < 2`：**只记账**，**禁止**进 `style` / `settings`；本轮仍问下一题。
4. `IntentDone=true` 且 `style` 仍 `pending`、风格卡未出 → **只出** `choose_skill_asset(style_template: "animation", title: "Styles")`。禁止同轮出规格提问。上一拍已是 `choose_skill_asset` → 按 `style-prompt.md` 解析回程，不要把工具回包当成选择。
5. 规格未齐且未写入 Session → 只出规格提问（或 FastForward 时写入默认）。回包已能解析 `aspectRatio` + `duration` + `model` → 按模型写入分辨率（H3=`768p`，其余=`720p`）后**立刻写入 Session，同轮进 `script`，禁止再推规格提问**。规格已齐但题未出、用户也未给齐 → 只出规格提问。`style` 未 resolved 时禁止进本条。
6. 剧本已打印（或 provided 已绑定），普通模式且 `ScriptAssetsGateDone=false` → **只出剧本后提问**，然后停。禁止成图。用户点继续生成 → `ScriptAssetsGateDone=true`，同轮按 `assets-prompt.md` 成图。点修改剧本 → 下一句有改写说明则带 `modify_request` 重跑 STEP1，打印后再出同一组提问；只点修改没写要改什么 → 停着问要改哪，禁止空改一轮。FastForward / AutoRun → 跳过这组提问，直接成图。
6b. `ScriptAssetsGateDone=true` 且 `assets` 仍 `run`、图未发 → **同轮成图**。正文 `Generating character and background images.` 禁止再推这组提问。
7. 当前该跑 `frames`（仅用户点了 `preview images` / `Continue to preview images`，或 FastForward）→ 按 `frames-prompt.md` **先出图再合写**：图未发则正文 `Generating preview images.`，只发 `generate_image`×N + `get_task`。已打印 `Video Prompt {i}` → 禁止再调 STEP3。失败章只补失败章（`Retrying the remaining preview images.`），禁止再夹带 STEP3。本批未齐禁止 STEP3；齐了一次状态句，下一拍只调 STEP3（正文 `Generating video prompts.`）。合写回包必须一段一项 `name`=`title`=`Video Prompt {i}` + `content`=该段词；同一 continuation **立刻全文打印**；没有打印齐 → **禁止** `generate_video`。禁止同拍出片。
8. FastForward / AutoRun 且上一步已齐 → 只跑下一 enabled 阶段。
9. 否则按当前阶段目的推进；含糊聊天且等待提问仍有效 → 重发同一提问，不要空回复。规格已写入 Session → 禁止再推规格提问。

---

## 阶段目的（该跑时才读对应 reference）

链隔离：`AiAnimationActive` 为真时只按本文件。启动：`/ai-animation`、`ai-animation`、long animation、动画长片、跳步 / 自供 / 回退式长动画，或本链已有入口 / 问询 / 相位。
状态从 history 每轮重推。禁止拿 `ugc-ads` / `tvc-ads` / `ai-story` / `cinematic` / `3d-cgi` / `long-video` generic_agent 正文跑本链。

### `style`

前置：`IntentDone=true`。默认 `pending`。未决时 **enabled**，排在 `settings` 之前。细则见 `style-prompt.md`。

- **HARD — StyleTemplate**：整链只许 `animation`。禁止写进 Chat / 问句 / 选项。禁止从故事 brief 的「电影 / 真人」等词切库。
- **HARD — 风格卡**（`pending`）：同轮必须 `choose_skill_asset(style_template: "animation", title: "Styles")`，正文可空。**禁止**先出规格提问。返回 ≠ 确认。
- 确认消息含 `Confirmed Styles info` 且能解析 `image:` → 绑 URL，`done`，同轮进 `settings`。
- 用户交出风格图 URL → 绑第一张 URL，`provided`，同轮进 `settings`。
- 明确 Skip / Continue / Next 且没图 → `skip`，同轮进 `settings`。
- FastForward / Jump(`settings` 或更后) 且未 Skip / Provide → `style = skip`，不发卡、不静默生成。

### `settings`

前置：`IntentDone=true`，且 `style` 已是 `done` / `provided` / `skip`。
一次 Host tools（能一次提多题就一次提完）。标题 `Set up your Video Settings`。assistant 正文最多一句：`Please configure your target video specs before we generate the script storyboard.`
**禁止**再放 `resolution`。禁止加第 4 项。禁止把 `"Custom"` 写进时长 `options`（手填走 Other）。

**固定三项、顺序 HARD**（每题 options 必须传齐）：

| 顺序 | 标签 | `name` | 全部可选项（必须全部列出） | 默认（只内部写，禁止印给用户） |
|------|------|--------|---------------------------|------|
| 1 | Aspect Ratio | `aspectRatio` | `9:16` / `16:9` / `1:1` / `4:3` / `3:4` / `21:9` | `16:9` |
| 2 | Duration | `duration` | `15s` / `15-30s` / `30-1min` | `15s` |
| 3 | Model | `model` | `MiniMax-H3` / `Seedance 2.0 Fast` / `Seedance 2.0` | `MiniMax-H3` |

禁止借用 ugc-ads 的 `"<30s"` / `"0-30s"` / `"30-60s"` / `"5s"`。时长三档是预设；用户 Other / 自由输入仍可手填总时长（`8s` / `180s` / `300秒`）。手填优先于三档默认。禁止把 `>1min` 写进 `options`。`model` 顺序必须是 `MiniMax-H3` → `Seedance 2.0 Fast` → `Seedance 2.0`。不要把 `Seedance 2.5` 写进题。题上是显示名，禁止把 API id 写进 `options`。

**HARD — 分辨率不上题**：确认或 FastForward 按已映射的 `VIDEO_MODEL` 写入 `VIDEO_RESOLUTION`：`MiniMax-H3` → `768p`；其余模型 → `720p`。用户口头点名分辨率且该值在该模型 Video 行 `resolutions` 里才覆盖；不配则忽略口头值，仍用上表默认。

确认或 FastForward 写入后冻结：`VIDEO_RATIO` / `VIDEO_RESOLUTION` / `VIDEO_DURATION_RANGE` / `VIDEO_MODEL`。`VIDEO_DURATION_RANGE` 用题上 token（`15s` / `15-30s` / `30-1min`，或手填原文）。整数 `VIDEO_DURATION`：`15s`→15；`15-30s`→22；`30-1min`→45；手填取开头整数（`300` / `300s` / `300S` / `300秒` 都 = 300）。≥4 即合法。该整数覆盖 brief 里口头时长。角色设定仍 `16:9`，场景底板仍 `16:9`，与成片画幅无关。

**HARD — 显示名 → API id**：回包的 `model` 先当显示名。用 `<available_models>` Video 表 `name` 对齐后，把该行 `model` 列原文写入 `VIDEO_MODEL`。对不上时用这张表，禁止把显示名传给成片 / `instruction.model`：

| 回包（显示名或旧 id 都认） | `VIDEO_MODEL`（API id） |
|----------------------------|-------------------------|
| `MiniMax-H3` | `MiniMax-H3` |
| `Seedance 2.0` / `seedance-2.0` / `seedance-2-0` | `seedance-2.0` |
| `Seedance 2.0 Fast` / `dreamina-seedance-2-0-fast-260128` | `dreamina-seedance-2-0-fast-260128` |
| `Seedance 2.5` / `seedance-2.5` | `seedance-2.5` |

未选则 `VIDEO_MODEL=MiniMax-H3`。确认或 FastForward **当下**就必须完成这张映射，再进 `script`。`generate_video.model`、STEP1 `instruction.model`、STEP3 `instruction.model` 都用这个 API id。缺 `instruction.model` = 本步失败。

**HARD — 确认即离开，禁止循环重推**：回包能解析三项 → 按模型写入分辨率，立刻写入 Session，同轮进 `script`。
- `duration` 不在 `options`、大于 120、或大小写 `S`/`s`，只要能取出 ≥4 的整秒，都算已齐。禁止因此重推题。
- `model` 为上表任一显示名或旧 id 即合法。
- 本题 `duration` 是**成片总时长**，不是单段生成秒数。禁止用模型行 `duration(s)` 否决本题。
- 默认组合恒适配（H3+`768p`，其余+`720p`）。口头覆盖的分辨率不在该模型 Video 行 → 丢掉口头值，仍用默认，不要重推题。
用户已给齐三项 → 写入 Session 后可不再停。FastForward 且规格未齐 → 写入默认：`16:9` + `15s` + `MiniMax-H3` + `768p`。普通模式规格未齐 → 只推这三项提问，然后停。已确认过一次 → 禁止再推同一套题。

### `script`

见 `script-prompt.md`。有用户剧本 → 整理成完整 Markdown 后**全文贴进 Chat**（provided）。否则 run_prompt `long_video_step1_script`（必带 `projectId`）。
成功**只**展示渲染后的剧本 `content`（禁止 code fence）。同一次返回的 `character_prompts` / `background_prompts` 写入内存。普通模式**不要**同拍成图：贴剧本后立刻出剧本后提问，然后停。

### `assets`

默认 `run`。排在 `frames` 之前。细则见 `assets-prompt.md`。

- **HARD — 剧本后提问**（普通模式，`ScriptAssetsGateDone=false`）：正文可空。同轮 Host tools：引导 `Modify the story script, or continue to character and background images?`。`options` 必须恰好这 2 条，顺序固定：
  1. `Continue generating character and background images`
  2. `Modify the story script`
- 点 1 / 同义继续 → `ScriptAssetsGateDone=true`，同轮按内存提示词 `generate_image` + `get_task`。
- 点 2 / 同义改剧本：下一句有改写说明 → 带 `modify_request` 重跑 STEP1；新剧本打印后 `ScriptAssetsGateDone` 仍为 false，再出同一组提问。只点修改、没有任何改写说明 → 停着问要改哪，禁止空跑一轮新剧本。
- 成图拍：正文 `Generating character and background images.` + `generate_image`。本批全部 `get_task` 终态后一次状态句，再停在资产后提问。
- **HARD — 资产后提问**（普通模式，成图或替换刚齐）：Host tools：引导 `Continue to preview images, regenerate the character and background images, or upload replacements?`。`options` 必须恰好这 3 条，顺序固定：
  1. `preview images`
  2. `Regenerate character and background images`
  3. `Upload to replace character and background images`
  点 1 / `Continue to preview images` → 进 `frames`。点 2 → 同轮按内存提示词 + 变化句重出全部资产图（不要挂旧资产图当参考），终态后再出同一组提问。点 3 → **先**用 Host tools 列出已有 `[Character]` / `[Prop]` / `[Background]` title，点哪张换哪张；再请用户发**一张**图 URL。新图接进**同一槽**，下游用法与生成图相同。禁止追加、禁止改挂风格图。FastForward / AutoRun → 跳过这组提问。

### `frames`

见 `frames-prompt.md`。该跑：从 `script_markdown` 各章第一条镜头行出预览图（可 Skip）。张数 = 章节数。本拍只出图 + `get_task`，终态后再调一次 STEP3。provided 预览图只绑定展示，**仍禁止**传入 STEP3 / 成片。预览图失败不得挡住各 `Video Prompt {i}` 打印。禁止资产成图成功拍直接进本阶段。

### `video_prompts`

见 `video-prompts.md`。预览图终态后的下一拍调用，**每个 run 只调一次**。禁止和预览图同一 `tool_calls`。已经打印任一 `Video Prompt {i}` → 禁止再调。调用方输入是 `instruction` **object**：`script_markdown` + `duration_sec` / `ratio` / `model`（Modify 另加 `modify_request`）。角色 / 场景用 `image_urls`（有才加）。禁止传 `frames[]`。禁止挂预览图。禁止 `instruction` 写成散文 string。上一拍若因 `instruction must be a JSON object` 失败 → **按 object 模板重发一次**。
成功：`result.items` 一段一项，`name`=`title`=`Video Prompt {i}`，`content` = 该段词。同一 continuation **立刻全文打印**每一段。没打印齐 = 本步失败，禁止出片。成片时 `generate_video.prompt` = 该段已打印 `content`（按 §占位符补 `<<<image_n>>>`），不要只挂 URL 不写词。

### `clips` / `merge`

见 `clips-merge.md`。每组一段新片子（`VIDEO_MODEL`），title = `Long Video {i}`。**同一拍最多 4 段** `generate_video`，其余等这批 `get_task` 终态再发。回包 `Concurrent execution detected` / `9002` / `5003` → 只重试失败段。禁止一次打满十几段。禁止把 BGM 写进 `Video Prompt {i}`，禁止对单段配乐。
普通模式：全部分段成功后推 **BGM 闸门**并停住。选项固定 `["Merge with BGM", "Merge without BGM"]`，引导 = `Sure, would you like to add BGM?` 用户选定后再调一次 `merge_videos`（with → `is_generate_bgm=true` / without → `false`），挂各段成片 URL。
FastForward / AutoRun 到 merge 且未点名 BGM → 无 BGM 合成。N=1 仍可走 BGM 闸门（单段配乐）。Skip(`merge`) → 以分段成片为结束态。

---

## 双通道文案（HARD — 全流程）

任意阶段的首次生成、重生成、Provide、等待下一步，都用**同一套拆句**。选哪个能力对照 tool 声明；这里只约束两句分别写什么。

| 槽 | 取值 |
|----|------|
| `{ReadyNoun}` | 本拍刚落地或刚更新的用户可见产物短名 |
| `{NextAct}` | 下一 **enabled** 阶段的主路径动作 |

**同轮同时发状态句 + 宿主提问时**：

1. 状态句 = **一句状态**，只说什么好了。首次：`Your {ReadyNoun} is ready.` 更新：`Your updated {ReadyNoun} is ready.` 禁止出现 review / then / continue / generate / merge。写在 assistant 正文。
2. 提问引导 = **一句行动**。有可审产物：`Review {the ReadyNoun}, then {NextAct}.` 禁止再写 is ready / is on the canvas / updated。
3. 两句禁止相同、禁止互为子串、禁止粘成一句再复制到两个表面。

子句例外：剧本 / Video Prompt 必须先贴全文，状态句可附在全文后。

**只发其中一个时**：自动续跑只发状态句；结束态只发 `Your {ReadyNoun} is ready.`（可保留 Revise 选项，不要再写引导）；上一拍已用状态句说过则本拍只发提问。用户可见 English **禁止** `on the canvas`。

选项只进 Host tools 的 `options`。禁止伪 call、编号列表、`Recommended:` 段落进 Chat。
开场问询**不适用**本表的 Review / NextAct 拆句：对 Host tools 真调用；问句只有那一句；3 条方向只进 `options`。
风格卡 / 规格提问用各自引导，不要再套 Review 句。风格卡有控件时不要再发 Host tools。

**通用提问规则**：第 1 条选项 = 下一 enabled 主路径；另给 Skip 或 Rollback 出口；只 Revise 实际存在的产物；FastForward / AutoRun 不发中间等待提问。BGM 闸门固定 `Merge with BGM` / `Merge without BGM`。剧本后提问固定两条，资产后提问固定三条，不要改成 Review then generate。结束态（合成后或跳过闸门的单段）可留 `Go to edit`，不要再写引导。

填空示例（按当前槽改写，非封闭）：

| 情境 | 状态句 | 提问引导 |
|------|--------|----------|
| 开场问询 | （可省略） | Host tools：标题=短题名；问句=`{问句}`；恰好 3 个方向进 `options` |
| 风格卡 | （可省略） | `choose_skill_asset`；无控件才 Host tools：`Pick a style reference image for this video.` |
| 点选刚绑定、下一拍是规格 | `Your style reference is ready.` | `Review the style reference, then set up your video.` |
| 规格提问 | （不重复预览） | `Please configure your target video specs before we generate the script storyboard.` |
| 成片：分辨率不适配该模型 | （可省略） | `This resolution is not compatible with the selected model. Change the resolution or the model.` |
| 剧本刚齐、等用户拍板 | 先全文贴剧本；可附 `Your story script is ready.` | `Modify the story script, or continue to character and background images?` 恰好两条 |
| 用户选继续、出资产图 | `Generating character and background images.` | （禁止再推剧本后提问） |
| 资产刚齐、`frames` 仍 enabled | `Your character and background images are ready.` | `Continue to preview images, regenerate the character and background images, or upload replacements?` 恰好三条 |
| 进入 `frames` 出预览图 | `Generating preview images.` | （禁止提问；本拍只出图） |
| 只补失败章 | `Retrying the remaining preview images.` | 禁止再调 STEP3 |
| 只合写 | `Generating video prompts.` | 禁止同拍出片 |
| 视频提示词已打印 | 先按段全文打印；可附 `Your video prompts are ready.` | `Review the video prompts, then generate the clips.` |
| 预览图（合写已齐或 Skip 提示词） | `Your preview images are ready.` | `Review the preview images, then generate the clips.` **前提**：已打印全部 `Video Prompt {i}` |
| 待合成 | `Your clips are ready.` | `Sure, would you like to add BGM?` |
| 单段 / 合成结束 | `Your long video is ready.` / `Your full long video is ready.` | （禁止提问引导；可留 `Go to edit`） |

产物 `title`（无产物不编造）：`[Style] {短名}` / 剧本用 STEP1 `name` / `[Character] {短名}` / `[Prop] {短名}` / `[Background] {短名}` / `[Preview Image] {i}` / `Video Prompt {i}` / `Long Video {i}`。加 BGM 合成才另有 `Final Video without BGM - v1` / `Final Video BGM - v1` / `Final Video with BGM - v1`。禁止再写 `[First Frame]`。禁止再写总稿 `Video Prompts`。禁止给分段再落 BGM。

---

## 并行

问询一题一轮：发出后本轮结束，未答前 continuation 也不得进 `style`。风格卡只发一次 `choose_skill_asset`，返回后停住等确认。普通模式剧本成功拍先出提问；用户选继续后再并发角色设定 + 场景底板成图；本批全部 `get_task` 终态后一次状态句 + 资产后三选项。进入 `frames`：预览图彼此可并发，本拍只出图，禁止夹 STEP3；齐后下一拍再合写。成片同一拍最多 4 段。run_prompt 不与 `generate_image / generate_video` 同拍并行。FastForward / AutoRun / Skip 后的下一阶段在 continuation 立刻开始。禁止资产成图成功拍直接进 `frames`。
