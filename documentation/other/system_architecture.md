# Vaani Banking Voice Assistant - System Architecture

This document provides a comprehensive overview of the entire Vaani system architecture, showing how all three microservices (Frontend, Backend API, AI Backend) work together.

**Diagram**: See `system_architecture.mmd` for the visual representation.

---

## System Overview

Vaani is a full-stack voice-enabled banking assistant built with three main components:

1. **Frontend** (React + Vite) - Port 5173
2. **Backend API** (FastAPI + SQLAlchemy) - Port 8000  
3. **AI Backend** (LangGraph + Ollama) - Port 8001

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │ ───▶ │ Backend API │ ───▶ │ AI Backend  │
│   (React)   │      │  (FastAPI)  │      │ (LangGraph) │
│   :5173     │      │    :8000    │      │    :8001    │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                     │
       │                    │                     │
       ▼                    ▼                     ▼
  Web Speech           SQLite DB            Ollama + ChromaDB
   API (TTS)           (vaani.db)          (qwen2.5:7b, llama3.2:3b)
```

---

## Architecture Layers

### 1. Presentation Layer (Frontend)

**Technology**: React 19 + Vite
**Port**: 5173
**Location**: `frontend/`

#### Key Components

**Pages**
- `LoginPage.jsx` - Voice biometric authentication
- `ChatPage.jsx` - Main conversational interface
- `ProfilePage.jsx` - User profile and settings
- `TransactionPage.jsx` - Transaction history

**Voice Features**
- `useVoiceRecognition.js` - Web Speech API for STT
- `useTextToSpeech.js` - Browser-based TTS (window.speechSynthesis)
- Voice mode toggle with continuous listening

**API Integration**
- `aiClient.js` - Connects to AI Backend (port 8001)
- `api.js` - Connects to Backend API (port 8000)

**State Management**
- Context API for global state
- Local storage for session persistence

---

### 2. Application Layer (Backend API)

**Technology**: FastAPI + SQLAlchemy
**Port**: 8000
**Location**: `backend/`
**Database**: SQLite (`backend/db/vaani.db`)

#### Core Modules

**Authentication & Security** (`backend/api/`)
- JWT token-based authentication
- Voice biometric verification (Resemblyzer)
- Device binding and multi-factor auth
- Password hashing (bcrypt)

**Database Models** (`backend/db/models/`)
```
- User (users table)
- Account (accounts table)
- Transaction (transactions table)
- DeviceBinding (device_bindings table)
- VoiceProfile (voice_profiles table)
- Reminder (reminders table)
- UPIPayment (upi_payments table)
```

**API Endpoints**
```
POST   /api/auth/login              - User login
POST   /api/auth/voice-login        - Voice biometric login
POST   /api/auth/register-device    - Register device
GET    /api/users/profile           - Get user profile
GET    /api/accounts/{id}           - Get account details
GET    /api/transactions            - Get transactions
POST   /api/transactions/transfer   - Transfer funds
GET    /api/reminders               - Get reminders
POST   /api/reminders               - Create reminder
POST   /api/upi/send-payment        - Hello UPI payment
POST   /api/upi/verify-pin          - Verify UPI PIN
```

**Services**
- `UserService` - User management
- `AccountService` - Account operations
- `TransactionService` - Transaction processing
- `VoiceVerificationService` - Voice biometrics
- `DeviceBindingService` - Device management
- `UPIService` - UPI payment processing

---

### 3. AI Layer (AI Backend)

**Technology**: LangGraph + Ollama + ChromaDB
**Port**: 8001
**Location**: `ai/`
**LLM Models**: Qwen 2.5 7B (primary), Llama 3.2 3B (fast)

#### Agent Architecture

**Orchestrator** (`ai/orchestrator/`)
```
HybridSupervisor
  ├── IntentRouter (classifies user intent)
  ├── ConversationState (maintains context)
  └── Agent Dispatcher (routes to appropriate agent)
```

**Agents** (`ai/agents/`)
```
1. Greeting Agent - Handles greetings
2. Banking Agent - Balance, transactions, transfers, reminders
3. UPI Agent - Hello UPI payments
4. RAG Supervisor - Routes to specialized RAG agents
   ├── Loan Agent (7 loan types)
   ├── Investment Agent (7 schemes)
   └── Customer Support Agent
5. Feedback Agent - Collects feedback
```

**Services** (`ai/services/`)
```
- LLMService - Ollama/OpenAI integration
- RAGService - ChromaDB vector retrieval
- GuardrailService - Input/output safety checks (content moderation, PII detection, prompt injection protection, rate limiting)
- Azure TTS Service (optional, not currently used)
```

**Tools** (`ai/tools/`)
```
Banking Tools:
  - get_account_balance
  - get_transaction_history
  - transfer_funds
  - get_reminders
  - set_reminder

UPI Tools:
  - initiate_upi_payment
  - verify_upi_pin
  - check_upi_status
```

#### RAG System

**Vector Databases** (ChromaDB - `ai/chroma_db/`)
```
1. loan_products (English)
2. loan_products_hindi (Hindi)
3. investment_schemes (English)
4. investment_schemes_hindi (Hindi)
```

**Embeddings**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`

**Document Sources**:
- `backend/documents/loan_products/*.pdf`
- `backend/documents/loan_products_hindi/*.pdf`
- `backend/documents/investment_schemes/*.pdf`
- `backend/documents/investment_schemes_hindi/*.pdf`

---

## Data Flow Examples

### 1. Voice Login Flow

```
User speaks enrollment phrase
    ↓
Frontend: Web Speech API transcribes
    ↓
POST /api/auth/voice-login
    {
      username: "user123",
      voice_sample: <audio_blob>,
      device_info: {...}
    }
    ↓
Backend: Resemblyzer compares voice embeddings
    ↓
Backend: Verifies device binding
    ↓
Backend: Returns JWT token
    ↓
Frontend: Stores token, redirects to chat
```

### 2. Banking Query Flow (Balance Check)

```
User: "What's my account balance?"
    ↓
Frontend: aiClient.sendChatMessage()
    → POST http://localhost:8001/api/chat
    ↓
AI Backend: Receives message
    ↓
HybridSupervisor:
  1. IntentRouter classifies as "banking_operation"
  2. Routes to Banking Agent
    ↓
Banking Agent (Qwen 2.5 7B):
  1. Decides to use get_account_balance tool
  2. Tool calls Backend API:
     GET http://localhost:8000/api/accounts/{id}
    ↓
Backend API:
  1. Queries SQLite database
  2. Returns: { balance: 50000.00, currency: "INR" }
    ↓
Banking Agent:
  1. Formats response: "Your account balance is ₹50,000.00"
    ↓
AI Backend returns response
    ↓
Frontend displays message + speaks via TTS
```

### 3. RAG Query Flow (Loan Information)

```
User: "Tell me about home loans" / "होम लोन के बारे में बताओ"
    ↓
AI Backend: Intent classified as "loan_inquiry"
    ↓
RAG Supervisor: Routes to Loan Agent
    ↓
Loan Agent:
  1. Detects language (English or Hindi)
  2. Queries appropriate vector DB:
     - loan_products (English)
     - loan_products_hindi (Hindi)
  3. Retrieves relevant PDF chunks
  4. Sends context + query to LLM
    ↓
LLM generates structured response with loan card
    ↓
Frontend displays loan information card
```

### 4. UPI Payment Flow

```
User: "Send ₹500 to John via UPI"
    ↓
AI Backend: Intent classified as "upi_payment"
    ↓
UPI Agent (Multi-step flow):
  Step 1: Confirm recipient and amount
    → "Confirming: Send ₹500 to John?"
  
  User: "Yes"
  
  Step 2: Request UPI PIN
    → "Please enter your UPI PIN"
    → structured_data: { action: "collect_upi_pin" }
  
  Frontend: Shows PIN input modal
  User enters PIN
  
  Step 3: Verify PIN
    → Tool calls: POST /api/upi/verify-pin
  
  Step 4: Process payment
    → Tool calls: POST /api/upi/send-payment
  
  Backend:
    1. Verifies PIN
    2. Creates transaction
    3. Updates balances
    4. Returns confirmation
  
  Step 5: Confirmation
    → "Payment successful! ₹500 sent to John."
    → structured_data: { payment_id: "TXN123", status: "success" }
```

### 5. Investment Scheme Query (Hindi)

```
User: "PPF योजना के बारे में बताओ"
    ↓
AI Backend: Routes to Investment Agent
    ↓
Investment Agent:
  1. Detects Hindi language
  2. Queries: investment_schemes_hindi vector DB
  3. Retrieves PPF scheme PDF content
  4. LLM generates response in Hindi
    ↓
Response includes structured investment card:
  {
    scheme_name: "पब्लिक प्रोविडेंट फंड (PPF)",
    returns: "7.1% प्रति वर्ष",
    tenure: "15 वर्ष",
    tax_benefit: "धारा 80C के तहत कटौती",
    minimum: "₹500",
    maximum: "₹1.5 लाख/वर्ष"
  }
```

---

## Technology Stack

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Voice**: Web Speech API (STT + TTS)
- **Styling**: CSS Modules
- **State**: Context API

### Backend API
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite (production: PostgreSQL ready)
- **Authentication**: JWT (python-jose)
- **Voice Biometrics**: Resemblyzer
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2

### AI Backend
- **Orchestration**: LangGraph
- **LLM Provider**: Ollama (local)
- **Models**: 
  - Qwen 2.5 7B (comprehensive)
  - Llama 3.2 3B (fast classification)
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace sentence-transformers
- **Observability**: LangSmith (optional)
- **Framework**: FastAPI
- **Logging**: structlog

---

## External Dependencies

### Required Services

**Ollama** (Port 11434)
- Must be running locally
- Models: `qwen2.5:7b`, `llama3.2:3b`
- Install: https://ollama.com

### Optional Services

**LangSmith** (Cloud)
- Agent tracing and monitoring
- Enabled via `ai/.env`: `LANGSMITH_TRACING=true`

**OpenAI API** (Cloud)
- Alternative to Ollama
- Set `LLM_PROVIDER=openai` in `ai/.env`

---

## Deployment Architecture

### Development Setup (Current)

```
localhost:5173  ──┐
localhost:8000  ──┼──▶ Same Machine
localhost:8001  ──┘
localhost:11434 (Ollama)
```

**Start Command**: `python run_services.py`

### Production Considerations

```
┌──────────────────────────────────────────────┐
│              Load Balancer / CDN             │
└──────────────┬───────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│Frontend │         │Frontend │
│ (Nginx) │         │ (Nginx) │
└────┬────┘         └────┬────┘
     │                   │
     └───────┬───────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│ Backend  │    │ Backend  │
│   API    │    │   API    │
└────┬─────┘    └────┬─────┘
     │               │
     └───────┬───────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
 ┌─────────┐   ┌─────────┐
 │AI Backend│   │AI Backend│
 └────┬────┘   └────┬────┘
      │             │
      └──────┬──────┘
             │
    ┌────────┴────────────┐
    │                     │
    ▼                     ▼
┌──────────┐      ┌────────────┐
│PostgreSQL│      │Ollama/Cloud│
│(Database)│      │    LLM     │
└──────────┘      └────────────┘
```

**Considerations**:
- Frontend: Static hosting (Vercel, Netlify, S3 + CloudFront)
- Backend API: Container deployment (Docker + Kubernetes)
- AI Backend: GPU instances for Ollama or cloud LLM APIs
- Database: PostgreSQL managed service (AWS RDS, Supabase)
- File Storage: S3/blob storage for voice samples and documents
- Vector DB: Managed ChromaDB or Pinecone/Weaviate

---

## Security Architecture

### Authentication Flow

```
1. User Login
   └─▶ Username/Password OR Voice Biometric
       └─▶ Backend validates credentials
           └─▶ Returns JWT token (24h expiry)

2. Device Binding
   └─▶ First login from new device
       └─▶ Device fingerprint stored
           └─▶ Future logins verified against fingerprint

3. Voice Verification
   └─▶ Voice sample captured
       └─▶ Resemblyzer generates embedding
           └─▶ Cosine similarity with stored profile
               └─▶ Threshold: 0.6 (adjustable)
```

### API Security

```
Frontend ──▶ Backend API
             │
             ├─▶ JWT validation (all protected routes)
             ├─▶ CORS policy (configured origins)
             ├─▶ Rate limiting (future)
             └─▶ Input validation (Pydantic schemas)

Frontend ──▶ AI Backend
             │
             ├─▶ Session validation
             ├─▶ User context verification
             └─▶ Tool authorization checks
```

### Data Security

- **Passwords**: bcrypt hashed (cost factor: 12)
- **Voice Samples**: Embeddings stored, not raw audio
- **Tokens**: Secure random generation, HTTP-only cookies (future)
- **Database**: SQLite with file permissions (prod: encrypted PostgreSQL)
- **API Keys**: Environment variables only, never committed

---

## Monitoring & Observability

### Logging Strategy

**Backend API** (`backend/`)
- Python logging to `logs/backend.log`
- Request/response logging
- Error tracking with stack traces

**AI Backend** (`ai/`)
- structlog for structured logging
- Agent decision logging
- Tool invocation tracking
- Performance metrics (latency, token usage)

### Tracing (LangSmith)

When enabled:
```
Every LLM interaction
    ↓
LangSmith SDK captures:
  - Input prompt
  - Model parameters
  - Output tokens
  - Latency
  - Agent decisions
  - Tool calls
    ↓
Dashboard visualization:
  - Trace waterfall
  - Token usage analytics
  - Error rates
  - User conversation flows
```

### Performance Metrics

**Target Response Times**:
- Voice mode (fast model): < 1 second
- Standard chat: < 2 seconds
- RAG queries: < 3 seconds
- Complex banking ops: < 5 seconds

**Current Bottlenecks**:
- Ollama inference time (local CPU/GPU)
- Vector similarity search (ChromaDB)
- Network latency (dev: localhost)

---

## Scalability Considerations

### Horizontal Scaling

**Frontend**
- Static files, infinitely scalable via CDN
- No state, can serve unlimited concurrent users

**Backend API**
- Stateless design (JWT tokens)
- Can scale horizontally with load balancer
- Database connection pooling required

**AI Backend**
- Stateless agent execution
- Can scale with multiple instances
- Shared ChromaDB required (managed service)
- Ollama: GPU scaling or cloud LLM switch

### Caching Strategy

**Current Implementation**:
- RAG context cache (120s TTL)
- In-memory caching per instance

**Future Enhancements**:
- Redis for distributed caching
- Cache frequent queries (balance checks)
- Session state caching
- Vector search result caching

---

## Error Handling & Resilience

### Retry Strategy

```
AI Backend Request
    ↓
Try 1 ───▶ Failure
    ↓ (wait 1s)
Try 2 ───▶ Failure
    ↓ (wait 2s)
Try 3 ───▶ Failure
    ↓
Fallback Response OR Error
```

### Circuit Breaker Pattern

```
Monitor Backend API health
    ↓
If 5 failures in 1 minute:
    ↓ Open circuit
Use cached data OR fallback
    ↓
After 30 seconds:
    ↓ Half-open (test)
Try one request
    ↓ Success?
Close circuit (resume normal)
```

### Graceful Degradation

```
Ollama unavailable
    ↓
Fallback to OpenAI API
    ↓ (if configured)
Use rule-based responses
    ↓ (if no LLM)
Return helpful error message
```

---

## Development Workflow

### Local Development

```bash
# Terminal 1: Backend API
python main.py

# Terminal 2: AI Backend
cd ai && ./run.sh

# Terminal 3: Frontend
cd frontend && npm run dev

# All-in-one
python run_services.py
```

### Testing Strategy

**Backend API**
- Unit tests: `pytest backend/tests/`
- Integration tests: API endpoint testing
- Database: Test fixtures with SQLite in-memory

**AI Backend**
- Agent tests: `pytest ai/test_*.py`
- RAG retrieval tests
- UPI flow tests
- Balance query tests
- Intent classification tests

**Frontend**
- Component tests: Vitest
- E2E tests: Playwright/Cypress (future)

### CI/CD Pipeline (Future)

```
Git Push
    ↓
GitHub Actions
    ├─▶ Lint (ESLint, Ruff)
    ├─▶ Type Check (TypeScript, mypy)
    ├─▶ Unit Tests
    ├─▶ Integration Tests
    └─▶ Build
        ↓
Deploy
    ├─▶ Staging Environment
    │   └─▶ E2E Tests
    │       └─▶ Manual Approval
    └─▶ Production Deployment
```

---

## Future Enhancements

### Planned Features

1. **Multi-tenant Support**
   - Organization/bank-level isolation
   - Custom branding per tenant
   - Separate vector databases per tenant

2. **Advanced Voice Features**
   - Voice activity detection
   - Noise cancellation
   - Speaker diarization (multiple users)

3. **Enhanced RAG**
   - Multilingual embeddings
   - Hybrid search (keyword + semantic)
   - Reranking models
   - Larger document corpus

4. **Mobile Apps**
   - React Native mobile app
   - Push notifications
   - Biometric authentication (Face ID, Touch ID)

5. **Analytics Dashboard**
   - User conversation analytics
   - Agent performance metrics
   - Banking operation insights
   - Custom reports

---

## Configuration Reference

### Environment Variables

**Frontend** (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000
VITE_AI_API_URL=http://localhost:8001
```

**Backend API** (`backend/.env` or defaults)
```
DATABASE_URL=sqlite:///backend/db/vaani.db
JWT_SECRET_KEY=<random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**AI Backend** (`ai/.env`)
```
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_FAST_MODEL=llama3.2:3b

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Backend Integration
BACKEND_BASE_URL=http://localhost:8000

# LangSmith (Optional)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=vaani-banking
```

---

## Troubleshooting

### Common Issues

**Issue**: "Connection refused to port 8001"
- **Solution**: Ensure AI backend is running: `cd ai && ./run.sh`

**Issue**: "Ollama model not found"
- **Solution**: Pull models: `ollama pull qwen2.5:7b && ollama pull llama3.2:3b`

**Issue**: "Voice recognition not working"
- **Solution**: Use HTTPS or localhost, check browser permissions

**Issue**: "ChromaDB collection not found"
- **Solution**: Run ingestion scripts:
  ```bash
  python ai/ingest_documents.py
  python ai/ingest_documents_hindi.py
  python ai/ingest_investment_documents.py
  ```

**Issue**: "Database locked (SQLite)"
- **Solution**: Close other connections, or switch to PostgreSQL for production

---

## Appendix

### Port Reference

| Service | Port | Protocol |
|---------|------|----------|
| Frontend | 5173 | HTTP |
| Backend API | 8000 | HTTP |
| AI Backend | 8001 | HTTP |
| Ollama | 11434 | HTTP |

### File Structure Reference

```
vaani-banking-voice-assistant/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   └── services/     # API clients
│   └── package.json
├── backend/              # FastAPI backend
│   ├── api/             # Routes and schemas
│   ├── db/              # Database models
│   └── app.py           # Main application
├── ai/                  # AI backend
│   ├── agents/          # LangGraph agents
│   ├── services/        # LLM and RAG services
│   ├── tools/           # Banking tools
│   └── main.py          # FastAPI server
├── documentation/       # This folder
└── run_services.py      # Unified startup script
```

### Related Documentation

- [Setup Guide](./setup_guide.md) - Installation instructions
- [AI Modules](../ai_modules.md) - Detailed AI documentation
- [Backend Modules](../backend_modules.md) - Backend API documentation
- [Frontend Modules](../frontend_modules.md) - Frontend documentation
- [Investment Schemes](./investment_schemes.md) - Investment feature guide
- [Hindi Support](./hindi_support.md) - Hindi implementation guide
- [UPI Payment Flow](./upi_payment_flow.md) - UPI payment guide
