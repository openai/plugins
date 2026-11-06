# AI Story — 下游输入适配（通用）

后一阶段需要前序产物时，对**每一个输入槽**按这次序取值。不要为某个举例写死「必须三槽」。

```text
provided  →  generated(done)  →  skip 则省略该槽  →  回退到次近同类素材  →  仍没有则 (none) / 不问该槽
```

- **禁止**把同一条素材挂两次来凑长度。
- **禁止**空 `<<<image_n>>>` / 空参考列表。
- 生成参考只含真实媒体，数量 = 主句里实际出现的占位符个数。
- **一律走 URL**：`generate_image` / `generate_video` / run_prompt / `merge_videos` 只传声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`，**禁止传 `nodeIds`**。URL 来自用户 Provide，或 `get_task` 成功后的素材 URL。禁止编造 HTTPS。
- 占位符只用 `<<<image_n>>>` / `<<<video_n>>>`（小写、从 1），与 URL 列表一一对应。历史里若是 `<<>>`，按当前绑定重写后再调用。
- 缺可选前序 **不得**阻塞后序。缺硬底线（故事身份、script、`video_prompts`、成片用的至少一块视觉）→ 问用户，不要空转。

## 文本槽

| 下游 | 优先取值 |
|------|----------|
| `script` instruction | object：`user_requirements` + 规格字段 + 问询字段（`story_goal` / `genre_tone` / `character_plan` / `visual_language`）。用户参考图 / 视频走 `image_urls` / `video_urls`（有才加），不把风格图放进去 |
| `frames` 出图 | 不调写作。`generate_image.prompt` = 剧本文各章第一条 `[start s - end s]` 镜头行原文（可带该章 Scene）。本拍只出图，禁止夹 STEP3。`image_urls` 只挂该章角色/场景图 URL，禁止挂预览图 / 风格图当唯一参考（风格已进资产）。失败只补该章；丢掉失效 URL，不挡各 `Video Prompt {i}` 打印 |
| `video_prompts` instruction | object：`script_markdown` + 规格；**禁止** `frames[]`。角色 / 场景 URL 有才加。Host 另喂 STEP2 细镜全文。写词时细镜主参考、剧本辅参考 |
| 成片正文 | `generate_video.prompt` = 已打印的该段 `Video Prompt {i}` `content`（按 SKILL §占位符补 `<<<image_n>>>`）+ 末尾 `no background music`。`image_urls` = 该项选中的角色/场景图 URL。禁止空 prompt |
| 合成 | 先停 BGM 闸门。选定后一次 `merge_videos(video_infos=各段 Long Video {i} 按时间线, is_generate_bgm)`，挂各段成片 URL。with→`true` / without 或 FastForward 未点名→`false`。禁止对单段配乐。**禁止传 `nodeIds`** |

Skip 且无正文 → 该描述槽写 `(none)`。Provide 的剧本文 / 提示词文原样绑定，不要再生成一份覆盖它。

`style = skip` 时即使内存里还留着旧 `StyleImageUrl`，也当作空，禁止再传。
剧本 / Video Prompt 文本**不是**生成参考，不要把它们的正文当 URL。

## 视觉槽

组列表时从左到右、有才加入：

1. 风格参考图（`style ≠ skip` 且已绑定；不是角色、不是场景、不是预览图）——**只给 assets 成图**
2. 该组选中的角色 / 道具设定图（该槽现行图：生成或替换上传，用法相同）
3. 该组选中的场景底板（该槽现行图：生成或替换上传，用法相同）
4. 用户另行指定的故事参考图（不是预览图、不是风格图）

**风格参考只辅助视觉，不是成片硬底线。** `script`：用户图 / 视频走 `image_urls` / `video_urls`；风格不当内容。`assets` 的每张 `generate_image` 必须带上已绑定风格图（`image_urls` 只含这一张）。
**预览图 / `video_prompts` / 成片不单独再挂风格图**——风格已经进角色和场景。

**预览图（`frames` 展示件）永远不是成片输入，也不是 STEP3 的 `image_urls`。**
`video_prompts` 的 `image_urls` = 角色 / 场景参考（有才加）。
`clips` 的图像输入 = 该项 `characters` + `background` 选中的 URL；文本输入 = 该段已打印 `content`。没有图则退到仍可用的角色图或场景图；再没有 → 问补图，不要硬出片。

角色设定画幅保持 `16:9`；场景底板保持 `16:9`；成片 / 预览图用 `VIDEO_RATIO`。不要把成片画幅回写到设定图。

普通模式剧本先打印再出剧本后提问；用户选继续后按内存提示词成图。提示词不是图；本批 `get_task` 未齐前只留进度句，禁止选项框。全部终态后一次状态句 + 资产后三选项。预览图同样：本批齐了一次状态句，禁止逐张提问。

## 回退作废（通用）

Rollback(S) 或 Reroute 使旧产物失效时：S 以及阶段图上 **S 之后**的阶段全部 `invalidated`。不要只作废举例里的列表；新加的阶段同样跟在目标后面就要作废。

重做 S 时带上用户这条建议。之后按**当前** Skip/Provide/Jump 自动顺跑，而不是按回退前的旧计划（本链 Rollback = AutoRun）。

内部交接也要作废：Rollback(`style`) 后不得再引用旧 `StyleImageUrl`。Rollback(`script`) 后不得再引用旧 `frames[]` / `groups[]` / 已打印 Video Prompt。Rollback(`frames`) 后不得再引用旧 `groups[]`。

## 实例（说明用，非封闭）

| 用户说法 | 算子 | 下游怎么适配 |
|----------|------|----------------|
| 点选风格库 / `Confirmed Styles info` | Provide / `done` | 绑 `StyleImageUrl`；禁止把 tool 回包当选择 |
| 自带风格图 | Provide(`style`) | 绑 `StyleImageUrl`；只给 assets 成图当画风；script 不把风格图当内容；不成片硬底线 |
| 不要风格参考 / 跳过风格 | Skip(`style`) | 后面不传风格图 |
| 直接做完、没选风格 | Jump(`clips`) | `style = skip`（除非已经绑了图）；不静默生成风格板 |
| 先看剧本再决定设定图 | 出剧本后提问 | 选继续才成图；选修改则重跑剧本 |
| 生成角色图和背景图 | Reroute(`assets`, run) | 用内存 `character_prompts` / `background_prompts` 成图 |
| 我自己上传设定图（成图前） | Reroute(`assets`, upload) → Provide | 一张一槽；禁止写成风格 |
| 点选某张资产再上传 | Provide 替换该槽 | 只换那一张；title / 下游挂法与生成图相同；不改风格图 |
| 不要场景底板 | Skip(`assets` 的背景槽) | 分镜 / 提示词 Background=`(none)`；成片不挂场景 URL |
| 不要角色设定图 | Skip(角色槽) | 成片只用场景图或用户参考图 |
| 别生成预览图 | Skip(`frames` 成图) | 只走 STEP3 合写（若要出 `video_prompts`）；不成图、成片不挂预览图 |
| 预览图有几张失败 | 只重出失败章 | 不重调 STEP3；各 `Video Prompt {i}` 已齐就先打印 |
| 自带角色图 | Provide(`assets` 角色) | 不生成该角色；下游当角色参考 |
| 自带完整剧本 | Provide(`script`) | 不跑 `long_video_step1_script`；下游用这份 Markdown |
| 自带视频提示词 | Provide(`video_prompts`) | 不跑 STEP3；按组绑定并打印。若还要预览图 → 从剧本镜头行出图 |
| 剧本后直接出视频 | Jump(`clips`) | assets 后先预览图（若 enabled），终态后再一次 STEP3；中间不推等待提问 |
| 成片后说剧本不对 | Rollback(`script`) | 作废 frames 及之后；重做剧本再顺跑 |
| 只要剧本、先不拍 | Jump(`script`) | 做到 script 停；不自动资产 / 成片 |
| 中途又传了场景图 | Provide(场景) | 即使曾 Skip，改为 provided，后续槽用这张图 |
| 跳过合成看分段 | Skip(`merge`) | 各段 `Long Video {i}` 完成后停；不调用合成 |
