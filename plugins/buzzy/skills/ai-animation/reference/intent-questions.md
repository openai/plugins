# AI Animation — 开场意图问询（基于用户指令组题）

正式流水线前先补齐叙事执行所需信息。
**禁止**用规格提问问这些问题。每题对 Host tools 真调用一次（Cursor `AskQuestion`、Claude `AskUserQuestion` / `ask_question`、Codex 同类）。问句写在提问 tool 的 `prompt`，不要写进 Chat 编号列表。

下表是**题型灵感**，不是每次必问的固定问卷。先读用户指令，再组题。

## HARD

- 用户给出指令后，**默认只问 2 题**，问完就 `IntentDone=true`。禁止为凑问卷问第 3、第 4 题。仅当用户把关键事实说糊、两题仍不够拍板时，才加第 3 题。
- 每题一次宿主提问：标题 = 从 brief 压的短名；问句 = **一句**点名本条 brief 的问句；`options` = **恰好 3 条**（第一条 = 推荐默认）。不要自己造第 4 个 Other；Cursor `AskQuestion` 自带 Other。
- **禁止**把 3 条方向写成 Chat 编号列表 / bullet / `Recommended:` 段落。那样写 = 本步失败。仅当 `tools/list` 里三个 host 名字都没有时才允许编号列表，并写明本宿主没有选择框。Cursor 有 `AskQuestion`，禁止走这条。
- **禁止**把题型表示例问句原文贴出去。问句里必须出现用户 brief 的词，让人听得出你读过这条指令。
- **禁止**因「没有路由缺口 / 指令看起来够用 / 用户首轮说直接开始」而 0 题进 `style` / `settings`。
- 已由文本或素材说清的事实 → 写入 Stage / 意图字段，**不要再问「确认一遍」**。风格卡即将收库图时，**不要**再问视听风格。**禁止**把「电影 vs 动漫 / 选哪套风格库」做成 2 题之一。禁止把 `ai_film` / `animation` / `StyleTemplate` 写进问句或选项。本链风格库已冻结为 animation，入口标记不进 `user_requirements`。
- 仅当 `IntentAskedCount ≥ 2` 后，用户说开始 / 默认 / 跳过剩余 → 剩余用默认，立刻进 `style`（普通模式）或按 Jump 处理。
- 首轮带了剧本 / 角色图 / 场景图 / 风格图：先问询，入口记在内存；明确风格图只绑 `style = provided`。`IntentDone` 后再处理 `style` / `settings`。
- **禁止**在开场问画幅 / 分辨率 / 时长——那三项目只走规格提问。
- 问询中上传的图（任意张）：按 `assets-prompt.md` **每一张先看再分槽**，不要一律当风格，不要只绑第一张。
- 开场问询那一拍**禁止**同拍 `create_project` 或任何 Buzzy MCP tool。

## 组题算法

1. 逐字读首轮用户消息、上传、已写明的故事设定。抽出**已明确事实**与**仍模糊的执行目标**。
2. 先写已明确事实（提供优先于再问）。
3. 再挖 **恰好 2** 道最有信息量的题。优先：这条故事要怎么好笑/怎么走 → 谁领这场戏。视听风格留给 `style` 卡。
4. 指令**简短** → 2 题都围着这条 brief 的故事核，不要改问生产路径。
5. 指令**已经较具体** → 2 题做专业深挖（人物、节拍），不要改问无关路线，也不要再问风格卡即将收集的视听题。
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
8. 问询中的上传先按 `assets-prompt.md` 把每一张识图分槽，再问下一题或结束。用户点名当风格用的图只绑 `style`，不要拷进角色 / 场景 / 故事参考。

**默认（未问到或用户跳过的项）**：`style = pending`（问询结束后必须出 `choose_skill_asset`；未问到 ≠ 已 skip）；`assets = run`（剧本后先出提问，选继续才成图）；其它可选阶段 `run`；不 Jump；`StyleTemplate=animation`；不预设「无角色」。
开场问询不代替剧本后提问。未问到 ≠ 已 skip。
开场若已明确交风格图 → `style = provided`，问询结束后不要再发卡。

## 题型示例（必须按当前指令改写，禁止原文照贴）

| 何时优先 | 标题 | prompt 怎么问 | options 怎么改 |
|----------|------|----------------|------------------|
| 指令短 / 目标不清 | brief 短名 | 用 brief 里的类型词问「这场戏要落到哪一种」 | 恰好 3 个贴着这条 brief 的短标签 |
| 类型语气未定 | brief 短名 | 问这条故事的语气，不要问「What genre and tone should the film hold?」原文 | Intimate / chaotic / warm 等按 brief 改，只给 3 个 |
| 人物未定 | brief 短名 | 问谁领这场戏 | 一人 / 搭档 / 小队（只给 3 个；自填留给 Other） |
| 指令已有方向 | brief 短名 | 围着已有方向补一个执行缺口 | 按语义给恰好 3 个选项 |

把回答映射到算子：不要某产物 → Skip；我会给 → Provide；做到 X → Jump；长文本 → `StoryGoal` / `GenreTone` / `CharacterPlan` / `VisualLanguage`。
Provide 与「不要角色图」冲突 → 以用户图为准。风格图与角色 / 场景图冲突 → 风格图只进 `style`。
