import {
  assert,
  rangesOverlap,
  requireArray,
  requireInteger,
  requireRecord,
  requireString,
  sha256Json,
} from "./dropdown-common.mjs";
import { assertRangeAllowed, validateDropdownContract } from "./dropdown-contract.mjs";
import { verifyDropdownInventory } from "./dropdown-inventory.mjs";

export const DROPDOWN_PLAN_VERSION = 1;
export const STAGE_TYPES = new Set([
  "docs_batch_update",
  "dropdown_create",
  "dropdown_replace_options",
  "dropdown_set_selected",
]);

function normalizeOptions(value, path) {
  const options = requireArray(value, path).map((option, index) => {
    const item = requireRecord(option, `${path}[${index}]`);
    return {
      label: requireString(item.label, `${path}[${index}].label`),
      ...(item.color !== undefined ? { color: item.color } : {}),
      ...(item.id !== undefined ? { id: item.id } : {}),
    };
  });
  assert(options.length > 0, "must not be empty", path);
  assert(new Set(options.map((option) => option.label)).size === options.length, "labels must be unique", path);
  return options;
}

function normalizeLocation(value, path) {
  const location = requireRecord(value, path);
  return {
    tabId: location.tabId ?? null,
    segmentId: location.segmentId ?? null,
    index: requireInteger(location.index, `${path}.index`, { minimum: 0 }),
  };
}

function requestRange(request) {
  const payload = request.deleteContentRange ?? request.updateTextStyle ?? request.updateParagraphStyle ?? request.createParagraphBullets ?? request.deleteParagraphBullets;
  if (payload?.range) return payload.range;
  const locationPayload = request.insertText ?? request.insertTable ?? request.insertPageBreak ?? request.insertInlineImage ?? request.insertDate ?? request.insertPerson ?? request.insertRichLink;
  const location = locationPayload?.location ?? locationPayload?.endOfSegmentLocation ?? null;
  if (location && Number.isInteger(location.index)) return { ...location, startIndex: location.index, endIndex: location.index + 1 };
  const tableLocation = request.insertTableRow?.tableCellLocation?.tableStartLocation ?? request.insertTableColumn?.tableCellLocation?.tableStartLocation ?? request.deleteTableRow?.tableCellLocation?.tableStartLocation ?? request.deleteTableColumn?.tableCellLocation?.tableStartLocation;
  if (tableLocation && Number.isInteger(tableLocation.index)) return { ...tableLocation, startIndex: tableLocation.index, endIndex: tableLocation.index + 1 };
  return null;
}

function normalizeDocsStage(stage, contractState) {
  const call = requireRecord(stage.call, "plan.stage.call");
  assert(call.document_id === contractState.contract.target.documentId, "document_id does not match target", "plan.stage.call.document_id");
  const writeControl = requireRecord(call.write_control, "plan.stage.call.write_control");
  assert(writeControl.requiredRevisionId === contractState.contract.target.revisionId, "requiredRevisionId does not match target revision", "plan.stage.call.write_control.requiredRevisionId");
  const requests = requireArray(call.requests, "plan.stage.call.requests");
  assert(requests.length > 0, "must not be empty", "plan.stage.call.requests");
  const expectedBefore = requireRecord(stage.expectedBefore, "plan.stage.expectedBefore");
  assert(expectedBefore.revisionId === contractState.contract.target.revisionId, "does not match target revision", "plan.stage.expectedBefore.revisionId");
  assert(expectedBefore.targetBindingsHash === contractState.contract.targetBindingsHash, "does not match frozen bindings", "plan.stage.expectedBefore.targetBindingsHash");
  const expectedAfter = requireRecord(stage.expectedAfter, "plan.stage.expectedAfter");
  assert(expectedAfter.revisionChanged === true, "must be true", "plan.stage.expectedAfter.revisionChanged");
  assert(expectedAfter.semanticBindingsPreserved === true, "must be true", "plan.stage.expectedAfter.semanticBindingsPreserved");
  requests.forEach((request, index) => {
    const item = requireRecord(request, `plan.stage.call.requests[${index}]`);
    assert(Object.keys(item).length === 1, "must contain exactly one request type", `plan.stage.call.requests[${index}]`);
    assert(!item.replaceAllText && !item.replaceNamedRangeContent, "broad replacement requests are not allowed in dropdown code mode", `plan.stage.call.requests[${index}]`);
    const range = requestRange(item);
    if (!range) return;
    assertRangeAllowed(range, contractState, `plan.stage.call.requests[${index}]`);
    for (const binding of contractState.contract.semanticElements) {
      assert(!rangesOverlap(range, binding.locator), `intersects preserved semantic element ${binding.bindingId}`, `plan.stage.call.requests[${index}]`);
    }
  });
  return { ...stage, call: { ...call, requests }, expectedBefore, expectedAfter };
}

function validateStageGuards(stage, contractState) {
  const assertions = requireRecord(stage.preservationAssertions, "plan.stage.preservationAssertions");
  assert(assertions.preserveUntouchedSemanticBindings === true, "must be true", "plan.stage.preservationAssertions.preserveUntouchedSemanticBindings");
  const bindingIds = requireArray(assertions.semanticBindingIds, "plan.stage.preservationAssertions.semanticBindingIds");
  const expectedIds = contractState.contract.semanticElements.map((binding) => binding.bindingId).sort();
  assert(sha256Json([...bindingIds].sort()) === sha256Json(expectedIds), "must enumerate every frozen semantic binding", "plan.stage.preservationAssertions.semanticBindingIds");
  const readback = requireRecord(stage.postWriteReadback, "plan.stage.postWriteReadback");
  assert(readback.documentStructure === true, "must be true", "plan.stage.postWriteReadback.documentStructure");
  assert(readback.dropdownMetadata === true, "must be true", "plan.stage.postWriteReadback.dropdownMetadata");
}

function exactDropdownById(inventory, dropdownId, path) {
  const matches = inventory.dropdowns.filter((binding) => binding.semanticProperties.dropdownId === dropdownId);
  assert(matches.length === 1, matches.length ? "is ambiguous" : "does not identify a live dropdown", path);
  return matches[0];
}

function exactDropdownTarget(inventory, operation) {
  if (operation.dropdown_id !== undefined && operation.dropdown_id !== null) {
    return exactDropdownById(inventory, requireString(operation.dropdown_id, "plan.stage.call.operation.dropdown_id"), "plan.stage.call.operation.dropdown_id");
  }
  const bindingId = requireString(operation.binding_id, "plan.stage.call.operation.binding_id");
  const matches = inventory.dropdowns.filter((binding) => binding.bindingId === bindingId);
  assert(matches.length === 1, matches.length ? "is ambiguous" : "does not identify a live dropdown", "plan.stage.call.operation.binding_id");
  const locator = requireRecord(operation.locator, "plan.stage.call.operation.locator");
  assert(sha256Json(locator) === sha256Json(matches[0].locator), "does not match the binding locator", "plan.stage.call.operation.locator");
  assert(operation.semantic_signature === matches[0].semanticProperties.signature, "does not match the binding signature", "plan.stage.call.operation.semantic_signature");
  return matches[0];
}

function normalizeDropdownStage(stage, inventory, contractState) {
  const call = requireRecord(stage.call, "plan.stage.call");
  assert(call.document_id === inventory.document.id, "document_id does not match target", "plan.stage.call.document_id");
  assert(call.tab_id === inventory.selectedTabId, "tab_id does not match selected tab", "plan.stage.call.tab_id");
  assert(call.required_revision_id === inventory.document.revisionId, "required_revision_id does not match target revision", "plan.stage.call.required_revision_id");
  requireString(call.idempotency_key, "plan.stage.call.idempotency_key");
  const operation = requireRecord(call.operation, "plan.stage.call.operation");
  const expectedType = stage.type === "dropdown_set_selected" ? "set_selected_value" : stage.type.replace("dropdown_", "");
  assert(operation.type === expectedType, `must be ${expectedType}`, "plan.stage.call.operation.type");
  assert(Object.prototype.hasOwnProperty.call(operation, "selected_value"), "is required", "plan.stage.call.operation.selected_value");
  if (stage.type === "dropdown_create") {
    const location = normalizeLocation(operation.location, "plan.stage.call.operation.location");
    assert(location.tabId === inventory.selectedTabId, "location tab does not match selected tab", "plan.stage.call.operation.location.tabId");
    assertRangeAllowed({ ...location, startIndex: location.index, endIndex: location.index + 1 }, contractState, "plan.stage.call.operation.location");
    operation.options = normalizeOptions(operation.options, "plan.stage.call.operation.options");
    if (operation.selected_value !== null) {
      assert(operation.options.some((option) => option.label === operation.selected_value), "must name one of the options", "plan.stage.call.operation.selected_value");
    }
    requireRecord(operation.anchor, "plan.stage.call.operation.anchor");
    const expectedBefore = requireRecord(operation.expected_before, "plan.stage.call.operation.expected_before");
    assert(expectedBefore.dropdownAbsent === true, "must be true", "plan.stage.call.operation.expected_before.dropdownAbsent");
  } else {
    const binding = exactDropdownTarget(inventory, operation);
    const dropdownId = binding.semanticProperties.dropdownId;
    assert(binding.locator.tabId === inventory.selectedTabId, "dropdown is not in the selected tab", "plan.stage.call.operation.dropdown_id");
    assertRangeAllowed(binding.locator, contractState, "plan.stage.call.operation.dropdown_id");
    if (stage.type === "dropdown_replace_options") {
      operation.options = normalizeOptions(operation.options, "plan.stage.call.operation.options");
      if (operation.selected_value !== null) {
        assert(operation.options.some((option) => option.label === operation.selected_value), "must name one of the options", "plan.stage.call.operation.selected_value");
      }
    } else {
      const selectedValue = requireString(operation.selected_value, "plan.stage.call.operation.selected_value");
      assert(binding.semanticProperties.options.some((option) => option.label === selectedValue), "must name an existing option", "plan.stage.call.operation.selected_value");
    }
    const expectedBefore = requireRecord(operation.expected_before, "plan.stage.call.operation.expected_before");
    assert((expectedBefore.dropdownId ?? null) === dropdownId, "does not match dropdown_id", "plan.stage.call.operation.expected_before.dropdownId");
    assert(expectedBefore.bindingId === binding.bindingId, "does not match binding", "plan.stage.call.operation.expected_before.bindingId");
    assert(sha256Json(normalizeOptions(expectedBefore.options, "plan.stage.call.operation.expected_before.options")) === sha256Json(binding.semanticProperties.options), "does not match live options", "plan.stage.call.operation.expected_before.options");
    assert(expectedBefore.selectedValue === binding.semanticProperties.selectedValue, "does not match live selected value", "plan.stage.call.operation.expected_before.selectedValue");
    if (binding.semanticProperties.signature !== null) {
      assert(expectedBefore.signature === binding.semanticProperties.signature, "does not match live signature", "plan.stage.call.operation.expected_before.signature");
    }
  }
  const expectedAfter = requireRecord(stage.expectedAfter, "plan.stage.expectedAfter");
  const expectedOptions = normalizeOptions(expectedAfter.options, "plan.stage.expectedAfter.options");
  if (["dropdown_create", "dropdown_replace_options"].includes(stage.type)) {
    assert(sha256Json(expectedOptions) === sha256Json(operation.options), "does not match requested options", "plan.stage.expectedAfter.options");
  } else {
    const binding = exactDropdownTarget(inventory, operation);
    assert(sha256Json(expectedOptions) === sha256Json(binding.semanticProperties.options), "must preserve the live option set", "plan.stage.expectedAfter.options");
  }
  assert(Object.prototype.hasOwnProperty.call(expectedAfter, "selectedValue"), "is required", "plan.stage.expectedAfter.selectedValue");
  assert(expectedAfter.selectedValue === (operation.selected_value ?? null), "does not match requested selected value", "plan.stage.expectedAfter.selectedValue");
  return { ...stage, call: { ...call, operation }, expectedAfter };
}

export function validateDropdownPlan(value, { inventory, contract } = {}) {
  const plan = requireRecord(value, "plan");
  verifyDropdownInventory(inventory);
  const contractState = validateDropdownContract(contract, inventory);
  assert(plan.version === DROPDOWN_PLAN_VERSION, `must be ${DROPDOWN_PLAN_VERSION}`, "plan.version");
  assert(plan.kind === "google-docs-v2-dropdown-plan", "unsupported kind", "plan.kind");
  assert(plan.target?.documentId === inventory.document.id, "does not match inventory", "plan.target.documentId");
  assert(plan.target?.title === inventory.document.title, "does not match inventory", "plan.target.title");
  assert(plan.target?.expectedRevisionId === inventory.document.revisionId, "does not match inventory", "plan.target.expectedRevisionId");
  assert((plan.target?.tabId ?? null) === (inventory.selectedTabId ?? null), "does not match inventory", "plan.target.tabId");
  assert(plan.baseSnapshot?.sha256 === inventory.sha256, "does not match inventory", "plan.baseSnapshot.sha256");
  assert(plan.contract?.targetBindingsHash === contract.targetBindingsHash, "does not match contract", "plan.contract.targetBindingsHash");
  assert(plan.contract?.decisionHash === contract.decisionHash, "does not match contract", "plan.contract.decisionHash");
  assert(!contractState.sourceDocumentIds.includes(plan.target.documentId), "target is source-denylisted", "plan.target.documentId");
  const stage = requireRecord(plan.stage, "plan.stage");
  assert(STAGE_TYPES.has(stage.type), "unsupported stage type", "plan.stage.type");
  requireString(stage.id, "plan.stage.id");
  validateStageGuards(stage, contractState);
  const normalizedStage = stage.type === "docs_batch_update"
    ? normalizeDocsStage(stage, contractState)
    : normalizeDropdownStage(stage, inventory, contractState);
  const normalized = { ...plan, stage: normalizedStage };
  return {
    plan: normalized,
    summary: {
      documentId: inventory.document.id,
      tabId: inventory.selectedTabId,
      stageId: stage.id,
      stageType: stage.type,
      dropdownCount: inventory.dropdowns.length,
      opaqueControlCount: inventory.opaqueControls.length,
      planSha256: sha256Json(normalized),
    },
  };
}
