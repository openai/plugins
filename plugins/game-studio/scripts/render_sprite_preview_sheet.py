#!/usr/bin/env python3
"""Render a simple contact sheet from a directory of normalized sprite frames."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install it with `python3 -m pip install pillow`."
    ) from exc


NUMBER_RE = re.compile(r"(\d+)")


def natural_key(path: Path) -> list[int | str]:
    parts: list[int | str] = []
    for chunk in NUMBER_RE.split(path.stem):
        if not chunk:
            continue
        if chunk.isdigit():
            parts.append(int(chunk))
        else:
            parts.append(chunk)
    parts.append(path.suffix)
    return parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a preview contact sheet from a directory of sprite frames."
    )
    parser.add_argument("--frames-dir", required=True, help="Directory containing PNG frames.")
    parser.add_argument("--out", required=True, help="Output PNG path.")
    parser.add_argument(
        "--columns",
        type=int,
        default=4,
        help="Number of columns in the preview sheet. Default: 4.",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=8,
        help="Gap between frames in pixels. Default: 8.",
    )
    return parser.parse_args()


def paint_checkerboard(image: Image.Image, tile: int = 16) -> None:
    draw = ImageDraw.Draw(image)
    colors = ((240, 243, 246, 255), (225, 230, 235, 255))
    for top in range(0, image.height, tile):
        for left in range(0, image.width, tile):
            color = colors[((left // tile) + (top // tile)) % 2]
            draw.rectangle((left, top, left + tile, top + tile), fill=color)


def main() -> None:
    args = parse_args()
    if args.columns < 1:
        raise SystemExit("--columns must be at least 1.")
    if args.gap < 0:
        raise SystemExit("--gap cannot be negative.")

    frame_dir = Path(args.frames_dir)
    frames = sorted(frame_dir.glob("*.png"), key=natural_key)
    if not frames:
        raise SystemExit("No PNG frames were found in --frames-dir.")

    images = [Image.open(path).convert("RGBA") for path in frames]
    frame_width = max(image.width for image in images)
    frame_height = max(image.height for image in images)
    rows = math.ceil(len(images) / args.columns)
    sheet_width = args.columns * frame_width + max(0, args.columns - 1) * args.gap
    sheet_height = rows * frame_height + max(0, rows - 1) * args.gap
    sheet = Image.new("RGBA", (sheet_width, sheet_height), (255, 255, 255, 255))
    paint_checkerboard(sheet)

    for index, image in enumerate(images):
        row = index // args.columns
        column = index % args.columns
        left = column * (frame_width + args.gap) + (frame_width - image.width) // 2
        top = row * (frame_height + args.gap) + (frame_height - image.height) // 2
        sheet.alpha_composite(image, (left, top))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


if __name__ == "__main__":
    main()
