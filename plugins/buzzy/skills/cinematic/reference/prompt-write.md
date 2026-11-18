# Cinematic — 写成本片词（`prompt`）

要出视频必须有一份可用的 cinematic prompt（生成或自供）。Jump / FastForward 会执行本步但不推中间提问，不是跳过本步。

**禁止**调 run_prompt。**禁止**发明 `prompt_key`。词由 agent 按本文件 + 按需知识库直接写出。

**HARD — Chat 打印替代画布节点**：写出后同一 continuation 必须把全文打印进对话（禁止 code fence，禁止说 on the canvas）。还没打印 = 本步未完成，禁止出片。成片时 `generate_video.prompt` = 已打印 `content`（按 SKILL §占位符补图 / 参考视频），不要指望宿主读节点。

## 何时读哪些知识库

写词前先读本文件。然后按缺口补读，不要一次把所有 reference 塞进上下文：

| 缺口 | 读 |
|------|----|
| 前 2 秒怎么抓注意力 | `hook-framework.md` |
| 4 / 8 / 10 / 15s 节拍 | `timeline.md` |
| 运镜用词 | `camera-language.md` |
| 灯光 / 气氛 | `lighting-library.md` |
| 调色 | `color-grading.md` |
| 对白 / Foley / 环境音 / 静音（不要写 BGM） | `sound-design.md` |
| 用户点名 TikTok / Shorts / Reels / LinkedIn | `platform-optimization.md` |
| 写完自检 | `mistakes.md` |
| 需要完整样例形状 | `examples.md` |

## 一次写作（HARD — 默认）

当需要**生成** `prompt`，且内存还没有可用词：

按 **Master Template** 写出**一份**结构化词，覆盖本片 `VIDEO_DURATION`（4–15s）整段，不是多段分章。

必须写入的事实：

- 用户 brief + 问询字段（`SceneGoal` / `MoodGenre` / `HookPlan` / `CameraPlan`）
- `VIDEO_DURATION` / `VIDEO_RATIO`（不要写死 720p；分辨率由成片填参继承）
- 已挂参考：词里用 `<<<image_n>>>` / `<<<video_n>>>` 点名，不要 `@material[name]`，不要 HTTPS

写完同一 continuation **立刻全文打印**：

```markdown
Here is the cinematic prompt:

{full structured prompt}
```

可附 `Your cinematic prompt is ready.`
禁止 code fence。打印后 `PromptGenerated = true`，写入内存 `CinematicPromptText`。

普通模式：打印后立刻出词后提问（见 SKILL §`prompt`），然后停。
FastForward：本拍只打印，**下一拍**再 `generate_video`。

已经打印过一份词 → **禁止**无故重写。Modify / Rollback(`prompt`) 才按用户说明改写后重打。只点修改没写要改什么 → 停着问要改哪。

## Master Template

按这个骨架写，允许按时长压缩（4s 可合并 Context / Action），但 **Opening Hook 必须在前 2 秒**：

```
[OPENING HOOK — 2 seconds maximum]
[Hook Technique from hook-framework.md]
[Describe specific sensory trigger]
[Transition to main action at 2-second mark]

[ESTABLISHING CONTEXT — 1–2 seconds]
[Location: geography, architecture, atmosphere]
[Lighting setup from lighting-library.md]
[Color grading approach]
[Time of day / season / weather mood]

[PRIMARY ACTION / NARRATIVE — remainder of VIDEO_DURATION]
[Camera movement from camera-language.md]
[Character action or environmental change]
[Emotional arc or tension point]
[Dialogue / diegetic audio integration points]
[Visual progression: beginning → middle → climax → resolution]

[DEPTH & COMPOSITION]
[Foreground / mid-ground / background]
[Depth cues: atmospheric perspective, focus layers, scale]

[CAMERA SPECIFICATIONS]
[Focal length equivalent: 24mm / 35mm / 50mm / 85mm / 200mm]
[Depth of field: f/1.4 shallow, f/2.8 moderate, f/8 deep]
[Camera movement speed: feet/second or Hz for rotation]
[Focus behavior: locked, breathing, racking]

[LIGHTING SPECIFICATIONS]
[Key light intensity and direction (clock position)]
[Fill light ratio (3:1 standard, 5:1 dramatic)]
[Back/rim light presence and intensity]
[Color temperature in Kelvin]
[Shadow characteristics]

[AUDIO INTEGRATION]
[Dialogue delivery if applicable]
[Foley / ambient / silence — diegetic only]
[Sound-effect timing]
[End with: no background music]

[PACING INSTRUCTION]
[Timing of cuts/transitions]
[Velocity of movement]
[Hold durations]

[MOOD & ATMOSPHERE]
[Emotional target]
[Atmosphere: fog, rain, particles, dust]
[Grain/texture]

[REFERENCE MATERIALS]
[<<<image_n>>> / <<<video_n>>> with the role of each]
[What to adopt from each reference]

[OUTPUT SPECIFICATION]
[Total duration: VIDEO_DURATION seconds]
[Aspect ratio: VIDEO_RATIO]
```

## 质量标准

每份词必须有：

- **具体数字**："3 ft/s" 不是 "fast"；"f/1.4" 不是 "shallow"；"3000K" 不是 "warm"
- **时间戳**："At 4.2s"、"0–2s window"
- **专业电影术语**，不要空泛形容词堆砌
- **2 秒钩子**写在开头两行
- **禁止** `@material[name]` / Higgsfield / 写死 720p
- **禁止**在词里写 BGM / background music / scored music / orchestral score。对白、口型、环境音、Foley、静音可以写。末尾必须有 `no background music`

长度预期：

- 4–8s：约 10–15 行有效描述
- 8–12s：约 20–25 行
- 12–15s：约 25–35 行

用户点名平台时再读 `platform-optimization.md` 改画幅建议与节奏；规格已冻结则**不要**用平台文案覆盖 `VIDEO_RATIO` / `VIDEO_DURATION`。

## Provide / Skip / Jump

- 用户粘贴完整成片词 → `provided`：全文打印；能用就不要再覆盖用户原文。缺占位则按当前绑定补一行。
- Skip(`prompt`) 后还要出片 → 缺硬底线，问用户。
- Jump(`clip`) → 仍须写出并打印词，本拍不出片。
