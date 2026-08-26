#!/usr/bin/env python3
"""Public entrypoint for the bundled DCF formula workbook materializer."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from runtime_loader import load_runtime_module

_runtime = load_runtime_module("build_banker_formula_workbook_runtime")

__all__ = [name for name in dir(_runtime) if not name.startswith("_")]
globals().update({name: getattr(_runtime, name) for name in __all__})


if __name__ == "__main__":
    raise SystemExit(_runtime.main())
