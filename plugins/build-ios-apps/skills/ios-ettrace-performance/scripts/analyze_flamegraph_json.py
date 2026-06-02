#!/usr/bin/env python3
"""Summarize ETTrace processed flamegraph JSON for performance triage.

This helper intentionally accepts only the Homebrew ETTrace v1.1.0 processed
flamegraph shape: one `output_<thread>.json` file with a top-level `nodes`
tree. ETTrace raw capture JSON usually lives under an `emerge-output/` temp
folder and has keys such as `threads` and `libraryInfo`; this script rejects
that shape because it has not been symbolicated into flamegraph nodes.

ETTrace v1.1.0 stores `duration` as inclusive time on every real frame and
appends an empty terminal child with zero duration to preserve same-name stack
buckets. The strict validation here is deliberate: a malformed or legacy file
should fail loudly instead of producing misleading hotspot evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


sys.setrecursionlimit(200_000)

IDLE_FRAMES = {
    "mach_msg_trap",
    "__psynch_cvwait",
    "semaphore_wait_trap",
    "kevent_id",
    "__ulock_wait",
    "__workq_kernreturn",
    "__semwait_signal",
    "nanosleep",
    "poll",
    "select",
    "start_wqthread",
}

WRAPPER_FRAME_EXACT = {
    "start",
    "main",
    "libsystem_kernel.dylib",
    "UIApplicationMain",
    "-[UIApplication _run]",
    "GSEventRunModal",
    "_CFRunLoopRunSpecificWithOptions",
    "__CFRunLoopRun",
    "__CFRunLoopDoSource0",
    "__CFRunLoopDoSource1",
    "__CFRunLoopServiceMachPort",
    "__CFMachPortPerform",
    "__CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__",
    "__CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE1_PERFORM_FUNCTION__",
    "__CFRUNLOOP_IS_SERVICING_THE_MAIN_DISPATCH_QUEUE__",
    "_dispatch_client_callout",
    "_dispatch_main_queue_callback_4CF",
    "_dispatch_main_queue_drain",
}

WRAPPER_FRAME_PREFIXES = (
    "runApp<",
    "closure #1 in App.",
)

APP_ENTRYPOINT_SUFFIXES = (
    ".$main()",
    ".main()",
    ".mainApp()",
)


def is_idle(frame: str) -> bool:
    """Return whether a frame represents a blocked or sleeping thread."""
    return frame in IDLE_FRAMES


def is_unattributed(frame: str) -> bool:
    """Return whether ETTrace could not map a sample to a symbol."""
    return frame == "<unattributed>"


def is_wrapper_frame(frame: str) -> bool:
    """Return whether an inclusive frame is generic app/run-loop scaffolding."""
    if frame in WRAPPER_FRAME_EXACT:
        return True

    if any(frame.startswith(prefix) for prefix in WRAPPER_FRAME_PREFIXES):
        return True

    if frame.startswith("static ") and any(frame.endswith(suffix) for suffix in APP_ENTRYPOINT_SUFFIXES):
        return True

    return False


def matches_any_pattern(frame: str, patterns: tuple[str, ...]) -> bool:
    """Return whether a frame matches any case-insensitive focus substring."""
    lowered = frame.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def display_name(node: dict[str, Any]) -> str:
    """Return the frame name for one processed flamegraph node."""
    return str(node.get("name") or "")


def children_of(node: dict[str, Any]) -> list[dict[str, Any]]:
    """Return child nodes while tolerating ETTrace's singleton-child variant."""
    if "children" not in node:
        raise ValueError("Processed ETTrace node is missing `children`.")

    children = node["children"]
    if isinstance(children, dict):
        return [children]

    if isinstance(children, list):
        if not all(isinstance(child, dict) for child in children):
            raise ValueError("Processed ETTrace node has a non-object child entry.")
        return children

    raise ValueError("Processed ETTrace node has invalid `children`.")


def node_weight(node: dict[str, Any]) -> float:
    """Return the inclusive `duration` stored on one ETTrace v1.1.0 node."""
    if "duration" not in node:
        raise ValueError("Processed ETTrace node is missing `duration`.")

    value = node["duration"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Processed ETTrace node has invalid `duration`.")

    duration = float(value)
    if not math.isfinite(duration):
        raise ValueError("Processed ETTrace node has invalid `duration`.")

    return duration


def collect_frame_weights(
    node: dict[str, Any],
    self_weights: dict[str, float],
    inclusive_weights: dict[str, float],
) -> tuple[float, float]:
    """Aggregate self and active-inclusive weights from one flamegraph subtree."""
    name = display_name(node)
    weight = node_weight(node)
    children = children_of(node)
    child_weight = 0.0
    child_active_weight = 0.0

    for child in children:
        total_child_weight, active_child_weight = collect_frame_weights(
            child,
            self_weights,
            inclusive_weights,
        )
        child_weight += total_child_weight
        child_active_weight += active_child_weight

    active_weight = child_active_weight

    if name and name != "<root>":
        self_weight = max(weight - child_weight, 0)
        if not children:
            self_weight = weight
        if self_weight > 0:
            self_weights[name] += self_weight

        if not is_unattributed(name) and not is_idle(name):
            active_weight += self_weight
            inclusive_weights[name] += active_weight

    return weight, active_weight


def thread_root_node(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Return the top-level `nodes` tree from ETTrace v1.1.0 processed JSON."""
    root = payload.get("nodes")
    if isinstance(root, dict):
        return root

    return None


def parse_flamegraph(path: Path):
    """Read processed ETTrace JSON and aggregate totals used by the report."""
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("Processed ETTrace JSON must be an object.")

    if "threadNodes" in payload:
        raise ValueError(
            "This looks like an intermediate or legacy ETTrace flamegraph shape with `threadNodes`. "
            "Use Homebrew ETTrace v1.1.0 output_<thread>.json with top-level `nodes`.",
        )

    if "threads" in payload and "libraryInfo" in payload:
        raise ValueError(
            "This looks like ETTrace raw capture JSON, not processed flamegraph JSON. "
            "Use the output_<thread>.json written in the directory where ettrace was run.",
        )

    thread_root = thread_root_node(payload)
    if thread_root is None:
        raise ValueError("Missing processed flamegraph nodes; this does not look like ETTrace flamegraph JSON.")

    self_weights = defaultdict(float)
    active_inclusive_weights = defaultdict(float)
    total = 0.0
    idle = 0.0
    unattributed = 0.0

    thread_summaries = []
    thread_name = path.stem
    thread_self_weights: dict[str, float] = defaultdict(float)
    thread_inclusive_weights: dict[str, float] = defaultdict(float)
    collect_frame_weights(thread_root, thread_self_weights, thread_inclusive_weights)

    thread_total = sum(thread_self_weights.values())
    thread_summaries.append((thread_total, str(thread_name)))
    total += thread_total

    for frame, weight in thread_self_weights.items():
        self_weights[frame] += weight
        if is_unattributed(frame):
            unattributed += weight
            continue

        if is_idle(frame):
            idle += weight

    for frame, weight in thread_inclusive_weights.items():
        if not is_unattributed(frame) and not is_idle(frame):
            active_inclusive_weights[frame] += weight

    return total, idle, unattributed, self_weights, active_inclusive_weights, thread_summaries


def print_top(
    title: str,
    rows: list[tuple[float, str]],
    denominator: float,
    limit: int,
    percentage_label: str,
) -> None:
    """Print a ranked table where percentages use the requested denominator."""
    print(f"\n{title}")
    for weight, frame in rows[:limit]:
        percent = weight / denominator * 100 if denominator else 0
        print(f"{weight:10.6f} {percent:7.2f}%{percentage_label} {frame}")


def main() -> None:
    """Parse arguments, summarize the flamegraph, and print ranked sections."""
    parser = argparse.ArgumentParser(
        description="Summarize ETTrace processed flamegraph JSON, excluding idle self frames from active percentages.",
    )
    parser.add_argument(
        "json",
        type=Path,
        help="Path to ETTrace v1.1.0 processed output_<thread>.json.",
    )
    parser.add_argument("--top", type=int, default=40, help="Number of rows to print per section.")
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help=(
            "Inclusive-frame substring to include in the focused section. Can be repeated. "
            "If omitted, all inclusive frames are shown."
        ),
    )
    parser.add_argument(
        "--show-wrappers",
        action="store_true",
        help="Include app entrypoint, run loop, and other wrapper frames in inclusive output.",
    )
    args = parser.parse_args()

    try:
        total, idle, unattributed, self_weights, active_inclusive_weights, thread_summaries = parse_flamegraph(
            args.json,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

    active = total - idle - unattributed
    patterns = tuple(args.patterns) if args.patterns else ()

    print(f"Trace: {args.json}")
    print(f"Total duration:     {total:.6f}")
    print(f"Idle self total:    {idle:.6f}")
    print(f"Unattributed total: {unattributed:.6f}")
    print(f"Active total:       {active:.6f}")

    thread_summaries.sort(reverse=True)
    print_top("Threads", thread_summaries, total, min(args.top, len(thread_summaries)), "total")

    active_self_frames = [
        (weight, frame)
        for frame, weight in self_weights.items()
        if not is_idle(frame) and not is_unattributed(frame)
    ]
    active_self_frames.sort(reverse=True)
    print_top("Top active self frames", active_self_frames, active, args.top, "active")

    inclusive_rows = [
        (weight, frame)
        for frame, weight in active_inclusive_weights.items()
        if not patterns or matches_any_pattern(frame, patterns)
        if args.show_wrappers or not is_wrapper_frame(frame)
    ]
    inclusive_rows.sort(reverse=True)
    section_title = "Top focused inclusive frames" if patterns else "Top inclusive frames"
    print_top(section_title, inclusive_rows, active, args.top, "active")


if __name__ == "__main__":
    main()
