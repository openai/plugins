# AI Story — 首帧展示图（`frames` 成图）

本阶段用户可见的只有首帧图。内部细镜 `frames[]` **不是**本文件出图依据，由**下一拍** STEP3 合写经 Host 跑 STEP2 产出。

| 层 | 可见性 | 能否 Skip |
|----|--------|-----------|
| 首帧成图 | 生成图（展示件） | 可以 Skip / Provide |
| 内部 `frames[]` | 不对用户展示 | 由 `video-prompts.md` 合写负责，不出图 |

输入：已确认剧本文 `script_markdown`、角色参考图 URL、场景参考图 URL。不要把历史无关附件挂上。首帧图是展示件，禁止传入 `video_prompts` 或成片。

## 两拍：先出图，再合写（HARD）

普通模式：资产成图成功拍**禁止**进入本文件。必须先停，推 `preview images`，等用户点了再跑。

预览图必须和资产图一样：**这一拍 `tool_calls` 只含 `generate_image`×N**。禁止夹带 run_prompt / STEP3。合写放到全部 `get_task` 终态后的**下一拍**（continuation，不用用户再点）。

用户点 `preview images` / `Continue to preview images`、或 FastForward 到 `frames` 时：

1. 成图仍 enabled 且图未发 → 本拍只出图。正文 `Generating preview images.` **禁止**同拍 STEP3。
2. 本批预览图全部 `get_task` 终态 → 一次状态句。下一拍只调一次 STEP3。正文 `Generating video prompts.`
3. 成图 Skip / 已齐、还没有打印 `Video Prompt {i}` → 本拍只调一次 STEP3。正文 `Generating video prompts.`
4. 已经打印任一 `Video Prompt {i}` → **禁止**再调 STEP3。只补失败首帧（若还要补）。

禁止：预览图和 STEP3 放进同一 `tool_calls`；用 `frames[].prompt` 出图；为出图调 `long_video_step2_frames`；对用户说缺记录 / canvas lost reference links / 请再试。失败章等这批终态后再补，**禁止**为补图再调 STEP3。

Skip 成图：本拍不出图，下一拍只走合写（若需要）。Provide 首帧：只绑定展示；若还要合写，下一拍再 STEP3。

## 进度句（HARD）

发出本批次的那一拍，正文 **必须**有一句 English 进度，禁止空结束：

| 本拍发出 | 正文 |
|----------|------|
| 只出预览图 | `Generating preview images.` |
| 只补失败章 | `Retrying the remaining preview images.` |
| 只合写 | `Generating video prompts.` |

禁止复用上一拍同一句。禁止中文。禁止在本拍再推等待提问。
**HARD — 状态句一次出齐**：本批预览图未全部终态 → 禁止 `Your preview images are ready.`、禁止提问。全部终态后一次状态句。失败张：同一拍正文点名缺的 `[Preview Image] {i}`。禁止每张成功立刻提问。半截词不打印。词里禁止写 BGM。

## 从剧本出图（HARD）

不调用任何写作 key。从已确认剧本文原文解析：

- 每一个 `## Chapter N`（或同等章节标题）取**第一条** `[start s - end s]` 镜头行 + 该章 `[Scene: …]`（有则带上）
- 一章一张。张数 **必须** = 章节数，不是全部时间段数，也不是 2 张
- `generate_image` 的 `prompt` = 这条镜头行原文（可紧接 Scene 原文）。禁止改写成 STEP2 式长生图词，禁止另调 LLM 扩写。有参考图时用 `<<<image_n>>>` 按序点名该章角色 / 场景
- `title` = `[Preview Image] {i}`（i 从 1，按章序）
- 同轮按章并发
- `model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文（`name` 只用来找行）
- `project_id` 必填
- `aspectRatio` = `VIDEO_RATIO`
- `resolution`：按 SKILL §生图分辨率，先由 `VIDEO_RESOLUTION` 映射到 1K / 2K / 4K 档，再取 `generate_image` 声明原文（禁止把目录 `1k` / `2k` / `4k` 或视频档 `768p` 原样传入）
- `image_urls` = **仅**该章用到的角色 / 场景**图** URL（有才加）。禁止挂风格图、其它章资产、预览图自己。不要把全部资产都挂到每一张上。
- 每张提交后必须 `get_task` 阻塞轮询到成功，记下素材 URL。全部终态前禁止发等待提问。

无任何可用视觉参考且模型需要图槽 → 问补图；纯文生图仍可按镜头行出图，不要空转。

## 失败补图（HARD）

首帧这批终态后立刻数成功张数。缺的或失败的（含超时）：

1. **立刻**只重出失败章，prompt 仍是该章第一条镜头行原文。每章最多补 1 次。本拍禁止再调 STEP3。
2. 丢掉失效 URL；只留还在的角色 / 场景 URL。全失效 → 不挂 `image_urls`，纯文重出。禁止把首帧失败解释成「缺细镜 / 请再试」。
3. 补图不得重调 STEP3 / STEP2。
4. 补图这批全部终态后一次状态句（成功张 + 此前已成功张）。失败张：正文必须点名 `[Preview Image] {i}`。补完仍缺 → 留下成功的，不要假装都齐；**不得**再推 `preview images`。禁止补一张问一次。

## 隔离（HARD）

1. 首帧图是展示件。禁止传入 `video_prompts` 或成片。
2. 禁止把 `source_reference_image` 或首帧路径当成视频输入。
3. Provide 的首帧图同样只绑定展示，不改变第 1 条。
4. 首帧失败 **不得**作废已打印的 `Video Prompt {i}`。

## Provide / Skip / Jump

- Skip 成图：不调用 `generate_image`。若还要生成 `video_prompts` → 下一拍只走合写。
- Provide 首帧：绑定用户图作展示。
- FastForward / AutoRun：先出图（若需要），终态后再合写，中间不推等待提问；提示词已齐且首帧已 Skip / 已发 / 已补过一轮 → 进 `clips`。禁止再调第二次写作。禁止把图和 STEP3 放进同一 `tool_calls`。

## 普通模式等待面

两路都齐（或成图 Skip / 提示词 provided / 失败章已补过一轮）**且**已打印全部 `Video Prompt {i}` → 第 1 选项 = generate the clips。**禁止**再推 generate video prompts，**禁止**再推 `preview images`。
只齐一路 → 只发状态句 + 已齐那路的全文/预览，不推成片提问。
另给 Modify / Skip 出口。Skip 成图且无可预览图时，不要假装「preview images are ready」。
