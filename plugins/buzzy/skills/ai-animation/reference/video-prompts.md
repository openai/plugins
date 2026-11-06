# AI Animation — 视频提示词（`video_prompts` / STEP3_VIDEO_PROMPTS）

要出视频必须有一份可用的 `video_prompts`（生成或自供）。Jump / FastForward 会执行本步但不推中间提问，不是跳过本步。

已注册 key：`long_video_step3_video_prompts`（v14：Agent 传完整剧本；Host 把 STEP2 细镜全文零删减进 `records[]`。细镜主参考、剧本辅参考；同一事实两边否定才选边。Gemini **只**写 `groups[]`）。

禁止挂预览图。角色 / 场景用 `image_urls`（有才加）。**禁止传 `nodeIds`**。Agent **必须**把确认剧本文写入 `instruction.script_markdown`。

**HARD — Chat 打印替代画布节点**：回包后同一 continuation 必须把每一段 `content` 全文打印进对话（一段一块 `### Video Prompt {i}`，禁止 code fence，禁止拼成一份总稿只打一次，禁止说 on the canvas）。还没打印齐 1…N = 本步未完成，禁止出片。这是本链对「落画布文本节点」的替代。成片时 `generate_video.prompt` = 该段已打印 `content`（按 SKILL §占位符补图），不要指望宿主读节点。

## 一次合并写作（HARD — 默认）

当需要**生成** `video_prompts`，且内存还没有可用的分段词：

还没有 `projectId` → 先 `create_project`。

**只调用一次** `long_video_step3_video_prompts`。必传 `projectId`。
**禁止**先调 `long_video_step2_frames`，**禁止**把 `frames[]` 写进 `instruction`。
**禁止**与 `generate_image` / `generate_video` 同拍并行。
Host 内部两步：STEP2（用 Agent 这份剧本切细镜）→ 细镜原文 + 同一份剧本一起给 STEP3。**禁止**传 `frames[]`。**不是**没跑 STEP2。中间细镜不回给 Agent。两轮 Gemini 会比较久，不要降速、不要自己串 STEP2。**禁止** `defer_step2_thinking`。Agent 不要自己复述 Host 进度句。回包**没有** `frames[]`，也没有一份总 `content`。每项必须同时有 `name` / `title` / `content`（`name`=`title`=`Video Prompt {i}`）。台词校验由 Host 做。一次返回。预览图若仍要出：先发完 `generate_image`×N 并 `get_task` 终态，**下一拍**再调本 key。禁止和预览图放进同一 `tool_calls`。已经打印任一 `Video Prompt {i}` → **禁止**再调用本 key（失败重试、补预览图、合写超时都不构成第二次调用）。第一次失败且一段都没打印 → 只允许再调一次，正文 `Retrying video prompts.`

- 禁止顶层 `prompt` / `outputSchema` / LLM `model` / `texts`。`instruction.model` **必填** = `VIDEO_MODEL`（API id），不是这条禁令。
- `instruction` **必须是 object**。禁止 stringify。写成散文会报 `instruction must be a JSON object`，本步失败。
- **必须** `script_markdown` + `duration_sec` / `ratio` / `model`。**禁止** `frames[]`。
- 角色 / 场景图 URL 有才加进 `image_urls`。禁止挂预览图 / 风格图 / `video_urls`。
- **禁止**把规格说明、格式要求、STEP2 细镜 JSON 拼成一段 string。下面这种调用 = 非法，必须改成下一节 object 后重发，禁止原样重试：

```text
instruction = "Confirmed settings: duration=60 seconds; ratio=9:16.\nReturn ONE object:...\nSTEP2 frame records (JSON, text only):[{...}]"
image_urls = ["https://..."]
```

```json
{
  "prompt_key": "long_video_step3_video_prompts",
  "projectId": "{projectId}",
  "image_urls": ["https://character-or-scene"],
  "instruction": {
    "duration_sec": 45,
    "ratio": "16:9",
    "model": "seedance-2.0",
    "script_markdown": "# title\\n\\n## Chapter 1\\n[0.0s - 5.0s] ..."
  }
}
```

`script_markdown` 用已确认的剧本文。角色 / 场景用 `image_urls`（有才加）。
若本次是 `Modify` / Rollback，同一 object 上加 `"modify_request": "{user request verbatim}"`。禁止传 `frames[]`。
**禁止** `defer_step2_thinking`。

内存已有 N 段已打印的 `Video Prompt {i}`（刚合并写完，本步只是 Advance）→ **不要再调 LLM**，只确认这些词已打印；缺哪个就补打缺的，禁止重开写作。
预览图缺了走 `frames-prompt.md`（从剧本出图），不要再调本 key，不要调 STEP2。预览图失败不得重跑本步。

## 成功（分段打印 HARD）

- `result.items.length` = 组数。**每一项**单独打印，不要拼回一份。
- `items[i].name` = `items[i].title` = `Video Prompt {i}`（i 从 1）
- `items[i].content` = **仅**该段词。回包**没有** `video_prompt` 字段。禁止一项里装全部组。禁止一项里再带 `frames[]` / 总 `content`。
- 同项还可读 `duration_sec` / `characters` / `background` / `chapter` / `start` / `end`（选择器）。不要读 `frames[]`。不要读 `items[0].groups`。不要把预览图挂进本次调用。
- Host 已校验该章剧本镜头行引号对白。Agent **不要**再为台词重调 STEP3。
- 打印块数 = `items.length`。禁止把多项拼成一个 `Video Prompts` 段落。
- 引导句：`Here are the video prompts:`（重做则 `Here are the updated video prompts:`）。然后按 i 升序：

```markdown
### Video Prompt {i}

{items[i].content}
```

段与段之间空一行。禁止 code fence。可附 `Your video prompts are ready.`
- 校验通过后：`VideoPromptsGenerated = true`。写入内存 `VideoPromptTexts[i]` / `VideoPromptDurations[i]` / 该段 `characters` / `background` 短名，供成片选 URL。不因单张预览图失败作废。预览图若仍 enabled 且未发 → 先按 `frames-prompt.md` 出图，终态后再调本 key。没发过或有失败章则按 `frames-prompt.md` 从剧本补发。不要空转、不要再调写作。
- **HARD — 先打印再成片**：这一拍只打印词，**禁止**同拍 `generate_video`。还没打印齐 `Video Prompt 1…N` 就出片 = 非法。FastForward / AutoRun 也要先打印，下一拍再成片。

## 成片时怎么用（选择器，不在本步调用视频）

见 `clips-merge.md`。每段 `generate_video.prompt` = 该段已打印 `content`（按 SKILL §占位符补 `<<<image_n>>>`），不要摘要，不要贴整份旧总稿。词里只写对白、环境音、口型，**禁止**写 BGM / background music / scored music。加 BGM 只在合成闸门后一次 `merge_videos(is_generate_bgm=true)`，不对单段配乐。

## Provide / Skip / Jump

- 用户粘贴 / 上传分组提示词 → `provided`：一段一段打印；能对齐就不要再调 LLM 覆盖用户原文。此时若还要预览图 → 按 `frames-prompt.md` 从剧本出图，不调 STEP2。
- 不能 Skip 后再进 `clips`。
- FastForward / AutoRun：打印后只发状态句；预览图若仍 enabled 且未出图 → 先从剧本出图，终态后再合写。禁止再调第二次写作。禁止图和 STEP3 同一 `tool_calls`。

## 普通模式等待面

同轮 Host tools。第 1 选项 = generate the clips（**仅当**已打印全部 `Video Prompt {i}`）。另给 Modify。不要在点 Continue / Jump 之前调用视频工具。
分段词已打印时，预览图等待面也不得再推 generate video prompts / `preview images`。预览图还在补失败章 → 先打印各 `Video Prompt {i}`，不挡成片提问。还没打印这些词 → 先打印，不要出片。
