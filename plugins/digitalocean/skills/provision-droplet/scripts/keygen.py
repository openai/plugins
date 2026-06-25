#!/usr/bin/env python3
"""Generate a unique prefix and ed25519 SSH key pair for a Codex droplet.

Outputs a single JSON object to stdout:
  {
    "prefix":   "bright-hawk-a3f2",
    "name":     "codex-bright-hawk-a3f2",
    "key_name": "codex-key-bright-hawk-a3f2",
    "key_path": "/Users/you/.ssh/codex_bright-hawk-a3f2_ed25519",
    "pub_key":  "ssh-ed25519 AAAA..."
  }
"""

from __future__ import annotations

import json
import os
import random
import secrets
import subprocess
from pathlib import Path

ADJECTIVES = [
    "bright", "silent", "swift", "calm", "bold",
    "dark", "keen", "vast", "crisp", "teal",
]
NOUNS = [
    "hawk", "reef", "pine", "dusk", "forge",
    "tide", "vale", "peak", "grove", "flint",
]


def make_prefix() -> str:
    return f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}-{secrets.token_hex(2)}"


def main() -> None:
    prefix = make_prefix()
    name = f"codex-{prefix}"
    key_name = f"codex-key-{prefix}"
    key_path = Path(f"~/.ssh/codex_{prefix}_ed25519").expanduser()

    key_path.parent.mkdir(parents=True, exist_ok=True)
    pub_path = Path(str(key_path) + ".pub")

    if not key_path.exists():
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", str(key_path),
             "-N", "", "-C", f"codex@{name}"],
            check=True,
        )
        key_path.chmod(0o600)

    pub_key = pub_path.read_text().strip()

    print(json.dumps({
        "prefix":   prefix,
        "name":     name,
        "key_name": key_name,
        "key_path": str(key_path),
        "pub_key":  pub_key,
    }))


if __name__ == "__main__":
    main()
