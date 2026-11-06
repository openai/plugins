---
name: 3d-cgi
description: "Always use this skill to make a single-shot 2–10s 3D CGI / rendered video clip. Must trigger for /3d-cgi, 3d-cgi, 3D animation, CGI, Pixar-style, Unreal Engine, Blender, octane render, ray tracing, photorealistic 3D, computer-generated, digitally rendered, volumetric, subsurface scattering, PBR, or when a 3d-cgi run is already in progress (intent answers, specs, CGI prompt, clip, BGM merge) or the user skips a step, supplies a reference, jumps ahead, or revises an earlier step without restarting. Even a vague \"make it look 3D\" or \"help me make a 3D render\" must start this skill. After the first instruction, ask 2 professional direction questions grounded in that brief before the formal pipeline. Preset durations 2s / 4s / 6s / 8s / 10s (default 4s)."
source: "buzzy"
risk: safe
scope: mcp
allowed-tools: |
  Buzzy MCP tools
  - create_project
  - generate_video
  - get_task
  - merge_videos

  Host tools — not part of this MCP server
  - AskQuestion
  - ask_question
  - AskUserQuestion
---

# 3D CGI Clip Orchestrator

本链自包含。查阅本 skill 文件只用完整前缀 `skills/3d-cgi/reference/`。
**怎么调平台能力、填哪些参数，对照各 tool 自己的声明**；本文件只写目的、产物和硬底线。
本文件是编排器。成片词由 agent **按本链 reference 直接写出**，禁止发明 `prompt_key`，禁止调 run_prompt。

**HARD — allowed-tools 分类**：`Buzzy MCP tools` 是本 MCP 服务注册的平台 tool，经 Buzzy MCP `tools/call`。`Host tools — not part of this MCP server` 是宿主内置提问 tool，**不是** Buzzy MCP tool，也不走 `load_workflow` / ExecuteTools。Cursor 用 `AskQuestion`，Claude 用 `AskUserQuestion` / `ask_question`，Codex 用同类。选择题必须调 Host tools 里当前可用的那个，禁止因为「不在 Buzzy MCP tools 列表里」就改成编号纯文本。
**HARD — create_project**：进入任何需要 `projectId` / `project_id` 的 Buzzy MCP tool 之前，必须先调 `create_project` 拿到真实 id。本会话只创建一次，后续全程复用。`merge_videos` 传 `projectId`；`generate_video` 传 `project_id`。禁止编造 id，禁止省略，禁止因为 generate_image / generate_video 写了「可自动建项目」就跳过。`create_project` 的入参是 `name`（可读项目名），不要把 catalog 的 `name` 或 `workflow` 抄过来。Host tools 开场问询 / 规格提问那一拍仍禁止同拍调 `create_project`。问询完成且即将调**需要项目 id** 的 Buzzy tool 时若还没有 id，必须先 `create_project`。Jump / FastForward 到更后阶段同此。

**HARD — 宿主提问**：等人选择或确认时，必须对 Host tools 里当前可用名字真调用一次。选项只进提问 tool 的 `options`，且**该题全部可选项必须传齐**（禁止只塞一档）。禁止用 `1.` `2.` `3.` 编号列表、bullet、`Recommended:` 前缀段落作为用户可见选项——那样写 = 本步失败，必须立刻改成真调用。assistant 正文最多一句问句或状态句，**不要复述选项**。不要自己造第 4 个 `Other` 选项：Cursor `AskQuestion` 自带 Other 自由输入。仅当 `tools/list` 里 `AskQuestion` / `ask_question` / `AskUserQuestion` 三个名字都没有时，才允许编号列表，并写明本宿主没有选择框；**规格题的编号列表必须每行列出该字段全部档位**。Cursor 有 `AskQuestion`，禁止走这条。媒体产物就绪只用 assistant 正文状态句。伪调用、编号单值、或缺档都算没发出提问。
**例外 — 成片词 `content`**：结构化 CGI prompt **必须原文贴进对话**（禁止 code fence），不受「正文最多一句」限制。禁止说 on the canvas。贴完后仍发对应 Host tools 等待提问（FastForward / AutoRun 除外）。

| 何时读 | 文件 |
|--------|------|
| 开场组题（默认 2 题） | `intent-questions.md` |
| 下游缺输入时怎么组槽 | `slot-adaptation.md` |
| 任意状态句 / 提问引导 | 本文件 §双通道文案 |
| 填 `generate_video` 参数 | 本文件 §运行时填参 |
| 写成本片词时 | `prompt-write.md`（必读）+ 按需 `hook-framework.md` / `render-styles.md` / `materials.md` / `lighting-library.md` / `camera-language.md` / `particles.md` / `mistakes.md` / `examples.md` |
| 跑到成片 / 合成时 | `clip-generate.md` |

禁止短路径、读其它 skill、把 YAML 当自由 prompt。禁止发明 `prompt_key`。禁止 Higgsfield / `@material[name]`。禁止把 4K / 60fps / codec / 比特率写成平台承诺。

用户可见文案 **固定 English**。禁止出现 `on the canvas`。`SessionScriptLanguage` / `user_lang` 只约束对白与可读场景描述。
参考素材**一律走 URL 字段**（`image_url` / `image_urls` / `video_url` / `video_urls`，以各 tool 声明为准）。**禁止传 `nodeIds`**。用户上传的参考图 / 视频有才加；禁止编造 URL。

**HARD — generate_image / generate_video 阻塞轮询**：`generate_video` 只返回 `task_id`，**不算完成**。同一 continuation 必须立刻反复调用 `get_task(task_id)`，直到终态：`TASK_STATE_PENDING` / `TASK_STATE_RUNNING` → 继续 `get_task`（禁止停住、禁止等用户下一句、禁止只写「生成中」就结束、禁止发下一阶段提问）；`TASK_STATE_SUCCEEDED` → 记下返回里的**素材 URL**，本段才算完成；失败态 → 说明失败，禁止当成功、禁止再叠一次 generate_image / generate_video。Apps widget 只展示进度，**不能**代替 `get_task`。后续 `generate_video` / `merge_videos` 都用这些 URL，**禁止**把 `node_id` 当素材入参。

**HARD — 本链无画布操作**：禁止 `PushStyleList` / `PushConfiguration` / `PushDirectionTool` / `PushSuggestions` / `PushMediaUpload` / `PushGeneratedNodes` / `create_canvas_node`。禁止 `choose_skill_asset`。等待面一律 Host tools。文本产物（CGI prompt）由 agent 打印，不落文本节点。`generate_video.prompt` = 已打印的那份词。

本链**没有**风格库 / 剧本 / 角色设定 / 预览图阶段。用户参考图直接绑给成片。渲染风格（Pixar / photoreal / low-poly…）写进问询字段 `RenderStyle`，不是规格题。

---

## 运行时填参（HARD）

本链没有 generic-agent system prompt。调平台 tool 时按下表填，**禁止发明**当前 tool schema 没有的字段。schema 有的必填项缺了就按本表补，不要空着让平台猜。

### 项目

| 调用 | 怎么填 |
|------|--------|
| `create_project` | `{ "name": "<短项目名>" }`。本链只调一次，记下返回的 id |
| `merge_videos` | 必传 `projectId` = 该 id |
| `generate_video` | 必传 `project_id` = 该 id。加载本 skill 后禁止省略、禁止靠自动建项目 |

还没有 id、且下一拍要调上表**需要项目 id** 的 tool 时，先 `create_project`。

### 模型

| 调用 | 怎么填 `model` |
|------|----------------|
| `generate_video`（成片） | `VIDEO_MODEL`（API id，见 §`settings` 映射表） |

`name` 只用来找行。禁止把别名、错表、其它行、卡上显示名写进 `model`。

### 画幅 / 分辨率（成片）

成片读 `<available_models>` 该 `VIDEO_MODEL` 的 Video 行：

| 字段 | 怎么填 |
|------|--------|
| `aspectRatio` | `VIDEO_RATIO` 若在该行 `ratios` 里 → 原样用。`ratios=fixed` → **整项省略**。不在表里 → 改用该行第一个合法 token；无法唯一确定则 Host tools 再问一次。禁止把非法 token 传出去 |
| `resolution` | `VIDEO_RESOLUTION` 若在该行 `resolutions` 里 → 原样用。H3 默认 `768p`（合法档 `768p` / `2k`）；其余默认 `720p`（2.0 / 2.0 Fast / 2.5 常见 `480p` / `720p`，以该行原文为准）。`resolutions` 为 `-` / 空 → **整项省略**。不在该行 → **禁止** `generate_video`，引导 `This resolution is not compatible with the selected model. Change the resolution or the model.` 禁止默默改档。禁止写死 4K / 1080p |
| `duration` | `VIDEO_DURATION`（本片整秒，2–10），不是档位原文。该模型 Video 行若有 `duration(s)` 且本秒数不在其中 → **禁止**默默改秒数，Host tools 再问一次合法档 |

规格写入 Session 后，后续成片**静默继承**仍合法的 `VIDEO_RATIO` / `VIDEO_RESOLUTION`；用户本句写了新值且该值在该行才改。

规格题**必须**走 Host tools，**每题全部可选项都要进 `options`**（画幅六档；时长五档；模型三档）。禁止 Chat 只打印一档。禁止在正文里写 default / 预选。手填秒数走 Other / 自由输入，不进 `values[]`。

### 媒体绑定

| 调用 | 怎么挂素材 |
|------|------------|
| `generate_video` / `merge_videos` | **只传 URL 字段**（声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`）。图进 image_*，视频进 video_*。**禁止传 `nodeIds`** |

这些 URL 只许用已有真实地址，禁止编造、禁止为凑槽复制同一条：

- 用户 Provide：用户消息 / 上传给出的图、视频 URL
- 本链生成：`get_task` 成功后的素材 URL

prompt 正文禁止写 HTTPS / `@Image` / `@Video` / `@material[...]`。

### 占位符

`generate_video` 的 prompt 正文只用 `<<<image_n>>>` / `<<<video_n>>>`：小写、从 `1` 起，与 `image_url(s)` / `video_url(s)` 顺序一一对应。每个占位必须写清角色。历史里若烂成 `<<>>` 或 Higgsfield `@material[name]`，按当前绑定重写成完整占位后再调用。禁止空占位。
写成片词时若本身没有占位而本片挂了图 / 参考视频，在词前加一行按序点名 `<<<image_n>>>` / `<<<video_n>>>`，再接原文，末尾 `no background music`。

### 串行

写词（打印）与 `generate_video` **禁止**同一 `tool_calls`。先打印齐再出片。

### 含糊 / 纯确认

**只**适用于已发出且仍有效的 **Host tools** 提问：`nice` / 无可执行新指令 → 重发同一提问，不要 Advance。
词后 / BGM 闸门上的 `continue` / `Generate the clip` / `Merge with BGM` = 已选，必须 Advance。

---

## 为什么要灵活

用户不会只走一条固定生产线。他们可能跳过写词、自带完整成片词、自带参考图 / 参考视频、从任意点直奔出片、中途改主意、或对词 / 规格 / 成片不满意。本 skill 用**阶段图 + 五个算子**处理这些情况。遇到未写出的说法，先归到某个算子，再往下走。

每条新用户请求开一条新 run：清空上轮状态、确认、词、成片。算子改的是**本 run 的 Stage 计划**。

---

## 阶段图

默认顺序（只执行 **enabled** 的阶段）：

```text
intent → settings → prompt → clip → merge
```

| 阶段 | 默认 | 用户可见产物 | 说明 |
|------|------|--------------|------|
| `intent` | **必跑**（默认 2 题） | 无 | 开场问询；不是规格题 |
| `settings` | 规格未齐则跑 | 规格提问 | 画幅 / 时长 / model；分辨率按模型写入，不上题 |
| `prompt` | 必有（生成或自供） | **只**结构化 CGI prompt（Chat 全文） | agent 按 `prompt-write.md` 写；禁止 run_prompt |
| `clip` | 必跑才能成片 | 单段成片 | 一张片子，2–10s |
| `merge` | 有成片则跑 | 成片（可选 BGM） | 普通模式先停 BGM 闸门；N=1 仍走闸门 |

每阶段状态：`pending` | `run` | `skip` | `provided` | `done` | `invalidated`。
**enabled** = 不是 `skip`，且（`pending`/`run`/`invalidated` 需要执行，或 `provided` 只需绑定不再生成）。

**硬底线**（不能整链跳过）：必须有镜头身份（用户 brief / 自供成片词之一）；要出视频必须有 `prompt`（生成或自供，且已打印）。参考图 / 参考视频**不是**成片硬底线；没有就纯文生视频。其它阶段都可以 skip 或 provided。
`prompt` / `clip` **不能**整段 Skip 后还声称能出视频；缺硬底线就问清楚。

---

## 五个算子（HARD — 任意阶段、任意轮次）

从用户这句话里识别**一个主算子**（一条消息可同时 Provide 多件素材）。然后立刻 Advance。

### 1. Skip(S)

用户不要某阶段的产物（「不要配乐直接看分段」「跳过合成」……）。

- `Stage[S] = skip`。不生成、不展示、不等该步提问。
- 下游按 `slot-adaptation.md` **缺了就省略**，禁止为凑槽复制同一 URL。
- 若当前正停在 S 的等待提问，马上离开。
- `prompt` / `clip` **不能**整段 Skip 后还声称能出视频。

### 2. Provide(S, asset)

用户交出该阶段产物（上传参考图 / 参考视频 URL、粘贴完整成片词……）。**提供优先于 Skip。**

- 绑定到 S 的锚点，`Stage[S] = provided`，不生成。
- 参考图 / 参考视频 **禁止**当成成片词正文；成片词 **禁止**当成参考图。
- 任意轮次都可 Provide；中途补交则改状态并继续。

### 3. Jump(T)

用户要尽快到达更后的阶段（「直接出视频」「先出词就行」「不要中间结果」……）。

- `FastForwardTo = T`（默认若只说「直接做完 / 出视频」则 `T = clip`，有成片时含 `merge`）。
- 从当前点起，对每个 enabled 阶段：**执行但不推中间等待提问**；文本产物仍须打印。
- 到达 T 的产物后，按 T 的完成态展示。T 之前被 Skip 的阶段仍然不做。
- Jump **不是**跳过硬底线：仍须跑完 enabled 的 `prompt` 才能进 `clip`。

### 4. Rollback(S)

用户不满意某前序（提问选项 `Revise …` 或自然语言点名词 / 规格 / 成片 / 问询方向……）。未点名时，按语义落到**最早仍影响当前问题的阶段**。

- `Stage[S] = invalidated`；S **之后**全部 `invalidated`（旧 URL 可留，状态禁止再引用）。
- 用这条建议改输入 / 规格；只说「重做」则同参重跑。
- `AutoRunDownstream = true`：重做 S 后，按**当前** Stage 计划自动顺跑后续 enabled 阶段，直到 `clip`（再停 BGM 闸门，除非 FastForward 且未点名 BGM）。中途不推「下一步」除非缺必填输入。

### 5. Reroute(S, mode)

同一阶段换做法（等用户传参考 → 改为纯文生；规格改走默认值……）。

- 更新该阶段模式，作废只依赖旧模式的下游（通常从该阶段起 invalidated）。
- 立刻按新模式执行或等待新输入。

**冲突**：Provide > Skip > 默认 run。Jump 不取消已 Provide 的素材。Rollback 之后以最新 Stage 计划为准。

---

## 不得卡住（HARD）

每一次 assistant action 必须是下面之一（自上而下，先匹配的优先；禁止用「调用平台能力」压过前面的等待）：

1. 开场问询：`IntentAskedCount < 2` 且下一题尚未对 Host tools 真发出 → 同轮真调用一次。标题 = 短题名；问句 = **恰好一句**点名 brief；`options` = **恰好 3 条**且第一条为推荐默认。无真调用、把 3 条写成 Chat 编号列表、或问句为空 = 本步失败。未满 2 题时**禁止**进 `settings`，禁止同拍 `create_project` / `generate_video` / `merge_videos`
2. 开场题已发出、用户尚未作答 → **停住**。Host tools 返回若没有选中的 option / Other 文本，只表示选择框已发出，不是已答
3. 停在**已经发出且仍有效**的其它宿主提问上（规格 / 词后 / BGM），等用户选择
4. 调用平台能力，产出下一件产物或下一轮宿主提问（仅当 1–3 都不适用）

禁止空回复且无任何能力调用、也无宿主提问、也未贴出必打的成片词——**但**开场问询 / 其它 Host tools 题已经发出、用户尚未作答时，**停住且不再调任何 tool 是正确终点**。伪调用文本已写出但没有真调用 → 重发真调用。
能力返回后的 continuation 必须 Advance，不需要用户再发一句——**例外**：Host tools 已发出、用户尚未作答。`generate_video` 返回 `task_id` 必须先 `get_task` 到终态再 Advance。
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

过渡态（规格刚写入 / 词已写未打印）**禁止停驻**。
`prompt` 刚打印、普通模式、`PromptClipGateDone=false` → **必须停**。同轮只贴词 + 推词后提问。禁止 `generate_video`。
`PromptClipGateDone=true` 且 `clip` 仍是 `run`、片未发 → 立刻成片。正文 `Generating the CGI clip.` 禁止再推这组提问。
`prompt` 已齐 → **先**把全文打印进 Chat。FastForward 到 `clip` 也一样：本拍只打印，**下一拍**再成片。禁止同拍出片，禁止只把词留在内存不打印。

---

## 开场意图（`intent`）

**目的**：用户给出指令后、进入 `settings` 之前，必须先基于这条指令挖掘并问出专业问题。细则见 `intent-questions.md`。

- **HARD**：正式流水线前默认只问 **2 题**。每题一次 Host tools。禁止为凑问卷问第 3 题。
- **引导 HARD**：标题 = 从 brief 压的短名；问句 = **恰好一句**（点名 brief）；`options` = **恰好 3 条**且第一条 = 推荐默认。**禁止**把问句写成 Chat 编号列表。**禁止**用规格提问问这些问题。
- 题必须**改写自当前用户指令**。已由首轮文本 / 上传说清的事实写入字段，**不要再确认一遍**；但仍须另挖至少 2 道能提升专业度的题。
- **禁止**因「看起来没有缺口 / 指令已够用 / 用户说直接开始」而 0 题进 `settings`。
- 仅当 `IntentAskedCount ≥ 2` 之后，用户再说开始 / 默认 / 跳过剩余 → `IntentDone=true`。问询中的上传先 Provide 再继续问。

---

## 每 turn

自上而下只取一条：

0. 伪调用无真执行 → 重发。
1. 某次能力调用已发出、**尚无结果** → 等这批结果，不要再叠下一批。`generate_video` 返回 `task_id` = **尚无结果**：本 continuation 必须 `get_task` 轮询到终态，`get_task` 不算叠生成。
2. `IntentDone=false` → 只问下一题或收回答。问下一题必须真调用 Host tools，且问句含 brief 词。首轮带了成片词 / 参考图也先问询，记下入口。题已发出未答 → 停住。
3. 本轮能识别算子 → 执行算子。若 `IntentAskedCount < 2`：**只记账**，**禁止**进 `settings`；本轮仍问下一题。
4. 规格未齐且未写入 Session → 只出规格提问（或 FastForward 时写入默认）。回包已能解析 `aspectRatio` + `duration` + `model` → 按模型写入分辨率（H3=`768p`，其余=`720p`）后**立刻写入 Session，同轮进 `prompt`，禁止再推规格提问**。规格已齐但题未出、用户也未给齐 → 只出规格提问。`IntentDone=false` 时禁止进本条。
5. 词已打印（或 provided 已绑定），普通模式且 `PromptClipGateDone=false` → **只出词后提问**，然后停。禁止成片。用户点继续生成 → `PromptClipGateDone=true`，同轮按 `clip-generate.md` 成片。点修改词 → 下一句有改写说明则按说明重写并打印，再出同一组提问；只点修改没写要改什么 → 停着问要改哪，禁止空改一轮。FastForward / AutoRun → 跳过这组提问，先确认词已打印，下一拍成片。
5b. `PromptClipGateDone=true` 且 `clip` 仍 `run`、片未发 → **同轮成片**。正文 `Generating the CGI clip.` 禁止再推这组提问。
6. FastForward / AutoRun 且上一步已齐 → 只跑下一 enabled 阶段。
7. 否则按当前阶段目的推进；含糊聊天且等待提问仍有效 → 重发同一提问，不要空回复。规格已写入 Session → 禁止再推规格提问。

---

## 阶段目的（该跑时才读对应 reference）

链隔离：`CgiActive` 为真时只按本文件。启动：`/3d-cgi`、3d-cgi、3D CGI、Pixar-style、Unreal、Blender、渲染感短镜头、跳步 / 自供 / 回退式 CGI，或本链已有入口 / 问询 / 相位。
状态从 history 每轮重推。禁止拿 `cinematic` / `ai-story` / `ai-animation` / `ugc-ads` / `tvc-ads` 正文跑本链。

### `settings`

前置：`IntentDone=true`。
一次 Host tools（能一次提多题就一次提完）。标题 `Set up your Video Settings`。assistant 正文最多一句：`Please configure your target video specs before we write the CGI prompt.`
**禁止**再放 `resolution`。禁止加第 4 项。禁止把 `"Custom"` 写进时长 `options`（手填走 Other）。

**固定三项、顺序 HARD**（每题 options 必须传齐）：

| 顺序 | 标签 | `name` | 全部可选项（必须全部列出） | 默认（只内部写，禁止印给用户） |
|------|------|--------|---------------------------|------|
| 1 | Aspect Ratio | `aspectRatio` | `9:16` / `16:9` / `1:1` / `4:3` / `3:4` / `21:9` | `16:9` |
| 2 | Duration | `duration` | `2s` / `4s` / `6s` / `8s` / `10s` | `4s` |
| 3 | Model | `model` | `MiniMax-H3` / `Seedance 2.0 Fast` / `Seedance 2.0` | `MiniMax-H3` |

禁止借用 cinematic / ugc-ads / ai-story 的时长档。时长五档是本链单段窗口（2–10s）；用户 Other / 自由输入仍可手填整秒（`3s` / `7s` / `7秒`）。手填优先于五档默认。取出的整秒 `<2` → 写入 `2`；`>10` → 不要硬做长片，引导用户改用 `ai-animation`（动画长片）或 `ai-story`（真人长片），或改回 ≤10s。禁止把 `15s` / `15-30s` / `30-1min` 写进 `options`。`model` 顺序必须是 `MiniMax-H3` → `Seedance 2.0 Fast` → `Seedance 2.0`。不要把 `Seedance 2.5` 写进题。题上是显示名，禁止把 API id 写进 `options`。

**HARD — 分辨率不上题**：确认或 FastForward 按已映射的 `VIDEO_MODEL` 写入 `VIDEO_RESOLUTION`：`MiniMax-H3` → `768p`；其余模型 → `720p`。用户口头点名分辨率且该值在该模型 Video 行 `resolutions` 里才覆盖；不配则忽略口头值，仍用上表默认。禁止把「4K / 60fps」当成已选规格。

确认或 FastForward 写入后冻结：`VIDEO_RATIO` / `VIDEO_RESOLUTION` / `VIDEO_DURATION_RANGE` / `VIDEO_MODEL`。`VIDEO_DURATION_RANGE` 用题上 token（`2s` / `4s` / `6s` / `8s` / `10s`，或手填原文）。整数 `VIDEO_DURATION`：`2s`→2；`4s`→4；`6s`→6；`8s`→8；`10s`→10；手填取开头整数（`7` / `7s` / `7S` / `7秒` 都 = 7）。2–10 合法。该整数覆盖 brief 里口头时长。

**HARD — 显示名 → API id**：回包的 `model` 先当显示名。用 `<available_models>` Video 表 `name` 对齐后，把该行 `model` 列原文写入 `VIDEO_MODEL`。对不上时用这张表，禁止把显示名传给成片：

| 回包（显示名或旧 id 都认） | `VIDEO_MODEL`（API id） |
|----------------------------|-------------------------|
| `MiniMax-H3` | `MiniMax-H3` |
| `Seedance 2.0` / `seedance-2.0` / `seedance-2-0` | `seedance-2.0` |
| `Seedance 2.0 Fast` / `dreamina-seedance-2-0-fast-260128` | `dreamina-seedance-2-0-fast-260128` |
| `Seedance 2.5` / `seedance-2.5` | `seedance-2.5` |

未选则 `VIDEO_MODEL=MiniMax-H3`。确认或 FastForward **当下**就必须完成这张映射，再进 `prompt`。`generate_video.model` 用这个 API id。

**HARD — 确认即离开，禁止循环重推**：回包能解析三项 → 按模型写入分辨率，立刻写入 Session，同轮进 `prompt`。
- `duration` 不在 `options` 或大小写 `S`/`s`，只要能取出 2–10 的整秒，都算已齐。禁止因此重推题。
- `model` 为上表任一显示名或旧 id 即合法。
- 本题 `duration` 是**本片时长**，不是多段总时长。
- 默认组合恒适配（H3+`768p`，其余+`720p`）。口头覆盖的分辨率不在该模型 Video 行 → 丢掉口头值，仍用默认，不要重推题。
用户已给齐三项 → 写入 Session 后可不再停。FastForward 且规格未齐 → 写入默认：`16:9` + `4s` + `MiniMax-H3` + `768p`。普通模式规格未齐 → 只推这三项提问，然后停。已确认过一次 → 禁止再推同一套题。

### `prompt`

见 `prompt-write.md`。有用户成片词 → 整理成完整结构化词后**全文贴进 Chat**（provided）。否则 agent 按 `prompt-write.md` + 按需知识库**直接写出**，禁止调 run_prompt。
成功**只**展示渲染后的词（禁止 code fence）。普通模式贴词后立刻出词后提问，然后停。

- **HARD — 词后提问**（普通模式，`PromptClipGateDone=false`）：正文可空。同轮 Host tools：引导 `Modify the CGI prompt, or generate the clip?`。`options` 必须恰好这 2 条，顺序固定：
  1. `Generate the clip`
  2. `Modify the CGI prompt`

### `clip` / `merge`

见 `clip-generate.md`。一段新片子（`VIDEO_MODEL`），title = `CGI Clip`。禁止把 BGM 写进 CGI prompt，禁止对单段配乐。
普通模式：成片成功后推 **BGM 闸门**并停住。选项固定 `["Merge with BGM", "Merge without BGM"]`，引导 = `Sure, would you like to add BGM?` 用户选定后再调一次 `merge_videos`（with → `is_generate_bgm=true` / without → `false`），挂该段成片 URL。
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

子句例外：CGI prompt 必须先贴全文，状态句可附在全文后。

**只发其中一个时**：自动续跑只发状态句；结束态只发 `Your {ReadyNoun} is ready.`（可保留 Revise 选项，不要再写引导）；上一拍已用状态句说过则本拍只发提问。用户可见 English **禁止** `on the canvas`。

选项只进 Host tools 的 `options`。禁止伪 call、编号列表、`Recommended:` 段落进 Chat。
开场问询**不适用**本表的 Review / NextAct 拆句：对 Host tools 真调用；问句只有那一句；3 条方向只进 `options`。
规格提问用各自引导，不要再套 Review 句。

**通用提问规则**：第 1 条选项 = 下一 enabled 主路径；另给 Skip 或 Rollback 出口；只 Revise 实际存在的产物；FastForward / AutoRun 不发中间等待提问。BGM 闸门固定 `Merge with BGM` / `Merge without BGM`。词后提问固定两条，不要改成 Review then generate。结束态（合成后或跳过闸门的单段）可留 `Go to edit`，不要再写引导。

填空示例（按当前槽改写，非封闭）：

| 情境 | 状态句 | 提问引导 |
|------|--------|----------|
| 开场问询 | （可省略） | Host tools：标题=短题名；问句=`{问句}`；恰好 3 个方向进 `options` |
| 规格提问 | （不重复预览） | `Please configure your target video specs before we write the CGI prompt.` |
| 成片：分辨率不适配该模型 | （可省略） | `This resolution is not compatible with the selected model. Change the resolution or the model.` |
| 词刚齐、等用户拍板 | 先全文贴词；可附 `Your CGI prompt is ready.` | `Modify the CGI prompt, or generate the clip?` 恰好两条 |
| 用户选继续、出片 | `Generating the CGI clip.` | （禁止再推词后提问） |
| 待合成 | `Your CGI clip is ready.` | `Sure, would you like to add BGM?` |
| 单段 / 合成结束 | `Your CGI clip is ready.` / `Your CGI video is ready.` | （禁止提问引导；可留 `Go to edit`） |

产物 `title`（无产物不编造）：`CGI Prompt` / `CGI Clip`。加 BGM 合成才另有 `Final Video without BGM - v1` / `Final Video BGM - v1` / `Final Video with BGM - v1`。禁止再写 `[First Frame]`。禁止给分段再落 BGM。

---

## 并行

问询一题一轮：发出后本轮结束，未答前 continuation 也不得进 `settings`。普通模式词成功拍先出提问；用户选继续后再成片。本链只有 1 段 `generate_video`。FastForward / AutoRun / Skip 后的下一阶段在 continuation 立刻开始。禁止词未打印就出片。
