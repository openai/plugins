# 3D CGI — 写成本片词（`prompt`）

要出视频必须有一份可用的 CGI prompt（生成或自供）。Jump / FastForward 会执行本步但不推中间提问，不是跳过本步。

**禁止**调 run_prompt。**禁止**发明 `prompt_key`。词由 agent 按本文件 + 按需知识库直接写出。

**HARD — Chat 打印替代画布节点**：写出后同一 continuation 必须把全文打印进对话（禁止 code fence，禁止说 on the canvas）。还没打印 = 本步未完成，禁止出片。成片时 `generate_video.prompt` = 已打印 `content`（按 SKILL §占位符补图 / 参考视频），不要指望宿主读节点。

## 何时读哪些知识库

写词前先读本文件。然后按缺口补读，不要一次把所有 reference 塞进上下文：

| 缺口 | 读 |
|------|----|
| 前 2 秒怎么抓注意力 | `hook-framework.md` |
| 渲染风格光谱 | `render-styles.md` |
| 材质 / PBR / SSS | `materials.md` |
| 灯光 / HDRI / 焦散 | `lighting-library.md` |
| CG 运镜 | `camera-language.md` |
| 粒子 / 体积特效 | `particles.md` |
| 写完自检 | `mistakes.md` |
| 需要完整样例形状 | `examples.md` |

## 一次写作（HARD — 默认）

当需要**生成** `prompt`，且内存还没有可用词：

按 **Master Template** 写出**一份**结构化词，覆盖本片 `VIDEO_DURATION`（2–10s）整段，不是多段分章。连续运动优先，不要写一串硬切。

必须写入的事实：

- 用户 brief + 问询字段（`SceneGoal` / `RenderStyle` / `HookPlan` / `CameraPlan` / `MaterialPlan`）
- `VIDEO_DURATION` / `VIDEO_RATIO`（不要写死 720p / 4K / 60fps；分辨率由成片填参继承）
- 已挂参考：词里用 `<<<image_n>>>` / `<<<video_n>>>` 点名，不要 `@material[name]`，不要 HTTPS

写完同一 continuation **立刻全文打印**：

```markdown
Here is the CGI prompt:

{full structured prompt}
```

可附 `Your CGI prompt is ready.`
禁止 code fence。打印后 `PromptGenerated = true`，写入内存 `CgiPromptText`。

普通模式：打印后立刻出词后提问（见 SKILL §`prompt`），然后停。
FastForward：本拍只打印，**下一拍**再 `generate_video`。

已经打印过一份词 → **禁止**无故重写。Modify / Rollback(`prompt`) 才按用户说明改写后重打。只点修改没写要改什么 → 停着问要改哪。

## Master Template

按这个骨架写。2s 片可压成 Hook + 一个主动作；**Opening Hook 必须在前 2 秒**（2s 片 = 整段都是钩子）。

```
[OPENING HOOK - 1–2 sentences establishing immediate visual intrigue]

Camera: [movement, angle, lens, DOF, easing — not a promised fps]

Render Style: [Pixar-style / photorealistic / low-poly / cel-shaded / isometric / …] 3D rendering

Lighting: [Key direction + Kelvin], [Fill], [Rim], [HDRI / GI], [caustics or volumetrics if any]

Subject/Environment: [geometry, scale, arrangement]

Materials & Surfaces: [PBR / SSS / refraction / wear — from materials.md]

Motion/Animation: [procedural / physical / artistic; speed; duration]

Details & Refinement: [texture, imperfections, dust, weathering]

Atmospheric & VFX: [particles, fog, reflections — from particles.md]

Color Palette: [primary colors, saturation, mood]

Duration: [VIDEO_DURATION seconds]

Composition: [thirds, symmetry, depth layers, focus]

[REFERENCE]
<<<image_n>>> / <<<video_n>>> and what to adopt from each

no background music
```

## 质量标准

每份词必须有：

- **具体数字**："45°/sec orbit" 不是 "nice spin"；"3200K key" 不是 "warm light"
- **时间戳**：运动写清在哪几秒完成多少度 / 多少距离
- **技术导演口吻**：Kelvin、材质物理、运镜曲线；不要影评散文
- **2 秒钩子**写在第一句
- **禁止** `@material[name]` / Higgsfield / 写死 4K / 60fps / codec
- **禁止**在词里写 BGM / background music / scored music / orchestral swell。画内声可以写。末尾必须有 `no background music`
- **禁止**矛盾材质（mirror-polished velvet）
- 连续运动优先，不要多段硬切

长度预期：

- 2–4s：约 8–12 行
- 6–8s：约 15–20 行
- 10s：约 20–25 行

更长 ≠ 更好。2s 产品揭示不要写成 30 行。

## Provide / Skip / Jump

- 用户粘贴完整成片词 → `provided`：全文打印；能用就不要再覆盖用户原文。缺占位则按当前绑定补一行。
- Skip(`prompt`) 后还要出片 → 缺硬底线，问用户。
- Jump(`clip`) → 仍须写出并打印词，本拍不出片。
