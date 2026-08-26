# Mobile And Device QA

Use this before finalizing a dashboard or changing shared layout assets.

## Required Checks

- Dashboard must remain readable at desktop, tablet, and phone widths.
- Tables must not require precision horizontal scrolling on phones. The shared CSS converts table rows into key/value cards below 700px.
- Touch targets for tabs and buttons should be at least 44px high.
- Sticky table-of-contents links in `single_page` layout should also be at least 44px high and horizontally scrollable on phones.
- Do not rely on hover-only controls.
- Citation chips must also work on keyboard focus and click/tap. Hover previews are additive; click should jump to the source ledger or open the source URL.
- Do not use remote fonts, remote logo fetches, or remote JavaScript for local dashboards.
- Generic issuer identity tiles must work when no logo exists.
- Text should wrap before shrinking. Do not use viewport-width font sizing for dashboard body text.
- Source and missing-evidence modules must remain visible on mobile.
- Inline citation chips, numeric citation links, section source notes, and source IDs must wrap without causing horizontal overflow.
- Single-page dashboards must keep all sections in the DOM; navigation should jump to anchors rather than hiding content.
- The dashboard should open from `file://` without a dev server.

## Smoke Commands

```bash
python skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py payload.json --profile production
python skills/public-equity-investing/internal-support/dashboard-builder/scripts/render_dashboard.py payload.json output/index.html --profile production
python -m py_compile shared/dashboard/*.py skills/public-equity-investing/internal-support/dashboard-builder/scripts/*.py
```

Then scan the rendered HTML for unresolved authoring text:

```bash
rg -n "TODO|FIXME|PLACEHOLDER|\\[TOKEN\\]|undefined" output/index.html
```
