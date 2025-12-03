# iOS Setup Complete - Summary

## ✅ Issues Fixed

### 1. App Shortcuts Phrase Validation Error
**Error:** `Invalid Utterance. Every App Shortcut utterance should have one '${applicationName}' in it.`

**Fixed in:** `CheckBalanceIntent.swift`
- Updated all App Shortcut phrases to include exactly one `${applicationName}` placeholder
- All three shortcuts now comply with validation rules:
  - Check Balance
  - Transfer Money
  - View Transactions

### 2. ContentView Access Control Error
**Error:** `Property must be declared fileprivate because its type uses a private type`

**Fixed in:** `ContentView.swift`
- Made `FrontendMode` enum internal instead of private
- Also modernized deprecated APIs:
  - Updated `onChange` to iOS 17+ two-parameter closure
  - Replaced deprecated `javaScriptEnabled` with `defaultWebpagePreferences.allowsContentJavaScript`

### 3. simctl Command Not Available
**Error:** `xcrun: error: unable to find utility "simctl", not a developer tool or in PATH`

**Root Cause:** Xcode command line tools pointing to standalone CommandLineTools instead of Xcode.app

**Solution Created:** 
- Created `setup-simctl.sh` script to fix this automatically
- Created comprehensive `TESTING_GUIDE.md` with all testing procedures

## 🚀 What You Need To Do Now

### Step 1: Fix simctl (Required for testing)

Run this command from the `ios-app` directory:

```bash
cd /Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app
./setup-simctl.sh
```

**What it does:**
- Switches Xcode command line tools to use Xcode.app
- Verifies simctl is available
- Checks if simulator is running
- Tests deep linking if app is running

**You'll need to enter your password** (for sudo access).

### Step 2: Configure Xcode Project Settings

Open your Xcode project and complete these manual steps:

#### A) Add URL Type for Deep Linking
1. Select your app target in Xcode
2. Go to **Info** tab
3. Expand **URL Types** section
4. Click **+** to add a new URL Type
5. Fill in:
   - **Identifier:** `vaani`
   - **URL Schemes:** `vaani`
   - **Role:** `Editor`

#### B) Add Privacy Strings
1. Still in **Info** tab
2. Under **Custom iOS Target Properties**, click **+** and add these keys:

| Key | Value |
|-----|-------|
| `NSMicrophoneUsageDescription` | "Microphone access is needed for voice input." |
| `NSSiriUsageDescription` | "Vaani Banking uses Siri to help with voice commands." |
| `NSCameraUsageDescription` | "Camera access is needed for scanning or video." (optional) |
| `NSSpeechRecognitionUsageDescription` | "Speech recognition is used to understand your voice commands." (optional) |

#### C) Fix App Transport Security Domain
1. In **Info** tab, expand **App Transport Security Settings**
2. Expand **Exception Domains**
3. **Rename** the key from `localhost:` to `localhost` (remove the trailing colon)
4. Verify these sub-keys under `localhost`:
   - `NSExceptionAllowsInsecureHTTPLoads` = YES
   - `NSIncludesSubdomains` = YES

#### D) Set iOS Deployment Target to 18.0
1. Select your **project** (not target) in the navigator
2. Go to **Build Settings** tab
3. Search for "iOS Deployment Target"
4. Set it to **18.0** for both:
   - Project level
   - Target level

### Step 3: Build and Test

1. **Build the app** in Xcode (⌘R)
2. Wait for app to fully load on simulator
3. **Test deep linking:**

```bash
xcrun simctl openurl booted "vaani://chat?message=Check%20balance"
xcrun simctl openurl booted "vaani://chat?message=Show%20my%20recent%20transactions"
xcrun simctl openurl booted "vaani://chat?message=Transfer%20money"
```

4. **Test App Shortcuts:**
   - Open **Shortcuts** app on simulator
   - Go to **App Shortcuts** section
   - Find **Vaani Banking**
   - Verify 3 shortcuts appear

5. **Test Debug Overlay:**
   - Long-press top-right corner to show/hide debug panel
   - Try switching between Prod/Local/Bundled modes
   - Verify bridge status turns green

## 📋 Xcode Configuration Checklist

Use this to verify everything is configured:

- [ ] URL Type `vaani` added
- [ ] NSMicrophoneUsageDescription added
- [ ] NSSiriUsageDescription added  
- [ ] App Transport Security domain fixed (`localhost` not `localhost:`)
- [ ] iOS Deployment Target set to 18.0
- [ ] simctl command working (run `./setup-simctl.sh`)
- [ ] App builds without errors
- [ ] Deep links work from command line
- [ ] App Shortcuts visible in Shortcuts app
- [ ] Debug overlay shows/hides with long-press

## 🧪 Testing Checklist

After configuration:

- [ ] Build app in Xcode successfully
- [ ] App loads frontend (Prod or Local mode)
- [ ] Bridge status shows "Ready" in debug overlay
- [ ] Deep link opens app with message
- [ ] App Shortcuts appear in Shortcuts app
- [ ] Mode switching works (if frontend running locally)
- [ ] No compile errors or warnings

## 📖 Documentation Created

1. **TESTING_GUIDE.md** - Comprehensive testing procedures
   - Deep link testing
   - App Shortcuts verification
   - Siri testing (device only)
   - Debug overlay usage
   - Troubleshooting tips

2. **setup-simctl.sh** - Automated setup script
   - Fixes simctl availability
   - Tests deep linking automatically
   - Provides helpful diagnostic output

3. **README.md** - Updated with quick start section
   - Links to testing guide
   - Quick test commands
   - Setup prerequisites

## 🎯 Why You Don't See "Siri" Capability

**You asked:** "I don't see Siri as capability"

**Answer:** You're using **App Intents** (modern approach, iOS 16+), not SiriKit Intents (legacy). 

- **App Intents** don't require a "Siri" capability in Signing & Capabilities
- Your shortcuts work through `AppShortcutsProvider` protocol
- They automatically integrate with Siri and Shortcuts app
- Only legacy SiriKit intents need the explicit "Siri" capability

**Your setup is correct!** ✅

## 🔄 Next Steps

### Immediate (Required):
1. Run `./setup-simctl.sh` to fix command line tools
2. Complete Xcode configuration checklist above
3. Build and test deep links

### Soon:
1. Test on physical device for full Siri experience
2. Configure production frontend URL
3. Test with live backend APIs

### Later:
1. Add app icon
2. Configure push notifications
3. Add biometric authentication
4. Prepare for App Store submission

## ❓ Common Questions

**Q: Do I need an Apple Developer account?**
A: Not for simulator testing. You need it for:
- Running on physical device
- Full Siri testing (requires device)
- App Store distribution

**Q: Can I test Siri on simulator?**
A: No, Siri testing requires a physical iOS device. But you can test App Shortcuts in the Shortcuts app on simulator.

**Q: Why localhost and not 127.0.0.1?**
A: Your code uses `http://localhost:5173`, so the ATS exception should match `localhost`. You can add `127.0.0.1` as another exception domain if needed.

**Q: What if deep links still don't work after fixing simctl?**
A: Make sure:
1. App is running on simulator (not terminated)
2. URL Type is registered in Xcode Info tab
3. Simulator is booted (`xcrun simctl list | grep Booted`)
4. Try opening from Safari first: `vaani://chat?message=Test`

## 🆘 Get Help

If you encounter issues:

1. Check `TESTING_GUIDE.md` troubleshooting section
2. Look at Xcode console for error messages
3. Verify all checklist items above are complete
4. Try clean build (⇧⌘K then ⌘B)

## 📝 Files Modified/Created

### Modified:
- ✅ `CheckBalanceIntent.swift` - Fixed phrase validation
- ✅ `ContentView.swift` - Fixed access control + deprecated APIs
- ✅ `README.md` - Added testing section

### Created:
- ✅ `setup-simctl.sh` - Automated setup script
- ✅ `TESTING_GUIDE.md` - Comprehensive testing documentation
- ✅ `iOS_SETUP_COMPLETE.md` - This file

---

**All Swift compiler errors are now resolved!** 🎉

You just need to complete the manual Xcode configuration steps listed above, then you're ready to test.
