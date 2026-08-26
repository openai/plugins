/* Dependency-free normalization for file-backed Google Docs trusted reads. */

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function unwrap(value) {
  if (isRecord(value?.structuredContent)) return value.structuredContent;
  if (isRecord(value?.result?.structuredContent)) return value.result.structuredContent;
  if (isRecord(value?.result)) return value.result;
  return value;
}

function findDocument(value) {
  const root = unwrap(value);
  const seen = new Set();
  const visit = (candidate) => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return null;
    seen.add(candidate);
    if (isRecord(candidate) && typeof (candidate.documentId ?? candidate.document_id) === "string" &&
        (candidate.tabs || candidate.body || candidate.revisionId || candidate.revision_id)) return candidate;
    for (const child of Array.isArray(candidate) ? candidate : Object.values(candidate)) {
      const found = visit(child);
      if (found) return found;
    }
    return null;
  };
  return visit(root);
}

function isPrivateUse(codePoint) {
  return (codePoint >= 0xE000 && codePoint <= 0xF8FF) ||
    (codePoint >= 0xF0000 && codePoint <= 0xFFFFD) ||
    (codePoint >= 0x100000 && codePoint <= 0x10FFFD);
}

function visibleText(value) {
  let output = "";
  for (const character of String(value ?? "")) {
    const codePoint = character.codePointAt(0);
    output += isPrivateUse(codePoint)
      ? `⟦PROTECTED_CONTROL U+${codePoint.toString(16).toUpperCase().padStart(4, "0")}⟧`
      : character;
  }
  return output;
}

function markdownLink(label, url) {
  const text = String(label ?? "").replace(/\n/g, " ").trim() || url;
  return `[${text.replace(/([\\\[\]])/g, "\\$1")}](${url})`;
}

function elementText(element) {
  if (element.textRun) {
    const content = visibleText(element.textRun.content);
    const url = element.textRun.textStyle?.link?.url;
    return url ? markdownLink(content, url) : content;
  }
  if (element.person) {
    const properties = element.person.personProperties ?? {};
    const label = properties.name ?? properties.email ?? "person";
    return properties.email ? `@${label} <${properties.email}>` : `@${label}`;
  }
  if (element.dateElement) {
    return element.dateElement.dateElementProperties?.displayText ?? "[DATE]";
  }
  if (element.richLink) {
    const properties = element.richLink.richLinkProperties ?? {};
    return properties.uri ? markdownLink(properties.title ?? properties.uri, properties.uri) : `[RICH_LINK ${properties.title ?? ""}]`;
  }
  if (element.inlineObjectElement) return `[INLINE_OBJECT ${element.inlineObjectElement.inlineObjectId ?? ""}]`;
  if (element.footnoteReference) return `[FOOTNOTE ${element.footnoteReference.footnoteId ?? ""}]`;
  if (element.horizontalRule) return "[HORIZONTAL_RULE]";
  if (element.equation) return "[EQUATION]";
  return "";
}

function tabRecords(document) {
  if (Array.isArray(document.tabs) && document.tabs.length > 0) {
    return document.tabs.map((tab, index) => ({
      tabId: tab.tabId ?? tab.tab_id ?? tab.tabProperties?.tabId ?? tab.tab_properties?.tab_id ?? null,
      title: tab.title ?? tab.tabProperties?.title ?? tab.tab_properties?.title ?? `Tab ${index + 1}`,
      body: tab.body ?? tab.documentTab?.body ?? tab.document_tab?.body ?? null,
    }));
  }
  return [{ tabId: null, title: "Document", body: document.body ?? null }];
}

function controlsForParagraph(controls, paragraph) {
  return controls.filter((control) =>
    (control.tabId ?? null) === (paragraph.tabId ?? null) &&
    (control.segmentId ?? null) === (paragraph.segmentId ?? null) &&
    Number.isInteger(control.startIndex) && Number.isInteger(control.endIndex) &&
    Number.isInteger(paragraph.startIndex) && Number.isInteger(paragraph.endIndex) &&
    control.startIndex >= paragraph.startIndex && control.endIndex <= paragraph.endIndex,
  ).map((control) => ({
    classification: control.classification,
    fidelityClass: control.fidelityClass,
    startIndex: control.startIndex,
    endIndex: control.endIndex,
    codePoints: control.codePoints ?? [],
    dropdownId: control.dropdownId ?? null,
    selectedValue: control.selectedValue ?? null,
  }));
}

function normalizeParagraph(structuralElement, context, path, controls, ordinal) {
  const paragraph = structuralElement.paragraph;
  const bullet = paragraph.bullet ?? null;
  const record = {
    paragraphId: `P${String(ordinal).padStart(5, "0")}`,
    path,
    tabId: context.tabId,
    tabTitle: context.tabTitle,
    segmentId: context.segmentId,
    startIndex: structuralElement.startIndex ?? structuralElement.start_index ?? null,
    endIndex: structuralElement.endIndex ?? structuralElement.end_index ?? null,
    namedStyleType: paragraph.paragraphStyle?.namedStyleType ?? paragraph.paragraph_style?.named_style_type ?? null,
    isListItem: Boolean(bullet),
    listId: bullet?.listId ?? bullet?.list_id ?? null,
    nestingLevel: bullet?.nestingLevel ?? bullet?.nesting_level ?? null,
    table: context.table,
    text: (paragraph.elements ?? []).map(elementText).join("").replace(/\n$/, ""),
  };
  return { ...record, protectedControls: controlsForParagraph(controls, record) };
}

function collectParagraphs(document, controls, selectedTabId) {
  const paragraphs = [];
  const visitContent = (content, context, path) => {
    for (let index = 0; index < (content ?? []).length; index += 1) {
      const structuralElement = content[index];
      const elementPath = `${path}[${index}]`;
      if (structuralElement.paragraph?.elements) {
        paragraphs.push(normalizeParagraph(structuralElement, context, elementPath, controls, paragraphs.length + 1));
      } else if (structuralElement.table?.tableRows) {
        const tableStartIndex = structuralElement.startIndex ?? structuralElement.start_index ?? null;
        structuralElement.table.tableRows.forEach((row, rowIndex) => {
          (row.tableCells ?? []).forEach((cell, columnIndex) => {
            visitContent(cell.content ?? [], {
              ...context,
              table: { tableStartIndex, rowIndex, columnIndex },
            }, `${elementPath}.table.rows[${rowIndex}].cells[${columnIndex}].content`);
          });
        });
      } else if (structuralElement.tableOfContents?.content) {
        visitContent(structuralElement.tableOfContents.content, context, `${elementPath}.tableOfContents.content`);
      }
    }
  };

  for (const tab of tabRecords(document)) {
    if (selectedTabId !== null && tab.tabId !== selectedTabId) continue;
    visitContent(tab.body?.content ?? [], {
      tabId: tab.tabId,
      tabTitle: tab.title,
      segmentId: null,
      table: null,
    }, `tabs.${tab.tabId ?? "body"}.body.content`);
  }

  for (const [collectionName, values] of [["headers", document.headers], ["footers", document.footers], ["footnotes", document.footnotes]]) {
    if (!isRecord(values)) continue;
    for (const [segmentId, segment] of Object.entries(values)) {
      visitContent(segment.content ?? [], {
        tabId: null,
        tabTitle: collectionName,
        segmentId,
        table: null,
      }, `${collectionName}.${segmentId}.content`);
    }
  }
  return paragraphs;
}

function controlLabel(control) {
  const codePoints = control.codePoints?.length ? ` ${control.codePoints.join(",")}` : "";
  const selected = control.selectedValue !== null && control.selectedValue !== undefined ? ` selected=${JSON.stringify(control.selectedValue)}` : "";
  return `${control.classification}/${control.fidelityClass}@${control.startIndex}:${control.endIndex}${codePoints}${selected}`;
}

export function renderNormalizedDocumentText(normalized) {
  const lines = [
    `# ${normalized.document.title ?? "Google Doc"}`,
    "",
    `- Document ID: ${normalized.document.documentId}`,
    `- Revision ID: ${normalized.document.revisionId ?? "unavailable"}`,
    `- Selected tab: ${normalized.selectedTabId ?? "all"}`,
    `- Protected controls: ${normalized.controlSummary.total}`,
    `- Opaque controls: ${normalized.controlSummary.opaque}`,
    `- Authoritative dropdowns: ${normalized.controlSummary.authoritativeDropdowns}`,
    "",
    "Protected-control annotations are preservation instructions. Do not insert their displayed placeholder text to recreate a native control.",
    "",
  ];
  let currentSection = Symbol("none");
  for (const paragraph of normalized.paragraphs) {
    const section = `${paragraph.tabTitle ?? "Document"}\u0000${paragraph.tabId ?? "body"}\u0000${paragraph.segmentId ?? ""}`;
    if (section !== currentSection) {
      currentSection = section;
      lines.push(`## ${paragraph.tabTitle ?? "Document"} (${paragraph.tabId ?? "body"})`, "");
    }
    const metadata = [
      paragraph.paragraphId,
      `${paragraph.startIndex ?? "?"}:${paragraph.endIndex ?? "?"}`,
      paragraph.namedStyleType ?? "NORMAL_TEXT",
      paragraph.isListItem ? `LIST id=${paragraph.listId ?? "?"} level=${paragraph.nestingLevel ?? 0}` : null,
      paragraph.table ? `TABLE row=${paragraph.table.rowIndex} col=${paragraph.table.columnIndex}` : null,
    ].filter(Boolean).join(" | ");
    lines.push(`[${metadata}]`);
    if (paragraph.protectedControls.length > 0) {
      lines.push(`⟦PROTECTED: ${paragraph.protectedControls.map(controlLabel).join("; ")} — preserve this control and its containing structure⟧`);
    }
    lines.push(paragraph.text || "⟦EMPTY PARAGRAPH⟧", "");
  }
  return `${lines.join("\n")}\n`;
}

export function normalizeGoogleDocumentRead({ documentResult, trustedReadContext, selectedTabId = null } = {}) {
  const document = findDocument(documentResult);
  if (!document) throw new Error("Could not locate the Google Docs document resource");
  const controls = trustedReadContext?.derivedControlInventory?.controls ?? [];
  const paragraphs = collectParagraphs(document, controls, selectedTabId);
  const normalized = {
    version: 1,
    kind: "google-docs-normalized-read",
    document: {
      documentId: document.documentId ?? document.document_id,
      title: document.title ?? null,
      revisionId: document.revisionId ?? document.revision_id ?? null,
      documentUrl: document.documentUrl ?? document.document_url ?? document.url ?? null,
    },
    selectedTabId,
    controlSummary: {
      total: controls.length,
      opaque: trustedReadContext?.derivedControlInventory?.opaqueControlCount ?? 0,
      authoritativeDropdowns: trustedReadContext?.derivedControlInventory?.authoritativeDropdownCount ?? 0,
      affectedParagraphs: paragraphs.filter((paragraph) => paragraph.protectedControls.length > 0).length,
    },
    paragraphs,
  };
  return { normalized, markdown: renderNormalizedDocumentText(normalized) };
}
