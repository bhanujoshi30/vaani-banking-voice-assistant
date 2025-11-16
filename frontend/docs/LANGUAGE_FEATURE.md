# Multi-Language Voice Input Feature

## Overview
The Vaani Banking Voice Assistant now supports multi-language voice input, allowing users to interact with the chatbot in their preferred language. Currently enabled: **English** and **Hindi**, with support for 8 additional regional Indian languages ready to enable.

## Features

### 1. **Language Selection**
- Dropdown selector in the chat header
- Shows language flag, name, and native name
- Persists across the session
- Visual indicator for active language
- Disabled during active voice recording

### 2. **Supported Languages**

#### Currently Enabled:
- 🇮🇳 **English (India)** - `en-IN`
- 🇮🇳 **Hindi (हिंदी)** - `hi-IN`

#### Ready to Enable (in `voiceConfig.js`):
- 🇮🇳 **Tamil (தமிழ்)** - `ta-IN`
- 🇮🇳 **Telugu (తెలుగు)** - `te-IN`
- 🇮🇳 **Marathi (मराठी)** - `mr-IN`
- 🇮🇳 **Bengali (বাংলা)** - `bn-IN`
- 🇮🇳 **Gujarati (ગુજરાતી)** - `gu-IN`
- 🇮🇳 **Kannada (ಕನ್ನಡ)** - `kn-IN`
- 🇮🇳 **Malayalam (മലയാളം)** - `ml-IN`
- 🇮🇳 **Punjabi (ਪੰਜਾਬੀ)** - `pa-IN`

### 3. **Voice Provider Abstraction**
The system is designed to easily switch between different voice recognition providers:

#### Current: Web Speech API
- Built into modern browsers (Chrome, Edge, Safari)
- No API keys required
- Works offline
- Free to use

#### Future Options:
- **Google Cloud Speech-to-Text**: Higher accuracy, more language support
- **Azure Cognitive Services**: Enterprise-grade, multi-region support
- **Custom Provider**: Easy to add your own

## Architecture

### File Structure
```
frontend/src/
├── config/
│   └── voiceConfig.js          # Centralized voice configuration
├── hooks/
│   └── useSpeechRecognition.js # Voice recognition logic
├── components/Chat/
│   ├── LanguageSelector.jsx    # Language picker UI
│   └── LanguageSelector.css    # Language picker styles
└── pages/
    └── Chat.jsx                # Chat page with language integration
```

### Key Components

#### 1. `voiceConfig.js` - Configuration Module
**Purpose**: Single source of truth for all voice-related settings

**Exports**:
```javascript
// Language definitions
SUPPORTED_LANGUAGES       // Array of all languages
DEFAULT_LANGUAGE         // 'en-IN'
getEnabledLanguages()    // Get only enabled languages
getLanguageByCode(code)  // Find language by code

// Provider configuration
VOICE_PROVIDER           // Current provider settings
createVoiceProvider(lang) // Factory to create provider config

// Voice settings
VOICE_SETTINGS           // Confidence threshold, delays, etc.

// UI text
VOICE_UI_TEXT            // Localized button labels, messages
getUIText(languageCode)  // Get UI text for language
```

**To Add a New Language**:
```javascript
// In SUPPORTED_LANGUAGES array
{
  code: 'ta-IN',        // Language code
  name: 'Tamil',        // English name
  nativeName: 'தமிழ்',  // Native name
  flag: '🇮🇳',          // Flag emoji
  enabled: true         // Set to true to enable
}
```

**To Switch Voice Provider**:
```javascript
// In VOICE_PROVIDER object
export const VOICE_PROVIDER = {
  type: 'google-cloud',  // Change from 'web-speech-api'
  
  googleCloud: {
    apiKey: process.env.VITE_GOOGLE_CLOUD_API_KEY,
    endpoint: 'https://speech.googleapis.com/v1/speech:recognize'
  }
};
```

#### 2. `useSpeechRecognition.js` - Voice Hook
**Purpose**: React hook that abstracts voice recognition logic

**Usage**:
```javascript
const {
  isListening,         // Currently recording
  isSpeechSupported,   // Browser support
  transcript,          // Final transcript
  interimTranscript,   // Live preview
  error,              // Error message
  toggleListening,     // Start/stop recording
  resetTranscript      // Clear transcript
} = useSpeechRecognition({
  lang: 'hi-IN',       // Selected language
  continuous: true,    // Keep listening
  interimResults: true // Show live preview
});
```

**How It Works**:
1. Gets provider config from `voiceConfig.js`
2. Initializes Web Speech API with language
3. Re-initializes when language changes
4. Handles continuous mode and auto-restart
5. Provides clean React state interface

#### 3. `LanguageSelector.jsx` - Language Picker
**Purpose**: UI component for selecting language

**Props**:
```javascript
<LanguageSelector
  selectedLanguage="en-IN"    // Current language code
  onLanguageChange={setLang}  // Callback when changed
  disabled={isListening}      // Disable during recording
/>
```

**Features**:
- Dropdown with flag + language name
- Shows native name (e.g., "हिंदी")
- Active language highlighted
- Click outside to close
- Smooth animations

#### 4. `Chat.jsx` - Integration
**How Language is Used**:
```javascript
// State management
const [language, setLanguage] = useState(DEFAULT_LANGUAGE);

// Pass to voice hook
const { ... } = useSpeechRecognition({
  lang: language,  // Dynamic language
  continuous: true,
  interimResults: true
});

// Render language selector
<LanguageSelector 
  selectedLanguage={language}
  onLanguageChange={setLanguage}
  disabled={isListening}
/>
```

**State Flow**:
1. User clicks language in selector
2. `setLanguage('hi-IN')` updates state
3. Voice hook re-initializes with new language
4. Voice recognition now uses Hindi

## User Experience

### Changing Language
1. Click the language button in the chat header
2. Select desired language from dropdown
3. Voice recognition automatically switches
4. Previous transcript is preserved

### Voice Recording Flow
1. Click microphone icon
2. Speak in selected language
3. See live preview (interim results)
4. Final transcript appears after pause
5. Click send or continue speaking

### Error Handling
- **No Browser Support**: Shows error message, disables voice button
- **Microphone Permission Denied**: Prompts user to allow access
- **Network Error**: Falls back to text input
- **No Speech Detected**: Shows retry message

## Configuration Guide

### Enable More Languages
**File**: `/frontend/src/config/voiceConfig.js`

```javascript
// Find the language in SUPPORTED_LANGUAGES array
{
  code: 'ta-IN',
  name: 'Tamil',
  nativeName: 'தமிழ்',
  flag: '🇮🇳',
  enabled: true  // Change from false to true
}
```

### Change Default Language
```javascript
// In voiceConfig.js
export const DEFAULT_LANGUAGE = 'hi-IN';  // Change from 'en-IN'
```

### Adjust Voice Settings
```javascript
// In VOICE_SETTINGS object
export const VOICE_SETTINGS = {
  autoSendDelay: 2000,        // Wait 2s before auto-send
  confidenceThreshold: 0.7,   // Minimum confidence
  maxDuration: 60000,         // Max 60s recording
  interimUpdateDelay: 100     // Update interim every 100ms
};
```

### Add Localized UI Text
```javascript
// In VOICE_UI_TEXT object
'ta-IN': {
  startListening: 'பேசத் தொடங்குங்கள்',
  stopListening: 'நிறுத்து',
  listening: 'கேட்கிறது...',
  // ... more translations
}
```

## Future Enhancements

### Planned Features
- [ ] Persistent language preference (localStorage)
- [ ] Auto-detect user's system language
- [ ] Language-specific voice commands
- [ ] Mixed language support (code-switching)
- [ ] Dialect support (e.g., British vs American English)

### Provider Migration (When Needed)

#### Google Cloud Speech-to-Text
```javascript
// 1. Update voiceConfig.js
VOICE_PROVIDER.type = 'google-cloud';

// 2. Add .env variable
VITE_GOOGLE_CLOUD_API_KEY=your_api_key_here

// 3. Implement in useSpeechRecognition.js
// Replace Web Speech API with Google Cloud API calls
```

#### Azure Cognitive Services
```javascript
// 1. Update voiceConfig.js
VOICE_PROVIDER.type = 'azure';

// 2. Add .env variables
VITE_AZURE_SUBSCRIPTION_KEY=your_key
VITE_AZURE_REGION=eastus

// 3. Implement in useSpeechRecognition.js
// Use Azure Speech SDK
```

## Testing

### Test Language Switching
1. Open chat page
2. Click language selector
3. Switch between English and Hindi
4. Click microphone and speak in each language
5. Verify correct language recognition

### Test Voice Recognition
- **English**: "Show my account balance"
- **Hindi**: "मेरा खाता बैलेंस दिखाओ"

### Browser Compatibility
- ✅ Chrome 25+ (Desktop & Mobile)
- ✅ Edge 79+
- ✅ Safari 14.1+ (macOS, iOS)
- ❌ Firefox (Limited support)

## Troubleshooting

### Language Not Switching
**Issue**: Voice still uses old language after switching
**Solution**: 
- Check browser console for errors
- Verify language code in `SUPPORTED_LANGUAGES`
- Ensure `enabled: true` for the language

### Voice Recognition Not Working
**Issue**: Microphone icon does nothing
**Solution**:
- Check browser permissions (chrome://settings/content/microphone)
- Verify browser support (check console warnings)
- Try in Chrome/Edge if using Firefox

### Poor Recognition Accuracy
**Issue**: Wrong words transcribed
**Solution**:
- Speak clearly and slowly
- Reduce background noise
- Consider switching to Google Cloud provider
- Adjust `confidenceThreshold` in `VOICE_SETTINGS`

### Dropdown Not Showing Languages
**Issue**: Language selector is empty
**Solution**:
- Check `getEnabledLanguages()` in console
- Ensure at least one language has `enabled: true`
- Verify import in `LanguageSelector.jsx`

## Code Examples

### Add Custom Language
```javascript
// In voiceConfig.js
{
  code: 'ur-IN',           // Urdu (India)
  name: 'Urdu',
  nativeName: 'اردو',
  flag: '🇮🇳',
  enabled: true
}
```

### Implement Voice Command
```javascript
// In Chat.jsx, after voice input
useEffect(() => {
  if (transcript.toLowerCase().includes('balance')) {
    // Trigger balance query
    handleQuickAction('Check Balance');
  }
}, [transcript]);
```

### Customize Provider
```javascript
// In useSpeechRecognition.js
const providerConfig = createVoiceProvider(lang);

if (providerConfig.type === 'custom-provider') {
  // Your custom implementation
  const recognition = new CustomSpeechRecognition({
    language: lang,
    apiKey: providerConfig.config.apiKey
  });
}
```

## Resources

### Web Speech API
- [MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Browser Support](https://caniuse.com/speech-recognition)

### Alternative Providers
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [Azure Speech Service](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/)
- [Amazon Transcribe](https://aws.amazon.com/transcribe/)

### Language Codes
- [BCP 47 Language Tags](https://www.ietf.org/rfc/bcp/bcp47.txt)
- [ISO 639-1 Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

---

**Last Updated**: December 2024  
**Maintained By**: Vaani Development Team
