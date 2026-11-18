# TVC ADS — 卖点分析（商品确认后）

产品信息被用户确认后、规格提问之前。三条入口都要跑。
用已注册模板 `tvc_ads_selling_analysis`。
**必须**把分析正文作为 markdown 贴进 Chat，且前后加上固定引导 / 确认句（见下方等待确认）。
**禁止**去调 UGC 的 brief / selling key。

---

## 生成（HARD — 只调一次 run_prompt）

1. `run_prompt(prompt_key="tvc_ads_selling_analysis", projectId=项目 id, instruction=下方输入)` **恰好 1 次**。还没有 `projectId` 就先 `create_project`。
2. 商品图 URL 有才加（确认消息 `Main Image:` / `Images:`，或 `display_product_info` 返回的图地址；主图第一位；否则用已记下的商品图 URL）。走 `image_url(s)`。**禁止传 `nodeIds`**。不要挂商品信息组当生成参考。
3. 成功：读 `items[].content` → `SellingPointDraft`。`name` 必须是 `Selling Point Analysis`。
4. 禁止因为「没有 `product_brief`」再调一次 run_prompt。
5. 返回空 / 缺 `content` → 同 key 重试 1 次；再失败用 Title+Description 原文作为 `content` 语义写入内存并说明，禁止空转。兜底也必须按下方等待确认贴出三段。
6. **「恰好 1 次」只约束 run_prompt**。run_prompt 已返回 **不等于** 用户已确认。同一 continuation **必须**按下方等待确认贴出三段正文；只写一句 status、只贴 `content` 不说明这是卖点、或调 Host tools Continue/Revise = 本步失败。

输入：

```text
Product Name: {ConfirmedProductTitle}

Product Description:
{ConfirmedProductDescription}

User instruction (relevant excerpts only):
{UserInstructionRelevant}

Intent notes:
{ExecutionGoal / 内容方向 / CharacterRole / VisualTone 中已有的项；无则 (none)}
```

`UserInstructionRelevant` = 与商品、品牌、受众、说服角度、使用场景有关的句子。
模板自己整理：1–2 句对象与情境 + 3–5 条具体卖点 + 1 句看完后行动；English；禁止编造认证 / 功效；禁止写成剧本。

---

## 等待确认（HARD — run_prompt 返回后的同一 continuation 必做）

普通模式（含 Rollback 重做）在 run_prompt **已经返回** 的那一次 continuation：

1. assistant 正文必须是下面三段（缺任一段 = 本步失败；用户可见 English，禁止改写成中文或其它措辞）：
   - 固定引导句：`Here are the product selling points:`
   - 空一行后：`items[].content` **原文 markdown**（禁止只写 `Your selling point analysis is ready.`；禁止 code fence；禁止改写成摘要）
   - 空一行后：固定确认句：`Confirm to continue, or tell me what you'd like to change.`
2. **不要**调 Host tools Continue/Revise。然后**停住**，等用户下一条自由回复。不要同 continuation 出规格提问 / 搜片提问 / script。

只贴 `content`、不写引导句 / 确认句 = 用户不知道这是卖点、也不知道可以确认或修改 = 本步失败。
贴过这三段 ≠ 用户已确认。只有用户在对话里确认 / 说继续 / 接受本稿，才算「卖点等待已完成」。
`不要叠新调用` 只适用于 run_prompt **尚未返回**；返回后贴这三段并停住是 mandatory continuation，不是叠生成。

用户回复 `ok` / `continue` / `looks good` / `confirm` / 确认 / 继续，或改了文案后接受 → `SellingPoint` = 本步 `content` 全文（不含引导句 / 确认句；若用户改了文案则以用户稿为准）→ 进 `info_card`。
不满意 / 要改 → 按用户意见重跑模板，再贴新的三段并再停住。

FastForward：仍跑这一次 run_prompt，把引导句 + `content` 贴进对话（可不写确认句），写入 `SellingPoint`，不停、不等人，继续。
Skip：不调模板；用 Title+Description 原文写入 `SellingPoint`。
Provide：用户自带卖点文原样写入 `SellingPoint`（自供，不调模板）。
Rollback(卖点)：作废后按当前产品信息重跑模板，**同一 continuation** 再贴三段并停住，不要顺跑规格 / 成片。
