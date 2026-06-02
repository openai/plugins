#!/usr/bin/env python3
"""Render a Codex Security markdown report as a self-contained HTML file."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "report_template_inlined.html"
REQUIRED_TEMPLATE_TOKENS = ("{escaped_title}", "{toc_items}", "{report_body}")


def slugify(text: str) -> str:
    slug = re.sub(r"<[^>]+>", "", text).strip().lower()
    slug = re.sub(r"`([^`]+)`", r"\1", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "section"


def sanitize_href(href: str) -> str:
    decoded = html.unescape(href).strip()
    decoded = "".join(ch for ch in decoded if ch >= " " and ch != "\x7f")
    parsed = urlsplit(decoded)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto", "file"}:
        return "#"
    return html.escape(decoded, quote=True)


def inline_markdown(text: str) -> str:
    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        href = sanitize_href(match.group(2))
        return f'<a href="{href}">{label}</a>'

    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, escaped)
    return escaped


def format_table_cell(cell: str, row: list[str], index: int, header: list[str]) -> str:
    field = row[0].lower() if row else ""
    column = header[index].lower() if index < len(header) else ""
    if cell.lower() in {"critical", "high", "medium", "low"} and (
        (index > 0 and field == "severity") or column == "severity"
    ):
        return cell.capitalize()
    if cell.lower() in {"high", "medium", "low"} and (
        (index > 0 and field == "confidence") or column == "confidence"
    ):
        return cell.capitalize()
    return cell


def render_table(lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        header = rows[0]
        body = rows[2:]
    else:
        header = []
        body = rows

    out = ["<table>"]
    if header:
        out.append("<thead><tr>")
        out.extend(f"<th>{inline_markdown(cell)}</th>" for cell in header)
        out.append("</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append("<tr>")
        out.extend(
            f"<td>{inline_markdown(format_table_cell(cell, row, index, header))}</td>"
            for index, cell in enumerate(row)
        )
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def render_markdown(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    body: list[str] = []
    toc: list[tuple[int, str, str]] = []
    lines = markdown.splitlines()
    i = 0
    in_code = False
    code_lines: list[str] = []

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                body.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            body.append(render_table(table_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = slugify(title)
            toc.append((level, title, anchor))
            body.append(f'<h{level} id="{anchor}">{inline_markdown(title)}</h{level}>')
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:])
                i += 1
            body.append(
                "<ul>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ul>"
            )
            continue
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            body.append(
                "<ol>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ol>"
            )
            continue
        elif not line.strip():
            body.append("")
        else:
            body.append(f"<p>{inline_markdown(line)}</p>")
        i += 1

    return "\n".join(body), toc


def read_template(template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    missing = [token for token in REQUIRED_TEMPLATE_TOKENS if token not in template]
    if missing:
        missing_tokens = ", ".join(missing)
        raise ValueError(f"report template {template_path} is missing: {missing_tokens}")
    return template


def render_page(title: str, markdown: str, template_path: Path = DEFAULT_TEMPLATE) -> str:
    body, toc = render_markdown(markdown)
    toc_items = "\n".join(
        f'<li class="toc-item depth-{level}"><a href="#{anchor}">{inline_markdown(text)}</a></li>'
        for level, text, anchor in toc
        if level <= 3
    )
    return (
        read_template(template_path)
        .replace("{escaped_title}", html.escape(title))
        .replace("{toc_items}", toc_items)
        .replace("{report_body}", body)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a markdown scan report to HTML.")
    parser.add_argument("--report-md", required=True)
    parser.add_argument("--report-html", required=True)
    parser.add_argument("--title", default="Codex Security Scan Report")
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="Path to the Codex Security HTML report template.",
    )
    args = parser.parse_args()

    markdown = Path(args.report_md).read_text(encoding="utf-8")
    html_page = render_page(args.title, markdown, Path(args.template))
    Path(args.report_html).write_text(html_page, encoding="utf-8")


if __name__ == "__main__":
    main()
