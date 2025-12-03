# Quick Start - iOS App with Siri Integration

Follow these steps to get the iOS app running with Siri and Shortcuts support.

## Prerequisites

- ✅ macOS with Xcode 14.0+
- ✅ iOS 16.0+ device (for Siri testing)
- ✅ Apple Developer account (free or paid)

## 🚀 5-Minute Setup

### Step 1: Create Xcode Project (2 min)

1. Open Xcode
2. File → New → Project
3. Choose "iOS" → "App"
4. Fill in:
   - Product Name: `VaaniBankingApp`
   - Team: Select your team
   - Organization Identifier: `com.yourcompany`
   - Bundle Identifier: `com.yourcompany.VaaniBankingApp`
   - Interface: **SwiftUI**
   - Language: **Swift**
5. Click "Next" and save

### Step 2: Add Files (2 min)

1. Delete default `ContentView.swift` and `VaaniBankingApp.swift`
2. Drag all folders from `ios-app/VaaniBankingApp/` into Xcode:
   - ✅ VaaniBankingApp.swift
   - ✅ Views/
   - ✅ Bridge/
   - ✅ Intents/
   - ✅ Resources/Info.plist
3. Select "Copy items if needed"

### Step 3: Configure (1 min)

1. Select project → Target → **Signing & Capabilities**
2. Enable "Automatically manage signing"
3. Select your Team
4. Click **+ Capability** → Add **Siri**
5. Replace Info.plist with the one from Resources/

### Step 4: Update URL

In `Views/ContentView.swift`, line 68, update:

**For Production:**
```swift
if let url = URL(string: "https://vaani-banking-voice-assistant.vercel.app") {
```

**For Local Development:**
```swift
if let url = URL(string: "http://localhost:5173") {
```

### Step 5: Build & Run

1. Select a simulator (iPhone 15 Pro)
2. Press **Cmd + R** (or click Play)
3. App should launch and load React frontend

## ✅ Test It Works

### Test 1: Basic Load
- App opens ✓
- React app loads ✓
- Can login and use chat ✓

### Test 2: Deep Link
1. Open Safari on simulator
2. Navigate to: `vaani://chat?message=Check%20balance`
3. Tap "Open"
4. Message should auto-send ✓

### Test 3: Shortcuts (Physical Device)
1. Build on physical device
2. Open Shortcuts app
3. + → Add Action → Apps → VaaniBankingApp → Check Balance
4. Tap to run
5. App opens and sends message ✓

### Test 4: Siri (Physical Device)
1. Settings → Siri & Search → VaaniBankingApp
2. Enable "Use with Ask Siri"
3. Say: "Hey Siri, check my balance"
4. Siri opens app and shows result ✓

## 🎯 Available Commands

Try these with Siri or Shortcuts:

| Command | Siri Phrase |
|---------|-------------|
| Check Balance | "Hey Siri, check my balance" |
| Transfer Money | "Hey Siri, transfer money" |
| View Transactions | "Hey Siri, show my transactions" |
| Set Reminder | "Hey Siri, set a payment reminder" |

## 📱 Create Home Screen Shortcut

1. Open Shortcuts app
2. Tap **+** to create new
3. Add Action → Apps → VaaniBankingApp → Check Balance
4. Tap **⋯** (three dots)
5. "Add to Home Screen"
6. Name it "💰 Check Balance"
7. Tap shortcut to use instantly

## 🐛 Common Issues

**"App won't load React frontend"**
- Check URL in ContentView.swift
- Verify React dev server is running (for localhost)
- Check console logs in Xcode

**"Siri not working"**
- Must use physical device (not simulator)
- Check Settings → Siri & Search → VaaniBankingApp
- Verify Siri capability is added in Xcode

**"Deep link not working"**
- Verify Info.plist has `vaani://` URL scheme
- Check URL format: `vaani://chat?message=...`
- Test in Safari first

**"sendAutoMessage not defined"**
- React frontend changes not applied
- Check browser console for errors
- Reload the app

## 📚 Next Steps

✅ App is working! Now you can:

1. **Customize intents** - Edit `Intents/CheckBalanceIntent.swift`
2. **Add app icon** - Generate at https://appicon.co
3. **Bundle React build** - For offline support (see README.md)
4. **Add authentication** - Store tokens in Keychain
5. **Submit to App Store** - Follow Apple guidelines

## 📖 Full Documentation

- `README.md` - Complete setup and features
- `INTEGRATION_GUIDE.md` - React integration details
- `ios-app/VaaniBankingApp/` - All source files

## 🆘 Need Help?

Check console logs:
- **Xcode**: View → Debug Area → Activate Console
- **Safari**: Develop → Simulator → Console (for React logs)

Look for these messages:
- ✅ `📱 Native iOS bridge detected`
- ✅ `✅ React app signaled ready`
- ✅ `📱 Received message from iOS`

---

**That's it! You now have a Siri-enabled banking app! 🎉**
