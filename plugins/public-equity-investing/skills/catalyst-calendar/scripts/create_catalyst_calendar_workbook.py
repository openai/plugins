#!/usr/bin/env python3
"""Create a PM-grade catalyst calendar workbook and optional ICS export.

This script intentionally uses only the Python standard library so it can run in
restricted Skill environments without external spreadsheet packages. It accepts a
clean CSV of event records and writes a multi-sheet .xlsx workbook. If no input
is provided, it creates a blank institutional template with headers, source map,
change log, and data dictionary.

Example:
  python scripts/create_catalyst_calendar_workbook.py \
    --input events.csv \
    --output catalyst_calendar.xlsx \
    --ics catalyst_calendar.ics
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from workbook_writer import write_xlsx

EVENT_HEADERS = [
    "event_id",
    "ticker",
    "issuer",
    "security_type",
    "portfolio_group",
    "position_context",
    "sector",
    "region",
    "event_category",
    "event_subcategory",
    "event_name",
    "event_description",
    "reported_period",
    "date_type",
    "event_date",
    "window_start",
    "window_end",
    "time_of_day",
    "time_zone",
    "status",
    "source_label",
    "source_id",
    "source_notes",
    "impact_score",
    "confidence_score",
    "urgency",
    "thesis_relevance",
    "kpi_or_model_line",
    "market_setup",
    "expected_outcome",
    "variant_watch",
    "prep_required",
    "owner",
    "prep_due_date",
    "follow_up_date",
    "decision_implication",
    "post_event_action",
    "notes",
]

FIELD_ALIASES = {
    "company": "issuer",
    "event_type": "event_category",
    "event_window_start": "window_start",
    "event_window_end": "window_end",
    "date_window_start": "window_start",
    "date_window_end": "window_end",
    "source": "source_label",
    "source_confidence": "confidence_score",
    "confidence": "confidence_score",
    "importance": "impact_score",
    "materiality": "impact_score",
    "impact": "impact_score",
    "impact_path": "kpi_or_model_line",
    "expected_market_impact": "market_setup",
    "thesis_link": "thesis_relevance",
    "prep_action": "prep_required",
    "next_decision": "decision_implication",
    "confirm_signal": "variant_watch",
    "disconfirm_signal": "variant_watch",
}

SOURCE_HEADERS = [
    "source_id",
    "source_name",
    "source_type",
    "source_owner_or_provider",
    "source_date",
    "retrieved_at",
    "fields_supported",
    "event_ids_supported",
    "confidence",
    "limitations",
    "citation_or_location",
    "restricted_flag",
    "notes",
]

CHANGE_HEADERS = [
    "change_id",
    "timestamp",
    "event_id",
    "field_changed",
    "old_value",
    "new_value",
    "source_id",
    "confidence_change",
    "rationale",
    "changed_by",
]

PREP_HEADERS = [
    "event_id",
    "ticker",
    "event_name",
    "prep_workstream",
    "owner",
    "due_date",
    "status",
    "dependency",
    "blocker",
    "next_step",
    "last_updated",
]

TOP_EVENT_HEADERS = [
    "rank",
    "ticker",
    "event_name",
    "date_or_window",
    "status",
    "impact_score",
    "confidence_score",
    "urgency",
    "why_it_matters",
    "market_setup",
    "owner",
    "prep_due_date",
    "decision_implication",
]

DASHBOARD_HEADERS = ["Metric", "Value", "PM implication"]

CATEGORY_SHEETS = [
    ("Earnings", ["earnings"]),
    ("Reg Legal", ["regulatory / legal", "regulatory", "legal"]),
    (
        "Clinical Product",
        ["clinical / scientific", "clinical", "scientific", "company event", "product"],
    ),
    ("Macro Rates", ["macro / rates / cross-asset", "macro", "rates", "cross-asset"]),
    ("CapMkts Flows", ["capital markets", "ownership / flow", "corporate action"]),
]

DATA_DICTIONARY_ROWS = [
    ["event_id", "Stable unique identifier used to avoid duplicate events on refresh."],
    [
        "date_type",
        "confirmed date, confirmed window, management-indicated window, street-estimated date/window, statutory deadline, model-derived date, speculative / needs confirmation.",
    ],
    [
        "source_label",
        "company-confirmed, official-confirmed, data-provider, street-estimated, model-derived, user-provided, assumption, pm-judgment, restricted/internal.",
    ],
    [
        "impact_score",
        "1-5 expected impact on estimates, valuation, risk, narrative, or thesis status.",
    ],
    ["confidence_score", "1-5 confidence in timing and event mechanics."],
    [
        "urgency",
        "red, amber, green, gray based on impact, timing, prep, and source conflict.",
    ],
    [
        "thesis_relevance",
        "confirmatory, disconfirmatory, asymmetric upside/downside, binary risk, volatility event, monitoring only.",
    ],
    [
        "market_setup",
        "high bar, low bar, crowded long/short, derisked, underfollowed, catalyst fatigue, high/low implied move, unknown.",
    ],
    [
        "prep_due_date",
        "Internal deadline before the event date; should not default to the event date.",
    ],
    ["follow_up_date", "Date to log actual outcome and update model/thesis/risk work."],
]

REVIEW_ROWS = [
    [
        "Source/date integrity",
        "Exact dates are sourced or mechanically derived; windows remain windows; source conflicts surfaced.",
    ],
    [
        "Calendar hygiene",
        "Moved/delayed/canceled/stale events are marked, not deleted; duplicate events consolidated.",
    ],
    [
        "PM usefulness",
        "Top events explain why they matter, what changes, market setup, prep, owner, and decision implication.",
    ],
    [
        "Sector judgment",
        "Sector-specific mechanics handled correctly (trial dates, bank CCAR, retail comps, lockups, etc.).",
    ],
    [
        "Compliance",
        "Restricted/internal sources flagged; external-clean outputs remove trade/position/private-source language.",
    ],
    [
        "Workbook safety",
        "Original data preserved; source map and change log append-only.",
    ],
]


@dataclass
class EventRecord:
    values: dict[str, str]

    def get(self, key: str, default: str = "") -> str:
        value = self.values.get(key, default)
        return "" if value is None else str(value).strip()

    def set(self, key: str, value: object) -> None:
        self.values[key] = "" if value is None else str(value)


def normalize_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")


def canonicalize_row(row: dict[str, str]) -> dict[str, str]:
    canonical: dict[str, str] = dict(row)
    for alias, target in FIELD_ALIASES.items():
        if alias in row and target not in canonical:
            canonical[target] = row[alias]
        elif alias in row and not str(canonical.get(target, "")).strip():
            canonical[target] = row[alias]

    # Convert legacy confidence labels into numeric timing confidence when needed.
    confidence = str(row.get("confidence", "") or row.get("source_confidence", "")).strip().lower()
    if confidence and not str(canonical.get("confidence_score", "")).strip().isdigit():
        canonical["confidence_score"] = {
            "confirmed": "5",
            "guided": "4",
            "expected": "3",
            "inferred": "2",
            "rumored": "1",
            "unknown": "1",
        }.get(confidence, canonical.get("confidence_score", ""))
        if not str(canonical.get("source_notes", "")).strip():
            canonical["source_notes"] = f"confidence label: {confidence}"
    return canonical


def parse_date(value: str) -> dt.date | None:
    if not value:
        return None
    text = value.strip()
    for fmt in (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y/%m/%d",
        "%d-%b-%Y",
        "%b %d %Y",
        "%B %d %Y",
    ):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def iso_date(value: dt.date | None) -> str:
    return value.isoformat() if value else ""


def safe_int(value: str, default: int = 0) -> int:
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(float(str(value).strip()))
    except ValueError:
        return default


def make_event_id(row: dict[str, str]) -> str:
    ticker = row.get("ticker") or row.get("issuer") or "unknown"
    category = row.get("event_category") or "event"
    name = row.get("event_name") or row.get("event_description") or "unnamed"
    period = (
        row.get("reported_period") or row.get("event_date") or row.get("window_start") or "undated"
    )
    raw = "|".join([ticker, category, name, period]).lower()
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    slug = re.sub(r"[^a-z0-9]+", "_", f"{ticker}_{category}_{digest}".lower()).strip("_")
    return slug[:60] or digest


def canonical_category(category: str) -> str:
    text = (category or "").strip().lower()
    aliases = {
        "earnings": "earnings",
        "print": "earnings",
        "results": "earnings",
        "regulatory": "regulatory / legal",
        "legal": "regulatory / legal",
        "court": "regulatory / legal",
        "clinical": "clinical / scientific",
        "biotech": "clinical / scientific",
        "trial": "clinical / scientific",
        "macro": "macro / rates / cross-asset",
        "rates": "macro / rates / cross-asset",
        "central bank": "macro / rates / cross-asset",
        "capital markets": "capital markets",
        "lockup": "capital markets",
        "flows": "ownership / flow",
        "ownership": "ownership / flow",
        "m&a": "corporate action",
        "ma": "corporate action",
        "merger": "corporate action",
        "conference": "sell-side / access",
        "broker": "sell-side / access",
        "investor day": "company event",
        "product": "company event",
    }
    if text in aliases:
        return aliases[text]
    return category.strip() if category else "needs classification"


def infer_date_type(row: dict[str, str]) -> str:
    if row.get("date_type"):
        return row["date_type"]
    if row.get("event_date"):
        source = (row.get("source_label") or "").lower()
        if "company" in source or "official" in source:
            return "confirmed date"
        if "street" in source or "provider" in source:
            return "street-estimated date/window"
        return "user-provided"
    if row.get("window_start") or row.get("window_end"):
        return (
            "confirmed window"
            if "confirmed" in (row.get("source_label") or "").lower()
            else "management-indicated window"
        )
    return "speculative / needs confirmation"


def date_sort_key(event: EventRecord) -> dt.date:
    return (
        parse_date(event.get("event_date"))
        or parse_date(event.get("window_start"))
        or dt.date(9999, 12, 31)
    )


def compute_urgency(event: EventRecord, as_of: dt.date) -> str:
    existing = event.get("urgency").lower()
    if existing in {"red", "amber", "green", "gray"}:
        return existing
    status = event.get("status").lower()
    if status in {"completed", "canceled", "cancelled", "superseded"}:
        return "gray"
    event_date = date_sort_key(event)
    days = (event_date - as_of).days
    impact = safe_int(event.get("impact_score"), 0)
    confidence = safe_int(event.get("confidence_score"), 0)
    prep_due = parse_date(event.get("prep_due_date"))
    prep_overdue = (
        prep_due is not None
        and prep_due < as_of
        and status not in {"completed", "canceled", "cancelled"}
    )
    source_conflict = (
        "conflict" in event.get("source_notes").lower()
        or "needs confirmation" in event.get("status").lower()
    )
    if (
        prep_overdue
        or (impact >= 4 and days <= 14)
        or (impact >= 5 and days <= 30)
        or (impact >= 4 and source_conflict)
    ):
        return "red"
    if (impact >= 3 and days <= 30) or (impact >= 4 and days <= 60) or confidence <= 2:
        return "amber"
    if status in {"stale", "completed"} or days < -1:
        return "gray"
    return "green"


def normalize_event_row(row: dict[str, str], as_of: dt.date) -> EventRecord:
    row = canonicalize_row(row)
    normalized = {h: str(row.get(h, "")).strip() for h in EVENT_HEADERS}
    # Preserve user-provided extra keys in notes if not part of the canonical schema.
    extras = {k: v for k, v in row.items() if k not in normalized and str(v).strip()}
    if extras and not normalized.get("notes"):
        normalized["notes"] = "; ".join(f"{k}: {v}" for k, v in extras.items())
    if not normalized["event_id"]:
        normalized["event_id"] = make_event_id(normalized)
    normalized["event_category"] = canonical_category(normalized.get("event_category", ""))
    normalized["date_type"] = infer_date_type(normalized)
    if not normalized["status"]:
        d = parse_date(normalized.get("event_date", "")) or parse_date(
            normalized.get("window_end", "")
        )
        normalized["status"] = "stale" if d and d < as_of else "upcoming"
    if not normalized["source_label"]:
        normalized["source_label"] = "user-provided" if any(row.values()) else "assumption"
    if not normalized["impact_score"]:
        normalized["impact_score"] = "3"
    if not normalized["confidence_score"]:
        normalized["confidence_score"] = "3" if normalized["event_date"] else "2"
    rec = EventRecord(normalized)
    rec.set("urgency", compute_urgency(rec, as_of))
    return rec


def load_events(path: Path | None, as_of: dt.date) -> list[EventRecord]:
    if not path:
        return []

    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8-sig") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            records = payload.get("events") or payload.get("rows") or []
        elif isinstance(payload, list):
            records = payload
        else:
            records = []
        events = []
        for raw_row in records:
            if isinstance(raw_row, dict):
                row = {
                    normalize_header(str(k)): ("" if v is None else str(v))
                    for k, v in raw_row.items()
                }
                events.append(normalize_event_row(row, as_of))
        return events

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        normalized_fields = {field: normalize_header(field) for field in reader.fieldnames}
        events: list[EventRecord] = []
        for raw_row in reader:
            row = {normalized_fields[k]: (v or "") for k, v in raw_row.items()}
            events.append(normalize_event_row(row, as_of))
        return events


def date_or_window(event: EventRecord) -> str:
    if event.get("event_date"):
        return event.get("event_date")
    start = event.get("window_start")
    end = event.get("window_end")
    if start and end:
        return f"{start} to {end}"
    if start:
        return f"From {start}"
    if end:
        return f"By {end}"
    return "Needs confirmation"


def why_it_matters(event: EventRecord) -> str:
    explicit = event.get("notes")
    if explicit:
        return explicit[:240]
    thesis = event.get("thesis_relevance") or "thesis confidence"
    kpi = event.get("kpi_or_model_line") or "estimates / narrative"
    category = event.get("event_category") or "event"
    return f"Tests {thesis} through {kpi}; {category} can affect estimates, narrative, risk premium, or position sizing."


def ranked_events(
    events: Sequence[EventRecord], as_of: dt.date, limit: int = 25
) -> list[EventRecord]:
    urgency_rank = {"red": 0, "amber": 1, "green": 2, "gray": 3}

    def score(event: EventRecord) -> tuple[int, int, int, dt.date]:
        urgency = urgency_rank.get(event.get("urgency").lower(), 2)
        impact = -safe_int(event.get("impact_score"), 0)
        confidence_penalty = 0 if safe_int(event.get("confidence_score"), 0) >= 3 else -1
        return (urgency, impact, confidence_penalty, date_sort_key(event))

    return sorted(events, key=score)[:limit]


def build_dashboard(events: Sequence[EventRecord], as_of: dt.date) -> list[list[object]]:
    def within(days: int) -> int:
        count = 0
        for event in events:
            d = date_sort_key(event)
            delta = (d - as_of).days
            if 0 <= delta <= days:
                count += 1
        return count

    red_count = sum(1 for e in events if e.get("urgency").lower() == "red")
    amber_count = sum(1 for e in events if e.get("urgency").lower() == "amber")
    needs_confirmation = sum(
        1
        for e in events
        if "needs confirmation" in (e.get("status") + " " + e.get("date_type")).lower()
    )
    stale_count = sum(1 for e in events if e.get("status").lower() == "stale")
    high_impact = sum(1 for e in events if safe_int(e.get("impact_score"), 0) >= 4)
    low_confidence = sum(1 for e in events if safe_int(e.get("confidence_score"), 0) <= 2)
    red_next_30 = 0
    missing_owner = 0
    overdue_prep = 0
    for event in events:
        d = date_sort_key(event)
        delta = (d - as_of).days
        if 0 <= delta <= 30 and event.get("urgency").lower() == "red":
            red_next_30 += 1
        if not event.get("owner") and not event.get("prep_owner"):
            missing_owner += 1
        due = parse_date(event.get("prep_due_date"))
        if (
            due
            and due < as_of
            and event.get("status").lower() not in {"completed", "canceled", "cancelled"}
        ):
            overdue_prep += 1
    top = ranked_events(events, as_of, 1)
    top_desc = (
        f"{top[0].get('ticker')} - {top[0].get('event_name')} ({date_or_window(top[0])})"
        if top
        else "No events loaded"
    )
    rows: list[list[object]] = [
        ["As of", as_of.isoformat(), "Refresh source data before PM/IC use."],
        [
            "Total events",
            len(events),
            "Use Event Master for full source-backed database.",
        ],
        ["Events next 30 days", within(30), "Prioritize red/amber events for prep."],
        [
            "Events next 60 days",
            within(60),
            "Start long-lead work for high-impact windows.",
        ],
        [
            "Events next 90 days",
            within(90),
            "Keep binary/high-impact events above the fold.",
        ],
        [
            "Red urgency",
            red_count,
            "High impact, near-term, overdue prep, or source conflict.",
        ],
        [
            "Amber urgency",
            amber_count,
            "Moderate/high impact or lower timing confidence.",
        ],
        [
            "Needs confirmation",
            needs_confirmation,
            "Do not treat as confirmed until better sourced.",
        ],
        [
            "Stale events",
            stale_count,
            "Mark completed/moved/canceled; do not delete history.",
        ],
        ["Overdue prep items", overdue_prep, "Escalate owner and workstream."],
        [
            "Top event",
            top_desc,
            "Review market setup, thesis linkage, and decision implication.",
        ],
    ]
    rows.extend(
        [
            [
                "High-impact events",
                high_impact,
                "Impact score >=4; should be explicit in PM/IC prep.",
            ],
            [
                "Red events next 30 days",
                red_next_30,
                "Near-term high-urgency items need owner, prep, and source refresh.",
            ],
            [
                "Low-confidence events",
                low_confidence,
                "Confidence score <=2; treat timing/read-through as provisional.",
            ],
            [
                "Missing prep owner",
                missing_owner,
                "Assign owner before using workbook as a live workplan.",
            ],
        ]
    )
    for idx, event in enumerate(ranked_events(events, as_of, 5), start=1):
        rows.append(
            [
                f"Top catalyst {idx}",
                f"{event.get('ticker') or event.get('issuer')} - {event.get('event_name')} ({date_or_window(event)})",
                why_it_matters(event),
            ]
        )
    rows.extend(
        [
            [
                "Workbook mode",
                "calendar_dashboard_export",
                "First tab is the PM cover; Top Events and Event Master contain detail.",
            ],
            [
                "Source posture",
                "See Source Map",
                "Confirm dates, confidence, and stale/moved events before external use.",
            ],
        ]
    )
    return rows


def build_top_events(events: Sequence[EventRecord], as_of: dt.date) -> list[list[object]]:
    rows: list[list[object]] = []
    for idx, event in enumerate(ranked_events(events, as_of, 30), start=1):
        rows.append(
            [
                idx,
                event.get("ticker") or event.get("issuer"),
                event.get("event_name"),
                date_or_window(event),
                event.get("status"),
                safe_int(event.get("impact_score"), 0),
                safe_int(event.get("confidence_score"), 0),
                event.get("urgency"),
                why_it_matters(event),
                event.get("market_setup"),
                event.get("owner"),
                event.get("prep_due_date"),
                event.get("decision_implication"),
            ]
        )
    return rows


def build_prep_rows(events: Sequence[EventRecord], as_of: dt.date) -> list[list[object]]:
    rows: list[list[object]] = []
    for event in ranked_events(events, as_of, 100):
        prep = event.get("prep_required")
        if not prep and safe_int(event.get("impact_score"), 0) < 4:
            continue
        rows.append(
            [
                event.get("event_id"),
                event.get("ticker") or event.get("issuer"),
                event.get("event_name"),
                prep or "Confirm source, refresh model/consensus, and prepare PM questions",
                event.get("owner"),
                event.get("prep_due_date"),
                "not started" if event.get("status").lower() == "upcoming" else event.get("status"),
                event.get("source_id"),
                "" if event.get("confidence_score") != "1" else "Low timing confidence",
                event.get("variant_watch") or "Define decision trigger before event",
                as_of.isoformat(),
            ]
        )
    return rows


def category_filter(events: Sequence[EventRecord], categories: Sequence[str]) -> list[list[object]]:
    cats = {c.lower() for c in categories}
    rows: list[list[object]] = []
    for event in events:
        category = event.get("event_category").lower()
        subcategory = event.get("event_subcategory").lower()
        if category in cats or subcategory in cats or any(c in category for c in cats):
            rows.append([event.get(h) for h in EVENT_HEADERS])
    return rows


def blank_rows(headers: Sequence[str], n: int = 5) -> list[list[str]]:
    return [["" for _ in headers] for _ in range(n)]


def event_rows(events: Sequence[EventRecord]) -> list[list[object]]:
    return [[event.get(h) for h in EVENT_HEADERS] for event in sorted(events, key=date_sort_key)]


def source_rows(events: Sequence[EventRecord], as_of: dt.date) -> list[list[object]]:
    source_ids = sorted({event.get("source_id") for event in events if event.get("source_id")})
    if not source_ids:
        return blank_rows(SOURCE_HEADERS, 5)
    rows = []
    for sid in source_ids:
        supported = [event.get("event_id") for event in events if event.get("source_id") == sid]
        rows.append(
            [
                sid,
                "",
                "",
                "",
                "",
                as_of.isoformat(),
                "",
                "; ".join(supported),
                "",
                "",
                "",
                "",
                "",
            ]
        )
    return rows


def change_rows(changes: Sequence[Sequence[object]]) -> list[list[object]]:
    return list(changes) if changes else blank_rows(CHANGE_HEADERS, 5)


def merge_events_for_refresh(
    prior_events: Sequence[EventRecord],
    current_events: Sequence[EventRecord],
    as_of: dt.date,
) -> tuple[list[EventRecord], list[list[object]]]:
    """Merge a prior calendar with new evidence and produce an append-only change log."""
    prior_by_id = {event.get("event_id"): event for event in prior_events if event.get("event_id")}
    current_by_id = {
        event.get("event_id"): event for event in current_events if event.get("event_id")
    }
    merged: dict[str, EventRecord] = {}
    changes: list[list[object]] = []
    timestamp = dt.datetime.combine(as_of, dt.time()).isoformat()

    for event_id, prior in prior_by_id.items():
        merged[event_id] = EventRecord(dict(prior.values))

    for event_id, current in current_by_id.items():
        if event_id not in prior_by_id:
            merged[event_id] = current
            changes.append(
                [
                    hashlib.sha1(f"{event_id}|row_added|{timestamp}".encode("utf-8")).hexdigest()[
                        :10
                    ],
                    timestamp,
                    event_id,
                    "row_added",
                    "",
                    current.get("event_name") or current.get("event_description"),
                    current.get("source_id"),
                    current.get("confidence_score"),
                    "New event in refreshed input.",
                    "catalyst-calendar script",
                ]
            )
            continue

        prior = prior_by_id[event_id]
        updated = dict(prior.values)
        for field in EVENT_HEADERS:
            new_value = current.get(field)
            old_value = prior.get(field)
            if new_value and new_value != old_value:
                updated[field] = new_value
                changes.append(
                    [
                        hashlib.sha1(
                            f"{event_id}|{field}|{old_value}|{new_value}|{timestamp}".encode(
                                "utf-8"
                            )
                        ).hexdigest()[:10],
                        timestamp,
                        event_id,
                        field,
                        old_value,
                        new_value,
                        current.get("source_id") or prior.get("source_id"),
                        f"{old_value}->{new_value}" if field == "confidence_score" else "",
                        "Updated from refreshed input.",
                        "catalyst-calendar script",
                    ]
                )
        merged[event_id] = EventRecord(updated)

    for event_id, prior in prior_by_id.items():
        if event_id in current_by_id:
            continue
        preserved = dict(prior.values)
        status = str(preserved.get("status", "")).lower()
        if status not in {"completed", "canceled", "cancelled", "superseded", "stale"}:
            old_status = preserved.get("status", "")
            preserved["status"] = "needs refresh"
            changes.append(
                [
                    hashlib.sha1(
                        f"{event_id}|needs_refresh|{timestamp}".encode("utf-8")
                    ).hexdigest()[:10],
                    timestamp,
                    event_id,
                    "status",
                    old_status,
                    "needs refresh",
                    preserved.get("source_id", ""),
                    "",
                    "Prior event was not present in refreshed input; preserved for review.",
                    "catalyst-calendar script",
                ]
            )
        merged[event_id] = EventRecord(preserved)

    return sorted(merged.values(), key=date_sort_key), changes


def ics_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def fold_ics_line(line: str) -> str:
    # RFC5545 line folding at 75 octets; approximate by chars for simplicity.
    if len(line) <= 75:
        return line
    chunks = [line[:75]]
    rest = line[75:]
    while rest:
        chunks.append(" " + rest[:74])
        rest = rest[74:]
    return "\r\n".join(chunks)


def is_confirmed_ics_date(event: EventRecord) -> bool:
    if not event.get("event_date"):
        return False
    date_type = event.get("date_type").lower()
    source = event.get("source_label").lower()
    if (
        "window" in date_type
        or "estimated" in date_type
        or "speculative" in date_type
        or "needs confirmation" in date_type
    ):
        return False
    return (
        date_type in {"confirmed date", "statutory deadline", "model-derived date"}
        or "confirmed" in source
        or "official" in source
    )


def write_ics(path: Path, events: Sequence[EventRecord], as_of: dt.date) -> None:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//catalyst-calendar skill//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for event in events:
        if event.get("source_label").lower() == "restricted/internal":
            continue
        if not is_confirmed_ics_date(event):
            continue
        d = parse_date(event.get("event_date"))
        if not d:
            continue
        end = d + dt.timedelta(days=1)
        uid = f"{event.get('event_id')}@catalyst-calendar-skill"
        summary = f"{event.get('ticker') or event.get('issuer')} - {event.get('event_name')}"
        description = (
            f"Category: {event.get('event_category')}\\n"
            f"Date type: {event.get('date_type')}\\n"
            f"Status: {event.get('status')}\\n"
            f"Impact: {event.get('impact_score')} | Confidence: {event.get('confidence_score')} | Urgency: {event.get('urgency')}\\n"
            f"Thesis linkage: {event.get('thesis_relevance')}\\n"
            f"Prep owner: {event.get('owner')} | Prep due: {event.get('prep_due_date')}\\n"
            f"Decision implication: {event.get('decision_implication')}"
        )
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{ics_escape(uid)}",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
                f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
                f"SUMMARY:{ics_escape(summary)}",
                f"DESCRIPTION:{ics_escape(description)}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    with path.open("w", encoding="utf-8", newline="") as f:
        for line in lines:
            f.write(fold_ics_line(line) + "\r\n")


def build_sheets(
    events: Sequence[EventRecord],
    as_of: dt.date,
    changes: Sequence[Sequence[object]] = (),
) -> list[tuple[str, Sequence[str], Sequence[Sequence[object]], str]]:
    event_master_rows = event_rows(events) if events else blank_rows(EVENT_HEADERS, 10)
    sheets: list[tuple[str, Sequence[str], Sequence[Sequence[object]], str]] = [
        (
            "Cover",
            DASHBOARD_HEADERS,
            build_dashboard(events, as_of),
            "Catalyst Calendar Dashboard Cover",
        ),
        (
            "Top Events",
            TOP_EVENT_HEADERS,
            build_top_events(events, as_of) if events else blank_rows(TOP_EVENT_HEADERS, 10),
            "PM-Ranked Top Events",
        ),
        ("Event Master", EVENT_HEADERS, event_master_rows, "Full Event Master"),
        (
            "Prep Tracker",
            PREP_HEADERS,
            build_prep_rows(events, as_of) if events else blank_rows(PREP_HEADERS, 10),
            "Pre-Event Workstreams",
        ),
    ]
    for sheet_name, categories in CATEGORY_SHEETS:
        rows = category_filter(events, categories) if events else blank_rows(EVENT_HEADERS, 10)
        sheets.append((sheet_name, EVENT_HEADERS, rows, sheet_name))
    sheets.extend(
        [
            (
                "Source Map",
                SOURCE_HEADERS,
                source_rows(events, as_of),
                "Append-Only Source Map",
            ),
            (
                "Change Log",
                CHANGE_HEADERS,
                change_rows(changes),
                "Append-Only Change Log",
            ),
            (
                "Data Dictionary",
                ["Field", "Definition"],
                DATA_DICTIONARY_ROWS,
                "Data Dictionary",
            ),
            (
                "Review Checklist",
                ["Review area", "Check"],
                REVIEW_ROWS,
                "PM Review Checklist",
            ),
            (
                "Read Me",
                ["Topic", "Guidance"],
                [
                    [
                        "Purpose",
                        "Track sourced, prioritized, PM-actionable public-equity catalysts.",
                    ],
                    [
                        "Safe refresh",
                        "Preserve prior views; append source map and change log; do not delete stale/moved events.",
                    ],
                    [
                        "Date discipline",
                        "Use exact dates only when confirmed or mechanically derived; otherwise use windows.",
                    ],
                    [
                        "Actionability",
                        "Top events should connect to thesis, model line, market setup, prep owner, and decision implication.",
                    ],
                    [
                        "External-clean",
                        "Remove position/trade/private-source language before broader sharing.",
                    ],
                ],
                "Read Me",
            ),
        ]
    )
    return sheets


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a catalyst calendar workbook and optional ICS export."
    )
    parser.add_argument("--input", type=Path, help="Optional CSV of catalyst events.")
    parser.add_argument(
        "--prior",
        type=Path,
        help="Optional prior CSV/JSON catalyst calendar for refresh/change-log mode.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("catalyst_calendar.xlsx"),
        help="Output .xlsx path.",
    )
    parser.add_argument("--ics", type=Path, help="Optional output .ics calendar path.")
    parser.add_argument(
        "--as-of",
        type=str,
        default=dt.date.today().isoformat(),
        help="As-of date, YYYY-MM-DD.",
    )
    args = parser.parse_args(argv)

    as_of = parse_date(args.as_of)
    if not as_of:
        print(f"Invalid --as-of date: {args.as_of}. Use YYYY-MM-DD.", file=sys.stderr)
        return 2

    if args.input and not args.input.exists():
        print(f"Input CSV not found: {args.input}", file=sys.stderr)
        return 2
    if args.prior and not args.prior.exists():
        print(f"Prior calendar not found: {args.prior}", file=sys.stderr)
        return 2

    events = load_events(args.input, as_of)
    changes: list[list[object]] = []
    if args.prior:
        prior_events = load_events(args.prior, as_of)
        events, changes = merge_events_for_refresh(prior_events, events, as_of)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_xlsx(args.output, build_sheets(events, as_of, changes))

    if args.ics:
        args.ics.parent.mkdir(parents=True, exist_ok=True)
        write_ics(args.ics, events, as_of)

    print(f"Created workbook: {args.output}")
    if args.ics:
        print(f"Created ICS: {args.ics}")
    print(f"Events loaded: {len(events)}")
    if args.prior:
        print(f"Refresh changes logged: {len(changes)}")
    print(
        "Sheets: Cover, Top Events, Event Master, Prep Tracker, category tabs, Source Map, Change Log, Data Dictionary, Review Checklist, Read Me"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
