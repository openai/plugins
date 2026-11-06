# TVC ADS — 分镜表格式与对话卡片（HARD）

模板产出字段 `content` = **Markdown GFM 管道表**；`name` = `Storyboard Table`。
有参考 / 无参考是**两套列**，以模板实际表头为准，禁止改写成 UGC 9 列。
本文件做**返回校验** + **对话卡片转写**。校验不拼进模板输入。

对话渲染（HARD）：**不要**把 `|` 管道表贴进对话。窄聊天栏会把多列表折成极高行。同一 continuation 必须按下方「对话分镜卡片」从每一表行转写卡片，然后发 Host tools Continue/Revise。禁止 code fence。

---

## 两套表头（顺序 HARD）

### A. 有参考 — `tvc_ads_storyboard_with_ref`（10 列）

| # | 表头 |
|---|------|
| 1 | Shot No. |
| 2 | Time Interval |
| 3 | Duration |
| 4 | Framing |
| 5 | Camera Movement |
| 6 | Visual Content |
| 7 | Scene |
| 8 | Lighting & Color Tone |
| 9 | Dialogue |
| 10 | Sound Design |

```markdown
| Shot No. | Time Interval | Duration | Framing | Camera Movement | Visual Content | Scene | Lighting & Color Tone | Dialogue | Sound Design |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

### B. 无参考 — `tvc_ads_storyboard_no_ref`（14 列）

| # | 表头 |
|---|------|
| 1 | Shot |
| 2 | Start |
| 3 | End |
| 4 | Duration |
| 5 | Visual Description |
| 6 | Narrative |
| 7 | Shot Size |
| 8 | Camera Angle |
| 9 | Camera Movement |
| 10 | Focal Length / DOF |
| 11 | Lighting |
| 12 | Background Music |
| 13 | Voice / SFX |
| 14 | Keyframe |

```markdown
| Shot | Start | End | Duration | Visual Description | Narrative | Shot Size | Camera Angle | Camera Movement | Focal Length / DOF | Lighting | Background Music | Voice / SFX | Keyframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

**必须**先输出表头行，再输出 `| --- | … |` 分隔行（段数 = 列数），再输出数据行。缺分隔行 / 列数对不上当前模式 → 非法，同 key 重试。
表头与单元格正文固定 English。单元格内禁止未转义的 `|`。
禁止竖排列名、禁止把卡片写法写进 `content`、禁止改成 UGC 9 列。

若模板实际返回的表头与上表个别用词不一致：校验以**返回表头**为准（仍必须是 GFM + 分隔行）；对话卡片的 bullet **标签必须用返回表头原文**，不要强行改成上表用词。

---

## 对话分镜卡片（HARD — 只约束 Chat，不改 `content`）

`content` 仍是管道表（plan / 成片只认这张表）。Chat 只给人看，必须转成卡片。
引导句：`Here is the storyboard table:`（重做则 `Here is the updated storyboard table:`）。
按镜号升序，每镜一块；镜与镜之间 **仅 1 个空行**。Shot / Duration 进标题，其余列各一条 bullet，**标签必须是表头原文**。禁止改写 Dialogue / Voice / SFX / Visual 事实。

**HARD — 卡片 ≠ 成片**：下面「禁止合并多镜进一块」**只约束 Chat 展示**。`plan` / `opening_visual` / `video` 必须把相邻短镜合并成段（见 `plan-and-opening.md` §Shot ≠ Segment）。禁止因为「对话里有 8 张 2s 卡片」就发 8 次 `generate_image` / `generate_video`。

### A. 有参考卡片

```markdown
### Shot {Shot No.} · {Duration}
- **Time Interval:** {Time Interval}
- **Framing:** {Framing}
- **Camera Movement:** {Camera Movement}
- **Visual Content:** {Visual Content}
- **Scene:** {Scene}
- **Lighting & Color Tone:** {Lighting & Color Tone}
- **Dialogue:** {Dialogue}
- **Sound Design:** {Sound Design}
```

### B. 无参考卡片

```markdown
### Shot {Shot} · {Duration}
- **Start:** {Start}
- **End:** {End}
- **Visual Description:** {Visual Description}
- **Narrative:** {Narrative}
- **Shot Size:** {Shot Size}
- **Camera Angle:** {Camera Angle}
- **Camera Movement:** {Camera Movement}
- **Focal Length / DOF:** {Focal Length / DOF}
- **Lighting:** {Lighting}
- **Background Music:** {Background Music}
- **Voice / SFX:** {Voice / SFX}
- **Keyframe:** {Keyframe}
```

**禁止（对话）**：

- 把 `|` 管道表、表头或 `| --- |` 贴进 Chat
- code fence
- 增删卡片字段、改标签措辞、合并多镜进一块（仅 Chat；plan / 成片必须合并短镜）
- 把有参考表改写成无参考列，或反过来
- 写回 UGC 的 `Lip Sync` / `On-Screen Text` / `Character/Subject` 等列

---

## 声音（从分镜写入内存）

script 首次生成后，从 Dialogue / Voice / SFX / Sound Design 整理一份全片统一 `VoiceProfile` 写入内存。不要把 `VoiceProfile` 加成新列或另贴一段 Chat。细则见 `storyboard-prompts.md`。
