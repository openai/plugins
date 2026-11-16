# Curated font resources

Use this catalog when selecting a face and existing brand/template/reference resources leave the choice open. Preserve accepted identity and actual reference lettering. The catalog covers 40 families spanning Simplified/Traditional Chinese, Japanese, Korean, Arabic/Persian, Devanagari and Latin roles; suitability tags are editorial suggestions, not a claim of improved design quality.

## Read candidates, not the whole library

1. Read `openmotion://fonts/index` with MCP resources/read. Filter by actual language and text role; inspect only plausible candidates through the returned `openmotion://fonts/<id>` URIs. The `motion://` resource alias is also accepted.
2. A family detail includes `brandFit` (construction traits, suitable conditions and mismatch risks), `readability` (reading role, phone-size risks and adjustments), conditional `pairings`, spacing/locale guidance and pinned file metadata: actual family, weight/style, variable axes, sample glyph coverage, source revision, sizes, SHA-256 and license. Compare candidates with the actual identity and words; suitability is editorial guidance, not a measured legibility score or a substitute for the [phone-size review](typography.md#compose-with-the-real-words).
   A pairing names a possible partner and its role, `when` and `avoidWhen`. One family may be sufficient. Pairing entries are neither required combinations, automatic fallback chains nor permission to replace a brand face. The glyph sample does not establish coverage of every character or regional form.
3. Skill-only clients can read the authoritative JSON at `../fonts/catalog.json` relative to this reference. Use host JSON filtering to select entries rather than loading every detail into the conversation. The compact index is a projection of that same data, not another catalog to maintain.

For script-sensitive comparisons, set the specimen role’s optional `lang` (for example `ja`, `zh-Hant`, `ar` or `hi`) and `direction` (`ltr`, `rtl` or `auto`). Use `rtl` for Arabic/Persian and inspect joining, punctuation and mixed-script order. Japanese/Traditional Han coverage does not establish Simplified Chinese regional fidelity.

## Prepare only the selected resource

The detail's `prepare.command` is an argument array for the installed runtime's `scripts/prepare-font.ts`. Run it through the host's execution capability. It downloads the chosen font at a fixed upstream commit and checks byte size and SHA-256, including the license. It writes only to the user's `~/.cache/openmotion/fonts/<source-commit>/<id>/` cache, and verifies cached bytes before reuse. It does not modify any project or download the other families.

Pass the family ID as a positional argument: `node --experimental-strip-types <runtime>/scripts/prepare-font.ts <id> [--weight 400]`. Use the returned command with the real runtime path rather than inventing flags. The default is 400 when available, otherwise the first available upright weight. Append `--weight <actual-weight>` to select another available upright face. A variable file may cover several weights; a missing weight fails explicitly. The catalog does not currently prepare italic resources. Skill-only installations locate the runtime through their existing `openmotion-install.json` or adapter `scope.json`; do not guess it from the current video directory.

Full font binaries are not inside the Skill or the application package. The small catalog and preparation script ship with the runtime; first use of a selected face requires access to its pinned upstream URL. Cached fonts work offline. A failed preparation is not a completed import; choose another suitable available resource or report the dependency.

## Compare prepared faces with actual copy

For a consequential open choice or a complaint about font character, use a representative actual phrase from the affected role. The optional offline helper builds a portable side-by-side specimen before importing fonts into a project:

```sh
node --experimental-strip-types <runtime>/scripts/font-specimen.ts <request.json> <new-output-directory>
```

Source installations resolve the parser from their installed dependencies. For an extracted plugin whose dependencies live separately, append `--runtime-root <existing-locked-runtime>`: the directory containing the `node_modules` used by `hyperframesCli` in project details. This selects an already installed parser; it does not install dependencies or acquire fonts.

Supply JSON in this shape, replacing the example copy, dimensions, roles and candidates with this task's inputs. `sourcePath` is a selected `files[].sourcePath` from preparation; `licensePath` is the same preparation's returned path. All resource paths must be absolute. Prepare each candidate at the role's weight first.

```json
{
  "title": "Opening claim: compare character",
  "sourceWidth": 1920,
  "displayWidth": 360,
  "roles": [{
    "name": "Opening claim — direct invitation",
    "text": "Actual supplied words\n真实文案",
    "fontSize": 180,
    "weight": 400,
    "width": 1600,
    "lineHeight": 1.1,
    "letterSpacing": 0,
    "candidates": [{
      "label": "Candidate A: Latin + deliberate CJK",
      "faces": [
        {"id": "ibmplexsans", "sourcePath": "/absolute/prepared-latin.ttf", "licensePath": "/absolute/latin-OFL.txt"},
        {"id": "notosanssc", "sourcePath": "/absolute/prepared-cjk.ttf", "licensePath": "/absolute/cjk-OFL.txt"}
      ]
    }]
  }]
}
```

Add the other candidates to the same role; their size, weight, width, line height and tracking stay equal. `fontSize`, `width` and `letterSpacing` are authored pixels, scaled by `displayWidth / sourceWidth`; `lineHeight` is a multiplier. `faces` gives the intended CSS family order, so put the Latin face before its CJK partner when comparing that relationship. Choose language-specific faces and inspect regional forms. This example is an input schema, not a recommended pairing or title scale.

The helper reads only supplied files, verifies font and license hashes against the catalog, and writes `index.html`, `specimen.json` and copied assets/licenses into a new output directory. It never fetches, installs fonts or changes a project. The parent directory must exist; existing output is refused. Missing preparation or an unavailable weight fails rather than synthesizing a face.

Open `index.html` with a host browser, wait for its supplied-font load status, then inspect actual glyphs and candidate differences at the stated display size. `specimen.json` records exact copy, conditions, pinned resources and codepoints missing from the supplied stack. Coverage and load status do not establish shaping, which face rendered each glyph, readability or fit. Use host rendered-font evidence where available; retain uncertainty about substitution. Record the useful visible distinction in the existing creative/review record, then validate the chosen treatment in the actual frame and playback window as described in [Typography](typography.md).

## Use the normal project write boundary

For managed projects, pass the returned `importItems` to `openmotion_import_assets` with the explicit projectId and a fresh requestId. Keep itemIds for retries. The Tool parses real font bytes, copies the optional license into the same version and returns actual metadata and project-relative `fontFaceCss`. Font-only imports do not require FFmpeg. This does not place text or edit a composition.

Read the project's new revision/version, then save the needed @font-face and text styling through `openmotion_edit_project`. Returned CSS paths are relative to the project root; adjust relative URLs when authoring a stylesheet in a nested folder. Follow [Typography](typography.md) for real-copy, mixed-language and rendered-face checks.

For independent portable projects, copy the selected prepared font and license through host file capabilities and use project-relative references. Full CJK resources preserve subsequent copy editing; these are not subsets restricted to the current sentence. Distributable packages retain the applicable license. Font import and technical readiness do not establish aesthetic acceptance.
