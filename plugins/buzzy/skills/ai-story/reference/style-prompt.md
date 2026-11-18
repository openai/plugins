# AI Story — 风格参考（`style`）

决策闸门。默认 `pending`。`StyleTemplate` 冻结为 `ai_film`。风格库走 `choose_skill_asset`，禁止 `PushStyleList`。
风格库交出 **一张风格参考图**，用来约束后面整条链的视觉。它不是角色设定、不是场景底板、不是预览图、不是成片输入。

见 `slot-adaptation.md`。

## 何时才能进 `settings`

| `style` 状态 | 本拍做什么 |
|--------------|------------|
| `pending`（未发卡 / 等确认） | **只**调 `choose_skill_asset`。禁止规格提问、禁止 `generate_image`、禁止同拍再发 Host tools 风格方向题 |
| 确认消息含 `Confirmed Styles info` 且能解析出图 URL | 绑定后 `done`，同轮进 `settings` |
| 无控件宿主：Host tools 点了库名 | 用该 `name` 在上一拍 `items` 里找回图 URL，绑定后 `done` |
| 用户交出风格图 URL（点名当风格） | 绑定后 `provided`，同轮进 `settings` |
| `provided` | 只绑定卡外自带风格图 |
| `skip` | 不传风格图；同轮进 `settings` |
| FastForward / Jump(`settings`+) 且未 skip/provided | `style = skip`。不发卡、**禁止**静默生成 |

开场问询已绑风格图 → `provided`，不要再发卡。已明确 Skip 风格 → 不要再发卡。

## 发卡（HARD — `pending` 且 `IntentDone=true`）

同轮必须调一次 `choose_skill_asset`，**禁止**先出规格提问、禁止先 `generate_image`、禁止同拍 `create_project`、禁止同拍 Host tools。

| 槽 | 值 |
|----|-----|
| tool | `choose_skill_asset` |
| `style_template` | `"ai_film"` |
| `title` | `"Styles"` |

只发这一次调用。不要缓存候选。每次重进重新发卡。
**返回值不是用户选择**：`items` / 控件打开只表示列表已出。有控件的宿主 → **停住**，等用户发 `Confirmed Styles info`。禁止把返回列表当成已选。禁止同拍再调 Host tools。
**无控件宿主**（结果带 `fallback.message`，或宿主渲染不了 Apps iframe）→ 同一 continuation 对 Host tools 发一题：问句 `Pick a style reference image for this video.`；`options` = 本次返回的 `items[].name` **全部列出**（禁止自己现写 3 条电影方向）。若宿主单次 options 有上限，按返回顺序取前 N 条，问句写明用户也可打风格名。

含糊重发必须仍是 `style_template: "ai_film"` + `title: "Styles"`，禁止改 key、禁止另发第二张卡。

## 回程（上一拍是 `choose_skill_asset` 或无控件 Host tools）

按这次序只取一条：

1. 消息含 `Confirmed Styles info` / `Confirmed <title> info` → 解析 `name:` 与 `image:`（无 `image:` 则 `hdImage` / 第一条 https）。写入 `StyleName` + `StyleImageUrl`（`image:` 原文）。`style = done`。**不要**把这张图拷进角色 / 场景 / 用户故事参考槽。同轮 Advance 到 `settings`。
   **例外**：上一拍是资产替换 / 成图前上传回来的图，**不要**走本条。按 `assets-prompt.md` 识图分槽，默认当角色/场景，除非用户点名当风格。
2. 无控件 Host tools 回了某个 `items[].name`（或 Other 打了库里的风格名）→ 在上一拍 `items` 里按 `name` 对齐，取 `hdImage` 否则 `icon`，写入 `StyleImageUrl` + `StyleName`。`style = done`。同轮进 `settings`。对不上 → 用同一批 `name` 重发 Host tools，不要进 `settings`。
3. 本轮携带非空风格图 URL（用户点名当风格，或消息里明确是 style reference）→ 取 **第一张** URL 原文写入 `StyleImageUrl`。`style = provided`。同轮进 `settings`。
4. 明确 Skip / Continue / Next，或 FastForward / Jump(`settings`+)，且没图 → `StyleImageUrl = ""`，`style = skip`。同轮进 `settings`。
5. 含糊聊天且风格卡仍有效 → 用同一 `style_template` / `title` 重发 `choose_skill_asset`。不要空回复，不要误判 Skip，不要换库。

`choose_skill_asset` 刚返回、还没有上面任一条 → **停住**。禁止 Advance 到 `settings`。

## Provide / Skip / Jump / Reroute

- Provide：绑定用户风格图 URL，不再发卡。模特图 / 角色图 / 场景图不是风格参考，除非用户点名「当风格用」。
- Skip：下游不传 `StyleImageUrl`。
- Jump(`settings` 或更后)：不堵在风格卡。已有图就绑定；没有则 `skip`。**禁止**静默生成。
- Reroute(`style`, pick)：重新发卡，仍是 `ai_film` + `Styles`。

Rollback(`style`) / 换风格 / 重开 → `style` 及之后全部 `invalidated`，`StyleTemplate` 仍是 `ai_film`，重新发卡。禁止按故事 brief 改成动画库。

## 普通模式等待面

发卡当拍：只调 `choose_skill_asset`，不发状态句。无控件 fallback 才发 Host tools，引导 `Pick a style reference image for this video.`
点选刚绑定、下一拍是规格：状态句 `Your style reference is ready.`；引导 `Review the style reference, then set up your video.`
FastForward / AutoRun：不发中间提问，风格 resolved 后立刻 `settings`。
