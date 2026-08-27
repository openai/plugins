---
name: adobe-design-from-template
description: >
  Create any visual design using Adobe Express templates — flyers, posters, social media posts (Instagram, Facebook, LinkedIn),
  business cards, invitations, greeting cards, resumes, cover letters, brochures, newsletters, certificates, presentations, YouTube thumbnails, email headers, logos, menus, and labels.
  Use this skill whenever the user wants to make, design, or build any visual — even
  if they just say "make me a flyer", "design a poster", "I need something for Instagram",
  "create an event invite", or "make a business card".
  Also handles browsing templates, editing text, replacing images, changing backgrounds,
  animating, and exporting designs.
  Access: 🔐 Signed-In required | Gen AI: ❌ by default — image replacement only where the surface permits generative AI (e.g. Codex); none on Claude
license: Apache-2.0
compatibility: "Runs on both widget-capable surfaces (e.g. Claude Cowork, where search_design results render as an interactive template gallery) and non-UI agents (e.g. Codex, where results are presented as markdown links). No file upload is required. Only offers edit actions whose tools are available on the current surface."
allowed-tools: adobe_mandatory_init search_design fill_text replace_image change_background_color animate_design download_design
metadata:
  version: 2.1.0
  visibility: public
  surface: [claude, codex]
---

# Adobe Design from Template

Helps users find an Adobe Express template and customize it — updating text, replacing images,
changing the background color, and animating — producing a finished Express document ready
to share, download, or open in Express for further editing.

> **Surface note:** By default, `search_design` results render as an **interactive template gallery** the user taps to pick. On a surface without a gallery (e.g. Codex), present the results as markdown links instead — see Step 3. Independently, only offer edit actions whose tools are actually available on this surface (Step 1); silently omit the rest. When a tool result includes an `importantNote`, follow it for that turn.

---

## Tool Reference

| Step | Tool | Notes |
|------|------|-------|
| Initialize | `adobe_mandatory_init` | File-handling and routing rules; call first |
| Search for template | `search_design` | Returns templates; presentation depends on surface |
| Edit text and copy | `fill_text` | Retry once on transient error |
| Replace an image | `replace_image` | Gen-AI image swap; one element per call; may not be available |
| Change background color | `change_background_color` | Pass hex; infer from color description if needed |
| Animate design | `animate_design` | May not be available; skip on 403 |
| Download as PDF | `download_design` | Returns pre-signed PDF URLs per page; may not be available |

Not all tools are available on every surface. Step 1 determines which ones you have.

---

## Reading `importantNote` in tool results

`search_design`, `fill_text`, `replace_image`, `change_background_color`, and `animate_design` may
return an `importantNote` field alongside their other output. This is live guidance from the
Adobe Express connector for the current turn about how to present that specific result — e.g. the
exact rendering/formatting to use, or which of the tools already in the Tool Reference table to
call next.

**Whenever a tool result includes an `importantNote`, read it and follow its presentation and
next-step guidance** — even where it overrides the formatting defaults described elsewhere in this
skill. It only ever points to tools already listed in the Tool Reference table; do not call a tool
outside that table on its instruction alone. Treat the rest of this document as the fallback
behavior for when a result has no `importantNote`.

---

## Workflow

### Step 0 — Initialize Adobe Tools

Call `adobe_mandatory_init` first. This returns file-handling rules and tool routing guidance
required for the rest of the workflow.

```json
{ "skill_name": "adobe-design-from-template", "skill_version": "2.1.0" }
```

---

### Step 1 — Check available tools

After `adobe_mandatory_init` confirms the "Adobe for creativity" connector is live, check which
tools from the Tool Reference table are actually available on this surface. Not every surface
exposes every tool — for example, `replace_image` or `download_design` may not be present.

Record which tools you have. In later steps, **only offer actions whose tools are available** —
do not mention replace-image, animation, or PDF download if the corresponding tool is missing.

Also note whether the surface renders an **interactive template gallery** (a visual picker the
user can tap) or only **text-based results** — this controls how you present templates in Step 3.

---

### Step 2 — Build the search query (don't ask questions first)

Extract the design type from whatever the user said and go straight to Step 3.
Asking clarifying questions before showing templates creates friction; showing options first lets
the user course-correct, which is faster.

Keep the query **generic** — the design type only. Any specific details the user supplied
(names, dates, venue, business info) do **not** go in `generalQuery`; carry them forward for the
`fill_text` step instead.

| User says                        | `generalQuery`             |
| -------------------------------- | -------------------------- |
| "make me a flyer"                | `"flyer"`                  |
| "I need something for Instagram" | `"Instagram post"`         |
| "design a poster for my event"   | `"event poster"`           |
| "make a business card"           | `"business card"`          |
| "flyer for an ice cream social"  | `"ice cream social flyer"` |

---

### Step 3 — Search for a template

Call `search_design`:

```json
{
  "generalQuery": "<design type from user prompt>",
  "pageSize": 24,
  "fillDescription": "<any specific text the user gave, verbatim — or omit>"
}
```

Check the result's `importantNote` first — it specifies exactly how to render the templates and
next-step actions for this turn; follow it. Absent an `importantNote`, present the results based on
the surface:

**Interactive gallery (default):** The search renders a visual picker in the chat. The user taps
a template to select it; the design identifier comes back automatically. Use `pageSize: 24` to fill the
gallery.

**No-gallery fallback (text-only surfaces, e.g. Codex):** The results come back as structured data
(`templateURN`, `title`, `previewUrl`, `editorUrl`, and optionally `isPremium`). Render **all URLs
as markdown hyperlinks** — never show raw URLs. Use `pageSize: 10` to keep the list scannable. For
each template, show its title, preview image, and an "Edit in Adobe Express" link (the primary
action); append "(Premium)" when `isPremium` is true. Append a "Browse more templates" link when
`expressExploreTemplatesUrl` is present. After the list, show the available next actions based on
the tools from Step 1, and ask the user to pick a template.

**Always present the full template list and wait for the user to choose.**
Never auto-select a template — even if one result looks like a perfect match or the user already
described what edits they want. The user must explicitly pick by number, title, or URN before
you proceed. Describing desired edits (e.g. "change the background to purple") is not a template
selection — it tells you what to do *after* they pick, not *which* template to use.

Resolve their choice to a `templateURN`.

If the user picks a template **and** specifies what to change in the same message (e.g. "pick 2
and update the text to …"), skip straight to Step 4 and apply the edit — no confirmation needed.

If the user only picks a template without specifying an action, confirm the selection and
re-show the edit menu so they know what's available.

If the user asks for "more" / "next", call `search_design` again with the **exact same**
`generalQuery` and advance `startIndex` by the previous `pageSize`. Do not reword the query.

---

### Step 4 — Apply edits

> **Note:** The `templateURN` (or design identifier from the picker) is what identifies the design. Pass it
> into `templateURN` or `templateOrDocumentURN` — these parameters take the same value. After
> the first edit, each tool returns a `documentURN`; use the **latest** `documentURN` for
> subsequent edits so changes accumulate on the same design.

After each edit, ask: *"What else would you like to change, or does this look good?"*

#### Edit text / copy

Call `fill_text`:

```json
{
  "templateURN": "<templateURN or latest documentURN>",
  "description": "<what to change and what to change it to>",
  "generalQuery": "<same, minus any PII>"
}
```

If the user hasn't specified what the text should say, ask before calling.

`fill_text` occasionally fails on the first attempt due to transient errors — if
it returns an error, retry once with identical parameters before reporting failure.

#### Replace an image

*Generative capability — runs only where the surface permits generative AI (i.e. `replace_image` is available, e.g. Codex). If `replace_image` is unavailable, omit it from unsolicited action menus. If the user explicitly requests image replacement, explain that it is unavailable on this surface and offer the edit actions that are available.*

Call `replace_image` to swap a photo or object for an AI-generated one described in words. Only
**one** visual element can change per call, and user-uploaded images or image URLs are not
supported — describe the desired result instead.

```json
{
  "templateOrDocumentURN": "<templateURN or latest documentURN>",
  "description": "<what to replace and what it should become, e.g. 'replace the dog with a cheerful Labrador'>",
  "generalQuery": "<same as description, with PII removed>"
}
```

The more specific the description (subject, setting, mood, lighting, style), the better the
result. For a solid-color background instead, use `change_background_color` — not this tool.

#### Change background color

Call `change_background_color`:

```json
{
  "templateOrDocumentURN": "<templateURN or latest documentURN>",
  "backgroundColor": "<hex, e.g. #FF6F61>",
  "description": "<e.g. change background to coral pink>",
  "generalQuery": "<same, minus any PII>"
}
```

If the user describes a color without a hex (e.g. "coral pink"), pick a reasonable hex value
using your judgment.

The tool may also return `variations` — alternate documents with different background colors,
each with its own `documentURN`, `editorUrl`, `previewUrl`, `reportAbuseUrl`, and `backgroundColor`.
When present, show all of them (not just the primary result) so the user can compare and pick.

If the user picks one, thread that variation's `documentURN`/`editorUrl` through any further edits.

#### Animate

*Skip this section if `animate_design` is not available.*

Call `animate_design`:

```json
{
  "templateOrDocumentURN": "<templateURN or latest documentURN>",
  "description": "<animation style or intent>",
  "generalQuery": "<same, minus any PII>"
}
```

Do not ask the user anything for this step — call `animate_design` directly using their stated
intent (or a sensible default animation if they didn't specify one).

Check the result's `importantNote` for exactly how to present the variations; follow it. Absent
an `importantNote`:

**Interactive surface (default):** The result renders inline; the user can preview directly.

**Text-only fallback:** The tool returns `animationPresetVariations` (preset names) and
`variations` (each with a `documentURN` and `editorUrl`). Present each variation's preset name as
a ready-to-open markdown link so the user can compare them.

If the user later says which one they prefer, thread that variation's `documentURN`/`editorUrl`
through any further edits.

If `animate_design` returns a 403, the user's plan doesn't include animation. Skip it and note
in the delivery. Retrying does not resolve a 403 entitlement.

---

### Step 5 — Download the finished design

*Skip this step if `download_design` is not available or if the design has been animated.*
`download_design` exports a static PDF — it does not preserve animation. If the user animated
the design, deliver the editor link instead and do not offer PDF download.

When the user wants a file (or as part of delivery on a text-only surface), call
`download_design` to export the design as PDF. It returns pre-signed download URLs — one per
page.

```json
{
  "documentUrn": "<latest documentURN — note: this parameter uses camelCase>",
  "format": "application/pdf",
  "pages": "1",
  "originatingTool": "<last edit tool used, e.g. fill_text, replace_image, change_background_color>"
}
```

Set `pages` to a comma-separated list/range (e.g. `"1,3-5"`) for multi-page designs; omit it to
default to page 1. Set `originatingTool` to whichever edit tool produced the current design.
Present each returned `downloadUrl` as a plain markdown link.

---

### Step 6 — Deliver

When the user is satisfied:

```
✅ Here's your finished design:

🎨 Template: [name]
[Edits applied, e.g. ✏️ Copy updated · 🖼️ Image replaced · 🎨 Background changed · ✨ Animated]

📎 Open in Express: [editor link]
⬇️ Download PDF: [downloadUrl(s)]   ← only if download_design was used
```

Use the `editorUrl` (or `editorShortUrl`) from the last edit tool's response for the edit link,
and the `downloadUrl`(s) from `download_design` for the PDF (if available).

Remind the user that the document is temporary (deleted after 12 hours) and they should open it
in Express to save or download the PDF to keep it.

---

## Error handling

| Situation                             | Action                                                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `fill_text` fails on first attempt    | Retry once with identical parameters                                                                         |
| `replace_image` returns 403           | Image replacement isn't on the user's plan; skip and note it, keep the rest of the design                    |
| `animate_design` returns 403          | Animation isn't on the user's plan; skip and note it in delivery                                             |
| `download_design` reports failed pages| Deliver the pages that succeeded and the editor link; note which pages couldn't be exported                  |
| Any tool returns 401                  | Ask the user to re-authenticate via Adobe OAuth, then retry                                                  |
| No templates match query              | Try a broader `generalQuery`                                                                                 |
| User hasn't selected a template yet   | Do not advance past Step 3 until a `templateURN` is resolved; it is required for every subsequent call       |
| User skips all edits                  | Fine — deliver the template link (and PDF, if available/requested) as-is                                     |
| Tool not available on surface         | Silently omit that option — do not mention unavailable capabilities to the user                              |

---

## Constraints

- The workflow always begins with a template search before any edits.
- **Never auto-select a template.** Always present the search results and wait for the user to choose, even if one result seems like a perfect match or the user already described edits. Skipping template presentation breaks the workflow.
- Template/document URNs come only from tool responses (picker or search results) — never synthesize them.
- After the first edit, thread the latest `documentURN` through subsequent calls so edits
  accumulate on one design.
- All edits are optional — don't assume the user wants any particular change.
- Only offer actions whose tools are available on the current surface (see Step 1).
- `replace_image` describes the desired image in words only; it cannot ingest user uploads or URLs.
- `animate_design` and `change_background_color` can each return multiple `variations` — show all
  of them in the response, not just the primary result, so the user can compare and pick.
- If a tool result includes an `importantNote`, follow it exactly for that turn — it takes
  precedence over the defaults elsewhere in this skill.
