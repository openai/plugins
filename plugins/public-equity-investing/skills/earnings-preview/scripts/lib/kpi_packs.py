#!/usr/bin/env python3
"""Load KPI packs and driver models from YAML assets."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_sector_packs(path: Path) -> dict[str, dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    packs = data.get("packs", {}) if isinstance(data, dict) else {}
    return packs


def get_kpis_for_pack(packs: dict[str, dict], sector_pack: str) -> list[str]:
    pack = packs.get(sector_pack)
    if not pack:
        return []
    kpis = []
    for key in ["primary_kpis", "secondary_kpis"]:
        vals = pack.get(key, [])
        if isinstance(vals, list):
            kpis.extend([str(x) for x in vals])
    # De-duplicate preserving order
    seen = set()
    out = []
    for k in kpis:
        if k not in seen:
            out.append(k)
            seen.add(k)
    return out


def load_driver_models(path: Path) -> dict[str, dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    models = data.get("models", {}) if isinstance(data, dict) else {}
    return models
