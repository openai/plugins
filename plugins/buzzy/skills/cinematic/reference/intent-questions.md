# Cinematic — 开场意图问询（基于用户指令组题）

正式流水线前先补齐这一镜的执行信息。
**禁止**用规格提问问这些问题。每题对 Host tools 真调用一次（Cursor `AskQuestion`、Claude `AskUserQuestion` / `ask_question`、Codex 同类）。问句写在提问 tool 的 `prompt`，不要写进 Chat 编号列表。

下表是**题型灵感**，不是每次必问的固定问卷。先读用户指令，再组题。

## HARD

- 用户给出指令后，**默认只问 2 题**，问完就 `IntentDone=true`。禁止为凑问卷问第 3、第 4 题。仅当用户把关键事实说糊、两题仍不够拍板时，才加第 3 题。
- 每题一次宿主提问：标题 = 从 brief 压的短名；问句 = **一句**点名本条 brief 的问句；`options` = **恰好 3 条**（第一条 = 推荐默认）。不要自己造第 4 个 Other；Cursor `AskQuestion` 自带 Other。
- **禁止**把 3 条方向写成 Chat 编号列表 / bullet / `Recommended:` 段落。那样写 = 本步失败。仅当 `tools/list` 里三个 host 名字都没有时才允许编号列表，并写明本宿主没有选择框。Cursor 有 `AskQuestion`，禁止走这条。
- **禁止**把题型表示例问句原文贴出去。问句里必须出现用户 brief 的词，让人听得出你读过这条指令。
- **禁止**因「没有路由缺口 / 指令看起来够用 / 用户首轮说直接开始」而 0 题进 `settings`。
- 已由文本或素材说清的事实 → 写入 Stage / 意图字段，**不要再问「确认一遍」**。**禁止**把画幅 / 时长 / 模型做成 2 题之一。
- 仅当 `IntentAskedCount ≥ 2` 后，用户说开始 / 默认 / 跳过剩余 → 剩余用默认，立刻进 `settings`（普通模式）或按 Jump 处理。
- 首轮带了成片词 / 参考图 / 参考视频：先问询，入口记在内存。`IntentDone` 后再处理 `settings`。
- **禁止**在开场问画幅 / 分辨率 / 时长——那三项目只走规格提问。
- 问询中上传的图 / 视频：按 `slot-adaptation.md` 绑成参考，不要当成成片词。
- 开场问询那一拍**禁止**同拍 `create_project` 或任何 Buzzy MCP tool。

## 组题算法

1. 逐字读首轮用户消息、上传、已写明的镜头设定。抽出**已明确事实**与**仍模糊的执行目标**。
2. 先写已明确事实（提供优先于再问）。
3. 再挖 **恰好 2** 道最有信息量的题。优先：这一镜要落到哪一种情绪/类型 → 前 2 秒用哪种钩子抓住眼睛。平台适配（TikTok / YouTube / Reels / 宽银幕）只在 brief 已点名平台、或两题仍缺执行缺口时才问。
4. 指令**简短** → 2 题都围着这条 brief 的镜头核，不要改问生产路径。
5. 指令**已经较具体** → 2 题做专业深挖（钩子、灯光情绪、运镜），不要再问规格。
6. 每题同轮发出（HARD）——必须真调用，形状如下（选项按当前 brief 现写，禁止照抄文案）：

```text
AskQuestion
title: {short name from this brief}
questions:
  - id: intent_{n}
    prompt: {one question that names words from this brief}
    options:
      - id: recommended
        label: {option 1, recommended default}
      - id: alt_a
        label: {option 2}
      - id: alt_b
        label: {option 3}
```

   - `prompt` = **恰好一句**。禁止在 `prompt` 里列选项。
   - `options` = **恰好 3** 个。**第一条 = 推荐默认**。短标签，1–6 词，按当前指令改写。
   - assistant 正文不要复述这 3 条。停住等用户点选或 Other。
7. 每轮只问一题。一条消息答了多题 → 全收。
8. 问询中的上传先按 `slot-adaptation.md` 绑参考，再问下一题或结束。

**默认（未问到或用户跳过的项）**：其它可选阶段 `run`；不 Jump；不预设必须有参考图。
未问到 ≠ 已 skip。

## 题型示例（必须按当前指令改写，禁止原文照贴）

| 何时优先 | 标题 | prompt 怎么问 | options 怎么改 |
|----------|------|----------------|------------------|
| 指令短 / 情绪不清 | brief 短名 | 用 brief 里的场景词问「这一镜要落到哪一种情绪」 | 恰好 3 个贴着这条 brief 的短标签（如 weary noir / golden awe / intimate farewell） |
| 钩子未定 | brief 短名 | 问前 2 秒怎么抓住眼睛，不要问「Which hook technique?」原文 | black-to-burst / eye-open / reverse-macro 等按 brief 改，只给 3 个 |
| 运镜未定 | brief 短名 | 问镜头怎么走 | slow dolly-in / locked-off / handheld 等，只给 3 个 |
| 指令已有方向 | brief 短名 | 围着已有方向补一个执行缺口 | 按语义给恰好 3 个选项 |

把回答映射到算子：不要某产物 → Skip；我会给 → Provide；做到 X → Jump；长文本 → `SceneGoal` / `MoodGenre` / `HookPlan` / `CameraPlan`。
