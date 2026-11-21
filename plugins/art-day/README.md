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

## Cross-client direction and review request

This is not a claim of universal compatibility or directory approval. A remote HTTPS MCP transport, user authentication and isolated per-user storage would be needed for web/cloud clients. The current local database must not be shared between remote users. An MCP Apps UI can be reused by compatible hosts, but a sidebar thumbnail is a host-specific enhancement.

We request maintainer feedback on whether this local plugin belongs in this examples/catalog repository and the appropriate review path. We understand that public local-MCP directory submission requires partner eligibility/organization allowlisting and is separate from a GitHub PR. No hosted endpoint, privacy/terms website or remote service is claimed by this proposal.

MIT licensed. Source, lockfile, tests and bundled runtime are included. No API keys or personal ratings are included.
