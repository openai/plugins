# jubarte Plugin

This plugin packages [jubarte](https://github.com/jandira-tech/jubarte), an open-source
(Apache-2.0) Word engine, in `plugins/jubarte`.

It includes one skill, `jubarte-documents`, and one local MCP server, `jubarte`.

## What it does

- Reads a `.docx` into paragraphs with ids, tracked changes and comments.
- Applies exact edits as Word tracked changes with comments. A plan whose anchor is
  missing or ambiguous is refused and nothing is written.
- Compares two versions into a redline, and accepts or rejects changes by id, author
  or kind.
- Checks that Word will open the result.
- Renders pages to PNG and PDF with its own layout engine, including a chosen set of
  pages. No LibreOffice or Poppler.

## Requirements

[`uv`](https://docs.astral.sh/uv/). The server starts with
`uvx --from 'jubarte-docx[mcp]==0.19.0' jubarte-mcp --root .` and downloads the
`jubarte-docx` wheel from PyPI on first use. It speaks stdio, opens no network port,
and reads and writes only under the folder it was started in.

## Measured

On Crosby's RedlineBench (134 tasks) and the redline tasks of Harvey's Legal Agent
Benchmark (90 pairs), agents given jubarte scored the same as agents given each
benchmark's own document tools and used fewer tokens and less time. Report and data:
<https://github.com/arthrod/redline-reports>.

## Support

Issues: <https://github.com/jandira-tech/jubarte/issues>
