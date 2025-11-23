# Vaani – AI Voice Assistant for Financial Operations (Round 2_1 Technical Write‑up)

## 1. Technology Stack

Vaani is implemented as a practical, production‑ready three‑tier system, tuned for the realities of Indian banking – intermittent connectivity, low‑end Android devices, and strict compliance requirements.

### 1.1 Frontend (Presentation Layer)

- **Framework**: React 19 with Vite
- **Language**: TypeScript/JavaScript (ES2020)
- **Routing**: React Router v6
- **Voice I/O**: Web Speech API for speech‑to‑text and text‑to‑speech in the browser
- **UI Components**: Custom chat UI inspired by ChatGPT with banking cards (balances, transactions, UPI flows)
- **State Management**: React Context + custom hooks (`useChatHandler`, `useVoiceMode`)
- **HTTP Client**: Axios wrappers for Backend API and AI Backend
- **Build & Tooling**: Vite dev server, ESLint, Vitest (unit tests)

This layer runs on **port 5173** during development and is designed to be deployed as static assets behind a CDN or Nginx in production.

### 1.2 Backend API (Banking & Auth Layer)

- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite for the hackathon build, with configuration hooks for PostgreSQL in production
- **Data Validation**: Pydantic v2 schemas
- **Authentication**: JWT (python‑jose) with session table
- **Cryptography**: `bcrypt` for password hashing, UPI PIN hashing helpers
- **Voice Biometrics**: Resemblyzer (ECAPA‑TDNN embeddings)
- **Logging**: Python logging + structured demo logs

This service exposes RESTful APIs on **port 8000**. It is the source of truth for customers, accounts, transactions, reminders, device bindings and UPI payments.

### 1.3 AI Backend (Conversational & RAG Layer)

- **Framework**: FastAPI
- **Agent Orchestration**: LangGraph based Hybrid Supervisor pattern
- **LLM Provider**: Ollama (local) with two models:
  - `qwen2.5:7b` – main reasoning and generation model
  - `llama3.2:3b` – fast intent classification and routing
- **Vector Store**: ChromaDB with multiple collections for English and Hindi content
- **Embeddings**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **Observability**: Optional LangSmith tracing for agent flows
- **Logging**: `structlog` based structured logs

The AI backend runs on **port 8001** and is responsible for understanding user utterances, deciding which banking tools to call, and grounding all product FAQs via Retrieval‑Augmented Generation.

### 1.4 Supporting Services

- **Ollama** (port 11434) for running open LLM models locally on the hackathon machine.
- **Browser Web Speech API** for speech recognition and synthesis.
- **Future‑ready Integrations**: Configuration hooks for OpenAI, Redis cache, and managed databases are already wired in configuration files.

Together, these technologies deliver an end‑to‑end, India‑ready voice banking experience while remaining hackathon‑friendly to set up on a single laptop.

---

## 2. System Architecture

At a high level, Vaani is a three‑service micro‑architecture:

1. **Frontend (React + Vite)** – chat‑style voice UI for customers.
2. **Backend API (FastAPI)** – secure banking and authentication APIs.
3. **AI Backend (LangGraph + Ollama)** – multi‑agent conversational brain.

During development all three services are started together using `python run_services.py`. In production the same pattern extends naturally to containerised deployments.

### 2.1 End‑to‑End Flow

1. A customer logs in from a mobile browser and lands on the **Chat page**.
2. The user either types in Hinglish (e.g., “Mera balance batao”) or taps the mic icon and speaks.
3. The browser’s Web Speech API converts speech to text and `useChatHandler` sends it as a message to the **AI Backend**.
4. The AI Backend’s **Hybrid Supervisor** classifies intent using the fast LLM and routes the request:
   - Banking operations → **Banking Agent**
   - UPI flows → **UPI Agent**
   - Loan or investment queries → **RAG Supervisor + domain agents**
   - Small‑talk or greetings → **Greeting Agent**
5. Whenever an operation needs real customer data, the agent invokes a **tool function**. Each tool calls the **Backend API** using an internal HTTP call with the user’s JWT.
6. The Backend API accesses the **database** via SQLAlchemy repositories, performs validations, and returns typed responses.
7. The agent composes a final natural‑language answer plus a structured JSON payload (for cards / flows) and returns it to the frontend.
8. The frontend renders the AI reply as chat bubbles plus rich components: balance cards, transaction tables, UPI confirmation panels, etc. If voice mode is on, the message is also spoken back in a friendly Indian English tone.

This architecture ensures **LLM decisions are always grounded in real banking systems** and that the AI layer never touches the database directly.

### 2.2 Logical Layers

1. **Presentation Layer (React)**
   - Pages: `LoginPage`, `ChatPage`, `TransactionPage`, `ProfilePage`.
   - Chat UI: `ChatInput`, `ChatMessage`, `ChatSidebar`, interactive cards.
   - Voice hooks: `useVoiceMode`, `useSpeechRecognition`, `useTextToSpeech`.

2. **Application Layer (FastAPI Backend)**
   - API routes under `/api/v1` for auth, accounts, transactions, reminders, device bindings, and UPI.
   - Domain services (`AuthService`, `BankingService`, `DeviceBindingService`, `VoiceVerificationService`).
   - Repositories for each aggregate (`AccountsRepository`, `TransactionsRepository`, etc.).

3. **AI Layer (LangGraph Backend)**
   - **HybridSupervisor**: keeps `ConversationState`, performs intent routing, and guards tool usage.
   - **Agents**: Banking, UPI, Greeting, Feedback, and RAG Specialist agents (Loan, Investment, Customer Support).
   - **RAGService**: abstracts ChromaDB collections and embeddings.
   - **LLMService**: encapsulates Ollama/OpenAI calls with retry and fallbacks.

### 2.3 Deployment View

For the hackathon, all services run on a single developer machine:

- `localhost:5173` – React frontend
- `localhost:8000` – Backend API
- `localhost:8001` – AI Backend
- `localhost:11434` – Ollama LLM server

For a bank‑grade rollout, the same design supports horizontal scaling:

- Frontend on CDN or Nginx.
- Multiple backend pods behind a load‑balancer with PostgreSQL.
- Multiple AI backend pods with shared vector DB and GPU‑backed LLMs.

---

## 3. Data Model and Storage

The backend uses a relational schema that mirrors how Indian retail banking works while staying compact for a hackathon deployment.

### 3.1 Core Entities

1. **User**
   - Captures KYC‑grade information: customer number, name, DOB, mobile, email, Aadhaar last‑4, PAN, preferred language (`en-IN` / `hi-IN`), risk segment.
   - Stores `upi_id` and `upi_pin_hash` to simulate NPCI style virtual payment addresses.
   - Links to accounts, cards, reminders, beneficiaries, sessions and device bindings.

2. **Account**
   - Represents individual savings or current accounts with `account_number`, `account_type`, `balance`, `currency`, `status`, and branch mapping.
   - Linked to **transactions** and the owning **user**.

3. **Transaction**
   - Records atomic movements of money: `debit` or `credit`, `amount`, `balance_after`, `channel` (UPI, ATM, BRANCH, NEFT, IMPS etc.), status and reference ID.
   - Forms the basis for on‑chat passbook style history and statement downloads.

4. **DeviceBinding**
   - Represents a trusted phone or browser: `device_identifier`, `device_fingerprint`, `platform`, `device_label`, `trust_level` (TRUSTED / SUSPICIOUS / REVOKED).
   - Stores **voice signature embeddings** and hashes for passive biometric verification.

5. **Reminder**
   - Captures bill payment/EMI reminders linked to a user and optionally to an account.
   - Includes `reminder_type`, `status`, `remind_at`, `channel`, and recurrence rules.

6. **Beneficiary**
   - Stores saved payees with `account_number`, `upi_id`, `ifsc_code`, and nicknames to support quick transfers.

7. **Session**
   - Represents an authenticated session with `access_token`, device ID, IP, `created_at`, and `expires_at`.

The schema is implemented via SQLAlchemy models under `backend/db/models/` and seeded with realistic demo data for the hackathon.

### 3.2 Storage Technologies

- **Primary Database**: SQLite file `backend/db/vaani.db` for the event, chosen for zero setup and easy seeding. The code is structured to switch to PostgreSQL by changing `DB_BACKEND` and `DATABASE_URL` environment variables.
- **Vector Stores**: ChromaDB collections under `ai/chroma_db/` for four knowledge bases:
  - `loan_products` (English)
  - `loan_products_hindi` (Hindi)
  - `investment_schemes` (English)
  - `investment_schemes_hindi` (Hindi)
- **Documents**: Source PDFs for loans and investments under `backend/documents/…`, which are processed by ingestion scripts into ChromaDB.

### 3.3 Data Access Patterns

- The Backend API exposes repository functions for each aggregate, promoting a clean **Domain Service → Repository → Database** flow.
- The AI Backend never touches the DB directly; instead, it calls **tools** that in turn hit Backend APIs.
- For auditability, every transaction and UPI payment is written once to the `Transaction` table and then only read via filtered, paginated queries.

This design keeps the data model simple but expressive enough to simulate a mid‑sized Indian retail bank.

---

## 4. AI / ML / Automation Components

The heart of Vaani is the AI Backend, which converts messy, code‑switched human language into safe banking actions.

### 4.1 Hybrid Supervisor & Multi‑Agent Design

The orchestration follows a **Hybrid Supervisor** pattern built on LangGraph:

- **IntentRouter** uses the fast `llama3.2:3b` model to classify each user utterance into intents such as `banking_operation`, `upi_payment`, `loan_inquiry`, `investment_query`, `general_faq`, or `chitchat`.
- **HybridSupervisor** maintains a structured `ConversationState` with user/session IDs, language preference, previous messages, and flags like "UPI flow in progress".
- Based on the route, the Supervisor delegates work to specialized agents:
  - **Greeting Agent** – deterministic, non‑LLM greetings and onboarding.
  - **Banking Agent** – uses tools for balance, transaction history, intra‑bank transfers, and reminders.
  - **UPI Agent** – orchestrates multi‑turn Hello UPI flows (amount + payee + PIN verification).
  - **RAG Supervisor & Specialists** – handle loans, investments and customer support FAQs.
  - **Feedback Agent** – captures ratings and complaints.

This modular design makes the system easy to extend: adding a new domain (e.g., credit cards) means adding a new agent plus a few tools and updating the router prompt.

### 4.2 Retrieval‑Augmented Generation (RAG)

For loan and investment information the system uses RAG to avoid hallucinations:

1. Product PDFs (both English and Hindi) are ingested using Python scripts in `ai/ingest_documents_*.py`.
2. Each document is chunked semantically, embedded using HuggingFace MiniLM, and stored in a ChromaDB collection with metadata (language, product type, scheme name).
3. At query time, the relevant **Loan Agent** or **Investment Agent** detects the language and queries the right collection.
4. Retrieved chunks are passed to the primary `qwen2.5:7b` model with a strict system prompt to answer **only from context**.
5. The agent emits both a natural‑language explanation and a structured schema (interest rates, tenure, tax benefits, eligibility), which the frontend renders as an information card.

This approach supports both **English** and **Hindi** queries like “Tell me about home loans” and “होम लोन के बारे में बताओ” with the same reliability.

### 4.3 Voice Biometrics & AI‑Assisted Risk Scoring

On the authentication side, automation comes from a two‑layer voice verification system:

- **Baseline Verification**: Resemblyzer generates a fixed‑length embedding from the customer’s voice sample. Cosine similarity with the stored embedding decides a basic match vs. no‑match.
- **AI‑Enhanced Verification**: A dedicated service can send the similarity score and device context to the AI Backend to get a richer verdict – confidence, risk band, and whether to request OTP.
- **Adaptive Thresholds**: Thresholds are tuned based on `DeviceTrustLevel`; new or suspicious devices demand higher similarity (or OTP fallback), while trusted devices allow slightly lower scores.

This makes the login flow closer to how Indian banks do risk‑based authentication, while still being fully simulated for the hackathon.

### 4.4 Automation of Banking Flows

- **UPI Payment Flow** – the UPI Agent automatically drives the conversation: confirms payee and amount, triggers a PIN collection UI, verifies the PIN through the Backend API, and finally executes a transfer, announcing the result.
- **Reminders & Alerts** – users can ask Vaani to “set EMI reminder for 5th of every month”. The agent calls reminder tools that create records in the Reminder table, which can be later surfaced as notifications.
- **Graceful Failure Handling** – instead of generic errors, agents are prompted to use conversational repair strategies: “I understood you want to transfer, but I missed the amount. How much would you like to send?”

---

## 5. Security and Compliance

From day one the design was aligned with RBI guidance and India’s DPDP Act, even though this build uses mock data.

### 5.1 Authentication & Authorisation

- **Multi‑Factor Authentication (MFA)**:
  - Password / voice biometric as the first factor.
  - Device binding as a possession factor.
  - Optional OTP or additional challenge can be plugged in easily.
- **JWT‑based Sessions**:
  - All APIs behind `/api/v1` require a valid access token.
  - Tokens map to a `Session` row capturing device ID and IP for full audit trail.

### 5.2 Device Binding and Voice Security

- During first login from a device, the backend registers a **DeviceBinding** with a fingerprint and voice signature.
- Only trusted devices can perform sensitive flows like UPI payments.
- On suspicious behaviour, bindings can be marked REVOKED; future attempts from that fingerprint are forced through re‑enrolment or OTP.

### 5.3 Data Protection & DPDP Alignment

- **Data Minimisation**: The AI Backend never receives raw PAN, Aadhaar or full account numbers. Tools abstract away PII, and prompts contain only masked identifiers and friendly names.
- **No Raw Audio Storage**: The system stores only voice embeddings and hashes, not original audio, reducing breach impact.
- **Purpose Limitation**: RAG indexes only public‑style product documents (loan/ investment PDFs). Customer data stays strictly inside the Backend API and DB, and is not used to train models.
- **Config‑Driven Secrets**: All secrets (JWT keys, DB URLs, LLM keys) are read from environment variables and excluded from version control.

### 5.4 API & Transport Security

- CORS is configured to only allow the expected frontend origins during normal deployment.
- Request/response validation via Pydantic ensures only well‑formed data reaches the database.
- Standardised error envelopes expose minimal internal details while being friendly for the UI.
- For a production rollout, all endpoints are assumed to be served over HTTPS with TLS termination at the load balancer.

### 5.5 Auditability & Observability

- Every banking operation and UPI payment is recorded in both **Transaction** tables and structured logs.
- The AI layer’s decisions (intent, selected agent, tools called) can be traced via logs or optional LangSmith traces, turning the system into a **transparent, auditable AI** rather than a black box.

---

## 6. Scalability and Performance

Although the hackathon deployment runs on a single laptop, the architecture is designed to scale out to a Tier‑1 bank scenario.

### 6.1 Horizontal Scaling Strategy

- **Frontend**: Pure static assets can be served from any CDN or Nginx cluster. Since there is no server‑side state, it can scale almost infinitely for read traffic.

- **Backend API**:
  - Stateless by design – all state sits in the database.
  - Multiple FastAPI instances can run behind a load balancer, each using a connection pool to a shared PostgreSQL instance.
  - Expensive operations (e.g., report generation) can be off‑loaded to background workers.

- **AI Backend**:
  - Each AI instance is stateless at process level, using `ConversationState` objects per request.
  - Multiple instances can be run behind an internal load balancer.
  - Vector DB (ChromaDB or a managed alternative) is shared, and LLMs can be scaled using GPU nodes or switched to cloud providers.

### 6.2 Performance Optimisations

- **Model Tiering** – routing uses a small model (`llama3.2:3b`), while full question answering uses `qwen2.5:7b`, balancing latency and quality.
- **RAG Caching** – retrieved contexts are cached for ~120 seconds, so repeated questions like “What is my balance?” or “NPS details batao” are served faster.
- **Pagination** – transaction history and statements are paginated to avoid heavy DB reads.
- **Asynchronous IO** – FastAPI’s async capabilities reduce waiting time during external calls to the AI Backend.

### 6.3 Reliability & Graceful Degradation

- **Retry Logic** – external calls to the AI Backend or LLM have bounded retries with exponential back‑off.
- **Circuit Breaker Pattern** – if downstream services repeatedly fail, the system temporarily opens a circuit and serves cached or rule‑based responses instead of timing out every request.
- **Fallback Modes**:
  - If Ollama is down, the AI Backend can switch to OpenAI or respond with template‑based answers.
  - If the AI Backend is unavailable entirely, the frontend can still provide a minimal non‑conversational mode (e.g., traditional menus).

---

## 7. Conclusion

Vaani is built as a **voice‑first, Bharat‑ready banking assistant** that goes beyond a demo chatbot. The stack, architecture, data model and AI design are aligned with real‑world Indian banking constraints – multilingual Hinglish conversations, low digital literacy, and RBI‑grade security expectations.

This document captures the implementation behind the Round‑1 concept note:
- Multi‑agent AI + RAG for grounded, auditable responses.
- Voice biometrics and device binding for frictionless yet secure logins.
- Rich, chat‑style UI for balances, history, UPI and product discovery.
- A deployment model that can start on a laptop today and scale to a production‑ready cluster tomorrow.

In short, Vaani turns “banking by conversation” into an engineering reality, not just a slideware promise.