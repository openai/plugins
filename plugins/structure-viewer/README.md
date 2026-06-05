# Molecular Structure Viewer

Molecular Structure Viewer opens molecular coordinate and ligand files in an interactive Mol* view directly inside Codex.

## Open A Structure

- Click a supported file in the Codex workspace tree to open the native rich preview.
- Ask Codex to open a supported local structure to render the viewer inline in chat.
- Use **Open in side pane** inside the viewer to move the same live view to the right pane.
- Use **Return to chat** to move it back without losing camera, representation, focus, or selection state.

## Supported Files

- PDB text coordinates: `.pdb`
- CIF and mmCIF coordinates: `.cif`, `.mmcif`
- MDL MOL small-molecule records: `.mol`

The read-only viewer supports Mol* representations and coloring, ligand focus, residue hover and selection, and model context for follow-up questions about the current view.

## Data Handling

The plugin runs a local MCP server. Native workspace opens use Codex host-managed resource handles. Chat opens expose an opaque local plugin resource through standard MCP `resources/read`.

File contents are sent to the embedded viewer, not returned to the model as tool output merely to open the file. The plugin does not impose its own file-size cap; Codex host behavior and normal local memory constraints still apply. When the MCP host supplies active workspace roots, chat opens are confined to those roots.

## Marketplace Package

This package is a generated, self-contained runtime bundle for the Codex official plugin marketplace. It includes the manifest, local MCP server runtime, viewer assets, agent guidance, and small synthetic smoke fixtures needed to validate supported formats.

## License

OpenAI-authored files are available under the [MIT License](LICENSE). Bundled third-party dependencies and their available license or notice texts are listed in `THIRD_PARTY_NOTICES.md`, which is included in the generated marketplace bundle.
