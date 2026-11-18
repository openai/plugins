# UGC ADS — 下游输入适配（通用）

后一阶段需要前序产物时，对**每一个输入槽**按这次序取值。不要为某个举例写死「必须三槽」。

```text
provided  →  generated(done)  →  skip 则省略该槽  →  回退到次近同类素材  →  仍没有则 (none) / 不问该槽
```

- **禁止**把同一条素材挂两次来凑长度。
- **禁止**空 `<<<image_n>>>` / 空参考列表。
- 生成参考只含真实媒体，数量 = 主句里实际出现的占位符个数。
- **一律走 URL**：`generate_image` / `generate_video` / run_prompt / `merge_videos` 只传声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`，**禁止传 `nodeIds`**。URL 来自确认消息 / `display_product_info` 图地址、用户 Provide、或 `get_task` 成功后的素材 URL。禁止编造 HTTPS。`display_product_info.images` 用确认消息里的 URL。
- 占位符只用 `<<<image_n>>>` / `<<<video_n>>>`（小写、从 1），与 URL 列表一一对应。历史里若是 `<<>>`，按当前绑定重写后再调用。
- 缺可选前序 **不得**阻塞后序。缺硬底线（商品身份、script、成片用的至少一块视觉）→ 问用户，不要空转。

## 文本槽

分镜 / 角色 / 场景模板输入：有 Prompt 正文或用户意图字段就写入；Skip 且无正文 → `(none)`。`SellingPoint` = 卖点分析经对话确认后的全文（用户改了文案则以用户稿为准）；未确认不得用规格提问旧字段凑。有 `CharacterRole` / `VisualTone` / `ExecutionGoal` / 其它问询结论 → 原样追加，供模型遵守。角色 / 场景 Prompt 由 agent 直接写，禁止 `ugc_ads_character_prompt` / `ugc_ads_scene_prompt`。

run_prompt 只挂商品图 URL（有才加；确认消息 / `display_product_info` 图地址）。分镜必含商品图 URL；角色图 / 场景图 / 参考视频 URL **有才加**。缺 Character/Scene Prompt 不阻塞。卖点正文 / brief / Prompt 文本**不是**生成参考。
所有生成 / 合成的参考都用确认消息、Provide、或 `get_task` 成功后的素材 URL。`merge_videos` 挂各段成片 URL。

## 视觉槽

组列表时从左到右、有才加入：

1. 本阶段专用图（该段首帧、用户指定的开场图……）
2. 角色参考（上传或成图）
3. 产品主图
4. 场景参考（上传或成图）

首帧（阶段未 skip 时）按「角色 → 产品 → 场景」组 1–3 个槽，agent 按 `first-frame-prompt.md` 直接写 Prompt。角色图 / 场景图 / 首帧 `model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文。
成片挂载：该段首帧（有则挂，正文不要写 first frame）→ 产品主图 → 角色图（有才加）→ 场景图（有才加）。Video i≥2 另挂 Video 1 成片为 `<<<video_1>>>`。`generate_video.model` = Video 表 **Seedance 2.0 Fast** 行的 `model` 列原文；画幅 / 分辨率按 SKILL §运行时填参收敛。模板见 `video-generate-prompt.md`。

连产品图都没有 → 不要硬生成首帧 / 成片；请用户补商品图或任意可用参考。

## 回退作废（通用）

Rollback(S) 或 Reroute 使旧产物失效时：S 以及阶段图上 **S 之后**的阶段全部 `invalidated`。不要只作废举例里的列表；新加的阶段同样跟在目标后面就要作废。

重做 S 时带上用户这条建议。下游阶段的 skip / run / provided **沿用回退前的计划**（不要把 `first_frame` 改成 skip）。重做完有用户可见产物 → 发等待提问并停住，**禁止**自动顺跑到成片。

## Jump 越过时怎么适配（实例，非封闭）

Jump(T) 先按 SKILL 把路上「可选可见」标 skip，再按本节取槽。不要为某一对 (起点, T) 另写例外。

| 用户说法 | 算子（由通用规则推出） | 下游怎么适配 |
|----------|------------------------|----------------|
| 不要场景 | Skip(`scene`) | 分镜不写身份/环境列；首帧 / 成片不挂场景槽 |
| 不要首帧 | Skip(`first_frame`) | 成片不挂首帧；opening look 回退到角色图，否则产品图 |
| 自带角色图 | Provide(`character`) | 不生成角色图；下游当角色参考 |
| 自带参考视频 | Provide(`ref_video`) | 分镜走 with-ref |
| 不要参考视频 | Skip(`ref_video`) | 清参考绑定；分镜走 no-ref |
| 角色图后直接出视频 | Jump(`video`) | 首帧是路上可选可见 → skip；只跑 extract 再成片；成片不挂首帧，opening look 用角色图，否则产品图 |
| 不生成角色，直接出首帧 | Jump(`first_frame`) | 角色 / 场景是路上可选可见 → skip；script / extract 是硬前置或内部 → 跑；首帧槽回退到产品图 |
| 只要分镜、先不拍 | Jump(`script`) | 做到 script 停；其后可选阶段不跑 |
| 成片后说分镜不对 | Rollback(`script`) | 作废 extract 及之后；重做分镜后停住等确认 |
| 中途又传了场景图 | Provide(`scene`) | 即使曾 Skip，改为 provided，后续槽用这张图 |
