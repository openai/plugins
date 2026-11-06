# UGC ADS — 开场意图问询（指令式触发）

是否问询由本任务**首轮**字面量决定，不是每次必问。
`no-questions` → 不问，直接进 `product`。`with-questions` 或未写 → 问恰好 1 题。
问的时候：必须对 Host tools 真调用一次（Cursor `AskQuestion`、Claude `AskUserQuestion` / `ask_question`、Codex 同类）。本题只问**广告视频内容方向**。选项不固定，必须根据本轮用户输入现写。
**禁止**把 3 条方向写成 Chat 编号列表 / bullet / `Recommended:` 段落。那样写 = 本步失败。仅当 `tools/list` 里三个 host 名字都没有时才允许编号列表，并写明本宿主没有选择框。Cursor 有 `AskQuestion`，禁止走这条。

## HARD

- **首轮冻结 `IntentQuestions`**：字面量 `no-questions` → `false`；`with-questions` 或两者都未出现 → `true`。后续轮次禁止改写。
- `IntentQuestions=false`：`intent=skip`，`IntentDone=true`，同轮进 `product`。卖点分析 / 规格提问仍走。未问到的项用文末默认。
- `IntentQuestions=true`：必须实际发出 **恰好 1 题**（真调用 Host tools）。发出 ≠ 答完：Host tools 返回 / 选择框出现 **不是** `IntentDone`。`IntentDone=true` **只**在用户点选、Other、或下一条消息给出可执行内容方向之后。发出后必须停住，禁止同拍或下一 continuation 调 `parse_product_info`。
- 每题一次宿主提问：标题 = 短题名；问句 = 恰好一句；`options` = **恰好 3 条**且**第一条为推荐默认**。不要自己造第 4 个 Other；Cursor `AskQuestion` 自带 Other。无真调用、问句为空、把选项写进 Chat、或把占位句当成唯一问句 = 非法。
- `IntentQuestions=true` 时，**禁止**因「没有路由缺口 / 指令看起来够用 / 用户说直接开始」而 0 题进 `product`。
- 问句和 3 个选项必须能看出它来自**本轮用户指令**。禁止原样套下表示例，禁止抛一套无关通用问卷，禁止使用固定选项库。
- 已由文本或素材说清的事实 → 写入 Stage / 意图字段，**不要再问「确认一遍」**。本题仍要给出 3 条内容方向供选。
- 首轮带了链接 / 商品图：`IntentQuestions=true` 则先问询，入口记在内存；**禁止**先调 `parse_product_info`。`IntentDone` 后再处理商品。`false` 则同轮处理商品。

## 组题算法（仅 `IntentQuestions=true`）

1. 逐字读首轮用户消息、上传、已冻结的 `IntentQuestions`。抽出**已明确事实**与商品 / 受众 / 使用场景。
2. 先写已明确事实（提供优先于再问）。
3. **恰好 1 题：广告视频内容方向（HARD）**。综合首轮指令与已明确商品事实，组 **恰好 3 条互不重复、可执行的内容方向**。每条必须具体到「这部片子拍什么」：
   - 运镜类：写清镜头怎么动、**展现什么**（开箱哪一步 / 哪处质感 / 哪次使用动作），禁止只写 `handheld camera`。
   - 剧情类：写清**具体情节**（谁、在哪、做什么、商品如何进入），禁止只写 `short story` / `mini drama`。
   - 口播评测 / 对比 / 使用演示类：写清口播切入点、对比对象或演示动作。
   - **第一条 = 最贴本轮指令的推荐方向**。
   - 选项是一句可执行方向，长度以能看懂拍什么为准；禁止空泛 2–3 词标签。
   - 调性默认贴近 authentic handheld UGC，除非用户指令另有画风。
4. 同轮发出（HARD）——必须真调用，形状如下（选项按本轮商品现写，禁止照抄文案）：

```text
AskQuestion
title: Content direction
questions:
  - id: content_direction
    prompt: What content direction should the UGC ad take?
    options:
      - id: recommended
        label: <本轮现写方向 1>
      - id: alt_a
        label: <本轮现写方向 2>
      - id: alt_b
        label: <本轮现写方向 3>
```

   - `prompt` = **恰好一句**。禁止在 `prompt` 里列选项。
   - `options` = **恰好 3** 个。**第一条 = 推荐默认**。
   - assistant 正文不要复述这 3 条。**这一拍到此结束**：禁止再调 `parse_product_info` 或任何流水线 tool。
5. 只问这一题，然后**停住**等用户点选或 Other。用户**下一条消息**给出方向，或 Host tools 返回里已有选中的 option / Other 文本 → 收下并 `IntentDone=true`，再进 `product`。返回里没有选中项 = 未答，禁止进 `product`。
6. 问询中的上传先按 Provide 绑定，再问本题或结束。题已发出、人未答 → 不要结束问询。

选定的内容方向写入 `ExecutionGoal`（可并入 `CharacterRole` / `VisualTone` / 路径算子）。后续卖点分析、角色/场景与分镜必须遵守该方向。

**默认（`no-questions` 或未问到的项）**：可选阶段 `run`；不 Jump；`ref_video = skip`；画风 `authentic handheld UGC`。

把用户回答映射到算子：不要某产物 → Skip；我会给 → Provide；做到 X → Jump(X)。长文本内容方向 → `ExecutionGoal`。
Provide 与「不要出镜」冲突 → 以用户图为准。

## 选项示例（必须按本轮指令现写，禁止原样照抄）

例如用户要做一款气泡水 UGC，指令只给了商品图和「做一支种草视频」。下面只说明 `options[].label` 该长什么样，真正发出时仍走上面的 `AskQuestion` 形状，不要把这 3 条贴进 Chat：

- 标题：`Content direction`
- 问句：`Which content direction should this UGC ad take?`
- 选项（第一条推荐）：
  - `Handheld kitchen unboxing: she cracks the can, first sip at the counter, then holds it to the window light`
  - `Mini story: after a workout she grabs the drink from the fridge, sits on the floor, and tells a friend it actually tastes clean`
  - `Mirror selfie review: she shakes the can, takes a sip on camera, and points at the ingredient label`

选项必须随商品和本轮指令改写。换美妆 / 数码 / 食品时，开箱动作、剧情角色、口播切入点都要换成该商品自己的事实，不能每次都用这一组。
