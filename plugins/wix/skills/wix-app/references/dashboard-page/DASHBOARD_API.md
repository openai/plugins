# Dashboard API Reference

Complete reference for the `@wix/dashboard` host module.

## navigate()

Host Module '@wix/dashboard' 'navigate()' method for navigating between dashboard pages.

**Method parameters:**
- `destination`: Destination
- `options?`: NavigationOptions

**Destination object:**
- `pageId` (string): ID of the page to navigate to
- `relativeUrl` (string): Optional. URL segment appended to the base page URL. Can include path segments, query string, and fragment.

**Navigation options:**
- `displayMode` ("main" | "overlay" | "auto"): How to display the destination page. "auto" (default) loads in current context.
- `history` ("push" | "replace"): Optional. Whether to push a new history entry or replace the current one.

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';
// Navigate to your own app's page with some internal state
dashboard.navigate({pageId: <your-page-id>, relativeUrl: "/an/internal/state?param=value"})
// Navigate to a relative route of the current page
dashboard.navigate({ relativeUrl: "/some/internal/route" });
// Navigate to the Products List page
dashboard.navigate({ pageId: "0845ada2-467f-4cab-ba40-2f07c812343d" });
// Add a button that navigates to the Products List page (React/TSX)
const GoToProductsButton = () => (
  <button onClick={() => dashboard.navigate({ pageId: "0845ada2-467f-4cab-ba40-2f07c812343d" })}>
    Go to Products
  </button>
);
// Open bookings settings page in an overlay page
dashboard.navigate(
  { pageId: "bcdb42a8-2423-4101-add6-cbebc1951bc2" },
  { displayMode: "overlay" },
);
// Navigate to the home page as a main page from inside an overlay page
dashboard.navigate(
  { pageId: "2e96bad1-df32-47b6-942f-e3ecabd74e57" },
  { displayMode: "main" },
);
```

## Page IDs

Common Wix dashboard page IDs useful for navigation. Use with `dashboard.navigate({ pageId })`.

**Selection policy:**
- When asked to navigate by page name, choose the closest match from the list below.
- Prefer exact match; otherwise use common aliases/synonyms.
- Do not default to "Home" unless the user asks for home or no reasonable match exists.
- If multiple names share the same ID, treat them as aliases.

**ID formats:**
- Most IDs are GUIDs. Some are slugs (e.g., "wix-restaurants-orders-new", "restaurants_orders"). Use them as-is.

**Aliases/synonyms (non-exhaustive):**
- Products List: product list, products page, catalog, product catalog, inventory products
- Automatic Discounts ↔ Coupons

**Page IDs:**
- Abandoned Carts: bb407b4d-6df5-4607-81df-6cd9ecf5d229
- Activity: dfad075a-1ab3-458c-a77b-8fc9f509eaca
- Accept Payments Page: abe22932-49cb-43e0-b22d-8e342482113e
- Automatic Discounts: ed0163bf-ddeb-4dbe-8042-648b44bcbaac
- Automations: 67028126-3a56-43dd-9ed2-0c9c875e739c
- Back in Stock Requests: 74ff0096-6e7f-4d40-9f72-e85a2a7d5726
- Behavior Overview: d53c7001-5056-48d3-81e8-5320f9ef08e4
- Bookings Settings: bcdb42a8-2423-4101-add6-cbebc1951bc2
- Blog Overview: a7f877e0-69ac-459f-8b5b-eb7c5e25bad2
- Blog Writers: b8c96d90-95d6-57de-9a97-0d44c4dfaa96
- Business Cards: 44a21d57-98a3-486f-9def-5e5f356363b5
- Business Email Settings: bfd22a01-fc5b-4b53-940d-beaeac065230
- Contacts List: bdd09dca-7cc9-4524-81d7-c9336071b33e
- Contacts Segments: 0f410434-052f-4edb-8a89-ef564e4465e5
- Contacts Workflows: 511fe7f0-d0fe-4acb-84bc-b9887e4c92b7
- Content Manager: 6513755b-2a3b-45b9-8172-99c16e00dfde
- Coupons: ed0163bf-ddeb-4dbe-8042-648b44bcbaac
- Domain Connection: 3aeabb6d-0bc6-4b88-a6ba-3b40096a9c3a
- Email Marketing: 2abbf001-de3d-4b60-a186-28afd3f4c7ac
- Facebook and Instagram Ads: 4ada9d29-ff4d-40b6-802e-97dbd661fd7c
- Find Products to Sell: 958a5f12-e276-4dee-9c05-4aa880f31932
- Forms & Submissions: 8b307095-20c5-48a8-a36e-6c7ad6f11552
- Forum Categories: d6d2f9e8-43a7-4781-8e3c-4da93f91ea45
- Forum Posts: 6ce59b51-95ce-485e-a158-42686d647793
- Forum Settings: b1b1df78-6340-4ef0-b576-5dab0b2602e3
- Gift Card Overview: 99bc7dcb-312d-4462-9ff6-ca764606cfbb
- Gift Card Sales: 8bae1213-e243-4cd5-910b-9c3d4b6c0750
- Google Business Profile: 98b6ed3b-9ac6-486f-a347-0de6f9929965
- Home: 2e96bad1-df32-47b6-942f-e3ecabd74e57
- Import Contacts Page: 135f0c27-4fb9-453d-8479-7f8762227234
- Inbox: 1ae6068f-0fe6-4986-975a-3565f4147fbe
- Integrations: 02bba945-0d2c-4173-838e-cf186d57d9c8
- Inventory: 59a8855e-515a-49c1-894a-035731d2fd44
- Invoices: 237552b5-9d8e-4bdc-a39b-6e70a83caea0
- Language and Region Settings: f1f1abd6-3949-4633-a6dc-74337c70957a
- Logs: 4576d2f4-7da6-4ad1-ad51-418e09847e34
- Loyalty Program: c3ad65e1-0b0f-4da9-a8a3-6025c321da50
- Manage Loyalty Program: 978a178c-a739-46ed-93c3-60afaabd6ca4
- Marketing Home: 6617e07c-c3f3-45eb-9280-b41f23f259dd
- Manage Installed Apps: ad471122-7305-4007-9210-2a764d2e5e57
- Monitoring: e1a20a83-1908-4bae-9214-b9e26e6fda2a
- Music Library: 5da7cc0e-93e2-49cf-b8fa-de46be1af7b7
- My Albums: ef237a91-20b1-4e62-bbd7-31e28bda04a0
- Notification You Get - settings: e96a4137-cf9d-42ba-96c2-b583fce6f00b
- Notifications You Send - settings: e6576ec0-802c-4816-a84e-a206a10e7b3d
- New Order Form: a0278851-325c-4115-9bf1-08848468ad45
- Orders List: 8107f05f-d646-4c81-be90-adf28d321398
- Payments Dashboard: efe44d1d-506c-46c7-a770-e212b697acf0
- Price Quotes: 9f45b934-56a1-4036-96eb-4f6e2ff15c73
- Pricing Plans: e7b7afbb-6d4e-46b2-8bd6-0af78dc9d21e
- Products List: 0845ada2-467f-4cab-ba40-2f07c812343d
- Programs: ccf2fe64-86c2-44a3-8e97-eed943c49b58
- Recurring Invoices: 5bfd82d5-51e0-4dc0-aab9-9b384bf15f5d
- Restaurants Menus (New): 37c3de13-6224-42ee-bd80-308d452a2c7d
- Restaurants Menus: b278a256-2757-4f19-9313-c05c783bec92
- Restaurant Orders (New): wix-restaurants-orders-new
- Orders: 2c7daf4b-dbe7-4e00-9ffd-9b44b1884507
- Restaurant Orders: restaurants_orders
- Pricing Plans Settings: ce9562b2-f279-4c45-bee8-af3870d27069
- Roles And Permissions: ca4fc2e2-e8fc-4b4c-bfa0-32479931a00a
- Sales Overview: 98052ea0-bfe4-4095-88ba-d5c65c03254b
- Secrets Manager: f94ac43e-52c4-4564-b1da-68df51b9e614
- Settings Page: 50103805-f706-428a-ab43-04579324d067
- SEO - Get Found on Google: baf8b254-72c1-417b-a546-ecc9d869aa71
- SEO Overview: 721868b6-1d4d-4a40-a876-786f6cbfffcc
- Shipping and Delivery Settings: 26128445-061b-4dfc-bc44-fd53b13dd687
- Site Alerts: cabc24b1-fb28-445f-b38f-4db49aa26a58
- Site History: 122ec73e-4e5d-4c3a-ad62-3f62bdb31e0f
- Site Groups: 04c7e480-f1ad-4742-81f6-ac0edfd8a350
- Site Insights: 7f57c576-7911-46cf-abee-cd8905e59a21
- Site Reports: 66aeefcd-3e60-4b41-8991-934c5ee331ec
- Site Members: c696eca6-7489-40ae-8c41-815cea571b53
- Social Media Marketing: 36f17da6-ba4a-4657-af44-a45196771850
- Staff Management: a4f36fac-ea18-483b-8236-095e29fcb726
- New Staff Member Page: 3e6d608b-bbc2-4e72-a1ef-4d441bb113ad
- Subscriptions: 79dbb935-d823-4feb-9272-ef2cbcf2aafd
- Table Reservations: e4d65aa4-30ba-4700-ad47-28765d4cf3bc
- Tasks & Reminders: e1d6190c-bb9b-41b8-aa67-6024d19442e1
- Tax Settings: 7f43cf15-e14a-48f7-a7fa-9d0d1b1a6f02
- Triggered Emails: 9b111e6f-76c4-48e9-89cb-99e804ce6d31
- New Triggered Email form: bf982c96-9bb7-49e1-8116-be03aa1fc0d5
- Video Library: a9e63e77-29c6-4822-8687-51fa4bdd2279
- Website Settings: 29570214-f230-4228-9209-f09efb53f768
- Wix App Market: e839f784-0e31-45e6-8de8-426824a6dc2d

## observeState()

Host Module '@wix/dashboard' 'observeState()' method to receive contextual state and environmental information for dashboard pages, widgets, and modals. The observer runs on initialization and whenever the state is updated.

**Method parameters:**
- `observer`: Observer — callback receiving (componentParams, environmentState)

**Observer:**
- `componentParams`: P | PageParams — Data sent to your component by its host. For dashboard pages rendered by the platform, this is PageParams
- `environmentState`: EnvironmentState — Information about the user's environment

**Page params:**
- `location`: PageLocation — Information about the location of the rendered page

**Environment state:**
- `locale` (string): User's locale (ISO 639-1)
- `pageLocation` (PageLocation): Deprecated. Information about the currently rendered page location

**Page location:**
- `pageId` (string): ID of the current page
- `pathname` (string): Any parts of the current URL path appended to the page's base URL path
- `search` (string, optional): Current URL query string
- `hash` (string, optional): Current URL fragment identifier

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Receive state passed by your host
dashboard.observeState((componentParams, environmentState) => {
  console.log(componentParams, environmentState);
});

// Receive user's locale
dashboard.observeState((_, { locale }) => {
  console.log('locale:', locale);
});

// Handle internal page routes
dashboard.observeState((pageParams, environmentState) => {
  // This value is logged on initialization and whenever either of the componentParams or environmentState objects change.
  const { pathname, search } = pageParams.location;
  if (pathname.startsWith("/list")) {
    const queryParams = new URLSearchParams(search);
    const sortBy = queryParams.get("sortBy");
    console.log("Show items list sorted by", sortBy);
  } else if (pathname.startsWith("/item")) {
    const { itemId } = pathname.match("/item/(?<itemId>.*)").groups;
    console.log("Show item with id", itemId);
  }
  console.log("Unknown route");
});
```

## showToast()

Host Module '@wix/dashboard' 'showToast()' displays a toast notification from a dashboard page or widget. Up to 3 toasts show at once; additional toasts may be queued.

**Method parameters:**
- `config`: ToastConfig — Toast configuration options

**Toast config:**
- `message` (string): Text to display
- `type` ("standard" | "success" | "warning" | "error"): Icon and message type. Default: standard
- `priority` ("low" | "normal" | "high"): Display priority. Default: normal
- `timeout` ("none" | "normal"): Auto-dismiss after ~6s if 'normal'
- `onToastSeen` (() => void, optional): Called when the toast is seen
- `onCloseClick` (() => void, optional): Called when the toast close button is clicked
- `action` (ToastAction, optional): call-to-action displayed in the toast

**Toast action:**
- `text` (string): Text that appears in the call-to-action.
- `uiType` ("button" | "link"): The type of call-to-action
- `onClick` (() => void): Callback function to run after the call-to-action is clicked.
- `removeToastOnClick` (boolean): Whether to remove the toast after click

**Returns:**
An object with a method to remove the toast programmatically
`{ remove: () => void }`

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Display a success toast when a product is updated
dashboard.showToast({
  message: "Product updated successfully!",
  type: "success",
});

// Display an error toast with a 'Learn more' link
dashboard.showToast({
  message: "Product update failed.",
  timeout: "none",
  type: "error",
  priority: "low",
  action: {
    uiType: "link",
    text: "Learn more",
    removeToastOnClick: true,
    onClick: () => {
      // Logic to run when the user clicks the 'Learn more' link.
      console.log("Learn more clicked!");
    },
  },
});

// Remove a displayed toast
const { remove } = dashboard.showToast({
  message: "Product updated successfully!",
  type: "success",
  timeout: "none",
});

// Remove the toast.
remove();
```

## openModal()

Host Module '@wix/dashboard' 'openModal()' opens a dashboard modal extension on your app's dashboard page.

**Notes:**
- Does not work when developing sites or building apps with Blocks.
- Requires a dashboard modal extension to be implemented first.
- Avoid using relative CSS height units (e.g., 'vh') in extensions opened by this method.

**Method parameters:**
- `modalInfo`: ModalInfo — Information about the dashboard modal to open

**Modal info:**
- `modalId` (string): ID of the dashboard modal extension to open
- `params` (Record<string, any>, optional): Custom data to pass into the modal (accessible via observeState in the modal)

**Returns:**
Promise that resolves when the modal is closed.
`{ modalClosed: Promise<Serializable> }`

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Open a modal
await dashboard.openModal({
  modalId: 'your-modal-id',
});

// Pass extra data when opening a modal
await dashboard.openModal({
  modalId: 'your-modal-id',
  params: { firstName: "Name" },
});

// Get notified when the modal is closed (continue after it closes)
const { modalClosed } = dashboard.openModal({
  modalId: "1d52d058-0392-44fa-bd64-ed09275a6fcc",
});
modalClosed.then((result) => {
  if (result) {
    console.log("The modal was closed and returned the value:", result);
  } else {
    console.log("The modal was closed without any data.");
  }
});
```

## navigateBack()

Host Module '@wix/dashboard' 'navigateBack()' navigates the user back to the previous dashboard page (equivalent to the browser back button).

**Signature:**
No parameters.

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Navigate back to the previous page
dashboard.navigateBack();
```

## getPageUrl()

Host Module '@wix/dashboard' 'getPageUrl()' returns the full URL for a dashboard page.

**Method parameters:**
- `destination`: Destination — URL destination details

**Destination object:**
- `pageId` (string): ID of the page to link to
- `relativeUrl` (string, optional): URL segment appended to the base page URL. Can include path segments, query string, and fragment

**Returns:**
The full URL (string) of the dashboard page with the provided relativeUrl appended.
`Promise<string>`

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Get the URL of the dashboard's home page with a query string
const pageUrl = await dashboard.getPageUrl({
  pageId: "0845ada2-467f-4cab-ba40-2f07c812343d",
  relativeUrl: "?referral=widget",
});
```

## openMediaManager()

Host Module '@wix/dashboard' 'openMediaManager()' opens the Wix Media Manager in a modal to let users pick media files. Developer Preview.

**Method parameters:**
- `options?`: Options — Optional Media Manager options

**Options:**
- `category` (string, optional): Media type to display. Supported: "IMAGE", "VIDEO", "MUSIC", "DOCUMENT", "VECTOR_ART", "3D_IMAGE". Default: all except "3D_IMAGE"
- `multiSelect` (boolean, optional): Whether multiple files can be selected. Default: false

**Returns:**
A promise that resolves to an object with a single key called items. The value of that key is an array of file descriptor objects for the selected media files.
`Promise<{ items: Array<FileDescriptor> }>`

**File descriptor:**
FileDescriptor is the full schema describing a Media Manager file, including IDs, timestamps, media-type, URLs, status, labels, and a media-specific payload.

**Typical fields:**
- `_id` (string): File GUID
- `_createdDate` (Date): Creation time
- `_updatedDate` (Date): Last update time
- `displayName` (string): File name as shown in Media Manager
- `mediaType` (ARCHIVE | AUDIO | DOCUMENT | IMAGE | MODEL3D | OTHER | UNKNOWN | VECTOR | VIDEO): Media file type
- `url` (string): Static URL of the file
- `thumbnailUrl` (string): Thumbnail URL
- `sizeInBytes` (string): File size in bytes
- `parentFolderId` (string): ID of the file's parent folder.
- `siteId` (string): Site GUID where the media is stored
- `private` (boolean): Whether file is private
- `operationStatus` (FAILED | READY | PENDING): Upload/processing status
- `state` (DELETED | OK): File state
- `hash` (string): File hash
- `labels` (string[]): User/AI labels
- `sourceUrl` (string): URL where the file was uploaded from.
- `media` (object): One of the following variants with specific fields
  - archive: { _id: string; filename: string; sizeInBytes: string; url: string; urlExpirationDate: Date }
  - audio: { _id: string; assets: string[]; bitrate: number; duration: number; format: string; sizeInBytes: string }
  - document: string
  - image: { caption: string; colors: { palette: Array<{ hex: string; rgb: { r: number; g: number; b: number } }>; prominent: { hex: string; rgb: { r: number; g: number; b: number } }; }; faces: Array<{ confidence: number; height: number; width: number; x: number; y: number }>; image: string; previewImage: string; }
  - model3d: { _id: string; altText: string; filename: string; sizeInBytes: string; thumbnail: string; url: string; urlExpirationDate: Date }
  - vector: { caption: string; colors: { palette: Array<{ hex: string; rgb: { r: number; g: number; b: number } }>; prominent: { hex: string; rgb: { r: number; g: number; b: number } }; }; faces: Array<{ confidence: number; height: number; width: number; x: number; y: number }>; image: string; previewImage: string; }
  - video: string

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Open a media manager modal allowing multiple image selection
const chosenMediaItems = await dashboard.openMediaManager({
  multiSelect: true,
});
console.log("You have chosen: ", chosenMediaItems.items);
```

## onBeforeUnload()

Host Module '@wix/dashboard' 'onBeforeUnload()' registers a beforeunload handler for a dashboard page, modal, or plugin extension. The callback runs when the user is about to navigate away or the browsing context is unloading. Calling event.preventDefault() pauses navigation and shows a warning dialog about unsaved data.

**Signature:**
`onBeforeUnload(callback: (event: { preventDefault: () => void }) => void): { remove: () => void }`

**Method parameters:**
- `callback`: (event: { preventDefault: () => void }) => void — Called when the beforeunload event fires

**Notes:**
- Do not assume the beforeunload event will always fire or that a confirmation dialog will always appear; behavior varies by browser.

**Returns:**
An object with a remove() method to unregister the handler
`{ remove: () => void }`

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Prompt for confirmation before unloading unsaved data
const { remove } = dashboard.onBeforeUnload((event) => {
  // Check if there's unsaved data on the page
  if (unsavedPageData) {
    event.preventDefault();
  }
});
```

## addSitePlugin()

Host Module '@wix/dashboard' 'addSitePlugin()' adds a site plugin to one of the slots supported in an app created by Wix. You can target a specific slot or rely on prioritized slots configured in your app's dashboard.

**Notes:**
- Developer Preview. API is subject to change.
- Requires a site plugin extension to be configured first.

**Method parameters:**
- `pluginId`: string — ID of your site plugin (from the extension's settings in your app's dashboard)
- `options`: addSitePluginOptions — Options for adding the site plugin

**Add site plugin options:**
- `placement?`: PluginPlacement — Details of the slot to add the plugin to. If omitted, the plugin is added to the first available slot based on your installation settings. If all prioritized slots are occupied, it won't be added

**Plugin placement:**
- `appDefinitionId`: string — ID of the Wix app hosting the widget and slot (see list of apps created by Wix)
- `widgetId`: string — ID of the host widget in which the slot exists
- `slotId`: string — ID of the slot in the host widget

**Returns:**
Resolves on success. See Errors for possible rejection reasons
`Promise<void>`

**Errors:**
- 3001: Slot occupied
- 3002: Slot not found
- 3003: Error adding plugin
- 3004: Error replacing existing plugin
- 3005: Error loading modal data
- 3006: Aborted by user
- 3007: Site not published yet

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Add a site plugin to a specific slot
const pluginId = "975bffb7-3c04-42cc-9840-3d48c24e73d5";
const pluginPlacement = {
  appDefinitionId: "13d21c63-b5ec-5912-8397-c3a5ddb27a97",
  widgetId: "a91a0543-d4bd-4e6b-b315-9410aa27bcde",
  slotId: "slot1",
};

dashboard
  .addSitePlugin(pluginId, { placement: pluginPlacement })
  .then(() => {
    console.log("Plugin added successfully");
  })
  .catch((error) => {
    console.error("Error adding plugin:", error);
  });

// Add a site plugin without specifying a slot (uses prioritized slots)
const pluginId = "975bffb7-3c04-42cc-9840-3d48c24e73d5";

dashboard
  .addSitePlugin(pluginId, {})
  .then(() => {
    console.log("Plugin added successfully");
  })
  .catch((error) => {
    console.error("Error adding plugin:", error);
  });
```

## setPageTitle()

Host Module '@wix/dashboard' 'setPageTitle()' sets the title of the current dashboard page in the browser tab. This can only be called from dashboard pages (not plugin extensions). Pass null to reset the title to the default dashboard page title.

**Method parameters:**
- `pageTitle`: string | null — Title to set (or null to reset)

**Returns:**
void

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Set a static page title
dashboard.setPageTitle('Orders Overview');

// Reset to default dashboard page title
dashboard.observeState((_, environmentState) => {
  // Use a regular expression to capture the productId value.
  const queryParams = environmentState.pageLocation.search;
  const productIdMatch = queryParams.match(/[?&]productId=([^&]+)/);
  let productId;
  if (productIdMatch) {
    productId = productIdMatch[1];
  }

  // If a product ID was found, set the page title to the ID.
  if (productId) {
    dashboard.setPageTitle("Product: " + productId);
    // If no product ID was found, reset the page title to default.
  } else {
    dashboard.setPageTitle(null);
  }
});
```

## onLayerStateChange()

Host Module '@wix/dashboard' 'onLayerStateChange()' registers a handler fired when a page, modal, or plugin extension moves between foreground and background. Use it to refresh data when coming to foreground and pause resource-intensive work when backgrounded.

**Method parameters:**
- `callback`: (state: "foreground" | "background") => void — Called whenever the layer state changes

**Returns:**
An object with remove() to unregister the handler
`{ remove: () => void }`

**Example:**
```typescript
import { dashboard } from '@wix/dashboard';

// Refresh/pause depending on visibility
const { remove } = dashboard.onLayerStateChange((state) => {
  if (state === "foreground") {
    refreshData();
  }
});

// Remove the onLayerStateChange handler when the beforeUnload event is triggered.
dashboard.onBeforeUnload(() => {
  remove();
});
```
