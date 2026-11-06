# AI Story — 成片与合成（`clips` / `merge`）

只在当前阶段恰好是 `clips`、且本 run 已具备 script + **已打印全部** `Video Prompt {i}` + 至少一块视觉参考时，才调用视频工具。
内存里有词、对话里没有对应全文 → 先补打，**本拍禁止** `generate_video`。
成片调用前对照 `<available_models>` 该模型 Video 行 `resolutions`（H3 = `768p` / `2k`；2.0 / 2.0 Fast / 2.5 = `480p` / `720p`，以该行原文为准）。`VIDEO_RESOLUTION` 不在该行 → **禁止** `generate_video`，告知不适配：`This resolution is not compatible with the selected model. Change the resolution or the model.` 可重推规格提问。禁止默默改档。禁止把 `Seedance 2.0` 收成 Fast。
默认模型：`VIDEO_MODEL`。用户显式改模型只改模型，不授权提前到本步。

还没有 `projectId` → 先 `create_project`。

每组生成一段**新片子**。不要把用户参考片当成片输入。媒体只传 URL 字段，**禁止传 `nodeIds`**。
禁止再推分段确认列表。只发 `generate_video`。

## 成片输入（HARD）

对每个已打印的 `Video Prompt {i}`（即 STEP3 `items[i-1]`）：

| 槽 | 取值 |
|----|------|
| 文本 prompt | **必须填**该段已打印 `content`。按 SKILL §占位符：若原文无 `<<<image_n>>>` 而本段挂了图，在词前加一行按序点名角色/道具/场景，再接原文，末尾 `no background music`。禁止摘要，禁止贴整份旧总稿 |
| 时长 | 该项的 `duration_sec` |
| 画幅 | `VIDEO_RATIO`（按 SKILL §运行时填参收敛） |
| 分辨率 | `VIDEO_RESOLUTION`（按 SKILL §运行时填参收敛；不在该行 → 禁止出片） |
| 图像 | 仅该项 `characters` 选中的角色图 URL + `background` 选中的场景图 URL → `image_urls` |
| 模型 | `VIDEO_MODEL`（API id，除非用户本 run 显式覆盖） |
| title | `Long Video {i}` |
| `project_id` | 本会话 id |

`image_urls` 顺序必须与 prompt 里 `<<<image_1>>>`… 一致：角色图…，场景图。
只挂**这一段**的图。禁止把其它段的词、预览图、风格图挂上。

禁止：

- 空 `prompt`（本链没有画布节点可读）
- 挂 STEP2 预览图 / `source_reference_image` / 预览图 URL
- 把别人的 Video Prompt 或旧的总稿当成本段输入
- 在 Chat 里重写一遍再另造一份冲突词
- 让视频模型在词里写 / 生成 BGM。成片词只保留对白、口型、环境音；必须带 `no background music`
- 对单段配乐。分段只有 `Long Video {i}` 一条片子
- 传 `nodeIds`

缺该组角色图 → 省略角色槽，不要复制场景图来凑。两组都缺且全片没有任何视觉参考 → 停下来请用户补图。

**HARD**：每段 `generate_video` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（视频通常要数分钟，不要停、不要等用户下一句）。记下素材 URL。Apps widget 不能代替轮询。后续 `merge_videos` 的各段成片用这些 URL。

**HARD — 分批成片**：同一拍最多 **4** 段 `generate_video`。多于 4 段先发前 4，等这批 `get_task` 终态再发下一批。禁止一次打满全部章节。
回包 `Concurrent execution detected` / code `9002` / `5003` → **立刻只重试失败段**（仍最多 4 段一批），不要把已成功的再打一遍。每段最多补 2 次。

本链**不**要求后续段参照 Video 1（与 ugc-ads 不同）。各段只吃自己的词 + 自己的角色/场景图。

## 调度

- 普通模式：发齐本组成片并全部终态 → 状态句 → **停在 BGM 闸门**（含 N=1）
- FastForward / AutoRun：发齐后同轮进 `merge`；未点名 BGM → `is_generate_bgm=false`
- Modify / Rollback(`clips`)：只重做被点名的组；仍用该组已打印词，不要改写正文；不要自动合成、不要给该组另配乐。AutoRun 仍按 SKILL 顺跑后续 enabled 阶段
- Skip(`merge`)：分段都完成后停，不要合成

## 合成（`merge`）

输入：全部成片 `Long Video {i}` 的视频 URL（N=1 也是这一条）。

普通模式先停闸门，**不要直接合成**。Host tools。引导 = `Sure, would you like to add BGM?`。选项固定 `["Merge with BGM", "Merge without BGM"]`。用户选定后再调**一次**：

```text
merge_videos(projectId, video_infos=[各段成片 URL 按时间线], is_generate_bgm=true|false)
```

- `Merge with BGM` → `is_generate_bgm=true`
- `Merge without BGM` → `is_generate_bgm=false`
- 工具名是 `merge_videos`，不是 `MergeVideoWorkflow`，也不是 `regenerate_background_music`
- **禁止传 `nodeIds`**。各段成片走 `video_url` / `video_urls` / `video_infos` 里声明的 URL 字段
- `video_infos` 按原剧本时间线 `start` 升序；时间戳相同则保持剧本与原数组顺序。按该顺序首尾相接，不漏、不重、不重排、不裁切。无 BGM 拼接必须连上**全部**分段成片。
- 保留每段原画面、对白、环境音、时长与顺序。不要重生成或改任何一段。
- 直接接成一条完整视频。不要加片头、片尾、转场、字幕、文字、logo、水印或任何新内容。
- Host 先拼完整片；`true` 时再对**整条**理解并配乐。禁止按段理解视频去配乐。
- `false` → 一条成片 `Final Video without BGM - v1`
- `true` → 三张：`Final Video without BGM - v1` / `Final Video BGM - v1` / `Final Video with BGM - v1`
- 核对无 BGM 成片总时长 = 各段时长之和

成功：状态句 `Your long video is ready.` / `Your full long video is ready.` 可留 `Go to edit`，不要再写引导。
