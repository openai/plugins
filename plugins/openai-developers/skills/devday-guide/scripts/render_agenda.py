#!/usr/bin/env python3
"""Render a small, offline agenda from newly verified public event data."""

import argparse
import html
import json
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


def text(value, field, limit=600):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{field} must be nonempty text, at most {limit} characters")
    return value


def timestamp(value, field):
    result = datetime.fromisoformat(text(value, field, 40))
    if result.utcoffset() is None:
        raise ValueError(f"{field} must include a UTC offset")
    return result


def validate(data):
    day = date.fromisoformat(data["date"])
    date.fromisoformat(data["checked_on"])
    zone = ZoneInfo(data["timezone"])
    text(data["location"], "location", 150)
    if data.get("note"):
        text(data["note"], "note")
    url = urlsplit(data["source_url"])
    if (url.scheme != "https" or url.hostname not in {
        "devday.openai.com", "events.openai.com", "openai.com", "www.openai.com"
    } or url.username or url.password or url.port not in (None, 443) or url.query):
        raise ValueError("source_url must be an official public HTTPS URL without query parameters")
    events = data["events"]
    if not isinstance(events, list) or not 1 <= len(events) <= 60:
        raise ValueError("events must contain 1 to 60 published activities")
    ids = set()
    for event in events:
        identifier = text(event["id"], "id", 100)
        if identifier in ids:
            raise ValueError("event IDs must be unique")
        ids.add(identifier)
        text(event["title"], "title", 180)
        if event.get("detail"):
            text(event["detail"], "detail")
        if not isinstance(event.get("selected", False), bool):
            raise ValueError("selected must be a boolean")
        start = timestamp(event["start"], "start")
        if start.astimezone(zone).date() != day:
            raise ValueError("every start must fall on the event date in its timezone")
        if event.get("end") is not None:
            end = timestamp(event["end"], "end")
            if end <= start:
                raise ValueError("end must be after start; use null if unpublished")
    return day, zone


def render(data, today=None):
    day, zone = validate(data)
    today = today or datetime.now(zone).date()
    esc = html.escape

    def clock(value):
        local = timestamp(value, "time").astimezone(zone)
        return local.strftime("%I:%M %p").lstrip("0").lower()

    rows = []
    for index, event in enumerate(sorted(data["events"], key=lambda e: timestamp(e["start"], "start"))):
        start, end = event["start"], event.get("end")
        label = f'<span>{esc(clock(start))}</span>'
        if end:
            label += f'<span class="time-end"> – {esc(clock(end))}</span>'
        when = f'<time datetime="{esc(start)}">{label}</time>'
        if not end:
            when += '<span class="start-only">Start time</span>'
        detail = f'<p>{esc(event["detail"])}</p>' if event.get("detail") else ""
        checked = " checked" if event.get("selected", False) else ""
        rows.append(
            f'<li class="event" data-id="{esc(event["id"])}" data-start="{esc(start)}" data-end="{esc(end or "")}">'
            f'<div class="when">{when}</div><div class="activity">'
            f'<h3 id="event-{index}">{esc(event["title"])}</h3>{detail}</div>'
            f'<label class="pick"><input type="checkbox" aria-labelledby="pick-label event-{index}"{checked}>'
            '<span aria-hidden="true">+</span></label></li>'
        )
    template = (Path(__file__).resolve().parents[1] / "assets" / "agenda.html").read_text()
    replacements = {
        "YEAR": str(day.year),
        "DATE": esc(day.strftime("%A, %B %d, %Y").replace(" 0", " ")),
        "ISO_DATE": day.isoformat(),
        "ZONE": esc(data["timezone"]),
        "ZONE_LABEL": "Pacific Time" if data["timezone"] == "America/Los_Angeles" else esc(data["timezone"].split("/")[-1].replace("_", " ")),
        "LOCATION": esc(data["location"]),
        "STATUS": "Past event · published agenda" if today > day else "Your day at DevDay",
        "CHECKED": esc(data["checked_on"]),
        "SOURCE": esc(data["source_url"]),
        "NOTE": esc(data.get("note", "")),
        "ROWS": "\n".join(rows),
    }
    # Substitute once so source text containing template tokens remains literal.
    import re
    return re.sub(r"@@([A-Z_]+)@@", lambda match: replacements[match.group(1)], template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = render(json.loads(args.data.read_text()))
    except (ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    print(args.output)


if __name__ == "__main__":
    main()
