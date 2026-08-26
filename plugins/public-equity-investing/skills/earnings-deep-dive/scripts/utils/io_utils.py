import json
from pathlib import Path
from typing import Any


def read_json(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(obj: Any, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_text(text: str, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def file_exists_or_missing(path: str) -> bool:
    if path is None:
        return False
    if isinstance(path, str) and path.strip().upper() == "MISSING":
        return False
    return Path(path).exists()
