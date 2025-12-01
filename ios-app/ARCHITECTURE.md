# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          iOS Device                              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     Siri / Shortcuts                        │ │
│  │                                                              │ │
│  │  "Hey Siri, check my balance"                              │ │
│  │  OR tap Home Screen shortcut                               │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
│                         │                                         │
│                         │ Invoke App Intent                       │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              CheckBalanceIntent.swift                       │ │
│  │                                                              │ │
│  │  1. Receives Siri command                                  │ │
│  │  2. Creates deep link: vaani://chat?message=...           │ │
│  │  3. Opens app with deep link                               │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
│                         │                                         │
│                         │ Deep Link                               │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              VaaniBankingApp.swift                          │ │
│  │                                                              │ │
│  │  1. Handles onOpenURL                                      │ │
│  │  2. Parses message from URL                                │ │
│  │  3. Sets pendingMessage in AppState                        │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
│                         │                                         │
│                         │ Message                                 │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  ContentView.swift                          │ │
│  │                                                              │ │
│  │  1. Observes pendingMessage                                │ │
│  │  2. Calls WebViewStore.sendMessage()                       │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
│                         │                                         │
│                         │ JavaScript Call                         │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 WebViewStore.swift                          │ │
│  │                                                              │ │
│  │  1. Evaluates JS: window.sendAutoMessage("Check balance") │ │
│  │  2. Receives responses via WKScriptMessageHandler          │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
│                         │                                         │
│                         │ JavaScript Bridge                       │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     WKWebView                               │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │           React Frontend (Chat.jsx)                   │ │ │
│  │  │                                                        │ │ │
│  │  │  1. Listens for 'nativeAutoSend' event               │ │ │
│  │  │  2. Calls sendMessage(message)                        │ │ │
│  │  │  3. Sends to FastAPI backend                          │ │ │
│  │  │  4. Receives AI response                              │ │ │
│  │  │  5. Sends response back to native via postMessage()  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Message Flow Sequence

```
User: "Hey Siri, check my balance"
  │
  ▼
Siri invokes CheckBalanceIntent
  │
  ▼
Intent creates URL: vaani://chat?message=Check%20balance
  │
  ▼
iOS opens app with URL
  │
  ▼
VaaniBankingApp.swift handles onOpenURL
  │
  ▼
Parses: message = "Check balance"
  │
  ▼
Sets AppState.pendingMessage = "Check balance"
  │
  ▼
ContentView observes change
  │
  ▼
WebViewStore.sendMessage("Check balance")
  │
  ▼
Evaluates JS: window.sendAutoMessage("Check balance")
  │
  ▼
React main.jsx dispatches 'nativeAutoSend' event
  │
  ▼
Chat.jsx listens and receives message
  │
  ▼
Calls sendMessage("Check balance")
  │
  ▼
Sends to FastAPI: POST /api/chat
  │
  ▼
AI processes and responds: "Your balance is ₹2,43,890.55"
  │
  ▼
Chat.jsx displays response
  │
  ▼
Sends back to native: window.webkit.messageHandlers.nativeHandler.postMessage()
  │
  ▼
WebViewStore receives via WKScriptMessageHandler
  │
  ▼
Updates lastResponse state
  │
  ▼
Siri displays response in snippet card
  │
  ▼
User sees balance in Siri interface ✓
```

## Component Responsibilities

### Native iOS Layer

**VaaniBankingApp.swift**
- App entry point
- Deep link handling
- AppState management
- Intent registration

**ContentView.swift**
- WebView container
- Loading states
- URL configuration
- AppState observer

**WebViewStore.swift**
- JavaScript bridge
- Message sending
- Response receiving
- WKWebView management

**CheckBalanceIntent.swift**
- Siri integration
- Intent handling
- URL construction
- Snippet views

### Web Layer

**main.jsx**
- Bridge detection
- `window.sendAutoMessage` setup
- Ready signal to native

**Chat.jsx**
- Event listener setup
- Message handling
- Response sending
- Native bridge communication

### Backend Layer

**FastAPI (backend/ai/main.py)**
- Chat endpoint: `/api/chat`
- AI processing
- Balance retrieval
- Response generation

## Data Flow

### Native → Web
```
Swift: WebViewStore.sendMessage("Check balance")
  ↓
JavaScript: window.sendAutoMessage("Check balance")
  ↓
Event: new CustomEvent('nativeAutoSend', { detail: { message } })
  ↓
React: useEffect listens for 'nativeAutoSend'
  ↓
React: sendMessage("Check balance")
```

### Web → Native
```
React: Assistant responds with "Your balance is..."
  ↓
React: useEffect detects new assistant message
  ↓
JavaScript: window.webkit.messageHandlers.nativeHandler.postMessage({
  type: 'chatResponse',
  response: "Your balance is..."
})
  ↓
Swift: WebViewStore.userContentController receives message
  ↓
Swift: Updates lastResponse state
```

## Technology Stack

### iOS Native
- Language: Swift 5.9+
- UI Framework: SwiftUI
- Web Integration: WKWebView
- Siri Integration: App Intents (iOS 16+)
- Deep Linking: Custom URL Schemes

### Web Frontend
- Framework: React 18
- Build Tool: Vite
- Routing: React Router
- Bridge: WKWebView JavaScript Bridge

### Backend
- Framework: FastAPI (Python)
- AI: LangChain + OpenAI GPT-4
- Database: PostgreSQL/SQLite
- Authentication: JWT tokens

## Communication Protocol

### Native → Web Messages
```json
{
  "message": "Check balance",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Web → Native Messages
```json
{
  "type": "chatResponse",
  "response": "Your balance is ₹2,43,890.55",
  "timestamp": "2025-01-15T10:30:05Z",
  "language": "en-IN",
  "structuredData": {
    "type": "balance",
    "accounts": [...]
  }
}
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. App Transport Security (Info.plist)                     │
│     - HTTPS enforcement for production                       │
│     - Localhost exception for development                    │
│                                                               │
│  2. Siri Authorization                                       │
│     - User must enable in Settings                           │
│     - App-specific permission required                       │
│                                                               │
│  3. Deep Link Validation                                     │
│     - URL scheme verification                                │
│     - Parameter sanitization                                 │
│                                                               │
│  4. WebView Security                                         │
│     - JavaScript enabled only                                │
│     - Message handler whitelist                              │
│     - CORS policy enforcement                                │
│                                                               │
│  5. Authentication (Backend)                                 │
│     - JWT tokens                                             │
│     - Session management                                     │
│     - API authorization                                      │
│                                                               │
│  Recommended: iOS Keychain for token storage                │
│  Recommended: Face ID/Touch ID for app launch               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Performance Optimization

### App Launch
- WebView preloading
- Cache React bundle
- Lazy load intents

### Message Handling
- Retry logic with backoff
- Ready state detection
- Queue messages if not ready

### Memory Management
- Proper cleanup in useEffect
- WebView resource limits
- Message handler cleanup

## Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│                      Error Scenarios                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. WebView fails to load                                    │
│     → Show error view with retry button                      │
│                                                               │
│  2. JavaScript bridge not ready                              │
│     → Retry message send after delay                         │
│                                                               │
│  3. Deep link parsing fails                                  │
│     → Log error, open app without message                    │
│                                                               │
│  4. Backend API error                                        │
│     → Display error message in chat                          │
│                                                               │
│  5. Siri intent fails                                        │
│     → Return error dialog to Siri                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Load from URL (Current)
```
Pros:
✓ Easy updates (just deploy React)
✓ No app resubmission needed
✓ Smaller app size

Cons:
✗ Requires internet connection
✗ Slower initial load
```

### Option 2: Bundle React Build
```
Pros:
✓ Offline support
✓ Faster load times
✓ Better user experience

Cons:
✗ Larger app size
✗ Need app update for changes
```

### Recommended: Hybrid Approach
- Bundle static assets
- Load dynamic content from API
- Cache for offline mode

---

This architecture provides:
- ✅ Native iOS performance
- ✅ Siri integration
- ✅ Shortcuts support
- ✅ Seamless React integration
- ✅ Bidirectional communication
- ✅ Production-ready error handling
