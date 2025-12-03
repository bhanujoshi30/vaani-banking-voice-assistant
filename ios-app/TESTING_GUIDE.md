# iOS App - Vaani Banking Assistant

This folder contains a native iOS application that wraps the React frontend and provides **App Intents** for Siri and Shortcuts integration.

## 🎯 Features

- ✅ **App Intents** - Siri commands like "Hey Siri, check my balance"
- ✅ **Shortcuts Integration** - Create home screen shortcuts
- ✅ **Deep Linking** - Open chat with pre-filled messages via `vaani://` URL scheme
- ✅ **WebView Bridge** - Seamless communication with React frontend
- ✅ **Native iOS Shell** - Better performance and offline support
- ✅ **Debug Overlay** - Switch between Prod/Local/Bundled frontend modes

## 📱 Supported Intents

1. **Check Balance** - "Hey Siri, check my Vaani Banking balance"
2. **Transfer Money** - "Hey Siri, transfer money with Vaani Banking"
3. **View Transactions** - "Hey Siri, show transactions in Vaani Banking"

## 🧪 Quick Start Testing

After building the app, see **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** for:
- Deep link testing commands
- App Shortcuts verification
- Siri testing on device
- Debug overlay usage
- Troubleshooting common issues

**Quick test (after fixing simctl):**
```bash
# One-time setup
./setup-simctl.sh

# Test deep link
xcrun simctl openurl booted "vaani://chat?message=Check%20balance"
```

## 🚀 Setup Instructions

### Prerequisites

- macOS with Xcode 14.0 or later
- iOS 16.0+ device or simulator
- Apple Developer account (for running on physical device and Siri)

### Step 1: Create Xcode Project

1. Open Xcode
2. File → New → Project
3. Choose "iOS" → "App"
4. Fill in:
   - **Product Name**: `VaaniBankingApp`
   - **Team**: Your development team
   - **Organization Identifier**: `com.yourcompany` (or your bundle ID)
   - **Bundle Identifier**: `com.yourcompany.VaaniBankingApp`
   - **Interface**: SwiftUI
   - **Language**: Swift
5. Click "Next" and choose save location

### Step 2: Add Files to Xcode

1. In Xcode, delete the default `ContentView.swift` and `VaaniBankingApp.swift`
2. Right-click on the project navigator → "Add Files to VaaniBankingApp..."
3. Add all files from this `ios-app/VaaniBankingApp` folder:
   - `VaaniBankingApp.swift`
   - `Views/ContentView.swift`
   - `Bridge/WebViewStore.swift`
   - `Intents/CheckBalanceIntent.swift`
   - `Resources/Info.plist`

### Step 3: Configure Project Settings

1. Select your project in the navigator
2. Select your target → **Signing & Capabilities**
3. Enable **Automatic Signing** and select your team
4. Click **+ Capability** and add:
   - **Siri** (required for App Intents)

### Step 4: Configure Info.plist

The provided `Info.plist` already includes:
- ✅ Custom URL scheme (`vaani://`)
- ✅ Siri usage description
- ✅ App Transport Security settings
- ✅ User Activity Types for intents

Make sure to copy this file to replace Xcode's default Info.plist.

### Step 5: Update React App URL

In `Views/ContentView.swift`, line 68, update the URL:

```swift
// OPTION 1: Production URL
if let url = URL(string: "https://your-deployed-app.vercel.app") {
    webView.load(URLRequest(url: url))
}

// OPTION 2: Local development
// if let url = URL(string: "http://localhost:5173") {
//     webView.load(URLRequest(url: url))
// }
```

### Step 6: Build and Run

1. Select a target device (iPhone simulator or physical device)
2. Click the "Play" button or press `Cmd + R`
3. The app should launch and load your React frontend

## 🧪 Testing

### Test Deep Links

1. Run the app on a device/simulator
2. Open Safari and enter: `vaani://chat?message=Check%20balance`
3. Tap "Open" when prompted
4. The app should open and auto-send the message

### Test Siri Integration

**Note:** Siri testing requires a physical device (not simulator)

1. Run app on physical device
2. Go to **Settings** → **Siri & Search** → **VaaniBankingApp**
3. Enable "Use with Ask Siri"
4. You should see suggested shortcuts
5. Say: **"Hey Siri, check my balance"**
6. Siri should open the app and send the message

### Test Shortcuts

1. Open **Shortcuts** app
2. Tap **+** to create new shortcut
3. Add Action → Apps → **VaaniBankingApp** → **Check Balance**
4. Tap **⋯** → "Add to Home Screen"
5. Name it "Check Balance"
6. Tap the home screen icon to test

## 🔧 Customization

### Add More Intents

Edit `Intents/CheckBalanceIntent.swift` and add new intent structs:

```swift
@available(iOS 16.0, *)
struct YourCustomIntent: AppIntent {
    static var title: LocalizedStringResource = "Your Action"
    static var description = IntentDescription("Description")
    static var suggestedInvocationPhrase: LocalizedStringResource = "Your phrase"
    
    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        let url = URL(string: "vaani://chat?message=Your%20message")!
        await UIApplication.shared.open(url)
        return .result(dialog: "Opening...")
    }
}
```

### Customize App Icon

1. Create app icons (1024x1024 PNG)
2. Use https://appicon.co to generate all sizes
3. Drag the `.appiconset` folder into **Assets.xcassets**

### Bundle React App (Offline Support)

For production, bundle the React build inside the app:

1. Build React app:
   ```bash
   cd frontend
   npm run build
   ```

2. Add `dist` folder to Xcode:
   - Right-click project → "Add Files..."
   - Select `frontend/dist` folder
   - Check "Create folder references"

3. Update `ContentView.swift`:
   ```swift
   if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "dist") {
       webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
   }
   ```

## 🐛 Troubleshooting

### "sendAutoMessage is not a function"

- Make sure you've added the JavaScript bridge to your React app (see React Integration below)
- Check browser console for errors
- Try reloading the app

### Siri not working

- Ensure you're testing on a **physical device** (not simulator)
- Check **Settings → Siri & Search → VaaniBankingApp** is enabled
- Make sure **Siri capability** is added in Xcode
- Try deleting the app and reinstalling

### WebView won't load

- Check the URL in `ContentView.swift` is correct
- For localhost, make sure dev server is running
- Check console logs in Xcode for errors
- Verify Info.plist allows the domain (App Transport Security)

### Deep links not working

- Verify URL scheme in Info.plist: `vaani://`
- Check `handleDeepLink` function in `VaaniBankingApp.swift`
- Test with Safari first before Shortcuts/Siri

## 📚 Next Steps

1. **Add Authentication**: Store tokens in Keychain
2. **Push Notifications**: Notify users about transactions
3. **Face ID/Touch ID**: Secure app launch
4. **Offline Mode**: Cache data for offline access
5. **Analytics**: Track usage with Firebase/Amplitude

## 🔗 Related Documentation

- [Apple App Intents Documentation](https://developer.apple.com/documentation/appintents)
- [Shortcuts Integration Guide](https://developer.apple.com/design/human-interface-guidelines/siri)
- [WKWebView Documentation](https://developer.apple.com/documentation/webkit/wkwebview)

## 📝 Notes

- This is a **hybrid approach** - native shell + React web content
- For full native app, you'd build SwiftUI views that call the FastAPI backend directly
- App Store submission requires proper privacy policy and permissions handling
- Test thoroughly on different iOS versions (16.0+)
