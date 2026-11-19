#!/usr/bin/env python3
"""Verify, smoke-test, and install selected skills into ~/.agents/skills."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(r"E:\PyCharmProject\plugins")
SKILLS_ROOT = Path(os.environ["USERPROFILE"]) / ".agents" / "skills"
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"
PLUGIN_EVAL = REPO / "plugins" / "plugin-eval" / "scripts" / "plugin-eval.js"
REPORT_PATH = REPO / "_selected_skills_install_report.md"
RESULTS_JSON = REPO / "_selected_skills_install_results.json"

# (install_name, relative_skill_dir from repo root)
SKILL_MAP: list[tuple[str, str]] = [
    # superpowers
    ("brainstorming", "plugins/superpowers/skills/brainstorming"),
    ("dispatching-parallel-agents", "plugins/superpowers/skills/dispatching-parallel-agents"),
    ("executing-plans", "plugins/superpowers/skills/executing-plans"),
    # build-web-apps
    ("frontend-app-builder", "plugins/build-web-apps/skills/frontend-app-builder"),
    ("react-best-practices", "plugins/build-web-apps/skills/react-best-practices"),
    # build-web-data-visualization
    ("dashboards-and-real-time-visualization", "plugins/build-web-data-visualization/skills/dashboards-and-real-time-visualization"),
    ("data-visualization", "plugins/build-web-data-visualization/skills/data-visualization"),
    ("grammar-of-graphics-and-declarative-visualization", "plugins/build-web-data-visualization/skills/grammar-of-graphics-and-declarative-visualization"),
    ("react-and-nextjs-data-visualization", "plugins/build-web-data-visualization/skills/react-and-nextjs-data-visualization"),
    ("reports-pdfs-and-slide-automation", "plugins/build-web-data-visualization/skills/reports-pdfs-and-slide-automation"),
    ("statistical-and-uncertainty-visualization", "plugins/build-web-data-visualization/skills/statistical-and-uncertainty-visualization"),
    ("testing-data-visualizations", "plugins/build-web-data-visualization/skills/testing-data-visualizations"),
    ("typescript-data-visualization-engineering", "plugins/build-web-data-visualization/skills/typescript-data-visualization-engineering"),
    ("visualization-strategy-and-critique", "plugins/build-web-data-visualization/skills/visualization-strategy-and-critique"),
    # figma
    ("figma-code-connect", "plugins/figma/skills/figma-code-connect"),
    ("figma-create-new-file", "plugins/figma/skills/figma-create-new-file"),
    ("figma-design-to-code", "plugins/figma/skills/figma-design-to-code"),
    ("figma-generate-design", "plugins/figma/skills/figma-generate-design"),
    ("figma-generate-diagram", "plugins/figma/skills/figma-generate-diagram"),
    ("figma-generate-library", "plugins/figma/skills/figma-generate-library"),
    ("figma-implement-motion", "plugins/figma/skills/figma-implement-motion"),
    ("figma-use", "plugins/figma/skills/figma-use"),
    ("figma-use-motion", "plugins/figma/skills/figma-use-motion"),
    # google-drive
    ("google-docs", "plugins/google-drive/skills/google-docs"),
    ("google-drive", "plugins/google-drive/skills/google-drive"),
    ("google-drive-comments", "plugins/google-drive/skills/google-drive-comments"),
    ("google-sheets", "plugins/google-drive/skills/google-sheets"),
    ("google-slides", "plugins/google-drive/skills/google-slides"),
    # nvidia
    ("omniverse-realtime-viewer", "plugins/nvidia/skills/omniverse-realtime-viewer"),
    ("physical-ai-neural-reconstruction", "plugins/nvidia/skills/physical-ai-neural-reconstruction"),
    # openai-developers (not cloudflare)
    ("agents-sdk", "plugins/openai-developers/skills/agents-sdk"),
    ("build-chatgpt-app", "plugins/openai-developers/skills/build-chatgpt-app"),
    # data-analytics
    ("analyze-data-quality", "plugins/data-analytics/skills/analyze-data-quality"),
    ("build-dashboard", "plugins/data-analytics/skills/build-dashboard"),
    ("build-report", "plugins/data-analytics/skills/build-report"),
    ("create-data-context", "plugins/data-analytics/skills/create-data-context"),
    ("gather-business-context", "plugins/data-analytics/skills/gather-business-context"),
    ("design-kpis", "plugins/data-analytics/skills/design-kpis"),
    ("index", "plugins/data-analytics/skills/index"),
    ("jupyter-notebooks", "plugins/data-analytics/skills/jupyter-notebooks"),
    ("kpi-reporting", "plugins/data-analytics/skills/kpi-reporting"),
    ("publish-artifact-to-sites", "plugins/data-analytics/skills/publish-artifact-to-sites"),
    ("report-to-google-doc", "plugins/data-analytics/skills/build-report/report-to-google-doc"),
    ("report-to-google-slides", "plugins/data-analytics/skills/build-report/report-to-google-slides"),
    ("report-to-pdf", "plugins/data-analytics/skills/build-report/report-to-pdf"),
    ("validate-data", "plugins/data-analytics/skills/validate-data"),
    ("visualize-data", "plugins/data-analytics/skills/visualize-data"),
    # product-design
    ("image-to-code", "plugins/product-design/skills/image-to-code"),
    ("research", "plugins/product-design/skills/research"),
    ("url-to-code", "plugins/product-design/skills/url-to-code"),
    ("user-context", "plugins/product-design/skills/user-context"),
    ("audit", "plugins/product-design/skills/audit"),
]

PARENT_PLUGINS = {
    "superpowers",
    "build-web-apps",
    "build-web-data-visualization",
    "figma",
    "google-drive",
    "nvidia",
    "openai-developers",
    "data-analytics",
    "product-design",
}


@dataclass
class SkillResult:
    install_name: str
    source_rel: str
    source_abs: str = ""
    resolved: bool = False
    verify_ok: bool = False
    verify_errors: list[str] = field(default_factory=list)
    verify_warnings: list[str] = field(default_factory=list)
    smoke_ok: bool = False
    smoke_notes: list[str] = field(default_factory=list)
    plugin_eval_ok: bool | None = None
    plugin_eval_summary: str = ""
    install_name_final: str = ""
    install_path: str = ""
    installed: bool = False
    install_notes: list[str] = field(default_factory=list)


def load_marketplace_names() -> set[str]:
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return {p["name"] for p in data.get("plugins", [])}


def parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = m.group(1)
    out: dict[str, str] = {}
    name = re.search(r'^name:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
    if name:
        out["name"] = name.group(1).strip().strip("\"'")
    dm = re.search(r'^description:\s*[>|]-?\s*\n((?:[ \t]+.+\n?)+)', fm, re.M)
    if dm:
        out["description"] = " ".join(
            line.strip() for line in dm.group(1).splitlines() if line.strip()
        )
    else:
        dm = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', fm, re.M)
        if dm:
            out["description"] = dm.group(1).strip().strip("\"'")
    return out


def find_relative_links(skill_md: Path, text: str) -> list[str]:
    errors: list[str] = []
    # markdown links and bare relative refs like (references/foo.md)
    for match in re.finditer(r"\((?!https?:|mailto:|skill://|#)([^)\s]+)\)", text):
        target = match.group(1).split("#", 1)[0].strip()
        if not target or target.startswith("`"):
            continue
        # skip template placeholders
        if "<" in target or "{" in target:
            continue
        candidate = (skill_md.parent / target).resolve()
        try:
            candidate.relative_to(skill_md.parent.resolve())
        except ValueError:
            # allow links into sibling dirs within same plugin? still check exists
            pass
        if not candidate.exists():
            # also try from skill root for ./ paths
            errors.append(f"broken link: {target}")
    return errors


def verify_skill(r: SkillResult, marketplace: set[str]) -> None:
    src = REPO / r.source_rel
    r.source_abs = str(src)
    if not src.exists():
        r.verify_errors.append("source directory missing")
        return
    skill_md = src / "SKILL.md"
    if not skill_md.exists():
        r.verify_errors.append("SKILL.md missing")
        return
    r.resolved = True
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    if not fm.get("name"):
        r.verify_errors.append("frontmatter name missing")
    if not fm.get("description"):
        r.verify_errors.append("frontmatter description missing")
    folder_name = src.name
    if fm.get("name") and fm["name"] != folder_name and fm["name"] != r.install_name:
        r.verify_warnings.append(
            f"frontmatter name '{fm.get('name')}' != folder '{folder_name}'"
        )
    # relative links (warn-only for soft failures elsewhere; broken = warning unless many)
    link_errors = find_relative_links(skill_md, text)
    # filter false positives for non-file refs that are intentional
    real_broken = []
    for err in link_errors:
        target = err.split(": ", 1)[-1]
        # ignore pure anchors already filtered; ignore .md in docs that are optional
        p = (src / target).resolve()
        if p.exists():
            continue
        # ignore links that look like CLI examples or globs
        if any(ch in target for ch in ["*", "$", "|"]):
            continue
        real_broken.append(err)
    if real_broken:
        # keep as warnings so install can proceed for soft doc issues
        r.verify_warnings.extend(real_broken[:10])
        if len(real_broken) > 10:
            r.verify_warnings.append(f"... +{len(real_broken) - 10} more broken links")

    # parent plugin in marketplace
    parts = Path(r.source_rel).parts
    if len(parts) >= 2 and parts[0] == "plugins":
        parent = parts[1]
        if parent not in marketplace:
            r.verify_errors.append(f"parent plugin '{parent}' not in marketplace.json")
        elif parent not in PARENT_PLUGINS:
            r.verify_warnings.append(f"parent '{parent}' unexpected for this selection")

    r.verify_ok = r.resolved and not r.verify_errors


def smoke_test(r: SkillResult) -> None:
    if not r.verify_ok:
        r.smoke_notes.append("skipped: verify failed")
        return
    src = Path(r.source_abs)
    skill_md = src / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    notes = []
    if len(fm.get("description", "")) < 20:
        notes.append("description very short")
    if len(text) < 80:
        notes.append("SKILL.md unusually short")
    # ensure UTF-8 readable and has a heading or workflow cue
    if not re.search(r"^#\s+", text, re.M) and "Workflow" not in text:
        notes.append("no top-level heading detected")
    r.smoke_notes = notes
    r.smoke_ok = True  # structural smoke pass if verify passed


def run_plugin_eval(r: SkillResult) -> None:
    if not r.verify_ok:
        r.plugin_eval_ok = None
        return
    if not PLUGIN_EVAL.exists():
        r.plugin_eval_ok = None
        r.plugin_eval_summary = "plugin-eval.js not found"
        return
    try:
        proc = subprocess.run(
            ["node", str(PLUGIN_EVAL), "analyze", r.source_abs, "--format", "markdown"],
            cwd=str(PLUGIN_EVAL.parent.parent),
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:  # noqa: BLE001
        r.plugin_eval_ok = False
        r.plugin_eval_summary = f"plugin-eval error: {exc}"
        return
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    # extract a short glance
    glance = ""
    for line in out.splitlines():
        if line.strip():
            glance = line.strip()
            break
    # look for Fix First / At a Glance sections
    m = re.search(r"(?:At a Glance|## At a Glance)(.*?)(?:\n## |\Z)", out, re.S | re.I)
    if m:
        glance = " ".join(m.group(1).split())[:240]
    fix = ""
    m2 = re.search(r"(?:Fix First|## Fix First)(.*?)(?:\n## |\Z)", out, re.S | re.I)
    if m2:
        fix = " ".join(m2.group(1).split())[:160]
    r.plugin_eval_ok = proc.returncode == 0
    summary = glance or out[:200].replace("\n", " ")
    if fix:
        summary += f" | Fix First: {fix}"
    if proc.returncode != 0:
        summary = f"exit={proc.returncode}; {summary or (proc.stderr or '')[:200]}"
    r.plugin_eval_summary = summary[:400]


def is_junction_or_link(path: Path) -> bool:
    try:
        return bool(path.is_symlink()) or bool(
            path.exists() and path.stat().st_file_attributes & 0x400  # type: ignore[attr-defined]
        )
    except Exception:
        return path.is_symlink()


def install_skill(r: SkillResult) -> None:
    if not r.verify_ok:
        r.install_notes.append("skipped: verify failed")
        return
    SKILLS_ROOT.mkdir(parents=True, exist_ok=True)
    name = r.install_name
    dest = SKILLS_ROOT / name
    target = Path(r.source_abs)

    # collision: existing non-matching path
    if dest.exists() or dest.is_symlink():
        try:
            # if already a junction/symlink to the same target, OK
            resolved = dest.resolve()
            if resolved == target.resolve():
                r.install_name_final = name
                r.install_path = str(dest)
                r.installed = True
                r.install_notes.append("already installed (same target)")
                return
        except Exception:
            pass
        # namespaced fallback
        plugin = Path(r.source_rel).parts[1]
        name = f"{plugin}--{r.install_name}"
        dest = SKILLS_ROOT / name
        r.install_notes.append(
            f"collision on '{r.install_name}'; using namespaced '{name}'"
        )
        if dest.exists() or dest.is_symlink():
            try:
                if dest.resolve() == target.resolve():
                    r.install_name_final = name
                    r.install_path = str(dest)
                    r.installed = True
                    r.install_notes.append("namespaced path already installed")
                    return
            except Exception:
                pass
            r.install_notes.append(f"namespaced destination also exists: {dest}")
            r.installed = False
            r.install_name_final = name
            r.install_path = str(dest)
            return

    # Create Windows junction via cmd mklink /J
    cmd = ["cmd", "/c", "mklink", "/J", str(dest), str(target)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        r.installed = False
        r.install_name_final = name
        r.install_path = str(dest)
        r.install_notes.append(
            f"mklink failed: {(proc.stdout or '') + (proc.stderr or '')}".strip()
        )
        return
    r.install_name_final = name
    r.install_path = str(dest)
    r.installed = dest.exists()
    r.install_notes.append((proc.stdout or "junction created").strip())


def write_report(results: list[SkillResult], marketplace: set[str]) -> None:
    passed = [r for r in results if r.verify_ok]
    failed = [r for r in results if not r.verify_ok]
    installed = [r for r in results if r.installed]
    scored: list[tuple[str, int, str]] = []
    for r in results:
        m = re.search(r"Score:\s*(\d+)/100", r.plugin_eval_summary or "")
        g = re.search(r"Grade:\s*([A-F][+-]?)", r.plugin_eval_summary or "")
        if m:
            scored.append((r.install_name, int(m.group(1)), g.group(1) if g else "?"))
    scored.sort(key=lambda x: (-x[1], x[0]))
    lines = [
        "# Selected skills install report",
        "",
        f"Repo: `{REPO}`",
        f"Install root: `{SKILLS_ROOT}`",
        f"Skills selected: **{len(results)}**",
        f"Verify passed: **{len(passed)}**",
        f"Verify failed: **{len(failed)}**",
        f"Smoke passed: **{sum(1 for r in results if r.smoke_ok)}**",
        f"plugin-eval completed: **{sum(1 for r in results if r.plugin_eval_ok)}**",
        f"Installed: **{len(installed)}**",
        "",
        "## plugin-eval scoreboard",
        "",
        "| Skill | Score | Grade |",
        "|---|---:|---|",
    ]
    for name, score, grade in scored:
        lines.append(f"| `{name}` | {score} | {grade} |")
    if not scored:
        lines.append("| _(no scores yet)_ | | |")
    lines += [
        "",
        "## Parent plugins in marketplace",
        "",
    ]
    for p in sorted(PARENT_PLUGINS):
        mark = "yes" if p in marketplace else "NO"
        lines.append(f"- `{p}`: {mark}")
    lines += ["", "## Results", ""]
    for r in results:
        status = "PASS" if r.verify_ok else "FAIL"
        inst = "installed" if r.installed else "not installed"
        lines.append(f"### `{r.install_name}` — {status} / {inst}")
        lines.append("")
        lines.append(f"- Source: `{r.source_rel}`")
        if r.verify_errors:
            lines.append(f"- Verify errors: {'; '.join(r.verify_errors)}")
        if r.verify_warnings:
            lines.append(f"- Verify warnings: {'; '.join(r.verify_warnings[:5])}")
        lines.append(f"- Smoke: {'ok' if r.smoke_ok else 'skip/fail'}; {'; '.join(r.smoke_notes) or '—'}")
        if r.plugin_eval_ok is None:
            lines.append(f"- plugin-eval: skipped ({r.plugin_eval_summary or 'n/a'})")
        else:
            pe = "ok" if r.plugin_eval_ok else "fail"
            lines.append(f"- plugin-eval: {pe}; {r.plugin_eval_summary or '—'}")
        if r.install_path:
            lines.append(f"- Install path: `{r.install_path}` (as `{r.install_name_final}`)")
        if r.install_notes:
            lines.append(f"- Install notes: {'; '.join(r.install_notes)}")
        lines.append("")
    lines += [
        "## Notes",
        "",
        "- Installs are Windows directory junctions into this repo (live updates).",
        "- Live Figma / Google Drive / Omniverse API tests were not run.",
        "- `agents-sdk` resolves to `openai-developers` (not Cloudflare).",
        "- `index` and `user-context` resolve to data-analytics and product-design respectively.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def save(results: list[SkillResult], marketplace: set[str]) -> None:
    write_report(results, marketplace)
    RESULTS_JSON.write_text(
        json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"WROTE {REPORT_PATH}")
    print(f"WROTE {RESULTS_JSON}")


def load_results() -> list[SkillResult]:
    if not RESULTS_JSON.exists():
        return []
    raw = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    out: list[SkillResult] = []
    for item in raw:
        out.append(SkillResult(**item))
    return out


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    phase = "all"
    if "--phase" in argv:
        i = argv.index("--phase")
        phase = argv[i + 1]
    skip_eval = "--skip-plugin-eval" in argv or phase in {"verify", "install", "verify-install"}
    eval_only = "--plugin-eval-only" in argv or phase == "eval"

    marketplace = load_marketplace_names()

    if eval_only:
        results = load_results()
        if not results:
            print("No prior results; run verify-install first", file=sys.stderr)
            return 2
        if not PLUGIN_EVAL.exists():
            for r in results:
                r.plugin_eval_summary = "plugin-eval.js missing"
            save(results, marketplace)
            return 0
        todo = [r for r in results if r.verify_ok]
        print(f"Running plugin-eval analyze for {len(todo)} skills (parallel)…", flush=True)

        def _one(item: SkillResult) -> SkillResult:
            run_plugin_eval(item)
            return item

        done = 0
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(_one, r): r for r in todo}
            for fut in as_completed(futures):
                r = futures[fut]
                try:
                    fut.result()
                except Exception as exc:  # noqa: BLE001
                    r.plugin_eval_ok = False
                    r.plugin_eval_summary = f"worker error: {exc}"
                done += 1
                pe = "ok" if r.plugin_eval_ok else "fail"
                print(
                    f"  plugin-eval [{done}/{len(todo)}] {r.install_name}: {pe}",
                    flush=True,
                )
                if done % 8 == 0:
                    save(results, marketplace)
        save(results, marketplace)
        return 0

    results: list[SkillResult] = []
    for install_name, rel in SKILL_MAP:
        results.append(SkillResult(install_name=install_name, source_rel=rel))

    print(f"Mapped {len(results)} skills", flush=True)
    for r in results:
        verify_skill(r, marketplace)
        status = "OK" if r.verify_ok else "FAIL"
        print(f"  verify [{status}] {r.install_name}", flush=True)

    for r in results:
        smoke_test(r)

    if not skip_eval:
        if PLUGIN_EVAL.exists():
            print("Running plugin-eval analyze…", flush=True)
            for i, r in enumerate(results, 1):
                if not r.verify_ok:
                    continue
                print(f"  plugin-eval [{i}/{len(results)}] {r.install_name}", flush=True)
                run_plugin_eval(r)
        else:
            for r in results:
                r.plugin_eval_summary = "plugin-eval.js missing"
    else:
        for r in results:
            if r.plugin_eval_summary == "":
                r.plugin_eval_summary = "deferred (run --plugin-eval-only)"

    if phase != "verify":
        print("Installing junctions…", flush=True)
        for r in results:
            install_skill(r)
            mark = "INSTALLED" if r.installed else "SKIP"
            print(
                f"  install [{mark}] {r.install_name} -> {r.install_name_final or '-'}",
                flush=True,
            )

    save(results, marketplace)
    failed = sum(1 for r in results if not r.verify_ok)
    not_installed = sum(1 for r in results if r.verify_ok and not r.installed)
    print(f"verify_failed={failed} install_failed={not_installed}", flush=True)
    return 1 if failed or not_installed else 0


if __name__ == "__main__":
    sys.exit(main())
