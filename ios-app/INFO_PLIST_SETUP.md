# Info.plist Configuration Guide

## ✅ Completed Steps

1. **Created** a new system-level Info.plist at:
   - `/ios-app/VaaniBankingApp/Info.plist`

2. **Backed up** the original Info.plist to:
   - `/ios-app/VaaniBankingApp/VaaniBankingApp/Resources/Info.plist.backup`

3. **Replaced** the Resources Info.plist with the new system version

## 📋 What's Included in the New Info.plist

### Core Bundle Configuration
- Bundle identifier and version info
- Display name: "Vaani Banking"
- Minimum iOS version: 16.0
- SwiftUI scene configuration

### Privacy Permissions
- ✅ Siri usage description
- ✅ Microphone access (for voice commands)
- ✅ Speech recognition
- ✅ Camera access (for QR codes)
- ✅ Photo library access
- ✅ Face ID authentication

### Deep Linking
- URL Schemes: `vaani://` and `vaanibanking://`
- Example: `vaani://balance` or `vaanibanking://transfer`

### App Intents (Siri Integration)
- CheckBalanceIntent
- TransferMoneyIntent
- ViewTransactionsIntent
- SetReminderIntent

### Network Security
- HTTPS enforced for production
- HTTP allowed for localhost (development)
- Exception for 127.0.0.1 (testing)

## 🔧 How to Configure in Xcode

### Method 1: Set Info.plist Path in Build Settings (Recommended)

1. **Open Xcode Project**
   ```bash
   cd /Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app/VaaniBankingApp
   open VaaniBankingApp.xcodeproj
   ```

2. **Select Your Target**
   - Click on the project in the Navigator
   - Select the "VaaniBankingApp" target

3. **Go to Build Settings**
   - Click on "Build Settings" tab
   - Search for "Info.plist"

4. **Set the Info.plist File Path**
   - Find "Info.plist File" setting
   - Set to: `VaaniBankingApp/Resources/Info.plist`
   - (This is relative to the project root)

5. **Clean and Build**
   - Product → Clean Build Folder (⇧⌘K)
   - Product → Build (⌘B)

### Method 2: Move to Standard Location

If you want the Info.plist at the project root level:

1. **In Xcode**, right-click on the project root in Navigator
2. **Add Files to "VaaniBankingApp"...**
3. **Select** the Info.plist from the root VaaniBankingApp folder
4. **Uncheck** "Copy items if needed" (it's already in your project)
5. **Check** your target is selected
6. Click "Add"

### Method 3: Via Xcode's General Tab

1. **Select Target** → General tab
2. Scroll to **"App Category"** section
3. Look for **"Info.plist File"** 
4. Either:
   - Browse to select the file
   - Or enter path: `VaaniBankingApp/Resources/Info.plist`

## 🧪 Testing the Configuration

### 1. Verify Info.plist is Recognized
```bash
# After building, check if Info.plist is included in the app bundle
cd ~/Library/Developer/Xcode/DerivedData/VaaniBankingApp-*/Build/Products/Debug-iphonesimulator/VaaniBankingApp.app
cat Info.plist
```

### 2. Test Permissions
- Run the app and trigger microphone/camera features
- Check if permission dialogs show your custom descriptions

### 3. Test Siri Integration
- Say "Hey Siri, check my balance"
- Should prompt to use Vaani Banking app

### 4. Test Deep Links
- From Safari or Terminal:
  ```bash
  xcrun simctl openurl booted "vaani://balance"
  ```

## 📝 Important Notes

### Current File Locations
```
ios-app/VaaniBankingApp/
├── Info.plist                              # ← New system Info.plist (master copy)
└── VaaniBankingApp/
    └── Resources/
        ├── Info.plist                       # ← Active Info.plist (copied from above)
        └── Info.plist.backup                # ← Original backup
```

### Best Practice
- Keep the **root Info.plist** as your master copy
- The **Resources/Info.plist** is what Xcode actually uses
- Update the root version, then copy to Resources when needed

### Updating Info.plist
When you need to make changes:

```bash
# 1. Edit the master copy
nano /Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app/VaaniBankingApp/Info.plist

# 2. Copy to Resources
cp /Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app/VaaniBankingApp/Info.plist \
   /Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app/VaaniBankingApp/VaaniBankingApp/Resources/Info.plist

# 3. Clean and rebuild in Xcode
```

## 🚨 Troubleshooting

### "Info.plist not found" error
- Check Build Settings → "Info.plist File" path
- Should be: `VaaniBankingApp/Resources/Info.plist`

### Permissions not working
- Make sure all NS*UsageDescription keys are present
- Rebuild the app completely
- Reset simulator: Device → Erase All Content and Settings

### Siri not recognizing intents
- Ensure iOS 16.0+ is set as minimum
- Check that NSAppIntentsMetadata is present
- Rebuild and re-install the app

### Deep links not working
- Verify CFBundleURLSchemes contains your schemes
- Test with: `xcrun simctl openurl booted "vaani://test"`

## 🎯 Next Steps

1. **Open Xcode and configure the Info.plist path** (see Method 1 above)
2. **Update Bundle Identifier** in Xcode to match your Apple Developer account
3. **Add your Team** in Signing & Capabilities
4. **Build and test** on simulator or device
5. **Test Siri integration** after installing on a physical device

## 📱 Bundle Identifier Recommendations

Current: `com.vaani.banking` (in URL scheme)

For your app, use:
- Development: `com.[yourname].vaanibanking`
- Production: `com.vaanibanking.app` or `com.[company].vaanibanking`

Update in Xcode:
1. Select Target → General
2. Bundle Identifier field
3. Must match your Apple Developer account provisioning profile
