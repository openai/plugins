import {
  assert,
  rangesOverlap,
  requireArray,
  requireInteger,
  requireRecord,
  requireString,
  sha256Json,
} from "./dropdown-common.mjs";
import { verifyDropdownInventory } from "./dropdown-inventory.mjs";

export const DROPDOWN_CONTRACT_VERSION = 1;

function normalizeRange(value, path) {
  const range = requireRecord(value, path);
  const startIndex = requireInteger(range.startIndex, `${path}.startIndex`, { minimum: 0 });
  const endIndex = requireInteger(range.endIndex, `${path}.endIndex`, { minimum: startIndex });
  return { tabId: range.tabId ?? null, segmentId: range.segmentId ?? null, startIndex, endIndex };
}

export function freezeDropdownContract({
  inventory,
  selectedTabId = null,
  sourceDocumentIds = [],
  protectedTabIds = [],
  protectedRanges = [],
} = {}) {
  verifyDropdownInventory(inventory);
  assert(!sourceDocumentIds.includes(inventory.document.id), "Target document cannot also be a source document");
  const base = {
    contractVersion: DROPDOWN_CONTRACT_VERSION,
    target: {
      documentId: inventory.document.id,
      title: inventory.document.title ?? null,
      revisionId: inventory.document.revisionId,
      selectedTabId,
      inventorySha256: inventory.sha256,
    },
    sourceDocumentIds: [...new Set(sourceDocumentIds)],
    protectedTabIds: [...new Set(protectedTabIds)],
    protectedRanges: protectedRanges.map((range, index) => normalizeRange(range, `protectedRanges[${index}]`)),
    semanticElements: inventory.semanticElements,
  };
  return {
    ...base,
    targetBindingsHash: sha256Json({ target: base.target, semanticElements: base.semanticElements }),
    decisionHash: sha256Json({
      sourceDocumentIds: base.sourceDocumentIds,
      protectedTabIds: base.protectedTabIds,
      protectedRanges: base.protectedRanges,
    }),
  };
}

export function validateDropdownContract(value, inventory) {
  const contract = requireRecord(value, "contract");
  verifyDropdownInventory(inventory);
  assert(contract.contractVersion === DROPDOWN_CONTRACT_VERSION, `must be ${DROPDOWN_CONTRACT_VERSION}`, "contract.contractVersion");
  requireString(contract.target?.documentId, "contract.target.documentId");
  assert(contract.target.documentId === inventory.document.id, "does not match inventory", "contract.target.documentId");
  assert(contract.target.revisionId === inventory.document.revisionId, "does not match inventory", "contract.target.revisionId");
  assert(contract.target.inventorySha256 === inventory.sha256, "does not match inventory", "contract.target.inventorySha256");
  const sourceDocumentIds = requireArray(contract.sourceDocumentIds ?? [], "contract.sourceDocumentIds");
  assert(!sourceDocumentIds.includes(contract.target.documentId), "source denylist contains target document", "contract.sourceDocumentIds");
  const protectedTabIds = requireArray(contract.protectedTabIds ?? [], "contract.protectedTabIds");
  const protectedRanges = requireArray(contract.protectedRanges ?? [], "contract.protectedRanges").map((range, index) => normalizeRange(range, `contract.protectedRanges[${index}]`));
  assert(sha256Json({ target: contract.target, semanticElements: contract.semanticElements }) === contract.targetBindingsHash, "targetBindingsHash mismatch", "contract.targetBindingsHash");
  assert(sha256Json({ sourceDocumentIds, protectedTabIds, protectedRanges }) === contract.decisionHash, "decisionHash mismatch", "contract.decisionHash");
  assert(sha256Json(contract.semanticElements) === sha256Json(inventory.semanticElements), "semantic inventory mismatch", "contract.semanticElements");
  return { contract, sourceDocumentIds, protectedTabIds, protectedRanges };
}

export function assertRangeAllowed(range, contractState, path = "range") {
  assert(!contractState.protectedTabIds.includes(range.tabId ?? null), "targets a protected tab", path);
  for (const protectedRange of contractState.protectedRanges) {
    assert(!rangesOverlap(range, protectedRange), "overlaps a protected range", path);
  }
}
