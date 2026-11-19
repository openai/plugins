#!/usr/bin/env python3
"""Consolidate duplicate personal skills that Cursor indexes from multiple roots.

Policy:
1. Prefer Cursor-managed ~/.cursor/skills-cursor over copies in ~/.agents/skills.
2. For ~/.agents vs ~/.claude overlaps, prefer ~/.claude/skills (Claude/TIA personal
   skills origin) and remove the ~/.agents duplicate so Cursor slash menu is unique.
3. Prefer installed Cursor plugin cache skills over junctions we created in ~/.agents/skills
   for the same skill name (remove the agents junction/copy).
4. Never delete ~/.cursor/skills-cursor or plugin cache contents.
5. Dry-run unless --apply is passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
AGENTS = HOME / ".agents" / "skills"
CLAUDE = HOME / ".claude" / "skills"
CURSOR_SKILLS = HOME / ".cursor" / "skills"
SKILLS_CURSOR = HOME / ".cursor" / "skills-cursor"
PLUGIN_CACHE = HOME / ".cursor" / "plugins" / "cache"
TRASH = CLAUDE / ".trash-dups"
AGENTS_TRASH = AGENTS / ".trash-dups"
REPORT = Path(r"E:\PyCharmProject\plugins\_skills_dedupe_report.md")


def skill_desc(skill_dir: Path) -> str:
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return ""
    text = md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return ""
    fm = m.group(1)
    dm = re.search(r'^description:\s*[>|]-?\s*\n((?:[ \t]+.+\n?)+)', fm, re.M)
    if dm:
        return " ".join(x.strip() for x in dm.group(1).splitlines() if x.strip())
    dm = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
    return dm.group(1).strip().strip("\"'") if dm else ""


def tree_hash(root: Path) -> str | None:
    if not root.exists():
        return None
    h = hashlib.md5()
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part.startswith(".trash") for part in p.parts):
            continue
        rel = str(p.relative_to(root)).replace("\\", "/").encode()
        h.update(rel)
        h.update(p.read_bytes())
    return h.hexdigest()


def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        # Windows junction: directory with FILE_ATTRIBUTE_REPARSE_POINT (0x400)
        attrs = path.lstat().st_file_attributes  # type: ignore[attr-defined]
        return bool(attrs & 0x400)
    except Exception:
        return False


def remove_path(path: Path, trash_root: Path, apply: bool) -> str:
    """Move to trash (safer than hard delete). Returns action description."""
    trash_root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = trash_root / f"{stamp}-{path.name}"
    n = 1
    while dest.exists():
        dest = trash_root / f"{stamp}-{path.name}-{n}"
        n += 1
    if not apply:
        return f"WOULD_MOVE {path} -> {dest}"
    # junctions/symlinks: unlink; real dirs: move
    if is_reparse_point(path) or path.is_symlink():
        path.unlink()
        return f"UNLINKED_JUNCTION {path}"
    shutil.move(str(path), str(dest))
    return f"MOVED {path} -> {dest}"


def plugin_skill_dirs() -> dict[str, list[Path]]:
    found: dict[str, list[Path]] = defaultdict(list)
    if not PLUGIN_CACHE.exists():
        return found
    for md in PLUGIN_CACHE.rglob("SKILL.md"):
        if "node_modules" in md.parts or ".trash" in md.parts:
            continue
        found[md.parent.name.lower()].append(md.parent)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    apply = args.apply

    actions: list[str] = []
    kept: list[str] = []

    plugin_map = plugin_skill_dirs()

    # --- Pass 1: agents vs skills-cursor / cursor/skills (Cursor builtins) ---
    for other_root, label in ((SKILLS_CURSOR, "skills-cursor"), (CURSOR_SKILLS, "cursor/skills")):
        if not other_root.exists() or not AGENTS.exists():
            continue
        for child in sorted(AGENTS.iterdir(), key=lambda p: p.name.lower()):
            if child.name.startswith("."):
                continue
            other = other_root / child.name
            if not other.exists() or not (other / "SKILL.md").exists():
                continue
            if not (child / "SKILL.md").exists():
                continue
            # Prefer Cursor-managed location; remove agents duplicate
            actions.append(
                f"[{label} wins] remove agents copy of `{child.name}` "
                f"(also in {other})"
            )
            actions.append(remove_path(child, AGENTS_TRASH, apply))
            kept.append(f"keep {other}")

    # Refresh agents listing after potential removals conceptually; on dry-run paths still exist
    # --- Pass 2: agents vs claude personal overlaps ---
    if AGENTS.exists() and CLAUDE.exists():
        agents_names = {
            p.name
            for p in AGENTS.iterdir()
            if not p.name.startswith(".") and (p / "SKILL.md").exists()
        }
        claude_names = {
            p.name
            for p in CLAUDE.iterdir()
            if not p.name.startswith(".") and (p / "SKILL.md").exists()
        }
        for name in sorted(agents_names & claude_names):
            a = AGENTS / name
            c = CLAUDE / name
            # If agents copy was already removed in pass1 plan on apply, skip if gone
            if apply and not a.exists():
                continue
            da, dc = skill_desc(a), skill_desc(c)
            ha, hc = tree_hash(a), tree_hash(c)
            note = "identical" if ha and ha == hc else "differ"
            if not dc and da:
                # Claude copy empty/broken — keep agents
                actions.append(f"[claude missing desc; {note}] keep agents, remove claude `{name}`")
                actions.append(remove_path(c, TRASH, apply))
                kept.append(f"keep {a}")
                continue
            actions.append(
                f"[claude canonical; {note}; agents_desc={bool(da)} claude_desc={bool(dc)}] "
                f"remove agents `{name}`"
            )
            actions.append(remove_path(a, AGENTS_TRASH, apply))
            kept.append(f"keep {c}")

    # --- Pass 3: agents junctions that duplicate Cursor plugin skills ---
    if AGENTS.exists():
        for child in sorted(AGENTS.iterdir(), key=lambda p: p.name.lower()):
            if child.name.startswith("."):
                continue
            if not (child / "SKILL.md").exists():
                continue
            plugs = plugin_map.get(child.name.lower(), [])
            if not plugs:
                continue
            # Only remove if agents entry is a junction/symlink (our install style)
            # OR content hash matches a plugin copy
            ch = tree_hash(child)
            match = None
            for p in plugs:
                if tree_hash(p) == ch:
                    match = p
                    break
            if is_reparse_point(child) or match:
                actions.append(
                    f"[plugin provides `{child.name}`] remove agents copy "
                    f"(plugin e.g. {plugs[0]})"
                )
                actions.append(remove_path(child, AGENTS_TRASH, apply))
                kept.append(f"keep plugin {plugs[0]}")

    # Deduplicate action noise for report
    lines = [
        "# Skills dedupe report",
        "",
        f"Mode: **{'APPLY' if apply else 'DRY-RUN'}**",
        "",
        "## Actions",
        "",
    ]
    for a in actions:
        lines.append(f"- {a}")
    lines += ["", "## Kept", ""]
    for k in kept:
        lines.append(f"- {k}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"actions={len(actions)} report={REPORT} apply={apply}")
    for a in actions:
        print(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
