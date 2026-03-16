#!/usr/bin/env python3
"""Build a transparent edit canvas around a shipped seed sprite frame."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install it with `python3 -m pip install pillow`."
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Upscale a seed sprite with nearest-neighbor sampling and place it into "
            "the leftmost slot of a larger transparent edit canvas."
        )
    )
    parser.add_argument("--seed", required=True, help="Path to the approved seed frame.")
    parser.add_argument("--out", required=True, help="Path to the output PNG.")
    parser.add_argument(
        "--frames",
        type=int,
        default=4,
        help="Number of horizontal frame slots to reserve. Default: 4.",
    )
    parser.add_argument(
        "--slot-size",
        type=int,
        default=256,
        help="Size of each square frame slot in pixels. Default: 256.",
    )
    parser.add_argument(
        "--canvas-size",
        type=int,
        default=1024,
        help="Size of the square transparent canvas in pixels. Default: 1024.",
    )
    return parser.parse_args()


def resize_seed(seed: Image.Image, slot_size: int) -> Image.Image:
    max_dim = max(seed.size)
    scale = slot_size / max_dim
    if scale >= 1:
        scale = max(1, int(scale))
    width = max(1, int(round(seed.width * scale)))
    height = max(1, int(round(seed.height * scale)))
    return seed.resize((width, height), Image.Resampling.NEAREST)


def main() -> None:
    args = parse_args()
    if args.frames < 1:
        raise SystemExit("--frames must be at least 1.")
    if args.slot_size < 1 or args.canvas_size < 1:
        raise SystemExit("--slot-size and --canvas-size must be positive.")

    strip_width = args.frames * args.slot_size
    if strip_width > args.canvas_size or args.slot_size > args.canvas_size:
        raise SystemExit("Frame slots do not fit inside the requested canvas size.")

    seed = Image.open(args.seed).convert("RGBA")
    seed = resize_seed(seed, args.slot_size)

    canvas = Image.new("RGBA", (args.canvas_size, args.canvas_size), (0, 0, 0, 0))
    strip_left = (args.canvas_size - strip_width) // 2
    strip_top = (args.canvas_size - args.slot_size) // 2
    slot_left = strip_left
    slot_top = strip_top
    paste_x = slot_left + (args.slot_size - seed.width) // 2
    paste_y = slot_top + (args.slot_size - seed.height) // 2
    canvas.alpha_composite(seed, (paste_x, paste_y))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


if __name__ == "__main__":
    main()
