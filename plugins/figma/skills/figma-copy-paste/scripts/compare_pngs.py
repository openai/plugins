#!/usr/bin/env python3
"""Compare two decoded PNG renders and emit stable JSON metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageStat


def global_ssim(left: Image.Image, right: Image.Image) -> float:
    """Return a deterministic whole-image SSIM-like score in the range [-1, 1]."""
    left_array = np.asarray(left, dtype=np.float64)
    right_array = np.asarray(right, dtype=np.float64)
    scores: list[float] = []
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    for channel in range(left_array.shape[2]):
        x = left_array[:, :, channel]
        y = right_array[:, :, channel]
        mean_x = float(x.mean())
        mean_y = float(y.mean())
        variance_x = float(x.var())
        variance_y = float(y.var())
        covariance = float(((x - mean_x) * (y - mean_y)).mean())
        numerator = (2 * mean_x * mean_y + c1) * (2 * covariance + c2)
        denominator = (mean_x**2 + mean_y**2 + c1) * (
            variance_x + variance_y + c2
        )
        scores.append(numerator / denominator if denominator else 1.0)
    return float(sum(scores) / len(scores))


def metrics(left: Image.Image, right: Image.Image) -> dict[str, object]:
    if left.size != right.size:
        return {"same_size": False, "left_size": left.size, "right_size": right.size}

    diff = ImageChops.difference(left, right)
    stat = ImageStat.Stat(diff)
    pixels = (
        diff.get_flattened_data()
        if hasattr(diff, "get_flattened_data")
        else diff.getdata()
    )
    changed = sum(1 for pixel in pixels if any(pixel))
    total = left.width * left.height
    return {
        "same_size": True,
        "decoded_exact": changed == 0,
        "changed_pixels": changed,
        "changed_pixel_ratio": changed / total if total else 0,
        "global_ssim": global_ssim(left, right),
        "mean_absolute_error_by_channel": stat.mean,
        "rms_by_channel": stat.rms,
        "max_delta_by_channel": [maximum for _, maximum in stat.extrema],
    }


def white_composite(image: Image.Image) -> Image.Image:
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, image).convert("RGB")


def crop_to_visible_bounds(image: Image.Image) -> tuple[Image.Image, tuple[int, ...] | None]:
    """Crop fully transparent outer padding without changing visible pixels."""
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0)), None
    return image.crop(bounds), bounds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    args = parser.parse_args()

    left = Image.open(args.left).convert("RGBA")
    right = Image.open(args.right).convert("RGBA")
    left_visible, left_bounds = crop_to_visible_bounds(left)
    right_visible, right_bounds = crop_to_visible_bounds(right)
    result = {
        "left": str(args.left),
        "right": str(args.right),
        "rgba": metrics(left, right),
        "white_composited": metrics(white_composite(left), white_composite(right)),
        "transparent_bounds_normalized": {
            "left_bounds": left_bounds,
            "right_bounds": right_bounds,
            "rgba": metrics(left_visible, right_visible),
            "white_composited": metrics(
                white_composite(left_visible), white_composite(right_visible)
            ),
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
