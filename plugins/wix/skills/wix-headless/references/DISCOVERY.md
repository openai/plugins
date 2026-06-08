# Discovery

Capture brand + vibe + imagery + the per-vertical intent inferred from the user's prompt, present a slim plan, get approval, write `.wix/site.json`.

Infer as much as possible from the user's opening message; ask only what's genuinely unknown. Target: **~1:30 of discovery** including user think-time, **≤ 80 s** excluding it.

This phase owns the *domain* of discovery only. Run FLOW — when background work is dispatched, what waits on what, batching, and the transition into Setup/Seed — is owned by `references/PLAN.md` (pre-approval) and `references/BUILD.md` (post-approval).

## Wave 0 — Mode detection (BEFORE any user-facing question)

Frontend mode is the single axis the frontend track branches on. Detect it from the working directory **first** — before the CLI-auth pre-flight, before Q1 — so the rest of Discovery knows which path to take. The detection is a file-existence check; cost is ~1 ms. The axis is binary: **astro (supported) vs custom (anything else, not available yet).**

```
Inspect CWD:

1. CWD is empty (or doesn't exist) → SCAFFOLD MODE (astro).
2. CWD contains `wix.config.json` AND Astro structure (`src/`, `astro.config.mjs`)
   → resume a prior wix-headless run. See SKILL.md § "When NOT to use this skill"
     ("continue or start fresh?" — out of pivot scope).
3. CWD contains `wix.config.json` AND a non-Astro frontend (e.g. `index.html` at
   root, `*.jsx`/`*.tsx`/`*.vue` files) → CUSTOM (non-astro), not available yet.
4. CWD contains source files (`index.html`, `*.jsx`, `*.tsx`, `*.vue`,
   `package.json` from a non-Wix template, etc.) AND no `wix.config.json`
   → CUSTOM (non-astro), not available yet.
```

Capture the resolved value in session scratch as `frontend`:

| Scenario | `frontend` value | Wave 0 next |
|---|---|---|
| Scaffold mode (empty CWD) | `astro` | Continue to Pre-flight below |
| Prompt names a non-astro frontend (Vite, React SPA, etc.) | `custom` | Route to the custom stub — see § "Custom (non-astro) — not available yet" below |
| Existing project detected (cases 3 & 4 above) | `custom` | Route to the custom stub — see § "Custom (non-astro) — not available yet" below |

> **No `AskUserQuestion` for mode detection.** Mode is detected, never asked. If the working directory is ambiguous, default to `custom` and let the not-available message redirect the user (they can re-run with an empty directory for the astro path).

`frontend` flows into three places:
- `scaffold.sh --frontend <value>` — the scaffolder's input (only `astro` is built; custom does not scaffold — see § "Custom (non-astro) — not available yet").
- `init-site-json.mjs --frontend <value>` — "After Approval" § 2 (records it in the slim site.json snapshot; only reached on the astro path).
- Orchestrator session scratch — every downstream branch reads the scratch value, not the file: the frontend-track project-prep script (`seed-utilities.sh --template astro`) and the SEED Layout-import bridge. (Business-track steps — app install, seeders — never read it.)

## Custom (non-astro) — not available yet (when `frontend === "custom"`)

Custom frontends are **not available yet** — astro is the only supported frontend. Do **not** run the interview, scaffold, Designer, Setup, or Seed. Open `<SKILL_ROOT>/references/custom/INSTRUCTIONS.md`, surface its not-available message to the user, and **stop**:

> *Custom (non-astro) frontends are not available yet — astro is the supported frontend. Re-run with the astro frontend (start from an empty directory), or check back later.*

No `.wix/site.json` is written and no `BUILD.md` flow runs. The intended future shape for the custom track (init scaffold + shared business track + per-pack SDK wiring) is recorded in `references/custom/INSTRUCTIONS.md` § "Intended future shape"; the retired Integrate (Path B) flow in `SETUP.md` is its historical reference. See `PLAN.md` § "Custom (non-astro) frontends — not available yet" for the routing.

---

## Pre-flight — Verify CLI auth (BEFORE any user-facing question)

The first Wix touch is the post-approval scaffold (`scaffold.sh` → `npm create @wix/new@latest headless`), which creates a business + project against the user's Wix account and so requires an active CLI session. Without one it fails — and because the scaffold now runs **after** approval (`BUILD.md` run-step 0), a logged-out user wouldn't find out until they'd done the whole interview *and* approved, only to have the build fail immediately. Run the auth check foreground here so a logged-out user sees the login prompt before any `AskUserQuestion`.

```bash
npx @wix/cli@latest whoami >/dev/null 2>&1
```

- Exit 0 → continue to Step 0.
- Exit non-zero → **run `npx @wix/cli@latest login` yourself; do NOT punt to the user.** Steps:
  1. `Bash` tool with command `npx @wix/cli@latest login`, `run_in_background: true`. No shell `&`, no `mktemp` redirect, no chaining.
  2. Read the harness output-file path from the tool reply's `<bash-stdout>` (or use `TaskOutput`).
  3. Parse line 1 for `{"event":"awaiting_user","userCode":"…","verificationUri":"…"}` (ignore any `TimeoutNaNWarning` on later lines).
  4. Surface in one plain-prose message — *not* `AskUserQuestion`: *"Open `<verificationUri>` in your browser and enter the code `<userCode>` — I'll continue once you've completed the login."*
  5. Wait for the harness `task-notification` with `<status>completed</status>`; confirm with `whoami`, then proceed to Step 0.

  Full recovery reference: [`shared/AUTHENTICATION.md`](shared/AUTHENTICATION.md#wix-login-from-a-non-interactive-agent).

## Step 0 — Infer Vertical(s) and Business Context

The user's opening message typically names what they want: *"build me a skincare store"*, *"I want to sell handmade jewelry"*, *"create a coffee shop website"*.

From the opening message, extract:
- **Vertical(s)** — which packs to load. See the routing table in `SKILL.md` § "When This Skill Triggers".
- **Business / product context** — feeds into brand-name suggestions, vibe options, product templates, image prompts.

If the opening message is too vague to infer a vertical (e.g., *"build me a site"*, *"I want to go online"*), ask **one conversational clarifier** (NOT an `AskUserQuestion`): *"What do you want your site to do — sell things, publish content, take bookings?"* One sentence. Only ask if you genuinely cannot infer.

**Do not ask the user what features they want.** Features are determined by the inferred vertical(s). The user reviews and adjusts the plan at Step 3.

---

## Step 1 — Brand Name

Use `AskUserQuestion` with a single-select question.

Generate **3–4 brand name suggestions** relevant to the business context, plus a "Type my own" option:

> *"What should we call your brand?"*

Options: [3–4 generated names], Type my own.

Guidelines for generated names:
- Short (1–3 words), memorable, relevant to the business context
- Mix styles: one punchy/modern, one descriptive, one abstract/evocative
- Avoid generic filler (*"Pro Store"*, *"Best Shop"*)

If the user picks *"Type my own"*, follow up conversationally: *"Sure — what should I call it?"*

If the user already named the brand in the opening message, skip this step.

### After Q1 — read the loaded pack files; scaffold inputs

Once the brand is confirmed, read the loaded pack contents (to compose the plan) and prepare the scaffold inputs (slug + frontend value) for later. **The scaffold is NOT dispatched during Discovery** — it is dispatched post-approval (`BUILD.md` run-step 0), so the funnel can present the plan without waiting on anything. This section defines only the slug derivation + the `scaffold.sh` command shape.

**(a) Read every pack in the resolved set.** The full resolved set lives in SKILL.md § "When this skill triggers" (third column). For example, a `stores` run reads four files: `stores.md`, `cms.md`, `ecom.md`, `gift-cards.md`. Read the whole resolved set at once — do **not** read the top-level pack alone, then discover its `requires:` and issue a second batch.

- `Read <SKILL_ROOT>/references/verticals/<pack>.md` for each pack in the resolved set (resolve `<SKILL_ROOT>` per SKILL.md § "Path resolution"). Read individual `.md` files; `Read` on the directory returns `EISDIR`.

These reads pre-load the `routes:`, `apps:`, `requires:`, and `disabled` fields needed to compose the Pages table at Step 3.

**(b) The scaffold inputs.** The scaffolder is invoked as:

```bash
bash <SKILL_ROOT>/scripts/scaffold.sh <slug> "<brand>" --frontend <frontend> 2> <tempfile>
```

`<frontend>` is `astro` — the only supported (and only scaffolded) frontend. The scaffold step is reached only on the astro path; a custom frontend never gets here, because Wave 0 routes it to the stub before Q1 (§ "Custom (non-astro) — not available yet"). If the opening prompt explicitly names a non-astro frontend (Vite / React SPA / etc.), Wave 0 already set `frontend = "custom"` and short-circuited — this step does not run.

**Slug derivation:** lowercase the brand, then **STRIP every character not matching `[a-z0-9]` — do NOT replace them with hyphens or underscores**. Truncate to 20 chars. The `scaffold.sh` pre-flight enforces `^[a-z0-9]{3,20}$` and rejects anything else with exit 2; a rejected slug forces a re-run of the ~30 s scaffold (the indie-bookshop-class regression).

   - Substitute `<brand>` with the user's confirmed brand (preserve original case; quotes are passed by the shell). Substitute `<slug>` with the validated slug.
   - The script passes bare `--site-template` so non-interactive scaffolding stays on the blank starter. Keep the new-site flow there unless the skill is explicitly redesigned around another scaffold. (Without it, `@wix/create-new` ≥0.0.72 prompts for a template and aborts in the agent's non-TTY shell.)
   - Append timing to `.wix/run.json.phases[]` as `{ phase: "scaffold", seconds: <duration>, started: $STARTED_AT, ended: $ENDED_AT }`.

Correct (strip-and-concatenate):
- `"Bloom & Root"` → `"bloomroot"` (not `"bloom-and-root"`, not `"bloom-root"`)
- `"Page & Ember"` → `"pageember"` (not `"page-ember"`, not `"page-and-ember"`)
- `"ACME, Co."` → `"acmeco"`
- `"42 Below"` → `"42below"`
- `"Single-Origin Roasters"` → `"singleoriginroasters"` (cap at 20 → `"singleoriginroaster"` if truncation needed)

**Wrong** (kebab-case / snake-case): any slug containing `-`, `_`, or any other separator. The transformation is **strip**, not **replace** — there are no separators in a valid slug.

Then continue to Q2.

---

## Step 2 — Vibe

Use `AskUserQuestion` with a single-select question. Generate **4 brand personality options** tailored to the inferred business context, plus "Something else":

> *"What's the vibe for [brand name]?"*

Example options for a jewelry store:
- **Bold & premium** — luxury feel, dark tones, sharp typography
- **Clean & modern** — minimal, lots of whitespace, crisp lines
- **Warm & approachable** — friendly, inviting, earthy tones
- **Something else** — let me describe it

If the user picks "Something else", follow up with `AskUserQuestion` using a text input.

---

## Step 2.5 — Imagery preference

Before crafting the aesthetic direction and presenting the plan, capture the user's imagery preference. Hold this `imagery` flag in orchestrator session scratch — it gates whether downstream phases generate AI imagery (Wix AI credits) or rely on CSS-only themed blocks. The flag is **not** persisted to `.wix/site.json`; the orchestrator inlines it into the prompts of any subagent that needs to branch on it (Image Phase 1 dispatch, Image Phase 2 gate).

**Skip rule.** If the user's opening prompt explicitly mentioned imagery — phrases like *"with photos"*, *"with images"*, *"AI imagery"*, *"product photos"*, *"with pictures"* — skip the Q3 `AskUserQuestion` call and default `imagery` to `"ai-generated"`. Re-asking would feel redundant ("you already said you wanted images"). The credit estimate (§ 2.5.1) and balance fetch (§ 2.5.2) still run so the captured intent has the right numbers for the plan's Imagery line — only the `AskUserQuestion` itself is skipped.

### 2.5.1 — Compute the credit estimate

In session scratch, compute `<estimatedCredits>` from the loaded packs and the per-vertical intent inferences (see "After Approval" § 1 for the inference rules — `productCount` defaults to 3, `postCount` defaults to 6).

```
estimatedCredits =
    1                                          // hero / home decorative
  + 2                                          // additional section decoratives
  + (cms loaded         ? 2                              : 0)   // /about + /faq hero images
  + (stores loaded      ? stores.productCount            : 0)   // default 3 when unknown
  + (blog loaded        ? blog.postCount                 : 0)   // default 6 when unknown
  + (forms loaded       ? 0                              : 0)   // forms never trigger imagery
  + (gift-cards loaded  ? 0                              : 0)   // disabled pack — skip
```

Packs with `disabled: true` contribute 0 regardless. The integer total is what we show. **Reuse** the `productCount=3` and `postCount=6` defaults from "After Approval" § 1 — do not invent new numbers.

Worked examples:
- Skincare (stores + cms, productCount=3, no blog): `1 + 2 + 2 + 3 + 0 + 0 + 0 = 8`.
- Coffee shop (stores + cms + blog, productCount=3, postCount=6): `1 + 2 + 2 + 3 + 6 + 0 + 0 = 14`.

### 2.5.2 — Fetch the AI-credit balance

`npx @wix/cli@latest token` **without** `--site` mints an **account-scoped** token. With that token, the balance endpoint at `POST https://manage.wix.com/credit-transactions/v1/credit-transactions/get-account-balance` returns the current periodic credit balance + cap.

```bash
ACCOUNT_TOKEN=$(npx @wix/cli@latest token)   # NO --site — mints account-scoped
curl -sS -X POST \
  -H "Authorization: Bearer $ACCOUNT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://manage.wix.com/credit-transactions/v1/credit-transactions/get-account-balance"
```

Successful response (HTTP 200):
```json
{
  "periodicCredits": { "balance": 250, "cap": 250 },
  "creditBalanceBreakdown": [
    { "subscriptionId": "…",
      "usageRules": [{ "period": "MONTH", "balance": 250, "cap": 250, "resetDate": "…" }] }
  ]
}
```

Hold `balance = response.periodicCredits.balance` and `cap = response.periodicCredits.cap` in scratch.

**Recovery / fallback (in order):**

1. **`wix token` (no `--site`) fails** — surface the error from the CLI; that is a `wix login` problem, not a balance-lookup problem. Set `balance = null` only after the CLI failure surfaces.
2. **POST returns 401/403** — the **account-scoped** token (no `--site`) was rejected. Re-mint the account-scoped token once and retry. (The site-scoped "never re-mint" rule in `SEED.md` / `SETUP.md` does not apply here — these are distinct token caches.) If still 401/403, set `balance = null` and proceed.
3. **POST returns 4xx other than 401/403** — log the response in scratch (do not crash) and set `balance = null`. The endpoint is POST-only; a GET returns 400.
4. **Network error / timeout** — set `balance = null`. The credit estimate (§ 2.5.1) is unaffected; only the Q3 description's *"Current balance: …"* tail goes silent.

> **Don't share the token across calls.** The account-scoped token is for account-level reads only (balance, account metadata). Every other site-operating call in this skill uses `npx @wix/cli@latest token --site "$SITE_ID"` — site-scoped — per `references/shared/AUTHENTICATION.md`. Site-scoped tokens are rejected by the account endpoint and vice-versa.

### 2.5.3 — Ask Q3

Ask **Q3** via `AskUserQuestion` with two single-select options. Interpolate `<estimatedCredits>` (from § 2.5.1) and the balance (from § 2.5.2) into the AI-generated `description:` before issuing the call.

> *"How should we handle imagery?"*

Options:
- **Themed blocks (Recommended)** — `description:` *"Polished CSS-only design. ~6 min build. Uses 0 Wix AI credits."*
- **AI-generated imagery** — `description:` *"Bespoke images per product and section. ~10 min build. Uses ~<estimatedCredits> Wix AI credits (1 image = 1 credit). Current balance: <balance> / <cap>."*

If `balance === null`, drop the trailing *"Current balance: …"* sentence entirely (do not print *"Current balance: unknown"* — silence is the contract). The AI-generated option then reads: *"Bespoke images per product and section. ~10 min build. Uses ~<estimatedCredits> Wix AI credits (1 image = 1 credit)."*

→ **Verify Q3:** Themed blocks description ends `Uses 0 Wix AI credits.`. AI-generated description contains the substring `Uses ~<estimatedCredits> Wix AI credits (1 image = 1 credit).` (with `<estimatedCredits>` replaced by the integer). When balance is known, description also ends with `Current balance: <balance> / <cap>.`. When balance is unknown, description ends with `(1 image = 1 credit).` and no balance text follows.

Capture the answer as `imagery: "themed-blocks" | "ai-generated"` in session scratch. The downstream dispatch gates that consume it are owned by `BUILD.md § "Imagery gates"`.

The captured `imagery` value lives in orchestrator session scratch (alongside the inferred per-vertical intent — see "After Approval" § 1). It is **not** written to `.wix/site.json`; subagents that need to branch on it receive it inlined in their prompts.

---

### Craft the aesthetic direction (in session scratch)

Based on vertical + brand personality + audience, craft a **2–3 sentence aesthetic direction** like a designer would. Decide — don't ask more questions.

Example:
> *"For Bloom & Root, I'm going with an organic editorial aesthetic — think Kinfolk magazine meets a botanical garden. Warm cream backgrounds, deep forest green accents, Playfair Display for headings paired with Source Sans 3 for body text. Subtle leaf-pattern overlays and generous whitespace to let the products breathe."*

> **Do NOT print this aesthetic direction as a standalone message.** Hold it in session scratch and weave it into the plan (Step 3) as the opening **Design Direction** section. Printing it above the plan detaches the most emotionally important content from the rest. Keep Q2 → plan presentation tight.

---

## The Designer's inputs

The Designer owns **the design itself** — it returns a framework-agnostic JSON spec (tokens + brand-voice strings) and **writes no files**. It is framework-blind and application-blind by construction, so its inputs are *judgment* inputs only, and they are all produced here in Discovery and held in scratch:

- **Brand**: `{ name, description }` from Q1 (description = the user's opening business context, distilled to one line).
- **Aesthetic direction, color palette, typography, mood, page color strategy**: from the craft step above.

The application inputs (loaded packs, packs-with-components, disabled packs, navigation links) are **not** passed to the Designer — they go to the **Composer**. Hold them in scratch too, but for the Composer prompt in SEED. (Nav-links example for stores+cms+ecom+gift-cards: `[{"href":"/about","label":"About"},{"href":"/faq","label":"FAQ"}]` — `/about` + `/faq` when `cms` is loaded; never `/products` (stores splices it), `/gift-cards` (disabled), or any route whose pack contributes a nav marker.)

The orchestrator dispatches the Designer with these inputs **post-approval** (`BUILD.md` run-step 0) — not during Discovery; the Designer's prompt template lives in `DESIGN_SYSTEM.md`. Discovery only produces and holds the inputs in scratch.

---

## Step 3 — Present the Plan

**Send the rendered plan as its own assistant message FIRST** — the full formatted markdown (Sections A/B/C + Imagery line) that the user reads. **Only then, as a separate step, use `AskUserQuestion` for approval.** Never bundle the plan into the approval question, never replace it with a one-line "here's the plan", and never skip straight to "Ready to build?" — the user must see the rendered plan before the question. (This is the only thing between Q&A and approval; there is nothing else to do here — see `PLAN.md` § "Wave 0".)

> **Do NOT show implementation details.** Users do not want to read about scaffolding, `npm install`, `env pull`, API calls, phase agents, designer handoffs, sidecars, or build/preview steps. They care about their site. The TaskList conveys progress; the plan conveys outcome. Never open with SDK packages or CMS collection fields.

The plan is composed from the loaded vertical packs. Each pack contributes: pages and features blurbs. The skill assembles; the packs supply. **Apps, packages, and CMS collection names are implementation details** — not surfaced in the plan; the loaded verticals determine apps to install and the seeder names CMS collections at run time.

### Plan structure (in order)

The plan has TWO halves: a short **decision card** (Sections A + B — what the user actually weighs in on) and a tighter **technical scope** block (Section C + Imagery line — what comes "for free" from the loaded packs). The user reads A and B carefully; C is reference material they skim or skip.

> **Section C is a markdown table.** It leads with the exact header skeleton — copy it verbatim. Do NOT type column headers from memory: that's the root cause of every plan-format regression.

**Section A: Design Direction** — Lead with this. Open with the aesthetic paragraph crafted in Step 2, then a compact detail block:
- Aesthetic tone (e.g., "organic editorial")
- Color palette (2–3 dominant colors with hex codes)
- Typography pairing (display + body)
- Mood and key visual elements
- Page color strategy: Uniform Light / Uniform Dark / Defined Hybrid

**Section B: Features** — 1–2 line descriptions of user-facing functionality from each pack. Bullet list is correct here. Explain what the user's visitors will be able to do. Tag CMS-powered features with **(CMS-based)** so the user knows which content they can edit from the dashboard.

**Skip features from packs with `disabled: true`** (today: only `gift-cards`). Its surfaces are inactive by default — they light up only when the user enables the matching Wix app from the dashboard. The plan must not promise a feature that isn't active out of the box. The code still ships (the `/gift-cards` page file is created plus the nav/home contributions) so activation is instant once the user opts in — but the plan stays silent until then. Packs without `disabled: true` (including transitive ones like ecom) contribute their features normally.

→ **Verify B:** No bullet derives from a `disabled: true` pack. Today: no "Gift cards" bullet, no "(when enabled)" / "(auto)" markers anywhere in B.

> **Visual separator before the technical scope.** After Section B, emit a `---` rule and a single line: *"Technical scope below — auto-decided from the features above. Skim if you want; not required reading."* This signals to the user that the decision is essentially made and the rest is reference material. Without the cue, users feel obligated to read every table cell before approving and stall the build for tens of minutes.

---

**Section C: Pages.** Emit exactly this header, then one row per loaded pack's `routes:` entry:

```
| Page | Route | Source |
|------|-------|--------|
```

> **STOP if you typed anything else.** `| Route | Purpose |` (drops Source), `| Page | Route |` (no Source), bullet list `- **Cart** (/cart)`, or Source merged into Route (`/cart (Stores)`) — each is a known regression. **Three columns, exact names, in that order.** Re-read the skeleton above before typing rows; do not type column headers from memory.

**Compose rows from each loaded pack's `routes:` array.** Do not hardcode rows; do not omit declared rows; do not invent rows. For every loaded pack (top-level OR transitive via `requires:`), iterate its `routes:` array.

**Skip rule.** Skip every route from any pack with `disabled: true`. Today that's only `gift-cards` — its `/gift-cards` row does NOT appear in the plan. The page file still ships so the runtime probe lights up the surface the moment the user enables the Wix Gift Card app from the dashboard, but the plan must not promise a surface the user did not ask for. Surfacing it with a `Source: "Wix Stores (auto)"` marker has been tried and rejected — users push back ("Giftcard shouldn't appear unless the user asked for it").

Each surviving entry → one table row:

```
Page name (Page cell):
  - Use the entry's `name:` field if present (override).
  - Else derive from the route path:
      "/"               → "Home"
      "/<seg>/[slug]"   → title-case(seg, singular) + " Detail"
      otherwise         → title-case the last static segment, replacing
                          "-" with space  ("/thank-you" → "Thank You")

Route cell:
  - The entry's `route:` value verbatim (e.g. "/cart" — or the literal
    string "Hosted by Wix" for Wix-hosted endpoints with no path).

Source cell:
  - For top-level packs with non-empty `apps:`, use apps[0].name
    (e.g. "Wix Stores", "Wix Blog").
  - For transitive packs (loaded via another pack's `requires:`),
    walk up the requires chain to the top-level puller and use ITS
    apps[0].name. So ecom's "/cart" shows Source: "Wix Stores"
    (because stores requires ecom and the user opted into "selling
    things", not into "an ecommerce SDK").
  - For the `cms` pack, use the literal "CMS (builtin)".
  - No suffixes (no "(auto)", no "(passive)", etc.) — disabled packs
    don't contribute rows at all.
```

**Order rows by user-facing flow:** CMS pages first (Home, About, FAQ), then catalog/content pages, then transactional pages (cart, thank-you, checkout). Within a pack, preserve declaration order from the pack's `routes:` array.

→ **Verify C:** Header is exactly `| Page | Route | Source |`. Row count = sum of `routes:` entries across all loaded packs that are NOT `disabled: true`. Every Route is either a `/`-prefixed path matching the slugified Page name OR the literal `Hosted by Wix`. No "(auto)"/"(passive)" suffixes anywhere. No "Gift Cards" row when gift-cards loads transitively.

---

**Imagery line.** A single line below Section C, not a table:

```
**Imagery:** Themed blocks
```

…or `**Imagery:** AI-generated (~<estimatedCredits> Wix AI credits)` when Q3 captured `ai-generated`, with `<estimatedCredits>` replaced by the integer computed in Step 2.5 § 2.5.1. Copy the imagery value from the captured preference; the credit count is the same number shown to the user at Q3. **Do not** repeat the current balance here — it was already shown at Q3, and re-printing it in Section C clutters the reference table the user skims.

→ **Verify Imagery:** Exactly one line. If themed: value is `Themed blocks`. If AI-generated: value matches `^AI-generated \(~\d+ Wix AI credits\)$`. No second line, no table, no other commentary.

### Example (skincare ecommerce brand)

```markdown
Here's my plan for **Bloom & Root**:

## Design Direction

For Bloom & Root, I'm going with **clean luxury with organic warmth** —
think a curated boutique where every product feels considered. Warm cream
backgrounds paired with deep charcoal text and rose gold accents. Cormorant
Garamond headlines bring editorial gravity; DM Sans keeps the body text
tactile and approachable.

- **Colors:** Warm cream (#FFF8F0), deep charcoal (#1A1A1A), rose gold (#B76E79)
- **Fonts:** Cormorant Garamond (headings) + DM Sans (body)
- **Mood:** Premium, approachable, tactile
- **Color strategy:** Uniform Light

## Features

- **Product catalog** — Browse all products with images, prices, and variants.
- **Cart & checkout** — Add to cart, review, check out via Wix's hosted checkout.
- **About (CMS-based)** — Brand story, editable from the Wix dashboard.
- **FAQ (CMS-based)** — Q&A about products, editable from the dashboard.

---

*Technical scope below — auto-decided from the features above. Skim if you want; not required reading.*

## Pages (8)

| Page           | Route             | Source        |
|----------------|-------------------|---------------|
| Home           | /                 | CMS (builtin) |
| About          | /about            | CMS (builtin) |
| FAQ            | /faq              | CMS (builtin) |
| Products       | /products         | Wix Stores    |
| Product Detail | /products/[slug]  | Wix Stores    |
| Cart           | /cart             | Wix Stores    |
| Thank You      | /thank-you        | Wix Stores    |
| Checkout       | Hosted by Wix     | Wix Stores    |

**Imagery:** Themed blocks

Should I proceed?
```

The Cart, Thank You, and Checkout rows show `Source: Wix Stores` — not "Wix eCommerce" — because ecom is loaded transitively via stores's `requires:` and the orchestrator walks up the chain. The user opted into "selling things", not into "an ecommerce SDK".

### Final scan (MANDATORY)

Before sending the plan, confirm each inline → Verify above (B, C, Imagery) passed. If any failed, regenerate that section and re-scan before emitting. Plans that violate multiple inline checks at once cost a full plan replay (~25 min of user time) when caught post-hoc. The inline → Verify lines exist to catch them before sending.

### Approval

Use `AskUserQuestion`: *"Ready to build?"* Options: **Yes, build it** / **Adjust something**.

If the user wants to adjust, handle it conversationally (swap brand, change vibe, add/remove a page). Re-present the plan and re-ask for approval.

---

## After Approval — capture intent in scratch and write `.wix/site.json`

On the user's "Yes, build it" approval, hold the captured intent in orchestrator session scratch and write a slim `.wix/site.json` metadata snapshot. The transition into Setup — and what Setup synchronizes on — is FLOW, owned by `PLAN.md` (which hands off to `BUILD.md` on approval).

### 1 · Compose the intent block in session scratch

In session scratch, build a single JSON object carrying the captured imagery flag plus per-vertical hints inferred from the user's prompt. Only include blocks for verticals that were loaded. This stays in orchestrator memory for the rest of the run — it is **not** written to disk. Seeders receive the relevant `intent.<pack>` slice inlined in their prompts (see `SEED.md` Step 2).

```json
{
  "imagery": "themed-blocks",
  "stores":     { "productCount": 3, "categoriesNamed": ["..."] },
  "cms":        { "collections": [{ "purpose": "about", "itemCount": 1 }] },
  "blog":       { "postCount": 6, "topics": ["..."] },
  "forms":      { "forms": [{ "purpose": "contact", "fields": ["..."] }] },
  "gift-cards": { "enabled": true }
}
```

Inference guidelines for each block:
- **`imagery`** — exactly the value captured at Step 2.5. If the user picked `"ai-generated"`, still pass `"ai-generated"` here; the AI-imagery fallback messaging happens in the user-facing summary, not in the captured intent.
- **`stores.productCount`** — number of products the user implied (e.g. *"a few candles"* → 3, *"a full catalog"* → 8). When unclear, default to 3.
- **`stores.categoriesNamed`** — strings the user explicitly named (*"a section for soaps and one for candles"* → `["Soaps", "Candles"]`). Empty array if none named.
- **`cms.collections`** — one entry per CMS-driven page: at minimum `{purpose: "about"}` and `{purpose: "faq"}` for any cms-loaded run. `itemCount` only when the user implied a number (*"a 5-question FAQ"* → `itemCount: 5`).
- **`blog.postCount`** — count the user implied; default to 6 when unclear. **`topics`** are explicit-only.
- **`forms.forms`** — one per form the user described; `purpose` is one of `contact`, `signup`, `lead`, etc.; `fields` are explicit only.
- **`gift-cards.enabled`** — `true` when the user explicitly asked for gift cards; `false` (or omit the block) otherwise.

When in doubt, omit a field rather than fabricate. The downstream phases that consume this block aren't built yet — overconfident inference can't be verified until then.

### 2 · Write the slim `.wix/site.json` snapshot

```bash
mkdir -p .wix
node "<SKILL_ROOT>/scripts/init-site-json.mjs" \
    "$(pwd)" "<brand name>" "<one-line aesthetic from Q2>" "<verticals-csv>" \
    --frontend "<frontend>"
```

- `<frontend>` is the value captured in Wave 0 — `astro` on the supported path (the only path that reaches this step; custom frontends are routed to the stub before approval and never write `.wix/site.json`). Always pass it explicitly so the recorded JSON is unambiguous.
- `<verticals-csv>` is the comma-joined list of all loaded packs (top-level + transitive via `requires:`). For a stores+cms run this is `"stores,ecom,cms,gift-cards"`.
- `<one-line aesthetic from Q2>` is the short aesthetic tone phrase, not the full 2–3 sentence direction.
- The script writes a slim `.wix/site.json` containing only `{brand, frontend, verticals}` (plus `siteId` / `appId` once Setup patches them in). It refuses to overwrite an existing file. If a stale site.json is present from a prior run, surface that to the user before retrying — do NOT silently `rm` it.
- The intent block from § 1 is **not** passed to the script — it lives in orchestrator scratch and feeds seeder prompts directly.
- **Trust the script's response.** A `{"status": "ok", "path": "..."}` return is the contract — do **not** follow up with a defensive `ls` + `Read` against `.wix/site.json` to confirm. Re-reading costs ~3s and adds nothing.

Once `init-site-json.mjs` returns `{"status": "ok"}`, Discovery's domain work is complete. The transition into Setup and the rest of the run is owned by `PLAN.md` (which hands off to `BUILD.md` on approval).
