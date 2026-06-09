# Catalyst Mobile SDKs Reference (Android, iOS, Flutter)

---

## Android SDK (Kotlin) v3

> **Docs:** https://docs.catalyst.zoho.com/en/sdk/android/

### Setup

**Gradle (project-level):**

```groovy
allprojects {
    repositories {
        maven { url "https://maven.zohodl.com" }
    }
}
```

**Gradle (app-level):**

```groovy
dependencies {
    implementation 'com.zoho.catalyst:catalyst-android-sdk:3.+'
}
```

**AndroidManifest.xml permissions:**

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

**strings.xml — URL scheme:**

```xml
<string name="url_scheme">zc-YOUR_PROJECT_ID</string>
```

**Config file:** Place the downloaded `AppConfigurationData.plist` (or the JSON config file) in `app/src/main/assets/`.

### Init

```kotlin
ZCatalystApp.init(context, ZCatalystEnvironment.DEVELOPMENT)
// For production:
// ZCatalystApp.init(context, ZCatalystEnvironment.PRODUCTION)
```

### Auth

```kotlin
val app = ZCatalystApp.getInstance()

// Sign Up
app.signup(firstName, lastName, email, object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* user registered */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Login
app.login(activity, object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* login success */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Logout
app.logout(object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* logged out */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Get Current User
app.getCurrentUser(object : ZCatalystCallback<ZCatalystUser> {
    override fun onSuccess(user: ZCatalystUser) {
        val email = user.emailId
        val name = user.firstName
    }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Check if user is signed in
val signedIn = app.isUserSignedIn()
```

### Data Store

```kotlin
val dataStore = ZCatalystApp.getInstance().getDataStoreInstance()

// Create rows
val row = ZCatalystRow()
row.setColumnValue("Name", "Alice")
row.setColumnValue("Age", 30)
dataStore.getTableInstance("Users").createRows(listOf(row), object : ZCatalystCallback<List<ZCatalystRow>> {
    override fun onSuccess(rows: List<ZCatalystRow>) { /* created */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Get rows
dataStore.getTableInstance("Users").getRows(object : ZCatalystCallback<List<ZCatalystRow>> {
    override fun onSuccess(rows: List<ZCatalystRow>) {
        for (row in rows) {
            val name = row.getColumnValue("Name")
        }
    }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Update rows
row.setColumnValue("ROWID", "12345")
row.setColumnValue("Age", 31)
dataStore.getTableInstance("Users").updateRows(listOf(row), object : ZCatalystCallback<List<ZCatalystRow>> {
    override fun onSuccess(rows: List<ZCatalystRow>) { /* updated */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Delete a row
dataStore.getTableInstance("Users").deleteRow("12345", object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* deleted */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})
```

### ZCQL

```kotlin
val zcql = ZCatalystApp.getInstance().getZCQLInstance()
zcql.executeQuery("SELECT * FROM Users WHERE Age > 25", object : ZCatalystCallback<List<Map<String, Any>>> {
    override fun onSuccess(rows: List<Map<String, Any>>) { /* process results */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})
```

### File Store

```kotlin
val fileStore = ZCatalystApp.getInstance().getFileStoreInstance()

// Get folders
fileStore.getFolders(object : ZCatalystCallback<List<ZCatalystFolder>> {
    override fun onSuccess(folders: List<ZCatalystFolder>) { /* list folders */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Upload file
val folder = fileStore.getFolderInstance("folderId")
folder.uploadFile(file, object : ZCatalystCallback<ZCatalystFile> {
    override fun onSuccess(uploadedFile: ZCatalystFile) { /* uploaded */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Download file
folder.downloadFile("fileId", object : ZCatalystCallback<InputStream> {
    override fun onSuccess(stream: InputStream) { /* read stream */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

// Delete file
folder.deleteFile("fileId", object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* deleted */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})
```

### Search

```kotlin
val search = ZCatalystApp.getInstance().getSearchInstance()
search.executeSearchQuery("search term", object : ZCatalystCallback<List<ZCatalystSearchResult>> {
    override fun onSuccess(results: List<ZCatalystSearchResult>) { /* process results */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})
```

### Push Notifications

```kotlin
val push = ZCatalystApp.getInstance().getPushNotificationInstance()
push.registerToken(fcmToken, object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* registered */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})
```

### Stratus

```kotlin
val stratus = ZCatalystApp.getInstance().getStratusInstance()
val bucket = stratus.bucket("bucket-name")

bucket.getObject("path/to/file.txt", object : ZCatalystCallback<ZCatalystStratusObject> {
    override fun onSuccess(obj: ZCatalystStratusObject) { /* use object */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

bucket.putObject("path/to/file.txt", file, object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* uploaded */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})

bucket.deleteObject("path/to/file.txt", object : ZCatalystCallback<Void> {
    override fun onSuccess(result: Void?) { /* deleted */ }
    override fun onFailure(exception: ZCatalystException) { /* handle error */ }
})
```

---

## iOS SDK (Swift) v2

> **Docs:** https://docs.catalyst.zoho.com/en/sdk/ios/

### Setup

**CocoaPods (Podfile):**

```ruby
pod 'ZCatalyst', :git => 'https://github.com/nicetomeetyou/ZCatalyst.git', :tag => '2.2.2'
```

Run `pod install` after adding.

**Config plist:** Place the downloaded `AppConfigurationData.plist` in your project bundle.

**Info.plist — URL scheme:**

```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>zc-YOUR_PROJECT_ID</string>
        </array>
    </dict>
</array>
```

### Init

```swift
import ZCatalyst

// In AppDelegate application(_:didFinishLaunchingWithOptions:)
ZCatalystApp.shared.initSDK()
```

### Handle Login Redirection

**AppDelegate:**

```swift
func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
    return ZCatalystApp.shared.handleLoginRedirection(for: url)
}
```

**SceneDelegate (iOS 13+):**

```swift
func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
    if let url = URLContexts.first?.url {
        ZCatalystApp.shared.handleLoginRedirection(for: url)
    }
}
```

### Auth

```swift
// Sign Up
ZCatalystApp.shared.signup(firstName: "Alice", lastName: "Smith", email: "alice@example.com") { result in
    switch result {
    case .success:
        print("Signup successful")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Login
ZCatalystApp.shared.login(presentingViewController: self) { result in
    switch result {
    case .success:
        print("Login successful")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Logout
ZCatalystApp.shared.logout { result in
    switch result {
    case .success:
        print("Logged out")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Get Current User
ZCatalystApp.shared.getCurrentUser { result in
    switch result {
    case .success(let user):
        print(user.emailId)
        print(user.firstName)
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Check if signed in
let signedIn = ZCatalystApp.shared.isUserSignedIn()
```

### Data Store

```swift
let dataStore = ZCatalystApp.shared.getDataStoreInstance()
let table = dataStore.getTableInstance(name: "Users")

// Get rows
table.getRows { result in
    switch result {
    case .success(let rows):
        for row in rows {
            let name = row.getValue(forColumn: "Name")
        }
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Create a row
var row = ZCatalystRow()
row.setColumnValue("Name", forColumn: "Name")
row.setColumnValue(30, forColumn: "Age")
table.createRow(row) { result in
    switch result {
    case .success(let createdRow):
        print("Created: \(createdRow)")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Update a row
row.setColumnValue("ROWID", forColumn: "12345")
row.setColumnValue(31, forColumn: "Age")
table.updateRow(row) { result in
    switch result {
    case .success(let updatedRow):
        print("Updated")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Delete a row
table.deleteRow(id: "12345") { result in
    switch result {
    case .success:
        print("Deleted")
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### ZCQL

```swift
let zcql = ZCatalystApp.shared.getZCQLInstance()
zcql.executeQuery("SELECT * FROM Users WHERE Age > 25") { result in
    switch result {
    case .success(let rows):
        for row in rows {
            print(row)
        }
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### File Store

```swift
let fileStore = ZCatalystApp.shared.getFileStoreInstance()

// Get folders
fileStore.getFolders { result in
    switch result {
    case .success(let folders):
        print(folders)
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Upload file
let folder = fileStore.getFolderInstance(id: "folderId")
folder.uploadFile(name: "photo.jpg", data: imageData) { result in
    switch result {
    case .success(let file):
        print("Uploaded: \(file.id)")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Download file
folder.downloadFile(id: "fileId") { result in
    switch result {
    case .success(let data):
        print("Downloaded \(data.count) bytes")
    case .failure(let error):
        print("Error: \(error)")
    }
}

// Delete file
folder.deleteFile(id: "fileId") { result in
    switch result {
    case .success:
        print("Deleted")
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### Stratus

```swift
let stratus = ZCatalystApp.shared.getStratusInstance()
let bucket = stratus.bucket("bucket-name")

bucket.getObject(path: "path/to/file.txt") { result in
    switch result {
    case .success(let obj):
        print("Object: \(obj)")
    case .failure(let error):
        print("Error: \(error)")
    }
}

bucket.putObject(path: "path/to/file.txt", data: fileData) { result in
    switch result {
    case .success:
        print("Uploaded")
    case .failure(let error):
        print("Error: \(error)")
    }
}

bucket.deleteObject(path: "path/to/file.txt") { result in
    switch result {
    case .success:
        print("Deleted")
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### Push Notifications

```swift
let push = ZCatalystApp.shared.getPushNotificationInstance()
push.registerToken(fcmToken: token) { result in
    switch result {
    case .success:
        print("Registered")
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

### Search

```swift
let search = ZCatalystApp.shared.getSearchInstance()
search.executeSearchQuery("search term") { result in
    switch result {
    case .success(let results):
        print(results)
    case .failure(let error):
        print("Error: \(error)")
    }
}
```

---

## Flutter SDK (Dart) v2

> **Docs:** https://docs.catalyst.zoho.com/en/sdk/flutter/

### Setup

**pubspec.yaml:**

```yaml
dependencies:
  zcatalyst_sdk: ^2.2.1
```

Run `flutter pub get`.

**Platform config:** Place the Catalyst config file in platform-specific locations:
- **Android:** `android/app/src/main/assets/`
- **iOS:** Add to Xcode project bundle

Set up URL schemes for each platform as described in the Android and iOS sections above.

### Init

```dart
import 'package:zcatalyst_sdk/zcatalyst_sdk.dart';

// Using config file (default)
await ZCatalystApp.init();

// Using custom SDKConfigs
await ZCatalystApp.init(
  config: SDKConfigs(
    projectId: "YOUR_PROJECT_ID",
    environment: Environment.development,
  ),
);
```

### Auth

```dart
final app = ZCatalystApp.getInstance();

// Sign Up (using Dart record pattern)
final (success, error) = await app.signup(
  firstName: "Alice",
  lastName: "Smith",
  email: "alice@example.com",
);
if (success) {
  print("Signup successful");
} else {
  print("Error: $error");
}

// Login
await app.login();

// Logout
await app.logout();

// Check if logged in
final isLoggedIn = await app.isUserLoggedIn();

// Get Current User
final user = await app.getCurrentUser();
print(user.emailId);
print(user.firstName);

// Handle Custom Login (for custom auth flows)
await app.handleCustomLogin(token: jwtToken);
```

### Data Store

```dart
final dataStore = ZCatalystApp.getInstance().getDataStoreInstance();
final table = dataStore.getTableInstance("Users");

// Get a single row
final row = await table.getRow("12345");

// Get all rows
final rows = await table.getRows();

// Create a single row
final newRow = await table.createRow({
  "Name": "Alice",
  "Age": 30,
});

// Create multiple rows
final newRows = await table.createRows([
  {"Name": "Alice", "Age": 30},
  {"Name": "Bob", "Age": 25},
]);

// Update a row
final updatedRow = await table.updateRow({
  "ROWID": "12345",
  "Age": 31,
});

// Delete a row
await table.deleteRow("12345");
```

### ZCQL Query Builder

The Flutter SDK provides a type-safe query builder:

```dart
final zcql = ZCatalystApp.getInstance().getZCQLInstance();

// Simple query
final results = await zcql.executeQuery("SELECT * FROM Users");

// Query Builder
final query = ZCatalystQueryBuilder()
    .select(["Name", "Age", "Email"])
    .from("Users")
    .where("Age", ">", 25)
    .and("Name", "LIKE", "%Alice%")
    .or("Email", "IS NOT NULL", null)
    .groupBy(["Age"])
    .orderBy("Name", ascending: true)
    .limit(50)
    .build();

final results = await zcql.executeQuery(query);

// Join queries
final joinQuery = ZCatalystQueryBuilder()
    .select(["Users.Name", "Orders.Total"])
    .from("Users")
    .innerJoin("Orders", "Users.ROWID", "Orders.UserId")
    .build();

final leftJoinQuery = ZCatalystQueryBuilder()
    .select(["Users.Name", "Orders.Total"])
    .from("Users")
    .leftJoin("Orders", "Users.ROWID", "Orders.UserId")
    .where("Orders.Total", ">", 100)
    .build();
```

### File Store

```dart
final fileStore = ZCatalystApp.getInstance().getFileStoreInstance();

// Get folders
final folders = await fileStore.getFolders();

// Upload file
final folder = fileStore.getFolderInstance("folderId");
final uploadedFile = await folder.uploadFile(file);

// Download with progress
await folder.downloadFile(
  "fileId",
  savePath: "/path/to/save/file.txt",
  onProgress: (received, total) {
    print("Progress: ${(received / total * 100).toStringAsFixed(0)}%");
  },
);

// Delete file
await folder.deleteFile("fileId");
```

### Stratus

```dart
final stratus = ZCatalystApp.getInstance().getStratusInstance();
final bucket = stratus.bucket("bucket-name");

// Get object metadata
final obj = await bucket.getObject("path/to/file.txt");

// Get objects (paginated)
final objects = await bucket.getObjects(
  prefix: "path/to/",
  maxKeys: 100,
  continuationToken: null,
);

// Download with progress
await bucket.downloadObject(
  "path/to/file.txt",
  savePath: "/local/path/file.txt",
  onProgress: (received, total) {
    print("Progress: ${(received / total * 100).toStringAsFixed(0)}%");
  },
);

// Upload object
await bucket.uploadObject("path/to/file.txt", file);

// Delete objects (batch)
await bucket.deleteObjects(["path/to/file1.txt", "path/to/file2.txt"]);

// Delete by path prefix
await bucket.deletePath("path/to/folder/");
```

### Search

```dart
final search = ZCatalystApp.getInstance().getSearchInstance();
final results = await search.executeSearchQuery("search term");
```

### Push Notifications

```dart
final push = ZCatalystApp.getInstance().getPushNotificationInstance();
await push.registerToken(fcmToken);
```

### Functions

```dart
final functions = ZCatalystApp.getInstance().getFunctionsInstance();

// GET request
final getResult = await functions.executeGET("functionName", queryParams: {"key": "value"});

// POST request
final postResult = await functions.executePOST("functionName", body: {"key": "value"});

// PUT request
final putResult = await functions.executePUT("functionName", body: {"key": "value"});

// DELETE request
final deleteResult = await functions.executeDELETE("functionName", queryParams: {"id": "123"});
```

### Error Handling

All SDK operations can throw `ZCatalystException`:

```dart
try {
  final rows = await table.getRows();
} on ZCatalystException catch (e) {
  print("Error code: ${e.code}");
  print("Error message: ${e.message}");
  print("HTTP status: ${e.httpStatusCode}");
}
```
