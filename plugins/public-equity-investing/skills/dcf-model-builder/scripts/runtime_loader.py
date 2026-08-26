#!/usr/bin/env python3
"""Load private runtime modules that are not prompt-facing instructions."""

from __future__ import annotations

import hashlib
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from types import ModuleType


def load_runtime_module(module_name: str) -> ModuleType:
    runtime_path = Path(__file__).resolve().parent / module_name
    if not runtime_path.exists():
        raise ImportError(f"runtime module not found: {runtime_path}")

    digest = hashlib.sha1(str(runtime_path).encode("utf-8")).hexdigest()[:12]
    loader_name = f"_skill_runtime_{module_name}_{digest}"
    if loader_name in sys.modules:
        return sys.modules[loader_name]

    loader = SourceFileLoader(loader_name, str(runtime_path))
    spec = spec_from_loader(loader.name, loader)
    if spec is None:
        raise ImportError(f"could not create runtime spec for {runtime_path}")
    module = module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module
