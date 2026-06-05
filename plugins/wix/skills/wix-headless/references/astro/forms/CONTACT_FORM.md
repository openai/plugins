# Recipe: Contact / Lead / Signup Form

Build a complete form feature using `@wix/forms` — server-side schema fetching + client-side submission.

> **Critical Rules — Read Before Starting**
> 1. **Style migration mandatory** — when replacing `.astro` placeholder with a React island, copy the `<style is:global>` block to the page file or all form styles vanish (invisible inputs on dark sites).
> 2. **Form creation is TWO steps** — POST to create, then PATCH to add `postSubmissionTriggers`. Skipping the PATCH means submissions are silently lost (no CRM Contact created).
> 3. **Namespace propagation** — if form creation fails with `UNSUPPORTED_FORM_NAMESPACE`, wait 10s and retry up to 3 times. Do NOT fall back to hardcoded fields — a form without a `formId` cannot submit to Wix.
> 4. **Discover forms via SDK** — use `forms.listForms("wix.form_app.form")` with `auth.elevate`. Never hardcode form field IDs or form ID.

> **⚠️ CRITICAL — Style Migration Required:** When you replace the designed `.astro` form placeholder with a React island, the placeholder's `<style is:global>` block is no longer rendered and ALL form styles vanish. You MUST copy the entire `<style is:global>` block from the designed component into the page file. Without this, form inputs are invisible on dark sites. See Step 1.4 below.

## Prerequisites

- Wix Forms app must be installed on the site (installed via the apps-installer REST endpoint after scaffolding, or manually in the Wix dashboard)
- `@wix/forms` package installed: `npm install @wix/forms`

> **Forms are auto-created during scaffolding.** When scaffolding with a forms template (e.g., the Registration template `e5d63bf1-cd06-48eb-ad77-0da9235adcf1`), a form is automatically created on the site with server-side privileges. Use `forms.listForms("wix.form_app.form")` with `auth.elevate` to discover it — no manual form ID needed. If no forms exist, use the REST API Form Setup below to create one (the Create Form API is not available to headless SDK calls, but the CLI-minted REST token can create forms).

## Form Setup (REST)

Before writing any form code, ensure a contact form exists on the site via the form-schema REST API:

1. **List forms** — `REST: GET https://www.wixapis.com/form-schema-service/v4/forms?namespace=wix.form_app.form`
2. **If the API returns a "missing installed app" error** → install the Wix Forms app:
   ```
   REST: POST https://www.wixapis.com/apps-installer-service/v1/app-instance/install
   body: {
     "tenant": { "tenantType": "SITE", "id": "<siteId>" },
     "appInstance": { "appDefId": "225dd912-7dea-4738-8688-4b8c6955ffc2", "enabled": true }
   }
   ```
   > Translate this prose-HTTP form into the full `curl` tool-call shape — pass `body` as JSON in `-d` (NOT a stringified JSON). See `../../shared/AUTHENTICATION.md` for the standard REST headers.

   Then retry listing forms.
3. **If forms list is empty** → create a form (two-step atomic operation):
   - **Step 3a:** POST to create the form (fields, layout, submit settings)
   - **Step 3b:** Immediately PATCH to add `postSubmissionTriggers` (the POST silently drops this field — see step 4)
   - Both steps must succeed. If 3a succeeds but 3b fails, log Status as `partial`.

   > **Namespace propagation:** If form creation fails with `UNSUPPORTED_FORM_NAMESPACE` immediately after installing the Forms app, the namespace hasn't propagated yet. Wait 10 seconds and retry up to 3 times. Do NOT silently fall back to static field definitions — forms without a `formId` cannot submit to Wix.

   Select only the fields needed for the form's purpose.

   **Field building blocks** — assemble the `formFields` array from these individual definitions:

   ```jsonc
   // EMAIL (required for all form types)
   {
     "id": "191b2fae-7313-467a-9d4f-fd85598b1bdb",
     "hidden": false, "identifier": "CONTACTS_EMAIL", "fieldType": "INPUT",
     "inputOptions": {
       "target": "email", "pii": true, "required": true, "inputType": "STRING", "readOnly": false,
       "stringOptions": { "validation": { "format": "EMAIL", "enum": [] }, "componentType": "TEXT_INPUT", "textInputOptions": { "label": "Email", "showLabel": true } }
     }
   }

   // FIRST_NAME
   {
     "id": "c16f3def-fc74-4950-3b72-46dbdc132a90",
     "hidden": false, "identifier": "CONTACTS_FIRST_NAME", "fieldType": "INPUT",
     "inputOptions": {
       "target": "first_name", "pii": true, "required": false, "inputType": "STRING", "readOnly": false,
       "stringOptions": { "validation": { "format": "UNKNOWN_FORMAT", "enum": [] }, "componentType": "TEXT_INPUT", "textInputOptions": { "label": "First name", "showLabel": true } }
     }
   }

   // LAST_NAME
   {
     "id": "84242617-c855-486f-4ec6-87443210fb4f",
     "hidden": false, "identifier": "CONTACTS_LAST_NAME", "fieldType": "INPUT",
     "inputOptions": {
       "target": "last_name", "pii": true, "required": false, "inputType": "STRING", "readOnly": false,
       "stringOptions": { "validation": { "format": "UNKNOWN_FORMAT", "enum": [] }, "componentType": "TEXT_INPUT", "textInputOptions": { "label": "Last name", "showLabel": true } }
     }
   }

   // PHONE
   {
     "id": "5f5995cc-2951-4ce9-ae89-82ff487b1619",
     "hidden": false, "identifier": "CONTACTS_PHONE", "fieldType": "INPUT",
     "inputOptions": {
       "target": "phone", "pii": true, "required": false, "inputType": "STRING", "readOnly": false,
       "stringOptions": { "validation": { "format": "PHONE", "enum": [] }, "componentType": "PHONE_INPUT", "phoneInputOptions": { "label": "Phone", "showLabel": true } }
     }
   }

   // MESSAGE
   // ⚠️ **Naming trap:** The MESSAGE field uses `identifier: "TEXT_AREA"` but its
   // `componentType` MUST be `"TEXT_INPUT"`. The API will reject `componentType: "TEXT_AREA"`
   // — that enum value does not exist in the Forms API. The `identifier` controls how the
   // Wix dashboard renders the field; `componentType` controls API schema validation.
   // Do not confuse the two.
   {
     "id": "ce6fc634-bc35-48ef-6f01-c2cded75d836",
     "hidden": false, "identifier": "TEXT_AREA", "fieldType": "INPUT",
     "inputOptions": {
       "target": "message", "pii": false, "required": false, "inputType": "STRING", "readOnly": false,
       "stringOptions": { "validation": { "format": "UNKNOWN_FORMAT", "enum": [] }, "componentType": "TEXT_INPUT", "textInputOptions": { "label": "Message", "showLabel": true } }
     }
   }

   // SUBMIT BUTTON (always include as the last field)
   {
     "id": "fe946b52-9719-4c57-57e8-a0791c29344f",
     "hidden": false, "identifier": "SUBMIT_BUTTON", "fieldType": "DISPLAY",
     "displayOptions": { "displayFieldType": "PAGE_NAVIGATION", "pageNavigationOptions": { "nextPageText": "Next", "previousPageText": "Back", "submitText": "Submit" } }
   }
   ```

   **Assembly by purpose:**

   | Purpose | Fields to include | Layout rows |
   |---------|------------------|-------------|
   | Waitlist / newsletter | EMAIL + SUBMIT | email row 0, submit row 1 |
   | Lead capture | FIRST_NAME + EMAIL + SUBMIT | first_name row 0, email row 1, submit row 2 |
   | Contact (full) | FIRST_NAME + LAST_NAME + EMAIL + PHONE + MESSAGE + SUBMIT | first+last row 0 (6+6 cols), email row 1, phone row 2, message row 3, submit row 4 |

   Build the `steps[0].layout.large.items` array to match — each field gets a `{ fieldId, row, column, width: 12, height: 1 }` entry. For side-by-side fields (first + last name), use `width: 6` with `column: 0` and `column: 6`.

   The `postSubmissionTriggers.upsertContact.fieldsMapping` must only include mappings for fields that exist on the form. For a waitlist form with email only:
   ```json
   "fieldsMapping": {
     "email": { "contactField": "EMAIL", "emailInfo": { "tag": "UNTAGGED" } }
   }
   ```

   Full REST call structure:
   ```
   REST: POST https://www.wixapis.com/form-schema-service/v4/forms
   body: {
     "form": {
       "formFields": [ <selected fields from above> ],
       "steps": [{ "id": "cfa7a3ed-ef11-4ae7-3a5b-7d450c86d217", "name": "Page 1", "hidden": false,
         "layout": { "large": { "items": [ <layout entries matching selected fields> ] }}
       }],
       "name": "<Form Name matching purpose>",
       "namespace": "wix.form_app.form",
       "spamFilterProtectionLevel": "ADVANCED",
       "enabled": true,
       "postSubmissionTriggers": {
         "upsertContact": {
           "fieldsMapping": { <only mappings for included contact fields> },
           "labels": []
         }
       },
       "submitSettings": {
         "submitSuccessAction": "THANK_YOU_MESSAGE",
         "thankYouMessageOptions": {
           "durationInSeconds": 8,
           "richContent": { "nodes": [{ "type": "PARAGRAPH", "id": "krhc065", "nodes": [{ "type": "TEXT", "id": "", "nodes": [], "textData": { "text": "Thanks, we received your submission.", "decorations": [] } }], "paragraphData": { "textStyle": { "textAlignment": "CENTER" } } }] }
         }
       }
     }
   }
   ```
4. **Always PATCH `postSubmissionTriggers` after creation** — The creation API silently drops this field. Treat form creation as a two-step atomic operation:
   - Step A: `POST /forms` to create the form
   - Step B: `PATCH /forms/<formId>` to add `postSubmissionTriggers`
   Never skip Step B, even if you included triggers in the creation payload. The cost of a redundant PATCH is zero; the cost of missing triggers is silent data loss (submissions recorded but no CRM contact created).
   - GET the form: `GET https://www.wixapis.com/form-schema-service/v4/forms?namespace=wix.form_app.form`
   - PATCH using the procedure in step 5 below
5. **If forms already exist** → verify the form has `postSubmissionTriggers.upsertContact`. This field is **critical** — without it, submissions are recorded but no Contact is created in the CRM. If missing, patch the form to add it:
   ```
   REST: PATCH https://www.wixapis.com/form-schema-service/v4/forms/<formId>
   body: {
     "form": {
       "revision": "<current revision from GET>",
       "postSubmissionTriggers": {
         "upsertContact": {
           "fieldsMapping": {
             <map each contact field target in the form, e.g.:>
             "email": { "contactField": "EMAIL", "emailInfo": { "tag": "UNTAGGED" } },
             "first_name": { "contactField": "FIRST_NAME" },
             "last_name": { "contactField": "LAST_NAME" },
             "phone": { "contactField": "PHONE", "phoneInfo": { "tag": "UNTAGGED" } }
           },
           "labels": []
         }
       }
     }
   }
   ```
   Only include mappings for fields that exist on the form. The `fieldsMapping` keys must match the `inputOptions.target` values of the form's fields.

## Files to Modify / Create

| File | Action |
|------|--------|
| Existing designed page (e.g., `src/pages/contact.astro`) | **Modify in place** — add SDK imports and replace placeholder form with React island |
| `src/components/ContactForm.tsx` | **Create** — React island for client-side submission |

## Implementation

### 1. Modify the Existing Designed Page

**Do NOT create a new page from scratch.** The design skill already created this page with branded styling, layout, and a `<style>` block. Modify it in place:

1. **Add SDK imports** to the frontmatter:
   ```astro
   import { forms } from "@wix/forms";
   import { auth } from "@wix/essentials";
   import ContactForm from "../components/ContactForm.tsx";
   ```

2. **Add the form discovery query** to the frontmatter:
   ```astro
   const elevatedListForms = auth.elevate(forms.listForms);
   const listResult = await elevatedListForms("wix.form_app.form");
   const wixForm = listResult.forms?.[0];
   const formId = wixForm?._id ?? "";

   const formFields = wixForm?.formFields
     ?.filter((field) => field.fieldType === "INPUT" && !field.hidden)
     .map((field) => {
       const opts = field.inputOptions;
       const str = opts?.stringOptions;
       const label =
         str?.textInputOptions?.label ??
         str?.dropdownOptions?.label ??
         str?.phoneInputOptions?.label ??
         "";
       return {
         label,
         target: opts?.target ?? "",
         required: opts?.required ?? false,
         componentType: str?.componentType ?? "TEXT_INPUT",
         identifier: field.identifier ?? "",
         options: str?.dropdownOptions?.options?.map((o) => ({
           value: o.value ?? o.label ?? "",
           label: o.label ?? o.value ?? "",
         })),
       };
     }) ?? [];
   ```

3. **Replace the placeholder form HTML** with the React island:
   ```astro
   {formId ? (
     <ContactForm client:load formId={formId} fields={formFields} />
   ) : (
     <p>No form found. Create one in the Wix dashboard.</p>
   )}
   ```

4. **Migrate the form's `<style is:global>` block into the page.**

   The designed Astro placeholder component (e.g., `ContactForm.astro`) contains a `<style is:global>` block with all form CSS. Once you replace the Astro import with the React island, that component is no longer rendered and its styles vanish.

   - Open the designed Astro placeholder component and copy its entire `<style is:global>...</style>` block
   - Paste it into the page file, below any existing `<style>` block
   - Keep both `<style>` blocks — the page's scoped styles handle layout, the `is:global` block handles form elements inside the React island
   - Do NOT remove or modify the page's existing `<style>` block

   **Why `is:global` is required:** Astro scoped styles use `data-astro-cid-*` attributes that don't transfer to React-rendered DOM. The form styles must be global to reach elements inside the React island.

### 2. Contact Form Component (`src/components/ContactForm.tsx`)

The React island must match the designed component's class names and use CSS variables for all visual properties. Two approaches:

**Approach A (preferred): Page provides styles via `<style>` block.** The component reuses the class names from the designed placeholder. The page's existing `<style>` block handles all visual styling. The component only needs minimal inline styles for dynamic states.

**Approach B: Component owns its styles using CSS variables.** If the page doesn't have a `<style>` block for the form, the component includes a `<style>` JSX element using only CSS custom properties.

> **Styling note:** The React island uses the styling contract class names (`.form-container`, `.form-field`, `.form-label`, `.form-input`, `.form-textarea`, `.form-button`, `.form-success`, `.form-error`, `.form-field-error`, `.form-input-error`) from the designed ContactForm component's `<style is:global>` block. See the design skill's `COMPONENT_PATTERNS.md` → Contact Form.

```tsx
import { useState } from "react";
import { submissions } from "@wix/forms";

interface FormField {
  label: string;
  target: string;
  required: boolean;
  componentType: string;
  identifier?: string;
  options?: { value: string; label: string }[];
}

interface ContactFormProps {
  formId: string;
  fields: FormField[];
}

export default function ContactForm({ formId, fields }: ContactFormProps) {
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setFieldErrors({});

    try {
      const result = await submissions.createSubmission({
        formId,
        submissions: formData,
      });

      if (result.status === "PENDING" || result.status === "CONFIRMED") {
        setStatus("success");
        setFormData({});
      } else {
        setStatus("error");
      }
    } catch (err: unknown) {
      const violations =
        (err as any)?.details?.validationError?.fieldViolations ?? [];
      const errorMap: Record<string, string> = {};

      for (const v of violations) {
        const fieldErrs: { errorPath?: string; errorMessage?: string }[] =
          v?.data?.errors ?? [];
        for (const fe of fieldErrs) {
          if (fe.errorPath && !errorMap[fe.errorPath]) {
            errorMap[fe.errorPath] = fe.errorMessage ?? "Invalid value";
          }
        }
      }

      if (Object.keys(errorMap).length > 0) {
        setFieldErrors(errorMap);
        setStatus("idle");
      } else {
        setStatus("error");
      }
    }
  };

  if (status === "success") {
    return (
      <div className="form-success">
        Thank you! We'll be in touch soon.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="form-container">
      {/* Styles come from the designed component's <style is:global> block.
          Uses styling contract classes: .form-container, .form-field, .form-label,
          .form-input, .form-select, .form-textarea, .form-button, .form-error,
          .form-field-error, .form-input-error.
          See design skill's COMPONENT_PATTERNS.md → Contact Form. */}

      {fields.map((field) => (
        <div key={field.target} className="form-field">
          <label className="form-label">
            {field.label}
            {field.required && <span className="required">*</span>}
          </label>
          {field.componentType === "DROPDOWN" && field.options ? (
            <select
              required={field.required}
              value={formData[field.target] ?? ""}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, [field.target]: e.target.value }))
              }
              className={`form-select${fieldErrors[field.target] ? " form-input-error" : ""}`}
            >
              <option value="">Select an option</option>
              {field.options.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          ) : field.identifier === "TEXT_AREA" || field.target === "message" ? (
            <textarea
              required={field.required}
              value={formData[field.target] ?? ""}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, [field.target]: e.target.value }))
              }
              rows={4}
              className={`form-textarea${fieldErrors[field.target] ? " form-input-error" : ""}`}
            />
          ) : (
            <input
              type={
                field.target === "email" ? "email" :
                field.componentType === "PHONE_INPUT" ? "tel" : "text"
              }
              required={field.required}
              value={formData[field.target] ?? ""}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, [field.target]: e.target.value }))
              }
              className={`form-input${fieldErrors[field.target] ? " form-input-error" : ""}`}
              {...(field.componentType === "PHONE_INPUT" ? { placeholder: "+1234567890" } : {})}
            />
          )}
          {fieldErrors[field.target] && (
            <p className="form-field-error">{fieldErrors[field.target]}</p>
          )}
        </div>
      ))}

      <button
        type="submit"
        disabled={status === "submitting"}
        className="form-button"
      >
        {status === "submitting" ? "Sending..." : "Send Message"}
      </button>

      {status === "error" && (
        <p className="form-error">Something went wrong. Please try again.</p>
      )}
    </form>
  );
}
```

> **Adapting class names:** The class names above (`form-container`, `form-field`, `form-label`, `form-input`, `form-button`, `form-success`, `form-error`, `form-field-error`, `form-input-error`) are defaults. If the designed component uses different class names, use those instead — the styling contract from the design skill takes precedence.

## Discovering Forms

Forms are auto-created when scaffolding with a forms template. Use `auth.elevate(forms.listForms)` with the `"wix.form_app.form"` namespace to discover them — no hardcoded ID needed:

```typescript
import { forms } from "@wix/forms";
import { auth } from "@wix/essentials";

const elevatedListForms = auth.elevate(forms.listForms);
const listResult = await elevatedListForms("wix.form_app.form");
const wixForm = listResult.forms?.[0];
const formId = wixForm?._id;
```

If no forms exist, use the REST API Form Setup section above to create one via `curl`. If curl auth is not available, create one in the Wix dashboard (Forms section → Add New Form).

## Form Field Schema (SDK Types)

Each field in `formFields` has this structure when `fieldType === "INPUT"`:

```typescript
field.identifier                                             // "CONTACTS_EMAIL", "TEXT_AREA", "SUBMIT_BUTTON", etc.
field.inputOptions.target                                    // "email", "first_name", "message", custom UUIDs
field.inputOptions.required                                  // boolean
field.inputOptions.stringOptions.componentType               // "TEXT_INPUT" | "DROPDOWN" | "PHONE_INPUT"
field.inputOptions.stringOptions.textInputOptions?.label     // label for text inputs
field.inputOptions.stringOptions.dropdownOptions?.label      // label for dropdowns
field.inputOptions.stringOptions.dropdownOptions?.options    // [{value, label}] for dropdowns
field.inputOptions.stringOptions.phoneInputOptions?.label    // label for phone inputs
```

> **⚠️ Textarea detection:** The message field's `componentType` is always `"TEXT_INPUT"` (the API rejects `"TEXT_AREA"` as a componentType value). To render a `<textarea>`, check `field.identifier === "TEXT_AREA"` or `field.target === "message"` — NOT `field.componentType`.

## Built-In Field Targets

| Target | Type | HTML Input |
|--------|------|-----------|
| `email` | Email | `type="email"` |
| `first_name` | Text | `type="text"` |
| `last_name` | Text | `type="text"` |
| `phone` | Phone | `type="tel"` |
| `company` | Text | `type="text"` |

Custom fields use UUID-based targets from the form schema.

## Log Results

After form verification, write a sidecar file at `.wix/logs/forms-data.md` (form schema setup) or `.wix/logs/forms-implementer.md` (Phase 2 wiring) — see `../../shared/LIFECYCLE_LOG.md` for the sidecar contract. Do **not** append to `.wix/lifecycle.log.md` directly — the orchestrator concatenates all sidecars at the end. Use a `####` heading so the entry nests under `### features-orchestrator` in the assembled log:

```markdown
## forms
- Status: complete
- Content: "{form name}" form created (fields: {field list})
- Images: not applicable
```

## Testing

1. Run `npx @wix/cli@latest dev`
2. Navigate to `/contact`
3. Fill in the form and submit
4. Check the Wix dashboard → Forms → Submissions to verify the data arrived