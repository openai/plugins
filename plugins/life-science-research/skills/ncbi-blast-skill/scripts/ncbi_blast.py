#!/usr/bin/env python3
"""ncbi_blast

Compact NCBI BLAST Common URL API helper.

Reads one JSON object from stdin and prints one JSON object to stdout.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path
from typing import Any, Callable

try:
    import requests
except ImportError as exc:  # pragma: no cover - exercised via runtime guard
    requests = None
    REQUESTS_IMPORT_ERROR = exc
else:
    REQUESTS_IMPORT_ERROR = None

BLAST_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
DEFAULT_TOOL = "ncbi-blast-skill"
DEFAULT_RESULT_FORMAT = "json2"
DEFAULT_MAX_HITS = 5
DEFAULT_MAX_QUERIES = 5
DEFAULT_HITLIST_SIZE = 50
DEFAULT_DESCRIPTIONS = 5
DEFAULT_ALIGNMENTS = 5
DEFAULT_WAIT_TIMEOUT_SEC = 900
MIN_REQUEST_INTERVAL_SEC = 10
MIN_POLL_INTERVAL_SEC = 60

RID_RE = re.compile(r"^\s*RID\s*=\s*(\S+)", re.MULTILINE)
RTOE_RE = re.compile(r"^\s*RTOE\s*=\s*(\d+)", re.MULTILINE)
STATUS_RE = re.compile(r"Status=(WAITING|READY|FAILED|UNKNOWN)")

VALID_ACTIONS = {"submit", "status", "fetch", "run"}
VALID_PROGRAMS = {"blastn", "blastp", "blastx", "tblastn", "tblastx"}
VALID_RESULT_FORMATS = {"json2", "text"}


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "warnings": warnings or [],
    }


def _parse_positive_int(payload: dict[str, Any], key: str, default: int) -> int:
    value = payload.get(key, default)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"`{key}` must be a positive integer.")
    return value


def _parse_bool(payload: dict[str, Any], key: str, default: bool) -> bool:
    value = payload.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"`{key}` must be a boolean.")
    return value


def _parse_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"`{key}` must be a non-empty string when provided.")
    return value.strip()


def parse_input(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be one JSON object.")

    action = payload.get("action")
    if not isinstance(action, str) or action not in VALID_ACTIONS:
        raise ValueError("`action` must be one of: submit, status, fetch, run.")

    program = _parse_str(payload, "program")
    if program is not None and program not in VALID_PROGRAMS:
        raise ValueError("`program` must be one of: blastn, blastp, blastx, tblastn, tblastx.")

    database = _parse_str(payload, "database")
    query_fasta = _parse_str(payload, "query_fasta")
    rid = _parse_str(payload, "rid")

    tool = _parse_str(payload, "tool") or os.environ.get("NCBI_TOOL", DEFAULT_TOOL)
    email = _parse_str(payload, "email") or os.environ.get("NCBI_EMAIL")
    if email:
        email = email.strip()

    result_format_raw = payload.get("result_format", DEFAULT_RESULT_FORMAT)
    if (
        not isinstance(result_format_raw, str)
        or result_format_raw.lower() not in VALID_RESULT_FORMATS
    ):
        raise ValueError("`result_format` must be `json2` or `text`.")
    result_format = result_format_raw.lower()

    raw_output_path = _parse_str(payload, "raw_output_path")

    config = {
        "action": action,
        "program": program,
        "database": database,
        "query_fasta": query_fasta,
        "rid": rid,
        "tool": tool,
        "email": email,
        "result_format": result_format,
        "max_hits": _parse_positive_int(payload, "max_hits", DEFAULT_MAX_HITS),
        "max_queries": _parse_positive_int(payload, "max_queries", DEFAULT_MAX_QUERIES),
        "hitlist_size": _parse_positive_int(payload, "hitlist_size", DEFAULT_HITLIST_SIZE),
        "descriptions": _parse_positive_int(payload, "descriptions", DEFAULT_DESCRIPTIONS),
        "alignments": _parse_positive_int(payload, "alignments", DEFAULT_ALIGNMENTS),
        "wait_timeout_sec": _parse_positive_int(
            payload, "wait_timeout_sec", DEFAULT_WAIT_TIMEOUT_SEC
        ),
        "megablast": _parse_bool(payload, "megablast", False),
        "save_raw": _parse_bool(payload, "save_raw", False),
        "raw_output_path": raw_output_path,
    }

    if action in {"submit", "run"}:
        if program is None:
            raise ValueError(f"`program` is required for `{action}`.")
        if database is None:
            raise ValueError(f"`database` is required for `{action}`.")
        if query_fasta is None:
            raise ValueError(f"`query_fasta` is required for `{action}`.")
        if email is None:
            raise ValueError(f"`email` is required for `{action}` or via NCBI_EMAIL.")

    if action in {"status", "fetch"} and rid is None:
        raise ValueError(f"`rid` is required for `{action}`.")

    return config


class RequestThrottle:
    def __init__(
        self,
        min_interval_sec: int = MIN_REQUEST_INTERVAL_SEC,
        sleep_fn: Callable[[float], None] = time.sleep,
        clock_fn: Callable[[], float] = time.time,
    ) -> None:
        self.min_interval_sec = min_interval_sec
        self.sleep_fn = sleep_fn
        self.clock_fn = clock_fn
        self.last_request_ts: float | None = None

    def request(self, session: requests.Session, method: str, **kwargs: Any) -> requests.Response:
        if self.last_request_ts is not None:
            remaining = self.min_interval_sec - (self.clock_fn() - self.last_request_ts)
            if remaining > 0:
                self.sleep_fn(remaining)
        response = session.request(method, BLAST_URL, **kwargs)
        self.last_request_ts = self.clock_fn()
        response.raise_for_status()
        return response


def make_session(tool: str | None, email: str | None) -> requests.Session:
    session = requests.Session()
    ua_parts = ["ncbi-blast-skill/1.0 (+requests)"]
    if tool:
        ua_parts.append(f"tool={tool}")
    if email:
        ua_parts.append(f"email={email}")
    session.headers["User-Agent"] = " ".join(ua_parts)
    return session


def submit_search(
    session: requests.Session,
    throttle: RequestThrottle,
    config: dict[str, Any],
) -> dict[str, Any]:
    params = {
        "CMD": "Put",
        "PROGRAM": config["program"],
        "DATABASE": config["database"],
        "QUERY": config["query_fasta"],
        "FORMAT_TYPE": "Text",
        "HITLIST_SIZE": config["hitlist_size"],
        "tool": config["tool"],
        "email": config["email"],
    }
    if config["megablast"] and config["program"] == "blastn":
        params["MEGABLAST"] = "on"

    response = throttle.request(session, "POST", data=params, timeout=60)
    text = response.text

    rid_match = RID_RE.search(text)
    rtoe_match = RTOE_RE.search(text)
    if not rid_match:
        raise ValueError("BLAST submit response did not include an RID.")

    rid = rid_match.group(1)
    rtoe_seconds = int(rtoe_match.group(1)) if rtoe_match else 10

    return {
        "ok": True,
        "source": "ncbi-blast",
        "action": "submit",
        "rid": rid,
        "rtoe_seconds": rtoe_seconds,
        "status": "SUBMITTED",
        "warnings": [],
    }


def parse_search_info(body: str) -> dict[str, Any]:
    status_match = STATUS_RE.search(body)
    if not status_match:
        raise ValueError("BLAST SearchInfo response did not include a recognized status.")
    status = status_match.group(1)
    has_hits = "ThereAreHits=yes" in body
    return {"status": status, "has_hits": has_hits}


def get_search_info(
    session: requests.Session,
    throttle: RequestThrottle,
    rid: str,
    tool: str | None,
    email: str | None,
) -> dict[str, Any]:
    params = {
        "CMD": "Get",
        "FORMAT_OBJECT": "SearchInfo",
        "RID": rid,
    }
    if tool:
        params["tool"] = tool
    if email:
        params["email"] = email

    response = throttle.request(session, "GET", params=params, timeout=30)
    parsed = parse_search_info(response.text)
    return {
        "ok": True,
        "source": "ncbi-blast",
        "action": "status",
        "rid": rid,
        "status": parsed["status"],
        "has_hits": parsed["has_hits"],
        "warnings": [],
    }


def _derive_raw_output_path(rid: str, result_format: str, raw_output_path: str | None) -> Path:
    if raw_output_path:
        return Path(raw_output_path)
    suffix = "json" if result_format == "json2" else "txt"
    return Path(f"/tmp/ncbi-blast-{rid}.{suffix}")


def _save_raw_output(
    rid: str,
    result_format: str,
    raw_output: str,
    raw_output_path: str | None,
) -> str:
    path = _derive_raw_output_path(rid, result_format, raw_output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw_output, encoding="utf-8")
    return str(path)


def _summarize_json2_payload(
    data: Any,
    max_queries: int,
    max_hits: int,
) -> dict[str, Any]:
    reports = data.get("BlastOutput2")
    if isinstance(reports, dict):
        reports = [reports]
    if not isinstance(reports, list):
        raise ValueError("BLAST JSON2 response did not include `BlastOutput2`.")

    summaries: list[dict[str, Any]] = []
    query_count_available = len(reports)
    has_hits = False

    for index, report in enumerate(reports[:max_queries], start=1):
        if not isinstance(report, dict):
            raise ValueError("BLAST JSON2 report entry was not an object.")
        report_body = report.get("report", {})
        if not isinstance(report_body, dict):
            raise ValueError("BLAST JSON2 report payload was not an object.")
        search = report_body.get("results", {}).get("search", {})
        if not isinstance(search, dict):
            raise ValueError("BLAST JSON2 search payload was not an object.")

        query_title = search.get("query_title") or search.get("query_id") or f"query_{index}"
        hits = search.get("hits") or []
        if not isinstance(hits, list):
            raise ValueError("BLAST JSON2 hits payload was not a list.")

        top_hits = []
        for rank, hit in enumerate(hits[:max_hits], start=1):
            if not isinstance(hit, dict):
                continue
            descriptions = hit.get("description") or []
            desc = descriptions[0] if descriptions and isinstance(descriptions[0], dict) else {}
            hsps = hit.get("hsps") or []
            hsp = hsps[0] if hsps and isinstance(hsps[0], dict) else {}
            top_hits.append(
                {
                    "rank": rank,
                    "accession": desc.get("accession") or desc.get("id"),
                    "title": desc.get("title"),
                    "evalue": hsp.get("evalue"),
                    "bit_score": hsp.get("bit_score"),
                }
            )

        hit_count_available = len(hits)
        has_hits = has_hits or hit_count_available > 0
        summaries.append(
            {
                "query_title": query_title,
                "hit_count_returned": len(top_hits),
                "hit_count_available": hit_count_available,
                "truncated": len(top_hits) < hit_count_available,
                "top_hits": top_hits,
            }
        )

    return {
        "query_count_returned": len(summaries),
        "query_count_available": query_count_available,
        "query_summaries_truncated": len(summaries) < query_count_available,
        "query_summaries": summaries,
        "has_hits": has_hits,
    }


def _load_json_member(zip_file: zipfile.ZipFile, member_name: str) -> tuple[Any, str]:
    try:
        text = zip_file.read(member_name).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"BLAST JSON2 archive member {member_name!r} was not UTF-8 text.") from exc
    try:
        return json.loads(text), text
    except ValueError as exc:
        raise ValueError(f"BLAST JSON2 archive member {member_name!r} was not valid JSON.") from exc


def _merge_blast_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not payloads:
        raise ValueError("BLAST JSON2 archive did not contain any payload JSON files.")
    if len(payloads) == 1:
        return payloads[0]

    merged = dict(payloads[0])
    merged_reports: list[Any] = []
    for payload in payloads:
        reports = payload.get("BlastOutput2")
        if isinstance(reports, dict):
            merged_reports.append(reports)
            continue
        if not isinstance(reports, list):
            raise ValueError("BLAST JSON2 payload did not include `BlastOutput2`.")
        merged_reports.extend(reports)
    merged["BlastOutput2"] = merged_reports
    return merged


def _extract_json2_payload(response: requests.Response) -> tuple[Any, str]:
    content_type = (response.headers.get("content-type") or "").lower()
    raw_bytes = response.content
    if content_type.startswith("application/zip") or raw_bytes.startswith(b"PK\x03\x04"):
        try:
            zip_file = zipfile.ZipFile(io.BytesIO(raw_bytes))
        except zipfile.BadZipFile as exc:
            raise ValueError(
                "BLAST JSON2 response looked like a ZIP archive but could not be opened."
            ) from exc

        with zip_file:
            json_members = [name for name in zip_file.namelist() if name.lower().endswith(".json")]
            if not json_members:
                raise ValueError("BLAST JSON2 archive did not contain any JSON members.")

            manifest: dict[str, Any] | None = None
            manifest_members: list[str] = []
            for member_name in json_members:
                payload, _ = _load_json_member(zip_file, member_name)
                if isinstance(payload, dict) and isinstance(payload.get("BlastJSON"), list):
                    manifest = payload
                    manifest_members = [
                        item.get("File")
                        for item in payload["BlastJSON"]
                        if isinstance(item, dict) and isinstance(item.get("File"), str)
                    ]
                    break

            payload_objects: list[dict[str, Any]] = []
            if manifest_members:
                for member_name in manifest_members:
                    if member_name not in zip_file.namelist():
                        raise ValueError(
                            f"BLAST JSON2 archive referenced missing member {member_name!r}."
                        )
                    payload, _ = _load_json_member(zip_file, member_name)
                    if not isinstance(payload, dict):
                        raise ValueError(
                            f"BLAST JSON2 archive member {member_name!r} was not an object."
                        )
                    payload_objects.append(payload)
            else:
                for member_name in json_members:
                    payload, _ = _load_json_member(zip_file, member_name)
                    if isinstance(payload, dict) and "BlastOutput2" in payload:
                        payload_objects.append(payload)

            if not payload_objects:
                if manifest is not None:
                    raise ValueError(
                        "BLAST JSON2 archive manifest did not point to any payload JSON files."
                    )
                raise ValueError("BLAST JSON2 archive did not contain a `BlastOutput2` payload.")

            merged_payload = _merge_blast_payloads(payload_objects)
            return merged_payload, json.dumps(merged_payload)

    raw_text = response.text
    try:
        return response.json(), raw_text
    except ValueError as exc:
        raise ValueError("BLAST JSON2 response was not valid JSON.") from exc


def _fetch_result_ready(
    session: requests.Session,
    throttle: RequestThrottle,
    rid: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    result_format = config["result_format"]
    params: dict[str, Any] = {
        "CMD": "Get",
        "RID": rid,
    }
    if config["tool"]:
        params["tool"] = config["tool"]
    if config["email"]:
        params["email"] = config["email"]

    if result_format == "json2":
        params["FORMAT_TYPE"] = "JSON2"
        response = throttle.request(session, "GET", params=params, timeout=60)
        raw_output_path = None
        try:
            data, raw_json_text = _extract_json2_payload(response)
        except ValueError as exc:
            if config["save_raw"]:
                raw_output_path = _save_raw_output(
                    rid=rid,
                    result_format=result_format,
                    raw_output=response.text,
                    raw_output_path=config["raw_output_path"],
                )
                raise ValueError(f"{exc} Raw response saved to {raw_output_path}.") from exc
            raise

        if config["save_raw"]:
            raw_output_path = _save_raw_output(
                rid=rid,
                result_format=result_format,
                raw_output=raw_json_text,
                raw_output_path=config["raw_output_path"],
            )

        summary = _summarize_json2_payload(
            data,
            max_queries=config["max_queries"],
            max_hits=config["max_hits"],
        )

        return {
            "ok": True,
            "source": "ncbi-blast",
            "action": "fetch",
            "rid": rid,
            "status": "READY",
            "has_hits": summary["has_hits"],
            "result_format": result_format,
            "query_count_returned": summary["query_count_returned"],
            "query_count_available": summary["query_count_available"],
            "query_summaries_truncated": summary["query_summaries_truncated"],
            "query_summaries": summary["query_summaries"],
            "raw_output_path": raw_output_path,
            "warnings": [],
        }

    params["FORMAT_TYPE"] = "Text"
    params["DESCRIPTIONS"] = config["descriptions"]
    params["ALIGNMENTS"] = config["alignments"]
    response = throttle.request(session, "GET", params=params, timeout=60)
    text = response.text

    raw_output_path = None
    if config["save_raw"]:
        raw_output_path = _save_raw_output(
            rid=rid,
            result_format=result_format,
            raw_output=text,
            raw_output_path=config["raw_output_path"],
        )
        return {
            "ok": True,
            "source": "ncbi-blast",
            "action": "fetch",
            "rid": rid,
            "status": "READY",
            "has_hits": True,
            "result_format": result_format,
            "raw_output_path": raw_output_path,
            "warnings": [],
        }

    text_head = text[:800]
    return {
        "ok": True,
        "source": "ncbi-blast",
        "action": "fetch",
        "rid": rid,
        "status": "READY",
        "has_hits": True,
        "result_format": result_format,
        "text_head": text_head,
        "text_head_truncated": len(text_head) < len(text),
        "raw_output_path": raw_output_path,
        "warnings": [],
    }


def fetch_action(
    session: requests.Session,
    throttle: RequestThrottle,
    config: dict[str, Any],
    status_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = config["rid"]
    if status_payload is None:
        status_payload = get_search_info(
            session=session,
            throttle=throttle,
            rid=rid,
            tool=config["tool"],
            email=config["email"],
        )

    status = status_payload["status"]
    has_hits = status_payload["has_hits"]

    if status == "WAITING":
        return {
            "ok": True,
            "source": "ncbi-blast",
            "action": "fetch",
            "rid": rid,
            "status": status,
            "has_hits": has_hits,
            "result_format": config["result_format"],
            "raw_output_path": None,
            "warnings": [],
        }

    if status == "FAILED":
        return error("blast_failed", f"BLAST job {rid} reported FAILED.")
    if status == "UNKNOWN":
        return error("blast_unknown", f"BLAST job {rid} reported UNKNOWN or expired.")
    if not has_hits:
        return {
            "ok": True,
            "source": "ncbi-blast",
            "action": "fetch",
            "rid": rid,
            "status": status,
            "has_hits": False,
            "result_format": config["result_format"],
            "raw_output_path": None,
            "warnings": [],
        }

    return _fetch_result_ready(session=session, throttle=throttle, rid=rid, config=config)


def run_action(
    session: requests.Session,
    throttle: RequestThrottle,
    config: dict[str, Any],
    sleep_fn: Callable[[float], None] = time.sleep,
    clock_fn: Callable[[], float] = time.time,
) -> dict[str, Any]:
    submit_payload = submit_search(session=session, throttle=throttle, config=config)
    rid = submit_payload["rid"]
    rtoe_seconds = submit_payload["rtoe_seconds"]
    deadline = clock_fn() + config["wait_timeout_sec"]

    initial_wait = max(rtoe_seconds, MIN_REQUEST_INTERVAL_SEC)
    now = clock_fn()
    if now + initial_wait > deadline:
        return {
            "ok": True,
            "source": "ncbi-blast",
            "action": "run",
            "rid": rid,
            "rtoe_seconds": rtoe_seconds,
            "status": "WAITING",
            "has_hits": False,
            "result_format": config["result_format"],
            "raw_output_path": None,
            "warnings": [],
        }
    sleep_fn(initial_wait)

    while True:
        status_payload = get_search_info(
            session=session,
            throttle=throttle,
            rid=rid,
            tool=config["tool"],
            email=config["email"],
        )
        status = status_payload["status"]
        has_hits = status_payload["has_hits"]

        if status == "READY":
            if not has_hits:
                return {
                    "ok": True,
                    "source": "ncbi-blast",
                    "action": "run",
                    "rid": rid,
                    "rtoe_seconds": rtoe_seconds,
                    "status": status,
                    "has_hits": False,
                    "result_format": config["result_format"],
                    "raw_output_path": None,
                    "warnings": [],
                }

            fetch_config = dict(config)
            fetch_config["rid"] = rid
            fetch_payload = fetch_action(
                session=session,
                throttle=throttle,
                config=fetch_config,
                status_payload=status_payload,
            )
            if fetch_payload.get("ok"):
                fetch_payload["action"] = "run"
                fetch_payload["rtoe_seconds"] = rtoe_seconds
            return fetch_payload

        if status == "FAILED":
            return error("blast_failed", f"BLAST job {rid} reported FAILED.")
        if status == "UNKNOWN":
            return error("blast_unknown", f"BLAST job {rid} reported UNKNOWN or expired.")

        remaining = deadline - clock_fn()
        if remaining <= MIN_POLL_INTERVAL_SEC:
            return {
                "ok": True,
                "source": "ncbi-blast",
                "action": "run",
                "rid": rid,
                "rtoe_seconds": rtoe_seconds,
                "status": "WAITING",
                "has_hits": False,
                "result_format": config["result_format"],
                "raw_output_path": None,
                "warnings": [],
            }
        sleep_fn(MIN_POLL_INTERVAL_SEC)


def execute(
    payload: Any,
    *,
    session: requests.Session | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    clock_fn: Callable[[], float] = time.time,
) -> dict[str, Any]:
    if requests is None:
        return error(
            "missing_dependency",
            f"`requests` is required to run this script: {REQUESTS_IMPORT_ERROR}",
        )

    config = parse_input(payload)
    local_session = session or make_session(config["tool"], config["email"])
    throttle = RequestThrottle(sleep_fn=sleep_fn, clock_fn=clock_fn)

    try:
        if config["action"] == "submit":
            return submit_search(session=local_session, throttle=throttle, config=config)
        if config["action"] == "status":
            return get_search_info(
                session=local_session,
                throttle=throttle,
                rid=config["rid"],
                tool=config["tool"],
                email=config["email"],
            )
        if config["action"] == "fetch":
            return fetch_action(session=local_session, throttle=throttle, config=config)
        return run_action(
            session=local_session,
            throttle=throttle,
            config=config,
            sleep_fn=sleep_fn,
            clock_fn=clock_fn,
        )
    except ValueError as exc:
        return error("invalid_response", str(exc))
    except requests.RequestException as exc:
        return error("network_error", f"BLAST request failed: {exc}")
    finally:
        if session is None:
            local_session.close()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps(error("invalid_json", f"Could not parse JSON input: {exc}")))
        return 2

    try:
        output = execute(payload)
    except ValueError as exc:
        output = error("invalid_input", str(exc))
        exit_code = 2
    else:
        if output.get("ok"):
            exit_code = 0
        elif output.get("error", {}).get("code") in {"invalid_json", "invalid_input"}:
            exit_code = 2
        else:
            exit_code = 1

    sys.stdout.write(json.dumps(output))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
