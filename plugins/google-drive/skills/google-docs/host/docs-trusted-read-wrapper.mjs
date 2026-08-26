/* Read-only trusted wrapper for Google Docs document and control discovery. */

const CAPABILITIES = {
  getDocument: [
    "mcp__codex_apps__google_drive_get_document",
    "google_drive_get_document",
    "get_document",
  ],
  getDocumentDropdowns: [
    "mcp__codex_apps__google_drive_get_document_dropdowns",
    "google_drive_get_document_dropdowns",
    "get_document_dropdowns",
  ],
};

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function assert(condition, message) {
  if (!condition) throw new TrustedReadError(message);
}

function unwrapResult(value) {
  if (value?.isError === true) throw new TrustedReadError("Connector returned isError=true");
  if (isRecord(value?.structuredContent)) return value.structuredContent;
  if (isRecord(value?.result)) return value.result;
  return value;
}

function findFirstRecord(value, predicate) {
  const seen = new Set();
  const visit = (candidate) => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return null;
    seen.add(candidate);
    if (isRecord(candidate) && predicate(candidate)) return candidate;
    for (const child of Array.isArray(candidate) ? candidate : Object.values(candidate)) {
      const found = visit(child);
      if (found) return found;
    }
    return null;
  };
  return visit(value);
}

function collectRecords(value, predicate) {
  const output = [];
  const seen = new Set();
  const visit = (candidate) => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return;
    seen.add(candidate);
    if (isRecord(candidate) && predicate(candidate)) output.push(candidate);
    for (const child of Array.isArray(candidate) ? candidate : Object.values(candidate)) visit(child);
  };
  visit(value);
  return output;
}

function documentIdentity(value) {
  const root = unwrapResult(value);
  const record = findFirstRecord(root, (candidate) =>
    typeof (candidate.documentId ?? candidate.document_id) === "string" &&
    (candidate.revisionId || candidate.revision_id || candidate.body || candidate.tabs),
  );
  assert(record, "Could not locate Google Docs document identity");
  return {
    documentId: record.documentId ?? record.document_id,
    title: record.title ?? null,
    revisionId: record.revisionId ?? record.revision_id ?? null,
    documentUrl: record.documentUrl ?? record.document_url ?? record.url ?? null,
  };
}

function dropdownReadIdentity(value) {
  const root = unwrapResult(value);
  const record = findFirstRecord(root, (candidate) =>
    typeof (candidate.documentId ?? candidate.document_id) === "string" &&
    typeof (candidate.revisionId ?? candidate.revision_id) === "string" &&
    Array.isArray(candidate.dropdowns),
  );
  if (!record) return null;
  return {
    documentId: record.documentId ?? record.document_id,
    revisionId: record.revisionId ?? record.revision_id,
    tabId: record.tabId ?? record.tab_id ?? null,
  };
}

function normalizeOptions(value) {
  if (!Array.isArray(value)) return [];
  return value.map((option) => ({
    label: option.label ?? option.text ?? option.value ?? null,
    ...(option.color ?? option.colorStyle ?? option.color_style
      ? { color: option.color ?? option.colorStyle ?? option.color_style }
      : {}),
    ...(option.id ?? option.optionId ?? option.option_id
      ? { id: option.id ?? option.optionId ?? option.option_id }
      : {}),
  }));
}

function dropdownRecords(value) {
  const root = unwrapResult(value);
  const records = collectRecords(root, (candidate) => Array.isArray(candidate.dropdowns))
    .flatMap((candidate) => candidate.dropdowns);
  if (Array.isArray(root)) records.push(...root);
  return records.filter(isRecord).map((dropdown) => {
    const range = dropdown.range ?? dropdown.locator ?? {};
    return {
      classification: "dropdownControl",
      fidelityClass: "exact-readable",
      dropdownId: dropdown.dropdownId ?? dropdown.dropdown_id ?? null,
      tabId: dropdown.tabId ?? dropdown.tab_id ?? range.tabId ?? range.tab_id ?? null,
      segmentId: dropdown.segmentId ?? dropdown.segment_id ?? range.segmentId ?? range.segment_id ?? null,
      startIndex: dropdown.startIndex ?? dropdown.start_index ?? range.startIndex ?? range.start_index ?? null,
      endIndex: dropdown.endIndex ?? dropdown.end_index ?? range.endIndex ?? range.end_index ?? null,
      options: normalizeOptions(dropdown.options ?? dropdown.optionItems ?? dropdown.option_items),
      selectedValue: dropdown.selectedValue ?? dropdown.selected_value ?? dropdown.value ?? null,
      signature: dropdown.signature ?? dropdown.semanticSignature ?? dropdown.semantic_signature ?? null,
      container: dropdown.container ?? dropdown.tableCell ?? dropdown.table_cell ?? null,
      displayText: dropdown.displayText ?? dropdown.display_text ?? null,
    };
  });
}

function isPrivateUse(codePoint) {
  return (codePoint >= 0xE000 && codePoint <= 0xF8FF) ||
    (codePoint >= 0xF0000 && codePoint <= 0xFFFFD) ||
    (codePoint >= 0x100000 && codePoint <= 0x10FFFD);
}

function privateUseMarkerSpans(value) {
  const text = String(value ?? "");
  const spans = [];
  let current = null;
  for (let offset = 0; offset < text.length;) {
    const codePoint = text.codePointAt(offset);
    const character = String.fromCodePoint(codePoint);
    if (isPrivateUse(codePoint)) {
      if (!current) current = { startOffset: offset, endOffset: offset, text: "", codePoints: [] };
      current.endOffset = offset + character.length;
      current.text += character;
      current.codePoints.push(`U+${codePoint.toString(16).toUpperCase().padStart(4, "0")}`);
    } else if (current) {
      spans.push(current);
      current = null;
    }
    offset += character.length;
  }
  if (current) spans.push(current);
  return spans;
}

function elementRange(element) {
  return {
    startIndex: element.startIndex ?? element.start_index ?? null,
    endIndex: element.endIndex ?? element.end_index ?? null,
  };
}

function paragraphContainer(structuralElement, paragraph, context, path) {
  const bullet = paragraph.bullet ?? null;
  return {
    kind: "paragraph",
    path,
    tabId: context.tabId,
    segmentId: context.segmentId,
    startIndex: structuralElement.startIndex ?? structuralElement.start_index ?? null,
    endIndex: structuralElement.endIndex ?? structuralElement.end_index ?? null,
    namedStyleType: paragraph.paragraphStyle?.namedStyleType ?? paragraph.paragraph_style?.named_style_type ?? null,
    listId: bullet?.listId ?? bullet?.list_id ?? null,
    nestingLevel: bullet?.nestingLevel ?? bullet?.nesting_level ?? null,
    table: context.table,
  };
}

function collectDocumentFeatures(value, { selectedTabId = null } = {}) {
  const root = unwrapResult(value);
  const opaqueControls = [];
  const nativeElements = [];
  const tabs = new Set();
  const seen = new Set();

  const addNative = (type, element, container, properties = null) => {
    nativeElements.push({ type, ...elementRange(element), tabId: container.tabId, segmentId: container.segmentId, container, properties });
  };

  const visitElement = (element, container, path) => {
    if (!isRecord(element)) return;
    const text = element.textRun?.content;
    const base = element.startIndex ?? element.start_index;
    if (typeof text === "string" && Number.isInteger(base)) {
      for (const marker of privateUseMarkerSpans(text)) {
        opaqueControls.push({
          classification: "opaqueTemplateControl",
          fidelityClass: "copy-only",
          tabId: container.tabId,
          segmentId: container.segmentId,
          startIndex: base + marker.startOffset,
          endIndex: base + marker.endOffset,
          markerText: marker.text,
          codePoints: marker.codePoints,
          textStyle: element.textRun?.textStyle ?? {},
          container,
          path,
        });
      }
    }
    if (element.dateElement) addNative("dateElement", element, container, element.dateElement.dateElementProperties ?? null);
    if (element.person) addNative("person", element, container, element.person.personProperties ?? null);
    if (element.richLink) addNative("richLink", element, container, element.richLink.richLinkProperties ?? null);
    if (element.inlineObjectElement) addNative("inlineObjectElement", element, container, element.inlineObjectElement);
    if (element.footnoteReference) addNative("footnoteReference", element, container, element.footnoteReference);
    if (element.horizontalRule) addNative("horizontalRule", element, container, null);
    if (element.equation) addNative("equation", element, container, element.equation);
  };

  const visit = (candidate, context = { tabId: null, segmentId: null, table: null }, path = "root") => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return;
    seen.add(candidate);
    if (Array.isArray(candidate)) {
      candidate.forEach((child, index) => visit(child, context, `${path}[${index}]`));
      return;
    }

    const directTabId = candidate.tabId ?? candidate.tab_id ?? null;
    const discoveredTabId = candidate.tabProperties?.tabId ?? candidate.tab_properties?.tab_id ?? directTabId ?? context.tabId;
    const isTabRecord = Boolean(
      candidate.tabProperties?.tabId ||
      candidate.tab_properties?.tab_id ||
      (directTabId && candidate.body),
    );
    if (isTabRecord) {
      tabs.add(discoveredTabId);
      if (selectedTabId !== null && discoveredTabId !== selectedTabId) return;
    }
    const nextContext = {
      ...context,
      tabId: discoveredTabId ?? null,
      segmentId: candidate.segmentId ?? candidate.segment_id ?? context.segmentId ?? null,
    };

    if (candidate.paragraph?.elements) {
      const container = paragraphContainer(candidate, candidate.paragraph, nextContext, path);
      candidate.paragraph.elements.forEach((element, index) => visitElement(element, container, `${path}.paragraph.elements[${index}]`));
      return;
    }

    if (candidate.table?.tableRows) {
      const tableStartIndex = candidate.startIndex ?? candidate.start_index ?? null;
      candidate.table.tableRows.forEach((row, rowIndex) => {
        (row.tableCells ?? []).forEach((cell, columnIndex) => {
          visit(cell.content ?? [], {
            ...nextContext,
            table: { tableStartIndex, rowIndex, columnIndex },
          }, `${path}.table.rows[${rowIndex}].cells[${columnIndex}].content`);
        });
      });
      return;
    }

    for (const [key, child] of Object.entries(candidate)) visit(child, nextContext, `${path}.${key}`);
  };

  visit(root);
  return { opaqueControls, nativeElements, tabs: [...tabs] };
}

function sameLocator(left, right) {
  return (left.tabId ?? null) === (right.tabId ?? null) &&
    (left.segmentId ?? null) === (right.segmentId ?? null) &&
    left.startIndex === right.startIndex && left.endIndex === right.endIndex;
}

function countByType(elements) {
  const output = {};
  for (const element of elements) output[element.type] = (output[element.type] ?? 0) + 1;
  return output;
}

function resolveTool(tools, names, override = null) {
  if (override) return typeof tools?.[override] === "function" ? { name: override, fn: tools[override] } : null;
  for (const name of names) if (typeof tools?.[name] === "function") return { name, fn: tools[name] };
  return null;
}

function connectorArgs({ documentId, documentUrl, tabId = null, includeTab = false }) {
  const args = documentId ? { document_id: documentId } : { document_url: documentUrl };
  if (includeTab && tabId !== null) args.tab_id = tabId;
  return args;
}

export class TrustedReadError extends Error {
  constructor(message) {
    super(message);
    this.name = "TrustedReadError";
  }
}

export async function readGoogleDocWithControlInventory({
  documentId = null,
  documentUrl = null,
  tabId = null,
  tools,
  capabilityOverrides = {},
} = {}) {
  assert(Boolean(documentId) !== Boolean(documentUrl), "Provide exactly one of documentId or documentUrl");
  assert(isRecord(tools), "Mounted connector tools are required");

  const getDocument = resolveTool(tools, CAPABILITIES.getDocument, capabilityOverrides.getDocument ?? null);
  assert(getDocument, "Required getDocument capability is unavailable");
  const documentResult = await getDocument.fn(connectorArgs({ documentId, documentUrl }));
  const identity = documentIdentity(documentResult);
  if (documentId !== null) assert(identity.documentId === documentId, "Document identity does not match the requested document");
  const discovered = collectDocumentFeatures(documentResult, { selectedTabId: tabId });

  let dropdownMetadata = { status: "unavailable", resolvedTool: null, authoritative: false, count: 0 };
  let dropdownResult = null;
  let authoritativeDropdowns = [];
  const getDropdowns = resolveTool(tools, CAPABILITIES.getDocumentDropdowns, capabilityOverrides.getDocumentDropdowns ?? null);
  if (getDropdowns) {
    try {
      dropdownResult = await getDropdowns.fn(connectorArgs({ documentId: identity.documentId, documentUrl: null, tabId, includeTab: true }));
      const dropdownIdentity = dropdownReadIdentity(dropdownResult);
      if (!dropdownIdentity || dropdownIdentity.documentId !== identity.documentId || dropdownIdentity.revisionId !== identity.revisionId ||
          (tabId !== null && dropdownIdentity.tabId !== null && dropdownIdentity.tabId !== tabId)) {
        dropdownMetadata = {
          status: "identity_or_revision_mismatch",
          resolvedTool: getDropdowns.name,
          authoritative: false,
          count: 0,
        };
      } else {
        authoritativeDropdowns = dropdownRecords(dropdownResult)
          .filter((dropdown) => tabId === null || dropdown.tabId === null || dropdown.tabId === tabId);
        dropdownMetadata = {
          status: "available",
          resolvedTool: getDropdowns.name,
          authoritative: true,
          count: authoritativeDropdowns.length,
        };
      }
    } catch {
      dropdownMetadata = {
        status: "read_failed",
        resolvedTool: getDropdowns.name,
        authoritative: false,
        count: 0,
      };
    }
  }

  const opaqueControls = discovered.opaqueControls.filter((opaque) =>
    !authoritativeDropdowns.some((dropdown) => sameLocator(dropdown, opaque)),
  );
  const controls = [...authoritativeDropdowns, ...opaqueControls].sort((left, right) =>
    String(left.tabId).localeCompare(String(right.tabId)) ||
    (left.startIndex ?? Number.MAX_SAFE_INTEGER) - (right.startIndex ?? Number.MAX_SAFE_INTEGER),
  );
  const warnings = [];
  if (controls.length > 0) {
    warnings.push("Existing native or opaque controls were detected. Preserve each control and its containing structure unless the user explicitly requests an exact supported mutation.");
  }
  if (opaqueControls.length > 0) {
    warnings.push("Private-use markers are classified as opaque copy-only controls. Do not replace them with visible text or infer dropdown semantics from the glyph alone.");
  }
  if (dropdownMetadata.status === "identity_or_revision_mismatch") {
    warnings.push("Dropdown metadata did not match the document revision and was ignored; unmatched controls remain opaque.");
  } else if (dropdownMetadata.status === "read_failed") {
    warnings.push("Authoritative dropdown metadata could not be read; unmatched controls remain opaque.");
  }

  return {
    version: 1,
    kind: "google-docs-trusted-read-context",
    documentResult,
    dropdownResult,
    target: { ...identity, selectedTabId: tabId },
    dropdownMetadata,
    derivedControlInventory: {
      hasProtectedControls: controls.length > 0,
      authoritativeDropdownCount: authoritativeDropdowns.length,
      opaqueControlCount: opaqueControls.length,
      nativeElementCounts: countByType(discovered.nativeElements),
      tabsScanned: tabId === null ? discovered.tabs : (discovered.tabs.includes(tabId) ? [tabId] : []),
      controls,
      nativeElements: discovered.nativeElements,
    },
    editGuidance: {
      advisoryOnly: true,
      requiresTargetedPreservation: controls.length > 0,
      recommendedBehavior: controls.length > 0
        ? "Edit supported text before or after protected controls; do not rewrite their containing structure."
        : "No protected controls were detected in the scanned scope.",
      warnings,
    },
  };
}

export { CAPABILITIES, privateUseMarkerSpans };
