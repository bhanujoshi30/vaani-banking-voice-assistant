# Frontend Module Documentation

## Overview

The Vaani frontend is a modern React application built with Vite, providing a voice-enabled banking interface. It features voice login, conversational AI chat, UPI payments, and comprehensive banking operations.

**Port**: 5173  
**Tech Stack**: React 19, Vite, React Router DOM, Web Speech API

---

## Architecture

```
frontend/
├── index.html                # HTML entry point
├── package.json              # Dependencies and scripts
├── vite.config.js            # Vite configuration
├── eslint.config.js          # ESLint configuration
│
├── public/                   # Static assets
│   └── images/              # Image files
│
└── src/
    ├── main.jsx             # Application entry point
    ├── App.jsx              # Main app component with routing
    ├── App.css              # Global styles
    ├── index.css            # Base styles
    │
    ├── pages/               # Page components
    │   ├── Login.jsx        # Login page with voice/password auth
    │   ├── Profile.jsx      # User profile and dashboard
    │   ├── Chat.jsx         # AI chat interface
    │   ├── Transactions.jsx # Transaction history
    │   ├── Reminders.jsx    # Payment reminders
    │   ├── Beneficiaries.jsx # Saved beneficiaries
    │   ├── DeviceBinding.jsx # Device management
    │   └── SignInHelp.jsx   # Login assistance
    │
    ├── components/          # Reusable components
    │   ├── SunHeader.jsx    # App header/navigation
    │   ├── LanguageDropdown.jsx # Language selector
    │   ├── LanguageToggle.jsx # Language toggle
    │   ├── UPIConsentModal.jsx # UPI terms consent
    │   ├── UPIPinModal.jsx  # UPI PIN entry
    │   ├── VoiceEnrollmentModal.jsx # Voice enrollment
    │   ├── ForceLogoutModal.jsx # Session timeout
    │   ├── AIAssistantLogo.jsx # AI logo component
    │   └── Chat/            # Chat UI components
    │       ├── ChatHeader.jsx
    │       ├── ChatInput.jsx
    │       ├── ChatMessage.jsx
    │       └── ChatSidebar.jsx
    │
    ├── hooks/               # Custom React hooks
    │   ├── useChatHandler.js # Chat message handling
    │   ├── useChatMessages.js # Message state management
    │   ├── useSpeechRecognition.js # Voice input
    │   ├── useTextToSpeech.js # Voice output
    │   ├── useVoiceMode.js  # Voice mode state
    │   └── usePageLanguage.js # Language preference
    │
    ├── api/                 # API client modules
    │   ├── client.js        # Backend API (port 8000)
    │   └── aiClient.js      # AI API (port 8001)
    │
    ├── services/            # Business logic services
    │   └── voiceService.js  # Voice processing utilities
    │
    ├── utils/               # Utility functions
    │   ├── audio.js         # Audio processing
    │   ├── date.js          # Date formatting
    │   └── currency.js      # Currency formatting
    │
    └── config/              # Configuration
        └── constants.js     # App constants
```

---

## Pages

### 1. Login Page (`pages/Login.jsx`)

Entry point for user authentication.

**Features:**
- **Password Login**: Traditional username/password
- **Voice Login**: Voice biometric authentication
- **OTP Verification**: Required for both modes
- **Device Binding**: Automatic device registration
- **Language Selection**: Choose preferred language
- **Voice Enrollment**: First-time voice registration

**Components:**
- Login form
- Voice enrollment modal
- Language selector
- Sign-in help link

**Flow:**

**Password Login:**
1. User enters customer number and password
2. Clicks "Sign In"
3. Enters OTP
4. Redirects to Profile

**Voice Login:**
1. User enters customer number
2. Clicks "Voice Login"
3. Records voice sample (says passphrase)
4. Enters OTP
5. Redirects to Profile

**First-Time Voice:**
1. User clicks "Enroll Voice"
2. Modal opens with instructions
3. Records voice sample
4. Stores voice signature
5. Can now use voice login

**State Management:**
- `authMode`: 'password' | 'voice'
- `userId`: Customer number
- `password`: Password (if password mode)
- `otp`: One-time password
- `voiceSample`: Recorded audio blob
- `isVoiceEnrolled`: Voice enrollment status

**API Calls:**
- `POST /api/v1/auth/login` (Backend)

### 2. Profile Page (`pages/Profile.jsx`)

User dashboard and account overview.

**Features:**
- Account summary cards
- Quick actions (Transfer, Pay Bill, etc.)
- Recent transactions preview
- Upcoming reminders
- Device binding status
- Logout

**Displayed Data:**
- Full name and customer ID
- Account numbers and balances
- Last login timestamp
- Segment and branch info
- Active device count

**Quick Actions:**
- Go to Chat
- View Transactions
- Manage Reminders
- View Beneficiaries
- Manage Devices

**API Calls:**
- Profile data from session
- Optional: Refresh account balances

### 3. Chat Page (`pages/Chat.jsx`)

Conversational AI interface for banking operations.

**Features:**
- **Text Chat**: Type messages
- **Voice Chat**: Speak naturally
- **Multi-language**: English/Hindi support
- **UPI Payments**: Hello UPI integration
- **Quick Actions**: Common banking tasks
- **Message History**: Conversation persistence
- **Account Statement Download**: Get statements via chat

**Chat Components:**
- ChatHeader: Title, language selector, voice toggle
- ChatSidebar: Quick action buttons
- ChatMessages: Message list
- ChatInput: Input box with send/mic buttons

**Voice Mode:**
- Click microphone icon to enable
- Speak query
- System responds with voice
- Auto-mic reactivation

**UPI Mode:**
- Toggle UPI mode in sidebar
- Say "Hello Vaani, pay ₹500 to John"
- Accept consent (first time)
- Enter PIN
- Payment processed

**Quick Actions:**
- Check Balance
- View Transactions
- Transfer Funds
- Pay via UPI
- Set Reminder
- Get Statement

**State Management:**
- `messages`: Array of chat messages
- `voiceMode`: Boolean for voice chat
- `upiMode`: Boolean for UPI payments
- `language`: Selected language
- `isLoading`: Processing state
- `error`: Error messages

**API Calls:**
- `POST /api/chat` (AI Backend)
- `POST /api/chat/stream` (AI Backend, streaming)
- `POST /api/tts` (AI Backend, optional)

### 4. Transactions Page (`pages/Transactions.jsx`)

Transaction history and filtering.

**Features:**
- Transaction list with details
- Filter by date range
- Filter by type (debit/credit)
- Filter by channel (UPI, NEFT, etc.)
- Transaction details modal
- Export to CSV (future)

**Transaction Card Display:**
- Date and time
- Description
- Amount (with +/- indicator)
- Channel badge
- Balance after
- Reference ID

**Filters:**
- Last 7 days / 30 days / 3 months / Custom
- All / Debit / Credit
- All Channels / UPI / NEFT / ATM / etc.

**API Calls:**
- `GET /api/v1/accounts/{account_number}/transactions` (Backend)

### 5. Reminders Page (`pages/Reminders.jsx`)

Payment and bill reminders management.

**Features:**
- List all reminders
- Filter by status (pending/completed)
- Create new reminder
- Mark as complete
- Delete reminder
- Recurrence support

**Reminder Types:**
- Bill Payment
- EMI Payment
- Subscription Renewal
- Custom Reminder

**Reminder Card Display:**
- Type icon
- Message/description
- Due date and time
- Status badge
- Action buttons (Complete/Delete)

**Create Reminder Form:**
- Reminder type selection
- Message/description
- Date and time picker
- Recurrence pattern (optional)
- Associated account

**API Calls:**
- `GET /api/v1/reminders` (Backend)
- `POST /api/v1/reminders` (Backend)
- `PATCH /api/v1/reminders/{id}/status` (Backend)
- `DELETE /api/v1/reminders/{id}` (Backend)

### 6. Beneficiaries Page (`pages/Beneficiaries.jsx`)

Saved beneficiary management for quick transfers.

**Features:**
- List all beneficiaries
- Add new beneficiary
- Edit beneficiary details
- Delete beneficiary
- Mark as favorite
- Quick transfer to beneficiary

**Beneficiary Card Display:**
- Name and nickname
- Account number / UPI ID
- Bank name
- Favorite star icon
- Action buttons (Edit/Delete/Transfer)

**Add Beneficiary Form:**
- Name
- Nickname (optional)
- Account number OR UPI ID
- Phone number
- Bank name and IFSC (if account number)
- Mark as favorite checkbox

**API Calls:**
- `GET /api/v1/beneficiaries` (Backend)
- `POST /api/v1/beneficiaries` (Backend)
- `DELETE /api/v1/beneficiaries/{id}` (Backend)

### 7. Device Binding Page (`pages/DeviceBinding.jsx`)

Trusted device management.

**Features:**
- List all trusted devices
- Device details (platform, last verified)
- Revoke device binding
- Re-bind device
- Voice signature status

**Device Card Display:**
- Device label (e.g., "iPhone 13")
- Platform (iOS/Android/Web)
- Trust level badge
- Registration date
- Last verified timestamp
- Voice enrolled status
- Revoke button

**Device Binding Status:**
- TRUSTED (green badge)
- SUSPICIOUS (yellow badge)
- REVOKED (red badge)

**API Calls:**
- `GET /api/v1/device-bindings` (Backend)
- `DELETE /api/v1/device-bindings/{id}` (Backend - revoke)

### 8. Sign-In Help Page (`pages/SignInHelp.jsx`)

Help and support for login issues.

**Features:**
- Forgot password instructions
- Voice login troubleshooting
- OTP not received help
- Contact support info
- Back to login link

**Help Topics:**
- Reset password
- Re-enroll voice
- Verify mobile number
- Device binding issues
- Contact customer care

---

## Components

### Header Component (`components/SunHeader.jsx`)

Application header with navigation and user menu.

**Features:**
- Bank logo
- Page title
- Navigation menu
- Language selector
- User profile dropdown
- Logout button

**Navigation Links:**
- Profile
- Chat
- Transactions
- Reminders
- Beneficiaries
- Devices

**Responsive:**
- Hamburger menu on mobile
- Collapsible navigation

### UPI Consent Modal (`components/UPIConsentModal.jsx`)

First-time UPI consent for RBI compliance.

**Features:**
- Terms and conditions display
- Consent checkbox
- Accept/Decline buttons
- Persistent consent (localStorage)

**Terms Covered:**
- PIN must be entered manually
- Not spoken aloud
- RBI compliance
- Transaction verification
- Security guidelines

**Storage:**
- Saves consent in localStorage
- Per-user consent tracking

### UPI PIN Modal (`components/UPIPinModal.jsx`)

Secure PIN entry for UPI payments.

**Features:**
- 6-digit PIN input
- Auto-focus between fields
- Paste support (6 digits)
- Auto-submit on completion
- Masked input (password type)
- Payment details display

**Security:**
- No autocomplete
- Password input type
- Client-side validation only
- Clears on close

**Payment Details Display:**
- Amount
- Recipient name
- Payment description

### Voice Enrollment Modal (`components/VoiceEnrollmentModal.jsx`)

Voice biometric enrollment interface.

**Features:**
- Instructions display
- Passphrase to speak
- Record button
- Audio waveform visualization (future)
- Re-record option
- Submit for enrollment

**Enrollment Flow:**
1. Read instructions
2. Click "Start Recording"
3. Speak passphrase
4. Click "Stop Recording"
5. Play back to verify
6. Submit for enrollment

**Passphrase:**
"Sun Bank mera saathi, har kadam surakshit banking ka vaada"

### Language Dropdown (`components/LanguageDropdown.jsx`)

Language selection dropdown.

**Supported Languages:**
- English (en-IN)
- Hindi (hi-IN)

**Features:**
- Current language display
- Dropdown menu
- Language switch callback
- Persistent preference

### Chat Components (`components/Chat/`)

#### ChatHeader
- Chat title
- Language selector
- Voice mode toggle
- Settings icon (future)

#### ChatSidebar
- Quick action buttons
- UPI mode toggle
- Common queries
- Help link

#### ChatMessage
- Message bubble
- User/assistant differentiation
- Timestamp
- Copy text button
- Voice playback (for AI responses)

#### ChatInput
- Text input field
- Send button
- Microphone button
- Voice recording indicator
- Character count (future)

---

## Hooks (Custom React Hooks)

### useChatHandler (`hooks/useChatHandler.js`)

Handles chat message sending and receiving.

**Features:**
- Send text messages
- Send voice messages
- Call AI backend
- Handle streaming responses
- Error handling
- Loading states

**Methods:**
- `sendMessage(message, voiceMode)`: Send message to AI
- `streamMessage(message)`: Stream response token-by-token

**State:**
- `isLoading`: Message processing state
- `error`: Error messages

### useChatMessages (`hooks/useChatMessages.js`)

Manages chat message state and history.

**Features:**
- Add user messages
- Add assistant messages
- Clear conversation
- Load message history
- Persist to localStorage (future)

**State:**
- `messages`: Array of message objects
- Each message: `{id, role, content, timestamp}`

**Methods:**
- `addMessage(role, content)`: Add new message
- `clearMessages()`: Clear all messages
- `loadHistory()`: Load from storage

### useSpeechRecognition (`hooks/useSpeechRecognition.js`)

Web Speech API integration for voice input.

**Features:**
- Start/stop recognition
- Continuous listening
- Language selection
- Interim results
- Final transcription
- Error handling

**Browser Support:**
- Chrome/Edge: Full support
- Safari: Partial support
- Firefox: Requires flag

**Methods:**
- `startListening()`: Start voice recognition
- `stopListening()`: Stop recognition
- `isListening`: Boolean state

**State:**
- `transcript`: Recognized text
- `isListening`: Recognition active state
- `error`: Error messages

**Configuration:**
- `continuous`: Keep listening after results
- `interimResults`: Show partial transcripts
- `lang`: Recognition language (en-IN, hi-IN)

### useTextToSpeech (`hooks/useTextToSpeech.js`)

Text-to-speech for AI responses using **Web Speech API**.

**Technology**: Browser-based `window.speechSynthesis` (SpeechSynthesis API)

**Features:**
- Speak text aloud using browser voices
- Stop speaking
- Pause and resume playback
- Voice selection (system voices)
- Rate and pitch control
- Queue management
- No external API calls required

**Methods:**
- `speak(text, language)`: Speak text using selected voice
- `stop()`: Stop speaking immediately
- `pause()`: Pause current speech
- `resume()`: Resume paused speech
- `isSpeaking`: Boolean state
- `getVoices()`: Get available system voices

**Voice Selection:**
- Hindi voices preferred for hi-IN (e.g., "hi-IN" locale)
- English voices for en-IN (e.g., "en-IN", "en-US" locale)
- Automatic voice matching based on language
- Fallback to default system voice

**Configuration:**
- `rate`: Speech rate (0.5-2.0, default: 1.0)
- `pitch`: Voice pitch (0.0-2.0, default: 1.0)
- `volume`: Volume (0.0-1.0, default: 1.0)

**Browser Support:**
- Chrome/Edge: Excellent (multiple voices)
- Safari: Good (limited voices)
- Firefox: Good
- Mobile: iOS Safari, Chrome Android

**Example Usage:**
```javascript
const { speak, stop, isSpeaking } = useTextToSpeech();

// Speak English
speak("Your balance is ₹10,000", "en-IN");

// Speak Hindi
speak("आपका बैलेंस ₹10,000 है", "hi-IN");

// Stop if speaking
if (isSpeaking) {
  stop();
}
```

### useVoiceMode (`hooks/useVoiceMode.js`)

Voice mode state management.

**Features:**
- Enable/disable voice mode
- Auto-mic activation
- Voice mode persistence
- Voice mode indicator

**State:**
- `isVoiceMode`: Boolean
- `toggleVoiceMode()`: Toggle function

**Behavior:**
- When enabled: Auto-starts mic after AI response
- When disabled: Manual send required

### usePageLanguage (`hooks/usePageLanguage.js`)

Page-level language preference.

**Features:**
- Get/set language preference
- Persist to localStorage
- Sync across components
- Fallback to browser language

**State:**
- `language`: Current language
- `setLanguage(lang)`: Update language

**Storage Key:** `userLanguage`

---

## API Clients

### Backend Client (`api/client.js`)

HTTP client for backend API (port 8000).

**Base URL:** `http://localhost:8000/api/v1`

**Methods:**

#### `authenticateUser({userId, password, deviceIdentifier, ...})`
- POST /auth/login
- Returns: `{success, profile, accessToken, expiresIn}`

#### `getUserAccounts(accessToken)`
- GET /accounts
- Returns: List of user accounts

#### `getAccountBalance(accountNumber, accessToken)`
- GET /accounts/{accountNumber}/balance
- Returns: Balance details

#### `getTransactions(accountNumber, params, accessToken)`
- GET /accounts/{accountNumber}/transactions
- Returns: Transaction list

#### `transferFunds(fromAccount, toAccount, amount, description, accessToken)`
- POST /accounts/{fromAccount}/transfer
- Returns: Transfer receipt

#### `getReminders(accessToken)`
- GET /reminders
- Returns: Reminder list

#### `createReminder(reminderData, accessToken)`
- POST /reminders
- Returns: Created reminder

#### `getBeneficiaries(accessToken)`
- GET /beneficiaries
- Returns: Beneficiary list

#### `getDeviceBindings(accessToken)`
- GET /device-bindings
- Returns: Device binding list

#### `revokeDeviceBinding(bindingId, accessToken)`
- DELETE /device-bindings/{bindingId}
- Returns: Success confirmation

#### `verifyUPIPin(pin, paymentDetails, accessToken)`
- POST /upi/verify-pin
- Returns: Verification result

**Error Handling:**
- Catches network errors
- Returns standardized error format
- Logs errors to console

### AI Client (`api/aiClient.js`)

HTTP client for AI backend (port 8001).

**Base URL:** `http://localhost:8001`

**Methods:**

#### `sendChatMessage({message, userId, sessionId, language, userContext, messageHistory, voiceMode, upiMode})`
- POST /api/chat
- Returns: AI response

**Request:**
```javascript
{
  message: "Check my balance",
  user_id: "uuid",
  session_id: "session-uuid",
  language: "en-IN",
  user_context: {
    account_number: "ACC001",
    name: "John Doe"
  },
  message_history: [...],
  voice_mode: false,
  upi_mode: false
}
```

**Response:**
```javascript
{
  success: true,
  response: "Your balance is ₹10,000",
  intent: "banking_operation",
  language: "en-IN",
  timestamp: "2025-11-20T14:30:00",
  statement_data: null,  // For downloads
  structured_data: null  // For UI components
}
```

#### `streamChatMessage({message, ...})`
- POST /api/chat/stream
- Returns: EventSource for SSE streaming

**Usage:**
```javascript
const eventSource = await streamChatMessage({...});
eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
  } else {
    appendToMessage(event.data);
  }
};
```

#### `getTextToSpeech(text, language, useAzure)`
- POST /api/tts
- Returns: Audio blob

#### `checkHealth()`
- GET /health
- Returns: Backend health status

---

## State Management

### App-Level State (App.jsx)

**Session State:**
```javascript
{
  authenticated: boolean,
  user: {
    fullName: string,
    accountSummary: [...],
    lastLogin: string,
    ...
  },
  accessToken: string,
  expiresAt: timestamp,
  meta: {},
  detail: {}
}
```

**Methods:**
- `authenticate({userId, password, ...})`: Login user
- `signOut()`: Logout user

### Chat State (Chat.jsx)

**Chat State:**
```javascript
{
  messages: [
    {id, role, content, timestamp}
  ],
  voiceMode: boolean,
  upiMode: boolean,
  language: string,
  isLoading: boolean,
  error: string
}
```

---

## Routing (React Router)

**Routes Defined in App.jsx:**

| Path | Component | Protected | Description |
|------|-----------|-----------|-------------|
| `/` | Login | No | Login page |
| `/profile` | Profile | Yes | User dashboard |
| `/chat` | Chat | Yes | AI chat interface |
| `/transactions` | Transactions | Yes | Transaction history |
| `/reminders` | Reminders | Yes | Payment reminders |
| `/beneficiaries` | Beneficiaries | Yes | Saved beneficiaries |
| `/device-binding` | DeviceBinding | Yes | Device management |
| `/sign-in-help` | SignInHelp | No | Login help |
| `*` | Navigate | - | Redirect to appropriate page |

**Protected Route Logic:**
```javascript
session.authenticated ? (
  <Component session={session} onSignOut={signOut} />
) : (
  <Navigate to="/" replace />
)
```

---

## Styling

### CSS Organization

- **Global Styles**: `index.css`, `App.css`
- **Component Styles**: Co-located with components (e.g., `Chat.css`, `UPIPinModal.css`)
- **Responsive Design**: Mobile-first approach
- **Color Scheme**: Bank branding colors

### Key Design Patterns

**Colors:**
- Primary: Bank blue
- Success: Green
- Warning: Orange
- Danger: Red
- Background: White/Light gray

**Typography:**
- Headings: Bold, larger sizes
- Body: Regular weight
- Code/Numbers: Monospace

**Layout:**
- Header: Fixed top
- Sidebar: Left navigation (desktop)
- Main Content: Centered, max-width
- Footer: Sticky bottom

---

## Voice Features

### Voice Login

**Process:**
1. User clicks "Voice Login"
2. Modal requests microphone permission
3. User speaks passphrase
4. Audio captured as WAV blob
5. Sent to backend for verification
6. Voice embedding compared
7. Login success/failure

**Browser Support:**
- Chrome/Edge: Full support
- Safari: Requires HTTPS or localhost
- Firefox: Limited support

### Voice Chat

**Process:**
1. User enables voice mode
2. Clicks microphone button
3. Speaks query
4. Speech recognized to text
5. Text sent to AI
6. AI response received
7. Response spoken via TTS
8. Mic auto-reactivates

**Features:**
- Continuous conversation
- Auto-mic reactivation
- Visual feedback (mic animation)
- Cancel mid-speech

---

## UPI Integration

### Hello UPI Flow

**Wake Phrase Detection:**
- "Hello Vaani" or "Hello UPI"
- Activates UPI mode
- Shows UPI badge

**Payment Command:**
```
"Hello Vaani, pay ₹500 to John via UPI"
```

**Flow:**
1. User speaks/types wake phrase + payment command
2. UPI mode activated
3. Consent modal (first time)
4. AI extracts: amount, recipient
5. PIN modal opens
6. User enters 6-digit PIN
7. Payment processed
8. Confirmation shown

**Components Involved:**
- UPIConsentModal: First-time consent
- UPIPinModal: PIN entry
- Chat: Command processing

---

## Performance Optimization

### Code Splitting

- Lazy load pages
- Dynamic imports for heavy components
- Route-based splitting

### Caching

- Service worker (future)
- LocalStorage for preferences
- Session storage for temporary data

### Optimization Tips

1. **Minimize Re-renders**: Use React.memo, useMemo, useCallback
2. **Debounce Input**: Especially for search/filter
3. **Virtual Scrolling**: For long transaction lists (future)
4. **Image Optimization**: Compress and lazy-load images

---

## Browser Support

**Recommended:**
- Chrome 90+
- Edge 90+
- Safari 14+
- Firefox 88+

**Features with Limited Support:**
- Voice Recognition: Chrome/Edge best
- Voice Synthesis: All modern browsers
- WebRTC: Chrome/Edge/Firefox

---

## Development Workflow

### Running Development Server

```bash
cd frontend
npm run dev
```

Server starts at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

Output in `dist/` folder

### Linting

```bash
npm run lint
```

### Preview Production Build

```bash
npm run preview
```

---

## Environment Variables

Create `.env` in frontend folder:

```env
# AI Backend URL
VITE_AI_BACKEND_URL=http://localhost:8001

# Backend API URL
VITE_BACKEND_URL=http://localhost:8000

# Enable debug logging
VITE_DEBUG=false
```

**Usage in code:**
```javascript
const AI_BACKEND_URL = import.meta.env.VITE_AI_BACKEND_URL;
```

---

## Testing

### Manual Testing Checklist

- [ ] Login with password
- [ ] Login with voice
- [ ] Voice enrollment
- [ ] Language switching
- [ ] Text chat
- [ ] Voice chat
- [ ] UPI payment
- [ ] Transaction viewing
- [ ] Reminder creation
- [ ] Beneficiary management
- [ ] Device binding
- [ ] Logout

### Future Automated Testing

- Unit tests with Vitest
- Component tests with React Testing Library
- E2E tests with Playwright

---

## Security Considerations

### Authentication

- Access token stored in memory (not localStorage)
- Session expiration handling
- Auto-logout on token expiry

### Voice Security

- Voice samples not stored in browser
- Sent to backend immediately
- Voice embeddings on server only

### UPI Security

- PIN never logged
- Cleared immediately after use
- No autocomplete on PIN fields
- HTTPS required for production

### Data Protection

- No sensitive data in localStorage
- Session data cleared on logout
- CORS properly configured

---

## Accessibility

### Features

- Keyboard navigation
- ARIA labels
- Screen reader support (partial)
- High contrast mode (future)

### Improvements Needed

- Full ARIA implementation
- Better focus management
- Voice guidance for blind users
- Keyboard shortcuts

---

## Future Enhancements

### Features
- Biometric authentication (Touch ID, Face ID)
- Push notifications
- Offline mode
- QR code scanner integration
- Dark mode
- Multiple themes

### Performance
- Progressive Web App (PWA)
- Service worker caching
- Virtual scrolling
- Image lazy loading

### Accessibility
- Full WCAG 2.1 compliance
- Screen reader optimization
- Voice-only mode
- Assistive technology support

---

## Related Documentation

- [Setup Guide](./other/setup_guide.md) - Installation instructions
- [Backend Documentation](./backend_modules.md) - Backend API details
- [AI Documentation](./ai_modules.md) - AI module details
- [UPI Flow](./other/upi_payment_flow.md) - UPI implementation
- [API Reference](./api_reference.md) - Complete API docs
