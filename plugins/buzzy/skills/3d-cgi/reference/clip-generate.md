# 3D CGI — 成片与合成（`clip` / `merge`）

只在当前阶段恰好是 `clip`、且本 run 已具备 **已打印** `CGI Prompt` 时，才调用视频工具。
内存里有词、对话里没有对应全文 → 先补打，**本拍禁止** `generate_video`。
成片调用前对照 `<available_models>` 该模型 Video 行 `resolutions`（H3 = `768p` / `2k`；2.0 / 2.0 Fast / 2.5 = `480p` / `720p`，以该行原文为准）。`VIDEO_RESOLUTION` 不在该行 → **禁止** `generate_video`，告知不适配：`This resolution is not compatible with the selected model. Change the resolution or the model.` 可重推规格提问。禁止默默改档。禁止把 `Seedance 2.0` 收成 Fast。
该行若有 `duration(s)` 且 `VIDEO_DURATION` 不在其中 → 不要默默改秒数，Host tools 再问一次合法档。
默认模型：`VIDEO_MODEL`。用户显式改模型只改模型，不授权提前到本步。

还没有 `projectId` → 先 `create_project`。

生成一段**新片子**。不要把用户参考片当成片输入（参考片只进 `video_urls` 当运动参考）。媒体只传 URL 字段，**禁止传 `nodeIds`**。
禁止再推分段确认列表。只发 `generate_video`。

## 成片输入（HARD）

| 槽 | 取值 |
|----|------|
| 文本 prompt | **必须填**已打印的 `CGI Prompt`。按 SKILL §占位符：若原文无 `<<<image_n>>>` / `<<<video_n>>>` 而本片挂了媒体，在词前加一行按序点名，再接原文，末尾 `no background music`。禁止摘要，禁止另造一份冲突词 |
| 时长 | `VIDEO_DURATION` |
| 画幅 | `VIDEO_RATIO`（按 SKILL §运行时填参收敛） |
| 分辨率 | `VIDEO_RESOLUTION`（按 SKILL §运行时填参收敛；不在该行 → 禁止出片） |
| 图像 | 用户 Provide 的参考图 URL → `image_urls`（有才加） |
| 参考视频 | 用户 Provide 的运动 / 转场参考 → `video_urls`（有才加） |
| 模型 | `VIDEO_MODEL`（API id，除非用户本 run 显式覆盖） |
| title | `CGI Clip` |
| `project_id` | 本会话 id |

`image_urls` / `video_urls` 顺序必须与 prompt 里 `<<<image_1>>>`… / `<<<video_1>>>`… 一致。

禁止：

- 空 `prompt`
- 把参考视频 URL 当成「已完成片」直接交付
- 在 Chat 里重写一遍再另造一份冲突词
- 让视频模型在词里写 / 生成 BGM。成片词只保留对白、口型、环境音、Foley；必须带 `no background music`
- 对单段配乐。本片只有 `CGI Clip` 一条片子
- 传 `nodeIds`

没有参考图也可以出片（纯文生）。有参考就挂，不要复制凑槽。

**HARD**：`generate_video` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（视频通常要数分钟，不要停、不要等用户下一句）。记下素材 URL。Apps widget 不能代替轮询。后续 `merge_videos` 用这条 URL。

回包 `Concurrent execution detected` / code `9002` / `5003` → **立刻只重试失败这次**，不要把已成功的再打一遍。最多补 2 次。

## 调度

- 普通模式：成片终态 → 状态句 → **停在 BGM 闸门**
- FastForward / AutoRun：成片后同轮进 `merge`；未点名 BGM → `is_generate_bgm=false`
- Modify / Rollback(`clip`)：仍用已打印词，不要改写正文；不要自动合成、不要给该组另配乐。AutoRun 仍按 SKILL 顺跑后续 enabled 阶段
- Skip(`merge`)：成片完成后停，不要合成

## 合成（`merge`）

输入：`CGI Clip` 的视频 URL（N=1 也是这一条）。

普通模式先停闸门，**不要直接合成**。Host tools。引导 = `Sure, would you like to add BGM?`。选项固定 `["Merge with BGM", "Merge without BGM"]`。用户选定后再调**一次**：

```text
merge_videos(projectId, video_infos=[CGI Clip URL], is_generate_bgm=true|false)
```

- `Merge with BGM` → `is_generate_bgm=true`
- `Merge without BGM` → `is_generate_bgm=false`
- 工具名是 `merge_videos`，不是 `MergeVideoWorkflow`，也不是 `regenerate_background_music`
- **禁止传 `nodeIds`**。成片走 `video_url` / `video_urls` / `video_infos` 里声明的 URL 字段
- 保留原画面、对白、环境音、时长。不要重生成或改画面。
- 不要加片头、片尾、转场、字幕、文字、logo、水印或任何新内容。
- `false` → 一条成片 `Final Video without BGM - v1`
- `true` → 三张：`Final Video without BGM - v1` / `Final Video BGM - v1` / `Final Video with BGM - v1`

成功：状态句 `Your CGI clip is ready.` / `Your CGI video is ready.` 可留 `Go to edit`，不要再写引导。
