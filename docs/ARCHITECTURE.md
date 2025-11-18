# Vaani Banking AI - System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                              │
│                     http://localhost:5174                            │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐              │
│  │  Chat UI     │  │  Voice Mode  │  │  Language   │              │
│  │  (Chat.jsx)  │  │  Toggle      │  │  Selector   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘              │
│         │                 │                  │                      │
│         └─────────────────┴──────────────────┘                      │
│                           │                                         │
│                    aiClient.js                                      │
│                  (API Integration)                                  │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                    HTTP REST API
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                  AI BACKEND (FastAPI)                               │
│               http://localhost:8001                                 │
│                      main.py                                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  API ENDPOINTS                               │  │
│  │  • POST /api/chat         - Main chat                       │  │
│  │  • POST /api/chat/stream  - Streaming                       │  │
│  │  • POST /api/tts          - Text-to-Speech                  │  │
│  │  • GET  /health           - Health check                    │  │
│  └─────────────────────────┬───────────────────────────────────┘  │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐  │
│  │              LANGGRAPH AGENT SYSTEM                          │  │
│  │                  (agent_graph.py)                            │  │
│  │                                                               │  │
│  │  ┌────────────────────────────────────────────────────┐     │  │
│  │  │  1. Intent Classifier (Llama 3.2 3B - Fast)       │     │  │
│  │  │     • banking_operation                            │     │  │
│  │  │     • general_faq                                  │     │  │
│  │  │     • loan_inquiry                                 │     │  │
│  │  │     • chitchat                                     │     │  │
│  │  └───────────────────┬────────────────────────────────┘     │  │
│  │                      │ Router                                │  │
│  │         ┌────────────┼────────────┐                         │  │
│  │         ▼            ▼            ▼                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │  │
│  │  │ Banking  │ │   FAQ    │ │   RAG    │                   │  │
│  │  │  Agent   │ │  Agent   │ │  Agent   │                   │  │
│  │  │ (Qwen)   │ │ (Qwen)   │ │ (Future) │                   │  │
│  │  └────┬─────┘ └──────────┘ └──────────┘                   │  │
│  │       │                                                     │  │
│  │       │ Uses Tools                                         │  │
│  │       ▼                                                     │  │
│  │  ┌──────────────────────────────────────┐                 │  │
│  │  │     DATABASE TOOLS                    │                 │  │
│  │  │  (banking_tools.py)                   │                 │  │
│  │  │                                        │                 │  │
│  │  │  • get_account_balance                │                 │  │
│  │  │  • get_transaction_history            │                 │  │
│  │  │  • transfer_funds                     │                 │  │
│  │  │  • get_reminders                      │                 │  │
│  │  │  • set_reminder                       │                 │  │
│  │  └────────────┬──────────────────────────┘                 │  │
│  └───────────────┼──────────────────────────────────────────┘  │
│                  │                                              │
│  ┌───────────────▼──────────────────────────────────────────┐  │
│  │              SERVICES                                     │  │
│  │                                                            │  │
│  │  ┌─────────────────────┐    ┌──────────────────────┐    │  │
│  │  │  Ollama Service     │    │  Azure TTS Service   │    │  │
│  │  │  (Qwen 2.5 7B)      │    │  (Optional)          │    │  │
│  │  │  • Chat             │    │  • Hi-IN voices      │    │  │
│  │  │  • Stream           │    │  • En-IN voices      │    │  │
│  │  │  • Embeddings       │    │  • Te-IN voices      │    │  │
│  │  └──────────┬──────────┘    └──────────────────────┘    │  │
│  └─────────────┼───────────────────────────────────────────┘  │
│                │                                               │
│  ┌─────────────▼───────────────────────────────────────────┐  │
│  │              UTILITIES                                   │  │
│  │  • Structured Logging (structlog)                       │  │
│  │  • Error Handling (custom exceptions)                   │  │
│  │  • Configuration (pydantic-settings)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌────────────────┐  ┌──────────────────┐
│   OLLAMA      │  │   DATABASE     │  │   LANGSMITH      │
│  localhost:   │  │   SQLite       │  │  smith.lang      │
│    11434      │  │   (Existing    │  │   chain.com      │
│               │  │    Backend)    │  │                  │
│  Models:      │  │                │  │  • Tracing       │
│  • qwen2.5:7b │  │  Tables:       │  │  • Monitoring    │
│  • llama3.2:3b│  │  • accounts    │  │  • Debugging     │
│               │  │  • transactions│  │  • Analytics     │
│               │  │  • reminders   │  │                  │
└───────────────┘  └────────────────┘  └──────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                     BACKEND API (Existing)                          │
│                   http://localhost:8000                             │
│                                                                     │
│  • Authentication (/api/auth/login)                                │
│  • User Management (/api/users)                                    │
│  • Database Models & Repositories                                  │
│  • Session Management                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

### Balance Check Request

```
1. User Types: "Check my balance"
   ↓
2. Frontend (Chat.jsx)
   → Calls aiClient.sendChatMessage()
   ↓
3. AI Backend (/api/chat)
   → Receives: {
       message: "Check my balance",
       user_id: 1,
       user_context: {account_number: "ACC001"}
     }
   ↓
4. LangGraph Agent System
   → Intent Classifier: "banking_operation"
   → Routes to: Banking Agent
   ↓
5. Banking Agent (Qwen 2.5 7B)
   → Decides to use: get_account_balance tool
   ↓
6. Database Tool
   → Executes: SELECT balance FROM accounts WHERE account_number = 'ACC001'
   → Returns: {success: true, balance: 10000.00}
   ↓
7. Banking Agent
   → Formats response: "Your account balance is ₹10,000.00"
   ↓
8. API Response
   → Returns: {
       success: true,
       response: "Your account balance is ₹10,000.00",
       intent: "banking_operation"
     }
   ↓
9. Frontend
   → Displays message in chat
   → (Optional) Speaks message via TTS in voice mode
```

### Hindi Query Flow

```
User: "मेरा बैलेंस क्या है?"
  ↓
Intent Classifier (Llama 3.2 3B)
  → Detects: banking_operation
  ↓
Banking Agent (Qwen 2.5 7B with language: "hi-IN")
  → System Prompt: "आप वाणी हैं..."
  → Calls: get_account_balance
  → Response: "आपके खाते का बैलेंस ₹10,000.00 है।"
  ↓
Frontend displays in Hindi
```

## Monitoring Flow

```
Every LLM Call
    ↓
LangSmith SDK (Automatic)
    ↓
Traces sent to smith.langchain.com
    ↓
Dashboard shows:
  • Input/Output
  • Latency
  • Token usage
  • Agent decisions
  • Tool calls
  • Errors
```

## Voice Mode Flow

```
User speaks: "Check my balance"
    ↓
Web Speech API (Frontend)
    → Transcribes to text
    ↓
aiClient.sendChatMessage({voice_mode: true})
    ↓
AI Backend (Fast Model: Llama 3.2 3B)
    → Quick response < 1s
    ↓
Response: "Your balance is ₹10,000"
    ↓
Frontend TTS
    → Option 1: Web Speech API (free)
    → Option 2: Azure TTS (better quality)
    ↓
User hears response
    ↓
Auto-enables mic for next input (Voice Mode feature)
```

## Error Handling Flow

```
Request → Try AI Backend
    ↓ (if fails)
Retry 3x with exponential backoff
    ↓ (if still fails)
Log error to structlog
    ↓
Send trace to LangSmith
    ↓
Return error response OR fallback to mock
    ↓
Frontend shows user-friendly error
```
