# TVC ADS — 下游输入适配（通用）

后一阶段需要前序产物时，对**每一个输入槽**按这次序取值。不要为某个举例写死「必须三槽」。

```text
provided  →  generated(done)  →  skip 则省略该槽  →  回退到次近同类素材  →  仍没有则 (none) / 不问该槽
```

- **禁止**把同一条素材挂两次来凑长度。
- **禁止**空 `<<<image_n>>>` / 空参考列表。
- 生成参考只含真实媒体，数量 = 主句里实际出现的占位符个数。
- **一律走 URL**：`generate_image` / `generate_video` / run_prompt / `merge_videos` 只传声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`，**禁止传 `nodeIds`**。URL 来自确认消息 / `display_product_info` 图地址、用户 Provide、或 `get_task` 成功后的素材 URL。禁止编造 HTTPS。`display_product_info.images` 用确认消息里的 URL。
- 占位符只用 `<<<image_n>>>` / `<<<video_n>>>`（小写、从 1），与 URL 列表一一对应。冻结模板 Prompt 若没有占位，调用前按当前绑定追加 Reference assets。历史里若是 `<<>>`，按当前绑定重写后再调用。
- 缺可选前序 **不得**阻塞后序。缺硬底线（商品身份、script、成片用的至少一块视觉）→ 问用户，不要空转。

## 文本槽

分镜 / 计划 / 开场视觉模板输入：有卖点正文或用户意图字段就写入；Skip 且无正文 → `(none)`。
`VoiceProfile` = script 阶段确定的全片统一声音身份描述；有则原样写入 plan 和每个视频片段，不按段重写。
`SellingPoint` = 卖点分析经对话确认后的全文（用户改了文案则以用户稿为准）；未确认不得用规格提问旧字段凑。
有 `CharacterRole` / `VisualTone` / `ExecutionGoal` → 原样追加，供模型遵守。

run_prompt 只挂商品图 URL（有才加；确认消息 / `display_product_info` 图地址）。有参考时分镜另挂参考视频 URL；无参考时不要挂虚构参考。其它素材 URL **有才加**。卖点正文 / Prompt 文本**不是**生成参考。
所有生成 / 合成的参考都用确认消息、Provide、或 `get_task` 成功后的素材 URL。`merge_videos` 挂各段成片 URL。

## 视觉槽

组列表时从左到右、有才加入：

1. 本阶段专用图（该段预览 / 首帧、用户指定的开场图……）
2. 角色参考（上传或成图）
3. 产品主图

`opening_visual` 未 skip 时：有参考 → 按 agent 写的 `PreviewPrompts[]` 成预览图（商品图 + 角色图，不挂分镜表）；无参考 → 按 `tvc_ads_first_frame_prompt` 返回的 `FirstFramePrompts[]` 成首帧（产品主图；分镜事实已在 Prompt 正文里）。条数 / 张数 = 合并后的 `SegmentCount`，禁止按 shot 行数出图。角色图 / Preview / 首帧 `model` = `<available_models>` Image 表 **gpt image2** 行的 `model` 列原文。
成片 opening：该段开场视觉 → 否则角色图 → 否则产品图。opening 已是产品图则不要再写第二个产品槽。
成片**禁止**挂用户参考视频。

连产品图都没有 → 不要硬生成开场视觉 / 成片；请用户补商品图或任意可用参考。

## 模式怎么跟 `ref_video` 走

| `ref_video` | script | plan | opening_visual |
|-------------|--------|------|----------------|
| provided | `tvc_ads_storyboard_with_ref`（角色 Prompt 用返回的 `character_prompts`） | `tvc_ads_script_plan`（只要分段）+ agent 写 Preview Prompt | 分段预览图 |
| skip（默认） | `tvc_ads_storyboard_no_ref` | Master 视频提示词 + `tvc_ads_first_frame_prompt` 生成首帧 Prompt | 分段首帧 |

Skip 角色 / `CharacterVisualPlan=skip`：即使 with-ref 返回了 `character_prompts`，也不生成角色图；计划里 Existing Character Prompts 写 `(none)`。Jump 越过 script 且未点名保留角色图时同样 `skip`。
禁止搜片，禁止 `tvc_ads_search_keywords`。无参考模式的首帧 Prompt 必须调用 `tvc_ads_first_frame_prompt`，禁止 agent 直接改写；禁止调用 `tvc_ads_master_first_frame_prompt`。

## 回退作废（通用）

Rollback(S) 或 Reroute 使旧产物失效时：S 以及阶段图上 **S 之后**的阶段全部 `invalidated`。不要只作废举例里的列表；新加的阶段同样跟在目标后面就要作废。

重做 S 时带上用户这条建议。下游阶段的 skip / run / provided **沿用回退前的计划**（不要把 `opening_visual` 改成 skip）。重做完有用户可见产物 → 发等待提问并停住，**禁止**自动顺跑到成片。

## Jump 越过时怎么适配（实例，非封闭）

Jump(T) 先按 SKILL 把路上「可选可见」标 skip，再按本节取槽。不要为某一对 (起点, T) 另写例外。

| 用户说法 | 算子（由通用规则推出） | 下游怎么适配 |
|----------|--------------------|----------------|
| 不要参考视频 | Skip(`ref_video`) | 分镜走 no-ref；计划走 Master 视频提示词 + `tvc_ads_first_frame_prompt` 生成首帧 Prompt；开场视觉走首帧 |
| 不要预览 / 不要首帧 | Skip(`opening_visual`) | 成片 opening 用角色图，否则产品图 |
| 自带角色图 | Provide 到 script 的角色锚点 | 不生成角色图；下游当角色参考 |
| 自带参考视频 | Provide(`ref_video`) | 不搜索；分镜走 with-ref |
| 分镜后直接出视频 / `directly generate the videos` / 跳过首帧出片 | Jump(`video`) | 开场视觉未点名 → skip；plan 静默只分段（不写 Preview、不调 `tvc_ads_first_frame_prompt`、不成首帧）；成片 opening 用角色图（若已有），否则产品图 |
| 角色图后直接出视频 | Jump(`video`) | 开场视觉是路上可选可见 → skip；角色图子产物未点名 → `CharacterVisualPlan=skip`；只跑 plan 再成片；opening 用角色图（若已 provided），否则产品图 |
| 不生成角色，直接出首帧 | Jump(`opening_visual`) | 角色是路上可选可见 → `CharacterVisualPlan=skip`；script / plan 是硬前置或内部 → 跑；首帧槽回退到产品图 |
| 只要分镜、先不拍 | Jump(`script`) | 做到 script 停；其后可选阶段不跑 |
| 成片后说分镜不对 | Rollback(`script`) | 作废 plan 及之后；重做分镜后停住等确认 |
| 中途又传了预览图 | Provide(`opening_visual`) | 即使曾 Skip，改为 provided，后续槽用这些图 |
