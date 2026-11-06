# UGC ADS — 分镜拆段格式（HARD）

内存变量 **`ExtractVideoContents[i-1]`** = **Markdown 逐镜提取**（小标题 + bullet 列表）；**纯内存，不调 LLM**。
agent 从分镜表**逐字组装**后写入内存。组装说明见 `storyboard-extract-prompt.md`。

**禁止** Markdown **表格**（`| col |`）；**禁止** JSON；**禁止**在 bullet 之间插入空行。

## 整体结构

1. **开头 1 句**（固定 English）
2. 按镜号顺序，每镜一节：**`### Shot {n}`**（固定 English）+ **9 条 bullet**
3. 镜与镜之间：**仅 1 个空行**

## 开头句（固定 English）

`Here is the extracted information for shots 1, 2, and 3:`

## 单镜模板（HARD — bullet 字段名固定 English）

每镜 **固定 9 条** `- **字段名:** 值` bullet，**顺序与分镜表列一致**（列位置 1…9）：

```markdown
### Shot {n}
- **Shot Number:** {n}
- **Duration:** {duration}
- **Shooting Style:** {shooting style}
- **Action:** {action}
- **Expression:** {expression}
- **Lighting:** {lighting}
- **Lip Sync (On-Camera Speaking):** {lip sync status}
- **Voiceover Narration:** {voiceover}
- **On-Screen Text:** {on-screen text}
```

## 字段来源

从分镜表 **对应行逐字提取**（按列序 1…9，表头固定 English）；口播 / 动作 / 口型同步 / 花字 **禁止**改写事实。**无 Character/Subject、Scene、Music/BGM 字段。**

## 分段（N 段）

- **`VideoSegments[0]` … `VideoSegments[N-1]`**：镜号升序 + **时长 / 镜数贪心**——每段 Duration **≤15s** 且 Shot 数 **≤3**（详见 `script-table-format.md`）
- 第 **i** 段 → 纯内存组装，写入 **`ExtractVideoContents[i-1]`**
- 下游：首帧正文内联本段 extract 全文；成片按 `video-generate-prompt.md` **改写 Timeline**，不要整段粘 extract；不要把分镜表当生成参考

## 完整示例（节选 2 镜 — English）

```markdown
Here is the extracted information for shots 1 and 2:

### Shot 1
- **Shot Number:** 1
- **Duration:** 3s
- **Shooting Style:** Handheld phone selfie, slight natural jitter
- **Action:** Holds the can close to the face and points at the label while speaking
- **Expression:** Starts attentive, livens mid-line, eases on the last word
- **Lighting:** Natural daylight from a side window
- **Lip Sync (On-Camera Speaking):** On-camera: speaking directly to lens/mirror, mouth visible
- **Voiceover Narration:** Okay, it is way too hot today…
- **On-Screen Text:** New favorite 😍

### Shot 2
- **Shot Number:** 2
- **Duration:** 3s
- **Shooting Style:** Close-up handheld shot
- **Action:** Rotates the can slowly to show the label; mouth out of frame
- **Expression:** Off-screen
- **Lighting:** Soft, diffused daylight
- **Lip Sync (On-Camera Speaking):** Off-camera V.O.: hands/product close-up, protagonist's mouth not shown, narration plays as voiceover over the action
- **Voiceover Narration:** Enter my new obsession…
- **On-Screen Text:** Look at this ✨
```
