# AI Animation — 剧本（`script` / STEP1_SCRIPT）

工具 = `run_prompt`（`prompt_key=long_video_step1_script`）。不要传顶层 `prompt` / `outputSchema` / LLM `model`。成片模型写在 `instruction.model` = `VIDEO_MODEL`。必传 `projectId`。
`content` = 完整渲染 Markdown 剧本（`story_markdown`）；`name` = `title`。
**HARD — Chat 全文**：同一 continuation 必须把 `content` **原文全文贴进对话**（禁止 code fence，禁止摘要，禁止说 on the canvas）。这是本链对「落画布文本节点」的替代。

输入：用户 verbatim 需求 + 已确认 `VIDEO_RATIO` / `VIDEO_RESOLUTION` / `VIDEO_DURATION` / `VIDEO_MODEL` + 问询结论。有用户参考图 / 视频时传 `image_urls` / `video_urls`（内容参考）。**禁止传 `nodeIds`**。还没有 `projectId` 就先 `create_project`。

Meta-prompt 使用已注册的 `prompt_key=long_video_step1_script`。不要把 YAML / `STEP1_WRITER_SPEC` 贴进 `instruction`。

Agent 不要自己复述 Host thinking 进度句。

## 生成

- `prompt_key` = `"long_video_step1_script"`
- `projectId` 必填
- 禁止顶层 `prompt` / `outputSchema` / LLM `model` / `texts`。`instruction.model` **必填** = `VIDEO_MODEL`（API id：`seedance-2.5` / `seedance-2.0` / `dreamina-seedance-2-0-fast-260128` / `MiniMax-H3`），禁止传显示名 `Seedance 2.5` / `Seedance 2.0` / `Seedance 2.0 Fast`。这不是 LLM 模型字段。缺字段、传显示名、或因「禁止 model」整段丢掉 = 本步失败。禁止省略后让 YAML 按 Seedance 2.5 切 25–30s 章。禁止把 `Seedance 2.0` 收成 Fast。
- **用户参考媒体（HARD）**：有用户上传的参考图 → `image_urls` 只放这些图的 URL（有才加）。有用户上传的参考视频 → `video_urls` 只放这些视频的 URL（有才加）。没有则省略，不要空数组。这是写剧本和 `character_prompts` / `background_prompts` 的内容参考。
- **禁止**把 `StyleImageUrl` / 风格图放进 `image_urls` / `image_url` / `video_urls` / `video_url`。风格图只在 `assets` 成图时当画风参考，不进本步。
- **禁止传 `nodeIds`**。
- `instruction` **必须是 object**。禁止先写成一段 prose 再当 string 传入。
- **禁止**与 `generate_image` / `generate_video` 同拍并行。

```json
{
  "duration_sec": "{VIDEO_DURATION}",
  "ratio": "{VIDEO_RATIO}",
  "resolution": "{VIDEO_RESOLUTION}",
  "model": "{VIDEO_MODEL}",
  "output_language": "{user_lang}",
  "language_rule": "All readable script body, dialogues, storyboard descriptions, and readable tags must be in output_language. Image-prompt vocabulary after each readable tag must be English. Structural heading literals stay `## Main Story` and `## Chapter N - ...`.",
  "story_goal": "{StoryGoalOrNone}",
  "genre_tone": "{GenreToneOrNone}",
  "character_plan": "{CharacterPlanOrNone}",
  "visual_language": "{VisualLanguageOrNone}",
  "user_requirements": "{full user brief verbatim}"
}
```

`duration_sec` 用数字。空槽用 `""`，不要写 `None` 散文。
若本次是 `Modify` / Rollback 重跑，同一 object 加 `"modify_request": "{user request verbatim}"`。

## 成功

- `result.items[0].name` = `title`；`content` = `story_markdown`。记下该项全文为 `ScriptMarkdown`。
- 读取 `character_prompts` / `background_prompts` **写入内存**，等用户过剧本后提问再成图。不要依赖 `result.text`。背景提示词必须和角色 / 道具同一套光线与调色，空场地、不要把人物画进背景。
- **只展示完全渲染的 Markdown 剧本。** 不要展示 JSON、转义文本、分镜提示词或图片。禁止 code fence。
- 引导句可用 `Here is the story script:`（重做则 `Here is the updated story script:`），然后空一行贴全文。可附 `Your story script is ready.`
- **HARD — 普通模式先停。** `Stage[script]=done`。`character_prompts` / `background_prompts` 写入内存。**禁止**本拍 `generate_image`。同轮贴剧本 + 按 SKILL §`assets` 出剧本后提问，然后停。FastForward / AutoRun 才按 `assets-prompt.md` 成图。

## Provide / Skip / Jump

- 用户交出完整剧本 → `Stage[script]=provided`，整理后全文贴进 Chat；能解析出角色 / 场景提示则写入内存供下游，解析不出就 `(none)`，不要为了补提示再偷偷生成一份新剧本盖掉用户文。
- 不能 Skip 后再声称能出视频。Jump(`script`) 普通模式仍出剧本后提问。
- FastForward / Jump(`assets` 或更后) / AutoRun：`assets` 未 Skip / Provide 则同轮成图；成图后不推中间提问。

## 普通模式（剧本成功拍）

同轮：贴全文 + 剧本后提问。禁止成图。用户点继续后才按 `assets-prompt.md` 出图。
