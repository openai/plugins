import {
  assert,
  collectRecords,
  findFirstRecord,
  isRecord,
  requireArray,
  requireInteger,
  requireRecord,
  requireString,
  sha256Json,
} from "./dropdown-common.mjs";

export const DROPDOWN_INVENTORY_VERSION = 1;

function unwrap(value) {
  if (isRecord(value?.structuredContent)) return value.structuredContent;
  if (isRecord(value?.result)) return value.result;
  return value;
}

function documentIdentity(raw) {
  const root = unwrap(raw);
  const document = findFirstRecord(root, (candidate) =>
    typeof (candidate.documentId ?? candidate.document_id) === "string" &&
    (candidate.revisionId || candidate.revision_id || candidate.body || candidate.tabs),
  );
  assert(document, "Could not locate a Google Docs document resource");
  return {
    id: document.documentId ?? document.document_id,
    title: document.title ?? null,
    revisionId: document.revisionId ?? document.revision_id ?? null,
    url: document.documentUrl ?? document.document_url ?? document.url ?? null,
  };
}

function isPrivateUse(codePoint) {
  return (codePoint >= 0xE000 && codePoint <= 0xF8FF) ||
    (codePoint >= 0xF0000 && codePoint <= 0xFFFFD) ||
    (codePoint >= 0x100000 && codePoint <= 0x10FFFD);
}

export function privateUseMarkerSpans(value) {
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

function semanticBinding({ type, fidelityClass, locator, container = null, semanticProperties, displayText = "", anchor = {} }) {
  const semanticPropertiesHash = sha256Json(semanticProperties);
  const anchorHash = sha256Json({
    prefixText: String(anchor.prefixText ?? "").slice(-96),
    suffixText: String(anchor.suffixText ?? "").slice(0, 96),
    container,
  });
  return {
    bindingId: sha256Json({ type, locator, semanticPropertiesHash, anchorHash }),
    type,
    fidelityClass,
    locator,
    container,
    displayText,
    semanticProperties,
    semanticPropertiesHash,
    anchorHash,
  };
}

function normalizeOptions(value, path) {
  return requireArray(value ?? [], path).map((option, index) => {
    const item = requireRecord(option, `${path}[${index}]`);
    return {
      label: requireString(item.label ?? item.text ?? item.value, `${path}[${index}].label`),
      ...(item.color ?? item.colorStyle ?? item.color_style ? { color: item.color ?? item.colorStyle ?? item.color_style } : {}),
      ...(item.id ?? item.optionId ?? item.option_id ? { id: item.id ?? item.optionId ?? item.option_id } : {}),
    };
  });
}

function dropdownRecords(raw) {
  const root = unwrap(raw);
  const containers = collectRecords(root, (candidate) => Array.isArray(candidate.dropdowns));
  const values = containers.flatMap((container) => container.dropdowns);
  if (Array.isArray(root)) values.push(...root);
  return values.filter((candidate) => isRecord(candidate) && (
    candidate.dropdownId || candidate.dropdown_id || candidate.options || candidate.optionItems || candidate.option_items
  ));
}

function dropdownResponseIdentity(raw) {
  const root = unwrap(raw);
  const record = findFirstRecord(root, (candidate) =>
    typeof (candidate.documentId ?? candidate.document_id) === "string" &&
    typeof (candidate.revisionId ?? candidate.revision_id) === "string" &&
    Array.isArray(candidate.dropdowns),
  );
  assert(record, "Dropdown metadata must include document identity, revision, and dropdown records");
  return {
    documentId: record.documentId ?? record.document_id,
    revisionId: record.revisionId ?? record.revision_id,
    tabId: record.tabId ?? record.tab_id ?? null,
  };
}

function normalizeDropdown(value, index, fallbackTabId = null) {
  const path = `dropdowns[${index}]`;
  const dropdown = requireRecord(value, path);
  const range = dropdown.range ?? dropdown.locator ?? {};
  const startIndex = requireInteger(range.startIndex ?? range.start_index ?? dropdown.startIndex ?? dropdown.start_index, `${path}.startIndex`, { minimum: 0 });
  const endIndex = requireInteger(range.endIndex ?? range.end_index ?? dropdown.endIndex ?? dropdown.end_index, `${path}.endIndex`, { minimum: startIndex + 1 });
  const tabId = range.tabId ?? range.tab_id ?? dropdown.tabId ?? dropdown.tab_id ?? fallbackTabId;
  const options = normalizeOptions(dropdown.options ?? dropdown.optionItems ?? dropdown.option_items, `${path}.options`);
  const selectedValue = dropdown.selectedValue ?? dropdown.selected_value ?? dropdown.value ?? null;
  assert(options.length > 0, "must not be empty", `${path}.options`);
  assert(new Set(options.map((option) => option.label)).size === options.length, "labels must be unique", `${path}.options`);
  if (selectedValue !== null) assert(options.some((option) => option.label === selectedValue), "must name an available option", `${path}.selectedValue`);
  const dropdownId = dropdown.dropdownId ?? dropdown.dropdown_id ?? null;
  if (dropdownId !== null) requireString(dropdownId, `${path}.dropdownId`);
  const providerSignature = dropdown.signature ?? dropdown.semanticSignature ?? dropdown.semantic_signature ?? null;
  assert(dropdownId !== null || (typeof providerSignature === "string" && providerSignature.length > 0), "requires a provider ID or stable semantic signature", path);
  const semanticProperties = {
    dropdownId,
    options,
    selectedValue,
    signature: providerSignature ?? sha256Json({ dropdownId, options, selectedValue }),
  };
  const container = dropdown.container ?? dropdown.tableCell ?? dropdown.table_cell ?? null;
  return semanticBinding({
    type: "dropdownControl",
    fidelityClass: "exact-writable",
    locator: { tabId: tabId ?? null, segmentId: range.segmentId ?? range.segment_id ?? null, startIndex, endIndex },
    container,
    semanticProperties,
    displayText: String(dropdown.displayText ?? dropdown.display_text ?? selectedValue ?? ""),
    anchor: dropdown.anchor ?? {},
  });
}

function collectOpaqueControls(rawDocument, exactDropdowns) {
  const root = unwrap(rawDocument);
  const output = [];
  const seen = new Set();
  const visit = (value, context = { tabId: null, segmentId: null, container: null, prefixText: "", suffixText: "" }) => {
    if (!value || typeof value !== "object" || seen.has(value)) return;
    seen.add(value);
    if (Array.isArray(value)) {
      value.forEach((child) => visit(child, context));
      return;
    }
    const tabId = value.tabProperties?.tabId ?? value.tab_properties?.tab_id ?? value.tabId ?? value.tab_id ?? context.tabId;
    const segmentId = value.segmentId ?? value.segment_id ?? context.segmentId;
    if (typeof value.textRun?.content === "string" && Number.isInteger(value.startIndex ?? value.start_index)) {
      const base = value.startIndex ?? value.start_index;
      for (const marker of privateUseMarkerSpans(value.textRun.content)) {
        const locator = { tabId: tabId ?? null, segmentId: segmentId ?? null, startIndex: base + marker.startOffset, endIndex: base + marker.endOffset };
        const identified = exactDropdowns.some((binding) =>
          binding.locator.tabId === locator.tabId && binding.locator.segmentId === locator.segmentId &&
          binding.locator.startIndex === locator.startIndex && binding.locator.endIndex === locator.endIndex,
        );
        if (identified) continue;
        output.push(semanticBinding({
          type: "opaqueTemplateControl",
          fidelityClass: "copy-only",
          locator,
          container: context.container,
          semanticProperties: {
            controlClass: "private-use-glyph",
            markerText: marker.text,
            codePoints: marker.codePoints,
            textStyle: value.textRun.textStyle ?? {},
          },
          displayText: marker.text,
          anchor: context,
        }));
      }
    }
    for (const [key, child] of Object.entries(value)) {
      if (key === "textRun") continue;
      visit(child, { ...context, tabId, segmentId });
    }
  };
  visit(root);
  return output;
}

export function buildDropdownInventory({ documentResult, dropdownResult, documentId = null, tabId = null } = {}) {
  const document = documentIdentity(documentResult);
  if (documentId) assert(document.id === documentId, "Document identity does not match requested document");
  const dropdownIdentity = dropdownResponseIdentity(dropdownResult);
  assert(dropdownIdentity.documentId === document.id, "Dropdown metadata belongs to a different document");
  assert(dropdownIdentity.revisionId === document.revisionId, "Document and dropdown metadata revisions do not match");
  if (tabId !== null) assert(dropdownIdentity.tabId === null || dropdownIdentity.tabId === tabId, "Dropdown metadata belongs to a different tab");
  const dropdowns = dropdownRecords(dropdownResult).map((value, index) => normalizeDropdown(value, index, tabId));
  const opaqueControls = collectOpaqueControls(documentResult, dropdowns);
  const semanticElements = [...dropdowns, ...opaqueControls].sort((left, right) =>
    String(left.locator.tabId).localeCompare(String(right.locator.tabId)) || left.locator.startIndex - right.locator.startIndex,
  );
  const base = {
    inventoryVersion: DROPDOWN_INVENTORY_VERSION,
    document,
    selectedTabId: tabId ?? null,
    dropdowns,
    opaqueControls,
    semanticElements,
  };
  return { ...base, sha256: sha256Json(base) };
}

export function verifyDropdownInventory(value) {
  const inventory = requireRecord(value, "inventory");
  assert(inventory.inventoryVersion === DROPDOWN_INVENTORY_VERSION, `must use version ${DROPDOWN_INVENTORY_VERSION}`, "inventory.inventoryVersion");
  requireString(inventory.document?.id, "inventory.document.id");
  requireString(inventory.document?.revisionId, "inventory.document.revisionId");
  requireArray(inventory.semanticElements, "inventory.semanticElements");
  const { sha256, ...base } = inventory;
  assert(sha256 === sha256Json(base), "sha256 does not match inventory content", "inventory.sha256");
  return inventory;
}
