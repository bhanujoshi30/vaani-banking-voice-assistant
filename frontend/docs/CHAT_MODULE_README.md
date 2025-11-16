# Chat Module Documentation

## Overview
The chat module has been refactored into a modular, maintainable structure with separate concerns for voice recognition, UI components, and utility functions. It now supports **multi-language voice input** (English/Hindi) with an extensible architecture for adding more languages.

## Structure

```
frontend/src/
├── config/
│   └── voiceConfig.js            # Voice provider & language config
├── components/
│   └── Chat/
│       ├── ChatMessage.jsx       # Individual message display
│       ├── ChatInput.jsx         # Input field with voice/text controls
│       ├── ChatSidebar.jsx       # Quick actions and status sidebar
│       ├── TypingIndicator.jsx   # Typing animation
│       ├── LanguageSelector.jsx  # Language picker dropdown
│       └── LanguageSelector.css  # Language selector styles
├── hooks/
│   └── useSpeechRecognition.js   # Custom hook for voice input
├── utils/
│   └── chatUtils.js              # Chat helper functions
└── pages/
    ├── Chat.jsx                  # Main chat page container
    └── Chat.css                  # Chat page styles
```

> **📖 For detailed language feature documentation, see [LANGUAGE_FEATURE.md](LANGUAGE_FEATURE.md)**

## Components

### ChatMessage.jsx
**Purpose:** Renders individual chat messages with avatar and metadata

**Props:**
- `message` (object): Message data with id, role, content, timestamp
- `userName` (string): Display name for user messages

**Features:**
- Different avatars for user vs assistant
- Timestamp formatting
- Role-based styling

---

### ChatInput.jsx
**Purpose:** Message input with voice and text controls

**Props:**
- `inputText` (string): Current input value
- `setInputText` (function): Update input value
- `isTyping` (boolean): Disable input when assistant is typing
- `isListening` (boolean): Voice recording state
- `isSpeechSupported` (boolean): Browser support status
- `onSubmit` (function): Form submit handler
- `onVoiceClick` (function): Voice button click handler
- `inputRef` (ref): Input element reference

**Features:**
- Voice input button with visual feedback
- Disabled state for unsupported browsers
- Dynamic placeholder based on listening state
- Send button with validation

---

### ChatSidebar.jsx
**Purpose:** Displays quick actions and voice feature status

**Props:**
- `isSpeechSupported` (boolean): Voice feature availability

**Features:**
- Quick action buttons for common tasks
- Recent topics list
- Voice feature status indicator

---

### TypingIndicator.jsx
**Purpose:** Animated typing indicator for assistant responses

**Features:**
- Animated dots
- Consistent styling with assistant messages

---

### LanguageSelector.jsx
**Purpose:** Language picker for voice input

**Props:**
- `selectedLanguage` (string): Current language code (e.g., 'en-IN')
- `onLanguageChange` (function): Callback when language changes
- `disabled` (boolean): Disable during voice recording

**Features:**
- Dropdown with flag + language name
- Shows native names (e.g., "हिंदी" for Hindi)
- Active language indicator
- Click outside to close
- Smooth animations

**Supported Languages:**
- 🇮🇳 English (en-IN) - Enabled
- 🇮🇳 Hindi (hi-IN) - Enabled
- 8+ regional languages ready in config

> **See [LANGUAGE_FEATURE.md](LANGUAGE_FEATURE.md) for full language documentation**

---

## Hooks

### useSpeechRecognition.js
**Purpose:** Custom React hook for Web Speech API integration with multi-language support

**Parameters:**
```javascript
{
  lang: 'en-IN',          // Language code (default: from voiceConfig)
  continuous: true,        // Keep listening (default: from voiceConfig)
  interimResults: true     // Show real-time results (default: from voiceConfig)
}
```

**Returns:**
```javascript
{
  isListening,          // boolean: Is currently listening
  isSpeechSupported,    // boolean: Browser support status
  transcript,           // string: Final transcript
  interimTranscript,    // string: Interim (live) transcript
  fullTranscript,       // string: Final + interim combined
  error,                // string|null: Error message
  startListening,       // function: Start voice input
  stopListening,        // function: Stop voice input
  toggleListening,      // function: Toggle listening state
  resetTranscript       // function: Clear transcript
}
```

**Features:**
- Automatic browser detection
- Continuous listening mode
- Auto-restart on end (for continuous mode)
- Comprehensive error handling
- Event logging for debugging

**Key Fix:**
- Changed `continuous: true` to keep listening beyond 2 seconds
- Implements auto-restart when recognition ends unexpectedly
- Properly handles manual stop vs automatic end

---

## Utilities

### chatUtils.js
**Purpose:** Helper functions for chat functionality

**Functions:**

#### `formatTime(date)`
Format timestamp for display
```javascript
formatTime(new Date()) // "2:30 PM"
```

#### `generateMessageId()`
Generate unique message ID
```javascript
generateMessageId() // 1700000000000
```

#### `createMessage(role, content)`
Create message object
```javascript
createMessage('user', 'Hello')
// { id: 1700000000000, role: 'user', content: 'Hello', timestamp: Date }
```

#### `simulateAIResponse(userMessage)`
Generate simulated AI response (async)
```javascript
const response = await simulateAIResponse('check balance')
// Returns: "I can help you check your account balance..."
```

**Constants:**
- `QUICK_ACTIONS`: Array of quick action templates
- `INITIAL_MESSAGE`: Default welcome message

---

## Voice Recognition - How It Works

### Issue Fixed
**Problem:** Voice recognition was stopping after ~2 seconds

**Root Cause:** 
- `continuous: false` was set, causing recognition to stop after first result
- No auto-restart mechanism

**Solution:**
1. Set `continuous: true` in speech recognition config
2. Implemented auto-restart on `onend` event
3. Added `isManualStopRef` to differentiate user stop vs automatic end
4. Proper event handling for all recognition states

### Flow

1. **User clicks microphone button**
   - `toggleListening()` called
   - `startListening()` initiates recognition
   - Visual feedback: green pulsing animation

2. **User speaks**
   - Interim results update in real-time
   - `fullTranscript` updates continuously
   - Input field shows live transcription

3. **Recognition continues**
   - `continuous: true` keeps listening
   - Auto-restarts if ended unexpectedly
   - Stops only on manual click or error

4. **User stops**
   - Click microphone again
   - `stopListening()` sets manual stop flag
   - Recognition ends cleanly

5. **User sends message**
   - Input text contains full transcript
   - Recognition auto-stops if active
   - Transcript is reset for next input

### Browser Support

✅ **Supported:**
- Chrome/Chromium
- Microsoft Edge
- Safari (iOS & macOS)

❌ **Not Supported:**
- Firefox (different API)
- Internet Explorer

### Error Handling

The hook handles various error scenarios:
- **no-speech**: No audio detected
- **audio-capture**: Microphone not found
- **not-allowed**: Permission denied
- **network**: Network issues
- **aborted**: Recognition cancelled

All errors are logged and user-friendly messages provided.

---

## Usage Example

```javascript
import Chat from './pages/Chat';

// In your app routing
<Route 
  path="/chat" 
  element={<Chat session={session} onSignOut={handleSignOut} />} 
/>
```

### Using the Voice Hook Independently

```javascript
import useSpeechRecognition from './hooks/useSpeechRecognition';

function MyComponent() {
  const {
    isListening,
    isSpeechSupported,
    fullTranscript,
    toggleListening,
  } = useSpeechRecognition({
    lang: 'hi-IN', // For Hindi
    continuous: true,
    interimResults: true,
  });

  return (
    <div>
      <button onClick={toggleListening}>
        {isListening ? 'Stop' : 'Start'}
      </button>
      <p>{fullTranscript}</p>
    </div>
  );
}
```

---

## Future Enhancements

### Planned Features
- [ ] Language selector UI (en-IN, hi-IN, etc.)
- [ ] Auto-send after silence detection
- [ ] Voice playback for assistant responses
- [ ] Multi-language "Hinglish" support
- [ ] Quick action button integration
- [ ] Backend API integration
- [ ] Toast notifications for errors
- [ ] Conversation history persistence
- [ ] Voice biometric authentication

### Backend Integration Points
- `simulateAIResponse()` → Replace with actual API call
- Message sending → Add API endpoint call
- User authentication → Validate session token
- Transaction data → Fetch from banking API

---

## Testing

### Manual Testing Checklist
- [ ] Voice input starts on microphone click
- [ ] Voice input continues beyond 2 seconds
- [ ] Input field shows live transcription
- [ ] Voice input stops on second click
- [ ] Messages send with voice transcription
- [ ] Typing indicator appears
- [ ] Assistant responses are simulated
- [ ] Error handling for no microphone
- [ ] Error handling for denied permissions
- [ ] Responsive design on mobile

### Browser Testing
Test in Chrome, Edge, Safari for voice features.
Verify graceful degradation in Firefox.

---

## Troubleshooting

### Voice Not Working
1. Check browser compatibility (use Chrome/Edge/Safari)
2. Ensure microphone permissions granted
3. Check console for error messages
4. Verify HTTPS or localhost (required for microphone)

### Recognition Stops Too Quickly
- Verify `continuous: true` in hook options
- Check network connection
- Ensure microphone is not auto-sleeping

### No Transcription Showing
- Check browser console for errors
- Verify `interimResults: true`
- Test microphone in system settings

---

## Contributing

When extending the chat module:
1. Keep components small and focused
2. Use PropTypes for type checking
3. Document new utility functions
4. Add error handling for edge cases
5. Test across browsers
6. Update this documentation

---

## License
Part of Vaani Banking Voice Assistant project.
