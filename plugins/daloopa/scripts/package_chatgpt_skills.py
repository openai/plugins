#!/usr/bin/env python3
"""Package Daloopa skills as one ChatGPT-uploadable zip per skill."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
DIST = ROOT / "dist" / "chatgpt-skills"


def rewrite_packaged_skill(text: str) -> str:
    replacements = {
        "../data-access.md": "references/data-access.md",
        "../design-system.md": "references/design-system.md",
        "`data-access.md`": "`references/data-access.md`",
        "`design-system.md`": "`references/design-system.md`",
        "data-access.md Section": "references/data-access.md Section",
        "design-system.md formatting": "references/design-system.md formatting",
        "design-system.md HTML": "references/design-system.md HTML",
        "design-system.md,": "references/design-system.md,",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def copy_skill(skill_dir: Path, dest_root: Path) -> Path:
    dest = dest_root / skill_dir.name
    shutil.copytree(skill_dir, dest)
    skill_md = dest / "SKILL.md"
    skill_md.write_text(rewrite_packaged_skill(skill_md.read_text()))

    refs = dest / "references"
    refs.mkdir(exist_ok=True)
    shutil.copy2(SKILLS / "data-access.md", refs / "data-access.md")
    shutil.copy2(SKILLS / "design-system.md", refs / "design-system.md")
    return dest


def zip_dir(source: Path, output: Path) -> None:
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source.parent))


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    for old_zip in DIST.glob("*.zip"):
        old_zip.unlink()

    for skill_dir in sorted(SKILLS.iterdir()):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
            continue
        with tempfile.TemporaryDirectory() as tmp:
            packaged = copy_skill(skill_dir, Path(tmp))
            zip_dir(packaged, DIST / f"{skill_dir.name}.zip")

    print(f"Packaged skills to {DIST}")


if __name__ == "__main__":
    main()
