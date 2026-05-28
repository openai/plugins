#!/usr/bin/env python3
"""Plugin auth manager — JSON wrapper around the mixpanel_headless auth namespaces.

Subcommands map 1:1 to ``mp account / project / workspace / target /
session / bridge`` per
``specs/042-auth-architecture-redesign/contracts/plugin-auth-manager.md``.
Every response carries ``schema_version: 1`` and a discriminated
``state`` (``ok`` | ``needs_account`` | ``needs_project`` | ``error``).
Errors emit JSON to stdout (exit 0) so the slash command can ``json.loads``
unconditionally.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from typing import Any

from mixpanel_headless import Workspace, accounts, targets
from mixpanel_headless import session as sess
from mixpanel_headless._internal.auth.bridge import (
    default_bridge_search_paths,
    load_bridge,
)
from mixpanel_headless._internal.auth.resolver import (
    resolve_account_axis,
    resolve_session,
)
from mixpanel_headless._internal.config import ConfigManager
from mixpanel_headless.exceptions import AccountNotFoundError, ConfigError

# Error codes the user can act on (re-login, set env, run specific CLI cmd).
# The slash command renders precise hints when ``actionable=True``.
_ACTIONABLE_CODES = frozenset({"OAUTH_TOKEN_ERROR", "OAUTH_REFRESH_ERROR", "OAUTH_REFRESH_REVOKED", "NEEDS_ACCOUNT", "NEEDS_PROJECT"})  # noqa: E501  # fmt: skip

SCHEMA_VERSION = 1

# fmt: off
_ONBOARDING = [
    {"command": "mp login", "label": "Frictionless login (recommended)"},
    {"command": "mp account add team --type service_account --username '<service-account-username>' --region us", "label": "Service account (explicit add)"},  # noqa: E501
    {"command": "export MP_OAUTH_TOKEN=<bearer> MP_REGION=us MP_PROJECT_ID=<id>", "label": "Static bearer (CI)"},  # noqa: E501
]
_PROJECT_NEXT = [
    {"command": "mp project list", "label": "List accessible projects"},
    {"command": "mp project use <id>", "label": "Select a project"},
]
# fmt: on


def _emit(payload: dict[str, Any]) -> None:
    """Write ``payload`` as pretty-printed JSON to stdout."""
    print(json.dumps(payload, indent=2, default=str))


def _ok(**fields: Any) -> dict[str, Any]:
    """Return a baseline ``state="ok"`` response with ``fields`` merged in."""
    return {"schema_version": SCHEMA_VERSION, "state": "ok", **fields}


def _err(exc: BaseException, *, actionable: bool | None = None) -> dict[str, Any]:
    """Wrap ``exc`` as a contracted ``state="error"`` envelope (P3).

    Pulls structured context off ``MixpanelHeadlessError`` subclasses (``code``,
    ``details``) and preserves ``__cause__``. ``MP_VERBOSE=1`` adds a
    one-line traceback. ``actionable`` defaults to True for ``_ACTIONABLE_CODES``.
    """
    code = str(getattr(exc, "code", None) or type(exc).__name__)
    err: dict[str, Any] = {"code": code, "message": str(exc), "actionable": actionable if actionable is not None else code in _ACTIONABLE_CODES}  # noqa: E501  # fmt: skip
    details = getattr(exc, "details", None)
    if isinstance(details, dict) and details:
        err["details"] = details
    if exc.__cause__ is not None:
        err["cause"] = f"{type(exc.__cause__).__name__}: {exc.__cause__}"
    if os.environ.get("MP_VERBOSE", "").lower() in ("1", "true", "yes"):
        import traceback as _tb

        err["traceback"] = _tb.format_exception_only(type(exc), exc)[-1].strip()
    return {"schema_version": SCHEMA_VERSION, "state": "error", "error": err}


def _account_record(account: Any) -> dict[str, Any]:
    """Render an Account → contract record (P5 — name/type/region required)."""
    return {"name": account.name, "type": account.type, "region": account.region}


def _has_env_auth() -> bool:
    """Return True when env vars alone can resolve a session."""
    sa = ("MP_USERNAME", "MP_SECRET", "MP_PROJECT_ID", "MP_REGION")
    oauth = ("MP_OAUTH_TOKEN", "MP_PROJECT_ID", "MP_REGION")
    return all(os.environ.get(v) for v in sa) or all(os.environ.get(v) for v in oauth)


def _active_block(project_override: str | None = None) -> dict[str, Any]:
    """Read ``[active]`` and return the contract's ``active`` block (§ 4.3)."""
    cm = ConfigManager()
    active = cm.get_active()
    proj = project_override
    if proj is None and active.account:
        # Narrow catch: only "account missing" / "config malformed" map to
        # ``proj=None``. Any other exception reflects a real bug and bubbles up.
        try:
            proj = cm.get_account(active.account).default_project
        except (AccountNotFoundError, ConfigError):
            proj = None
    return {"account": active.account, "project": proj, "workspace": active.workspace}


def _do(fn: Callable[..., Any], *args: Any, project_override: str | None = None, **kwargs: Any) -> dict[str, Any]:  # noqa: E501  # fmt: skip
    """Run ``fn`` then emit the contract's ``active`` block per § 4.3."""
    fn(*args, **kwargs)
    return _ok(active=_active_block(project_override=project_override))


def _with_workspace(extractor: Callable[[Any], dict[str, Any]]) -> dict[str, Any]:
    """Open Workspace, run ``extractor(ws)``, close, and emit the result."""
    ws = Workspace()
    try:
        return extractor(ws)
    finally:
        ws.close()


def _cached_user(account_name: str) -> dict[str, Any] | None:
    """Return ``{id,email}`` from MeCache without fetching (FR-046)."""
    from mixpanel_headless._internal.me import MeCache

    me = MeCache(account_name=account_name).get()
    if me is None or me.user_id is None or me.user_email is None:
        return None
    return {"id": me.user_id, "email": me.user_email}


def cmd_session(_args: argparse.Namespace) -> dict[str, Any]:
    """Resolve the persisted session into a discriminated state response.

    Delegates to ``resolve_session()`` so bridge-only and env-only auth
    report ``state="ok"`` with the resolved axes (prior bug: bridge-only
    returned ``needs_account``; env-only returned ok with all-null axes).
    """
    cm = ConfigManager()
    bridge = load_bridge()
    try:
        session = resolve_session(config=cm, bridge=bridge)
    except ConfigError:
        # Two-pass: account-axis only — distinguishes needs_account from needs_project.
        account = resolve_account_axis(explicit=None, target_account_name=None, bridge=bridge, config=cm)  # noqa: E501  # fmt: skip
        if account is None:
            return {"schema_version": SCHEMA_VERSION, "state": "needs_account", "next": _ONBOARDING}  # noqa: E501  # fmt: skip
        return {"schema_version": SCHEMA_VERSION, "state": "needs_project", "account": _account_record(account), "next": _PROJECT_NEXT}  # noqa: E501  # fmt: skip

    ws_id = session.workspace.id if session.workspace is not None else None
    has_env_account = _has_env_auth()
    src_account = "env" if has_env_account else ("bridge" if bridge is not None and bridge.account.name == session.account.name else "config")  # noqa: E501  # fmt: skip
    src_project = "env" if os.environ.get("MP_PROJECT_ID") else ("bridge" if bridge is not None and bridge.project == session.project.id else "config")  # noqa: E501  # fmt: skip
    if ws_id is None:
        src_workspace = "unset"
    elif os.environ.get("MP_WORKSPACE_ID"):
        src_workspace = "env"
    elif bridge is not None and bridge.workspace == ws_id:
        src_workspace = "bridge"
    else:
        src_workspace = "config"
    return _ok(
        account=_account_record(session.account),
        project={"id": session.project.id},
        workspace={"id": ws_id} if ws_id is not None else None,
        user=_cached_user(session.account.name),
        source={
            "account": src_account,
            "project": src_project,
            "workspace": src_workspace,
        },  # noqa: E501  # fmt: skip
    )


def cmd_account_list(_args: argparse.Namespace) -> dict[str, Any]:
    """List configured accounts; empty config also includes onboarding hints."""
    items = [s.model_dump(mode="json") for s in accounts.list()]
    payload = _ok(items=items)
    if not items:
        payload["next"] = _ONBOARDING
    return payload


def cmd_account_add(args: argparse.Namespace) -> dict[str, Any]:
    """Add a new account from a JSON record on stdin (per § 4.1)."""
    if not args.from_stdin:
        raise SystemExit("auth_manager.py: account add requires --from-stdin (security: never pass secrets on the command line)")  # noqa: E501  # fmt: skip
    r = json.loads(sys.stdin.read())
    summary = accounts.add(r["name"], type=r["type"], region=r["region"], default_project=r.get("default_project"), username=r.get("username"), secret=r.get("secret"), token=r.get("token"), token_env=r.get("token_env"))  # noqa: E501  # fmt: skip
    return _ok(added=summary.model_dump(mode="json"))


def cmd_account_login(args: argparse.Namespace) -> dict[str, Any]:
    """Run the OAuth PKCE flow for an oauth_browser account (per § 4.4)."""
    result = accounts.login(args.name)
    user = result.user.model_dump(mode="json") if result.user else None
    expires = result.expires_at.isoformat() if result.expires_at else None
    return _ok(logged_in_as={"name": result.account_name, "user": user, "expires_at": expires})  # noqa: E501  # fmt: skip


def cmd_account_test(args: argparse.Namespace) -> dict[str, Any]:
    """Probe ``/me`` for an account; never raises — captures errors in result."""
    return _ok(result=accounts.test(args.name).model_dump(mode="json"))


def cmd_project_list(_args: argparse.Namespace) -> dict[str, Any]:
    """Enumerate accessible projects via the live ``/me`` API."""

    def _extract(ws: Any) -> dict[str, Any]:
        active_id = ws.session.project.id
        return _ok(items=[{"id": p.id, "name": p.name, "organization_id": p.organization_id, "is_active": p.id == active_id} for p in ws.projects()])  # noqa: E501  # fmt: skip

    return _with_workspace(_extract)


def cmd_workspace_list(_args: argparse.Namespace) -> dict[str, Any]:
    """List workspaces for the active project via ``/me``."""

    def _extract(ws: Any) -> dict[str, Any]:
        project = {"id": ws.session.project.id, "name": ws.session.project.name}
        return _ok(project=project, items=[{"id": w.id, "name": w.name, "is_default": w.is_default, "is_active": w.id == ws.session.workspace_id} for w in ws.workspaces()])  # noqa: E501  # fmt: skip

    return _with_workspace(_extract)


def cmd_target_add(args: argparse.Namespace) -> dict[str, Any]:
    """Add a new target block referencing an existing account."""
    workspace = int(args.workspace) if args.workspace else None
    target = targets.add(args.name, account=args.account, project=args.project, workspace=workspace)  # noqa: E501  # fmt: skip
    return _ok(added=target.model_dump(mode="json"))


def cmd_bridge_status(_args: argparse.Namespace) -> dict[str, Any]:
    """Report bridge file presence plus parsed metadata."""
    bridge = load_bridge()
    if bridge is None:
        return _ok(bridge=None)
    candidates = ([os.environ["MP_AUTH_FILE"]] if os.environ.get("MP_AUTH_FILE") else []) + [str(p) for p in default_bridge_search_paths()]  # noqa: E501  # fmt: skip
    path = next((p for p in candidates if os.path.exists(p)), None)
    return _ok(bridge={"path": path, "version": bridge.version, "account": _account_record(bridge.account), "project": bridge.project, "workspace": bridge.workspace, "headers": dict(bridge.headers)})  # noqa: E501  # fmt: skip


def _target_use(args: argparse.Namespace) -> dict[str, Any]:
    """Apply target then emit active block with the target's project pin."""
    target = targets.show(args.name)
    return _do(targets.use, args.name, project_override=target.project)


_Handler = Callable[[argparse.Namespace], dict[str, Any]]
_DISPATCH: dict[tuple[str, str | None], _Handler] = {
    ("session", None): cmd_session,
    ("account", "list"): cmd_account_list,
    ("account", "add"): cmd_account_add,
    ("account", "use"): lambda a: _do(accounts.use, a.name),
    ("account", "login"): cmd_account_login,
    ("account", "test"): cmd_account_test,
    ("project", "list"): cmd_project_list,
    ("project", "use"): lambda a: _do(
        sess.use, project=a.project_id, project_override=a.project_id
    ),  # noqa: E501  # fmt: skip
    ("workspace", "list"): cmd_workspace_list,
    ("workspace", "use"): lambda a: _do(sess.use, workspace=int(a.workspace_id)),
    ("target", "list"): lambda _a: _ok(
        items=[t.model_dump(mode="json") for t in targets.list()]
    ),  # noqa: E501  # fmt: skip
    ("target", "add"): cmd_target_add,
    ("target", "use"): _target_use,
    ("bridge", "status"): cmd_bridge_status,
}


def _build_parser() -> argparse.ArgumentParser:
    """Construct the two-level argparse tree (group → action)."""
    parser = argparse.ArgumentParser(prog="auth_manager.py")
    sub = parser.add_subparsers(dest="group", required=True)
    sub.add_parser("session")
    acct = sub.add_parser("account").add_subparsers(dest="action", required=True)
    acct.add_parser("list")
    acct.add_parser("add").add_argument("--from-stdin", action="store_true")
    for verb in ("use", "login", "test"):
        acct.add_parser(verb).add_argument("name")
    proj = sub.add_parser("project").add_subparsers(dest="action", required=True)
    proj.add_parser("list")
    proj.add_parser("use").add_argument("project_id")
    wsp = sub.add_parser("workspace").add_subparsers(dest="action", required=True)
    wsp.add_parser("list")
    wsp.add_parser("use").add_argument("workspace_id")
    tgt = sub.add_parser("target").add_subparsers(dest="action", required=True)
    tgt.add_parser("list")
    tgt_add = tgt.add_parser("add")
    tgt_add.add_argument("name")
    tgt_add.add_argument("--account", required=True)
    tgt_add.add_argument("--project", required=True)
    tgt_add.add_argument("--workspace")
    tgt.add_parser("use").add_argument("name")
    sub.add_parser("bridge").add_subparsers(dest="action", required=True).add_parser("status")  # noqa: E501  # fmt: skip
    return parser


def main() -> None:
    """Parse args, dispatch, emit JSON; never let exceptions escape."""
    args = _build_parser().parse_args()
    handler = _DISPATCH.get((args.group, getattr(args, "action", None)))
    if handler is None:  # pragma: no cover — argparse already enforces choices
        _emit(_err(SystemExit(f"Unknown subcommand: {args.group}")))
        return
    try:
        _emit(handler(args))
    except Exception as exc:  # noqa: BLE001 — exit-0 contract
        _emit(_err(exc))


if __name__ == "__main__":
    main()
