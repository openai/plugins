#!/usr/bin/env python3
"""Normalize a raw animation strip into fixed-size transparent frames."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install it with `python3 -m pip install pillow`."
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract one horizontal strip into fixed-size frames using a shared "
            "global scale and bottom-center alignment."
        )
    )
    parser.add_argument("--input", required=True, help="Path to the raw strip image.")
    parser.add_argument("--out-dir", required=True, help="Output directory for frames.")
    parser.add_argument(
        "--frames",
        type=int,
        required=True,
        help="Number of horizontal frames in the strip.",
    )
    parser.add_argument(
        "--frame-size",
        type=int,
        default=64,
        help="Output square frame size in pixels. Default: 64.",
    )
    parser.add_argument(
        "--anchor",
        help="Optional anchor frame used to stabilize global scale and frame 01 output.",
    )
    parser.add_argument(
        "--lock-frame1",
        action="store_true",
        help="Replace frame 01 with the provided anchor frame after normalization.",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=8,
        help="Pixels with alpha above this threshold count as sprite content. Default: 8.",
    )
    return parser.parse_args()


def threshold_bbox(image: Image.Image, alpha_threshold: int) -> tuple[int, int, int, int] | None:
    alpha = image.getchannel("A").point(lambda value: 255 if value > alpha_threshold else 0)
    return alpha.getbbox()


def crop_to_content(image: Image.Image, alpha_threshold: int) -> Image.Image | None:
    bbox = threshold_bbox(image, alpha_threshold)
    if bbox is None:
        return None
    return image.crop(bbox)


def split_strip(strip: Image.Image, frames: int) -> list[Image.Image]:
    if frames < 1:
        raise ValueError("frames must be at least 1")
    step = strip.width / frames
    slots: list[Image.Image] = []
    for index in range(frames):
        left = int(round(index * step))
        right = int(round((index + 1) * step))
        slots.append(strip.crop((left, 0, right, strip.height)))
    return slots


def max_content_size(images: Iterable[Image.Image | None]) -> tuple[int, int]:
    widths: list[int] = []
    heights: list[int] = []
    for image in images:
        if image is None:
            continue
        widths.append(image.width)
        heights.append(image.height)
    if not widths or not heights:
        raise SystemExit("No sprite content was detected in the provided strip.")
    return max(widths), max(heights)


def compose_frame(
    image: Image.Image | None,
    frame_size: int,
    scale: float,
) -> Image.Image:
    canvas = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    if image is None:
        return canvas

    width = max(1, int(round(image.width * scale)))
    height = max(1, int(round(image.height * scale)))
    resized = image.resize((width, height), Image.Resampling.NEAREST)
    offset_x = (frame_size - width) // 2
    offset_y = frame_size - height
    canvas.alpha_composite(resized, (offset_x, offset_y))
    return canvas


def load_anchor(path: str | None, alpha_threshold: int) -> tuple[Image.Image | None, Image.Image | None]:
    if path is None:
        return None, None
    anchor = Image.open(path).convert("RGBA")
    cropped = crop_to_content(anchor, alpha_threshold)
    return anchor, cropped


def main() -> None:
    args = parse_args()
    if args.frames < 1:
        raise SystemExit("--frames must be at least 1.")
    if args.frame_size < 1:
        raise SystemExit("--frame-size must be positive.")
    if args.lock_frame1 and not args.anchor:
        raise SystemExit("--lock-frame1 requires --anchor.")

    strip = Image.open(args.input).convert("RGBA")
    slots = split_strip(strip, args.frames)
    contents = [crop_to_content(slot, args.alpha_threshold) for slot in slots]
    anchor_image, anchor_content = load_anchor(args.anchor, args.alpha_threshold)
    max_width, max_height = max_content_size([*contents, anchor_content])
    scale = min(args.frame_size / max_width, args.frame_size / max_height)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for index, content in enumerate(contents, start=1):
        if index == 1 and args.lock_frame1:
            assert anchor_image is not None
            if anchor_image.width == args.frame_size and anchor_image.height == args.frame_size:
                frame = anchor_image
            else:
                frame = compose_frame(anchor_content, args.frame_size, scale)
        else:
            frame = compose_frame(content, args.frame_size, scale)
        frame.save(out_dir / f"{index:02d}.png")


if __name__ == "__main__":
    main()
