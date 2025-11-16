# Quick Start: Multi-Language Voice Feature

## What's New? 🎉
Your Vaani Banking Voice Assistant now supports **English** and **Hindi** voice input with a language selector!

## Try It Out

### 1. Start the App
```bash
cd frontend
npm run dev
```
Visit: http://localhost:5175/

### 2. Login & Navigate to Chat
- Login with demo credentials
- Click "Start Chat" button on profile page

### 3. Use Language Selector
- Look for the language button in the chat header (next to "Back to Profile")
- Click to see dropdown with 🇮🇳 English and 🇮🇳 Hindi
- Select your preferred language

### 4. Test Voice Input

#### English Test:
1. Select "English" from language selector
2. Click microphone icon
3. Say: **"Show my account balance"**
4. See the transcript appear in the input box

#### Hindi Test:
1. Select "हिंदी" from language selector
2. Click microphone icon
3. Say: **"मेरा खाता बैलेंस दिखाओ"**
4. See the transcript appear in the input box

## Features to Notice

### Language Selector
- **Button**: Shows current language with flag
- **Dropdown**: Lists all available languages
- **Active Indicator**: Checkmark on selected language
- **Disabled During Recording**: Can't change while listening

### Voice Recognition
- **Live Preview**: See words as you speak (gray text)
- **Final Transcript**: Confirmed words appear in black
- **Auto-restart**: Keeps listening in continuous mode
- **Error Messages**: Clear feedback for permission/support issues

### UI Updates
- Language selector is disabled while recording
- Voice button pulses when listening
- Input placeholder changes based on state

## Quick Configuration

### Enable More Languages
**File**: `src/config/voiceConfig.js`

```javascript
// Find language in SUPPORTED_LANGUAGES array
{
  code: 'ta-IN',
  name: 'Tamil',
  nativeName: 'தமிழ்',
  flag: '🇮🇳',
  enabled: true  // ← Change this to true
}
```

### Change Default Language
```javascript
export const DEFAULT_LANGUAGE = 'hi-IN';  // Start with Hindi
```

## Browser Requirements
- ✅ Chrome (Desktop/Mobile)
- ✅ Edge
- ✅ Safari (macOS/iOS)
- ❌ Firefox (Limited support)

## Troubleshooting

### Language selector not showing?
- Check browser console for errors
- Verify at least one language has `enabled: true`

### Voice not working?
- Allow microphone permission
- Use Chrome, Edge, or Safari
- Check browser console for detailed errors

### Wrong language recognition?
- Ensure you selected the correct language before speaking
- Wait for language to fully switch (watch console logs)

## Architecture Highlights

### Single File Changes
All voice provider settings in **one file**: `src/config/voiceConfig.js`

Want to switch from Web Speech API to Google Cloud?
```javascript
VOICE_PROVIDER.type = 'google-cloud'  // That's it!
```

### Clean Separation
- **Config**: `voiceConfig.js` - All settings
- **Logic**: `useSpeechRecognition.js` - Voice hook
- **UI**: `LanguageSelector.jsx` - Language picker
- **Integration**: `Chat.jsx` - Ties it together

## Next Steps

### For Users
1. Try both languages
2. Test voice commands
3. Provide feedback on recognition accuracy

### For Developers
1. Read [LANGUAGE_FEATURE.md](./LANGUAGE_FEATURE.md) for full documentation
2. Check [CHAT_MODULE_README.md](./CHAT_MODULE_README.md) for architecture
3. Enable more regional languages as needed

## Support
- **Web Speech API Docs**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **Language Codes**: https://www.ietf.org/rfc/bcp/bcp47.txt

---

**Happy Testing!** 🎤🇮🇳
