# Biological Sequence & Alignment Viewer

Biological Sequence & Alignment Viewer opens sequence and multiple-sequence-alignment files in an interactive rich view directly inside Codex.

## Open A Sequence Or Alignment

- Click a supported file in the Codex workspace tree to open the native rich preview.
- Ask Codex to open a supported local sequence or alignment to render the viewer inline in chat.
- Use **Open in side pane** inside the viewer to move the same live view to the right pane.
- Use **Return to chat** to move it back without losing mode, focus, selection, or alignment state.

## Supported Files

- FASTA and plain biological sequence: `.fasta`, `.fa`, `.fas`, `.fna`, `.faa`, `.ffn`, `.frn`, `.mfa`
- Explicit aligned FASTA: `.aln-fasta`, `.afa`, `.afasta`
- GenBank and RefSeq flat files: `.gb`, `.gbk`, `.genbank`, `.gbff`
- EMBL and ENA flat files: `.embl`, `.emb`
- FASTQ: `.fastq`, `.fq`
- Common alignment formats: CLUSTAL, Stockholm, A2M, A3M, MSF, PHYLIP, NEXUS, and PIR

The read-only viewer supports sequence and alignment modes, annotations, FASTQ quality, motif search, selections, consensus and conservation metrics, and model context for follow-up questions about the current view.

## Data Handling

The plugin runs a local MCP server. Native workspace opens use Codex host-managed resource handles. Chat opens expose an opaque local plugin resource through standard MCP `resources/read`.

File contents are sent to the embedded viewer, not returned to the model as tool output merely to open the file. The plugin does not impose its own file-size cap; Codex host behavior and normal local memory constraints still apply. When the MCP host supplies active workspace roots, chat opens are confined to those roots.

## Marketplace Package

This package is a generated, self-contained runtime bundle for the Codex official plugin marketplace. It includes the manifest, local MCP server runtime, viewer assets, agent guidance, and small synthetic smoke fixtures needed to validate supported formats.

## License

OpenAI-authored files are available under the [MIT License](LICENSE). Bundled third-party dependencies and their available license or notice texts are listed in `THIRD_PARTY_NOTICES.md`, which is included in the generated marketplace bundle.
