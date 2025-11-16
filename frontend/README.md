# Vaani Banking Voice Assistant - Frontend

A modern React-based voice-enabled banking assistant with multi-language support.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Visit: http://localhost:5173/

## ✨ Features

- 💬 **ChatGPT-like Interface** - Modern chat UI with message history
- 🎤 **Voice Input** - Web Speech API integration with continuous listening
- 🌐 **Multi-Language Support** - English and Hindi (+ 8 regional languages ready)
- 🔄 **Real-time Updates** - Live transcript preview while speaking
- 📱 **Responsive Design** - Works on desktop and mobile
- 🔧 **Modular Architecture** - Clean separation of concerns

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs) folder:

- **[Getting Started](./docs/QUICK_START_LANGUAGE.md)** - Quick guide to test the language feature
- **[Language Feature Guide](./docs/LANGUAGE_FEATURE.md)** - Multi-language voice implementation
- **[Chat Module Architecture](./docs/CHAT_MODULE_README.md)** - Component structure and hooks

👉 **Start here**: [docs/README.md](./docs/README.md)

## 🛠️ Tech Stack

- **Framework**: React 18 + Vite
- **Routing**: React Router
- **Voice**: Web Speech API (extensible to Google Cloud/Azure)
- **Styling**: CSS Modules
- **State Management**: React Hooks

## 📁 Project Structure

```
src/
├── config/
│   └── voiceConfig.js          # Voice provider & language config
├── components/
│   ├── Chat/
│   │   ├── ChatMessage.jsx
│   │   ├── ChatInput.jsx
│   │   ├── ChatSidebar.jsx
│   │   ├── LanguageSelector.jsx
│   │   └── TypingIndicator.jsx
│   └── SunHeader.jsx
├── hooks/
│   └── useSpeechRecognition.js # Voice recognition hook
├── utils/
│   └── chatUtils.js            # Helper functions
├── pages/
│   ├── Chat.jsx                # Main chat page
│   ├── Profile.jsx
│   ├── Login.jsx
│   └── ...
└── api/
    └── client.js               # API integration
```

## 🎯 Key Features

### Voice Recognition
- Continuous listening mode (no timeout)
- Live transcript preview
- Language selection (English/Hindi)
- Auto-restart on interruption
- Comprehensive error handling

### Language Support
Currently enabled:
- 🇮🇳 English (India)
- 🇮🇳 हिंदी (Hindi)

Ready to enable: Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi

### Chat Interface
- Message history
- Typing indicators
- Quick action buttons
- Voice/text input toggle
- Responsive sidebar

## ⚙️ Configuration

### Enable More Languages
Edit `src/config/voiceConfig.js`:

```javascript
{
  code: 'ta-IN',
  name: 'Tamil',
  enabled: true  // ← Change to true
}
```

### Change Voice Provider
```javascript
VOICE_PROVIDER.type = 'google-cloud'  // Switch provider
```

See [Language Feature Guide](./docs/LANGUAGE_FEATURE.md) for details.

## 🌐 Browser Support

- ✅ Chrome 25+ (Desktop & Mobile)
- ✅ Edge 79+
- ✅ Safari 14.1+ (macOS, iOS)
- ⚠️ Firefox (Limited Web Speech API support)

## 📦 Build & Deploy

```bash
# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🤝 Contributing

1. Read the [architecture documentation](./docs/CHAT_MODULE_README.md)
2. Follow the modular structure
3. Update docs when adding features
4. Test voice features in supported browsers

## 📖 Learn More

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vite.dev)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

## Original Vite Template Info

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

