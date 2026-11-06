# UGC ADS — 分镜脚本

| 分支 | 工具 |
|------|----------|
| 有参考视频 | `ugc_ads_storyboard_with_ref` |
| 无参考视频 | `ugc_ads_storyboard_no_ref` |

产出字段 **`content`** = Markdown 9 列管道表；**`name`** 必须是 `[Script] UGC Storyboard`。
校验见 `script-table-format.md`。
**HARD — 对话渲染**：同一 continuation 必须按 `script-table-format.md`「对话分镜卡片」把每一表行转成卡片贴进对话。**禁止**把 `|` 管道表贴进 Chat。禁止 code fence。卡片贴完后发 Host tools Continue/Revise。

## 生成（HARD — 只调一次 run_prompt）

1. run_prompt **恰好 1 次**（有参考 = `ugc_ads_storyboard_with_ref`；无参考 = `ugc_ads_storyboard_no_ref`）。必挂商品图 URL；角色图 / 场景图 / 参考视频 URL 有才加。图进 `image_url(s)`，视频进 `video_url(s)`。**禁止传 `nodeIds`**。不要挂 Prompt 文本。
2. 成功：读 `items[].content` → `ScriptDraftText`。`name` = `[Script] UGC Storyboard`。同一 continuation 按「对话分镜卡片」贴进对话。
3. 禁止因为「没有 `storyboard_script`」再调一次 run_prompt。
4. 只有缺 GFM 分隔行 / 非 9 列 / 缺 `content` 才允许再调 **同 key** 的 run_prompt。行数少于 `StoryboardRowCount` **不要**重试。
5. 有参考视频却返回无法访问 → 非法；重试并在输入顶部说明参考已挂上。缺 Character/Scene Prompt 不阻塞。

- 参考：产品主图；有参考视频时一并挂上。不要挂 brief / Prompt 文本 / 分镜表
- 输入：
```text
Product Information: {ProductBrief}
Key Selling Points: {SellingPoint}
Character Description: {CharacterPromptBody 或 (none)}
Scene Description: {ScenePromptBody 或 (none)}
Video Duration: {SessionVideoDuration}s
Storyboard Rows: {StoryboardRowCount}
User Language: {SessionScriptLanguage}
Reference Video: {<<<video_1>>> 或 (none)}
Reference Video Notes or Transcript: {ReferenceNotesOrNone}
Reference Use Scope: {ReferenceUseScopeOrNone}
Character Role: {CharacterRoleOrNone}
Visual Tone: {VisualToneOrNone}
Voiceover Pace (HARD): If a shot has speech (on-camera or V.O.), Voiceover Narration word count ≈ Duration_seconds × 2 (~2 words/sec; ±1 word). No speech → N/A (not empty). Do not write denser lines to fill time.
Action (HARD): Write only the physical action. Exactly one main action that can be completed within this shot's Duration. Do not describe identity, wardrobe, or location — those come from attached character/scene images. No Character/Subject or Scene columns.
Expression (HARD): Write how the face/energy changes inside the shot (start → mid → end). Do not write one held emotion for the whole duration.
Voice delivery (HARD): Keep ~2 words/sec, but require natural pitch, stress, and brief breaths — not flat or metronome speech.
On-Screen Text (HARD): 3–15 words summarizing the current narration (need not match Voiceover verbatim); emojis allowed. No on-screen copy → N/A.
Table columns (HARD): exactly 9 in this order: Shot Number | Duration | Shooting Style | Action | Expression | Lighting | Lip Sync | Voiceover Narration | On-Screen Text
```
