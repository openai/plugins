# Cinematic — 下游输入适配（通用）

后一阶段需要前序产物时，对**每一个输入槽**按这次序取值。不要为某个举例写死「必须三槽」。

```text
provided  →  generated(done)  →  skip 则省略该槽  →  回退到次近同类素材  →  仍没有则 (none) / 不问该槽
```

- **禁止**把同一条素材挂两次来凑长度。
- **禁止**空 `<<<image_n>>>` / 空参考列表。
- 生成参考只含真实媒体，数量 = 主句里实际出现的占位符个数。
- **一律走 URL**：`generate_video` / `merge_videos` 只传声明里的 `image_url` / `image_urls` / `video_url` / `video_urls`，**禁止传 `nodeIds`**。URL 来自用户 Provide，或 `get_task` 成功后的素材 URL。禁止编造 HTTPS。
- 占位符只用 `<<<image_n>>>` / `<<<video_n>>>`（小写、从 1），与 URL 列表一一对应。历史里若是 `<<>>` 或 `@material[name]`，按当前绑定重写后再调用。
- 缺可选前序 **不得**阻塞后序。缺硬底线（镜头身份、已打印 `prompt`）→ 问用户，不要空转。参考图不是硬底线。

## 文本槽

| 下游 | 优先取值 |
|------|----------|
| `prompt` 正文 | 用户 Provide 的成片词原文；否则 agent 按 `prompt-write.md` 现写。写入问询字段（`SceneGoal` / `MoodGenre` / `HookPlan` / `CameraPlan`）+ 规格（`VIDEO_DURATION` / `VIDEO_RATIO` / `VIDEO_MODEL`）。用户参考图 / 视频走 URL 字段，不把词正文当 URL |
| 成片正文 | `generate_video.prompt` = 已打印的 `Cinematic Prompt`（按 SKILL §占位符补 `<<<image_n>>>` / `<<<video_n>>>`）+ 末尾 `no background music`。禁止空 prompt |
| 合成 | 先停 BGM 闸门。选定后一次 `merge_videos(video_infos=Cinematic Clip, is_generate_bgm)`，挂成片 URL。with→`true` / without 或 FastForward 未点名→`false`。禁止对单段配乐。**禁止传 `nodeIds`** |

Skip 且无正文 → 该描述槽写 `(none)`。Provide 的成片词原样绑定，不要再生成一份覆盖它。

成片词文本**不是**生成参考，不要把它的正文当 URL。

## 视觉槽

组列表时从左到右、有才加入：

1. 用户点名的风格 / mood-board 参考图
2. 用户点名的角色 / 主体参考图
3. 用户点名的场景 / 地点参考图
4. 用户 Provide 的运动 / 转场参考视频

没有参考 → 不传 `image_urls` / `video_urls`，纯文生视频。禁止为凑槽复制同一 URL。

## 音频

本链**没有**独立音频 URL 槽（除非当前 `generate_video` 声明里明确有 `audio_url` / `audio_urls` —— 有才传，没有就不要发明）。
对白 / Foley / 环境音写进成片词。**禁止**在成片词里写 BGM / background music / scored music。配乐只走 `merge` 闸门。
