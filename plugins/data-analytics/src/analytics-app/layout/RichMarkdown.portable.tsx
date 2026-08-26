import type { ReactNode } from "react";

type RichMarkdownProps = {
  activation?: "click" | "doubleClick" | "manual";
  ariaLabel: string;
  className?: string;
  isEditMode?: boolean;
  markdown: string;
  minRows?: number;
  onCommit?: (nextMarkdown: string) => void;
  onMarkdownChange: (nextMarkdown: string) => void;
  onRequestEditMode?: () => void;
  placeholder: string;
  variant?: "cellHeader" | "pageHeader" | "reportBlock";
};

function safeHref(value: string): string | null {
  const href = value.trim();
  if (href.startsWith("#") || /^(https?:|mailto:)/i.test(href)) return href;
  return null;
}
function renderInline(text: string) {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={`${index}:${part}`}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      return <code key={`${index}:${part}`}>{part.slice(1, -1)}</code>;
    }
    const link = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
    if (link) {
      const href = safeHref(link[2] ?? "");
      return href
        ? <a href={href} key={`${index}:${part}`} rel="noreferrer" target="_blank">{link[1]}</a>
        : <span key={`${index}:${part}`}>{link[1]}</span>;
    }
    return <span key={`${index}:${part}`}>{part}</span>;
  });
}

function splitTableRow(line: string) {
  const trimmed = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  return trimmed.split(/(?<!\\)\|/g).map((cell) => cell.replace(/\\\|/g, "|").trim());
}

function tableAlignments(line: string): Array<"center" | "left" | "right"> | null {
  const cells = splitTableRow(line);
  if (!cells.length || cells.some((cell) => !/^:?-{3,}:?$/.test(cell))) return null;
  return cells.map((cell) => cell.startsWith(":") && cell.endsWith(":")
    ? "center"
    : cell.endsWith(":")
      ? "right"
      : "left");
}

export function normalizeInlineOrderedListMarkers(markdown: string) {
  return markdown
    .replace(/\u00a0/g, " ")
    .split(/\r?\n/)
    .map((line) => /^\s*\d+[.)]\s+/.test(line)
      ? line.replace(/([^\n])[\t ]+(?=\d+[.)]\s+)/g, "$1\n")
      : line)
    .join("\n");
}

export function RichMarkdownPreview({ markdown }: { markdown: string }) {
  const lines = normalizeInlineOrderedListMarkers(markdown).split(/\r?\n/);
  const nodes: ReactNode[] = [];
  let paragraph: string[] = [];
  let listItems: string[] = [];
  let orderedListItems: string[] = [];
  let blockquote: string[] = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    nodes.push(<p key={`p-${nodes.length}`}>{renderInline(paragraph.join(" "))}</p>);
    paragraph = [];
  }

  function flushList() {
    if (!listItems.length) return;
    nodes.push(<ul key={`ul-${nodes.length}`}>{listItems.map((item, index) => <li key={`${item}-${index}`}>{renderInline(item)}</li>)}</ul>);
    listItems = [];
  }

  function flushOrderedList() {
    if (!orderedListItems.length) return;
    nodes.push(<ol key={`ol-${nodes.length}`}>{orderedListItems.map((item, index) => <li key={`${item}-${index}`}>{renderInline(item)}</li>)}</ol>);
    orderedListItems = [];
  }

  function flushBlockquote() {
    if (!blockquote.length) return;
    nodes.push(<blockquote key={`blockquote-${nodes.length}`}>{blockquote.map((item, index) => <p key={`${item}-${index}`}>{renderInline(item)}</p>)}</blockquote>);
    blockquote = [];
  }

  function flushTextRuns() {
    flushParagraph();
    flushList();
    flushOrderedList();
    flushBlockquote();
  }

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index] ?? "";
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushBlockquote();
      continue;
    }

    const heading = /^(#{1,3})\s+(.+)$/.exec(trimmed);
    if (heading) {
      flushTextRuns();
      const content = renderInline(heading[2] ?? "");
      const level = heading[1]?.length ?? 1;
      nodes.push(level === 1
        ? <h1 key={`h-${index}`}>{content}</h1>
        : level === 2
          ? <h2 key={`h-${index}`}>{content}</h2>
          : <h3 key={`h-${index}`}>{content}</h3>);
      continue;
    }

    const alignments = lines[index + 1] ? tableAlignments(lines[index + 1] ?? "") : null;
    if (trimmed.includes("|") && alignments) {
      flushTextRuns();
      const headers = splitTableRow(line);
      const rows: string[][] = [];
      index += 2;
      while (index < lines.length && (lines[index] ?? "").trim().includes("|")) {
        rows.push(splitTableRow(lines[index] ?? ""));
        index += 1;
      }
      index -= 1;
      nodes.push(<div className="rich-markdown-table-scroll" key={`table-${index}`}>
        <table className="rich-markdown-table">
          <thead><tr>{headers.map((header, cell) => <th key={`${cell}:${header}`} style={{ textAlign: alignments[cell] ?? "left" }}>{renderInline(header)}</th>)}</tr></thead>
          <tbody>{rows.map((row, rowIndex) => <tr key={`row-${rowIndex}`}>{headers.map((_, cell) => <td key={`cell-${cell}`} style={{ textAlign: alignments[cell] ?? "left" }}>{renderInline(row[cell] ?? "")}</td>)}</tr>)}</tbody>
        </table>
      </div>);
      continue;
    }

    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      flushTextRuns();
      nodes.push(<hr key={`hr-${index}`}/>);
      continue;
    }

    const quoteMatch = /^>\s?(.*)$/.exec(trimmed);
    if (quoteMatch) {
      flushParagraph();
      flushList();
      flushOrderedList();
      const content = quoteMatch[1]?.trim() ?? "";
      if (content) blockquote.push(content);
      continue;
    }

    const unorderedMatch = /^[-*]\s+(.+)$/.exec(trimmed);
    if (unorderedMatch) {
      flushParagraph();
      flushOrderedList();
      flushBlockquote();
      listItems.push(unorderedMatch[1] ?? "");
      continue;
    }

    const orderedMatch = /^\d+[.)]\s+(.+)$/.exec(trimmed);
    if (orderedMatch) {
      flushParagraph();
      flushList();
      flushBlockquote();
      orderedListItems.push(orderedMatch[1] ?? "");
      continue;
    }

    flushList();
    flushOrderedList();
    flushBlockquote();
    paragraph.push(trimmed);
  }

  flushTextRuns();

  return <>{nodes.length ? nodes : <p className="markdown-placeholder">No content.</p>}</>;
}

export function RichMarkdown({
  ariaLabel,
  className,
  markdown,
  placeholder,
  variant = "reportBlock"
}: RichMarkdownProps) {
  const displayMarkdown = markdown.trim() ? markdown : placeholder;
  const variantClassName = `rich-markdown-${variant}`;
  return <div
    aria-label={ariaLabel}
    className={`markdown-render rich-markdown rich-markdown-preview viz-card__no-drag ${variantClassName} ${className ?? ""}`.trim()}
    data-rich-markdown-edit-mode="false"
    data-rich-markdown-variant={variant}
  >
    <RichMarkdownPreview markdown={displayMarkdown}/>
  </div>;
}
