#!/usr/bin/env python3
"""Shared helpers for plugin-owned NGS execution runners."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

RUN_ENVELOPE_SCHEMA_VERSION = "0.4.0"
MAX_AUTO_CHECKSUM_BYTES = 128 * 1024 * 1024
LOCAL_ENV_FILE = Path.cwd() / ".ngs-analysis-local.env"


def _load_local_env_file(path: Path = LOCAL_ENV_FILE) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        values[key] = os.path.expandvars(value)
    return values


LOCAL_ENV = _load_local_env_file()


def _apply_local_env() -> None:
    for key, value in LOCAL_ENV.items():
        if key == "NGS_TOOL_PATH_PREPEND":
            continue
        os.environ.setdefault(key, value)


def _effective_path() -> str:
    base_path = os.environ.get("PATH", "")
    prepend = LOCAL_ENV.get("NGS_TOOL_PATH_PREPEND", "").strip()
    if not prepend:
        return base_path
    return os.pathsep.join([prepend, base_path]) if base_path else prepend


def _effective_env() -> dict[str, str]:
    env = os.environ.copy()
    for key, value in LOCAL_ENV.items():
        if key == "NGS_TOOL_PATH_PREPEND":
            continue
        env.setdefault(key, value)
    env["PATH"] = _effective_path()
    return env


_apply_local_env()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slug_timestamp(label: str) -> str:
    safe_label = label.strip().replace("_", "-")
    return datetime.now().strftime(f"%Y-%m-%dT%H-%M-%S-{safe_label}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def command_path(name: str) -> str | None:
    return shutil.which(name, path=_effective_path())


def module_present(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def shell_tool_command(name: str) -> str | None:
    resolved = command_path(name)
    if resolved:
        return name
    module_fallbacks = {
        "snakemake": "snakemake",
        "multiqc": "multiqc",
        "cutadapt": "cutadapt",
    }
    module_name = module_fallbacks.get(name)
    if module_name and module_present(module_name):
        return f"{sys.executable} -m {module_name}"
    return None


def run_cmd(cmd: list[str], cwd: Path, timeout: int | None = None) -> dict[str, Any]:
    started = now_iso()
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            env=_effective_env(),
        )
        output = result.stdout or ""
        return {
            "cmd": cmd,
            "cwd": str(cwd),
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": result.returncode,
            "ok": result.returncode == 0,
            "stdout_tail": output[-12000:],
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout if isinstance(exc.stdout, str) else ""
        return {
            "cmd": cmd,
            "cwd": str(cwd),
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": None,
            "ok": False,
            "error": f"TimeoutExpired: exceeded {timeout}s",
            "stdout_tail": output[-12000:],
        }


def run_cmd_stdout_to_file(
    cmd: list[str],
    cwd: Path,
    stdout_path: Path,
    timeout: int | None = None,
) -> dict[str, Any]:
    started = now_iso()
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with stdout_path.open("w", encoding="utf-8") as handle:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=False,
                stdout=handle,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                env=_effective_env(),
            )
        stderr = result.stderr or ""
        preview = stdout_path.read_text(encoding="utf-8")[-12000:] if stdout_path.exists() else ""
        return {
            "cmd": cmd,
            "cwd": str(cwd),
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": result.returncode,
            "ok": result.returncode == 0,
            "stdout_path": str(stdout_path),
            "stdout_tail": preview,
            "stderr_tail": stderr[-12000:],
        }
    except subprocess.TimeoutExpired as exc:
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        preview = stdout_path.read_text(encoding="utf-8")[-12000:] if stdout_path.exists() else ""
        return {
            "cmd": cmd,
            "cwd": str(cwd),
            "started_at": started,
            "finished_at": now_iso(),
            "returncode": None,
            "ok": False,
            "stdout_path": str(stdout_path),
            "error": f"TimeoutExpired: exceeded {timeout}s",
            "stdout_tail": preview,
            "stderr_tail": stderr[-12000:],
        }


def executable_status(name: str) -> dict[str, Any]:
    resolved = command_path(name)
    return {"name": name, "present": resolved is not None, "path": resolved}


def module_status(name: str) -> dict[str, Any]:
    return {"name": name, "present": module_present(name)}


def tool_preflight(required: list[str], optional: list[str] | None = None) -> dict[str, Any]:
    optional = optional or []
    checked = []
    for name in required + optional:
        checked.append(executable_status(name))
    missing_required = [item["name"] for item in checked[: len(required)] if not item["present"]]
    return {
        "ok": not missing_required,
        "required": required,
        "optional": optional,
        "checked": checked,
        "missing_required": missing_required,
    }


def software_versions(commands: dict[str, list[str]]) -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name, cmd in commands.items():
        if not command_path(cmd[0]):
            versions[name] = None
            continue
        result = run_cmd(cmd, Path.cwd(), timeout=30)
        detail = result.get("stdout_tail") or result.get("error") or ""
        versions[name] = "\n".join(str(detail).splitlines()[:3]).strip() or None
    return versions


def _iter_existing_paths(value: Any) -> list[Path]:
    paths: list[Path] = []
    if isinstance(value, dict):
        for item in value.values():
            paths.extend(_iter_existing_paths(item))
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            paths.extend(_iter_existing_paths(item))
    elif isinstance(value, str):
        candidate = Path(value).expanduser()
        if candidate.exists() and candidate.is_file():
            paths.append(candidate.resolve())
    return paths


def input_checksums(inputs: dict[str, Any] | None) -> list[dict[str, Any]]:
    seen: set[Path] = set()
    checksums: list[dict[str, Any]] = []
    for path in _iter_existing_paths(inputs or {}):
        if path in seen:
            continue
        seen.add(path)
        size = path.stat().st_size
        record: dict[str, Any] = {"path": str(path), "bytes": size}
        if size <= MAX_AUTO_CHECKSUM_BYTES:
            record["sha256"] = sha256_file(path)
        else:
            record["sha256"] = None
            record["sha256_skipped_reason"] = (
                f"file exceeds {MAX_AUTO_CHECKSUM_BYTES} bytes auto-checksum threshold"
            )
        checksums.append(record)
    return sorted(checksums, key=lambda item: item["path"])


def _flatten_declared_paths(value: Any, prefix: str = "") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_declared_paths(item, next_prefix))
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            rows.extend(_flatten_declared_paths(item, f"{prefix}[{index}]"))
    elif isinstance(value, str) and value.strip():
        rows.append({"logical_name": prefix or "value", "path": value})
    return rows


def _resolve_run_relative_path(run_dir: Path, raw_path: str) -> Path | None:
    if any(char in raw_path for char in "*?[]{}"):
        return None
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (run_dir / candidate).resolve()


def write_io_lineage(
    run_dir: Path, inputs: dict[str, Any] | None, outputs: dict[str, Any] | None
) -> Path:
    input_records = _flatten_declared_paths(inputs or {})
    output_records = _flatten_declared_paths(outputs or {})
    source_inputs = ";".join(sorted(record["logical_name"] for record in input_records))

    lines = [
        "\t".join(
            [
                "record_type",
                "logical_name",
                "path",
                "exists",
                "bytes",
                "sha256",
                "source_inputs",
            ]
        )
    ]
    for record in input_records:
        resolved = _resolve_run_relative_path(run_dir, record["path"])
        exists = bool(resolved and resolved.exists() and resolved.is_file())
        size = str(resolved.stat().st_size) if exists and resolved else ""
        checksum = (
            sha256_file(resolved)
            if exists and resolved and resolved.stat().st_size <= MAX_AUTO_CHECKSUM_BYTES
            else ""
        )
        lines.append(
            "\t".join(
                [
                    "input",
                    record["logical_name"],
                    record["path"],
                    "true" if exists else "false",
                    size,
                    checksum,
                    "",
                ]
            )
        )
    for record in output_records:
        resolved = _resolve_run_relative_path(run_dir, record["path"])
        exists = bool(resolved and resolved.exists() and resolved.is_file())
        size = str(resolved.stat().st_size) if exists and resolved else ""
        checksum = (
            sha256_file(resolved)
            if exists and resolved and resolved.stat().st_size <= MAX_AUTO_CHECKSUM_BYTES
            else ""
        )
        lines.append(
            "\t".join(
                [
                    "output",
                    record["logical_name"],
                    record["path"],
                    "true" if exists else "false",
                    size,
                    checksum,
                    source_inputs,
                ]
            )
        )
    lineage_path = run_dir / "manifest" / "lineage.tsv"
    write_text(lineage_path, "\n".join(lines) + "\n")
    return lineage_path


def _find_plugin_root() -> Path | None:
    for current in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        if (current / ".codex-plugin" / "plugin.json").exists():
            return current
    return None


def plugin_metadata() -> dict[str, Any]:
    root = _find_plugin_root()
    metadata: dict[str, Any] = {
        "name": None,
        "version": None,
        "repository": None,
        "source_root": str(root) if root else None,
        "git_commit": None,
    }
    if root is None:
        return metadata
    plugin_json = root / ".codex-plugin" / "plugin.json"
    try:
        payload = json.loads(plugin_json.read_text(encoding="utf-8"))
        metadata["name"] = payload.get("name")
        metadata["version"] = payload.get("version")
        metadata["repository"] = payload.get("repository")
    except (OSError, json.JSONDecodeError):
        pass
    git_root = next(
        (candidate for candidate in [root, *root.parents] if (candidate / ".git").exists()), None
    )
    if git_root is not None:
        revision = run_cmd(["git", "rev-parse", "HEAD"], git_root, timeout=15)
        if revision.get("ok") and revision.get("stdout_tail"):
            metadata["git_commit"] = str(revision["stdout_tail"]).splitlines()[0].strip()
    return metadata


def environment_snapshot() -> dict[str, Any]:
    return {
        "cwd": str(Path.cwd()),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "argv": sys.argv,
        "argv_string": shlex.join(sys.argv),
        "selected_env": {
            "MPLCONFIGDIR": str(Path(os.environ["MPLCONFIGDIR"]))
            if os.environ.get("MPLCONFIGDIR")
            else None,
            "XDG_CACHE_HOME": str(Path(os.environ["XDG_CACHE_HOME"]))
            if os.environ.get("XDG_CACHE_HOME")
            else None,
        },
    }


def build_artifact_index(
    run_dir: Path,
    patterns: list[str] | None = None,
    extra_roots: dict[str, Path] | None = None,
) -> dict[str, Any]:
    patterns = patterns or [
        "config*",
        "commands.sh",
        "run_manifest.json",
        "summary.md",
        "artifact_index.json",
        "validation/**/*",
        "logs/**/*",
        "versions/**/*",
        "workflow/**/*",
        "fastqc/**/*",
        "multiqc/**/*",
        "rnaseq_salmon/**/*",
        "qc/**/*",
        "results/**/*",
        "plots/**/*",
        "visualizations/**/*",
        "tables/**/*",
        "notebooks/**/*",
        "variants/**/*",
        "alignment/**/*",
        "peaks/**/*",
        "tracks/**/*",
        "motifs/**/*",
        "consensus/**/*",
        "f1r2/**/*",
        "functional_profile/**/*",
        "taxonomic_classification/**/*",
        "bcl/**/*",
        "demux/**/*",
        "methods/**/*",
        "manifest/**/*",
        "resources/**/*",
        "*.json",
    ]
    artifacts = []
    seen: set[Path] = set()

    def collect(root_label: str | None, root: Path, root_patterns: list[str]) -> None:
        prefix = "" if not root_label else f"{root_label}/"
        for pattern in root_patterns:
            for path in root.glob(pattern):
                if path.is_file() and path not in seen:
                    seen.add(path)
                    artifacts.append(
                        {
                            "path": f"{prefix}{path.relative_to(root)}",
                            "bytes": path.stat().st_size,
                            "modified_at": datetime.fromtimestamp(path.stat().st_mtime)
                            .astimezone()
                            .isoformat(timespec="seconds"),
                            "sha256": sha256_file(path)
                            if path.stat().st_size <= MAX_AUTO_CHECKSUM_BYTES
                            else "",
                            "sha256_skipped_reason": (
                                None
                                if path.stat().st_size <= MAX_AUTO_CHECKSUM_BYTES
                                else f"file exceeds {MAX_AUTO_CHECKSUM_BYTES} bytes auto-checksum threshold"
                            ),
                        }
                    )

    collect(None, run_dir, patterns)
    if extra_roots:
        for label, root in extra_roots.items():
            if root.exists():
                collect(label, root, ["**/*"])
    return {
        "created_at": now_iso(),
        "checksum_algorithm": "sha256",
        "artifacts": sorted(artifacts, key=lambda item: item["path"]),
    }


def write_standard_manifest(
    run_dir: Path,
    *,
    run_id: str,
    lane: str,
    analysis_intent: str = "real_analysis",
    workflow: str,
    status: str,
    execute_requested: bool,
    validation: dict[str, Any],
    tool_preflight_result: dict[str, Any],
    dry_run: dict[str, Any] | None = None,
    execution: dict[str, Any] | None = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    method: dict[str, Any] | None = None,
    audit: dict[str, Any] | None = None,
    review_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lineage_path = write_io_lineage(run_dir, inputs, outputs)
    parameter_hash = sha256_json(
        {
            "lane": lane,
            "workflow": workflow,
            "execute_requested": execute_requested,
            "inputs": inputs or {},
            "outputs": outputs or {},
            "method": method or {},
        }
    )
    merged_audit = {
        "plugin": plugin_metadata(),
        "environment": environment_snapshot(),
        "input_checksums": input_checksums(inputs),
        "parameter_sha256": parameter_hash,
        "lineage_table_path": str(lineage_path.relative_to(run_dir)),
    }
    config_path = run_dir / "config.json"
    if config_path.exists():
        merged_audit["config_sha256"] = sha256_file(config_path)
    if audit:
        merged_audit.update(audit)
    manifest = {
        "schema_version": RUN_ENVELOPE_SCHEMA_VERSION,
        "run_id": run_id,
        "created_at": now_iso(),
        "lane": lane,
        "analysis_intent": analysis_intent,
        "workflow": workflow,
        "run_dir": str(run_dir),
        "status": status,
        "execute_requested": execute_requested,
        "validation_ok": validation.get("ok"),
        "tool_preflight_ok": tool_preflight_result.get("ok"),
        "ready_to_execute": bool(validation.get("ok") and tool_preflight_result.get("ok")),
        "dry_run_performed": dry_run is not None,
        "dry_run_ok": dry_run.get("ok") if dry_run else None,
        "execution_ok": execution.get("ok") if execution else None,
        "dry_run_result": dry_run,
        "execution_result": execution,
        "inputs": inputs or {},
        "outputs": outputs or {},
        "method": method or {},
        "audit": merged_audit,
        "artifact_index_path": "artifact_index.json",
        "review_bundle": review_bundle or {},
    }
    write_json(run_dir / "run_manifest.json", manifest)
    return manifest
