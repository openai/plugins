# Site Plugin Examples

Complete examples showing all required files for site plugins.

## Best Seller Badge Plugin

A customizable badge that displays on product pages with configurable text and colors.

### Plugin Component (`best-seller-badge.tsx`)

```typescript
class BestSellerBadge extends HTMLElement {
  static get observedAttributes() {
    return ['badge-text', 'bg-color', 'text-color'];
  }

  constructor() {
    super();
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  render() {
    const badgeText = this.getAttribute('badge-text') || 'Best Seller';
    const bgColor = this.getAttribute('bg-color') || '#ff6b35';
    const textColor = this.getAttribute('text-color') || '#ffffff';

    this.innerHTML = `
      <span style="
        display: inline-block;
        padding: 8px 16px;
        background-color: ${bgColor};
        color: ${textColor};
        font-weight: bold;
        border-radius: 4px;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
      ">${badgeText}</span>
    `;
  }
}

export default BestSellerBadge;
```

### Settings Panel (`best-seller-badge.panel.tsx`)

```typescript
import React, { type FC, useState, useEffect, useCallback } from 'react';
import { widget, inputs } from '@wix/editor';
import {
  SidePanel,
  WixDesignSystemProvider,
  Input,
  FormField,
  Box,
  FillPreview,
} from '@wix/design-system';
import '@wix/design-system/styles.global.css';

const Panel: FC = () => {
  const [badgeText, setBadgeText] = useState<string>('');
  const [bgColor, setBgColor] = useState<string>('#ff6b35');
  const [textColor, setTextColor] = useState<string>('#ffffff');

  useEffect(() => {
    Promise.all([
      widget.getProp('badge-text'),
      widget.getProp('bg-color'),
      widget.getProp('text-color'),
    ])
      .then(([text, bg, color]) => {
        setBadgeText(text || 'Best Seller');
        setBgColor(bg || '#ff6b35');
        setTextColor(color || '#ffffff');
      })
      .catch(error => console.error('Failed to fetch props:', error));
  }, []);

  const handleTextChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newText = event.target.value;
    setBadgeText(newText);
    widget.setProp('badge-text', newText);
  }, []);

  const handleBgColorChange = useCallback((value: string) => {
    setBgColor(value);
    widget.setProp('bg-color', value);
  }, []);

  const handleTextColorChange = useCallback((value: string) => {
    setTextColor(value);
    widget.setProp('text-color', value);
  }, []);

  return (
    <WixDesignSystemProvider>
      <SidePanel width="300" height="100vh">
        <SidePanel.Content noPadding stretchVertically>
          <SidePanel.Field>
            <FormField label="Badge Text">
              <Input
                type="text"
                value={badgeText}
                onChange={handleTextChange}
                aria-label="Badge Text"
              />
            </FormField>
          </SidePanel.Field>
          <SidePanel.Field>
            <FormField label="Background Color">
              <Box width="30px" height="30px">
                <FillPreview
                  fill={bgColor}
                  onClick={() => inputs.selectColor(bgColor, { onChange: (val) => { if (val) handleBgColorChange(val); } })}
                />
              </Box>
            </FormField>
          </SidePanel.Field>
          <SidePanel.Field>
            <FormField label="Text Color">
              <Box width="30px" height="30px">
                <FillPreview
                  fill={textColor}
                  onClick={() => inputs.selectColor(textColor, { onChange: (val) => { if (val) handleTextColorChange(val); } })}
                />
              </Box>
            </FormField>
          </SidePanel.Field>
        </SidePanel.Content>
      </SidePanel>
    </WixDesignSystemProvider>
  );
};

export default Panel;
```

### Extension Configuration (`best-seller-badge.extension.ts`)

```typescript
import { extensions } from '@wix/astro/builders';

export default extensions.sitePlugin({
  id: 'f8e2a1b3-c4d5-6789-abcd-ef0123456789',
  name: 'Best Seller Badge',
  marketData: {
    name: 'Best Seller Badge',
    description: 'Display a customizable badge on product pages',
    logoUrl: '{{BASE_URL}}/best-seller-badge-logo.svg',
  },
  placements: [
    {
      appDefinitionId: '1380b703-ce81-ff05-f115-39571d94dfcd',
      widgetId: '13a94f09-2766-3c40-4a32-8edb5acdd8bc',
      slotId: 'product-page-details-2',
    },
    {
      appDefinitionId: 'a0c68605-c2e7-4c8d-9ea1-767f9770e087',
      widgetId: '6a25b678-53ec-4b37-a190-65fcd1ca1a63',
      slotId: 'product-page-details-2',
    },
  ],
  installation: { autoAdd: true },
  tagName: 'best-seller-badge',
  element: './extensions/site/plugins/best-seller-badge/best-seller-badge.tsx',
  settings: './extensions/site/plugins/best-seller-badge/best-seller-badge.panel.tsx',
});
```

## Dashboard Page for Plugin Management

For plugins that require back-office management (especially checkout and side cart plugins that may not support auto-add), create a dashboard page.

> **Note:** The `placement` option in `addSitePlugin()` is optional. If omitted, the plugin is placed in the first available slot based on the priority order configured in the plugin's installation settings in your app's dashboard.

```typescript
// src/extensions/dashboard/pages/plugin-settings/page.tsx
import { dashboard } from "@wix/dashboard";
import { Page, WixDesignSystemProvider, Card, FormField, Input, Button } from "@wix/design-system";

export default function PluginSettingsPage() {
  const handleAddToSlot = async () => {
    const pluginId = "your-plugin-id";
    const pluginPlacement = {
      appDefinitionId: "host-app-definition-id",
      widgetId: "host-widget-id",
      slotId: "target-slot-id",
    };

    await dashboard.addSitePlugin(pluginId, {
      placement: pluginPlacement,
    });
    dashboard.showToast({ message: "Plugin added!", type: "success" });
  };

  return (
    <WixDesignSystemProvider>
      <Page>
        <Page.Header title="Plugin Settings" />
        <Page.Content>
          <Card>
            <Card.Header title="Manage Your Plugin" />
            <Card.Content>
              <Button onClick={handleAddToSlot}>Add Plugin to Slot</Button>
            </Card.Content>
          </Card>
        </Page.Content>
      </Page>
    </WixDesignSystemProvider>
  );
}
```

## Wix Data API Integration

When using Wix Data API in plugins, handle the Wix Editor environment:

```typescript
import { items } from "@wix/data";
import { window as wixWindow } from "@wix/site-window";

class DataPlugin extends HTMLElement {
  static get observedAttributes() {
    return ['collection-id'];
  }

  constructor() {
    super();
  }

  connectedCallback() {
    this.render();
    this.loadData();
  }

  attributeChangedCallback() {
    this.loadData();
  }

  render() {
    this.innerHTML = `
      <div style="padding: 16px; border: 1px solid #ccc; border-radius: 8px;">
        <p>Loading...</p>
      </div>
    `;
  }

  async loadData() {
    const collectionId = this.getAttribute('collection-id');
    if (!collectionId) return;

    try {
      const viewMode = await wixWindow.viewMode();

      if (viewMode === 'Editor') {
        this.innerHTML = `
          <div style="padding: 20px; border: 2px dashed #ccc;">
            <p>Plugin will display data on the live site</p>
            <p>Collection: ${collectionId}</p>
          </div>
        `;
        return;
      }

      const results = await items.query(collectionId).limit(10).find();
      this.innerHTML = `
        <div style="padding: 16px;">
          ${results.items.map(item => `<div>${item.title}</div>`).join('')}
        </div>
      `;
    } catch (error) {
      console.error('Failed to load data:', error);
      this.innerHTML = `<div style="color: red;">Error loading data</div>`;
    }
  }
}

export default DataPlugin;
```

## Example Use Cases

### Booking Confirmation Message Plugin

**Request:** "Create a plugin for booking pages that shows a custom confirmation message"

**Output:**

- Plugin with configurable title, message, and styling
- Settings panel with text inputs and color pickers
- Responsive layout that fits the booking page slot

### Product Reviews Summary Plugin

**Request:** "Create a plugin that displays a reviews summary on product pages"

**Output:**

- Plugin showing star rating and review count
- Configurable display options (show count, show average)
- Settings panel for styling customization
- Integration with slot on product page
- Include placements for both old and new Wix Stores product page versions
