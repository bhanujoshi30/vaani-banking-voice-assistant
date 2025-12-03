# Vaani Banking Voice Assistant

Full-stack voice-enabled banking assistant with AI-powered conversational interface.

## Overview

Vaani is a comprehensive banking solution that combines voice biometrics, natural language processing, and secure banking operations to provide an accessible, voice-first banking experience.

**Key Features:**
- 🎤 Voice-based authentication with biometric verification
- 💬 AI-powered conversational banking (English & Hindi)
- 💸 Hello UPI payments with voice commands
- 🏦 Intelligent loan information (7 types) via RAG system
- 💰 Investment scheme guidance (PPF, NPS, SSY, ELSS, FD, RD, NSC)
- 🌐 Full Hindi language support with bilingual RAG databases
- 🔐 Secure device binding and multi-factor authentication
- 📱 Modern React frontend with voice interface
- 🤖 LangGraph multi-agent AI backend (Ollama/OpenAI)

## Architecture

### Technology Stack

**Frontend (Port 5173)**
- React 19 with Vite
- Web Speech API for voice I/O
- React Router for navigation

**Backend (Port 8000)**
- FastAPI with SQLAlchemy ORM
- SQLite database
- JWT authentication
- Voice verification with Resemblyzer

**AI Backend (Port 8001)**
- LangGraph for agent orchestration
- Ollama (Qwen 2.5 7B, Llama 3.2 3B)
- ChromaDB vector database for RAG
- HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)
- LangSmith for observability

### System Components

```
Frontend (React)  →  Backend API (FastAPI)  →  Database (SQLite)
      ↓                                              
   AI Chat  →  AI Backend (LangGraph + Ollama)
```

## Documentation

**📖 Complete documentation available in the [`documentation/`](./documentation/) folder:**

### System Overview

- **[System Architecture](./documentation/other/system_architecture.md)** - Complete system design
  - Three-tier architecture (Frontend, Backend API, AI Backend)
  - Data flow diagrams for voice login, banking queries, RAG, UPI payments
  - Technology stack details
  - Security architecture
  - Deployment and scalability
  - Monitoring and troubleshooting

### Getting Started

- **[Setup Guide](./documentation/other/setup_guide.md)** - Complete installation and setup instructions
  - Prerequisites installation (Python, Node.js, uv, Ollama)
  - Model downloads (qwen2.5:7b, llama3.2:3b)
  - Environment configuration
  - Running all services with `python run_services.py`

### Module Documentation

- **[Backend Modules](./documentation/backend_modules.md)** - Backend API and database architecture
  - Database models (User, Account, Transaction, DeviceBinding, etc.)
  - Repositories and services
  - API endpoints
  - Authentication and authorization

- **[AI Modules](./documentation/ai_modules.md)** - AI agent system documentation
  - Multi-agent architecture
  - RAG supervisor with specialized agents (Loan, Investment, Customer Support)
  - Intent classification
  - Banking and UPI agents
  - RAG service with vector databases
  - LLM services (Ollama/OpenAI)
  - Tools and orchestration

- **[Frontend Modules](./documentation/frontend_modules.md)** - Frontend components and pages
  - Page components (Login, Chat, Profile, Transactions)
  - Custom React hooks
  - API clients
  - Voice features

### Feature Documentation

- **[Investment Schemes](./documentation/other/investment_schemes.md)** - Investment information system
  - 7 investment schemes with detailed information
  - RAG-based retrieval from PDF documents
  - Bilingual support (English/Hindi)
  - Structured information cards

- **[Hindi Language Support](./documentation/other/hindi_support.md)** - Complete Hindi implementation
  - Hindi vector databases
  - Hindi PDF document generation
  - Font management and extraction
  - Bilingual RAG system

- **[UPI Payment Flow](./documentation/other/upi_payment_flow.md)** - Hello UPI implementation
  - Complete payment flow
  - PIN verification
  - RBI compliance
  - Multi-language support

- **[Voice Authentication](./docs/VOICE_LOGIN_IMPROVEMENTS.md)** - Voice biometric login
  - Voice verification flow
  - Device binding
  - AI-enhanced verification
  - Security features

### Architecture Documentation

- **[AI Architecture](./documentation/ai_architecture.md)** - AI system design
- **[Backend Architecture](./documentation/backend_architecture.md)** - Backend design
- **[Frontend Architecture](./documentation/frontend_architecture.md)** - Frontend design
- **[Hybrid Supervisor Pattern](./documentation/other/hybrid_supervisor_pattern.md)** - Agent orchestration

### Additional Resources

- **[docs/ folder](./docs/)** - Original development documentation
  - [Implementation Summary](./docs/IMPLEMENTATION_SUMMARY.md)
  - [Architecture Diagrams](./docs/ARCHITECTURE.md)
  - [AI README](./docs/AI_README.md)
  - [UPI Debugging](./docs/UPI_MODE_DEBUGGING.md)

## Setup (macOS)

Prerequisites
- Python 3.11+
- Node.js 18+
- uv package manager (https://github.com/astral-sh/uv)
- Ollama (https://ollama.com)

1) Install Ollama and pull models
```
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
```

2) Ensure Ollama is running (required by the AI backend)
```
ollama list
```
Confirm both models are listed.

3) Create Python environment with uv (project root)
```
uv venv .venv
source .venv/bin/activate
```

4) Install Python dependencies (root)
```
uv add -r requirements.txt
```


5) Install AI module dependencies
```
uv add -r backend/ai/requirements.txt
```

6) Install frontend dependencies
```
cd frontend
npm install
cd ..
```

7) Configure AI env (optional)
Review `backend/ai/.env` for `OLLAMA_MODEL=qwen2.5:7b`, `OLLAMA_FAST_MODEL=llama3.2:3b`, and `API_PORT=8001`.

8) Run all three modules
```
python run_services.py
```
This starts:
- Backend: `python main.py` (port 8000)
- AI: `cd backend/ai && ./run.sh` (port 8001)
- Frontend: `cd frontend && npm run dev` (port 5173)

Optional manual runs
```
python main.py
(cd backend/ai && ./run.sh)
(cd frontend && npm run dev)
```

## Seeding sample data (optional)
```
python -m backend.db.seed
```

## Notes
- If `npm run lint` fails in `frontend/`, fix warnings/errors reported by ESLint.
- Multilingual RAG: embeddings are English today; see `documentation/ai_architecture.md` for Hindi handling strategy and upgrade path to multilingual embeddings.

