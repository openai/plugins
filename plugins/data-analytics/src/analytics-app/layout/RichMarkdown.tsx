import {
  $convertFromMarkdownString,
  $convertToMarkdownString,
  BOLD_STAR,
  HEADING,
  INLINE_CODE,
  LINK,
  ORDERED_LIST,
  QUOTE,
  UNORDERED_LIST,
  type Transformer
} from "@lexical/markdown";
import { HistoryPlugin } from "@lexical/react/LexicalHistoryPlugin";
import { LexicalComposer } from "@lexical/react/LexicalComposer";
import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import { ContentEditable } from "@lexical/react/LexicalContentEditable";
import { LexicalErrorBoundary } from "@lexical/react/LexicalErrorBoundary";
import { MarkdownShortcutPlugin } from "@lexical/react/LexicalMarkdownShortcutPlugin";
import { OnChangePlugin } from "@lexical/react/LexicalOnChangePlugin";
import { RichTextPlugin } from "@lexical/react/LexicalRichTextPlugin";
import { LinkNode } from "@lexical/link";
import { ListItemNode, ListNode } from "@lexical/list";
import { HeadingNode, QuoteNode } from "@lexical/rich-text";
import {
  $getSelection,
  $isRangeSelection,
  COMMAND_PRIORITY_HIGH,
  KEY_ESCAPE_COMMAND,
  PASTE_COMMAND
} from "lexical";
import {
  type CSSProperties,
  type KeyboardEvent as ReactKeyboardEvent,
  type MouseEvent as ReactMouseEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState
} from "react";

const MARKDOWN_TRANSFORMERS: Transformer[] = [
  HEADING,
  QUOTE,
  UNORDERED_LIST,
  ORDERED_LIST,
  BOLD_STAR,
  INLINE_CODE,
  LINK
];
const MARKDOWN_COMMIT_DEBOUNCE_MS = 180;

type RichMarkdownFocusPoint = {
  clientX: number;
  clientY: number;
};

type CaretPositionDocument = Document & {
  caretPositionFromPoint?: (
    x: number,
    y: number
  ) => { offset: number; offsetNode: Node } | null;
  caretRangeFromPoint?: (x: number, y: number) => Range | null;
};

export type RichMarkdownActivation = "click" | "doubleClick" | "manual";
export type RichMarkdownVariant = "cellHeader" | "pageHeader" | "reportBlock";

export type RichMarkdownProps = {
  activation?: RichMarkdownActivation;
  ariaLabel: string;
  className?: string;
  isEditMode?: boolean;
  markdown: string;
  minRows?: number;
  onCommit?: (nextMarkdown: string) => void;
  onMarkdownChange: (nextMarkdown: string) => void;
  onRequestEditMode?: () => void;
  placeholder: string;
  variant?: RichMarkdownVariant;
};

const richMarkdownTheme = {
  heading: {
    h1: "rich-markdown-heading rich-markdown-heading-1",
    h2: "rich-markdown-heading rich-markdown-heading-2",
    h3: "rich-markdown-heading rich-markdown-heading-3"
  },
  link: "rich-markdown-link",
  list: {
    listitem: "rich-markdown-list-item",
    ol: "rich-markdown-list",
    ul: "rich-markdown-list"
  },
  quote: "rich-markdown-quote",
  text: {
    bold: "rich-markdown-bold",
    code: "rich-markdown-inline-code"
  }
};

function renderMarkdownInline(text: string) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={`${part}-${index}`}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      return <code key={`${part}-${index}`}>{part.slice(1, -1)}</code>;
    }
    const linkMatch = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
    if (linkMatch) {
      return (
        <a href={linkMatch[2]} key={`${part}-${index}`} rel="noreferrer" target="_blank">
          {linkMatch[1]}
        </a>
      );
    }
    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

type MarkdownTableAlignment = "center" | "left" | "right";

function splitMarkdownTableRow(line: string) {
  const trimmed = line.trim();
  const withoutLeadingPipe = trimmed.startsWith("|") ? trimmed.slice(1) : trimmed;
  const withoutOuterPipes = withoutLeadingPipe.endsWith("|")
    ? withoutLeadingPipe.slice(0, -1)
    : withoutLeadingPipe;
  return withoutOuterPipes
    .split(/(?<!\\)\|/g)
    .map((cell) => cell.replace(/\\\|/g, "|").trim());
}

function parseMarkdownTableSeparator(line: string): MarkdownTableAlignment[] | null {
  const cells = splitMarkdownTableRow(line);
  if (!cells.length) return null;
  const alignments: MarkdownTableAlignment[] = [];
  for (const cell of cells) {
    if (!/^:?-{3,}:?$/.test(cell)) return null;
    if (cell.startsWith(":") && cell.endsWith(":")) alignments.push("center");
    else if (cell.endsWith(":")) alignments.push("right");
    else alignments.push("left");
  }
  return alignments;
}

function isMarkdownTableStart(lines: string[], index: number) {
  const header = lines[index]?.trim() ?? "";
  const separator = lines[index + 1]?.trim() ?? "";
  return header.includes("|") && Boolean(parseMarkdownTableSeparator(separator));
}

function isMarkdownTableRow(line: string) {
  const trimmed = line.trim();
  return Boolean(trimmed) && trimmed.includes("|");
}

export function normalizeInlineOrderedListMarkers(markdown: string) {
  return markdown
    .replace(/\u00a0/g, " ")
    .split(/\r?\n/)
    .map((line) => {
      if (!/^\s*\d+[.)]\s+/.test(line)) return line;
      return line.replace(/([^\n])[\t ]+(?=\d+[.)]\s+)/g, "$1\n");
    })
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
    nodes.push(<p key={`p-${nodes.length}`}>{renderMarkdownInline(paragraph.join(" "))}</p>);
    paragraph = [];
  }

  function flushList() {
    if (!listItems.length) return;
    nodes.push(
      <ul key={`ul-${nodes.length}`}>
        {listItems.map((item, index) => (
          <li key={`${item}-${index}`}>{renderMarkdownInline(item)}</li>
        ))}
      </ul>
    );
    listItems = [];
  }

  function flushOrderedList() {
    if (!orderedListItems.length) return;
    nodes.push(
      <ol key={`ol-${nodes.length}`}>
        {orderedListItems.map((item, index) => (
          <li key={`${item}-${index}`}>{renderMarkdownInline(item)}</li>
        ))}
      </ol>
    );
    orderedListItems = [];
  }

  function flushBlockquote() {
    if (!blockquote.length) return;
    nodes.push(
      <blockquote key={`blockquote-${nodes.length}`}>
        {blockquote.map((item, index) => (
          <p key={`${item}-${index}`}>{renderMarkdownInline(item)}</p>
        ))}
      </blockquote>
    );
    blockquote = [];
  }

  function flushTextRuns() {
    flushParagraph();
    flushList();
    flushOrderedList();
    flushBlockquote();
  }

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushBlockquote();
      continue;
    }
    if (isMarkdownTableStart(lines, index)) {
      flushTextRuns();
      const headers = splitMarkdownTableRow(lines[index]);
      const alignments = parseMarkdownTableSeparator(lines[index + 1]) ?? [];
      const rows: string[][] = [];
      index += 2;
      while (index < lines.length && isMarkdownTableRow(lines[index])) {
        rows.push(splitMarkdownTableRow(lines[index]));
        index += 1;
      }
      index -= 1;
      nodes.push(
        <div className="rich-markdown-table-scroll" key={`table-${nodes.length}`}>
          <table className="rich-markdown-table">
            <thead>
              <tr>
                {headers.map((header, headerIndex) => (
                  <th
                    key={`${header}-${headerIndex}`}
                    style={{ textAlign: alignments[headerIndex] ?? "left" }}
                  >
                    {renderMarkdownInline(header)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={`row-${rowIndex}`}>
                  {headers.map((_, cellIndex) => (
                    <td
                      key={`cell-${rowIndex}-${cellIndex}`}
                      style={{ textAlign: alignments[cellIndex] ?? "left" }}
                    >
                      {renderMarkdownInline(row[cellIndex] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      flushTextRuns();
      nodes.push(<hr key={`hr-${nodes.length}`} />);
      continue;
    }
    const headingMatch = /^(#{1,3})\s+(.+)$/.exec(trimmed);
    if (headingMatch) {
      flushTextRuns();
      const level = headingMatch[1].length;
      const content = renderMarkdownInline(headingMatch[2]);
      if (level === 1) nodes.push(<h1 key={`h-${nodes.length}`}>{content}</h1>);
      else if (level === 2) nodes.push(<h2 key={`h-${nodes.length}`}>{content}</h2>);
      else nodes.push(<h3 key={`h-${nodes.length}`}>{content}</h3>);
      continue;
    }
    const blockquoteMatch = /^>\s?(.*)$/.exec(trimmed);
    if (blockquoteMatch) {
      flushParagraph();
      flushList();
      flushOrderedList();
      const content = blockquoteMatch[1].trim();
      if (content) blockquote.push(content);
      continue;
    }
    const listMatch = /^[-*]\s+(.+)$/.exec(trimmed);
    if (listMatch) {
      flushParagraph();
      flushOrderedList();
      flushBlockquote();
      listItems.push(listMatch[1]);
      continue;
    }
    const orderedListMatch = /^\d+[.)]\s+(.+)$/.exec(trimmed);
    if (orderedListMatch) {
      flushParagraph();
      flushList();
      flushBlockquote();
      orderedListItems.push(orderedListMatch[1]);
      continue;
    }
    flushList();
    flushOrderedList();
    flushBlockquote();
    paragraph.push(trimmed);
  }

  flushTextRuns();

  return <>{nodes.length ? nodes : <p className="markdown-placeholder">Double-click to edit text.</p>}</>;
}

function normalizeEditorMarkdown(markdown: string) {
  return normalizeInlineOrderedListMarkers(markdown)
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function htmlToMarkdown(html: string) {
  if (typeof DOMParser === "undefined") return "";
  const document = new DOMParser().parseFromString(html, "text/html");

  function childrenToMarkdown(node: Node): string {
    return Array.from(node.childNodes).map(nodeToMarkdown).join("");
  }

  function nodeToMarkdown(node: Node): string {
    if (node.nodeType === Node.TEXT_NODE) return node.textContent ?? "";
    if (!(node instanceof HTMLElement)) return childrenToMarkdown(node);

    const content = childrenToMarkdown(node).trim();
    switch (node.tagName.toLowerCase()) {
      case "a": {
        const href = node.getAttribute("href");
        return href && content ? `[${content}](${href})` : content;
      }
      case "b":
      case "strong":
        return content ? `**${content}**` : "";
      case "br":
        return "\n";
      case "code":
        return content ? `\`${content.replaceAll("`", "'")}\`` : "";
      case "h1":
        return content ? `# ${content}\n\n` : "";
      case "h2":
        return content ? `## ${content}\n\n` : "";
      case "h3":
        return content ? `### ${content}\n\n` : "";
      case "li":
        return content ? `- ${content}\n` : "";
      case "ol":
      case "ul":
        return `${childrenToMarkdown(node).trim()}\n\n`;
      case "div":
      case "p":
      case "section":
        return content ? `${content}\n\n` : "";
      default:
        return content;
    }
  }

  return normalizeEditorMarkdown(childrenToMarkdown(document.body));
}

function MarkdownChangePlugin({ onDraftChange }: { onDraftChange: (nextMarkdown: string) => void }) {
  return (
    <OnChangePlugin
      ignoreSelectionChange
      onChange={(editorState) => {
        editorState.read(() => {
          onDraftChange(normalizeEditorMarkdown($convertToMarkdownString(MARKDOWN_TRANSFORMERS)));
        });
      }}
    />
  );
}

function rangeFromPoint(
  document: CaretPositionDocument,
  point: RichMarkdownFocusPoint
): Range | null {
  const position = document.caretPositionFromPoint?.(point.clientX, point.clientY);
  if (position) {
    const range = document.createRange();
    range.setStart(position.offsetNode, position.offset);
    range.collapse(true);
    return range;
  }
  return document.caretRangeFromPoint?.(point.clientX, point.clientY) ?? null;
}

function focusContentEditableAtPoint(
  rootElement: HTMLElement,
  point: RichMarkdownFocusPoint
): boolean {
  const ownerDocument = rootElement.ownerDocument as CaretPositionDocument;
  const range = rangeFromPoint(ownerDocument, point);
  if (!range || !rootElement.contains(range.startContainer)) return false;
  const selection = ownerDocument.defaultView?.getSelection();
  if (!selection) return false;

  rootElement.focus({ preventScroll: true });
  selection.removeAllRanges();
  selection.addRange(range);
  return true;
}

function FocusOnMountPlugin({ focusPoint }: { focusPoint: RichMarkdownFocusPoint | null }) {
  const [editor] = useLexicalComposerContext();

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      const rootElement = editor.getRootElement();
      if (rootElement && focusPoint && focusContentEditableAtPoint(rootElement, focusPoint)) {
        return;
      }
      editor.focus(() => {}, { defaultSelection: "rootEnd" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [editor, focusPoint]);

  return null;
}

function CommitOnEscapePlugin({ onCommit }: { onCommit: () => void }) {
  const [editor] = useLexicalComposerContext();

  useEffect(() => {
    return editor.registerCommand(
      KEY_ESCAPE_COMMAND,
      (event) => {
        event?.preventDefault();
        onCommit();
        return true;
      },
      COMMAND_PRIORITY_HIGH
    );
  }, [editor, onCommit]);

  return null;
}

function PasteSanitizerPlugin() {
  const [editor] = useLexicalComposerContext();

  useEffect(() => {
    return editor.registerCommand(
      PASTE_COMMAND,
      (event) => {
        if (!("clipboardData" in event) || !event.clipboardData) return false;
        const html = event.clipboardData.getData("text/html");
        if (!html) return false;
        const markdown = htmlToMarkdown(html);
        if (!markdown) return false;
        event.preventDefault();
        editor.update(() => {
          const selection = $getSelection();
          if ($isRangeSelection(selection)) selection.insertText(markdown);
        });
        return true;
      },
      COMMAND_PRIORITY_HIGH
    );
  }, [editor]);

  return null;
}

export function RichMarkdown({
  activation = "doubleClick",
  ariaLabel,
  className,
  isEditMode = false,
  markdown,
  minRows = 1,
  onCommit,
  onMarkdownChange,
  onRequestEditMode,
  placeholder,
  variant = "reportBlock"
}: RichMarkdownProps) {
  const editorId = useId();
  const [isEditing, setIsEditing] = useState(false);
  const [editSessionKey, setEditSessionKey] = useState(0);
  const initialMarkdownRef = useRef(markdown);
  const latestDraftRef = useRef(markdown);
  const lastEmittedRef = useRef(markdown);
  const debounceRef = useRef<number | null>(null);
  const focusPointRef = useRef<RichMarkdownFocusPoint | null>(null);
  const isEditingRef = useRef(isEditing);
  const flushRef = useRef<() => void>(() => {});
  const displayMarkdown = markdown.trim() ? markdown : placeholder;
  const variantClassName = `rich-markdown-${variant}`;
  const canEdit = isEditMode || typeof onRequestEditMode === "function";

  useEffect(() => {
    if (!isEditing) {
      latestDraftRef.current = markdown;
      lastEmittedRef.current = markdown;
    }
  }, [isEditing, markdown]);

  useEffect(() => {
    isEditingRef.current = isEditing;
  }, [isEditing]);

  const emitMarkdownChange = useCallback((nextMarkdown: string) => {
    if (nextMarkdown === lastEmittedRef.current) return;
    lastEmittedRef.current = nextMarkdown;
    onMarkdownChange(nextMarkdown);
  }, [onMarkdownChange]);

  const flushMarkdownChange = useCallback(() => {
    if (debounceRef.current !== null) {
      window.clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }
    const nextMarkdown = latestDraftRef.current;
    emitMarkdownChange(nextMarkdown);
    onCommit?.(nextMarkdown);
  }, [emitMarkdownChange, onCommit]);

  flushRef.current = flushMarkdownChange;

  useEffect(() => {
    return () => {
      if (debounceRef.current !== null) window.clearTimeout(debounceRef.current);
      if (isEditingRef.current) flushRef.current();
    };
  }, []);

  const scheduleMarkdownChange = useCallback((nextMarkdown: string) => {
    latestDraftRef.current = nextMarkdown;
    if (debounceRef.current !== null) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      debounceRef.current = null;
      emitMarkdownChange(latestDraftRef.current);
    }, MARKDOWN_COMMIT_DEBOUNCE_MS);
  }, [emitMarkdownChange]);

  const startEditing = useCallback((focusPoint: RichMarkdownFocusPoint | null = null) => {
    initialMarkdownRef.current = markdown;
    latestDraftRef.current = markdown;
    lastEmittedRef.current = markdown;
    focusPointRef.current = focusPoint;
    setEditSessionKey((current) => current + 1);
    setIsEditing(true);
  }, [markdown]);

  const handlePreviewClick = useCallback((event: ReactMouseEvent<HTMLDivElement>) => {
    if (!isEditMode || activation === "manual") return;
    event.preventDefault();
    window.getSelection()?.removeAllRanges();
    startEditing({ clientX: event.clientX, clientY: event.clientY });
  }, [activation, isEditMode, startEditing]);

  const handlePreviewDoubleClick = useCallback((event: ReactMouseEvent<HTMLDivElement>) => {
    if (!canEdit) return;
    if (activation === "manual" && isEditMode) return;
    event.preventDefault();
    event.stopPropagation();
    window.getSelection()?.removeAllRanges();
    if (!isEditMode) onRequestEditMode?.();
    startEditing({ clientX: event.clientX, clientY: event.clientY });
  }, [activation, canEdit, isEditMode, onRequestEditMode, startEditing]);

  const handlePreviewMouseDownCapture = useCallback((event: ReactMouseEvent<HTMLDivElement>) => {
    if (!canEdit) return;
    if (!isEditMode && activation !== "manual" && event.detail > 1) {
      event.preventDefault();
      event.stopPropagation();
      window.getSelection()?.removeAllRanges();
      onRequestEditMode?.();
      startEditing({ clientX: event.clientX, clientY: event.clientY });
    }
  }, [activation, canEdit, isEditMode, onRequestEditMode, startEditing]);

  const commitAndClose = useCallback(() => {
    flushMarkdownChange();
    setIsEditing(false);
  }, [flushMarkdownChange]);

  const initialConfig = useMemo(() => ({
    editorState: () => {
      $convertFromMarkdownString(initialMarkdownRef.current, MARKDOWN_TRANSFORMERS);
    },
    namespace: `DataScienceRichMarkdown-${editorId}-${editSessionKey}`,
    nodes: [HeadingNode, QuoteNode, ListNode, ListItemNode, LinkNode],
    onError(error: Error) {
      throw error;
    },
    theme: richMarkdownTheme
  }), [editSessionKey, editorId]);

  const interactiveProps =
    !canEdit
      ? {}
      : isEditMode && activation !== "manual"
      ? { onClick: handlePreviewClick }
      : activation !== "manual" || onRequestEditMode
        ? { onDoubleClick: handlePreviewDoubleClick }
        : {};

  if (isEditing) {
    return (
      <div
        className={`rich-markdown-editor-shell viz-card__no-drag ${variantClassName}`.trim()}
        style={{ "--rich-markdown-min-height": `${Math.max(1, minRows) * 22}px` } as CSSProperties}
      >
        <LexicalComposer initialConfig={initialConfig} key={editSessionKey}>
          <RichTextPlugin
            contentEditable={
              <ContentEditable
                aria-label={ariaLabel}
                className={`markdown-render markdown-edit-target rich-markdown rich-markdown-editor viz-card__no-drag ${variantClassName} ${className ?? ""}`.trim()}
                onBlur={commitAndClose}
                spellCheck
              />
            }
            ErrorBoundary={LexicalErrorBoundary}
            placeholder={
              <div className={`markdown-render rich-markdown-placeholder ${variantClassName} ${className ?? ""}`.trim()}>
                <RichMarkdownPreview markdown={placeholder} />
              </div>
            }
          />
          <HistoryPlugin />
          <FocusOnMountPlugin focusPoint={focusPointRef.current} />
          <MarkdownShortcutPlugin transformers={MARKDOWN_TRANSFORMERS} />
          <MarkdownChangePlugin onDraftChange={scheduleMarkdownChange} />
          <CommitOnEscapePlugin onCommit={commitAndClose} />
          <PasteSanitizerPlugin />
        </LexicalComposer>
      </div>
    );
  }

  function handleKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (!canEdit) return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (!isEditMode) onRequestEditMode?.();
      startEditing();
    }
  }

  return (
    <div
      aria-label={canEdit ? ariaLabel : undefined}
      className={`markdown-render markdown-edit-target rich-markdown rich-markdown-preview viz-card__no-drag ${variantClassName} ${className ?? ""}`.trim()}
      data-rich-markdown-activation={activation}
      data-rich-markdown-edit-mode={isEditMode ? "true" : "false"}
      data-rich-markdown-variant={variant}
      onKeyDown={handleKeyDown}
      onMouseDownCapture={handlePreviewMouseDownCapture}
      role={canEdit ? "button" : undefined}
      tabIndex={canEdit ? 0 : undefined}
      {...interactiveProps}
    >
      <RichMarkdownPreview markdown={displayMarkdown} />
    </div>
  );
}
