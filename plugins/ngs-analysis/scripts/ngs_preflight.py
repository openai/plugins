#!/usr/bin/env python3
"""Check NGS tool availability before suggesting or running installs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ngs_run_utils import command_path

DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "references" / "pipeline-registry.json"


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def executable_status(name: str) -> dict[str, Any]:
    resolved = command_path(name)
    return {"name": name, "present": resolved is not None, "path": resolved}


def module_status(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)
    return {"name": name, "present": spec is not None}


def executable_uses_docker(path: str | None) -> bool:
    if not path:
        return False
    candidate = Path(path)
    if not candidate.exists():
        return False
    try:
        head = candidate.read_text(encoding="utf-8", errors="ignore")[:2000]
    except OSError:
        return False
    return "docker run" in head


def run_probe(cmd: list[str], timeout: int = 30) -> dict[str, Any]:
    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"cmd": cmd, "present": False, "ok": False, "detail": "command not found"}
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "present": True, "ok": False, "detail": "timeout"}
    detail = (result.stdout or result.stderr).strip().splitlines()
    return {
        "cmd": cmd,
        "present": True,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "detail": detail[:5],
    }


def check_index(tool_name: str, tool: dict[str, Any], network_checks: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "tool": tool_name,
        "executables": [executable_status(item) for item in tool.get("executables", [])],
        "python_modules": [module_status(item) for item in tool.get("python_modules", [])],
        "network": [],
        "install": tool.get("install", {}),
        "notes": tool.get("notes"),
        "license": tool.get("license", "public_or_open"),
    }
    if tool_name == "bcl-convert":
        resolved = next((item["path"] for item in checks["executables"] if item["present"]), None)
        if executable_uses_docker(resolved):
            checks["runtime"] = {
                "docker_backed_wrapper": True,
                "docker_daemon": run_probe(["docker", "info"], timeout=30),
            }
    if not network_checks:
        return checks

    install = tool.get("install", {})
    conda_spec = install.get("conda")
    pip_spec = install.get("pip")

    conda_cmd = shutil.which("mamba") or shutil.which("conda") or shutil.which("micromamba")
    if conda_spec and conda_cmd:
        package = conda_spec.split("::", 1)[-1]
        channel = conda_spec.split("::", 1)[0] if "::" in conda_spec else "bioconda"
        channels = (
            ["-c", "conda-forge", "-c", "bioconda"] if channel == "bioconda" else ["-c", channel]
        )
        checks["network"].append(run_probe([conda_cmd, "search", *channels, package], timeout=60))

    if pip_spec:
        checks["network"].append(
            run_probe([sys.executable, "-m", "pip", "index", "versions", pip_spec], timeout=60)
        )

    docker_cmd = shutil.which("docker") or shutil.which("podman")
    if docker_cmd:
        for image in tool.get("container_images", []):
            checks["network"].append(
                run_probe([docker_cmd, "manifest", "inspect", image], timeout=60)
            )

    return checks


def tool_is_present(status: dict[str, Any]) -> bool:
    exe_ok = any(item["present"] for item in status.get("executables", []))
    module_ok = any(item["present"] for item in status.get("python_modules", []))
    return exe_ok or module_ok


def missing_by_profile_role(profile: dict[str, Any], missing: list[str]) -> dict[str, list[str]]:
    missing_set = set(missing)
    return {
        role: [name for name in profile.get(field, []) if name in missing_set]
        for role, field in [
            ("required", "required_tools"),
            ("preferred", "preferred_tools"),
            ("optional", "optional_tools"),
        ]
    }


def missing_by_pipeline_role(pipeline: dict[str, Any], missing: list[str]) -> dict[str, list[str]]:
    missing_set = set(missing)
    return {
        role: [name for name in pipeline.get(field, []) if name in missing_set]
        for role, field in [
            ("preferred", "preferred_tools"),
            ("optional", "optional_tools"),
            ("local_light", "local_light_tools"),
        ]
    }


def install_command(tool_name: str, tool: dict[str, Any], manager: str) -> list[str] | None:
    del tool_name
    install = tool.get("install", {})
    if manager in {"conda", "mamba", "micromamba"} and "conda" in install:
        spec = install["conda"].split("::", 1)
        if len(spec) == 2:
            channel, package = spec
            if channel == "bioconda":
                return [manager, "install", "-y", "-c", "conda-forge", "-c", "bioconda", package]
            return [manager, "install", "-y", "-c", channel, package]
        return [manager, "install", "-y", install["conda"]]
    if manager == "pip" and "pip" in install:
        return [sys.executable, "-m", "pip", "install", install["pip"]]
    return None


def install_plan_entries(
    missing: list[str], registry: dict[str, Any], manager: str
) -> list[dict[str, Any]]:
    entries = []
    for name in missing:
        tool = registry["tools"][name]
        cmd = install_command(name, tool, manager)
        entries.append(
            {
                "tool": name,
                "manager": manager,
                "command": cmd,
                "command_display": shlex.join(cmd) if cmd else None,
                "install": tool.get("install", {}),
                "executables": tool.get("executables", []),
                "python_modules": tool.get("python_modules", []),
                "notes": tool.get("notes"),
                "license": tool.get("license", "public_or_open"),
                "requires_user_approval": cmd is not None,
            }
        )
    return entries


def build_install_artifact(
    *,
    args: argparse.Namespace,
    statuses: list[dict[str, Any]],
    missing: list[str],
    runtime_missing: list[str],
    blocking_missing: list[str],
    plan_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "selection": {
            "tool": args.tool,
            "pipeline": args.pipeline,
            "profile": args.profile,
        },
        "manager": args.manager,
        "network_checks_requested": args.network_checks,
        "permission_model": {
            "requires_explicit_user_approval": bool(plan_entries),
            "install_script_default_mode": "review_only",
            "execution_opt_in": "Set NGS_RUN_INSTALL_COMMANDS=1 before running install_commands.sh.",
            "does_not_install_by_itself": True,
        },
        "missing": missing,
        "runtime_missing": runtime_missing,
        "blocking_missing": blocking_missing,
        "install_plan": plan_entries,
        "checked": statuses,
    }


def render_install_commands(plan: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Generated by ngs_preflight.py from install_plan.json.",
        "# Review install_plan.json before executing package installs.",
        "# This script is review-only unless NGS_RUN_INSTALL_COMMANDS=1 is set.",
        "",
        'PLAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"',
        'echo "Install plan: ${PLAN_DIR}/install_plan.json"',
        'if [[ "${NGS_RUN_INSTALL_COMMANDS:-}" != "1" ]]; then',
        '  echo "Review-only mode. Set NGS_RUN_INSTALL_COMMANDS=1 to execute these commands."',
        "  exit 0",
        "fi",
        "",
        "run_cmd() {",
        '  printf "+ "',
        '  printf "%q " "$@"',
        '  printf "\\n"',
        '  "$@"',
        "}",
        "",
    ]

    commands = [entry for entry in plan.get("install_plan", []) if entry.get("command")]
    if not commands:
        lines.extend(['echo "No package install commands are required for this selection."', ""])
        return "\n".join(lines)

    for entry in plan.get("install_plan", []):
        lines.append(f"# tool: {entry['tool']}")
        if entry.get("notes"):
            lines.append(f"# notes: {entry['notes']}")
        if entry.get("license"):
            lines.append(f"# license: {entry['license']}")
        cmd = entry.get("command")
        if cmd:
            lines.append("run_cmd " + " ".join(shlex.quote(str(part)) for part in cmd))
        else:
            lines.append(
                f"# No {entry.get('manager', 'selected manager')} install command is registered for {entry['tool']}."
            )
        lines.append("")
    return "\n".join(lines)


def write_install_artifacts(plan: dict[str, Any], outdir: Path) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    plan_path = outdir / "install_plan.json"
    commands_path = outdir / "install_commands.sh"
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    commands_path.write_text(render_install_commands(plan), encoding="utf-8")
    commands_path.chmod(0o755)
    return {"install_plan_json": str(plan_path), "install_commands_sh": str(commands_path)}


def selected_tools(
    registry: dict[str, Any], tool: str | None, pipeline: str | None, profile: str | None
) -> list[str]:
    if tool:
        if tool not in registry["tools"]:
            raise SystemExit(f"Unknown tool: {tool}")
        return [tool]
    if profile:
        profiles = registry.get("profiles", {})
        if profile not in profiles:
            raise SystemExit(f"Unknown profile: {profile}")
        entry = profiles[profile]
        names: list[str] = []
        for field in ("required_tools", "preferred_tools", "optional_tools"):
            names.extend(entry.get(field, []))
        return [name for name in dict.fromkeys(names) if name in registry["tools"]]
    if pipeline:
        pipelines = registry["pipelines"]
        if pipeline not in pipelines:
            raise SystemExit(f"Unknown pipeline: {pipeline}")
        entry = pipelines[pipeline]
        names: list[str] = []
        for field in ("preferred_tools", "optional_tools", "local_light_tools"):
            names.extend(entry.get(field, []))
        return [name for name in dict.fromkeys(names) if name in registry["tools"]]
    raise SystemExit("Provide --tool, --pipeline, --profile, or --list")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--tool")
    parser.add_argument("--pipeline")
    parser.add_argument("--profile", help="Check a named runtime profile such as local_light.")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--network-checks", action="store_true")
    parser.add_argument("--emit-install-plan", action="store_true")
    parser.add_argument(
        "--install-plan-outdir",
        type=Path,
        help="Write install_plan.json and guarded install_commands.sh artifacts to this directory.",
    )
    parser.add_argument(
        "--manager", choices=["conda", "mamba", "micromamba", "pip"], default="mamba"
    )
    parser.add_argument("--install-missing", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Required with --install-missing.")
    args = parser.parse_args()

    registry = load_registry(args.registry)

    if args.list:
        print(
            json.dumps(
                {
                    "pipelines": sorted(registry["pipelines"]),
                    "profiles": sorted(registry.get("profiles", {})),
                    "tools": sorted(registry["tools"]),
                },
                indent=2,
            )
        )
        return 0

    names = selected_tools(registry, args.tool, args.pipeline, args.profile)
    statuses = [check_index(name, registry["tools"][name], args.network_checks) for name in names]
    missing = [status["tool"] for status in statuses if not tool_is_present(status)]
    runtime_missing = [
        f"{status['tool']}:docker_daemon"
        for status in statuses
        if status.get("runtime", {}).get("docker_backed_wrapper")
        and not status["runtime"]["docker_daemon"].get("ok", False)
    ]

    output: dict[str, Any] = {
        "checked": statuses,
        "missing": missing,
        "runtime_missing": runtime_missing,
    }
    blocking_missing = missing + runtime_missing

    if args.profile:
        profile = registry.get("profiles", {})[args.profile]
        by_role = missing_by_profile_role(profile, missing)
        output["profile"] = {
            "name": args.profile,
            "missing_by_role": by_role,
            "blocking_missing": by_role["required"],
        }
        blocking_missing = by_role["required"]
    elif args.pipeline:
        pipeline = registry.get("pipelines", {})[args.pipeline]
        by_role = missing_by_pipeline_role(pipeline, missing)
        output["pipeline"] = {
            "name": args.pipeline,
            "missing_by_role": by_role,
            "blocking_missing": by_role["preferred"] + runtime_missing,
        }
        blocking_missing = by_role["preferred"] + runtime_missing

    if args.emit_install_plan or args.install_plan_outdir:
        plan_entries = install_plan_entries(missing, registry, args.manager)
        output["install_plan"] = plan_entries
        install_artifact = build_install_artifact(
            args=args,
            statuses=statuses,
            missing=missing,
            runtime_missing=runtime_missing,
            blocking_missing=blocking_missing,
            plan_entries=plan_entries,
        )
        if args.install_plan_outdir:
            output["install_artifacts"] = write_install_artifacts(
                install_artifact, args.install_plan_outdir
            )

    print(json.dumps(output, indent=2))

    if args.install_missing:
        if not args.yes:
            raise SystemExit("--install-missing requires --yes")
        for name in missing:
            cmd = install_command(name, registry["tools"][name], args.manager)
            if not cmd:
                print(f"No {args.manager} install command registered for {name}", file=sys.stderr)
                continue
            subprocess.run(cmd, check=True)

    return 1 if blocking_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
