#!/usr/bin/env python3

"""Start the canned Sales walkthrough from its existing canonical response copy."""

from __future__ import annotations

import argparse
import importlib.util
import json
import socket
import subprocess
import sys
import time
from datetime import date
from http.client import HTTPConnection, HTTPException
from pathlib import Path
from urllib.parse import urlsplit

RENDERER_SPEC = importlib.util.spec_from_file_location(
    "sales_demo_renderer", Path(__file__).resolve().with_name("render_demo_dashboard.py")
)
if RENDERER_SPEC is None or RENDERER_SPEC.loader is None:
    raise RuntimeError("The packaged Sales dashboard renderer could not be loaded.")
renderer = importlib.util.module_from_spec(RENDERER_SPEC)
RENDERER_SPEC.loader.exec_module(renderer)


FLOW_REFERENCE = renderer.SKILL_DIRECTORY / "references" / "demo-flow.md"
PREVIEW_CACHE = renderer.DEFAULT_OUTPUT_DIRECTORY / ".preview.json"
HOSTED_LEADERSHIP_URL = "https://meridian-sales-operating-views.openai.chatgpt.site/leadership"
HOSTED_SELLER_URL = "https://meridian-sales-operating-views.openai.chatgpt.site/seller"
STATE_HEADINGS = {
    "leadership": "### Step 1: leadership_dashboard",
    "account": "### Step 2: account_priority_view",
    "meeting": "### Step 3: meeting_followup",
    "complete": "### Step 4: salesforce_review_complete",
    "presentation": "### Branch: northstar_presentation_draft",
    "email": "### Branch: launch_reengagement_draft",
}


def normalize_preview_url(value: str | None) -> str | None:
    """Accept only a loopback HTTP preview and discard page-specific paths."""

    if not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        return None
    if parsed.port is None:
        return None
    return f"http://{parsed.hostname}:{parsed.port}"


def normalize_hosted_dashboard_url(value: str, expected_route: str) -> str:
    """Accept only the supplied HTTPS Site route, never a private loopback preview."""

    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or not parsed.hostname.endswith(".chatgpt.site")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path.rstrip("/") != expected_route
    ):
        raise ValueError(f"A verified hosted Sites URL ending in {expected_route} is required.")
    return value.rstrip("/")


def preview_is_ready(base_url: str | None) -> bool:
    """Verify both expected loopback artifacts without connector or browser discovery."""

    if not base_url:
        return False
    parsed = urlsplit(base_url)
    for route, expected in (
        ("/", b"Riley"),
        ("/leadership/", b"Revenue Leadership Command Center"),
    ):
        connection = HTTPConnection(parsed.hostname or "", parsed.port, timeout=0.4)
        try:
            connection.request("GET", route)
            response = connection.getresponse()
            if response.status != 200 or expected not in response.read(8192):
                return False
        except (HTTPException, OSError, TimeoutError, ValueError):
            return False
        finally:
            connection.close()
    return True


def cached_preview_url() -> str | None:
    """Return an existing ephemeral preview location, never conversation state."""

    try:
        cached = json.loads(PREVIEW_CACHE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(cached, dict):
        return None
    return normalize_preview_url(cached.get("base_url"))


def write_preview_cache(base_url: str) -> None:
    PREVIEW_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW_CACHE.write_text(json.dumps({"base_url": base_url}), encoding="utf-8")


def _stop_preview(process: subprocess.Popen[bytes]) -> None:
    """Reap only the server this invocation started, escalating if it ignores termination."""

    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=1)


def launch_preview(preferred_url: str | None = None, *, current_date: date | None = None) -> str:
    """Detach a loopback-only server and wait briefly for verified readiness."""

    preferred_port = urlsplit(preferred_url).port if preferred_url else None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        try:
            candidate.bind(("127.0.0.1", preferred_port or 0))
        except OSError:
            candidate.bind(("127.0.0.1", 0))
        port = candidate.getsockname()[1]

    process = subprocess.Popen(
        [
            sys.executable,
            str(Path(renderer.__file__).resolve()),
            "--dashboard",
            "both",
            "--serve",
            "--port",
            str(port),
            "--current-date",
            renderer.resolve_demo_date(current_date).isoformat(),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if preview_is_ready(base_url):
                write_preview_cache(base_url)
                return base_url
            if process.poll() is not None:
                raise RuntimeError(
                    "The loopback Sales demo server exited before its preview was ready."
                )
            time.sleep(0.05)
        raise RuntimeError(
            "The loopback Sales demo preview did not become ready within three seconds."
        )
    except BaseException:
        _stop_preview(process)
        raise


def ensure_preview(preferred_url: str | None, *, current_date: date | None = None) -> str:
    """Refresh the small generated artifacts and reuse a healthy loopback preview."""

    portfolio = renderer.load_portfolio()
    current_date = renderer.resolve_demo_date(current_date)
    renderer.render_dashboard(portfolio, current_date=current_date)
    renderer.render_leadership_dashboard(
        renderer.load_leadership_data(portfolio=portfolio), current_date=current_date
    )

    normalized_preference = normalize_preview_url(preferred_url)
    if normalized_preference:
        if preview_is_ready(normalized_preference):
            write_preview_cache(normalized_preference)
            return normalized_preference
        return launch_preview(normalized_preference, current_date=current_date)

    cached = cached_preview_url()
    if preview_is_ready(cached):
        assert cached is not None
        return cached
    return launch_preview(current_date=current_date)


def canonical_response(
    state: str,
    sites_available: bool,
    base_url: str | None,
    *,
    leadership_url: str | None = None,
    seller_url: str | None = None,
    current_date: date | None = None,
) -> str:
    """Extract the canonical response; keep legacy Sites arguments for compatibility."""

    flow = FLOW_REFERENCE.read_text(encoding="utf-8")
    heading = STATE_HEADINGS[state]
    if heading not in flow:
        raise ValueError(f"The canonical demo flow is missing {heading}.")
    section = flow.split(heading, maxsplit=1)[1]
    section = section.split("\n### ", maxsplit=1)[0]
    if "- **Final message:**" not in section:
        raise ValueError(f"The canonical {state} state has no prepared final response.")
    response = section.split("- **Final message:**", maxsplit=1)[1].lstrip()

    if state == "presentation":
        boundary = "\n- **Artifact link:**"
    elif state == "complete":
        boundary = "\n- **Workflow selection:**"
    else:
        boundary = "\n- **Reply `1`:**"
    if boundary not in response:
        raise ValueError(f"The canonical {state} state is missing its response boundary.")
    response = response.split(boundary, maxsplit=1)[0]

    if base_url is not None:
        leadership_url = f"{base_url}/leadership/"
        seller_url = f"{base_url}/"
    if leadership_url is None or seller_url is None:
        raise ValueError("Both leadership and seller dashboard URLs must be available.")
    response = response.replace(HOSTED_LEADERSHIP_URL, leadership_url)
    response = response.replace(HOSTED_SELLER_URL, seller_url)
    response = renderer._resolve_relative_dates(
        response, renderer.demo_relative_dates(current_date)
    )
    if "{{" in response:
        raise ValueError("The prepared demo response still contains unresolved dynamic values.")
    return response.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit a ready-to-send canned Sales demo response.")
    parser.add_argument("--step", choices=tuple(STATE_HEADINGS), default="leadership")
    parser.add_argument("--base-url", help="Current loopback browser URL, when already available.")
    parser.add_argument(
        "--current-date", type=date.fromisoformat, help="User-local date (YYYY-MM-DD)."
    )
    parser.add_argument("--timezone", help="User's IANA timezone when no date was supplied.")
    parser.add_argument(
        "--delivery-mode",
        choices=("development", "work"),
        help="Defaults to the published site unless a valid local preview URL was supplied.",
    )
    parser.add_argument("--leadership-url", default=HOSTED_LEADERSHIP_URL)
    parser.add_argument("--seller-url", default=HOSTED_SELLER_URL)
    parser.add_argument("--sites-available", action="store_true")
    options = parser.parse_args()
    try:
        current_date = renderer.resolve_demo_date(options.current_date, options.timezone)
    except ValueError as error:
        parser.error(str(error))
    delivery_mode = options.delivery_mode or (
        "development" if normalize_preview_url(options.base_url) else "work"
    )
    if delivery_mode == "work":
        if options.base_url:
            parser.error("Work-mode delivery requires hosted Sites URLs, not a local preview.")
        try:
            leadership_url = normalize_hosted_dashboard_url(options.leadership_url, "/leadership")
            seller_url = normalize_hosted_dashboard_url(options.seller_url, "/seller")
        except ValueError as error:
            parser.error(str(error))
        print(
            canonical_response(
                options.step,
                False,
                None,
                leadership_url=leadership_url,
                seller_url=seller_url,
                current_date=current_date,
            ),
            flush=True,
        )
        return

    base_url = ensure_preview(options.base_url, current_date=current_date)
    print(
        canonical_response(
            options.step, options.sites_available, base_url, current_date=current_date
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
