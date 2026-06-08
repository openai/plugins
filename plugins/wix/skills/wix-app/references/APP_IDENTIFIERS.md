# App Identifiers

How to obtain required app identifiers from Wix Dev Center.

## App Namespace

Required when creating **Data Collections**. Scopes collection IDs to prevent conflicts between apps.

### First, check if you already have an app namespace:
1. Go to [Wix Dev Center](https://manage.wix.com/studio/custom-apps/)
2. Open your app dashboard
3. Click the three dots (...) menu button in the top-right corner (next to "Test App" button)
4. Select "View ID & keys" from the dropdown menu
5. In the modal that opens, scroll to the bottom to find the "Namespace" field
6. If you see a Namespace value, copy it

### If there is no app namespace, create one:
1. Go to [Wix Dev Center](https://manage.wix.com/studio/custom-apps/)
2. Select your app
3. In the left menu, select **Develop > Extensions**
4. Click **+ Create Extension** and find the **Data Collections** extension
5. Click **+ Create**
6. You will be prompted to create an app namespace - follow the prompts to set it up

## Code Identifier

Required when creating **Editor React components**. Used as the type prefix for Editor React component extensions (e.g. `type: '<CODE_IDENTIFIER>.ComponentName'`). Every Wix app has one automatically — there is no need to create it.

### How to get the Code Identifier:
1. Go to [Wix Dev Center](https://manage.wix.com/studio/custom-apps/)
2. Open your app dashboard
3. Click the three dots (...) menu button in the top-right corner (next to "Test App" button)
4. Select "View ID & keys" from the dropdown menu
5. In the modal that opens, find the "Code Identifier" field
6. Copy the Code Identifier value
