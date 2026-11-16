# OpenMotion

Create, recreate and edit motion videos with an editable project that stays in
OpenMotion Studio. These skills guide the local agent through planning,
composition, revision, preview and export.

## Included workflows

| Skill | Use it for |
| --- | --- |
| `openmotion-director` | Original motion videos, creative planning and changes to motion, narrative or sound. |
| `openmotion-production` | Scoped edits, preview, troubleshooting and export of existing projects. |
| `openmotion-recreate` | Rebuilding a motion-graphics reference as an editable project. |
| `openmotion-template-to-video` | Opening or adapting an existing editable template. |
| `openmotion-video-to-template` | Turning a reference video into a reusable editable template. |
| `openmotion-media` | Supporting image, video, speech and music asset generation through configured providers. |

References, font metadata and workflow helper scripts are included alongside the
skills. Reference recreation currently covers motion graphics; it does not
promise recreation of live action or talking heads.

## Requirements and connection

This is a desktop skills companion. It does not contain or register the
OpenMotion application, an MCP server, npm dependencies or native executables.
Planning can work without a runtime; project creation, editing, preview, media
generation and export require a separately installed OpenMotion runtime whose
local MCP connection is available in the current chat.

1. Reuse an existing OpenMotion installation and its workspace. If none exists,
   follow the maintained [source installation guide](https://github.com/nexu-io/openmotion/blob/main/install.md).
   The source guide specifies the Node.js version, dependencies and build steps.
   Published npm installation is a separate, explicit choice described in the
   [application installation guide](https://github.com/nexu-io/openmotion/blob/main/docs/install.md).
2. Connect that installation using its Studio **MCP · Connect Agent** page or the
   [host adapter guide](https://github.com/nexu-io/openmotion/blob/main/docs/agent-adapters.md).
   Preserve existing projects, credentials and unrelated host configuration.
3. Discover the connected `openmotion_` tools and perform a read with
   `openmotion_get_project` to check the intended workspace. A CLI registration
   or independent probe does not establish that the current chat has connected.
4. Continue through the skill for the user's task. Report connection problems
   before attempting project changes. New capabilities in these skills may
   require a runtime update; do not silently replace an existing installation.

Use the actual registered launch configuration or the installation's
`openmotion-install.json` / `scope.json` to locate its runtime and shared `docs/`.
The runtime is separate from this plugin directory. Run helpers that require the
runtime, such as `vision-tools.mjs`, from that installation's matching `skills/`
directory. Do not assume a runtime exists above this plugin cache. The standalone
delivery helper also accepts the documented `--runtime-root` argument. Keep
machine-specific paths and installation metadata out of the distributed package.

Preview and export need the installation's working browser and FFmpeg/ffprobe.
The optional managed vision helpers support macOS 13+ arm64 and Windows 11+ x64;
follow the installed runtime's platform and download requirements. Generated
media needs a configured provider or an authorized account and may incur costs.
Never place provider credentials in this package or ask users to paste them into
chat. Installation does not authorize project creation, export or paid model calls.

## Source and maintenance

The maintained source is [nexu-io/openmotion](https://github.com/nexu-io/openmotion).
This directory mirrors the five creative workflows and their media support from
`main` at commit
[`4fdf2c32905d2e3cb2f579d16dfbcf6fdf010845`](https://github.com/nexu-io/openmotion/tree/4fdf2c32905d2e3cb2f579d16dfbcf6fdf010845).
All 51 files under `skills/` are byte-for-byte copies of that snapshot;
[source.json](source.json) records their SHA-256 hashes. The directory-specific
manifest and this README describe the skills-companion distribution.

The plugin version follows that source snapshot's `0.0.1` version. It is not a
claim that the existing ChatGPT directory package has been upgraded or replaced.
The existing [OpenMotion ChatGPT plugin](https://chatgpt.com/plugins/plugins_6a742d13e88481919b42002864b1bb26)
is maintained separately; this repository contribution does not publish changes
to that listing or automatically associate the two plugin identities.

For updates, copy the same supported skill directories and all their referenced
files from a reviewed source commit, refresh `source.json`, and verify links,
host discovery and the relevant runtime requirements. Report workflow issues to
[the source repository](https://github.com/nexu-io/openmotion/issues).

## Acknowledgements

OpenMotion text and helper code are distributed under [Apache-2.0](LICENSE).
The unmodified OpenDesign symbol and its theme variants come from OpenMotion's
maintained brand assets; see [asset provenance](assets/NOTICE.md).
The font catalog contains metadata and download/license references, not font
binaries. Upstream and external resources retain their respective licenses and
attribution.
