# ctxd

Open-source context infrastructure between agents and data. The local tracker synchronizes source content into ctxfs. This plugin lets Codex inspect paths and read that content through Model Context Protocol (MCP).

## Set up a source

On a Linux workstation as your normal user, install Python 3.11 or 3.12, `uv` and the system `ps` command. In your Python environment:

```bash
pip install ctxd
ctxd backend set ctxfs
ctxd folders add /path/to/your/source --name Source
python -m ctxd.tracker_service sync-once
ctxd tracker start
```

Replace `/path/to/your/source` with a folder you want Codex to read. Start Codex under the same operating-system account. The plugin launches the local bridge with `uvx --python 3.12 --from ctxd ctxd-mcp`; no ctxd hosted account or API key is required.

## Use the source

- Start with `tree` or `glob` to find a source path.
- Pass the returned path to `read` or `read_lines`. `ls` and `stat` also work.
- Edit a source file, wait for synchronization, then read the same path again.
- Remove the source file and verify that `glob` no longer returns it.

The included skill explains bounded reads, synchronization checks and setup. Python and the CLI provide exact text search. In ctxd 0.1.16, the MCP bridge advertises `grep`, but that tool fails because `CtxfsFiles.grep` is missing; use the CLI for exact text search.

Source content remains in the local ctxfs store until the client reads it. Codex can send retrieved content to its model provider. Track only sources you intend to share with that client. This setup uses the operating-system account boundary and is not a separate security sandbox.

[Get started](https://ctxd.dev/_ucf/) · [Source and stars](https://github.com/ctxd-dev/ctxd) · [Privacy](https://github.com/ctxddev/ctxd-agent-plugin/blob/main/PRIVACY.md)

Support: [hi@ctxd.dev](mailto:hi@ctxd.dev).
