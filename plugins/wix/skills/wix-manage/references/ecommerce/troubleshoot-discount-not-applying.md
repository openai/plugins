---
name: "Troubleshoot: Discount Not Applying"
description: Diagnostic tree for when a discount rule exists but isn't applying at checkout. Checks active status, time window, scope targeting, revision, and app installation.
layer: troubleshoot
---
# Troubleshoot: Discount Not Applying

## When to use

Use this diagnostic tree when a merchant reports that a discount rule exists but products are not showing the discounted price at checkout or in the storefront.

---

## Step 1: Check rule active status

Query the discount rule by ID and verify the `active` field.

- If `active: false` → **Resolution**: "The rule is deactivated. Set `active: true` to enable it."
- If `active: true` → proceed to Step 2.

---

## Step 2: Check time window

Examine the `activeTimeInfo` field on the discount rule.

- If `activeTimeInfo` does not exist → the rule has no time constraints, proceed to Step 3.
- If `activeTimeInfo` exists:
  - Is the current date/time within the `start` and `end` range?
  - If the current date is before `start` → **Resolution**: "The campaign hasn't started yet. It begins on {startDate}."
  - If the current date is after `end` → **Resolution**: "The campaign ended on {endDate}. Update or remove the time window to re-enable."
  - If within range → proceed to Step 3.

---

## Step 3: Check scope targeting

Examine the discount rule's scope configuration:

### CATALOG scope
- Should apply to all products. If it's not applying, skip to Step 5 (app installation check).

### COLLECTION scope
- Verify that `categoryIds` contain valid GUIDs, not collection names.
- Common mistake: using the collection name string instead of its GUID.
- Call `getCategoryIds` or query collections to validate that each ID resolves to an existing collection.
- If any ID is invalid → **Resolution**: "The collection ID '{id}' does not match any existing collection. Use the collection GUID, not the display name."

### SPECIFIC_PRODUCTS scope
- Verify that each `productId` in the rule exists in the store catalog.
- Query products to confirm each ID resolves.
- If any product was deleted → **Resolution**: "Product '{id}' no longer exists in the catalog. Remove it from the discount rule or replace it with a valid product ID."

---

## Step 4: Check revision

Was the rule recently updated? A revision mismatch indicates the update failed silently.

- Query the current rule and compare the `revision` field against the expected value.
- If the revision does not match what was expected after an update → **Resolution**: "The last update to this rule may have failed. The current revision is {currentRevision}. Try updating the rule again with the correct revision number."

---

## Step 5: Check app installation

Is the Wix Stores or eCommerce app installed on the site?

- Error code `WDE0110: Wix Code not enabled` → **Resolution**: "The Wix Stores app is not installed. Install Wix Stores first, then the discount rule will take effect."
- If the eCommerce platform is not fully set up, discount rules cannot be evaluated at checkout.

---

## Step 6: Check stacking interference

Are other active discount rules conflicting with or overriding this one?

1. Query all active discount rules.
2. Check for scope overlap with the problematic rule.
3. Some discount combinations may cause unexpected behavior where one rule appears to "not apply" because another rule takes precedence.

**Resolution**: "There are {count} other active discount rules that overlap with this rule's scope. Review them to check if another rule is taking priority or if stacking behavior is masking this rule's effect."

---

## Summary: Diagnostic checklist

| Step | Check | Common resolution |
|---|---|---|
| 1 | `active` field | Set `active: true` |
| 2 | Time window | Update or remove expired `activeTimeInfo` |
| 3 | Scope targeting | Fix invalid collection/product GUIDs |
| 4 | Revision mismatch | Retry the update with correct revision |
| 5 | App installation | Install Wix Stores app |
| 6 | Stacking interference | Review and resolve overlapping rules |
