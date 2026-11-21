# Art Day

Discover a daily museum painting from Wikimedia Commons, read its story, rate it, and build a personal collection and taste profile.

## Current support

This proposal is a **desktop-only local MCP plugin**, requiring Node.js 22.13+ on PATH. It has no BB or Claude runtime dependency. Runtime dependencies are bundled in dist; installation does not require npm install.

The optional MCP Apps gallery provides Today, Favorites and My taste views, 1–5 stars, five preference chips, image download and Commons attribution. The gallery follows the host locale: Russian for ru-* and English otherwise. Painting translations are stored separately from identity and preferences. Sidebar entrypoints and remote thumbnail rendering depend on host support; pinning may be required.

The Codex agent researches Commons, verifies attribution and public-domain/CC0 eligibility, inspects the image, and publishes a local daily edition. Selection uses an explainable heuristic: 80% taste-weighted selection by artist/tags, 20% exploration. Explicit preference chips are available to candidate research and displayed as counts, not used as numerical selection weights.

Daily automation is **optional and must be configured separately by each user**. Installing this package does not create an automation. A suggested schedule is 09:00 Europe/Paris, with freshness checks at 10:00 and 12:00. Local execution must be available. Without automation, request a painting manually.

## Data and permissions

Data stays in ~/.local/share/art-day-codex/art-day.sqlite (override ART_DAY_DATA_DIR). No account, telemetry, publisher service or private user database is included. The plugin fetches Commons images; the host agent uses its own research tools. Tool results are processed under the host's data policy. Ratings, favorites and explicit trait choices are independent. Full current/favorite cards are retained; older non-favorite images are compacted. art_export provides local history and preferences on request.

## Validation

From this directory: `npm ci --ignore-scripts`, `npm run build`, `npm test`.

16 automated tests cover storage, partial updates, trait counts, RU/EN translations, selection, source restrictions, redirects, image validation, bundled MCP launch, UI script syntax and gallery metadata. An isolated browser host was used to verify rating, favorites, preference chips and the taste view. Native Codex sidebar access was confirmed by the user, not automated GUI verification. Native-host downloads and a full unattended daily automation cycle remain unverified.

## Local architecture and review request

The intended architecture is local execution on each user's computer. We distribute the source and bundled runtime; the user's plugin downloads images directly from Wikimedia Commons and stores artwork data, ratings, favorites and the taste profile locally. No Art Day account, publisher-hosted MCP endpoint, shared database or publisher-operated backend is required or planned for this proposal.

The MCP server is a local stdio process launched by the user's desktop client. Research and story preparation use the user's Codex agent and available tools; this does not mean Codex itself is offline. Daily automation is configured in the user's environment. Web/mobile execution and universal sidebar support are outside this submission's scope.

We request review as a self-contained local desktop plugin and guidance on the appropriate directory submission route. We understand that local-MCP public-directory submission requires partner eligibility/organization allowlisting and is separate from a GitHub PR. No migration to a publisher-hosted service is proposed.

MIT licensed. Source, lockfile, tests and bundled runtime are included. No API keys or personal ratings are included.
