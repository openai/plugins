#!/usr/bin/env python3

"""Safely render and refresh real Sales dashboards without hosting or external writes."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

PLUGIN_DIRECTORY = Path(__file__).resolve().parent.parent
TEMPLATE_DIRECTORY = PLUGIN_DIRECTORY / "skills" / "demo-exec-and-seller-dash" / "assets"
PERSONA_TEMPLATES = {
    "seller": TEMPLATE_DIRECTORY / "account-priority-workspace.template.html",
    "leadership": TEMPLATE_DIRECTORY / "sales-leadership-dashboard.template.html",
}
PERSONA_PLACEHOLDERS = {
    "seller": "__PRIORITIZE_ACCOUNTS_DATA_JSON__",
    "leadership": "__LEADERSHIP_DATA_JSON__",
}
PERSONA_ASSIGNMENTS = {
    "seller": "const payload = ",
    "leadership": "window.__LEADERSHIP_DATA__ = ",
}
DASHBOARD_MODES = ("real", "placeholder", "representative")
PLACEHOLDER_EMPTY_FIELDS = {
    "accountDetails",
    "accountOverview",
    "connectedSources",
    "decisions",
    "divisionTeams",
    "forecast",
    "metrics",
    "paused",
    "quarter",
    "reporting",
    "scope",
    "seller",
    "sellerOverview",
    "signals",
    "source",
    "sourceCoverage",
    "topDeals",
    "watch",
    "workNow",
}
PLACEHOLDER_ALLOWED_FIELDS = PLACEHOLDER_EMPTY_FIELDS | {
    "codexPet",
    "company",
    "dashboardIdentity",
    "dashboardLabel",
    "dashboardMode",
    "disclosure",
    "evidenceGaps",
    "generatedAt",
    "title",
}
DISCLOSURE_PATTERN = re.compile(
    r'(<aside\b(?=[^>]*\bdata-sales-dashboard-disclosure="([^"]+)")[^>]*>)'
    r"(.*?)"
    r"(</aside>)",
    re.DOTALL,
)
PLACEHOLDER_EMPTY_STATE_SCRIPT = """
    <script data-sales-dashboard-empty-state="true">
      (() => {
        const notice = document.querySelector('[data-sales-dashboard-disclosure="placeholder"]');
        const set = (id, value) => {
          const node = document.getElementById(id);
          if (node) node.textContent = value;
        };
        const viewer = notice ? notice.dataset.salesDashboardViewer : "";
        set("greeting", viewer + " · Dashboard placeholder");
        set("viewer-persona", viewer + " · Dashboard placeholder");
        set("page-subtitle", "No verified customer, account, or pipeline data is available.");
        set("overview-kicker", "Sales dashboard placeholder · No verified data");
        set("overview-summary", "No verified account, team, or forecast data is available.");
        set("forecast-briefing-copy", "No verified forecast or account data is available.");
        set("account-briefing-copy", "No verified account or opportunity data is available.");
        set("reporting-snapshot", "No verified reporting snapshot");
        set("quarter-progress", "Unavailable");
        set("accounts-summary", "Account data unavailable");
        set("attention-list", "Account follow-up data unavailable.");
        set("book-caption", "Account data unavailable");
        set("renewal-caption", "Follow-up data unavailable");
        set("expansion-caption", "Meeting data unavailable");
        const unavailableMetrics = [
          "book-value-metric",
          "renewal-value-metric",
          "expansion-value-metric",
          "source-count-metric"
        ];
        for (const id of unavailableMetrics) set(id, "—");
        for (const id of ["attention-count", "opportunities-count"])
          set(id, "Unavailable");
        for (const id of ["forecast-evidence-count", "account-evidence-count"])
          set(id, "No verified source data");
      })();
    </script>
"""


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _is_macos_system_alias(path: Path) -> bool:
    """Allow only macOS's fixed root aliases, never user-created redirecting links."""

    if sys.platform != "darwin":
        return False
    alias = Path(os.path.abspath(path))
    expected = {
        Path("/tmp"): Path("/private/tmp"),
        Path("/var"): Path("/private/var"),
        Path("/etc"): Path("/private/etc"),
    }.get(alias)
    return expected is not None and path.resolve(strict=True) == expected


def _validate_codex_pet(payload: dict[str, object]) -> None:
    """Accept only an explicitly supplied, renderable Codex pet."""

    if "codexPet" not in payload:
        return
    pet = payload["codexPet"]
    if not isinstance(pet, dict) or set(pet) != {"name", "imageUrl"}:
        raise ValueError("A Codex pet needs exactly a name and imageUrl.")
    name = _text(pet.get("name"))
    image_url = _text(pet.get("imageUrl"))
    if not name or not re.match(
        r"^data:image/(?:png|jpeg|gif|webp);base64,", image_url, re.IGNORECASE
    ):
        raise ValueError("A Codex pet needs a nonempty name and safe renderable image URL.")


def _dashboard_identity(
    persona: str, payload: dict[str, object]
) -> tuple[tuple[str, ...], str, str]:
    identity = payload.get("dashboardIdentity")
    if not isinstance(identity, dict) or identity.get("persona") != persona:
        raise ValueError("A dashboard fallback needs its exact viewer-owned persona identity.")
    if set(identity) - {"owner", "persona", "scope"}:
        raise ValueError("A dashboard viewer identity cannot contain customer or sales data.")
    owner = identity.get("owner")
    if not isinstance(owner, dict) or not _text(owner.get("name")):
        raise ValueError("A dashboard fallback needs its verified requesting viewer's name.")
    if set(owner) - {"id", "name"}:
        raise ValueError("A dashboard viewer identity cannot claim an unverified sales role.")
    if "id" in owner and not _text(owner.get("id")):
        raise ValueError("A supplied dashboard viewer identifier must be nonempty text.")
    scope = _text(identity.get("scope"))
    if not scope:
        raise ValueError("A dashboard fallback needs a stable viewer-owned project scope.")
    return (scope,), _text(owner.get("id")), _text(owner.get("name"))


def _validated_placeholder(persona: str, payload: dict[str, object]) -> dict[str, object]:
    _dashboard_identity(persona, payload)
    unknown_fields = set(payload) - PLACEHOLDER_ALLOWED_FIELDS
    if unknown_fields:
        raise ValueError("An empty placeholder cannot include customer, sales, or forecast data.")
    for key in PLACEHOLDER_EMPTY_FIELDS:
        if key not in payload:
            continue
        value = payload[key]
        if not isinstance(value, (dict, list)) or value:
            raise ValueError(f"An empty placeholder cannot contain populated {key} data.")
    for key in ("generatedAt", "title"):
        if key in payload and not _text(payload[key]):
            raise ValueError("Placeholder metadata must contain only nonempty text.")

    company = payload.get("company")
    if company is not None and (
        not isinstance(company, dict)
        or set(company) - {"name"}
        or "name" in company
        and not _text(company.get("name"))
    ):
        raise ValueError("An empty placeholder cannot claim a sales owner, leader, or team.")
    disclosure = payload.get("disclosure")
    if disclosure is not None and (
        not isinstance(disclosure, dict)
        or set(disclosure) - {"isFictional", "message"}
        or "isFictional" in disclosure
        and disclosure.get("isFictional") is not False
        or "message" in disclosure
        and not _text(disclosure.get("message"))
    ):
        raise ValueError("A placeholder disclosure must only describe its empty state.")
    gaps = payload.get("evidenceGaps", [])
    if not isinstance(gaps, list) or any(not _text(gap) for gap in gaps):
        raise ValueError("Placeholder evidence gaps must contain only truthful text.")
    return payload


def _validated_payload(persona: str, payload: object, mode: str = "real") -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("A real dashboard payload must be a JSON object.")
    if mode not in DASHBOARD_MODES:
        raise ValueError(f"Unknown dashboard mode: {mode}")
    _validate_codex_pet(payload)
    declared_mode = payload.get("dashboardMode", "real")
    if declared_mode != mode:
        raise ValueError("The requested dashboard mode must exactly match its payload marker.")
    if mode == "real" and ("dashboardIdentity" in payload or "dashboardLabel" in payload):
        raise ValueError("A real dashboard cannot silently claim a fallback viewer or disclosure.")
    if mode != "real":
        label = _text(payload.get("dashboardLabel"))
        if not label or mode not in label.casefold():
            raise ValueError(f"A {mode} dashboard needs an explicit, truthful visible label.")

    demo = payload.get("demo")
    disclosure = payload.get("disclosure")
    source = payload.get("source")
    if (
        isinstance(demo, dict)
        and _text(demo.get("mode")).casefold() == "fictional"
        or isinstance(disclosure, dict)
        and disclosure.get("isFictional") is True
        or isinstance(source, dict)
        and re.search(r"\bfictional\b", _text(source.get("label")), re.IGNORECASE)
    ):
        raise ValueError("Fictional demo payloads cannot be used for a real dashboard.")

    if mode == "placeholder":
        return _validated_placeholder(persona, payload)
    if mode == "representative":
        _dashboard_identity(persona, payload)

    source_key = "connectedSources" if persona == "seller" else "sourceCoverage"
    supplied_sources = payload.get(source_key, [])
    if not isinstance(supplied_sources, list) or not supplied_sources:
        raise ValueError(f"{source_key} must contain at least one verified source.")
    for source_record in supplied_sources:
        if not isinstance(source_record, dict) or source_record.get("verified") is not True:
            raise ValueError(f"Every real {source_key} entry must declare verified: true.")
        if not _text(source_record.get("name")) and not _text(source_record.get("label")):
            raise ValueError("A verified dashboard source needs a nonempty name.")
        if any(
            re.search(r"\b(?:demo|fictional|fixture|mock|sample|simulated)\b", _text(value), re.I)
            for value in (source_record.get("name"), source_record.get("label"))
        ):
            raise ValueError("A verified dashboard source cannot be fictional or simulated.")
        if re.search(
            r"\b(?:disconnected|unavailable|not connected)\b",
            _text(source_record.get("status")),
            re.I,
        ):
            raise ValueError("A verified dashboard source must be available.")

    if persona == "seller":
        seller = payload.get("seller")
        if not isinstance(seller, dict) or not _text(seller.get("name")):
            raise ValueError("A real seller dashboard needs a verified account owner.")
        scope = payload.get("scope")
        if (
            not isinstance(scope, dict)
            or not _text(scope.get("sourceOfTruth"))
            or not _text(scope.get("accountSet"))
        ):
            raise ValueError("A real seller dashboard needs a verified account scope and source.")

        account_names: set[str] = set()
        for group in ("workNow", "watch", "paused"):
            accounts = payload.get(group)
            if not isinstance(accounts, list):
                raise ValueError(f"The seller dashboard needs a {group} account array.")
            for account in accounts:
                if not isinstance(account, dict) or not _text(account.get("account")):
                    raise ValueError("Every real seller account needs a verified account name.")
                account_name = _text(account["account"]).casefold()
                if account_name in account_names:
                    raise ValueError("Every owned account must appear exactly once.")
                if _text(account.get("owner")).casefold() != _text(seller["name"]).casefold():
                    raise ValueError("Seller accounts must match their verified dashboard owner.")
                account_names.add(account_name)
    else:
        company = payload.get("company")
        if not isinstance(company, dict) or not _text(company.get("name")):
            raise ValueError("A real leadership dashboard needs a verified organization.")
        if not _text(company.get("division")):
            raise ValueError("A real leadership dashboard needs a verified division or team scope.")
        leader = company.get("divisionLead")
        if not isinstance(leader, dict) or not (
            _text(leader.get("id")) or _text(leader.get("name"))
        ):
            raise ValueError("A real leadership dashboard needs a verified owner.")
        if not isinstance(payload.get("forecast"), dict):
            raise ValueError("A real leadership dashboard needs its sourced forecast context.")

    if mode == "representative":
        _, represented_id, represented_name = _identity_fields(persona, payload)
        _, viewer_id, viewer_name = _dashboard_identity(persona, payload)
        if not represented_name:
            raise ValueError(
                "A representative dashboard must identify its actual represented owner."
            )
        if (
            represented_name.casefold() == viewer_name.casefold()
            or represented_id
            and viewer_id
            and represented_id.casefold() == viewer_id.casefold()
        ):
            raise ValueError("A representative dashboard cannot impersonate its requesting viewer.")
    return payload


def _identity_fields(persona: str, payload: dict[str, object]) -> tuple[tuple[str, ...], str, str]:
    if payload.get("dashboardMode") == "placeholder":
        return _dashboard_identity(persona, payload)
    if persona == "seller":
        seller = payload.get("seller")
        scope = payload.get("scope")
        if not isinstance(seller, dict) or not isinstance(scope, dict):
            return (), "", ""
        return (
            (_text(scope.get("accountSet")),),
            _text(seller.get("id")),
            _text(seller.get("name")),
        )

    company = payload.get("company")
    if not isinstance(company, dict):
        return (), "", ""
    leader = company.get("divisionLead")
    if not isinstance(leader, dict):
        return (), "", ""
    return (
        (_text(company.get("name")), _text(company.get("division"))),
        _text(leader.get("id")),
        _text(leader.get("name")),
    )


def _same_identity(
    existing: tuple[tuple[str, ...], str, str],
    replacement: tuple[tuple[str, ...], str, str],
) -> bool:
    existing_scope, existing_owner_id, existing_owner_name = existing
    replacement_scope, replacement_owner_id, replacement_owner_name = replacement
    if existing_owner_id and replacement_owner_id:
        same_owner = existing_owner_id.casefold() == replacement_owner_id.casefold()
    else:
        same_owner = bool(
            existing_owner_name
            and replacement_owner_name
            and existing_owner_name.casefold() == replacement_owner_name.casefold()
        )
    return bool(
        same_owner
        and existing_scope
        and len(existing_scope) == len(replacement_scope)
        and all((*existing_scope, *replacement_scope))
        and all(
            previous.casefold() == current.casefold()
            for previous, current in zip(existing_scope, replacement_scope, strict=True)
        )
    )


def _refresh_existing_html(
    persona: str,
    existing_html: str,
    payload: dict[str, object],
    serialized: str,
    mode: str,
) -> str:
    assignment = PERSONA_ASSIGNMENTS[persona]
    matches = list(re.finditer(r"(?m)^[ \t]*" + re.escape(assignment), existing_html))
    if len(matches) != 1:
        raise ValueError("Existing project does not contain exactly one matching dashboard.")

    value_start = matches[0].end()
    whitespace = len(existing_html[value_start:]) - len(existing_html[value_start:].lstrip())
    value_start += whitespace
    try:
        existing_payload, consumed = json.JSONDecoder().raw_decode(existing_html[value_start:])
    except json.JSONDecodeError as error:
        raise ValueError("Existing dashboard payload cannot be refreshed safely.") from error
    try:
        if not isinstance(existing_payload, dict):
            raise ValueError("Existing dashboard payload must be a JSON object.")
        existing_mode = existing_payload.get("dashboardMode", "real")
        if not isinstance(existing_mode, str):
            raise ValueError("Existing dashboard mode must be explicit and valid.")
        existing_payload = _validated_payload(persona, existing_payload, existing_mode)
    except ValueError as error:
        raise ValueError(
            "Existing dashboard identity and grounded evidence cannot be verified."
        ) from error

    if (
        existing_mode != mode
        or not _same_identity(
            _identity_fields(persona, existing_payload), _identity_fields(persona, payload)
        )
        or mode == "representative"
        and not _same_identity(
            _dashboard_identity(persona, existing_payload), _dashboard_identity(persona, payload)
        )
    ):
        raise ValueError(
            "Existing dashboard belongs to a different mode, owner, persona, or scope."
        )
    if mode != "real":
        _verified_mode_disclosure(
            existing_html, mode, expected_viewer=_dashboard_identity(persona, existing_payload)[2]
        )

    return existing_html[:value_start] + serialized + existing_html[value_start + consumed :]


def _mode_disclosure(persona: str, payload: dict[str, object], mode: str) -> tuple[str, str]:
    label = _text(payload.get("dashboardLabel"))
    _, _, viewer = _dashboard_identity(persona, payload)
    if mode == "placeholder":
        message = (
            f"{label} — Empty placeholder; no verified customer, account, team, or forecast data."
        )
    else:
        _, _, represented_owner = _identity_fields(persona, payload)
        message = (
            f"{label} — Verified data for {represented_owner}; requested by {viewer}. "
            "Not the requester's own sales dashboard."
        )
    return html.escape(message), html.escape(viewer, quote=True)


def _verified_mode_disclosure(
    rendered: str, mode: str, *, expected_viewer: str | None = None
) -> re.Match[str]:
    matches = list(DISCLOSURE_PATTERN.finditer(rendered))
    if len(matches) != 1 or matches[0].group(2) != mode:
        raise ValueError("Existing fallback dashboard is missing its truthful visible label.")
    opening = matches[0].group(1)
    viewer_matches = re.findall(r'\bdata-sales-dashboard-viewer="([^"]*)"', opening)
    if len(viewer_matches) != 1:
        raise ValueError("A dashboard fallback disclosure must identify its requesting viewer.")
    if expected_viewer is not None and html.unescape(viewer_matches[0]) != expected_viewer:
        raise ValueError("Existing dashboard disclosure belongs to a different requesting viewer.")
    if (
        re.search(r"\s(?:hidden|inert)(?=[\s=>])", opening, re.I)
        or re.search(r"\baria-hidden\s*=\s*['\"]?true\b", opening, re.I)
        or re.search(
            r"\b(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))", opening, re.I
        )
    ):
        raise ValueError("A dashboard fallback disclosure must stay visibly displayed.")
    if mode == "placeholder" and (
        rendered.count('data-sales-dashboard-empty-state="true"') != 1
        or rendered.count(PLACEHOLDER_EMPTY_STATE_SCRIPT) != 1
    ):
        raise ValueError(
            "Existing placeholder is missing its verified truthful empty-state display."
        )
    return matches[0]


def _with_mode_disclosure(
    rendered: str, persona: str, payload: dict[str, object], mode: str, *, refresh: bool
) -> str:
    if mode == "real":
        return rendered
    disclosure, viewer = _mode_disclosure(persona, payload, mode)
    if refresh:
        match = _verified_mode_disclosure(rendered, mode)
        opening = re.sub(
            r'(\bdata-sales-dashboard-viewer=")[^"]*(")',
            lambda viewer_match: viewer_match.group(1) + viewer + viewer_match.group(2),
            match.group(1),
        )
        return (
            rendered[: match.start()]
            + opening
            + disclosure
            + match.group(4)
            + rendered[match.end() :]
        )
    if DISCLOSURE_PATTERN.search(rendered):
        raise ValueError("A dashboard template must not already contain a fallback disclosure.")
    body = re.search(r"<body(?:\s[^>]*)?>", rendered)
    if body is None:
        raise ValueError("A fallback dashboard template needs a visible document body.")
    banner = (
        f'\n    <aside data-sales-dashboard-disclosure="{mode}" '
        f'data-sales-dashboard-viewer="{viewer}" role="status" '
        'style="padding:14px 20px;background:#fff7ed;color:#7c2d12;'
        'border-bottom:1px solid #fdba74;font:600 14px/1.5 system-ui,sans-serif">'
        f"{disclosure}</aside>"
    )
    rendered = rendered[: body.end()] + banner + rendered[body.end() :]
    if mode == "placeholder":
        if "</body>" not in rendered:
            raise ValueError("A placeholder dashboard needs a complete document body.")
        rendered = rendered.replace("</body>", PLACEHOLDER_EMPTY_STATE_SCRIPT + "  </body>", 1)
    return rendered


def render_dashboard(
    persona: str, payload: dict[str, object], project_directory: Path, *, mode: str = "real"
) -> Path:
    """Embed a real payload in one stable project while preserving existing customizations."""

    if persona not in PERSONA_TEMPLATES:
        raise ValueError(f"Unknown dashboard persona: {persona}")
    validated = _validated_payload(persona, payload, mode)
    serialized = json.dumps(
        validated, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True
    ).replace("<", "\\u003c")

    requested_project = project_directory.expanduser()
    if not requested_project.is_absolute():
        requested_project = Path.cwd() / requested_project
    if any(
        component.is_symlink() and not _is_macos_system_alias(component)
        for component in (requested_project, *requested_project.parents)
    ):
        raise ValueError("A dashboard project path must not contain symbolic links.")
    resolved_project = requested_project.resolve()
    if resolved_project == PLUGIN_DIRECTORY or PLUGIN_DIRECTORY in resolved_project.parents:
        raise ValueError("Dashboard projects must be user-owned and outside the Sales plugin.")

    destination = resolved_project / "index.html"
    if destination.is_symlink():
        raise ValueError("A dashboard index must not be a symbolic link.")
    refresh = destination.exists()
    if refresh:
        rendered = _refresh_existing_html(
            persona, destination.read_text(encoding="utf-8"), validated, serialized, mode
        )
    else:
        template = PERSONA_TEMPLATES[persona].read_text(encoding="utf-8")
        placeholder = PERSONA_PLACEHOLDERS[persona]
        if template.count(placeholder) != 1:
            raise ValueError("The dashboard template must contain exactly one data placeholder.")
        rendered = template.replace(placeholder, serialized, 1)
    rendered = _with_mode_disclosure(rendered, persona, validated, mode, refresh=refresh)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a grounded, local-only Sales dashboard.")
    parser.add_argument("--persona", choices=sorted(PERSONA_TEMPLATES), required=True)
    parser.add_argument("--mode", choices=DASHBOARD_MODES, default="real")
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    arguments = parser.parse_args()
    payload = json.loads(arguments.payload.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("A real dashboard payload must be a JSON object.")
    print(render_dashboard(arguments.persona, payload, arguments.project_dir, mode=arguments.mode))


if __name__ == "__main__":
    main()
