# AI Animation — 角色 / 场景资产（`assets` / STEP1_ASSETS）

默认 `run`。普通模式必须先过剧本后提问（`ScriptAssetsGateDone=true`）才能成图。
同一 Meta-prompt（`long_video_step1_script`）带回的 `character_prompts[]` / `background_prompts[]` 是成图原料。

见 `slot-adaptation.md`。

## 何时才能成图

| `assets` 状态 | 本拍做什么 |
|---------------|------------|
| `run` 且闸门未过 | 只出剧本后提问（Host tools 两条），禁止成图 |
| `run` 且闸门已过 | 按内存提示词逐条 `generate_image` + `get_task`。只带进度句 |
| 用户点名 I'll upload 且尚无资产图 | 成图前 Provide：请用户发一张图 URL；禁止生成 |
| 成图后替换 | 先点选 title，再请用户发一张图 URL |
| `provided` | 只绑定用户图 URL |
| `skip` | 不成图；下游槽 `(none)` |
| FastForward / AutoRun | 成图后不推中间提问，立刻 Advance |

## 进度句（HARD — 成图拍）

发出资产 `generate_image` 的那一拍，只写进度句，并发出图。禁止选项框、确认列表。

正文：`Generating character and background images.`

禁止空结束。禁止再推剧本后提问。本批全部 `get_task` 终态后一次状态句，禁止逐张提问。
title：人 / 动物 = `[Character] {短名}`；关键道具 = `[Prop] {短名}`；场景 = `[Background] {短名}`。`{短名}` 取 `- 名称：` / `- 场景：`。失败张：同一拍正文点名该 title。

选 I'll upload **且还没有任何资产图**：立刻请用户发一张图 URL（成图前的 Provide，不是替换）。本轮消息里已经有图 → **不要再问**，按「成图前 Provide」把图绑到还没生成的槽。

**HARD — 一个入口。** 一次只收 **一张**。禁止「传到几张用几张」。

成图前 Provide：一张图绑一个还空的角色 / 道具 / 场景槽，title 按上表。禁止写成风格。禁止当成本链结束。

## 成图后替换（HARD — 点哪张换哪张）

资产图已经生成之后，**禁止**再收「任意张」。替换不是追加，不是风格图。

1. 用户点 `Upload to replace character and background images` → **先出点选提问**，不要立刻等图。Host tools 引导 `Which character or background image do you want to replace?`。`options` = 现有资产 title，一条一项，原文照抄（`[Character] …` / `[Prop] …` / `[Background] …`）。禁止夹带 `preview images`。禁止风格图 title。
2. 用户点其中一条 → 记下 `AssetReplaceSlot` = 该 title。同轮请用户发**一张**图 URL：正文 `Upload one image to replace {AssetReplaceSlot}.`
   只收 **一张**。多张只取第一张，丢掉其余。
3. 回包那一张 **只替换** `AssetReplaceSlot` 对应槽：同一个短名、同一个 title、同一个下游槽位。旧 URL 不再传给预览图 / STEP3 / 成片。新 URL 按 §成图后怎么用图 接进去。
4. 禁止把这张图写成 `StyleImageUrl`。风格图保持原样，不在这条替换路径里。
5. 禁止追加成第 7 张。禁止重新识图改槽（用户点的是背景就还是背景，即使画面里有人）。
6. 换完：一次状态句（当前全部资产）+ 资产后三选项。`AssetReplaceSlot` 清空。

## 成图后怎么用图（HARD — 生成和上传同一套）

每个资产槽只有一张现行图（生成或替换后的上传）。下游 **只认槽位**，不认来源：

- 预览图 `generate_image.image_urls`、STEP3 `image_urls`、成片 `generate_video.image_urls`：该章用到的角色 / 道具 / 场景，挂该槽现行 URL
- 上传替换后的用法 = 生成图的用法。禁止只给生成图挂 URL、把上传图丢掉或改挂风格
- 禁止把资产图和风格图对调

## 上传识图分槽（HARD — 仅成图前 Provide）

本链**禁止** `UnderstandContent`。成图前的 Provide 才按画面分槽；成图后替换按上一节，不走本表。

| 画面 | 绑到 |
|------|------|
| 人 / 脸 / 全身 / 角色设定 | `assets` 角色。`title`=`[Character] {短名}` |
| 单独道具 / 产品静物 | `assets` 道具。`title`=`[Prop] {短名}` |
| 空景 / 室内外环境 / 场地 | `assets` 场景。`title`=`[Background] {短名}` |
| 用户点名「当风格用」 | 才绑 `style = provided` |
| 说不清 | 先当角色参考，**不要**当风格 |

禁止把上传的第一张自动写成 `StyleImageUrl`。禁止不把已绑 URL 传给后续预览图 / 成片。

## 成图（默认 `run`）

还没有 `projectId` → 先 `create_project`。

每条真实 `generate_image`：

- `model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文（必填；`name` 只用来找行；禁止 `gpt-image-2` / Banana / `Nano Banana Pro` / `gpt2` / 把 `Nano Banana 2` 别名写入 / 省略 `model`）
- `project_id` 必填
- `prompt` = 该条目提示词正文。首次成图逐字。**每一张**（含背景）必须追加同一句套系锁（本链只做 animation）：`Same animation sheet as the other character/prop/background sheets in this batch: same line weight, palette, and rendering family. Empty location for backgrounds: no people, no fashion portrait, no second movie.` **重生成**再追加：`Fresh variation of the same subject: change camera height, framing, and pose or furniture staging. Do not recreate the previous still. Keep identity, wardrobe, location facts, and the same animation look.` 禁止把上一张资产图挂进这次 `image_urls`（风格参考除外）。若带风格图，prompt 用 `<<<image_1>>>` 点名该风格参考。
- 角色 / 道具设定：`aspectRatio` = `"16:9"`，`resolution` = 按 SKILL §生图分辨率取 **1K 档** 的 tool 声明原文（禁止写死 `1k`）
- 场景底板：`aspectRatio` = `"16:9"`，`resolution` 同上（1K 档 / tool 声明原文）。背景必须是空场地，禁止画出人物站在景里。
- 已绑定风格图且 `style ≠ skip`：每张调用都带上这张风格参考。`image_urls` = `[StyleImageUrl]`，且只含这一张。角色 / 道具 / 背景 **同一张**风格参考，禁止背景另挂别的图。`style = skip` 或未绑定 → 不要传风格图。禁止把资产图当风格参考。成图参考图只有这张风格图；不要把开场用户上传再挂成第二张风格。
- **HARD**：`generate_image` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`，记下素材 URL。并发多张时每个 `task_id` 都要轮询到终态。禁止把 `node_id` 当后续素材入参。

同轮并发：所有角色条目 + 所有场景条目一起发。
有 Avatar / 用户角色图 → 跳过对应角色成图。有匹配场景图 → 跳过对应场景成图。
用户只要「不要角色」→ 只 skip 角色槽，场景仍按当前计划。只要「不要场景」同理。

成功只在正文写状态句。文案按 SKILL §双通道。
`title`：角色 `[Character] {短名}`，道具 `[Prop] {短名}`，场景 `[Background] {短名}`。禁止写成 `[First Frame]` / `[Preview Image]`。
下一 enabled 阶段通常是 `frames`。主路径选项写 `preview images`。禁止写成 generate first-frame images / generate the clips。
**HARD — 成图成功拍必须停**：本批全部终态后一次状态句 **角色/场景资产图** + 推资产后提问。禁止读 `frames-prompt.md` / `video-prompts.md`，禁止预览图 `generate_image`，禁止 `long_video_step3_video_prompts`。用户没点 `preview images` / `Continue to preview images` 之前，当「所有图片任务完成了」也不许自动进 `frames`。

## Provide / Skip / Modify

- Provide：绑定用户图 URL，不再生成该槽。模特图不是场景底板，场景图不是角色设定。即使曾 Skip，中途上传也改为 provided。
- Skip：对应 Description 下游写 `(none)`；不得为凑槽复制剧本 URL。
- Modify / Rollback(`assets`) / 点 `Regenerate character and background images`：按内存提示词 + 重生成变化句重出全部角色/道具/场景图；仍须 Nano Banana 2 行；**不要**把旧资产图当参考。本批终态后一次状态句，title 保持原槽，再出同一组资产后提问。
- 点 `Upload to replace character and background images`：先出「点哪张」提问，再对该槽收一张 URL。见 §成图后替换。
- FastForward / AutoRun：成图后不推中间提问，立刻 Advance。

## 普通模式等待面（成图之后）

Host tools。引导 `Continue to preview images, regenerate the character and background images, or upload replacements?`
`options` 必须恰好这 3 条，顺序固定：

1. `preview images`
2. `Regenerate character and background images`
3. `Upload to replace character and background images`

禁止第 4 条。
点 1 / `Continue to preview images` → 进 `frames`。点 2 → 带变化句重出全部资产图。点 3 → 先点选要换的那张，再收一张 URL 替换该槽。自然语言 Skip preview images 仍按 Skip(`frames`)。
