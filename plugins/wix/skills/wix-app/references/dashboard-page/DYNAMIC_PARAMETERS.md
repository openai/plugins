# Dynamic Parameters Management

Complete guide for managing dynamic parameters for embedded scripts in dashboard pages.

## Description

This dashboard page manages dynamic parameters for an embedded script. The parameters are configurable values that site owners can set through this dashboard interface, and they will be passed to the embedded script as template variables.

**IMPORTANT:** Only implement UI for parameters that are relevant to your current use case. Ignore parameters that don't apply to the functionality you're building. It's perfectly fine to not use all parameters if they're not applicable.

## Implementation Requirements

### 1. Import embeddedScripts

- Import embeddedScripts directly from '@wix/app-management'
- Use embeddedScripts.getEmbeddedScript() to load parameters
- Use embeddedScripts.embedScript({ parameters }) to save parameters
- Example:
  ```typescript
  import { embeddedScripts } from '@wix/app-management';
  ```

### 2. Type Definition

- Create a TypeScript type/interface that includes all the dynamic parameters
- Example:
  ```typescript
  export type MyScriptOptions = {
    headline: string;
    text: string;
    imageUrl: string;
    activationMode: 'active' | 'timed' | 'disabled';
    startDate?: string;
    endDate?: string;
  };
  ```

### 3. State Management

- Use React useState to manage the parameter values locally
- Initialize with default values for all parameters
- Add separate state for isLoading and isSaving
- Use useEffect to load parameters on mount
- **IMPORTANT:** Parameters are returned as strings from the API, so you must handle type conversions:
  * BOOLEAN parameters: Convert from string 'true'/'false' to boolean
  * NUMBER parameters: Convert from string to number using Number()
  * Other types: Use as-is
- Example:
  ```typescript
  const [options, setOptions] = useState<MyScriptOptions>(defaultOptions);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const embeddedScript = await embeddedScripts.getEmbeddedScript();
        const data = embeddedScript.parameters as Partial<Record<keyof MyScriptOptions, string>> || {};

        setOptions((prev) => ({
          ...prev,
          textField: data?.textField || prev.textField,
          booleanField: data?.booleanField === 'true' ? true : data?.booleanField === 'false' ? false : prev.booleanField,
          numberField: Number(data?.numberField) || prev.numberField,
        }));
      } catch (error) {
        console.error('Failed to load settings:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadSettings();
  }, []);
  ```

### 4. Loading State

- Show a Loader component while isLoading is true
- Example:
  ```typescript
  {isLoading ? (
    <Box align="center" verticalAlign="middle" height="50vh">
      <Loader text="Loading..." />
    </Box>
  ) : (
    // ... form content
  )}
  ```

### 5. Form Components

- **IMPORTANT:** Only create form fields for parameters relevant to your use case
- Skip parameters that don't apply to the functionality being built
- Create appropriate WDS form fields based on parameter types:
  * TEXT → Input component with FormField
  * NUMBER → Input component with type="number"
  * BOOLEAN → Checkbox or ToggleSwitch
  * IMAGE → Custom ImagePicker component (see components/image-picker.tsx)
  * DATE → DatePicker component
  * SELECT → Dropdown component with options
  * URL → Input with URL validation
- Use FormField wrapper for labels and validation messages
- Set required validation based on parameter.required flag
- Show validation errors using FormField status and statusMessage props

### 6. Save Functionality

- Add a Save button in the Page.Header actionsBar
- Make handleSave an async function
- **CRITICAL:** All parameters must be passed as STRING values because they are used as template variables in the embedded script
- Convert all values to strings before saving:
  * BOOLEAN: Use String(value) or value.toString()
  * NUMBER: Use String(value) or value.toString()
  * Other types: Already strings, use as-is
- Disable the Save button if required fields are missing or while saving
- Add proper error handling

### 7. Form Validation

- Implement validation for required fields
- Show error states on FormField components
- Display clear error messages

### 8. Layout and Organization

- Use Card components to group related fields
- Use Box with direction="vertical" for form layout
- Add appropriate spacing with gap props
- Include helpful descriptions using Card subtitle or FormField infoContent
- Consider creating a separate settings component for complex forms

### 9. Preview Component (Optional but Recommended)

- If applicable, create a preview component that shows how the configuration will look
- Display the preview alongside the settings form using Layout and Cell components
- The preview should react to parameter changes in real-time

## Example Implementation

See the generated site-popup example for a complete reference implementation:
- src/extensions/dashboard/withProviders.tsx - Provider wrapper with WDS
- src/extensions/dashboard/pages/page.tsx - Dashboard page with parameter management (wrapped with withProviders)
- src/extensions/dashboard/components/site-popup-settings.tsx - Settings form component
- src/extensions/dashboard/types.ts - Type definitions

Key implementation patterns from the example:
1. withProviders.tsx wraps the component with WixDesignSystemProvider
2. page.tsx exports the component wrapped: export default withProviders(MyComponent)
3. Parameters are saved as individual string fields, not as JSON
4. Parameters are loaded with proper type conversion (string to boolean, string to number, etc.)
5. Use embeddedScripts directly from '@wix/app-management'

## File Generation Requirements

When dynamic parameters are present, you MUST generate these files:
1. src/extensions/dashboard/withProviders.tsx - Provider wrapper (REQUIRED for WDS)
2. src/extensions/dashboard/pages/page.tsx - The main dashboard page component
3. src/extensions/dashboard/types.ts - Type definitions for the parameters (if needed)
4. Any additional component files (settings forms, previews, etc.)

The withProviders.tsx is NOT optional - it must always be generated when there are dynamic parameters.

## Provider Wrapper Implementation

You MUST generate the following file: src/extensions/dashboard/withProviders.tsx

This file is REQUIRED to wrap dashboard components with the Wix Design System provider.

```typescript
import React from 'react';
import { WixDesignSystemProvider } from '@wix/design-system';
import { i18n } from '@wix/essentials';

export default function withProviders<P extends {} = {}>(Component: React.FC<P>) {
  return function DashboardProviders(props: P) {
    const locale = i18n.getLocale();
    return (
      <WixDesignSystemProvider locale={locale} features={{ newColorsBranding: true }}>
        <Component {...props} />
      </WixDesignSystemProvider>
    );
  };
}

// Also export as named export for backwards compatibility
export { withProviders };
```

This file must be included in your generated files output.

## Using Provider Wrapper

In your dashboard page component (page.tsx):
1. Import the withProviders wrapper: `import withProviders from '../../withProviders';`
2. Import embeddedScripts from '@wix/app-management'
3. DO NOT wrap your component with WixDesignSystemProvider - the provider wrapper does this
4. Export the component wrapped with withProviders: `export default withProviders(MyComponent);`
5. Your component should only contain the Page component and its content, not providers

Example structure:
```typescript
import { useEffect, useState, type FC } from 'react';
import { dashboard } from '@wix/dashboard';
import { embeddedScripts } from '@wix/app-management';
import { Page, Card, Button, ... } from '@wix/design-system';
import '@wix/design-system/styles.global.css';
import withProviders from '../../withProviders';

const MyDashboardPage: FC = () => {
  const [options, setOptions] = useState<MyScriptOptions>(defaultOptions);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const embeddedScript = await embeddedScripts.getEmbeddedScript();
        const data = embeddedScript.parameters || {};
        // ... update options with data
      } catch (error) {
        console.error('Failed to load settings:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadSettings();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await embeddedScripts.embedScript({ parameters: { /* ... */ } });
      dashboard.showToast({ message: 'Saved!', type: 'success' });
    } catch (error) {
      console.error('Failed to save:', error);
      dashboard.showToast({ message: 'Failed to save', type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Page height="100vh">
      {/* Page content - NO WixDesignSystemProvider here */}
    </Page>
  );
};

export default withProviders(MyDashboardPage);
```

## Critical Notes

- Only implement UI for parameters that are relevant to your specific use case - ignore parameters that don't apply
- ALWAYS generate withProviders.tsx when there are dynamic parameters
- ALWAYS wrap the dashboard page export with withProviders()
- DO NOT use WixDesignSystemProvider directly in the dashboard page component - use withProviders instead
- ALWAYS use embeddedScripts directly from '@wix/app-management'
- ALWAYS convert parameter values to strings when saving (embeddedScripts.embedScript must receive all string values in the parameters object)
- ALWAYS convert string parameters back to proper types when loading (e.g., 'true' -> true for booleans, string to number for numbers)
- ALWAYS handle the loading state with isLoading state variable
- ALWAYS handle the saving state with isSaving state variable
- ALWAYS add try/catch blocks for async operations (loading and saving)
- ALWAYS use async/await for embeddedScripts operations
- ALWAYS merge parameter values correctly in useEffect with proper type conversions
- ALWAYS validate required fields and show appropriate error states
- The parameter keys MUST match exactly what is expected in the embedded script template variables
- Each parameter is saved as a separate field, NOT as a JSON string
