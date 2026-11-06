# UGC ADS — 分镜表格式（HARD）

模板产出字段 `content` = **Markdown 表格纯文本**（**9** 列）；`name` = `[Script] UGC Storyboard`。
竖排 `字段: 值` **不会**被渲染为表 → **禁止**竖排输出。
本文件只做**返回校验**（9 列管道表 / 列序固定 / GFM 分隔行），不拼进模板输入。

对话渲染（HARD）：**不要**把 `|` 管道表贴进对话。窄聊天栏会把 9 列折成极高行。同一 continuation 必须按下方「对话分镜卡片」从每一表行转写卡片，然后发 Host tools Continue/Revise。禁止 code fence。

---

## 表头（9 列，顺序 HARD）

列语义顺序固定。**表头列名固定 English**；单元格正文跟 `SessionScriptLanguage`；语义必须与下列 9 列一一对应（**禁止**增删列 / 打乱顺序 / 自创列）：

| # | 列语义（English 锚名） |
|---|------------------------|
| 1 | Shot Number |
| 2 | Duration |
| 3 | Shooting Style |
| 4 | Action |
| 5 | Expression |
| 6 | Lighting |
| 7 | Lip Sync |
| 8 | Voiceover Narration |
| 9 | On-Screen Text |

**管道表头示例（User Language = English 时）：**

```markdown
| Shot Number | Duration | Shooting Style | Action | Expression | Lighting | Lip Sync | Voiceover Narration | On-Screen Text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

**必须**先输出表头行，再输出 `| --- | … |` 分隔行（**正好 9 段** `---`），再输出数据行（每行也是 **9** 个 cell）。

**禁止（模板 `content` 不合格）**：
- 竖排列名或 `Shot Number: …` 块（这是 Chat 卡片的写法，禁止写进 `content`）
- 把 9 个列名各占一行列出（无 `|` 管道）
- 中文表头；或与上表不一致的列名
- `Character/Subject` / `Scene` 列（身份与环境靠角色图 / 场景图，不进表）
- `Music/BGM` / `Video` 列；旧名 `Scene Number` / `Visual/Framing` / `On-Screen Text (OST)` 等（本列表头必须是 `On-Screen Text`）
- 省略口型同步列或花字列（不得退回 8 列）
- 单元格内未转义的 `|`

**表头与单元格正文**语言 = `SessionScriptLanguage`（`Custom`→English）；列语义顺序仍按上表 9 列。

---

## 对话分镜卡片（HARD — 只约束 Chat，不改 `content`）

`content` 仍是 9 列管道表（extract / 成片只认这张表）。Chat 只给人看，必须转成卡片。字段与上表 9 列一一对应：Shot Number / Duration 进标题，其余 7 列各一条 bullet，**标签必须是表头原文**。

固定结构（用户可见 English 标签；单元格正文跟 `SessionScriptLanguage`，禁止改写口播 / 动作 / 口型 / 花字事实）：

1. 引导句：`Here is the storyboard script:`（重做则 `Here is the updated storyboard script:`）
2. 按 Shot Number 升序，每镜一块；镜与镜之间 **仅 1 个空行**
3. 单镜模板：

```markdown
### Shot {Shot Number} · {Duration}
- **Shooting Style:** {Shooting Style}
- **Action:** {Action}
- **Expression:** {Expression}
- **Lighting:** {Lighting}
- **Lip Sync:** {Lip Sync}
- **Voiceover Narration:** {Voiceover Narration}
- **On-Screen Text:** {On-Screen Text}
```

**禁止（对话）**：
- 把 `|` 管道表、表头或 `| --- |` 贴进 Chat
- 用 extract 的 9 条 bullet 模板（会重复 Shot Number / Duration）
- code fence
- 增删卡片字段、改标签措辞、合并多镜进一块
- 写回 `Character/Subject` / `Scene` / `On screen` / `Line` 等旧卡片字段

对话卡片示例（对应下方表示例前 2 行）：

```markdown
Here is the storyboard script:

### Shot 1 · 3s
- **Shooting Style:** Handheld phone selfie, slight natural jitter
- **Action:** Holds the can close to the face and points at the label while speaking
- **Expression:** Starts attentive, livens mid-line, eases on the last word
- **Lighting:** Natural daylight coming from a side window, low contrast
- **Lip Sync:** On-camera: speaking directly to lens/mirror, mouth visible
- **Voiceover Narration:** Guys, I found my favorite drink.
- **On-Screen Text:** New favorite 😍

### Shot 2 · 3s
- **Shooting Style:** Close-up handheld shot, subtle autofocus adjustment
- **Action:** Rotates the can slowly to show the label; mouth out of frame
- **Expression:** Off-screen
- **Lighting:** Soft, diffused daylight from the kitchen window
- **Lip Sync:** Off-camera V.O.: hands/product close-up, protagonist's mouth not shown, narration plays as voiceover over the action
- **Voiceover Narration:** Strawberry Bliss juice. Look at this.
- **On-Screen Text:** Look at this ✨
```

---

## 列说明

| # | 表头 | 要求 |
|---|------|------|
| 1 | Shot Number | 从 1 递增整数 |
| 2 | Duration | 单镜时长：`3s`、`2.5s`、`4s` 等 |
| 3 | Shooting Style | **必须**手持 / 非稳定器 / 非专业器材质感 |
| 4 | Action | **只写动作**。恰好一个主动作，且必须能在该镜 `Duration` 内做完。允许伴随眨眼、呼吸、轻微点头/转头、视线挪动。禁止写身份、外貌、服装、地点、环境（靠角色图 / 场景图）。出镜说话镜须含口型/下颌/停顿/呼吸 |
| 5 | Expression | **必须写该镜内的变化**（起 → 中 → 收）。禁止整镜一个情绪标签。画外/无人物时写 `Off-screen` / `N/A` |
| 6 | Lighting | **禁止**棚拍光；优先自然光、家居环境光等 |
| 7 | Lip Sync | 每镜必填；**单元格语言 = `SessionScriptLanguage`**。语义二选一：出镜说话 / 画外 V.O.。`On-camera: speaking…` / `Off-camera V.O.: …` |
| 8 | Voiceover Narration | 该镜口播；语言 = `SessionScriptLanguage`。**有说话（HARD）**：英文词数 ≈ `Duration` 秒 × 2（约每秒 2 词，允许 ±1）。无说话 → `N/A`（禁止空 cell，禁止用更密台词填满时长） |
| 9 | On-Screen Text | 烧进画面的花字 / 字幕 / 标签。语言 = `SessionScriptLanguage`。**3–15 词**，是当前口播的概括，**无需**与 Voiceover 逐字一致；允许表情。无屏幕字 → `N/A` |

单元格内**禁止**未转义的 `|`。

### Lip-Sync 一致性（HARD）

- 出镜说话镜：Voiceover = 画面中正在说的那句；**词数 ≈ Duration × 2**（约每秒 2 词，±1）。Action/Expression 须写出口型、停顿，以及表情/语气随台词的起伏；禁止整镜同一表情、禁止匀速平念
- 画外 V.O. 镜：嘴部不得成为画面焦点；若该镜仍有口播，词数同样 ≈ Duration × 2
- 全片至少 **40%** 镜为出镜说话；其余为 B-roll/cutaway
- 禁止把过长口播塞进单条出镜长镜头；禁止为填满时长把语速写到每秒 2 词以上

---

## 输出范围（HARD）

- **只**输出完整 **9 列** Markdown 管道表。行数目标见下方「镜数与时长」；少于目标**不**因此重试。
- **禁止**表后 Character Description / Scene Description。
- **禁止**表前/表后其它解释、建议、推理正文。
- 成片拆分按第 1 列（镜号）升序 + 第 2 列（时长）与镜数联合贪心（列位置固定，与表头语言无关）；每段 ≤15s 且 ≤3 镜。

---

## 成片拆分（内部 — 无 Video 列）

按 **Shot Number 升序** + **Duration / 镜数贪心**拆成 **N 段**。每段必须同时满足：
- Duration 合计 **≤ 15s**
- Shot 数量 **≤ 3**（HARD）

```
VideoSegments = []
current = []
acc = 0
按 Shot Number 升序遍历每一行 row:
  if (acc + row.Duration > 15s) or (len(current) >= 3):
    VideoSegments.push(current)
    current = [row]
    acc = row.Duration
  else:
    current.push(row)
    acc += row.Duration
VideoSegments.push(current)
SegmentCount = VideoSegments.length
```

**校验（HARD）**：
1. 每段 Duration 合计 **≤ 15s**
2. 每段 Shot 数量 **≤ 3**（含 1–3；禁止 4 镜及以上落在同一段）
3. 各段之和 = 全片总时长
4. 单行 Duration **> 15s** → 拆分失败，提示编辑脚本
5. 典型：在 ≤15s 约束外，若连续镜较多会因镜数上限额外切段（例如 4 镜合计 12s → 仍拆为 3+1 两段）

---

## 镜数与时长（HARD）

行数按所选时长灵活算，**每 30 秒对应 8 行**：

```text
StoryboardRowCount = round(SessionVideoDuration / 30 × 8)
```

三档对照（目标，不是硬校验）：

| 规格 | 映射秒 `SessionVideoDuration` | 目标行数 |
|--------|------------------------------|----------|
| `<15s` | 12 | **3** |
| `15s-30s` | 25 | **7** |
| `30s-1min` | 45 | **12** |

- 行数目标 **≥ `StoryboardRowCount`**，可以更多。少于目标也照收，**不要**因行数重试。
- 各镜 Duration 合计必须 ≈ `SessionVideoDuration`。单镜大约 3–4s，禁止为凑行数把单镜压到 1–2s。
- 分段约束：每段 **≤15s 且 ≤3 镜**；extract / 成片按此双约束拆分。
- 有说话则口播词数严格按 **约每秒 2 词**（`词数 ≈ Duration × 2`，±1）；无说话写 `N/A`。词数均匀分布，但**语调必须有轻重和起伏**，禁止节拍器式平念。与画面动作自然咬合；On-camera 段须在该镜 Duration 内按此语速可自然说完。对照：2s≈4 词、3s≈6 词、4s≈8 词、5s≈10 词

---

## 内容规则

- UGC 手持 / 手机自拍 / 自然手抖 / 非专业器材；Lighting 避免棚拍感
- 人物镜与产品特写交替；产品特写 / 手部镜 Lip Sync 通常为 Off-camera V.O.；Expression 常用 `Off-screen`
- 禁止空 cell；禁止合并单元格；禁止表格外散文。行数不够不是重试理由。

---

## 示例（节选 2 行）

```markdown
| Shot Number | Duration | Shooting Style | Action | Expression | Lighting | Lip Sync | Voiceover Narration | On-Screen Text |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3s | Handheld phone selfie, slight natural jitter | Holds the can close to the face and points at the label while speaking | Starts attentive, livens mid-line, eases on the last word | Natural daylight coming from a side window, low contrast | On-camera: speaking directly to lens/mirror, mouth visible | Guys, I found my favorite drink. | New favorite 😍 |
| 2 | 3s | Close-up handheld shot, subtle autofocus adjustment | Rotates the can slowly to show the label; mouth out of frame | Off-screen | Soft, diffused daylight from the kitchen window | Off-camera V.O.: hands/product close-up, protagonist's mouth not shown, narration plays as voiceover over the action | Strawberry Bliss juice. Look at this. | Look at this ✨ |
```
