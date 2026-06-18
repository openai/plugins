"""Progress transition helpers for the Codex Security workbench."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workbench_constants import PHASES


def reportable_count(
    current_phase: str, requested_phase: str | None, count: int | None
) -> int | None:
    if count is None and requested_phase in PHASES[3:] and current_phase in PHASES[:3]:
        return 0
    return count


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
