#!/usr/bin/env python3
"""Template rendering.

Templates use bracket tokens like `[TICKER]`.
This keeps things simple and avoids external dependencies.
"""

from __future__ import annotations

import re
from pathlib import Path

TOKEN_RE = re.compile(r"\[(?P<token>[A-Z0-9_]+)\]")


def render_text(template_text: str, mapping: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        tok = m.group("token")
        return str(mapping.get(tok, m.group(0)))

    return TOKEN_RE.sub(repl, template_text)


def render_file(template_path: Path, mapping: dict[str, str]) -> str:
    text = Path(template_path).read_text(encoding="utf-8")
    return render_text(text, mapping)


def write_rendered(template_path: Path, mapping: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_file(template_path, mapping), encoding="utf-8")
