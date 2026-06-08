# WDS Docs File Structure

All files are under `node_modules/@wix/design-system/dist/docs/`.

## Example File Format

````markdown
## Feature Examples

### ExampleName

- description: What it shows
- example:

```jsx
<Component prop="value">Content</Component>
```
````

## Props File Format

```markdown
### propName
- type: TypeDefinition
- description: What it does
```

## Testkit File Format

`components/{Name}Testkit.md`:

```markdown
## {Name} Testkit

### Import

- unidriver: `import { {Name}UniDriver } from '@wix/design-system/dist/testkit/unidriver';`
- vanilla: `import { {Name}Testkit } from '@wix/design-system/dist/testkit';`
- puppeteer: `import { {Name}Testkit } from '@wix/design-system/dist/testkit/puppeteer';`
- playwright: `import { {Name}Testkit } from '@wix/design-system/dist/testkit/playwright';`

### API

### methodName
- signature: methodName(arg)
- returns: Promise<ReturnType>
- description: What it does
```

## Common Components

### High-traffic (learn these patterns)

- Button, Input, FormField, Dropdown
- Table, Card, Page, Modal
- Box, Layout, Cell
