#!/usr/bin/env python3
"""Render a one-day Google Calendar brief as polished Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo


@dataclass
class Event:
    index: int
    summary: str
    start_raw: str
    end_raw: str
    start: datetime
    end: datetime
    transparency: str | None
    location: str | None
    all_day: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a day brief from Google Calendar JSON.")
    parser.add_argument("--time-min", required=True, help="Inclusive day start in ISO 8601 format.")
    parser.add_argument("--time-max", required=True, help="Exclusive day end in ISO 8601 format.")
    parser.add_argument("--timezone", required=True, help="IANA timezone such as America/Los_Angeles.")
    parser.add_argument("--now", help="Current time in ISO 8601 format for Remaining Today.")
    parser.add_argument("--input", help="Optional path to JSON input. Defaults to stdin.")
    return parser.parse_args()


def load_payload(path: str | None) -> object:
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def parse_iso(raw: str, tz: ZoneInfo) -> datetime:
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def is_all_day_event(start_raw: str, end_raw: str, start: datetime, end: datetime) -> bool:
    if any(marker in start_raw for marker in ("+", "Z")) or any(marker in end_raw for marker in ("+", "Z")):
        return False
    duration = end - start
    return (
        start.time() == time(0, 0)
        and end.time() == time(0, 0)
        and duration >= timedelta(days=1)
        and duration % timedelta(days=1) == timedelta(0)
    )


def normalize_events(payload: object, tz: ZoneInfo) -> list[Event]:
    if isinstance(payload, dict):
        raw_events = payload.get("events", [])
    elif isinstance(payload, list):
        raw_events = payload
    else:
        raise ValueError("Expected a JSON object with an events field or a JSON array.")

    events: list[Event] = []
    for index, item in enumerate(raw_events):
        start_raw = item["start"]
        end_raw = item["end"]
        start = parse_iso(start_raw, tz)
        end = parse_iso(end_raw, tz)
        all_day = is_all_day_event(start_raw, end_raw, start, end)
        events.append(
            Event(
                index=index,
                summary=item.get("summary") or "(Untitled event)",
                start_raw=start_raw,
                end_raw=end_raw,
                start=start,
                end=end,
                transparency=item.get("transparency"),
                location=item.get("location"),
                all_day=all_day,
            )
        )
    events.sort(key=lambda event: (event.start, -(event.end - event.start).total_seconds(), event.index))
    return events


def format_clock(value: datetime) -> str:
    hour = value.hour % 12 or 12
    suffix = "AM" if value.hour < 12 else "PM"
    return f"{hour}:{value.minute:02d} {suffix}"


def format_clock_short(value: datetime) -> str:
    hour = value.hour % 12 or 12
    suffix = "AM" if value.hour < 12 else "PM"
    if value.minute == 0:
        return f"{hour}:00 {suffix}"
    return f"{hour}:{value.minute:02d} {suffix}"


def format_range(start: datetime, end: datetime) -> str:
    return f"{format_clock_short(start)}-{format_clock_short(end)}"


def format_clock_compact(value: datetime) -> tuple[str, str]:
    hour = value.hour % 12 or 12
    suffix = "AM" if value.hour < 12 else "PM"
    if value.minute == 0:
        return f"{hour}:00", suffix
    return f"{hour}:{value.minute:02d}", suffix


def format_range_compact(start: datetime, end: datetime) -> str:
    start_text, start_suffix = format_clock_compact(start)
    end_text, end_suffix = format_clock_compact(end)
    if start_suffix == end_suffix:
        return f"{start_text}-{end_text} {end_suffix}"
    return f"{start_text} {start_suffix}-{end_text} {end_suffix}"


def format_range_agenda(start: datetime, end: datetime) -> str:
    start_text, _ = format_clock_compact(start)
    end_text, _ = format_clock_compact(end)
    return f"{start_text}-{end_text}"


def format_duration(delta: timedelta) -> str:
    minutes = int(delta.total_seconds() // 60)
    hours, remainder = divmod(minutes, 60)
    if hours and remainder:
        return f"{hours}h {remainder}m"
    if hours:
        return f"{hours}h"
    return f"{remainder}m"


def opaque_timed_events(events: Iterable[Event]) -> list[Event]:
    return [event for event in events if not event.all_day and event.transparency != "transparent"]


def timed_events(events: Iterable[Event]) -> list[Event]:
    return [event for event in events if not event.all_day]


def merge_intervals(events: Iterable[Event]) -> list[tuple[datetime, datetime]]:
    intervals = [(event.start, event.end) for event in events]
    if not intervals:
        return []
    intervals.sort()
    merged: list[tuple[datetime, datetime]] = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start < last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def conflict_zones(events: list[Event]) -> list[tuple[datetime, datetime, list[Event]]]:
    if len(events) < 2:
        return []
    buckets: dict[datetime, dict[str, list[Event]]] = {}
    for event in events:
        buckets.setdefault(event.start, {"start": [], "end": []})["start"].append(event)
        buckets.setdefault(event.end, {"start": [], "end": []})["end"].append(event)

    ordered_times = sorted(buckets)
    active: list[Event] = []
    zones: list[tuple[datetime, datetime, list[Event]]] = []

    for index, current_time in enumerate(ordered_times):
        bucket = buckets[current_time]
        if bucket["end"]:
            active = [event for event in active if all(event is not finished for finished in bucket["end"])]
        active.extend(bucket["start"])

        if index + 1 >= len(ordered_times):
            continue
        next_time = ordered_times[index + 1]
        if current_time >= next_time or len(active) < 2:
            continue

        active_snapshot = list(active)
        if zones and zones[-1][1] == current_time:
            prior_start, _, prior_events = zones[-1]
            merged_events = {id(event): event for event in prior_events}
            for event in active_snapshot:
                merged_events[id(event)] = event
            zones[-1] = (prior_start, next_time, list(merged_events.values()))
        else:
            zones.append((current_time, next_time, active_snapshot))
    return zones


def free_windows(day_start: datetime, day_end: datetime, busy: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    windows: list[tuple[datetime, datetime]] = []
    cursor = day_start
    for start, end in busy:
        if cursor < start:
            windows.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        windows.append((cursor, day_end))
    return windows


def summarize_best_free_windows(
    windows: list[tuple[datetime, datetime]],
    first_event: Event | None,
    last_event: Event | None,
    day_start: datetime,
    day_end: datetime,
) -> str | None:
    if not windows:
        return None

    selected: list[tuple[datetime, datetime]] = []
    internal = []
    before_first = None
    after_last = None

    for start, end in windows:
        duration = end - start
        if duration < timedelta(minutes=25):
            continue
        if day_start.replace(hour=11, minute=30) <= start < day_start.replace(hour=14, minute=0) and duration < timedelta(minutes=45):
            continue
        if start == day_start and first_event is not None:
            before_first = (start, end)
        elif end == day_end and last_event is not None:
            after_last = (start, end)
        else:
            internal.append((start, end))

    if before_first:
        selected.append(before_first)
    internal = sorted(internal, key=lambda pair: (pair[1] - pair[0], pair[0]), reverse=True)
    selected.extend(internal[: 3 - len(selected)])
    if len(selected) < 3 and after_last:
        selected.append(after_last)

    if not selected:
        return None

    selected = sorted(selected, key=lambda pair: pair[0])
    return ", ".join(window_label(start, end, first_event, last_event, day_start, day_end) for start, end in selected)


def window_label(
    start: datetime,
    end: datetime,
    first_event: Event | None,
    last_event: Event | None,
    day_start: datetime,
    day_end: datetime,
) -> str:
    if start == day_start and first_event is not None:
        return f"before `{format_clock(first_event.start)}`"
    if end == day_end and last_event is not None:
        return f"after `{format_clock(last_event.end)}`"
    return f"`{format_range(start, end)}`"


def lunch_note(windows: list[tuple[datetime, datetime]], day_start: datetime) -> str:
    lunch_start = day_start.replace(hour=11, minute=30)
    lunch_end = day_start.replace(hour=14, minute=0)
    best: tuple[datetime, datetime] | None = None
    for start, end in windows:
        overlap_start = max(start, lunch_start)
        overlap_end = min(end, lunch_end)
        if overlap_start >= overlap_end:
            continue
        if best is None or (overlap_end - overlap_start) > (best[1] - best[0]):
            best = (overlap_start, overlap_end)

    if best and (best[1] - best[0]) >= timedelta(minutes=45):
        return f"Lunch window: `{format_range(best[0], best[1])}`"
    return "No real lunch break"


def build_day_shape(timed: list[Event], busy_intervals: list[tuple[datetime, datetime]]) -> str:
    if not timed:
        return "This day is open. There are no timed events on the calendar."
    compressed = most_compressed_block(timed)
    if compressed:
        start, end = compressed
        return (
            "This is a collaboration-heavy day with very little slack once the afternoon starts. "
            f"After `{format_clock(start)}`, you're essentially in continuous meetings or overlapping commitments until `{format_clock(end)}`."
        )

    longest = max((end - start for start, end in busy_intervals), default=timedelta(0))
    if len(timed) >= 8 or longest >= timedelta(hours=2):
        return "This is a collaboration-heavy day with only a few short recovery windows between meetings."
    return "This day is fairly manageable, with a few concentrated meeting blocks and some room between them."


def remaining_events(now: datetime | None, day_end: datetime, events: list[Event]) -> list[Event]:
    if now is None or not (events and now < day_end):
        return []
    return [event for event in events if event.end > now]


def overlap_events(target: Event, events: list[Event]) -> list[Event]:
    overlaps = []
    for other in events:
        if other is target:
            continue
        if target.start < other.end and other.start < target.end:
            overlaps.append(other)
    overlaps.sort(key=lambda event: (event.start, event.index))
    return overlaps


def representative_conflicts(events: list[Event]) -> list[tuple[Event, list[Event], datetime, datetime]]:
    items: list[tuple[Event, list[Event], datetime, datetime]] = []
    for event in events:
        overlaps = overlap_events(event, events)
        if not overlaps:
            continue

        duration = event.end - event.start
        if any((other.end - other.start) > duration for other in overlaps):
            continue
        if any((other.end - other.start) == duration and other.index < event.index for other in overlaps):
            continue

        near_start = [other for other in overlaps if other.start <= event.start + timedelta(minutes=30)]
        selected = near_start or overlaps
        intersections = []
        for other in selected:
            start = max(event.start, other.start)
            end = min(event.end, other.end)
            if start < end:
                intersections.append((start, end))
        if not intersections:
            continue

        intersections.sort()
        overlap_start = intersections[0][0]
        overlap_end = intersections[0][1]
        for start, end in intersections[1:]:
            if start <= overlap_end:
                overlap_end = max(overlap_end, end)
            else:
                break
        items.append((event, selected, overlap_start, overlap_end))

    items.sort(key=lambda item: (item[2], item[0].index))
    deduped: list[tuple[Event, list[Event], datetime, datetime]] = []
    seen: set[tuple[int, ...]] = set()
    for item in items:
        key = tuple(sorted([item[0].index] + [other.index for other in item[1]]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def agenda_note(event: Event, overlaps: list[Event], overlap_start: datetime, overlap_end: datetime) -> str | None:
    if not overlaps:
        return None
    if len(overlaps) == 1:
        other = overlaps[0]
        if overlap_start == event.start and other.start < event.start:
            return f" ⚠ overlaps {other.summary} at the start"
        return f" ⚠ overlaps {other.summary}"
    return f" ⚠ overlaps other meetings from {format_range_agenda(overlap_start, overlap_end)}"


def midday_buffer(windows: list[tuple[datetime, datetime]], day_start: datetime) -> tuple[datetime, datetime] | None:
    lunch_start = day_start.replace(hour=11, minute=30)
    lunch_end = day_start.replace(hour=14, minute=0)
    candidates = []
    for start, end in windows:
        overlap_start = max(start, lunch_start)
        overlap_end = min(end, lunch_end)
        if overlap_end - overlap_start >= timedelta(minutes=25):
            candidates.append((overlap_start, overlap_end))
    if len(candidates) == 1:
        return candidates[0]
    if candidates:
        return max(candidates, key=lambda pair: pair[1] - pair[0])
    return None


def most_compressed_block(timed: list[Event]) -> tuple[datetime, datetime] | None:
    if not timed:
        return None
    blocks: list[tuple[datetime, datetime]] = []
    current_start = timed[0].start
    current_end = timed[0].end
    for event in timed[1:]:
        if event.start - current_end <= timedelta(minutes=10):
            current_end = max(current_end, event.end)
        else:
            blocks.append((current_start, current_end))
            current_start = event.start
            current_end = event.end
    blocks.append((current_start, current_end))

    afternoon_blocks = [block for block in blocks if block[0].hour >= 12]
    candidate_blocks = afternoon_blocks or blocks
    best = max(candidate_blocks, key=lambda block: block[1] - block[0], default=None)
    if best and best[1] - best[0] >= timedelta(hours=2):
        return best
    return None


def evening_readout(timed: list[Event], day_start: datetime) -> str | None:
    evening_events = [event for event in timed if event.start >= day_start.replace(hour=17, minute=0)]
    if not evening_events:
        return None
    if len(evening_events) == 1:
        return f"Tonight is light: one event at `{format_clock(evening_events[0].start)}`."
    first = evening_events[0]
    second = evening_events[1]
    bridge = "then a later hold" if "[hold]" in second.summary.lower() else "then another meeting"
    return f"Tonight is lighter: one 1:1 at `{format_clock(first.start)}`, {bridge} at `{format_clock(second.start)}`."


def render(events: list[Event], day_start: datetime, day_end: datetime, now: datetime | None) -> str:
    timed = timed_events(events)
    busy_events = opaque_timed_events(events)
    busy_intervals = merge_intervals(busy_events)
    windows = free_windows(day_start, day_end, busy_intervals)
    conflicts = representative_conflicts(busy_events)

    day_heading = f"**{day_start.strftime('%A, %B')} {day_start.day}**"
    lines = [day_heading]

    day_markers = [event.summary for event in events if event.all_day]
    if day_markers:
        office_markers = [marker for marker in day_markers if "office" in marker.lower()]
        if office_markers:
            lines.append(f"📍 **Office day:** `{office_markers[0]}`")
        else:
            joined = ", ".join(f"`{marker}`" for marker in day_markers[:3])
            lines.append(f"📍 **Day markers:** {joined}")

    if conflicts:
        label = "conflict zone" if len(conflicts) == 1 else "conflict zones"
        lines.append(f"⚠ **{len(conflicts)} {label}**")

    if busy_events:
        lines.append(f"🍽 **{lunch_note(windows, day_start)}**")
        best_windows = summarize_best_free_windows(windows, timed[0] if timed else None, timed[-1] if timed else None, day_start, day_end)
        if best_windows:
            lines.append(f"🟢 **Best free windows:** {best_windows}")

    lines.extend(["", "**Day Shape**", build_day_shape(timed, busy_intervals), "", "**Agenda**", "", "| Time | Meeting |", "|---|---|"])

    conflict_by_event = {event.index: (selected, overlap_start, overlap_end) for event, selected, overlap_start, overlap_end in conflicts}
    if timed:
        for event in timed:
            suffix = ""
            if event.index in conflict_by_event:
                selected, overlap_start, overlap_end = conflict_by_event[event.index]
                suffix = agenda_note(event, selected, overlap_start, overlap_end) or ""
            lines.append(f"| {format_range_agenda(event.start, event.end)} | {event.summary}{suffix} |")
    else:
        lines.append("| — | No timed events |")

    if conflicts:
        lines.extend(["", "**What Needs Attention**"])
        for event, selected, start, end in conflicts:
            if len(selected) == 1:
                first, second = (selected[0], event) if selected[0].start < event.start else (event, selected[0])
                lines.append(f"- ⚠ `{format_range_agenda(start, end)}`: `{first.summary}` vs `{second.summary}`")
            elif len(selected) == 2:
                lines.append(
                    f"- ⚠ `{format_range_agenda(start, end)}`: `{event.summary}` overlaps `{selected[0].summary}` and `{selected[1].summary}`"
                )
            else:
                joined = ", ".join(f"`{other.summary}`" for other in selected[:-1])
                lines.append(f"- ⚠ `{format_range_agenda(start, end)}`: `{event.summary}` overlaps {joined}, and `{selected[-1].summary}`")

    lines.extend(["", "**Useful Readout**"])
    if timed:
        midday = midday_buffer(windows, day_start)
        if midday:
            lines.append(f"- `{format_range_compact(midday[0], midday[1])}` is your only meaningful midday buffer.")
        compressed = most_compressed_block(timed)
        if compressed:
            lines.append(f"- `{format_range_compact(compressed[0], compressed[1])}` is the most compressed part of the day.")
        evening = evening_readout(timed, day_start)
        if evening:
            lines.append(f"- {evening}")
        if lines[-1] == "**Useful Readout**":
            lines.append(f"- You have `{len(timed)}` timed events today.")
    else:
        lines.append("- The calendar is open for this day.")

    upcoming = remaining_events(now, day_end, timed)
    if upcoming:
        lines.extend(["", "**Remaining Today**"])
        for event in upcoming:
            lines.append(f"- `{format_range(event.start, event.end)}`: `{event.summary}`")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = parse_args()
    tz = ZoneInfo(args.timezone)
    payload = load_payload(args.input)
    events = normalize_events(payload, tz)
    day_start = parse_iso(args.time_min, tz)
    day_end = parse_iso(args.time_max, tz)
    now = parse_iso(args.now, tz) if args.now else None
    sys.stdout.write(render(events, day_start, day_end, now))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
