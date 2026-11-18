# UGC ADS — 产品 Brief（无链接、有商品图）

适用：无产品页链接、但有商品主图。解析 / 无链接无图路径的卖点分析见 `selling-analysis-prompt.md`，不要在本文件再写一份 brief。

模板 key：`ugc_ads_product_brief`。调用时必传 `projectId`；还没有 id 就先 `create_project`。

- `UserProductInfo` 无/过少 → 跑模板；有实质用户文 → 跳过模板，整理后写入 `ProductBrief`
- 参考：产品主图 URL（有才加；走 `image_url(s)`，禁止传 `nodeIds`）
- 输入：
```text
user_product_info:{UserProductInfoOrNone}
```
- 成功：读 `product_brief`（模板不要带 `content`，以免多落一份 brief）→ 写入 `ProductBrief`，`title=[Product] Brief` → 状态句 → 立刻进入卖点分析（必须按 `selling-analysis-prompt.md` 贴三段）。禁止本步出规格提问。
