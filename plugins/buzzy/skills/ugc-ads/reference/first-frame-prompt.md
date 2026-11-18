# UGC ADS — 首帧正文（变槽）

仅当 `first_frame` 仍 enabled 且本段需要生成首帧时使用。
agent **按本文件模板直接写出**各段首帧 Prompt，禁止再调 run_prompt 获取。Prompt 不进 Chat。
extract 仍是内存变量 `ExtractVideoContents[i-1]`，必须逐字内联。
媒体只挂**实际参考图**的 URL（`image_url` / `image_urls`，以 tool 声明为准），数量 = 主句里出现的 `<<<image_n>>>` 个数（1–3）。**禁止传 `nodeIds`**。prompt 正文不要写 HTTPS / `@Image`。
`title` = `[First Frame] Video {i}`；画幅 = `SessionRatio`。
`generate_image.model` = `<available_models>` Image 表 **Nano Banana 2** 行的 `model` 列原文（`name` 只用来找行）。Edit 重生成仍用该行。
**HARD**：`generate_image` 只返回 `task_id`。同一 continuation 必须反复 `get_task` 直到 `TASK_STATE_SUCCEEDED`（PENDING/RUNNING 就继续查，不要停、不要等用户），记下素材 URL。并发 ×N 时每个 `task_id` 都要轮询到终态。Apps widget 不能代替轮询。后续成片的 `generate_video` 用这个 URL，禁止把 `node_id` 当素材入参。

槽位来源见 `slot-adaptation.md`。按下表选 **恰好一套** 主句 + 末尾句，禁止提及不存在的槽。

## 3 槽：角色 + 产品 + 场景

参考顺序：角色图 → 产品主图 → 场景图。

主句：

```text
Generate the first frame image based on the storyboard content. The character is <<<image_1>>>, the product is <<<image_2>>>, the scene is <<<image_3>>>.
```

末尾 Closing Fixed Sentence：

```text
Generate exactly ONE full-screen image showing the FIRST FRAME of the FIRST shot described below. The character is <<<image_1>>>, the product is <<<image_2>>>, the scene is <<<image_3>>>,with low saturation, natural lighting, smartphone camera quality, a completely authentic non-AI look, and subtle image noise.
```

## 2 槽：角色 + 产品（无场景）

参考顺序：角色图 → 产品主图。

主句：

```text
Generate the first frame image based on the storyboard content. The character is <<<image_1>>>, the product is <<<image_2>>>.
```

末尾句：

```text
Generate exactly ONE full-screen image showing the FIRST FRAME of the FIRST shot described below. The character is <<<image_1>>>, the product is <<<image_2>>>,with low saturation, natural lighting, smartphone camera quality, a completely authentic non-AI look, and subtle image noise.
```

## 2 槽：产品 + 场景（无角色）

参考顺序：产品主图 → 场景图。

主句：

```text
Generate the first frame image based on the storyboard content. The product is <<<image_1>>>, the scene is <<<image_2>>>.
```

末尾句：

```text
Generate exactly ONE full-screen image showing the FIRST FRAME of the FIRST shot described below. The product is <<<image_1>>>, the scene is <<<image_2>>>,with low saturation, natural lighting, smartphone camera quality, a completely authentic non-AI look, and subtle image noise.
```

## 1 槽：仅产品

参考：产品主图。

主句：

```text
Generate the first frame image based on the storyboard content. The product is <<<image_1>>>.
```

末尾句：

```text
Generate exactly ONE full-screen image showing the FIRST FRAME of the FIRST shot described below. The product is <<<image_1>>>,with low saturation, natural lighting, smartphone camera quality, a completely authentic non-AI look, and subtle image noise.
```

## 全文模板（复制后替换）

```text
{OpeningSentence}

Match the referenced images in order. Compose ONE photorealistic UGC first-frame still for Video {i}, opening shot {OpeningShotNumber}, aspect ratio {SessionRatio}.

Requirements (HARD):
- Follow the opening shot in the inlined storyboard extract below. Do not invent conflicting beats.
- Stay consistent with every referenced <<<image_n>>> listed in the opening sentence.
- If both character and scene images are referenced: take the person from the character image and the environment from the scene image. Do not blend two different rooms.
- Authentic UGC / non-studio look; no extra text overlays, watermarks, or UI chrome.
- Output a single still suitable as the video starting frame.

Storyboard extract for Video {i} (inline — opening shot {OpeningShotNumber}; verbatim, in-memory only):

{ExtractVideoContent}

{ClosingFixedSentence}
```

`{ExtractVideoContent}` = `ExtractVideoContents[i-1]` 逐字全文。禁止省略末尾句或挪到 extract 之前。禁止空占位、`@Image` 或 URL。
