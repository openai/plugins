/* Dependency-free host executor for the Google Docs dropdown workflow. */

const CAPABILITIES = {
  getDocument: [
    "mcp__codex_apps__google_drive_get_document",
    "google_drive_get_document",
    "get_document",
  ],
  getDocumentTables: [
    "mcp__codex_apps__google_drive_get_document_tables",
    "google_drive_get_document_tables",
    "get_document_tables",
  ],
  batchUpdateDocument: [
    "mcp__codex_apps__google_drive_batch_update_document",
    "google_drive_batch_update_document",
    "batch_update_document",
  ],
  getDocumentDropdowns: [
    "mcp__codex_apps__google_drive_get_document_dropdowns",
    "google_drive_get_document_dropdowns",
    "get_document_dropdowns",
  ],
  updateDocumentDropdown: [
    "mcp__codex_apps__google_drive_update_document_dropdown",
    "google_drive_update_document_dropdown",
    "update_document_dropdown",
  ],
};

function assert(condition, message) {
  if (!condition) throw new DropdownExecutorError(message);
}

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  if (isRecord(value)) return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function redact(value, key = "") {
  if (Array.isArray(value)) return value.map((item) => redact(item, key));
  if (!isRecord(value)) {
    if (/token|credential|signed|authorization|cookie|option|label|text/i.test(key)) return "[REDACTED]";
    return value;
  }
  return Object.fromEntries(Object.entries(value).map(([childKey, child]) => [childKey, redact(child, childKey)]));
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

function unwrapResult(value) {
  if (value?.isError === true) {
    const error = new DropdownExecutorError("Connector returned isError=true", { raw: value });
    error.outcomeClass = connectorOutcome(value);
    throw error;
  }
  if (isRecord(value?.structuredContent)) return value.structuredContent;
  if (isRecord(value?.result)) return value.result;
  return value;
}

const OUTCOME_CLASSES = new Set([
  "applied",
  "rejected_before_apply",
  "stale_revision",
  "ambiguous_anchor",
  "rate_limited_before_apply",
  "unknown_application_state",
  "applied_readback_failed",
  "verification_failed",
]);

function connectorOutcome(value) {
  const record = findFirstRecord(value, (candidate) => {
    const outcome = candidate.outcomeClass ?? candidate.outcome_class ?? candidate.outcome ?? candidate.status;
    return OUTCOME_CLASSES.has(outcome);
  });
  return record ? (record.outcomeClass ?? record.outcome_class ?? record.outcome ?? record.status) : null;
}

function documentIdentity(value) {
  const root = unwrapResult(value);
  const record = findFirstRecord(root, (candidate) =>
    typeof (candidate.documentId ?? candidate.document_id) === "string" &&
    (candidate.revisionId || candidate.revision_id || candidate.body || candidate.tabs),
  );
  assert(record, "Could not locate document identity in connector result");
  return {
    documentId: record.documentId ?? record.document_id,
    title: record.title ?? null,
    revisionId: record.revisionId ?? record.revision_id ?? null,
  };
}

function dropdownReadIdentity(value) {
  const root = unwrapResult(value);
  const record = findFirstRecord(root, (candidate) =>
    typeof (candidate.documentId ?? candidate.document_id) === "string" &&
    typeof (candidate.revisionId ?? candidate.revision_id) === "string" &&
    Array.isArray(candidate.dropdowns),
  );
  assert(record, "Dropdown readback is missing document identity or revision");
  return {
    documentId: record.documentId ?? record.document_id,
    revisionId: record.revisionId ?? record.revision_id,
    tabId: record.tabId ?? record.tab_id ?? null,
  };
}

function normalizeOptions(value) {
  return (value ?? []).map((option) => ({
    label: option.label ?? option.text ?? option.value,
    ...(option.color ?? option.colorStyle ?? option.color_style ? { color: option.color ?? option.colorStyle ?? option.color_style } : {}),
    ...(option.id ?? option.optionId ?? option.option_id ? { id: option.id ?? option.optionId ?? option.option_id } : {}),
  }));
}

function dropdownRecords(value) {
  const root = unwrapResult(value);
  const records = collectRecords(root, (candidate) => Array.isArray(candidate.dropdowns)).flatMap((candidate) => candidate.dropdowns);
  if (Array.isArray(root)) records.push(...root);
  return records.filter(isRecord).map((dropdown) => {
    const range = dropdown.range ?? dropdown.locator ?? {};
    return {
      dropdownId: dropdown.dropdownId ?? dropdown.dropdown_id ?? null,
      tabId: dropdown.tabId ?? dropdown.tab_id ?? range.tabId ?? range.tab_id ?? null,
      segmentId: dropdown.segmentId ?? dropdown.segment_id ?? range.segmentId ?? range.segment_id ?? null,
      startIndex: dropdown.startIndex ?? dropdown.start_index ?? range.startIndex ?? range.start_index ?? null,
      endIndex: dropdown.endIndex ?? dropdown.end_index ?? range.endIndex ?? range.end_index ?? null,
      options: normalizeOptions(dropdown.options ?? dropdown.optionItems ?? dropdown.option_items),
      selectedValue: dropdown.selectedValue ?? dropdown.selected_value ?? dropdown.value ?? null,
      signature: dropdown.signature ?? dropdown.semanticSignature ?? dropdown.semantic_signature ?? null,
      container: dropdown.container ?? dropdown.tableCell ?? dropdown.table_cell ?? null,
    };
  });
}

function isPrivateUse(codePoint) {
  return (codePoint >= 0xE000 && codePoint <= 0xF8FF) ||
    (codePoint >= 0xF0000 && codePoint <= 0xFFFFD) ||
    (codePoint >= 0x100000 && codePoint <= 0x10FFFD);
}

function opaqueMarkers(value) {
  const output = [];
  const seen = new Set();
  const visit = (candidate, context = { tabId: null, segmentId: null }) => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return;
    seen.add(candidate);
    if (Array.isArray(candidate)) return candidate.forEach((child) => visit(child, context));
    const tabId = candidate.tabProperties?.tabId ?? candidate.tab_properties?.tab_id ?? candidate.tabId ?? candidate.tab_id ?? context.tabId;
    const segmentId = candidate.segmentId ?? candidate.segment_id ?? context.segmentId;
    const content = candidate.textRun?.content;
    const base = candidate.startIndex ?? candidate.start_index;
    if (typeof content === "string" && Number.isInteger(base)) {
      let marker = null;
      for (let offset = 0; offset < content.length;) {
        const codePoint = content.codePointAt(offset);
        const character = String.fromCodePoint(codePoint);
        if (isPrivateUse(codePoint)) {
          if (!marker) marker = { startIndex: base + offset, endIndex: base + offset, markerText: "", codePoints: [] };
          marker.endIndex = base + offset + character.length;
          marker.markerText += character;
          marker.codePoints.push(`U+${codePoint.toString(16).toUpperCase().padStart(4, "0")}`);
        } else if (marker) {
          output.push({ tabId: tabId ?? null, segmentId: segmentId ?? null, ...marker, textStyle: candidate.textRun.textStyle ?? {} });
          marker = null;
        }
        offset += character.length;
      }
      if (marker) output.push({ tabId: tabId ?? null, segmentId: segmentId ?? null, ...marker, textStyle: candidate.textRun.textStyle ?? {} });
    }
    for (const [key, child] of Object.entries(candidate)) if (key !== "textRun") visit(child, { tabId, segmentId });
  };
  visit(unwrapResult(value));
  return output;
}

function resolveTool(tools, capability, overrides = {}) {
  const override = overrides[capability];
  if (override) {
    assert(typeof tools[override] === "function", `Capability override ${override} is unavailable`);
    return { name: override, fn: tools[override] };
  }
  for (const name of CAPABILITIES[capability] ?? []) {
    if (typeof tools[name] === "function") return { name, fn: tools[name] };
  }
  throw new DropdownExecutorError(`Required connector capability ${capability} is unavailable`);
}

async function callTool({ tools, capability, args, overrides }) {
  const resolved = resolveTool(tools, capability, overrides);
  const result = await resolved.fn(args);
  unwrapResult(result);
  const outcomeClass = connectorOutcome(result);
  if (outcomeClass && outcomeClass !== "applied") {
    const error = new DropdownExecutorError(`Connector reported ${outcomeClass}`, { raw: result });
    error.outcomeClass = outcomeClass;
    throw error;
  }
  return { capability, resolvedTool: resolved.name, args: redact(args), result };
}

function optionsEqual(left, right) {
  return stableStringify(normalizeOptions(left)) === stableStringify(normalizeOptions(right));
}

function findDropdown(records, { dropdownId = null, location = null, expected = null, signature = null } = {}) {
  const matches = records.filter((record) => {
    if (dropdownId && record.dropdownId !== dropdownId) return false;
    if (location && (record.tabId !== (location.tabId ?? null) || record.startIndex !== location.index)) return false;
    if (signature && record.signature !== signature) return false;
    if (expected?.options && !optionsEqual(record.options, expected.options)) return false;
    if (Object.prototype.hasOwnProperty.call(expected ?? {}, "selectedValue") && record.selectedValue !== expected.selectedValue) return false;
    return true;
  });
  return matches.length === 1 ? matches[0] : null;
}

function assertFrozenSemantics(documentResult, dropdownResult, contract, { ignoredBindingIds = [] } = {}) {
  const liveDropdowns = dropdownRecords(dropdownResult);
  const liveOpaque = opaqueMarkers(documentResult);
  for (const binding of contract.semanticElements ?? []) {
    if (binding.type === "dropdownControl") {
      if (ignoredBindingIds.includes(binding.bindingId)) continue;
      const match = findDropdown(liveDropdowns, {
        dropdownId: binding.semanticProperties?.dropdownId,
        location: binding.semanticProperties?.dropdownId ? null : { tabId: binding.locator?.tabId ?? null, index: binding.locator?.startIndex },
        expected: { options: binding.semanticProperties?.options, selectedValue: binding.semanticProperties?.selectedValue },
        signature: binding.semanticProperties?.dropdownId ? null : binding.semanticProperties?.signature,
      });
      assert(match, `Frozen dropdown ${binding.bindingId} is missing`);
      assert(optionsEqual(match.options, binding.semanticProperties?.options), `Frozen dropdown ${binding.bindingId} options changed`);
      assert(match.selectedValue === binding.semanticProperties?.selectedValue, `Frozen dropdown ${binding.bindingId} selected value changed`);
      if (match.signature !== null && binding.semanticProperties?.signature !== null) assert(match.signature === binding.semanticProperties.signature, `Frozen dropdown ${binding.bindingId} signature changed`);
      if (match.container !== null && binding.container !== null) assert(stableStringify(match.container) === stableStringify(binding.container), `Frozen dropdown ${binding.bindingId} container changed`);
    } else if (binding.type === "opaqueTemplateControl") {
      let match = liveOpaque.find((candidate) =>
        candidate.tabId === (binding.locator?.tabId ?? null) && candidate.segmentId === (binding.locator?.segmentId ?? null) &&
        candidate.startIndex === binding.locator?.startIndex && candidate.endIndex === binding.locator?.endIndex &&
        candidate.markerText === binding.semanticProperties?.markerText,
      );
      if (!match) {
        const shiftedMatches = liveOpaque.filter((candidate) =>
          candidate.tabId === (binding.locator?.tabId ?? null) && candidate.segmentId === (binding.locator?.segmentId ?? null) &&
          candidate.markerText === binding.semanticProperties?.markerText &&
          stableStringify(candidate.textStyle ?? {}) === stableStringify(binding.semanticProperties?.textStyle ?? {}),
        );
        if (shiftedMatches.length === 1) match = shiftedMatches[0];
      }
      assert(match, `Frozen opaque control ${binding.bindingId} is missing or changed`);
    }
  }
}

function rangesOverlap(left, right) {
  if ((left.tabId ?? null) !== (right.tabId ?? null)) return false;
  if ((left.segmentId ?? null) !== (right.segmentId ?? null)) return false;
  const leftStart = left.startIndex ?? left.index;
  const leftEnd = left.endIndex ?? ((left.index ?? 0) + 1);
  const rightStart = right.startIndex ?? right.index;
  const rightEnd = right.endIndex ?? ((right.index ?? 0) + 1);
  return leftStart < rightEnd && rightStart < leftEnd;
}

function stageRequestRange(request) {
  const payload = request.deleteContentRange ?? request.updateTextStyle ?? request.updateParagraphStyle ?? request.createParagraphBullets ?? request.deleteParagraphBullets;
  if (payload?.range) return payload.range;
  const locationPayload = request.insertText ?? request.insertTable ?? request.insertPageBreak ?? request.insertInlineImage ?? request.insertDate ?? request.insertPerson ?? request.insertRichLink;
  const location = locationPayload?.location ?? locationPayload?.endOfSegmentLocation ?? null;
  if (location && Number.isInteger(location.index)) return { ...location, startIndex: location.index, endIndex: location.index + 1 };
  const tableLocation = request.insertTableRow?.tableCellLocation?.tableStartLocation ?? request.insertTableColumn?.tableCellLocation?.tableStartLocation ?? request.deleteTableRow?.tableCellLocation?.tableStartLocation ?? request.deleteTableColumn?.tableCellLocation?.tableStartLocation;
  if (tableLocation && Number.isInteger(tableLocation.index)) return { ...tableLocation, startIndex: tableLocation.index, endIndex: tableLocation.index + 1 };
  return null;
}

function assertRangeAllowed(range, contract) {
  assert(!(contract.protectedTabIds ?? []).includes(range.tabId ?? null), "Stage targets a protected tab");
  for (const protectedRange of contract.protectedRanges ?? []) assert(!rangesOverlap(range, protectedRange), "Stage overlaps a protected range");
}

function assertOptions(value, label) {
  assert(Array.isArray(value) && value.length > 0, `${label} must contain options`);
  const options = normalizeOptions(value);
  assert(options.every((option) => typeof option.label === "string" && option.label.length > 0), `${label} contains an invalid option`);
  assert(new Set(options.map((option) => option.label)).size === options.length, `${label} contains duplicate labels`);
  return options;
}

function bindingByDropdownId(contract, dropdownId) {
  const matches = (contract.semanticElements ?? []).filter((binding) =>
    binding.type === "dropdownControl" && binding.semanticProperties?.dropdownId === dropdownId,
  );
  assert(matches.length === 1, "Dropdown target is missing or ambiguous in the frozen contract");
  return matches[0];
}

function bindingForOperation(contract, operation) {
  if (operation.dropdown_id !== undefined && operation.dropdown_id !== null) return bindingByDropdownId(contract, operation.dropdown_id);
  const matches = (contract.semanticElements ?? []).filter((binding) => binding.type === "dropdownControl" && binding.bindingId === operation.binding_id);
  assert(matches.length === 1, "Dropdown binding target is missing or ambiguous in the frozen contract");
  assert(stableStringify(matches[0].locator) === stableStringify(operation.locator), "Dropdown binding locator mismatch");
  assert(matches[0].semanticProperties?.signature === operation.semantic_signature, "Dropdown binding signature mismatch");
  return matches[0];
}

function validateHostStage(plan, contract) {
  const stage = plan.stage;
  const assertions = stage.preservationAssertions;
  assert(isRecord(assertions) && assertions.preserveUntouchedSemanticBindings === true, "Stage preservation assertions are missing");
  const actualBindingIds = [...(assertions.semanticBindingIds ?? [])].sort();
  const expectedBindingIds = (contract.semanticElements ?? []).map((binding) => binding.bindingId).sort();
  assert(stableStringify(actualBindingIds) === stableStringify(expectedBindingIds), "Stage does not freeze every semantic binding");
  assert(stage.postWriteReadback?.documentStructure === true && stage.postWriteReadback?.dropdownMetadata === true, "Stage post-write readback requirements are incomplete");

  const call = stage.call;
  assert(isRecord(call) && call.document_id === plan.target.documentId, "Stage document target mismatch");
  if (stage.type === "docs_batch_update") {
    assert(call.write_control?.requiredRevisionId === plan.target.expectedRevisionId, "Docs stage revision mismatch");
    assert(stage.expectedBefore?.revisionId === plan.target.expectedRevisionId, "Docs expected-before revision mismatch");
    assert(stage.expectedBefore?.targetBindingsHash === contract.targetBindingsHash, "Docs expected-before binding mismatch");
    assert(stage.expectedAfter?.revisionChanged === true && stage.expectedAfter?.semanticBindingsPreserved === true, "Docs expected-after assertions are incomplete");
    assert(Array.isArray(call.requests) && call.requests.length > 0, "Docs stage requests are missing");
    for (const request of call.requests) {
      assert(isRecord(request) && Object.keys(request).length === 1, "Each Docs request must contain one operation");
      assert(!request.replaceAllText && !request.replaceNamedRangeContent, "Broad Docs replacements are not allowed");
      const range = stageRequestRange(request);
      if (!range) continue;
      assertRangeAllowed(range, contract);
      for (const binding of contract.semanticElements ?? []) assert(!rangesOverlap(range, binding.locator), `Docs stage intersects semantic binding ${binding.bindingId}`);
    }
    return;
  }

  assert(call.tab_id === (plan.target.tabId ?? null), "Dropdown stage tab mismatch");
  assert(call.required_revision_id === plan.target.expectedRevisionId, "Dropdown stage revision mismatch");
  assert(typeof call.idempotency_key === "string" && call.idempotency_key.length > 0, "Dropdown stage idempotency key is missing");
  const operation = call.operation;
  assert(isRecord(operation) && Object.prototype.hasOwnProperty.call(operation, "selected_value"), "Dropdown operation is incomplete");
  const expectedType = stage.type === "dropdown_set_selected" ? "set_selected_value" : stage.type.replace("dropdown_", "");
  assert(operation.type === expectedType, "Dropdown operation type mismatch");
  const expectedOptions = assertOptions(stage.expectedAfter?.options, "expectedAfter.options");
  assert(Object.prototype.hasOwnProperty.call(stage.expectedAfter ?? {}, "selectedValue"), "expectedAfter.selectedValue is required");
  assert(stage.expectedAfter.selectedValue === (operation.selected_value ?? null), "Expected selected value mismatch");

  if (stage.type === "dropdown_create") {
    assert(isRecord(operation.location) && Number.isInteger(operation.location.index), "Create location is missing");
    assert(operation.location.tabId === (plan.target.tabId ?? null), "Create location tab mismatch");
    assertRangeAllowed({ ...operation.location, startIndex: operation.location.index, endIndex: operation.location.index + 1 }, contract);
    assert(isRecord(operation.anchor), "Create anchor is missing");
    assert(operation.expected_before?.dropdownAbsent === true, "Create expected-before condition is missing");
    assert(optionsEqual(operation.options, expectedOptions), "Create options do not match expectedAfter");
  } else {
    const binding = bindingForOperation(contract, operation);
    assertRangeAllowed(binding.locator, contract);
    assert((operation.expected_before?.dropdownId ?? null) === (binding.semanticProperties?.dropdownId ?? null), "Dropdown expected-before ID mismatch");
    assert(operation.expected_before?.bindingId === binding.bindingId, "Dropdown expected-before binding mismatch");
    assert(optionsEqual(operation.expected_before?.options, binding.semanticProperties?.options), "Dropdown expected-before options mismatch");
    assert(operation.expected_before?.selectedValue === binding.semanticProperties?.selectedValue, "Dropdown expected-before selection mismatch");
    if (binding.semanticProperties?.signature !== null) assert(operation.expected_before?.signature === binding.semanticProperties.signature, "Dropdown expected-before signature mismatch");
    if (stage.type === "dropdown_replace_options") assert(optionsEqual(operation.options, expectedOptions), "Replacement options do not match expectedAfter");
    else assert(optionsEqual(binding.semanticProperties?.options, expectedOptions), "Selection stage must preserve options");
  }
  if (operation.selected_value !== null) assert(expectedOptions.some((option) => option.label === operation.selected_value), "Selected value is not in the expected option set");
}

function validateHostInputs(plan, contract, validation) {
  assert(plan?.version === 1 && plan?.kind === "google-docs-v2-dropdown-plan", "Unsupported plan");
  assert(contract?.contractVersion === 1, "Unsupported contract");
  assert(validation?.validationVersion === 1, "Unsupported validation sidecar");
  assert(plan.target?.documentId === contract.target?.documentId, "Plan target does not match contract");
  assert(plan.target?.title === contract.target?.title, "Plan title does not match contract");
  assert((plan.target?.tabId ?? null) === (contract.target?.selectedTabId ?? null), "Plan tab does not match contract");
  assert(plan.target?.expectedRevisionId === contract.target?.revisionId, "Plan revision does not match contract");
  assert(plan.baseSnapshot?.sha256 === contract.target?.inventorySha256, "Plan snapshot does not match contract inventory");
  assert(plan.contract?.targetBindingsHash === contract.targetBindingsHash, "Plan target binding does not match contract");
  assert(plan.contract?.decisionHash === contract.decisionHash, "Plan decision hash does not match contract");
  assert(!contract.sourceDocumentIds?.includes(plan.target.documentId), "Target document is source-denylisted");
  assert(["docs_batch_update", "dropdown_create", "dropdown_replace_options", "dropdown_set_selected"].includes(plan.stage?.type), "Unsupported stage type");
  assert(validation.summary?.documentId === plan.target.documentId, "Validation summary target mismatch");
  assert(validation.summary?.stageId === plan.stage.id && validation.summary?.stageType === plan.stage.type, "Validation summary stage mismatch");
  validateHostStage(plan, contract);
}

function classifyFailure(error, fallback = "rejected_before_apply") {
  if (OUTCOME_CLASSES.has(error?.outcomeClass)) return error.outcomeClass;
  const message = String(error?.message ?? error).toLowerCase();
  if (message.includes("stale") || message.includes("revision")) return "stale_revision";
  if (message.includes("rate") || message.includes("429")) return "rate_limited_before_apply";
  if (message.includes("ambiguous")) return "ambiguous_anchor";
  return fallback;
}

function mutationCapability(stage) {
  return stage.type === "docs_batch_update" ? "batchUpdateDocument" : "updateDocumentDropdown";
}

function mutationArgs(stage) {
  return stage.call;
}

function assertExpectedAfter(plan, preDropdowns, postDropdowns, mutationResult) {
  const stage = plan.stage;
  if (stage.type === "docs_batch_update") return;
  const operation = stage.call.operation;
  const expected = stage.expectedAfter;
  let dropdownId = operation.dropdown_id ?? null;
  if (!dropdownId) {
    const mutationRecords = dropdownRecords(mutationResult);
    dropdownId = mutationRecords[0]?.dropdownId ?? null;
  }
  const target = findDropdown(postDropdowns, {
    dropdownId,
    location: stage.type === "dropdown_create"
      ? operation.location
      : (!dropdownId && operation.locator ? { tabId: operation.locator.tabId ?? null, index: operation.locator.startIndex } : null),
    expected,
    signature: null,
  });
  assert(target, "Post-write dropdown readback does not satisfy expectedAfter");
  if (stage.type === "dropdown_create") {
    const existed = findDropdown(preDropdowns, { dropdownId: target.dropdownId });
    assert(!existed, "Create operation did not produce a new dropdown identity");
  }
}

export class DropdownExecutorError extends Error {
  constructor(message, { receipt = null, checkpoints = [], raw = null } = {}) {
    super(message);
    this.name = "DropdownExecutorError";
    this.receipt = receipt;
    this.checkpoints = checkpoints;
    this.raw = raw;
  }
}

export async function executeDocsDropdownPlan({
  plan,
  contract,
  validation,
  tools,
  capabilityOverrides = {},
} = {}) {
  validateHostInputs(plan, contract, validation);
  const checkpoints = [];
  const startedAt = new Date().toISOString();
  let revisionBefore = plan.target.expectedRevisionId;
  let revisionAfter = null;
  const receipt = (status, error = null) => ({
    receiptVersion: 1,
    kind: "google-docs-v2-dropdown-execution",
    status,
    stageId: plan.stage.id,
    stageType: plan.stage.type,
    target: {
      documentId: plan.target.documentId,
      tabId: plan.target.tabId ?? null,
      revisionBefore,
      revisionAfter,
    },
    hashes: {
      targetBindingsHash: contract.targetBindingsHash,
      decisionHash: contract.decisionHash,
      planFileSha256: validation.planFileSha256,
    },
    startedAt,
    completedAt: new Date().toISOString(),
    error: error ? {
      name: error.name ?? "Error",
      outcomeClass: error.outcomeClass ?? status,
      message: "Execution did not reach a verified applied state; inspect protected stage artifacts.",
    } : null,
  });

  let preDocument;
  let preDropdownsCall;
  let preTables = null;
  try {
    preDocument = await callTool({ tools, capability: "getDocument", args: { document_id: plan.target.documentId }, overrides: capabilityOverrides });
    preDropdownsCall = await callTool({
      tools,
      capability: "getDocumentDropdowns",
      args: { document_id: plan.target.documentId, ...(plan.target.tabId ? { tab_id: plan.target.tabId } : {}) },
      overrides: capabilityOverrides,
    });
    if (plan.stage.postWriteReadback?.tables === true) {
      preTables = await callTool({
        tools,
        capability: "getDocumentTables",
        args: { document_id: plan.target.documentId, ...(plan.target.tabId ? { tab_id: plan.target.tabId } : {}) },
        overrides: capabilityOverrides,
      });
    }
    checkpoints.push({ phase: "preflight-document", ...preDocument }, { phase: "preflight-dropdowns", ...preDropdownsCall });
    if (preTables) checkpoints.push({ phase: "preflight-tables", ...preTables });
    const identity = documentIdentity(preDocument.result);
    const dropdownIdentity = dropdownReadIdentity(preDropdownsCall.result);
    assert(identity.documentId === plan.target.documentId, "Preflight returned the wrong document");
    assert(identity.revisionId === plan.target.expectedRevisionId, "Preflight revision is stale");
    assert(identity.title === plan.target.title, "Preflight title changed");
    assert(dropdownIdentity.documentId === identity.documentId, "Preflight dropdown metadata belongs to the wrong document");
    assert(dropdownIdentity.revisionId === identity.revisionId, "Preflight document and dropdown revisions differ");
    if (plan.target.tabId !== null && plan.target.tabId !== undefined) assert(dropdownIdentity.tabId === null || dropdownIdentity.tabId === plan.target.tabId, "Preflight dropdown metadata belongs to the wrong tab");
    revisionBefore = identity.revisionId;
    assertFrozenSemantics(preDocument.result, preDropdownsCall.result, contract);
  } catch (error) {
    const status = classifyFailure(error);
    throw new DropdownExecutorError(error.message ?? String(error), { receipt: receipt(status, error), checkpoints, raw: error.raw ?? null });
  }

  let mutation;
  try {
    mutation = await callTool({
      tools,
      capability: mutationCapability(plan.stage),
      args: mutationArgs(plan.stage),
      overrides: capabilityOverrides,
    });
    checkpoints.push({ phase: "mutation", ...mutation });
  } catch (error) {
    const outcomeClass = classifyFailure(error, "unknown_application_state");
    if (["rejected_before_apply", "stale_revision", "ambiguous_anchor", "rate_limited_before_apply"].includes(outcomeClass)) {
      throw new DropdownExecutorError(error.message ?? String(error), {
        receipt: receipt(outcomeClass, error),
        checkpoints,
        raw: error.raw ?? null,
      });
    }
    throw new DropdownExecutorError(`Mutation outcome is ambiguous: ${error.message ?? String(error)}`, {
      receipt: receipt(outcomeClass === "applied_readback_failed" ? "applied_readback_failed" : "unknown_application_state", error),
      checkpoints,
      raw: error.raw ?? null,
    });
  }

  let postDocument;
  let postDropdownsCall;
  let postTables = null;
  try {
    postDocument = await callTool({ tools, capability: "getDocument", args: { document_id: plan.target.documentId }, overrides: capabilityOverrides });
    postDropdownsCall = await callTool({
      tools,
      capability: "getDocumentDropdowns",
      args: { document_id: plan.target.documentId, ...(plan.target.tabId ? { tab_id: plan.target.tabId } : {}) },
      overrides: capabilityOverrides,
    });
    if (plan.stage.postWriteReadback?.tables === true) {
      postTables = await callTool({
        tools,
        capability: "getDocumentTables",
        args: { document_id: plan.target.documentId, ...(plan.target.tabId ? { tab_id: plan.target.tabId } : {}) },
        overrides: capabilityOverrides,
      });
    }
    checkpoints.push({ phase: "post-document", ...postDocument }, { phase: "post-dropdowns", ...postDropdownsCall });
    if (postTables) checkpoints.push({ phase: "post-tables", ...postTables });
  } catch (error) {
    throw new DropdownExecutorError(error.message ?? String(error), { receipt: receipt("applied_readback_failed", error), checkpoints, raw: error.raw ?? null });
  }

  try {
    const identity = documentIdentity(postDocument.result);
    const dropdownIdentity = dropdownReadIdentity(postDropdownsCall.result);
    assert(identity.documentId === plan.target.documentId, "Post-write readback returned the wrong document");
    assert(identity.revisionId && identity.revisionId !== revisionBefore, "Post-write revision did not change");
    assert(dropdownIdentity.documentId === identity.documentId, "Post-write dropdown metadata belongs to the wrong document");
    assert(dropdownIdentity.revisionId === identity.revisionId, "Post-write document and dropdown revisions differ");
    if (plan.target.tabId !== null && plan.target.tabId !== undefined) assert(dropdownIdentity.tabId === null || dropdownIdentity.tabId === plan.target.tabId, "Post-write dropdown metadata belongs to the wrong tab");
    revisionAfter = identity.revisionId;
    const preRecords = dropdownRecords(preDropdownsCall.result);
    const postRecords = dropdownRecords(postDropdownsCall.result);
    assertExpectedAfter(plan, preRecords, postRecords, mutation.result);
    const ignoredBindingIds = ["dropdown_replace_options", "dropdown_set_selected"].includes(plan.stage.type)
      ? [bindingForOperation(contract, plan.stage.call.operation).bindingId]
      : [];
    assertFrozenSemantics(postDocument.result, postDropdownsCall.result, contract, { ignoredBindingIds });
    return { receipt: receipt("applied"), checkpoints };
  } catch (error) {
    throw new DropdownExecutorError(error.message ?? String(error), { receipt: receipt("verification_failed", error), checkpoints, raw: error.raw ?? null });
  }
}

export async function reconcileUnknownDropdownMutation({ plan, contract, validation, tools, capabilityOverrides = {} } = {}) {
  validateHostInputs(plan, contract, validation);
  assert(plan.stage.type !== "docs_batch_update", "Only dropdown mutations support semantic reconciliation");
  const read = await callTool({
    tools,
    capability: "getDocumentDropdowns",
    args: { document_id: plan.target.documentId, ...(plan.target.tabId ? { tab_id: plan.target.tabId } : {}) },
    overrides: capabilityOverrides,
  });
  const records = dropdownRecords(read.result);
  try {
    assertExpectedAfter(plan, [], records, null);
    return { status: "applied", resolvedTool: read.resolvedTool };
  } catch {
    return { status: "not_proven", resolvedTool: read.resolvedTool };
  }
}
