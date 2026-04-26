# Step 7: Validate & Deliver

## Lint + Validate

Run in sequence. Fix all errors before proceeding to the next command.

```bash
npx hyperframes lint
npx hyperframes validate
```

`lint` checks HTML structure statically — missing attributes, timeline registration, tween conflicts, CSS transform + GSAP conflicts (including inline styles).
`validate` loads the composition in headless Chrome and catches runtime JS errors, missing assets, and failed network requests.

## Visual Verification (snapshot)

After lint and validate pass, capture snapshot frames to SEE your own output. **Always use `hyperframes snapshot`** — do not roll your own ffmpeg/headless Chrome script; the default naming (`frame-XX-at-Ys.png`) is expected by later tooling.

```bash
npx hyperframes snapshot <project-dir> --at <beat-midpoints>
```

If the snapshot command isn't available, fall back to:

```bash
npx tsx packages/cli/src/cli.ts snapshot <project-dir> --at <beat-midpoints>
```

Calculate the midpoint of each beat from your STORYBOARD.md timings. For a 4-beat video with beats at 0-5.8s, 5.8-15.0s, 15.0-22.5s, 22.5-25.3s:

```bash
npx hyperframes snapshot <project-dir> --at 2.9,10.4,18.7,23.9
```

This renders one frame per beat at the moment when content is most visible. Use timestamps where the most content is on screen — usually 60-70% into each beat, after entrances finish but before exits start. Output lands in `<project-dir>/snapshots/` with filenames like `frame-00-at-2.9s.png`.

**View every snapshot image carefully.** Don't glance and move on. For each frame, check:

**Visibility:**

- Is there visible content? All-white or all-black frames mean compositions aren't rendering.
- Can you read ALL text? White text on white/light background is invisible. Dark text on dark background is invisible. Every text element needs contrast against what's directly behind it.
- Are images and assets showing? Empty space where an image should be means a path issue or missing file.

**Positioning and layout:**

- Do background images fill the entire frame? If an image only covers half the screen, the `object-fit`, `width`, `height`, or position values are wrong.
- Are elements where the storyboard says they should be? Compare the snapshot to the beat description.
- Is there too much empty/dead space? If more than 40% of the frame is a flat solid color with nothing on it, the composition is sparse.
- Are elements overlapping incorrectly? Text over text, or content bleeding off the edges?

**Visual quality:**

- Are overlays too heavy? If a background image is barely visible through a dark overlay, reduce the overlay opacity.
- Is the visual hierarchy clear? One dominant element per frame, supporting elements secondary.
- Do the colors match DESIGN.md? Check actual rendered colors against what was planned.

**Code vs. rendered verification:**

- For each beat, check: does the snapshot show the assets you referenced in the HTML? If a composition has `<img src="...wave.png">` but the snapshot shows no wave — the image isn't loading, the path is wrong, or it's hidden behind another element.
- If a snapshot shows nothing at a timestamp, try a slightly different time (1-2 seconds later). Compositions may still be in entrance animations.
- The snapshot command is fast — run it multiple times at different timestamps if needed.

If any frame has issues, go back to Step 6 and fix that composition before proceeding.

## Preview

```bash
npx hyperframes preview
```

Open the studio in a browser. Scrub through every beat.

### Handoff URL

The Studio URL is the project handoff surface. In the final response, report the
active preview URL with the project hash:

```text
http://localhost:<port>/#project/<project-name>
```

Use the actual port selected by `hyperframes preview` and the project name shown
by the preview command. If you run `hyperframes preview --port 3017` for a
project directory named `codex-openai-video`, the project URL is:

```text
http://localhost:3017/#project/codex-openai-video
```

Do **not** present `index.html` as the project link. `index.html` is the source
file for agents and editors; the user-facing project is the running HyperFrames
Studio preview. You may include source file links as secondary context, but the
primary "Project" or "Preview" line must be the localhost Studio URL.

If a render was also requested, still include the Studio URL first so the user
can scrub and inspect the project. Include the MP4 path as the rendered output,
not as a replacement for the project URL.

## Render (on-demand only)

**Do NOT render automatically as part of the pipeline.** Preview is the delivery — the user scrubs, spots anything they want tweaked, and you iterate. Rendering to MP4 takes minutes of wall-clock time per pass and is wasted work if the user wants changes.

Only run `hyperframes render` when the user **explicitly asks** — e.g. "render it", "make the final", "export the MP4", "I'm happy, produce the file". Until then, stop at preview + snapshots.

When the user does ask to render, always pass `--output renders/<project-name>.mp4` so the final file has a predictable, human-readable name. The CLI default is timestamped (`<project>_YYYY-MM-DD_HH-MM-SS.mp4`) which is hard to reference from docs or later iterations.

```bash
npx hyperframes render --output renders/<project-name>.mp4
```

Example: `npx hyperframes render --output renders/stripe-launch.mp4`

For social-media vertical output, check `npx hyperframes render --help` for viewport/format flags.
