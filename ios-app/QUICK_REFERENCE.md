# iOS App - Quick Reference Card

## 🚀 First Time Setup

```bash
cd ios-app
./setup-simctl.sh         # Fix command line tools (requires password)
```

## 🔧 Xcode Configuration (Manual)

### 1. URL Type
Target → Info → URL Types → +
- Identifier: `vaani`
- URL Schemes: `vaani`
- Role: `Editor`

### 2. Privacy Strings (Info tab)
```
NSMicrophoneUsageDescription = "Microphone access is needed for voice input."
NSSiriUsageDescription = "Vaani Banking uses Siri to help with voice commands."
```

### 3. App Transport Security
Fix domain key: `localhost:` → `localhost`

### 4. Deployment Target
Build Settings → iOS Deployment Target = `18.0`

## 🧪 Testing Commands

### Deep Links (simulator must be running)
```bash
# Check balance
xcrun simctl openurl booted "vaani://chat?message=Check%20balance"

# View transactions
xcrun simctl openurl booted "vaani://chat?message=Show%20my%20recent%20transactions"

# Transfer money
xcrun simctl openurl booted "vaani://chat?message=Transfer%20money"
```

### Interactive Menu
```bash
./quick-commands.sh       # Launch interactive testing menu
```

## 📱 App Shortcuts (Siri)

After building the app once, these phrases work:

- "Hey Siri, **check my Vaani Banking balance**"
- "Hey Siri, **transfer money with Vaani Banking**"
- "Hey Siri, **show transactions in Vaani Banking**"

**Note:** Siri testing requires a physical device, not simulator.

## 🐛 Troubleshooting

### simctl not found
```bash
./setup-simctl.sh
```

### Deep links not working
1. Check URL Type is registered in Xcode
2. Verify app is running on simulator
3. Try from Safari first: `vaani://chat?message=Test`

### Shortcuts not appearing
1. Rebuild and run app at least once
2. Check deployment target is iOS 16+
3. Force-quit Shortcuts app and reopen

### Frontend not loading (Local mode)
```bash
cd frontend
npm install
npm run dev              # Should run on http://localhost:5173
```

## 📋 Pre-Flight Checklist

Before submitting/demoing:

- [ ] App builds without errors
- [ ] Deep links work
- [ ] App Shortcuts appear
- [ ] Frontend loads correctly
- [ ] Bridge status shows "Ready"
- [ ] Voice input works (if implemented)
- [ ] Backend API calls succeed

## 🎯 Files to Know

| File | Purpose |
|------|---------|
| `VaaniBankingAppApp.swift` | App entry point, deep link handler |
| `ContentView.swift` | Main UI, WebView container |
| `CheckBalanceIntent.swift` | Siri/Shortcuts intents |
| `WebViewStore.swift` | JavaScript bridge |
| `Info.plist` | Configuration (URL scheme, permissions) |

## 🔗 Useful Commands

```bash
# List simulators
xcrun simctl list devices

# Boot simulator
xcrun simctl boot "iPhone 15 Pro"

# Show running simulators
xcrun simctl list devices | grep Booted

# Open Shortcuts app
xcrun simctl openurl booted "shortcuts://"

# View logs
xcrun simctl spawn booted log stream --predicate 'processImagePath contains "VaaniBankingApp"'

# Clean build
cd VaaniBankingApp
xcodebuild clean -project VaaniBankingApp.xcodeproj -scheme VaaniBankingApp
```

## 📖 Documentation

- **TESTING_GUIDE.md** - Complete testing procedures
- **iOS_SETUP_COMPLETE.md** - Setup checklist & troubleshooting
- **README.md** - Project overview & setup

## ⚡ Quick Tips

- **Debug Overlay:** Long-press top-right corner to show/hide
- **Mode Switching:** Use debug overlay to switch Prod/Local/Bundled
- **Bridge Ready:** Green dot = ready, Orange = waiting
- **Local Dev:** Requires `npm run dev` in frontend folder
- **No Siri Capability Needed:** App Intents work without it

---

**Need help?** Check TESTING_GUIDE.md or iOS_SETUP_COMPLETE.md
