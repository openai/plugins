# UGC ADS — 角色 / 场景

阶段轮到且仍 enabled 时自动做（不要等额外按钮）。
该跑：agent **直接写出** Prompt（不上 Chat），再按 Prompt 成图。
**禁止**调 `ugc_ads_character_prompt` / `ugc_ads_scene_prompt` 或其它 run_prompt 获取这些正文。
`skip` 且无自供图 → 不做；`provided` → 只绑定。见 `slot-adaptation.md`。

角色图 / 场景图的 `generate_image.model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文（`name` 只用来找行）。
**HARD — 画幅**：角色图 / 场景图的 `generate_image.aspectRatio` **固定 `9:16`**。禁止写 `SessionRatio`、禁止跟规格提问画幅。首帧 / 成片仍用 `SessionRatio`，不要被本步带偏。

---

## 1. 角色 / 场景 Prompt（agent 写）

- 要场景，或用户已给场景图但仍需 Scene 正文 → 写 `ScenePromptBody`
- 要角色且无用户模特图 → 写 `CharacterPromptBody`
- **同轮先写 `ScenePromptBody`，再写 `CharacterPromptBody`**（角色背景槽要对齐场景正文）。然后两张图**并发**成图。
- 依据：产品主图事实、`ProductBrief`、`SellingPoint`、`ExecutionGoal` / `CharacterRole` / `VisualTone`、`SessionScriptLanguage` / Duration。画幅不读 `SessionRatio`，本步固定 `9:16`
- Prompt 语言固定 English。不上 Chat。写完记在内存：`CharacterPromptBody` / `ScenePromptBody`。成图只吃这份正文，不要再调 run_prompt。

### 角色 Prompt 要求

按下面**固定句式**写出一条 English `CharacterPromptBody`。槽名仅中文标注，**禁止**抄进 Prompt；填入值必须 English。禁止另起一条自由场面描述。旧规则只约束怎么填槽。

默认模板：

```text
A raw front-camera selfie video snapshot of a [年龄/性别/外貌特征], [动作与场景位置], looking directly into the lens and talking with [微表情/说话状态]. Wearing [服装描述]. Natural healthy skin tone with soft warmth, smooth mobile sensor texture without over-sharpening. Balanced natural [光线], vivid and realistic everyday colors, [背景环境细节] background. Authentic iPhone front camera video still, lifelike saturation, no grey wash, no desaturation, no cinematic color grading, no phone in hands, no screen UI, 9:16.
```

| 槽 | 怎么填 |
|----|--------|
| `[年龄/性别/外貌特征]` | 从商品受众推断的年龄段、性别、体态、发型发色、五官 |
| `[动作与场景位置]` | 默认：自拍机位下的日常站/坐位置。**有 `ScenePromptBody`（HARD）** → 必须落在场景正文的同一空间 / 同一坐具或站位，禁止另换房间 |
| `[微表情/说话状态]` | 默认对镜说话时的表情与口型 |
| `[服装描述]` | 日常穿着，禁止奢侈造型 |
| `[光线]` | **必须**跟 `[背景环境细节]` 匹配（如 `indoor daylight` / `outdoor daylight` / `overcast window light`）。模板里的 `Balanced natural` **禁止删、禁止再写一遍**。禁止影棚 / 电影广告光。**有 `ScenePromptBody`（HARD）** → 与场景 `[光线]` / `[光源位置]` **同一套用词**，禁止另写光源 |
| `[背景环境细节]` | **有 `ScenePromptBody`（HARD）** → **强制对齐场景 Prompt 描述**：空间类型、家具、环境元素必须从 `ScenePromptBody` 的 `[空间类型]` / `[主体家具/背景设施]` / `[前景物体细节]` 转写，禁止另编一处背景。无场景正文：与该商品最自然使用处相关的日常环境，不要无依据默认家里 |
| 画幅 | **固定写 `9:16`**。禁止填 `SessionRatio` / 规格提问画幅 |

**默认机位（HARD）**：front-camera selfie + `looking directly into the lens and talking with …`。仅当用户本轮 / `ExecutionGoal` / `CharacterRole` **点名**了不同出镜方式（开箱、不看镜头、演示、侧拍等）才改 `[动作与场景位置]` 和对镜/说话从句；其余句式、皮肤质感句、片尾句不动。

片尾**只许**这一句：`Authentic iPhone front camera video still, lifelike saturation, no grey wash, no desaturation, no cinematic color grading, no phone in hands, no screen UI, 9:16.`
禁止再追加 `photorealistic` / `ordinary consumer` / `low-end smartphone camera` / `slight film grain` / `authentic handheld UGC` / `imperfect framing` 等旧质感词。

补充（只约束填槽，不另写正文）：

- 像真实消费者，不是专业模特 / 网红。Mainstream 好看，但自然、可接近；保留毛孔、轻微瑕疵、不对称、碎发。禁止磨皮、美颜、影楼光、奢侈造型。
- **必须与商品完全分离**：禁止出现商品、包装、品牌、拿着/使用/展示商品、看向商品。受众画像只通过外貌与环境间接体现。
- 现场感应是随手自拍，不是广告摆拍。有 `CharacterRole` / `VisualTone` / `ExecutionGoal` → 填槽时遵守，不要另起段落。
- **背景对齐（HARD）**：只要本轮会写或已有 `ScenePromptBody`，角色的 `[背景环境细节]` / `[光线]` / `[动作与场景位置]` 必须与该正文描述一致。禁止角色成图挂场景图。

### 场景 Prompt 要求

按下面**固定句式**写出一条 English `ScenePromptBody`。槽名仅中文标注，**禁止**抄进 Prompt；填入值必须 English。禁止另起一条自由场面描述。旧规则只约束怎么填槽。

默认模板：

```text
A casual vertical smartphone photo taken from a seated perspective on [拍摄起始位置/座椅], eye-level POV looking towards [视觉焦点/正前方主体]. [前景物体细节] in the immediate foreground, [座椅/桌角等边缘] visible at the bottom corner, [主体家具/背景设施] straight ahead with [屏幕或环境细节状态]. Balanced natural [光线] from [光源位置], true-to-life everyday colors, realistic mobile phone camera field of view. Cozy lived-in [空间类型], no high angle, no overhead shot, no top-down perspective, no elevated angle, no wide-angle room overview, no professional interior photography, 9:16.
```

| 槽 | 怎么填 |
|----|--------|
| 开头 `vertical` | **固定保留**（角色/场景图始终 `9:16`）。禁止因规格提问画幅删掉该词 |
| `[拍摄起始位置/座椅]` | 默认坐着的起始位；优先该商品最自然使用处（沙发、餐椅、办公椅、公园椅），不要无依据默认家里 |
| `[视觉焦点/正前方主体]` | 平视正前方的环境主体；禁止写成人物或商品 |
| `[前景物体细节]` | 近景日常物；禁止商品 / 包装 / 品牌 |
| `[座椅/桌角等边缘]` | 画面底部可见的椅缘、桌角、膝前平面 |
| `[主体家具/背景设施]` | 正前方家具或设施 |
| `[屏幕或环境细节状态]` | 屏幕 / 窗 / 灯等状态；禁止品牌 UI / 商品特写 |
| `[光线]` | **必须**跟空间匹配（如 `daylight` / `window light` / `overcast daylight` / `warm interior light`）。模板里的 `Balanced natural` **禁止删、禁止再写一遍**。禁止影棚 / 电影广告光 |
| `[光源位置]` | 光线来处（如 `a window on the left`）；无窗则写真实光源，不要硬写窗户 |
| `[空间类型]` | living room / kitchen / cafe / office 等，跟商品真实使用处。默认保留 `Cozy lived-in`；空间明显不是室内日常处时，只改气氛词，不要硬写 cozy home |
| 画幅 | **固定写 `9:16`**。禁止填 `SessionRatio` / 规格提问画幅 |

**默认机位（HARD）**：seated perspective + eye-level POV。仅当用户本轮 / `ExecutionGoal` / `VisualTone` **点名**了不同机位（站立、俯拍、跟拍等）才改起始位和对句；其余句式、片尾句不动。禁止无依据改成俯拍或房间全景。

片尾**只许**这一句：`no high angle, no overhead shot, no top-down perspective, no elevated angle, no wide-angle room overview, no professional interior photography, 9:16.`
禁止再追加 `authentic handheld` / `casual medium-wide` / `slight shake` / `subtle noise` / `authentic UGC` 等旧镜头词。禁止写「中景/广景」或「留出人物站位」。

补充（只约束填槽，不另写正文）：

- **禁止**写人物、肢体、服装、表情、动作、商品本身或商品特写。
- 环境来自该商品最自然的真实使用处；空间要够一个人坐/用，但不要为留站位改成广角全景。
- 有 `VisualTone` / `ExecutionGoal` → 填槽时遵守，不要另起段落。

---

## 2. 成图

该跑的 Prompt 写好后，**同轮并发**按各自 Prompt 正文成图。不要再挂产品图当生成参考。
角色图 / 场景图都**只吃自己的 Prompt**。角色成图 **禁止**挂场景图当参考。

`model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文。
`generate_image.aspectRatio` **固定 `9:16`**（HARD）。禁止传 `SessionRatio` 或规格提问画幅。
角色成图 title = `[Character] Creator`；场景成图 title = `[Scene] {短名}`。
**HARD**：`generate_image` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（PENDING/RUNNING 就继续查，不要停、不要等用户），记下素材 URL。Apps widget 不能代替轮询。后续 `generate_image` / `generate_video` / run_prompt 都用这个 URL，禁止把 `node_id` 当素材入参。
有 Avatar → 跳过角色 Prompt + 成图。有匹配场景图 → 跳过场景成图。`scene = skip` 且无场景图 → Scene Prompt 也不做。
全部成功 → 正文写状态句，文案按 SKILL §双通道。立刻 Advance 到 script 等待提问。
