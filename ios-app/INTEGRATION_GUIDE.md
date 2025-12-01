# iOS App Integration Guide

This guide helps you integrate the native iOS app with your React frontend for Siri and Shortcuts support.

## ✅ Changes Made to React Frontend

The following changes have been made to enable iOS native bridge communication:

### 1. `frontend/src/main.jsx`
Added iOS bridge detection and initialization:
- Detects if running inside native iOS app (WKWebView)
- Sets up `window.sendAutoMessage()` function for native app to call
- Sends "ready" signal to native app when React loads
- Logs bridge status to console

### 2. `frontend/src/pages/Chat.jsx`
Added two useEffect hooks:

**Hook 1: Listen for native messages**
- Listens for `nativeAutoSend` custom events
- Stops any ongoing TTS/listening when message received
- Calls `sendMessage()` with the message from iOS app
- Handles messages from Siri, Shortcuts, or deep links

**Hook 2: Send responses back to native**
- Sends assistant responses back to iOS app
- Enables Siri to show response in snippet card
- Includes language and structured data for rich cards

## 🔧 Testing the Integration

### Test in Web Browser (No iOS App)
1. Start React dev server:
   ```bash
   cd frontend
   npm run dev
   ```
2. Open http://localhost:5173
3. Console should show: `🌐 Running in web browser (not native iOS app)`
4. Everything should work normally

### Test with iOS App
1. Open Xcode project (see ios-app/README.md for setup)
2. In `ContentView.swift`, update URL to localhost:
   ```swift
   if let url = URL(string: "http://localhost:5173") {
       webView.load(URLRequest(url: url))
   }
   ```
3. Start React dev server (keep it running)
4. Run iOS app in simulator
5. Console should show:
   - `📱 Native iOS bridge detected - setting up communication`
   - `✅ iOS bridge initialized - window.sendAutoMessage available`
   - `✅ React app signaled ready`

### Test Deep Link
1. With app running in simulator
2. Open Safari on simulator
3. Navigate to: `vaani://chat?message=Check%20balance`
4. Tap "Open" when prompted
5. App should open and auto-send "Check balance" message
6. Watch console for:
   - `📱 Received message from iOS native app: Check balance`
   - Message should appear in chat and get response

### Test Siri (Physical Device Only)
1. Build app on physical device (requires Apple Developer account)
2. Go to Settings → Siri & Search → VaaniBankingApp
3. Enable "Use with Ask Siri"
4. Say: "Hey Siri, check my balance"
5. Siri should:
   - Open the app
   - Auto-send the message
   - Show response in Siri card

## 🐛 Troubleshooting

### "sendAutoMessage is not defined"
- Check browser console for iOS bridge initialization messages
- Make sure you're running inside iOS app (not web browser)
- Verify `main.jsx` changes are applied
- Try reloading the app

### Message not sending automatically
- Check Chat.jsx useEffect hooks are added correctly
- Look for `nativeAutoSend` event in console
- Verify `sendMessage` function is available in scope
- Check dependencies array includes all required values

### Native app not receiving responses
- Verify `window.webkit.messageHandlers.nativeHandler` exists
- Check for errors in postMessage call
- Look for `📱 Sent response to native app` in console
- Verify WebViewStore.swift has `nativeHandler` message handler

### Deep link not working
- Verify URL scheme in Info.plist: `vaani://`
- Check `handleDeepLink` function in VaaniBankingApp.swift
- Test URL format: `vaani://chat?message=Your%20message`
- Check for URL encoding (spaces = %20)

## 📝 URL Encoding Reference

When creating deep links or shortcuts, encode special characters:

| Character | Encoded |
|-----------|---------|
| Space     | %20     |
| ?         | %3F     |
| &         | %26     |
| =         | %3D     |

Example URLs:
```
Check balance:
vaani://chat?message=Check%20balance

Transfer money:
vaani://chat?message=I%20want%20to%20transfer%20money

View transactions:
vaani://chat?message=Show%20my%20recent%20transactions

Set reminder:
vaani://chat?message=Set%20a%20payment%20reminder
```

## 🚀 Deployment

### For Development (localhost)
Use in ContentView.swift:
```swift
if let url = URL(string: "http://localhost:5173") {
    webView.load(URLRequest(url: url))
}
```

### For Production (Vercel/deployed URL)
Use in ContentView.swift:
```swift
if let url = URL(string: "https://your-app.vercel.app") {
    webView.load(URLRequest(url: url))
}
```

### Bundle React Build (Offline Support)
1. Build React app:
   ```bash
   cd frontend
   npm run build
   ```

2. Add `dist` folder to Xcode project:
   - Right-click project → "Add Files..."
   - Select `frontend/dist` folder
   - Check "Create folder references"

3. Update ContentView.swift:
   ```swift
   if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "dist") {
       webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
   }
   ```

## 🔐 Security Notes

1. **Authentication**: Store tokens in iOS Keychain, not localStorage
2. **HTTPS Only**: Use HTTPS for production URLs (App Transport Security)
3. **Input Validation**: Native app should validate all URLs and messages
4. **Sensitive Data**: Don't send sensitive data (PINs, passwords) via URL parameters

## 📚 Next Steps

1. **Test all intents**: Check Balance, Transfer, Transactions, Reminders
2. **Add more intents**: Create new App Intents for other features
3. **Customize Siri responses**: Improve snippet views and dialogs
4. **Add authentication**: Implement Keychain storage for secure tokens
5. **Submit to App Store**: Follow Apple's review guidelines

## 🆘 Support

If you encounter issues:
1. Check console logs in both Xcode and browser
2. Verify all file changes are applied correctly
3. Test in web browser first (no iOS app)
4. Test deep links in Safari before testing Siri
5. Use physical device for Siri testing (not simulator)

For more details, see:
- `ios-app/README.md` - Complete iOS app setup guide
- Apple's [App Intents Documentation](https://developer.apple.com/documentation/appintents)
- [WKWebView Documentation](https://developer.apple.com/documentation/webkit/wkwebview)
