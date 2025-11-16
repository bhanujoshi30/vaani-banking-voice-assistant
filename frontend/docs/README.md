# Vaani Voice Assistant - Frontend Documentation

Welcome to the Vaani Banking Voice Assistant frontend documentation!

## 📚 Documentation Index

### Quick Start
- **[Quick Start: Language Feature](./QUICK_START_LANGUAGE.md)** - Get started testing the multi-language voice feature

### Feature Documentation
- **[Language Feature Guide](./LANGUAGE_FEATURE.md)** - Complete guide to multi-language voice input
  - Supported languages (English, Hindi + 8 regional languages)
  - Voice provider configuration
  - How to add new languages
  - Switching voice providers (Web Speech API, Google Cloud, Azure)
  - Troubleshooting

### Architecture Documentation
- **[Chat Module Architecture](./CHAT_MODULE_README.md)** - Complete chat module documentation
  - Component structure
  - Custom hooks
  - Utility functions
  - Integration guide

## 🎯 What's Inside?

### Chat Module
The chat interface provides a ChatGPT-like experience with:
- Real-time message display
- Text and voice input options
- Quick action sidebar
- Typing indicators
- Multi-language voice support

### Voice Recognition
Voice-to-text functionality using Web Speech API with:
- Continuous listening mode
- Live transcript preview
- Language selection (English/Hindi)
- Error handling and user feedback
- Extensible provider architecture

### Multi-Language Support
Currently enabled languages:
- 🇮🇳 **English** (India) - `en-IN`
- 🇮🇳 **हिंदी** (Hindi) - `hi-IN`

Ready to enable:
- Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi

## 🚀 Getting Started

### For Users
1. Read [QUICK_START_LANGUAGE.md](./QUICK_START_LANGUAGE.md)
2. Try the language selector
3. Test voice input in both English and Hindi

### For Developers
1. Review [CHAT_MODULE_README.md](./CHAT_MODULE_README.md) for architecture
2. Read [LANGUAGE_FEATURE.md](./LANGUAGE_FEATURE.md) for language implementation
3. Check `src/config/voiceConfig.js` for configuration options

## 📁 Key Files

### Configuration
- `src/config/voiceConfig.js` - Voice provider and language settings

### Components
- `src/components/Chat/ChatMessage.jsx` - Message display
- `src/components/Chat/ChatInput.jsx` - Input with voice controls
- `src/components/Chat/ChatSidebar.jsx` - Quick actions
- `src/components/Chat/LanguageSelector.jsx` - Language picker
- `src/components/Chat/TypingIndicator.jsx` - Typing animation

### Hooks
- `src/hooks/useSpeechRecognition.js` - Voice recognition logic

### Utilities
- `src/utils/chatUtils.js` - Chat helper functions

### Pages
- `src/pages/Chat.jsx` - Main chat page
- `src/pages/Chat.css` - Chat styling

## 🔧 Configuration Quick Reference

### Enable a Language
```javascript
// In src/config/voiceConfig.js
{
  code: 'ta-IN',
  name: 'Tamil',
  nativeName: 'தமிழ்',
  flag: '🇮🇳',
  enabled: true  // ← Change to true
}
```

### Change Voice Provider
```javascript
// In src/config/voiceConfig.js
export const VOICE_PROVIDER = {
  type: 'google-cloud',  // Change from 'web-speech-api'
  // ... provider config
};
```

### Adjust Voice Settings
```javascript
// In src/config/voiceConfig.js
export const VOICE_SETTINGS = {
  autoSendDelay: 2000,        // Time before auto-send
  confidenceThreshold: 0.7,   // Recognition confidence
  maxDuration: 60000,         // Max recording time
};
```

## 🌟 Features

- ✅ ChatGPT-like UI
- ✅ Voice-to-text input
- ✅ Multi-language support (English/Hindi)
- ✅ Continuous voice recognition
- ✅ Live transcript preview
- ✅ Language selector
- ✅ Quick action buttons
- ✅ Typing indicators
- ✅ Responsive design
- ✅ Modular architecture
- ✅ Provider abstraction

## 📖 External Resources

### Web Speech API
- [MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Browser Support](https://caniuse.com/speech-recognition)

### Alternative Providers
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [Azure Speech Service](https://azure.microsoft.com/services/cognitive-services/speech-to-text/)

### Standards
- [BCP 47 Language Tags](https://www.ietf.org/rfc/bcp/bcp47.txt)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

## 🤝 Contributing

When adding features:
1. Update relevant documentation in this folder
2. Add examples and code snippets
3. Update this index if adding new docs

## 📝 Documentation Standards

- Use clear, descriptive headings
- Include code examples
- Add troubleshooting sections
- Keep quick start guides concise
- Provide architecture diagrams where helpful

---

**Last Updated**: November 2025  
**Maintained By**: Vaani Development Team
