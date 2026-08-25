const MUTATING_INTENTS = new Set([
  "create",
  "replace_options",
  "set_selected_value",
]);

const REQUIRED_DROPDOWN_CAPABILITIES = new Set([
  "getDocumentDropdowns",
  "updateDocumentDropdown",
]);

export const DROPDOWN_CODE_MODE_FEATURE_FLAG = "google_docs_v2_dropdown_code_mode";

function normalizeCapabilities(capabilities) {
  if (!Array.isArray(capabilities)) return new Set();
  return new Set(capabilities.filter((value) => typeof value === "string"));
}

export function selectDocsExecutionRoute({
  dropdownIntent = "none",
  featureEnabled = false,
  capabilities = [],
  plainTextApproximationApproved = false,
} = {}) {
  if (!["none", "preserve", ...MUTATING_INTENTS].includes(dropdownIntent)) {
    throw new Error(`Unsupported dropdown intent: ${dropdownIntent}`);
  }

  if (dropdownIntent === "none" || dropdownIntent === "preserve") {
    return {
      route: "direct",
      reason: dropdownIntent === "preserve"
        ? "preservation_only"
        : "no_dropdown_mutation",
      ownsEntireTrajectory: false,
    };
  }

  if (plainTextApproximationApproved) {
    return {
      route: "direct",
      reason: "user_approved_plain_text_approximation",
      ownsEntireTrajectory: false,
      nativeDropdownResult: false,
    };
  }

  if (!featureEnabled) {
    return {
      route: "blocked",
      reason: "dropdown_code_mode_feature_disabled",
      ownsEntireTrajectory: false,
    };
  }

  const available = normalizeCapabilities(capabilities);
  const missingCapabilities = [...REQUIRED_DROPDOWN_CAPABILITIES]
    .filter((name) => !available.has(name));
  if (missingCapabilities.length > 0) {
    return {
      route: "blocked",
      reason: "dropdown_connector_capability_unavailable",
      missingCapabilities,
      ownsEntireTrajectory: false,
    };
  }

  return {
    route: "dropdown-code-mode",
    reason: `native_dropdown_${dropdownIntent}`,
    ownsEntireTrajectory: true,
    nativeDropdownResult: true,
  };
}

export {
  MUTATING_INTENTS,
  REQUIRED_DROPDOWN_CAPABILITIES,
};
