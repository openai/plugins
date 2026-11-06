# UGC ADS — 分镜拆段组装（HARD；纯内存，不调 LLM）

script 通过后，agent 静默拆段，从本段表格行逐字组装 markdown，**直接写入内存**。不调 LLM。

## 内存写入（HARD）

| 项 | 值 |
|------|-----|
| 目标 | **`ExtractVideoContents[i-1]`**（内存变量，i = 1…N） |
| 内容 | 本段组装后的 markdown（见下方 + `storyboard-extract-format.md`） |
| 下游引用 | 首帧正文**内联**本段全文；成片按 `video-generate-prompt.md` 改写 Timeline；不要把分镜表当生成参考 |

仅当用户已确认离开 script（等待提问选继续）或 FastForward 时才进入本文件。Rollback 刚重做完 script **禁止**进入。

组装完成（i = 1…N 全部写入内存）后：`first_frame` 仍 enabled 且该段没有 **provided** 首帧（已 `invalidated` 的旧首帧不算）→ 按 `first-frame-prompt.md` 并发 ×N，然后发等待提问并停住（FastForward 除外）；否则进入成片调度。

**顺序（HARD）**：N 段（N = `SegmentCount`）**同一 turn 内**依次静默组装完成（纯内存计算）。FastForward 时完成后同轮续首帧或成片、中途不停。普通模式（含从 script 等待提问选继续）完成后进入 `first_frame` 或 `video`，在下一个**用户可见**产物处停住。

---

## 组装规则（HARD）

1. 只使用本段 `VideoSegments[i-1]` 对应镜行；**禁止**混入其它段。
2. 从分镜表 **对应行逐字提取** **9** 列；**禁止**改写 Voiceover Narration / Action / Lip Sync / On-Screen Text 事实。
3. 输出结构见 `storyboard-extract-format.md`：开头 1 句 + 逐镜 `### Shot n` + **9** bullets；**禁止** Markdown `|` 表格；**无 Character/Subject、Scene、Music/BGM**。
4. 开头句中的镜号列表 = 本段 Shot Number 升序（`{ShotList}` 写法见下）。

### `{ShotList}` 写法（用于开头句）

设本段 Shot Number 升序为 `n1, n2, …, nk`：

- **k = 1**：`{n1}`（如 `5`）
- **k = 2**：`{n1} and {n2}`（如 `5 and 6`）
- **k = 3**：`{n1}, {n2}, and {n3}`（如 `1, 2, and 3`；单段最多 3 镜，不得出现 k≥4）

开头句固定 English：`Here is the extracted information for shots {ShotList}:`

---

## 与 `storyboard-extract-format.md`

- 本文件 = **组装规则**
- `storyboard-extract-format.md` = **内存变量输出格式**（单镜 **9**-bullet 模板）
- 分段范围由静默贪心得到的 `VideoSegments[i-1]` 决定（每段 **≤15s 且 ≤3 镜**）；开头句镜号必须与该段 Shot Number **完全一致**；单段 `k` 不得大于 3
