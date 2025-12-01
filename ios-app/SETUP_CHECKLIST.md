# iOS App Setup Checklist

Use this checklist to track your progress setting up the iOS app.

## ✅ Prerequisites

- [ ] Mac with macOS 12.0+ (Monterey or later)
- [ ] Xcode 14.0+ installed (download from Mac App Store)
- [ ] Apple Developer account (free or paid)
- [ ] iOS device with iOS 16.0+ (for Siri testing)
- [ ] USB cable for connecting device to Mac

## 📱 Xcode Project Setup

- [ ] Open Xcode
- [ ] Create new iOS App project
  - [ ] Product Name: `VaaniBankingApp`
  - [ ] Team: Selected
  - [ ] Organization Identifier: Set (e.g., `com.yourcompany`)
  - [ ] Interface: SwiftUI
  - [ ] Language: Swift
- [ ] Delete default `ContentView.swift` and `VaaniBankingApp.swift`
- [ ] Add all files from `ios-app/VaaniBankingApp/`:
  - [ ] VaaniBankingApp.swift
  - [ ] Views/ContentView.swift
  - [ ] Bridge/WebViewStore.swift
  - [ ] Intents/CheckBalanceIntent.swift
  - [ ] Resources/Info.plist

## 🔧 Configuration

- [ ] Project Settings → Signing & Capabilities:
  - [ ] Enable "Automatically manage signing"
  - [ ] Select your Team
  - [ ] Add capability: **Siri**
- [ ] Replace Info.plist with the one from Resources/
- [ ] Update React app URL in `ContentView.swift` (line 68):
  - [ ] Production: `https://your-app.vercel.app`
  - [ ] OR Local dev: `http://localhost:5173`

## 🧪 Testing - Simulator

- [ ] Select iPhone simulator (iPhone 15 Pro recommended)
- [ ] Press Cmd+R to build and run
- [ ] App opens successfully
- [ ] React frontend loads
- [ ] Can login to app
- [ ] Chat works normally
- [ ] Check console for: `📱 Native iOS bridge detected`

## 🧪 Testing - Deep Links

- [ ] App running in simulator
- [ ] Open Safari on simulator
- [ ] Navigate to: `vaani://chat?message=Check%20balance`
- [ ] Tap "Open" when prompted
- [ ] App opens and message auto-sends
- [ ] Check console for: `📱 Received message from iOS native app`

## 📱 Testing - Physical Device

### Build on Device
- [ ] Connect iPhone to Mac via USB
- [ ] Trust computer on iPhone (if prompted)
- [ ] Select your iPhone as build target in Xcode
- [ ] Build and run (Cmd+R)
- [ ] App installs and runs on device
- [ ] Trust developer certificate:
  - [ ] Settings → General → VPN & Device Management
  - [ ] Tap your developer name
  - [ ] Tap "Trust"

### Test Shortcuts
- [ ] Open Shortcuts app on iPhone
- [ ] Tap + to create new shortcut
- [ ] Add Action → Apps → VaaniBankingApp
- [ ] Select "Check Balance"
- [ ] Run shortcut
- [ ] App opens and sends message

### Test Siri
- [ ] Settings → Siri & Search → VaaniBankingApp
- [ ] Enable "Use with Ask Siri"
- [ ] See "Suggested Shortcuts" appear
- [ ] Say: "Hey Siri, check my balance"
- [ ] Siri opens app
- [ ] Message auto-sends
- [ ] Response shows in Siri card

## 🎨 Customization

- [ ] Create app icon (1024x1024):
  - [ ] Design icon or use template
  - [ ] Generate all sizes at https://appicon.co
  - [ ] Add to Assets.xcassets in Xcode
- [ ] Customize app colors (optional):
  - [ ] Add color sets in Assets.xcassets
  - [ ] Use bank brand colors
- [ ] Test in both light and dark modes

## 🔐 Production Preparation

- [ ] Update URL to production domain
- [ ] Test with production API
- [ ] Implement authentication storage (Keychain)
- [ ] Add Face ID/Touch ID (optional)
- [ ] Test all intents thoroughly
- [ ] Add privacy policy
- [ ] Prepare App Store screenshots
- [ ] Write app description
- [ ] Set up App Store Connect

## 📝 All 4 Intents Tested

- [ ] "Check Balance" - Works
- [ ] "Transfer Money" - Works
- [ ] "View Transactions" - Works
- [ ] "Set Reminder" - Works

## 🏠 Home Screen Shortcuts Created

- [ ] Check Balance shortcut
- [ ] Transfer Money shortcut (optional)
- [ ] View Transactions shortcut (optional)

## 📚 Documentation Read

- [ ] QUICKSTART.md
- [ ] README.md
- [ ] INTEGRATION_GUIDE.md
- [ ] IMPLEMENTATION_SUMMARY.md

## 🐛 Issues Resolved

- [ ] No console errors
- [ ] Deep links working
- [ ] Siri integration working
- [ ] All intents functional
- [ ] React bridge communicating

## ✨ Optional Enhancements

- [ ] Bundle React build for offline support
- [ ] Add more custom intents
- [ ] Implement push notifications
- [ ] Add analytics tracking
- [ ] Create widgets (iOS 14+)
- [ ] Support iPad layout

## 🚀 Ready for Users

- [ ] App tested thoroughly
- [ ] No critical bugs
- [ ] Siri commands work reliably
- [ ] User experience is smooth
- [ ] Documentation complete
- [ ] Ready to share/deploy

---

## Quick Links

- **Start Here**: QUICKSTART.md
- **Full Guide**: README.md
- **Troubleshooting**: INTEGRATION_GUIDE.md
- **Summary**: IMPLEMENTATION_SUMMARY.md

## Next Step

👉 **Open QUICKSTART.md and follow the 5-minute setup!**
